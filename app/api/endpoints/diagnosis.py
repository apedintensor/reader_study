# backend/app/api/endpoints/diagnosis.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app import crud
from app.schemas import schemas as app_schemas
from app.api import deps

router = APIRouter()

@router.get("/assessment/{assessment_id}", response_model=List[app_schemas.DiagnosisRead])
def read_diagnoses_by_assessment(
    assessment_id: int,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100
):
    """Retrieve diagnoses for a specific assessment."""
    diagnoses = crud.diagnosis["get_multi_by_assessment"](db=db, assessment_id=assessment_id, skip=skip, limit=limit)
    return diagnoses

@router.post("/", response_model=app_schemas.DiagnosisRead, status_code=201)
def create_diagnosis(
    *, # Enforces keyword-only arguments
    db: Session = Depends(deps.get_db),
    diagnosis_in: app_schemas.DiagnosisCreate
):
    """Create new diagnosis entry."""
    # Add checks (e.g., assessment exists, diagnosis term exists)
    diagnosis = crud.diagnosis["create"](db=db, diagnosis=diagnosis_in)
    return diagnosis

# Add GET by ID, PUT, DELETE if needed
