# backend/app/api/routes.py
from fastapi import APIRouter

api_router = APIRouter()

@api_router.get("/ping")
def ping():
    return {"message": "pong"}