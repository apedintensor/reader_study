# backend/app/crud/crud_diagnosis_term.py
from sqlalchemy.orm import Session
from app.models import models
from app.schemas import schemas

def get_diagnosis_term(db: Session, term_id: int):
    return db.query(models.DiagnosisTerm).filter(models.DiagnosisTerm.id == term_id).first()

def get_diagnosis_term_by_name(db: Session, name: str):
    return db.query(models.DiagnosisTerm).filter(models.DiagnosisTerm.name == name).first()

def get_diagnosis_terms(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.DiagnosisTerm).offset(skip).limit(limit).all()

def create_diagnosis_term(db: Session, term: schemas.DiagnosisTermCreate):
    db_term = models.DiagnosisTerm(name=term.name)
    db.add(db_term)
    db.commit()
    db.refresh(db_term)
    return db_term

# Update/Delete as needed

diagnosis_term = {
    "get": get_diagnosis_term,
    "get_by_name": get_diagnosis_term_by_name,
    "get_multi": get_diagnosis_terms,
    "create": create_diagnosis_term,
}
