# backend/app/api/endpoints/diagnosis_term.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app import crud
from app.schemas import schemas as app_schemas
from app.api import deps

router = APIRouter()

@router.get("/", response_model=List[app_schemas.DiagnosisTermRead])
def read_diagnosis_terms(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100
):
    """Retrieve diagnosis terms."""
    terms = crud.diagnosis_term.get_multi(db, skip=skip, limit=limit)
    return terms

@router.post("/", response_model=app_schemas.DiagnosisTermRead, status_code=201)
def create_diagnosis_term(
    *, # Enforces keyword-only arguments
    db: Session = Depends(deps.get_db),
    term_in: app_schemas.DiagnosisTermCreate
):
    """Create new diagnosis term."""
    # Check if term already exists by name
    existing_term = crud.diagnosis_term.get_by_name(db=db, name=term_in.name)
    if existing_term:
        raise HTTPException(status_code=400, detail="Diagnosis term with this name already exists")
    term = crud.diagnosis_term.create(db=db, term=term_in)
    return term

@router.get("/{term_id}", response_model=app_schemas.DiagnosisTermRead)
def read_diagnosis_term(
    term_id: int,
    db: Session = Depends(deps.get_db),
):
    """Get diagnosis term by ID."""
    db_term = crud.diagnosis_term.get(db=db, term_id=term_id)
    if db_term is None:
        raise HTTPException(status_code=404, detail="Diagnosis term not found")
    return db_term

# Add PUT, DELETE if needed
