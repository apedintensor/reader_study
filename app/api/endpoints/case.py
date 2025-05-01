# backend/app/api/endpoints/case.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

# Change the import style
from app import crud
# Import the schemas module directly and alias it
from app.schemas import schemas as app_schemas
from app.api import deps
# Import the authentication dependency directly
from app.auth.manager import current_active_user
from app.auth.models import User

router = APIRouter()

# Use the alias for the response_model
@router.get("/", response_model=List[app_schemas.CaseRead])
def read_cases(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(current_active_user),  # Direct dependency on auth
    skip: int = 0,
    limit: int = 100
):
    """Retrieve cases."""
    cases = crud.case["get_multi"](db, skip=skip, limit=limit)
    return cases

# Use the alias for the response_model and input schema
@router.post("/", response_model=app_schemas.CaseRead, status_code=201)
def create_case(
    *, # Enforces keyword-only arguments
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(current_active_user),  # Direct dependency on auth
    case_in: app_schemas.CaseCreate
):
    """Create new case."""
    # Add checks (e.g., diagnosis term exists)
    case = crud.case["create"](db=db, case=case_in)
    return case

# Use the alias for the response_model
@router.get("/{case_id}", response_model=app_schemas.CaseRead)
def read_case(
    case_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(current_active_user),  # Direct dependency on auth
):
    """Get case by ID."""
    db_case = crud.case["get"](db=db, case_id=case_id)
    if db_case is None:
        raise HTTPException(status_code=404, detail="Case not found")
    return db_case

# Add PUT, DELETE if needed
