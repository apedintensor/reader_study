# backend/app/auth/models.py
from typing import Optional
from datetime import datetime

from fastapi_users.db import SQLAlchemyBaseUserTable
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.db.base import Base

class User(SQLAlchemyBaseUserTable[int], Base):
    # Change the table name to avoid conflicts with the existing User model
    __tablename__ = "auth_users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # The following fields are from our original User model
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)
    age_bracket = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    years_experience = Column(Integer, nullable=True)
    years_derm_experience = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    role = relationship("Role")
    # Remove the problematic relationship
    # We'll handle linking auth users to assessments separately if needed