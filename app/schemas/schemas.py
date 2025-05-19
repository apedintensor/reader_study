# backend/app/schemas/schemas.py
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import datetime

# Import User schemas from auth module
from app.auth.schemas import UserRead, UserCreate, UserUpdate

# Base Schemas (common fields)
class RoleBase(BaseModel):
    name: str

class DiagnosisTermBase(BaseModel):
    name: str

class CaseBase(BaseModel):
    ground_truth_diagnosis_id: int
    typical_diagnosis: bool

class CaseMetaDataBase(BaseModel):
    age: Optional[int] = None
    gender: Optional[str] = None
    fever_history: Optional[bool] = None
    psoriasis_history: Optional[bool] = None
    other_notes: Optional[str] = None

class ImageBase(BaseModel):
    image_url: str

class AIOutputBase(BaseModel):
    rank: Optional[int] = None
    confidence_score: Optional[float] = None

class AssessmentBase(BaseModel):
    user_id: int
    case_id: int
    is_post_ai: bool
    assessable_image_score: Optional[int] = None
    confidence_level_top1: Optional[int] = None
    management_confidence: Optional[int] = None
    certainty_level: Optional[int] = None
    ai_usefulness: Optional[str] = None

# Add AssessmentUpdate schema before AssessmentCreate
class AssessmentUpdate(BaseModel):
    assessable_image_score: Optional[int] = None
    confidence_level_top1: Optional[int] = None
    management_confidence: Optional[int] = None
    certainty_level: Optional[int] = None
    ai_usefulness: Optional[str] = None

class AssessmentCreate(AssessmentBase):
    pass

class DiagnosisBase(BaseModel):
    rank: int
    is_ground_truth: Optional[bool] = None
    diagnosis_accuracy: Optional[int] = None

class ManagementStrategyBase(BaseModel):
    name: str

class ManagementPlanBase(BaseModel):
    free_text: Optional[str] = None
    quality_score: Optional[int] = None

class ManagementPlanUpdate(BaseModel):
    strategy_id: Optional[int] = None
    free_text: Optional[str] = None
    quality_score: Optional[int] = None

class CaseBase(BaseModel):
    ground_truth_diagnosis_id: int
    typical_diagnosis: bool

class CaseMetaDataBase(BaseModel):
    age: Optional[int] = None
    gender: Optional[str] = None
    fever_history: Optional[bool] = None
    psoriasis_history: Optional[bool] = None
    other_notes: Optional[str] = None

class ImageBase(BaseModel):
    image_url: str

class AIOutputBase(BaseModel):
    rank: Optional[int] = None
    confidence_score: Optional[float] = None

class AssessmentBase(BaseModel):
    user_id: int
    case_id: int
    is_post_ai: bool
    assessable_image_score: Optional[int] = None
    confidence_level_top1: Optional[int] = None
    management_confidence: Optional[int] = None
    certainty_level: Optional[int] = None
    ai_usefulness: Optional[str] = None

# Add AssessmentUpdate schema before AssessmentCreate
class AssessmentUpdate(BaseModel):
    assessable_image_score: Optional[int] = None
    confidence_level_top1: Optional[int] = None
    management_confidence: Optional[int] = None
    certainty_level: Optional[int] = None
    ai_usefulness: Optional[str] = None

class AssessmentCreate(AssessmentBase):
    pass

class DiagnosisBase(BaseModel):
    rank: int
    is_ground_truth: Optional[bool] = None
    diagnosis_accuracy: Optional[int] = None

class ManagementStrategyBase(BaseModel):
    name: str

class ManagementPlanBase(BaseModel):
    free_text: Optional[str] = None
    quality_score: Optional[int] = None

class ManagementPlanUpdate(BaseModel):
    strategy_id: Optional[int] = None
    free_text: Optional[str] = None
    quality_score: Optional[int] = None

class ManagementPlanCreate(ManagementPlanBase):
    assessment_user_id: int
    assessment_case_id: int
    assessment_is_post_ai: bool
    strategy_id: int

# Schemas for Creation (inheriting from Base, adding specific fields)
class RoleCreate(RoleBase):
    pass

class DiagnosisTermCreate(DiagnosisTermBase):
    pass

class CaseCreate(CaseBase):
    pass

class CaseMetaDataCreate(CaseMetaDataBase):
    pass # Linked via Case creation

class ImageCreate(ImageBase):
    case_id: int

class AIOutputCreate(AIOutputBase):
    case_id: int
    prediction_id: int

class AssessmentCreate(AssessmentBase):
    pass

class DiagnosisCreate(DiagnosisBase):
    assessment_user_id: int
    assessment_case_id: int
    assessment_is_post_ai: bool
    diagnosis_id: int

class ManagementStrategyCreate(ManagementStrategyBase):
    pass

class ManagementPlanCreate(ManagementPlanBase):
    assessment_user_id: int
    assessment_case_id: int
    assessment_is_post_ai: bool
    strategy_id: int

# Schemas for Reading (inheriting from Base, adding ID and relationships)
class RoleRead(RoleBase):
    id: int

    class Config:
        from_attributes = True # Pydantic v2

class DiagnosisTermRead(DiagnosisTermBase):
    id: int

    class Config:
        from_attributes = True

class CaseMetaDataRead(CaseMetaDataBase):
    id: int
    case_id: int

    class Config:
        from_attributes = True

class ImageRead(ImageBase):
    id: int
    case_id: int

    class Config:
        from_attributes = True

class AIOutputRead(AIOutputBase):
    id: int
    case_id: int
    prediction_id: int
    prediction: DiagnosisTermRead # Nested prediction info

    class Config:
        from_attributes = True

class CaseRead(CaseBase):
    id: int
    created_at: datetime.datetime | None = None
    ground_truth_diagnosis_id: Optional[int] = None
    ground_truth_diagnosis: Optional[DiagnosisTermRead] = None # Nested ground truth
    case_metadata_relation: Optional[CaseMetaDataRead] = None # Nested metadata
    images: List[ImageRead] = [] # List of images
    ai_outputs: List[AIOutputRead] = [] # List of AI outputs

    class Config:
        from_attributes = True

class ManagementStrategyRead(ManagementStrategyBase):
    id: int

    class Config:
        from_attributes = True

class ManagementPlanRead(ManagementPlanBase):
    id: int
    assessment_user_id: int
    assessment_case_id: int
    assessment_is_post_ai: bool
    strategy_id: int
    strategy: ManagementStrategyRead # Nested strategy info

    class Config:
        from_attributes = True

class DiagnosisRead(DiagnosisBase):
    id: int
    assessment_user_id: int
    assessment_case_id: int
    assessment_is_post_ai: bool
    diagnosis_id: int
    diagnosis_term: DiagnosisTermRead # Nested diagnosis term info

    class Config:
        from_attributes = True

class AssessmentRead(AssessmentBase):
    created_at: datetime.datetime
    change_diagnosis_after_ai: Optional[bool] = None
    change_management_after_ai: Optional[bool] = None
    user: Optional[UserRead] = None
    case: Optional[CaseRead] = None
    diagnoses: List[DiagnosisRead] = []
    management_plan: Optional[ManagementPlanRead] = None

    class Config:
        from_attributes = True

# Schemas for Updates (Optional, define as needed)

# UserBase, UserCreate, UserRead, and UserUpdate are now imported from auth.schemas

