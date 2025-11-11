"""
Configuration module for Dumroo AI Backend
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # API Configuration
    api_title: str = "Dumroo AI - Industry Ready Backend"
    api_description: str = "AI-powered student data query system with advanced filtering"
    api_version: str = "2.0.0"
    
    # Server Configuration
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    
    # Environment
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = environment == "development"
    
    # CORS Configuration
    allowed_origins: list = os.getenv(
        "http://localhost:5173,http://localhost:3000,https://dumroo-ai.onrender.com"
    ).split(",")
    
    # Google Gemini API
    google_api_key: Optional[str] = os.getenv("GOOGLE_API_KEY")
    gemini_model: str = "gemini-flash-latest"
    
    # Data Configuration
    data_path: str = "data/students.csv"
    
    # Session Configuration
    max_session_history: int = 10
    max_concurrent_sessions: int = 1000
    
    # Logging Configuration
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.environment == "production"
    
    def validate_required_settings(self) -> None:
        """Validate that all required settings are configured"""
        if not self.google_api_key:
            raise ValueError("GOOGLE_API_KEY is required")
        
        if not self.allowed_origins:
            raise ValueError("ALLOWED_ORIGINS is required")

# Global settings instance
settings = Settings()
