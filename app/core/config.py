# app/core/config.py
import os
from typing import Any, Dict, Optional
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()


class Settings(BaseSettings):
    # Basic settings
    PROJECT_NAME: str = "Reader Study Web API"
    API_V1_STR: str = "/api/v1"
    
    # Security settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey")
    JWT_ALGORITHM: str = "HS256"
    JWT_LIFETIME_SECONDS: int = 3600 * 24 * 7  # 1 week
    
    # Database settings
    SQLALCHEMY_SYNC_DATABASE_URI: str = os.getenv(
        "SYNC_DATABASE_URI", "sqlite:///./test.db"
    )
    SQLALCHEMY_ASYNC_DATABASE_URI: str = os.getenv(
        "ASYNC_DATABASE_URI", "sqlite+aiosqlite:///./test.db"
    )
    
    # CORS settings
    CORS_ORIGINS: list = ["*"]  # In production, specify exact domain
    
    # User settings
    SUPERUSER_EMAIL: str = os.getenv("SUPERUSER_EMAIL", "admin@example.com")
    SUPERUSER_PASSWORD: str = os.getenv("SUPERUSER_PASSWORD", "adminpassword")
    
    # Additional settings can be added as needed
    
    class Config:
        case_sensitive = True
        env_file = ".env"


# Create a global settings object
settings = Settings()