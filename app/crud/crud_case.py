# backend/app/crud/crud_case.py
from sqlalchemy.orm import Session
from app.models import models
from app.schemas import schemas
from typing import List, Optional

def get_case(db: Session, case_id: int):
    # Eager load related data often needed with a case
    return db.query(models.Case).options(
        # Add eager loading as needed, e.g.:
        # joinedload(models.Case.images),
        # joinedload(models.Case.metadata),
        # joinedload(models.Case.ai_outputs)
    ).filter(models.Case.id == case_id).first()

def get_cases(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Case).offset(skip).limit(limit).all()

def create_case(db: Session, case: schemas.CaseCreate):
    db_case = models.Case(
        ground_truth_diagnosis_id=case.ground_truth_diagnosis_id,
        typical_diagnosis=case.typical_diagnosis,
    )
    db.add(db_case)
    db.commit()
    db.refresh(db_case)
    # Note: Creating related objects like CaseMetaData, Images, AIOutputs
    # might happen in separate steps or service layer logic.
    return db_case

# Update and Delete functions can be added similarly

case = {
    "get": get_case,
    "get_multi": get_cases,
    "create": create_case,
    # "update": update_case,
    # "remove": remove_case,
}
