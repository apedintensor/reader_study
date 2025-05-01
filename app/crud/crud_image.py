# backend/app/crud/crud_image.py
from sqlalchemy.orm import Session
from app.models import models
from app.schemas import schemas
from typing import List

def get_image(db: Session, image_id: int):
    return db.query(models.Image).filter(models.Image.id == image_id).first()

def get_images_by_case(db: Session, case_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Image).filter(models.Image.case_id == case_id).offset(skip).limit(limit).all()

def create_image(db: Session, image: schemas.ImageCreate):
    db_image = models.Image(**image.model_dump()) # Pydantic v2
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image

# Update/Delete as needed

image = {
    "get": get_image,
    "get_multi_by_case": get_images_by_case,
    "create": create_image,
}
