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
    condition: str = Field(..., description="Generated pandas code")
    results: List[Dict[str, Any]] = Field(default_factory=list, description="Filtered results")
    count: int = Field(..., description="Number of results")
    timestamp: str = Field(..., description="Query execution time")
    raw_model_output: Optional[str] = Field(None, description="Raw Gemini output")
    structured_condition: Optional[Dict[str, Any]] = Field(None, description="Metadata about execution")

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
        "version": "3.0.0",
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
        "message": "Dumroo AI - Gemini-Powered Backend 🚀",
        "version": "3.0.0",
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
    Execute natural language query by generating and executing pandas code via Gemini.
    
    Flow:
    1. Get user query and apply role-based access control
    2. Ask Gemini to generate pandas code
    3. Execute code safely in isolated namespace
    4. Return results
    """
    try:
        if df.empty:
            raise HTTPException(status_code=500, detail="No data available")

        logger.info(f"📥 Query: '{req.query}' | Role: grade={req.role.grade}, class={req.role.class_name}")

        # Get or create session agent
        session_id = req.sessionId
        if session_id not in session_agents:
            session_agents[session_id] = QueryAgent()
        agent = session_agents[session_id]

        # Apply role-based access control
        scoped_df = filter_data_by_role(
            df.copy(),
            {"grade": req.role.grade, "class": req.role.class_name}
        )
        
        if scoped_df.empty:
            logger.warning("⚠️ No data available for this role scope")
            return QueryResult(
                condition="No data in scope",
                results=[],
                count=0,
                timestamp=datetime.now().isoformat(),
                raw_model_output="",
                structured_condition={"type": "empty_scope"}
            )

        # Get sample data for Gemini context
        sample_rows = f"Sample rows:\n{scoped_df.head(3).to_string()}"

        # Ask Gemini to generate pandas code
        pandas_code = agent.get_pandas_query(
            req.query, 
            list(scoped_df.columns),
            sample_rows
        )

        logger.info(f"🧠 Gemini generated code:\n{pandas_code}")

        # Security check: Block dangerous operations
        dangerous_keywords = [
            'import ', '__import__', 'eval(', 'exec(', 'compile(',
            'open(', 'file(', 'input(', '__builtins__',
            'os.', 'sys.', 'subprocess', 'shutil',
            'globals(', 'locals(', 'vars(', 'dir(',
            'getattr', 'setattr', 'delattr', 'hasattr'
        ]
        
        code_lower = pandas_code.lower()
        for keyword in dangerous_keywords:
            if keyword.lower() in code_lower:
                logger.error(f"🚨 Security: Blocked dangerous keyword '{keyword}'")
                raise HTTPException(
                    status_code=400,
                    detail=f"Security violation: Code contains forbidden operation"
                )

        # Execute the pandas code safely
        try:
            # Create isolated namespace with only necessary objects
            local_namespace = {
                'df': scoped_df,
                'pd': pd,
                'np': np,
                'result_df': None
            }
            
            # Execute code in isolated namespace
            exec(pandas_code, {'pd': pd, 'np': np, '__builtins__': __builtins__}, local_namespace)
            
            # Extract result
            result_df = local_namespace.get('result_df')
            
            # Validate result
            if result_df is None:
                logger.error("❌ Code didn't create result_df")
                raise ValueError("Generated code didn't produce result_df")
            
            if not isinstance(result_df, pd.DataFrame):
                logger.warning(f"⚠️ Result is {type(result_df)}, converting to DataFrame")
                if isinstance(result_df, pd.Series):
                    result_df = result_df.to_frame()
                else:
                    result_df = pd.DataFrame({'result': [result_df]})
            
            logger.info(f"✅ Code executed successfully: {len(result_df)} results")
            
        except Exception as exec_error:
            logger.error(f"❌ Code execution failed: {exec_error}")
            raise HTTPException(
                status_code=400,
                detail=f"Query execution failed: {str(exec_error)}"
            )

        # Build response
        response = QueryResult(
            condition=pandas_code,
            results=result_df.to_dict(orient="records"),
            count=len(result_df),
            timestamp=datetime.now().isoformat(),
            raw_model_output=pandas_code,
            structured_condition={
                "type": "pandas_code_execution",
                "code": pandas_code,
                "success": True
            },
        )

        logger.info(f"✅ Query completed: '{req.query}' → {response.count} result(s)")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

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
    logger.info("🚀 Dumroo AI Backend (Gemini-Powered) started successfully")
    logger.info("📊 Query processing: Gemini generates pandas code → Execute directly")