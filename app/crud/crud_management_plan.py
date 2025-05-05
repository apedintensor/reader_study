# backend/app/crud/crud_management_plan.py
from sqlalchemy.orm import Session
from app.models import models
from app.schemas import schemas

class ManagementPlanCRUD:
    def get(self, db: Session, plan_id: int):
        return db.query(models.ManagementPlan).filter(models.ManagementPlan.id == plan_id).first()

    def get_by_assessment(self, db: Session, assessment_id: int):
        # Assuming one plan per assessment due to unique constraint
        return db.query(models.ManagementPlan).filter(models.ManagementPlan.assessment_id == assessment_id).first()

    def create(self, db: Session, plan: schemas.ManagementPlanCreate):
        db_plan = models.ManagementPlan(**plan.model_dump()) # Pydantic v2
        db.add(db_plan)
        db.commit()
        db.refresh(db_plan)
        return db_plan

management_plan = ManagementPlanCRUD()
