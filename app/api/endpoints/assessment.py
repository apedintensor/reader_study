# backend/app/api/endpoints/assessment.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app import crud, schemas
from app.api import deps

router = APIRouter()

@router.get("/", response_model=List[schemas.AssessmentRead])
def read_assessments(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100
):
    """Retrieve assessments."""
    assessments = crud.assessment.get_multi(db, skip=skip, limit=limit)
    return assessments

@router.post("/", response_model=schemas.AssessmentRead, status_code=201)
def create_assessment(
    *, # Enforces keyword-only arguments
    db: Session = Depends(deps.get_db),
    assessment_in: schemas.AssessmentCreate
):
    """Create new assessment."""
    # Add checks (e.g., user exists, case exists)
    assessment = crud.assessment.create(db=db, assessment=assessment_in)
    return assessment

@router.get("/{assessment_id}", response_model=schemas.AssessmentRead)
def read_assessment(
    assessment_id: int,
    db: Session = Depends(deps.get_db),
):
    """Get assessment by ID."""
    db_assessment = crud.assessment.get(db=db, assessment_id=assessment_id)
    if db_assessment is None:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return db_assessment

@router.get("/user/{user_id}", response_model=List[schemas.AssessmentRead])
def read_assessments_by_user(
    user_id: int,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100
):
    """Retrieve assessments for a specific user."""
    assessments = crud.assessment.get_multi_by_user(db=db, user_id=user_id, skip=skip, limit=limit)
    return assessments

@router.get("/case/{case_id}", response_model=List[schemas.AssessmentRead])
def read_assessments_by_case(
    case_id: int,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100
):
    """Retrieve assessments for a specific case."""
    assessments = crud.assessment.get_multi_by_case(db=db, case_id=case_id, skip=skip, limit=limit)
    return assessments

# Add PUT, DELETE if needed
