"""Application configuration via Pydantic Settings (v2 friendly).

Refactored to avoid unannotated class attributes that Pydantic interpreted as
fields (causing PydanticUserError in production).
"""
import os
import json
from typing import List, Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    # Basic
    PROJECT_NAME: str = "Reader Study Web API"
    API_V1_STR: str = "/api/v1"

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey")
    JWT_ALGORITHM: str = "HS256"
    JWT_LIFETIME_SECONDS: int = 3600 * 24 * 7

    # Source DB URL (raw) – optional so we can derive URIs post-init
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")

    # Computed/derived SQLAlchemy URIs (populated in model_post_init if None)
    SQLALCHEMY_ASYNC_DATABASE_URI: Optional[str] = None
    SQLALCHEMY_SYNC_DATABASE_URI: Optional[str] = None

    # CORS (store raw string to avoid Pydantic attempting JSON list parse first)
    CORS_ORIGINS_RAW: Optional[str] = os.getenv("CORS_ORIGINS", "*")

    @property
    def cors_origins(self) -> List[str]:
        """Return parsed CORS origins as list.

        Supports:
        - '*' or empty -> ['*']
        - JSON array string
        - Comma-separated list
        - Single origin
        """
        raw = (self.CORS_ORIGINS_RAW or "").strip()
        if not raw or raw == "*":
            return ["*"]
        if raw.startswith("[") and raw.endswith("]"):
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, list) and all(isinstance(i, str) for i in parsed):
                    return parsed or ["*"]
            except Exception:
                pass
        if "," in raw:
            parts = [p.strip() for p in raw.split(",") if p.strip()]
            return parts or ["*"]
        return [raw]

    # Superuser bootstrap
    SUPERUSER_EMAIL: str = os.getenv("SUPERUSER_EMAIL", "admin@example.com")
    SUPERUSER_PASSWORD: str = os.getenv("SUPERUSER_PASSWORD", "adminpassword")

    # Media
    IMAGE_BASE_URL: str = os.getenv("IMAGE_BASE_URL", "")

    # Game config
    GAME_BLOCK_SIZE: int = int(os.getenv("GAME_BLOCK_SIZE", "2"))

    model_config = {
        "case_sensitive": True,
        "env_file": ".env",
    }

    def model_post_init(self, __context):  # pydantic v2 hook
        # If DATABASE_URL provided, derive sync/async variants if not already set
        if self.DATABASE_URL:
            url = self.DATABASE_URL
            if url.startswith("postgres://"):
                async_url = url.replace("postgres://", "postgresql+asyncpg://", 1)
                sync_url = url.replace("postgres://", "postgresql+psycopg2://", 1)
            elif url.startswith("postgresql://"):
                async_url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
                sync_url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
            else:
                # Fallback to SQLite if unexpected scheme
                print(
                    f"Warning: DATABASE_URL not recognized as PostgreSQL ({url}); falling back to SQLite."
                )
                async_url = "sqlite+aiosqlite:///./test.db"
                sync_url = "sqlite:///./test.db"
            if not self.SQLALCHEMY_ASYNC_DATABASE_URI:
                self.SQLALCHEMY_ASYNC_DATABASE_URI = async_url
            if not self.SQLALCHEMY_SYNC_DATABASE_URI:
                self.SQLALCHEMY_SYNC_DATABASE_URI = sync_url

        # Final fallback if still unset
        if not self.SQLALCHEMY_ASYNC_DATABASE_URI:
            self.SQLALCHEMY_ASYNC_DATABASE_URI = os.getenv(
                "ASYNC_DATABASE_URI", "sqlite+aiosqlite:///./test.db"
            )
        if not self.SQLALCHEMY_SYNC_DATABASE_URI:
            self.SQLALCHEMY_SYNC_DATABASE_URI = os.getenv(
                "SYNC_DATABASE_URI", "sqlite:///./test.db"
            )


settings = Settings()