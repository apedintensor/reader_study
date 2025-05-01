# backend/app/crud/crud_management_plan.py
from sqlalchemy.orm import Session
from app.models import models
from app.schemas import schemas

def get_management_plan(db: Session, plan_id: int):
    return db.query(models.ManagementPlan).filter(models.ManagementPlan.id == plan_id).first()

def get_management_plan_by_assessment(db: Session, assessment_id: int):
    # Assuming one plan per assessment due to unique constraint
    return db.query(models.ManagementPlan).filter(models.ManagementPlan.assessment_id == assessment_id).first()

def create_management_plan(db: Session, plan: schemas.ManagementPlanCreate):
    db_plan = models.ManagementPlan(**plan.model_dump()) # Pydantic v2
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan

# Update/Delete as needed

management_plan = {
    "get": get_management_plan,
    "get_by_assessment": get_management_plan_by_assessment,
    "create": create_management_plan,
}
