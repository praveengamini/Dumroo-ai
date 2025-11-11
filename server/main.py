from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from access_control import filter_data_by_role
from query_agent import QueryAgent
from config import settings
import pandas as pd
import numpy as np
import re
import json
import logging
from datetime import datetime
import os

# Configure logging
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
)

# Enhanced CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.allowed_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load data
def load_data(filepath):
    """Load CSV file as pandas DataFrame"""
    try:
        df = pd.read_csv(filepath)
        # Convert grade and quiz_score to numeric types
        df['grade'] = pd.to_numeric(df['grade'], errors='coerce')
        df['quiz_score'] = pd.to_numeric(df['quiz_score'], errors='coerce')
        return df
    except FileNotFoundError:
        logger.error(f"Data file not found: {filepath}")
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        return pd.DataFrame()







try:
    df = load_data(settings.data_path)
    logger.info(f"Loaded {len(df)} student records from {settings.data_path}")
except Exception as e:
    logger.error(f"Error loading data: {e}")
    df = pd.DataFrame()

session_agents = {}  # session-wise context

# ============= Request/Response Models =============
class RoleModel(BaseModel):
    grade: Optional[int] = Field(None, description="Student grade filter")
    class_name: Optional[str] = Field(None, description="Class identifier")

    class Config:
        schema_extra = {
            "example": {"grade": 8, "class_name": "A"}
        }

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500, description="Natural language query")
    role: RoleModel = Field(..., description="User role and permissions")
    sessionId: str = Field(..., description="Session identifier")

    class Config:
        schema_extra = {
            "example": {
                "query": "Which students haven't submitted homework?",
                "role": {"grade": 8, "class_name": "A"},
                "sessionId": "uuid-string-here"
            }
        }

class QueryResult(BaseModel):
    condition: str = Field(..., description="Generated filter condition or JSON string")
    results: List[Dict[str, Any]] = Field(default_factory=list, description="Filtered results")
    count: int = Field(..., description="Number of results")
    timestamp: str = Field(..., description="Query execution time")
    raw_model_output: Optional[str] = Field(None, description="Raw output returned by the model (for debugging)")
    structured_condition: Optional[Dict[str, Any]] = Field(None, description="Parsed structured condition when provided by the model")

class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")
    code: str = Field(..., description="Error code")
    timestamp: str = Field(..., description="Error timestamp")

# ============= Health Check =============
@app.get(
    "/health",
    tags=["System"],
    summary="Health Check",
    responses={200: {"description": "Service is healthy"}}
)
async def health_check():
    """System health check endpoint"""
    return {
        "status": "healthy",
        "service": "Dumroo AI Backend",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get(
    "/",
    tags=["System"],
    summary="API Info",
    responses={200: {"description": "API information"}}
)
async def root():
    """Get API information"""
    return {
        "message": "Dumroo AI - Industry Ready Backend 🚀",
        "version": "2.0.0",
        "docs": "/docs",
        "status": "operational"
    }

# ============= Data Stats =============
@app.get(
    "/stats",
    tags=["Data"],
    summary="Get Data Statistics",
    responses={200: {"description": "Dataset statistics"}}
)
async def get_stats(grade: Optional[int] = None, class_name: Optional[str] = None):
    """Get statistics about the dataset"""
    try:
        if df.empty:
            raise HTTPException(status_code=500, detail="No data available")
        
        filtered_df = df.copy()
        
        if grade is not None:
            filtered_df = filtered_df[filtered_df["grade"] == grade]
        if class_name:
            filtered_df = filtered_df[filtered_df["class"] == class_name]
        
        stats = {
            "total_records": len(df),
            "filtered_records": len(filtered_df),
            "columns": list(df.columns),
            "grades": sorted(df["grade"].dropna().unique().tolist()),
            "classes": sorted(df["class"].unique().tolist()),
            "average_quiz_score": float(np.mean(df["quiz_score"].dropna())) if "quiz_score" in df.columns else None,
            "homework_submitted_count": len(df[df["homework_submitted"] == "Yes"]) if "homework_submitted" in df.columns else None,
        }
        
        return stats
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve statistics")

# ============= Query Handler =============
@app.post(
    "/query",
    response_model=QueryResult,
    tags=["Query"],
    summary="Execute Natural Language Query",
)
async def handle_query(req: QueryRequest):
    """
    Execute a natural language query against student data.
    Logs key checkpoints:
      1️⃣ Incoming request from frontend
      2️⃣ Response from AI (Gemini)
      3️⃣ Final response returned to frontend
    """
    try:
        if df.empty:
            raise HTTPException(status_code=500, detail="No data available")

        # 1️⃣ ==== FRONTEND INPUT ====
        logger.debug("\n🟡 ===== FRONTEND → BACKEND REQUEST =====")
        logger.debug(f"Query: {req.query}")
        logger.debug(f"Role: grade={req.role.grade}, class={req.role.class_name}")
        logger.debug(f"Session ID: {req.sessionId}")

        session_id = req.sessionId
        user_query = req.query.strip()
        admin_role = req.role

        if session_id not in session_agents:
            session_agents[session_id] = QueryAgent()
        agent = session_agents[session_id]

        scoped_df = filter_data_by_role(
            df.copy(),
            {"grade": admin_role.grade, "class": admin_role.class_name}
        )
        if scoped_df.empty:
            logger.warning("⚠️ No records for the given role scope.")
            return QueryResult(condition="", results=[], count=0, timestamp=datetime.now().isoformat())

        # 2️⃣ ==== AI INTERPRETATION ====
        condition_resp = agent.get_condition(user_query, list(scoped_df.columns))
        raw_model_output = condition_resp.get("raw", "")
        parsed = condition_resp.get("parsed", {"type": "filter", "expr": ""})

        logger.debug("\n🧠 ===== AI MODEL RESPONSE =====")
        logger.debug(f"Raw Output: {raw_model_output}")
        logger.debug(f"Parsed Object: {json.dumps(parsed, indent=2)}")

        result_df = scoped_df.copy()
        condition_str = ""
        structured_cond_obj = None

        # 3️⃣ ==== APPLY CONDITION TO DATA ====
        try:
            if isinstance(parsed, dict):
                structured_cond_obj = parsed
                typ = parsed.get("type", "filter")

                if typ == "filter":
                    expr = parsed.get("expr", "")
                    expr = expr.replace("class", "grade") if re.search(r"class\s*==\s*\d", expr) else expr
                    result_df = scoped_df.query(expr) if expr else scoped_df
                    condition_str = expr

                    # Smart topper inference
                    if any(k in user_query.lower() for k in ["topper", "highest", "best", "top student"]) \
                            and "quiz_score" in result_df.columns:
                        mv = result_df["quiz_score"].max()
                        result_df = result_df[result_df["quiz_score"] == mv]
                        logger.debug("🧩 Auto-applied topper logic on filtered subset.")

                elif typ in ("agg", "lookup_conditional"):
                    op = parsed.get("op")
                    col = parsed.get("column") or parsed.get("lookup_by_max") or "quiz_score"
                    group_by = parsed.get("group_by")
                    condition = parsed.get("condition")

                    if typ == "lookup_conditional" and condition:
                        cond_expr = condition.strip()
                        cond_expr = cond_expr.replace("class", "grade") if re.search(r"class\s*==\s*\d", cond_expr) else cond_expr
                        try:
                            subset_df = scoped_df.query(cond_expr)
                            if not subset_df.empty and col in subset_df.columns:
                                mv = subset_df[col].max()
                                result_df = subset_df[subset_df[col] == mv]
                            else:
                                result_df = scoped_df
                        except Exception as e:
                            logger.warning(f"lookup_conditional failed: {e}")
                            result_df = scoped_df

                    elif op == "global_max" and col in scoped_df.columns:
                        mv = scoped_df[col].max()
                        result_df = scoped_df[scoped_df[col] == mv]

                    elif op == "global_min" and col in scoped_df.columns:
                        mv = scoped_df[col].min()
                        result_df = scoped_df[scoped_df[col] == mv]

                    elif op == "group_max" and group_by in scoped_df.columns and col in scoped_df.columns:
                        result_df = scoped_df[
                            scoped_df[col] == scoped_df.groupby(group_by)[col].transform("max")
                        ]

                    elif op == "group_min" and group_by in scoped_df.columns and col in scoped_df.columns:
                        result_df = scoped_df[
                            scoped_df[col] == scoped_df.groupby(group_by)[col].transform("min")
                        ]

                    else:
                        q = user_query.lower()
                        if any(word in q for word in ["topper", "highest", "best"]) and "quiz_score" in scoped_df.columns:
                            if "class" in q or "section" in q:
                                result_df = scoped_df[
                                    scoped_df["quiz_score"] == scoped_df.groupby("class")["quiz_score"].transform("max")
                                ]
                            elif "grade" in q or re.search(r"\b\d+th\b", q):
                                result_df = scoped_df[
                                    scoped_df["quiz_score"] == scoped_df.groupby("grade")["quiz_score"].transform("max")
                                ]
                            else:
                                mv = scoped_df["quiz_score"].max()
                                result_df = scoped_df[scoped_df["quiz_score"] == mv]
                        else:
                            result_df = scoped_df

                    condition_str = json.dumps(parsed)

            else:
                condition_str = str(parsed)
                if condition_str:
                    try:
                        result_df = scoped_df.query(condition_str)
                    except Exception:
                        result_df = scoped_df

        except Exception as e:
            logger.error(f"Condition parsing failed: {e}")
            result_df = scoped_df

        # 4️⃣ ==== FINAL RESPONSE ====
        response = QueryResult(
            condition=condition_str or json.dumps(structured_cond_obj) if structured_cond_obj else condition_str,
            results=result_df.to_dict(orient="records"),
            count=len(result_df),
            timestamp=datetime.now().isoformat(),
            raw_model_output=raw_model_output,
            structured_condition=structured_cond_obj,
        )

        logger.debug("\n📤 ===== BACKEND → FRONTEND RESPONSE =====")
        logger.debug(f"Condition: {response.condition}")
        logger.debug(f"Count: {response.count}")
        logger.debug(f"Sample Result: {json.dumps(response.results[:2], indent=2)}")  # show first 2 for readability

        logger.info(f"✅ Query completed: {user_query} → {response.count} result(s)")
        return response

    except Exception as e:
        logger.error(f"Query error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process query: {str(e)}")

def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            code="HTTP_ERROR",
            timestamp=datetime.now().isoformat()
        ).model_dump()
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Dumroo AI Backend started successfully")
