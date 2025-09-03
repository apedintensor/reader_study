# backend/app/db/session.py
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from app.core.config import settings

# Create both sync and async engines
sync_engine = create_engine(
    settings.SQLALCHEMY_SYNC_DATABASE_URI, 
    connect_args={"check_same_thread": False}
)

async_engine = create_async_engine(
    settings.SQLALCHEMY_ASYNC_DATABASE_URI,
    connect_args={"check_same_thread": False}
)

# Create session factories
# Sync session for compatibility with existing code
SessionLocal = sessionmaker(bind=sync_engine, autoflush=False, autocommit=False)

# Async session for new code and fastapi-users
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine, 
    autoflush=False,
    autocommit=False,
    expire_on_commit=False
)

# Helper functions for dependency injection
def get_db():
    """Synchronous database session dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_async_db():
    """Asynchronous database session dependency"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()