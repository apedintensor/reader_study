# backend/app/crud/crud_assessment.py
from sqlalchemy.orm import Session
from app.models import models
from app.schemas import schemas
from typing import List, Optional

class AssessmentCRUD:
    def get(self, db: Session, assessment_id: int):
        return db.query(models.Assessment).filter(models.Assessment.id == assessment_id).first()

    def get_multi_by_user(self, db: Session, user_id: int, skip: int = 0, limit: int = 100):
        return db.query(models.Assessment).filter(models.Assessment.user_id == user_id).offset(skip).limit(limit).all()

    def get_multi_by_case(self, db: Session, case_id: int, skip: int = 0, limit: int = 100):
        return db.query(models.Assessment).filter(models.Assessment.case_id == case_id).offset(skip).limit(limit).all()

    def get_multi(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(models.Assessment).offset(skip).limit(limit).all()

    def create(self, db: Session, assessment: schemas.AssessmentCreate):
        db_assessment = models.Assessment(**assessment.model_dump())
        db.add(db_assessment)
        db.commit()
        db.refresh(db_assessment)
        return db_assessment

assessment = AssessmentCRUD()
