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
    condition: str = Field(..., description="Generated filter condition")
    results: List[Dict[str, Any]] = Field(default_factory=list, description="Filtered results")
    count: int = Field(..., description="Number of results")
    timestamp: str = Field(..., description="Query execution time")

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
    responses={
        200: {"description": "Query executed successfully"},
        400: {"description": "Invalid request"},
        500: {"description": "Server error"}
    }
)
async def handle_query(req: QueryRequest):
    """
    Execute a natural language query against student data.
    
    The query is converted to a pandas filter condition using AI,
    and results are filtered based on user role.
    """
    try:
        if df.empty:
            raise HTTPException(status_code=500, detail="No data available")
        
        session_id = req.sessionId
        user_query = req.query
        admin_role = req.role
        
        logger.info(f"Query from session {session_id}: {user_query[:50]}...")
        
        if session_id not in session_agents:
            session_agents[session_id] = QueryAgent()

        agent = session_agents[session_id]
        scoped_df = filter_data_by_role(
            df.copy(),
            {"grade": admin_role.grade, "class": admin_role.class_name}
        )

        if scoped_df.empty:
            logger.warning(f"No data available for role: {admin_role}")
            return QueryResult(
                condition="",
                results=[],
                count=0,
                timestamp=datetime.now().isoformat()
            )

        condition = agent.get_condition(user_query, list(scoped_df.columns))
        
        if not condition or condition == "":
            result_df = scoped_df
        else:
            try:
                result_df = scoped_df.query(condition)
            except Exception as e:
                logger.warning(f"Failed to apply condition, returning all scoped results: {e}")
                result_df = scoped_df
        
        logger.info(f"Query returned {len(result_df)} results")
        
        return QueryResult(
            condition=condition,
            results=result_df.to_dict(orient="records"),
            count=len(result_df),
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Query error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process query: {str(e)}"
        )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
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
