# backend/app/api/endpoints/case_metadata.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas
from app.api import deps

router = APIRouter()

@router.get("/case/{case_id}", response_model=schemas.CaseMetaDataRead)
def read_case_metadata_by_case(
    case_id: int,
    db: Session = Depends(deps.get_db),
):
    """Get metadata for a specific case."""
    db_metadata = crud.case_metadata.get_by_case(db=db, case_id=case_id)
    if db_metadata is None:
        raise HTTPException(status_code=404, detail="Metadata not found for this case")
    return db_metadata

@router.post("/case/{case_id}", response_model=schemas.CaseMetaDataRead, status_code=201)
def create_case_metadata(
    case_id: int,
    *, # Enforces keyword-only arguments
    db: Session = Depends(deps.get_db),
    metadata_in: schemas.CaseMetaDataCreate
):
    """Create new metadata for a case."""
    # Check if case exists
    db_case = crud.case.get(db=db, case_id=case_id)
    if not db_case:
        raise HTTPException(status_code=404, detail="Case not found")
    # Check if metadata already exists for this case
    existing_metadata = crud.case_metadata.get_by_case(db=db, case_id=case_id)
    if existing_metadata:
        raise HTTPException(status_code=400, detail="Metadata already exists for this case")

    metadata = crud.case_metadata.create(db=db, metadata=metadata_in, case_id=case_id)
    return metadata

# Add GET by ID, PUT, DELETE if needed
