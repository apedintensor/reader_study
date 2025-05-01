# backend/app/main.py
from fastapi import FastAPI
from app.api.routes import api_router
from app.db.session import engine
from app.db.base import Base

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Reader Study API")

app.include_router(api_router)