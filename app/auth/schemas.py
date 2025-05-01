# backend/app/auth/schemas.py
from typing import Optional
from datetime import datetime

from fastapi_users import schemas
from pydantic import EmailStr, Field


class UserRead(schemas.BaseUser[int]):
    id: int
    email: EmailStr
    role_id: Optional[int] = None
    age_bracket: Optional[str] = None
    gender: Optional[str] = None
    years_experience: Optional[int] = None
    years_derm_experience: Optional[int] = None
    created_at: datetime
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False

    class Config:
        from_attributes = True


class UserCreate(schemas.BaseUserCreate):
    email: EmailStr
    password: str
    role_id: Optional[int] = None
    age_bracket: Optional[str] = None
    gender: Optional[str] = None
    years_experience: Optional[int] = None
    years_derm_experience: Optional[int] = None
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False


class UserUpdate(schemas.BaseUserUpdate):
    password: Optional[str] = None
    email: Optional[EmailStr] = None
    role_id: Optional[int] = None
    age_bracket: Optional[str] = None
    gender: Optional[str] = None
    years_experience: Optional[int] = None
    years_derm_experience: Optional[int] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    is_verified: Optional[bool] = None