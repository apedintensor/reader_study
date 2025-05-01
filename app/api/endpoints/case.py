# backend/app/api/endpoints/case.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app import crud, schemas
from app.api import deps

router = APIRouter()

@router.get("/", response_model=List[schemas.CaseRead])
def read_cases(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100
):
    """Retrieve cases."""
    cases = crud.case.get_multi(db, skip=skip, limit=limit)
    return cases

@router.post("/", response_model=schemas.CaseRead, status_code=201)
def create_case(
    *, # Enforces keyword-only arguments
    db: Session = Depends(deps.get_db),
    case_in: schemas.CaseCreate
):
    """Create new case."""
    # Add checks (e.g., diagnosis term exists)
    case = crud.case.create(db=db, case=case_in)
    return case

@router.get("/{case_id}", response_model=schemas.CaseRead)
def read_case(
    case_id: int,
    db: Session = Depends(deps.get_db),
):
    """Get case by ID."""
    db_case = crud.case.get(db=db, case_id=case_id)
    if db_case is None:
        raise HTTPException(status_code=404, detail="Case not found")
    return db_case

# Add PUT, DELETE if needed
