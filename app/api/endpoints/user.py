# backend/app/api/endpoints/user.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Any

from app import crud, schemas, models
from app.api import deps

router = APIRouter()

@router.get("/", response_model=List[schemas.UserRead])
def read_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100
):
    """Retrieve users."""
    users = crud.user.get_multi(db, skip=skip, limit=limit)
    return users

@router.post("/", response_model=schemas.UserRead, status_code=201)
def create_user(
    *, # Enforces keyword-only arguments
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserCreate
):
    """Create new user."""
    # Check if user already exists by email
    existing_user = crud.user.get_by_email(db=db, email=user_in.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists")
    # Check if role exists
    db_role = crud.role.get(db=db, role_id=user_in.role_id)
    if not db_role:
        raise HTTPException(status_code=404, detail="Role not found")

    user = crud.user.create(db=db, user=user_in)
    return user

@router.get("/{user_id}", response_model=schemas.UserRead)
def read_user(
    user_id: int,
    db: Session = Depends(deps.get_db),
):
    """Get user by ID."""
    db_user = crud.user.get(db=db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.put("/{user_id}", response_model=schemas.UserRead)
def update_user(
    user_id: int,
    *, # Enforces keyword-only arguments
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserUpdate
):
    """Update a user."""
    db_user = crud.user.get(db=db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    # Check for email conflict if email is being updated
    if user_in.email and user_in.email != db_user.email:
        existing_user = crud.user.get_by_email(db=db, email=user_in.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="User with this email already exists")
    # Check if role exists if role_id is being updated
    if user_in.role_id and user_in.role_id != db_user.role_id:
        db_role = crud.role.get(db=db, role_id=user_in.role_id)
        if not db_role:
            raise HTTPException(status_code=404, detail="Role not found")

    user = crud.user.update(db=db, db_obj=db_user, obj_in=user_in)
    return user

@router.delete("/{user_id}", response_model=schemas.UserRead)
def delete_user(
    user_id: int,
    db: Session = Depends(deps.get_db),
):
    """Delete a user."""
    db_user = crud.user.get(db=db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    user = crud.user.remove(db=db, id=user_id)
    return user
