# backend/app/models/models.py
# Refactored models for clarity and optimization

from sqlalchemy import (
    Column, Integer, String, Boolean, Float, ForeignKey, DateTime, Text
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

# Import the User model from auth.models
from app.auth.models import User

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)

    users = relationship("User", back_populates="role")

class DiagnosisTerm(Base):
    __tablename__ = "diagnosis_terms"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)

    cases = relationship("Case", back_populates="ground_truth_diagnosis")
    ai_outputs = relationship("AIOutput", back_populates="prediction")
    diagnoses = relationship("Diagnosis", back_populates="diagnosis_term")

class Case(Base):
    __tablename__ = "cases"
    id = Column(Integer, primary_key=True, index=True)
    ground_truth_diagnosis_id = Column(Integer, ForeignKey("diagnosis_terms.id"))
    typical_diagnosis = Column(Boolean)
    created_at = Column(DateTime, default=datetime.utcnow)

    ground_truth_diagnosis = relationship("DiagnosisTerm", back_populates="cases")
    case_metadata_relation = relationship("CaseMetaData", back_populates="case", uselist=False)
    images = relationship("Image", back_populates="case")
    ai_outputs = relationship("AIOutput", back_populates="case")
    assessments = relationship("Assessment", back_populates="case")

class CaseMetaData(Base):
    __tablename__ = "case_metadata"
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False, unique=True)
    age = Column(Integer)
    gender = Column(String)
    fever_history = Column(Boolean)
    psoriasis_history = Column(Boolean)
    other_notes = Column(Text)

    case = relationship("Case", back_populates="case_metadata_relation")

class Image(Base):
    __tablename__ = "images"
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False)
    image_url = Column(String)

    case = relationship("Case", back_populates="images")

class AIOutput(Base):
    __tablename__ = "ai_outputs"
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False)
    rank = Column(Integer)
    prediction_id = Column(Integer, ForeignKey("diagnosis_terms.id"), nullable=False)
    confidence_score = Column(Float)

    case = relationship("Case", back_populates="ai_outputs")
    prediction = relationship("DiagnosisTerm", back_populates="ai_outputs")

class Assessment(Base):
    __tablename__ = "assessments"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False)
    is_post_ai = Column(Boolean)
    assessable_image_score = Column(Integer)
    confidence_level_top1 = Column(Integer)
    management_confidence = Column(Integer)
    certainty_level = Column(Integer)
    change_diagnosis_after_ai = Column(Boolean)
    change_management_after_ai = Column(Boolean)
    ai_usefulness = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="assessments")
    case = relationship("Case", back_populates="assessments")
    diagnoses = relationship("Diagnosis", back_populates="assessment")
    management_plan = relationship("ManagementPlan", back_populates="assessment", uselist=False)

class Diagnosis(Base):
    __tablename__ = "diagnoses"
    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    rank = Column(Integer)
    diagnosis_id = Column(Integer, ForeignKey("diagnosis_terms.id"), nullable=False)
    is_ground_truth = Column(Boolean)
    diagnosis_accuracy = Column(Integer)

    assessment = relationship("Assessment", back_populates="diagnoses")
    diagnosis_term = relationship("DiagnosisTerm", back_populates="diagnoses")

class ManagementStrategy(Base):
    __tablename__ = "management_strategies"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)

    management_plans = relationship("ManagementPlan", back_populates="strategy")

class ManagementPlan(Base):
    __tablename__ = "management_plans"
    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False, unique=True)
    strategy_id = Column(Integer, ForeignKey("management_strategies.id"), nullable=False)
    free_text = Column(String)
    quality_score = Column(Integer)

    assessment = relationship("Assessment", back_populates="management_plan")
    strategy = relationship("ManagementStrategy", back_populates="management_plans")

