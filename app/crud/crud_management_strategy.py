# backend/app/crud/crud_management_strategy.py
from sqlalchemy.orm import Session
from app.models import models
from app.schemas import schemas

def get_management_strategy(db: Session, strategy_id: int):
    return db.query(models.ManagementStrategy).filter(models.ManagementStrategy.id == strategy_id).first()

def get_management_strategy_by_name(db: Session, name: str):
    return db.query(models.ManagementStrategy).filter(models.ManagementStrategy.name == name).first()

def get_management_strategies(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.ManagementStrategy).offset(skip).limit(limit).all()

def create_management_strategy(db: Session, strategy: schemas.ManagementStrategyCreate):
    db_strategy = models.ManagementStrategy(name=strategy.name)
    db.add(db_strategy)
    db.commit()
    db.refresh(db_strategy)
    return db_strategy

# Update/Delete as needed

management_strategy = {
    "get": get_management_strategy,
    "get_by_name": get_management_strategy_by_name,
    "get_multi": get_management_strategies,
    "create": create_management_strategy,
}
