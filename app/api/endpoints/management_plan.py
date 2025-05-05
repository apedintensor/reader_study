# backend/app/api/endpoints/management_plan.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud
from app.schemas import schemas as app_schemas
from app.api import deps

router = APIRouter()

@router.get("/assessment/{user_id}/{case_id}/{is_post_ai}", response_model=app_schemas.ManagementPlanRead)
def read_management_plan_by_assessment(
    user_id: int,
    case_id: int,
    is_post_ai: bool,
    db: Session = Depends(deps.get_db),
):
    """Get management plan for a specific assessment."""
    # Get the assessment first
    db_assessment = crud.assessment.get_by_composite_key(
        db=db,
        user_id=user_id,
        case_id=case_id,
        is_post_ai=is_post_ai
    )
    if not db_assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    # Get the management plan for this assessment
    db_plan = db_assessment.management_plan
    if not db_plan:
        raise HTTPException(status_code=404, detail="Management plan not found for this assessment")
    return db_plan

@router.post("/", response_model=app_schemas.ManagementPlanRead, status_code=201)
def create_management_plan(
    *, # Enforces keyword-only arguments
    db: Session = Depends(deps.get_db),
    plan_in: app_schemas.ManagementPlanCreate
):
    """Create new management plan."""
    # Check if assessment exists using composite key
    db_assessment = crud.assessment.get_by_composite_key(
        db=db,
        user_id=plan_in.assessment_user_id,
        case_id=plan_in.assessment_case_id,
        is_post_ai=plan_in.assessment_is_post_ai
    )
    if not db_assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    # Check if strategy exists
    db_strategy = crud.management_strategy.get(db=db, strategy_id=plan_in.strategy_id)
    if not db_strategy:
        raise HTTPException(status_code=404, detail="Management strategy not found")
    
    # Check if plan already exists for this assessment
    if db_assessment.management_plan:
        raise HTTPException(status_code=400, detail="Management plan already exists for this assessment")
    
    plan = crud.management_plan.create(db=db, plan=plan_in)
    return plan
