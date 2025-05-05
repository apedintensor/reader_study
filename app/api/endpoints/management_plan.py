# backend/app/api/endpoints/management_plan.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud
from app.schemas import schemas as app_schemas
from app.api import deps

router = APIRouter()

@router.get("/assessment/{assessment_id}", response_model=app_schemas.ManagementPlanRead)
def read_management_plan_by_assessment(
    assessment_id: int,
    db: Session = Depends(deps.get_db),
):
    """Get management plan for a specific assessment."""
    db_plan = crud.management_plan.get_by_assessment(db=db, assessment_id=assessment_id)
    if db_plan is None:
        raise HTTPException(status_code=404, detail="Management plan not found for this assessment")
    return db_plan

@router.post("/", response_model=app_schemas.ManagementPlanRead, status_code=201)
def create_management_plan(
    *, # Enforces keyword-only arguments
    db: Session = Depends(deps.get_db),
    plan_in: app_schemas.ManagementPlanCreate
):
    """Create new management plan."""
    # Check if assessment exists
    db_assessment = crud.assessment.get(db=db, assessment_id=plan_in.assessment_id)
    if not db_assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    # Check if strategy exists
    db_strategy = crud.management_strategy.get(db=db, strategy_id=plan_in.strategy_id)
    if not db_strategy:
        raise HTTPException(status_code=404, detail="Management strategy not found")
    
    # Check if plan already exists for this assessment
    existing_plan = crud.management_plan.get_by_assessment(db=db, assessment_id=plan_in.assessment_id)
    if existing_plan:
        raise HTTPException(status_code=400, detail="Management plan already exists for this assessment")
    
    plan = crud.management_plan.create(db=db, plan=plan_in)
    return plan
