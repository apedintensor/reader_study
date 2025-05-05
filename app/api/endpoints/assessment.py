# backend/app/api/endpoints/assessment.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import select

from app import crud
from app.schemas import schemas as app_schemas
from app.api import deps
from app.models.models import Assessment

router = APIRouter()

@router.get("/", response_model=List[app_schemas.AssessmentRead])
def read_assessments(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100
):
    """Retrieve assessments."""
    assessments = crud.assessment.get_multi(db=db, skip=skip, limit=limit)
    return assessments

@router.get("/user/{user_id}", response_model=List[app_schemas.AssessmentRead])
def read_user_assessments(
    user_id: int,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100
):
    """Retrieve assessments for a specific user."""
    assessments = crud.assessment.get_multi_by_user(db=db, user_id=user_id, skip=skip, limit=limit)
    return assessments

@router.get("/case/{case_id}", response_model=List[app_schemas.AssessmentRead])
def read_case_assessments(
    case_id: int,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100
):
    """Retrieve assessments for a specific case."""
    assessments = crud.assessment.get_multi_by_case(db=db, case_id=case_id, skip=skip, limit=limit)
    return assessments

@router.get("/{user_id}/{case_id}/{is_post_ai}", response_model=app_schemas.AssessmentRead)
def read_assessment(
    user_id: int,
    case_id: int,
    is_post_ai: bool,
    db: Session = Depends(deps.get_db)
):
    """Retrieve a specific assessment."""
    assessment = crud.assessment.get(db=db, user_id=user_id, case_id=case_id, is_post_ai=is_post_ai)
    if assessment is None:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return assessment

@router.post("/", response_model=app_schemas.AssessmentRead, status_code=201)
async def create_assessment(
    *,
    db: Session = Depends(deps.get_db),
    assessment_in: app_schemas.AssessmentCreate
):
    """Create new assessment."""
    # Check if assessment already exists
    existing_assessment = crud.assessment.get(
        db=db, 
        user_id=assessment_in.user_id, 
        case_id=assessment_in.case_id, 
        is_post_ai=assessment_in.is_post_ai
    )
    if existing_assessment:
        raise HTTPException(
            status_code=400,
            detail="An assessment with these keys already exists"
        )
    
    # For post-AI assessments, ensure pre-AI assessment exists
    if assessment_in.is_post_ai:
        # Query for pre-AI assessment
        stmt = select(Assessment).where(
            Assessment.user_id == assessment_in.user_id,
            Assessment.case_id == assessment_in.case_id,
            Assessment.is_post_ai == False
        )
        pre_assessment = db.execute(stmt).scalar_one_or_none()

        if not pre_assessment:
            raise HTTPException(
                status_code=400,
                detail="Cannot create post-AI assessment without corresponding pre-AI assessment"
            )
    
    assessment = crud.assessment.create(db=db, assessment=assessment_in)
    return assessment
