# app/core/config.py
import os
from typing import Any, Dict, Optional
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Get the general database URL from the environment, if available
DATABASE_URL = os.getenv("DATABASE_URL")


def _get_database_urls() -> tuple[str, str]:
    """Get database URLs for async and sync connections."""
    if DATABASE_URL:
        # Ensure it's a PostgreSQL URL for Render
        if DATABASE_URL.startswith("postgres://"):
            async_url = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
            sync_url = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)
        elif DATABASE_URL.startswith("postgresql://"):
            async_url = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
            sync_url = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)
        else:
            # Fallback to SQLite if DATABASE_URL is set but not recognized as postgres
            print(f"Warning: DATABASE_URL is set but not recognized as a PostgreSQL URL: {DATABASE_URL}. Falling back to SQLite.")
            async_url = "sqlite+aiosqlite:///./test.db"
            sync_url = "sqlite:///./test.db"
        return async_url, sync_url
    else:
        # Fallback to SQLite for local development if DATABASE_URL is not set
        async_url = os.getenv("ASYNC_DATABASE_URI", "sqlite+aiosqlite:///./test.db")
        sync_url = os.getenv("SYNC_DATABASE_URI", "sqlite:///./test.db")
        return async_url, sync_url


class Settings(BaseSettings):
    # Basic settings
    PROJECT_NAME: str = "Reader Study Web API"
    API_V1_STR: str = "/api"  # Updated to /api
    
    # Security settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey")
    JWT_ALGORITHM: str = "HS256"
    JWT_LIFETIME_SECONDS: int = 3600 * 24 * 7  # 1 week
    
    # Database settings - properly typed
    SQLALCHEMY_ASYNC_DATABASE_URI: str = ""
    SQLALCHEMY_SYNC_DATABASE_URI: str = ""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set database URLs after initialization
        async_url, sync_url = _get_database_urls()
        self.SQLALCHEMY_ASYNC_DATABASE_URI = async_url
        self.SQLALCHEMY_SYNC_DATABASE_URI = sync_url
    
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