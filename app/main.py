# backend/app/main.py
import asyncio
from fastapi import FastAPI
from app.api.routes import api_router
from app.auth.routes import auth_router
from app.auth.db import engine as async_engine
from app.db.base import Base

# Create an async function to create tables
async def create_db_and_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Create FastAPI app
app = FastAPI(title="Reader Study API")

# Include the authentication router
app.include_router(auth_router, prefix="/auth", tags=["auth"])
# Include the main API router
app.include_router(api_router)

# Add startup event to create tables
@app.on_event("startup")
async def on_startup():
    await create_db_and_tables()