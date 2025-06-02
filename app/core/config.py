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


class Settings(BaseSettings):
    # Basic settings
    PROJECT_NAME: str = "Reader Study Web API"
    API_V1_STR: str = "/api/v1"
    
    # Security settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey")
    JWT_ALGORITHM: str = "HS256"
    JWT_LIFETIME_SECONDS: int = 3600 * 24 * 7  # 1 week
    
    # Database settings
    # Determine database URIs based on whether DATABASE_URL is set (for Render/PostgreSQL)
    if DATABASE_URL:
        # Ensure it's a PostgreSQL URL for Render
        if DATABASE_URL.startswith("postgres://"):
            ASYNC_DB_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
            SYNC_DB_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1) # Or psycopg
        elif DATABASE_URL.startswith("postgresql://"): # Already in a compatible format for replacement
            ASYNC_DB_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
            SYNC_DB_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1) # Or psycopg
        else: # Fallback or raise error if DATABASE_URL is not a postgres URL
            # For simplicity, falling back to SQLite if DATABASE_URL is set but not recognized as postgres
            # In a real scenario, you might want to raise an error here.
            print(f"Warning: DATABASE_URL is set but not recognized as a PostgreSQL URL: {DATABASE_URL}. Falling back to SQLite.")
            ASYNC_DB_URL = "sqlite+aiosqlite:///./test.db"
            SYNC_DB_URL = "sqlite:///./test.db"
        
        SQLALCHEMY_ASYNC_DATABASE_URI: str = ASYNC_DB_URL
        SQLALCHEMY_SYNC_DATABASE_URI: str = SYNC_DB_URL
    else:
        # Fallback to SQLite for local development if DATABASE_URL is not set
        SQLALCHEMY_ASYNC_DATABASE_URI: str = os.getenv(
            "ASYNC_DATABASE_URI", "sqlite+aiosqlite:///./test.db"
        )
        SQLALCHEMY_SYNC_DATABASE_URI: str = os.getenv(
            "SYNC_DATABASE_URI", "sqlite:///./test.db"
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