from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from .services.ai_service import SaaSAnalyticsAI
from .services.data_generator import generate_sample_data
from .database import get_db, create_tables
from .models.saas_models import User
from .config import settings
from fastapi.responses import JSONResponse
from fastapi import Request
from .config import settings


load_dotenv()

app = FastAPI(
    title="SaaS Analytics Assistant API",
    description="AI-powered analytics for SaaS businesses",
    version="0.115.0"
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://saas-analytics-assistant.vercel.app",
        "https://*.vercel.app",  # All Vercel preview deployments
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Initialize AI service
ai_service = SaaSAnalyticsAI()

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    success: bool
    result: dict = None
    error: str = None

@app.on_event("startup")
async def startup_event():
    create_tables()

@app.get("/")
async def root():
    return {"message": "SaaS Analytics Assistant API is running!"}

@app.post("/api/query", response_model=QueryResponse)
async def analyze_query(request: QueryRequest, db: Session = Depends(get_db)):
    try:
        # Generate SQL from natural language
        sql_query = ai_service.generate_sql_query(request.question)
        
        # Execute query
        query_result = ai_service.execute_query(db, sql_query)
        
        # Generate insights
        insights = ai_service.generate_insights(request.question, query_result)
        
        # Format response
        result = {
            "sql_query": sql_query,
            "data": query_result["data"],
            "type": query_result["type"],
            "insights": insights,
            "row_count": query_result.get("row_count", 0)
        }
        
        return QueryResponse(success=True, result=result)
        
    except Exception as e:
        return QueryResponse(success=False, error=str(e))


@app.post("/api/generate-data")
async def generate_data(db: Session = Depends(get_db)):
    try:
        result = generate_sample_data(db)
        return {"success": True, "generated": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/initialize-database")
async def initialize_database(db: Session = Depends(get_db)):
    """Initialize database with sample data (for first-time deployment)"""
    try:
        # Check if already has data
        from sqlalchemy import select
        result = db.execute(select(User)).first()
        
        if result:
            user_count = db.query(User).count()
            return {
                "success": True, 
                "message": "Database already initialized", 
                "user_count": user_count
            }
        
        # Generate sample data
        generated = generate_sample_data(db)
        return {
            "success": True, 
            "message": "Database initialized successfully", 
            "generated": generated
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# Update CORS middleware:
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://saas-analytics-assistant.vercel.app",
        "https://*.vercel.app",  # All Vercel preview deployments
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False, 
            "error": "An unexpected error occurred. Please try again."
        }
    )