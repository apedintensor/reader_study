# backend/app/crud/crud_role.py
from sqlalchemy.orm import Session
from app.models import models
from app.schemas import schemas

def get_role(db: Session, role_id: int):
    return db.query(models.Role).filter(models.Role.id == role_id).first()

def get_role_by_name(db: Session, name: str):
    return db.query(models.Role).filter(models.Role.name == name).first()

def get_roles(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Role).offset(skip).limit(limit).all()

def create_role(db: Session, role: schemas.RoleCreate):
    db_role = models.Role(name=role.name)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role

# Update and Delete functions can be added similarly if needed

role = {
    "get": get_role,
    "get_by_name": get_role_by_name,
    "get_multi": get_roles,
    "create": create_role,
}
