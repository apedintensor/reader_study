# backend/app/crud/crud_diagnosis.py
from sqlalchemy.orm import Session
from app.models import models
from app.schemas import schemas
from typing import List

def get_diagnosis(db: Session, diagnosis_id: int):
    return db.query(models.Diagnosis).filter(models.Diagnosis.id == diagnosis_id).first()

def get_diagnoses_by_assessment(db: Session, assessment_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Diagnosis).filter(models.Diagnosis.assessment_id == assessment_id).offset(skip).limit(limit).all()

def create_diagnosis(db: Session, diagnosis: schemas.DiagnosisCreate):
    db_diagnosis = models.Diagnosis(**diagnosis.model_dump()) # Pydantic v2
    db.add(db_diagnosis)
    db.commit()
    db.refresh(db_diagnosis)
    return db_diagnosis

# Update/Delete as needed

diagnosis = {
    "get": get_diagnosis,
    "get_multi_by_assessment": get_diagnoses_by_assessment,
    "create": create_diagnosis,
}
