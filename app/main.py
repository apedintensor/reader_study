# backend/app/main.py
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from app.api.routes import api_router
from app.auth.routes import auth_router
from app.db.session import async_engine
from app.db.base import Base
from app.core.config import settings
from app.db.init_db import init_db

# Create FastAPI app
app = FastAPI(title=settings.PROJECT_NAME)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """
    Root endpoint that provides basic information about the API.
    """
    return {
        "title": settings.PROJECT_NAME,
        "description": "Backend API for Reader Study Web Application",
        "version": "1.0.0",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }

# Admin endpoint
@app.get("/admin", tags=["admin"])
async def admin():
    """
    Admin endpoint that redirects to the admin interface.
    In the future, this could be a protected admin interface.
    """
    # You can customize this to redirect to your admin UI when it's ready
    # For now, redirecting to API docs as placeholder
    return RedirectResponse(url="/docs")

# Include the authentication router
app.include_router(auth_router, prefix="/auth", tags=["auth"])
# Include the main API router
app.include_router(api_router)

# Add startup event to create tables and initialize data
@app.on_event("startup")
async def on_startup():
    # Initialize database with tables and initial data
    await init_db()

# Add shutdown event to close resources
@app.on_event("shutdown")
async def on_shutdown():
    # Close any open connections
    await async_engine.dispose()