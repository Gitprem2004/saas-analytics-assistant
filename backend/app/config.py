import os
from typing import List
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # API Keys
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", " ")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./saas_analytics.db")
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # CORS
    @property
    def CORS_ORIGINS(self) -> List[str]:
        origins = [
            "http://localhost:3000",
            "http://localhost:8000",
        ]
        
        # Add production frontend URL from environment
        frontend_url = os.getenv("http://localhost:8000", "")
        if frontend_url:
            origins.append(frontend_url)
            
        return origins

settings = Settings()