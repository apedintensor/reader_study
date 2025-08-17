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


        # Map Fly.io / AWS style env vars if S3_* not explicitly set
        if not self.S3_ACCESS_KEY and os.getenv("AWS_ACCESS_KEY_ID"):
            self.S3_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
        if not self.S3_SECRET_KEY and os.getenv("AWS_SECRET_ACCESS_KEY"):
            self.S3_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
        if not self.S3_ENDPOINT and os.getenv("AWS_ENDPOINT_URL_S3"):
            # Fly Tigris provides an S3-compatible endpoint in AWS_ENDPOINT_URL_S3
            self.S3_ENDPOINT = os.getenv("AWS_ENDPOINT_URL_S3")
        if not self.S3_REGION and os.getenv("AWS_REGION"):
            self.S3_REGION = os.getenv("AWS_REGION")
        if not self.S3_BUCKET and os.getenv("BUCKET_NAME"):
            self.S3_BUCKET = os.getenv("BUCKET_NAME")
        if not self.STORAGE_PROVIDER and (self.S3_ENDPOINT or os.getenv("AWS_ENDPOINT_URL_S3")):
            self.STORAGE_PROVIDER = "tigris"  # sensible default for Fly object storage

    @property
    def storage_enabled(self) -> bool:
        return all([self.S3_BUCKET, self.S3_ACCESS_KEY, self.S3_SECRET_KEY, self.S3_ENDPOINT])
    
    # Raw CORS origins string from env (optional). We parse manually to avoid Pydantic attempting JSON first.
    CORS_ORIGINS_RAW: str | None = os.getenv("CORS_ORIGINS")

    @property
    def cors_origins(self) -> list[str]:
        raw = self.CORS_ORIGINS_RAW
        if not raw:
            return ["*"]
        raw = raw.strip()
        if raw.startswith("["):
            import json
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, list):
                    return [str(o).strip() for o in parsed if str(o).strip()]
            except Exception:
                pass
        return [o.strip() for o in raw.split(',') if o.strip()]
    
    # User settings
    SUPERUSER_EMAIL: str = os.getenv("SUPERUSER_EMAIL", "admin@example.com")
    SUPERUSER_PASSWORD: str = os.getenv("SUPERUSER_PASSWORD", "adminpassword")

    # Object storage (S3 / Tigris) settings (optional)
    # Set these as environment variables or Fly secrets when enabling external file storage
    STORAGE_PROVIDER: str | None = os.getenv("STORAGE_PROVIDER")  # e.g. "tigris" or "s3"
    S3_ENDPOINT: str | None = os.getenv("S3_ENDPOINT")  # e.g. https://fly.storage.tigris.dev
    S3_REGION: str | None = os.getenv("S3_REGION")      # e.g. "auto" or specific region
    S3_BUCKET: str | None = os.getenv("S3_BUCKET")
    S3_ACCESS_KEY: str | None = os.getenv("S3_ACCESS_KEY")
    S3_SECRET_KEY: str | None = os.getenv("S3_SECRET_KEY")
    S3_USE_PATH_STYLE: bool = os.getenv("S3_USE_PATH_STYLE", "true").lower() == "true"  # Tigris prefers path-style
    
    # Additional settings can be added as needed
    
    class Config:
        case_sensitive = True
        env_file = ".env"


# Create a global settings object
settings = Settings()