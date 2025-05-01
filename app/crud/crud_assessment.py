# backend/app/crud/crud_assessment.py
from sqlalchemy.orm import Session
from app.models import models
from app.schemas import schemas
from typing import List, Optional

def get_assessment(db: Session, assessment_id: int):
    return db.query(models.Assessment).filter(models.Assessment.id == assessment_id).first()

def get_assessments_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Assessment).filter(models.Assessment.user_id == user_id).offset(skip).limit(limit).all()

def get_assessments_by_case(db: Session, case_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Assessment).filter(models.Assessment.case_id == case_id).offset(skip).limit(limit).all()

def get_assessments(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Assessment).offset(skip).limit(limit).all()

def create_assessment(db: Session, assessment: schemas.AssessmentCreate):
    db_assessment = models.Assessment(**assessment.model_dump()) # Pydantic v2
    db.add(db_assessment)
    db.commit()
    db.refresh(db_assessment)
    # Note: Creating related Diagnoses and ManagementPlan might happen separately
    return db_assessment

# Update and Delete functions can be added if needed

assessment = {
    "get": get_assessment,
    "get_multi_by_user": get_assessments_by_user,
    "get_multi_by_case": get_assessments_by_case,
    "get_multi": get_assessments,
    "create": create_assessment,
}
