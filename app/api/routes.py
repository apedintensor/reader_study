# backend/app/api/routes.py
from fastapi import APIRouter

from app.api.endpoints import (
    ai_output,
    assessment,
    case,
    case_metadata,
    diagnosis,
    diagnosis_term,
    image,
    management_plan,
    management_strategy,
    role,
    user,
)

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(ai_output.router, prefix="/ai_outputs", tags=["AI Outputs"])
api_router.include_router(assessment.router, prefix="/assessments", tags=["Assessments"])
api_router.include_router(case.router, prefix="/cases", tags=["Cases"])
api_router.include_router(case_metadata.router, prefix="/case_metadata", tags=["Case Metadata"])
api_router.include_router(diagnosis.router, prefix="/diagnoses", tags=["Diagnoses"])
api_router.include_router(diagnosis_term.router, prefix="/diagnosis_terms", tags=["Diagnosis Terms"])
api_router.include_router(image.router, prefix="/images", tags=["Images"])
api_router.include_router(management_plan.router, prefix="/management_plans", tags=["Management Plans"])
api_router.include_router(management_strategy.router, prefix="/management_strategies", tags=["Management Strategies"])
api_router.include_router(role.router, prefix="/roles", tags=["Roles"])
api_router.include_router(user.router, prefix="/users", tags=["Users"])


@api_router.get("/ping")
def ping():
    return {"message": "pong"}