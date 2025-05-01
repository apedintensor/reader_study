# backend/app/crud/crud_user.py
from sqlalchemy.orm import Session
from app.models import models
from app.schemas import schemas
from typing import Any, Dict, Optional, Union

# Basic password hashing - replace with a proper security utility like passlib
def get_password_hash(password: str) -> str:
    # In a real app, use bcrypt or similar
    return f"hashed_{password}"

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        password_hash=hashed_password,
        role_id=user.role_id,
        age_bracket=user.age_bracket,
        gender=user.gender,
        years_experience=user.years_experience,
        years_derm_experience=user.years_derm_experience,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(
    db: Session,
    db_obj: models.User,
    obj_in: Union[schemas.UserUpdate, Dict[str, Any]]
):
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.model_dump(exclude_unset=True) # Pydantic v2

    if "password" in update_data and update_data["password"]:
        hashed_password = get_password_hash(update_data["password"])
        del update_data["password"] # Don't store plain password
        update_data["password_hash"] = hashed_password

    for field, value in update_data.items():
        setattr(db_obj, field, value)

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def remove_user(db: Session, id: int):
    db_obj = db.query(models.User).get(id)
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj


user = {
    "get": get_user,
    "get_by_email": get_user_by_email,
    "get_multi": get_users,
    "create": create_user,
    "update": update_user,
    "remove": remove_user,
}
