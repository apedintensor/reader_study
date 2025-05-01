# backend/app/crud/crud_case_metadata.py
from sqlalchemy.orm import Session
from app.models import models
from app.schemas import schemas

def get_case_metadata(db: Session, metadata_id: int):
    return db.query(models.CaseMetaData).filter(models.CaseMetaData.id == metadata_id).first()

def get_case_metadata_by_case(db: Session, case_id: int):
    # Assuming one metadata per case due to unique constraint
    return db.query(models.CaseMetaData).filter(models.CaseMetaData.case_id == case_id).first()

def create_case_metadata(db: Session, metadata: schemas.CaseMetaDataCreate, case_id: int):
    db_metadata = models.CaseMetaData(**metadata.model_dump(), case_id=case_id) # Pydantic v2
    db.add(db_metadata)
    db.commit()
    db.refresh(db_metadata)
    return db_metadata

# Update/Delete as needed

case_metadata = {
    "get": get_case_metadata,
    "get_by_case": get_case_metadata_by_case,
    "create": create_case_metadata,
}
