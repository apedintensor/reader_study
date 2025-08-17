#!/usr/bin/env python
# backend/create_mock_data.py
"""
Generate mock data for testing the Reader Study Web API.
This script creates test data including:
- DiagnosisTerms
- Cases with metadata and images
- AI outputs for cases
- Test users
- Management strategies
- Assessments with diagnoses and management plans
"""
import asyncio
import random
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Session

# Import models and schemas
from app.models.models import (
    DiagnosisTerm, Case, CaseMetaData, Image, AIOutput,
    Assessment, Diagnosis, ManagementStrategy, ManagementPlan,
    Role  # Import Role from app.models.models
)
# Fix circular import by importing User directly from auth.models
from app.auth.models import User
from app.db.session import AsyncSessionLocal, SessionLocal
from app.auth.manager import UserManager
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from app.core.config import settings
from app.auth.schemas import UserCreate

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("mock_data_generator")

# Mock data constants
DIAGNOSIS_TERMS = [
    "Melanoma", "Basal Cell Carcinoma", "Squamous Cell Carcinoma", 
    "Actinic Keratosis", "Seborrheic Keratosis", "Nevus", 
    "Dermatofibroma", "Tinea Versicolor", "Psoriasis", 
    "Eczema", "Rosacea", "Acne Vulgaris", 
    "Vitiligo", "Atopic Dermatitis", "Contact Dermatitis",
    "Lupus", "Scabies", "Hives",
    "Warts", "Shingles", "Impetigo",
    "Cellulitis", "Folliculitis", "Cysts",
    "Sebaceous Hyperplasia", "Milia", "Cherry Angioma"
]

MANAGEMENT_STRATEGIES = [
    "Reassure and Discharge", "Topical Treatment", "Oral Medication",
    "Surgical Excision", "Cryotherapy", "Phototherapy",
    "Refer to Dermatologist", "Biopsy", "Laser Treatment", 
    "Immunotherapy", "Chemotherapy", "Radiotherapy"
]

# Optional fallback patterns (used only if mock file missing)
IMAGE_URL_PATTERNS = [
    "https://example.com/images/case_{case_id}_front.jpg",
    "https://example.com/images/case_{case_id}_back.jpg",
    "https://example.com/images/case_{case_id}_close.jpg",
    "https://example.com/images/case_{case_id}_dermoscopic.jpg",
]

MOCK_IMAGE_FILE = "mock-skin-images.txt"

def load_mock_image_urls() -> list[str]:
    """Load list of mock skin image URLs from file.

    Returns fallback pattern-based (empty list -> patterns) if file missing or empty.
    """
    if os.path.exists(MOCK_IMAGE_FILE):
        try:
            with open(MOCK_IMAGE_FILE, "r", encoding="utf-8") as f:
                urls = [ln.strip() for ln in f if ln.strip() and not ln.startswith("#")]
            if urls:
                logger.info(f"Loaded {len(urls)} mock skin image URLs from {MOCK_IMAGE_FILE}")
                return urls
            else:
                logger.warning(f"No URLs found in {MOCK_IMAGE_FILE}; falling back to generated patterns")
        except Exception as e:
            logger.warning(f"Failed reading {MOCK_IMAGE_FILE}: {e}; using fallback patterns")
    else:
        logger.info(f"Mock image file {MOCK_IMAGE_FILE} not found; using fallback patterns")
    return []  # Indicate to use internal patterns

# Helper functions
def generate_random_date(start_date=None, days_back=365):
    """Generate a random datetime between start_date and days_back"""
    if start_date is None:
        start_date = datetime.now()
    random_days = random.randint(0, days_back)
    return start_date - timedelta(days=random_days)

def random_bool_with_bias(true_probability=0.5):
    """Generate a random boolean with bias toward True"""
    return random.random() < true_probability

def random_int_range(min_val, max_val):
    """Generate a random integer within range"""
    return random.randint(min_val, max_val)

def random_float_range(min_val, max_val):
    """Generate a random float within range"""
    return random.uniform(min_val, max_val)

def random_choice_from_list(items):
    """Select a random item from a list"""
    return random.choice(items)

def random_sample_from_list(items, min_count=1, max_count=None):
    """Select a random sample from a list"""
    if max_count is None:
        max_count = len(items)
    count = random.randint(min_count, min(max_count, len(items)))
    return random.sample(items, count)

# Data generation functions
async def create_diagnosis_terms(db: AsyncSession) -> List[DiagnosisTerm]:
    """Create diagnosis terms if they don't exist"""
    logger.info("Creating diagnosis terms...")
    result = []
    
    # Check existing terms first
    for term_name in DIAGNOSIS_TERMS:
        # Check if term exists
        stmt = select(DiagnosisTerm).where(DiagnosisTerm.name == term_name)
        res = await db.execute(stmt)
        existing_term = res.scalars().first()
        
        if existing_term:
            result.append(existing_term)
            logger.debug(f"Diagnosis term '{term_name}' already exists")
        else:
            # Create new term
            new_term = DiagnosisTerm(name=term_name)
            db.add(new_term)
            await db.commit()
            await db.refresh(new_term)
            result.append(new_term)
            logger.debug(f"Created diagnosis term: {term_name}")
    
    logger.info(f"Created/found {len(result)} diagnosis terms")
    return result

async def create_management_strategies(db: AsyncSession) -> List[ManagementStrategy]:
    """Create management strategies if they don't exist"""
    logger.info("Creating management strategies...")
    result = []
    
    # Check existing strategies first
    for strategy_name in MANAGEMENT_STRATEGIES:
        # Check if strategy exists
        stmt = select(ManagementStrategy).where(ManagementStrategy.name == strategy_name)
        res = await db.execute(stmt)
        existing_strategy = res.scalars().first()
        
        if existing_strategy:
            result.append(existing_strategy)
            logger.debug(f"Management strategy '{strategy_name}' already exists")
        else:
            # Create new strategy
            new_strategy = ManagementStrategy(name=strategy_name)
            db.add(new_strategy)
            await db.commit()
            await db.refresh(new_strategy)
            result.append(new_strategy)
            logger.debug(f"Created management strategy: {strategy_name}")
    
    logger.info(f"Created/found {len(result)} management strategies")
    return result

async def create_test_users(db: AsyncSession, role_ids: List[int], count=10) -> List[User]:
    """Create test users with different roles"""
    logger.info(f"Creating {count} test users...")
    result = []
    user_db = SQLAlchemyUserDatabase(db, User)
    user_manager = UserManager(user_db)
    
    # Create users with different roles
    for i in range(1, count + 1):
        role_id = random.choice(role_ids)
        years_exp = random.randint(1, 30)
        years_derm = random.randint(0, years_exp)
        gender = random.choice(["male", "female", "non-binary", "prefer not to say"])
        age_bracket = random.choice(["20-29", "30-39", "40-49", "50-59", "60+"])
        
        user_data = UserCreate(
            email=f"test_user{i}@example.com",
            password=f"Password{i}!",
            is_active=True,
            is_verified=True,
            role_id=role_id,
            gender=gender,
            age_bracket=age_bracket,
            years_experience=years_exp,
            years_derm_experience=years_derm,
        )
        
        # Check if user exists
        stmt = select(User).where(User.email == user_data.email)
        res = await db.execute(stmt)
        existing_user = res.scalars().first()
        
        if existing_user:
            result.append(existing_user)
            logger.debug(f"User '{user_data.email}' already exists")
        else:
            try:
                # Create user with UserManager (properly hashes password)
                user = await user_manager.create(user_data)
                result.append(user)
                logger.debug(f"Created user: {user.email} (Role ID: {user.role_id})")
            except Exception as e:
                logger.error(f"Error creating user {user_data.email}: {e}")
    
    logger.info(f"Created/found {len(result)} test users")
    return result

async def create_test_cases(
    db: AsyncSession,
    diagnosis_terms: List[DiagnosisTerm],
    count=40
) -> List[Case]:
    """Create test cases with metadata and images"""
    logger.info(f"Creating {count} test cases...")
    result = []
    
    mock_image_urls = load_mock_image_urls()

    for i in range(1, count + 1):
        # Choose a random diagnosis term for ground truth
        diagnosis_term = random.choice(diagnosis_terms)
        
        # Create case
        case = Case(
            ground_truth_diagnosis_id=diagnosis_term.id,
            typical_diagnosis=random_bool_with_bias(0.7),  # 70% chance of being typical
            created_at=generate_random_date()
        )
        db.add(case)
        await db.commit()
        await db.refresh(case)
        logger.debug(f"Created case #{case.id} with diagnosis: {diagnosis_term.name}")
        
        # Create case metadata
        age = random.randint(1, 95)
        gender = random.choice(["male", "female", "unknown"])
        metadata = CaseMetaData(
            case_id=case.id,
            age=age,
            gender=gender,
            fever_history=random_bool_with_bias(0.3),  # 30% chance of fever history
            psoriasis_history=random_bool_with_bias(0.2),  # 20% chance of psoriasis history
            other_notes=f"Test case #{case.id}. Patient presented with symptoms for {random.randint(1, 60)} days."
        )
        db.add(metadata)
        
        # Assign exactly 3 random images per case.
        # If mock file loaded, sample from it (with replacement across cases, without within case).
        if mock_image_urls:
            chosen_urls = random.sample(mock_image_urls, k=min(3, len(mock_image_urls)))
        else:
            # Fallback: build 3 patterned URLs
            chosen_patterns = random.sample(IMAGE_URL_PATTERNS, k=min(3, len(IMAGE_URL_PATTERNS)))
            chosen_urls = [p.format(case_id=case.id) for p in chosen_patterns]

        for image_url in chosen_urls:
            db.add(Image(case_id=case.id, image_url=image_url))
        
        await db.commit()
        result.append(case)
    
    logger.info(f"Created {len(result)} test cases with metadata and images")
    return result

async def create_ai_outputs(
    db: AsyncSession, 
    cases: List[Case], 
    diagnosis_terms: List[DiagnosisTerm]
) -> List[AIOutput]:
    """Create AI outputs for cases"""
    logger.info(f"Creating AI outputs for {len(cases)} cases...")
    result = []
    
    for case in cases:
        # Get ground truth diagnosis
        gt_diagnosis_id = case.ground_truth_diagnosis_id
        
        # Create correct prediction with high confidence (rank 1)
        ai_output_correct = AIOutput(
            case_id=case.id,
            prediction_id=gt_diagnosis_id,
            rank=1,
            confidence_score=random_float_range(0.7, 0.99)  # High confidence
        )
        db.add(ai_output_correct)
        result.append(ai_output_correct)
        
        # Create 2-4 additional predictions with lower confidences
        other_diagnoses = [d for d in diagnosis_terms if d.id != gt_diagnosis_id]
        num_predictions = random.randint(2, 4)
        selected_diagnoses = random.sample(other_diagnoses, num_predictions)
        
        for rank, diagnosis in enumerate(selected_diagnoses, 2):  # Start from rank 2
            confidence = random_float_range(0.1, 0.7 - (rank * 0.1))  # Decreasing confidence
            ai_output = AIOutput(
                case_id=case.id,
                prediction_id=diagnosis.id,
                rank=rank,
                confidence_score=confidence
            )
            db.add(ai_output)
            result.append(ai_output)
    
    await db.commit()
    logger.info(f"Created {len(result)} AI outputs")
    return result

async def create_assessments_and_diagnoses(
    db: AsyncSession,
    users: List[User],
    cases: List[Case],
    diagnosis_terms: List[DiagnosisTerm],
    management_strategies: List[ManagementStrategy],
    assessments_per_user_min=3,
    assessments_per_user_max=10
) -> List[Assessment]:
    """Create assessments with diagnoses and management plans"""
    logger.info("Creating assessments with diagnoses and management plans...")
    result = []
    
    for user in users:
        # Each user completes a random number of assessments
        num_assessments = random.randint(assessments_per_user_min, assessments_per_user_max)
        selected_cases = random.sample(cases, min(num_assessments, len(cases)))
        
        for i, case in enumerate(selected_cases):
            # Create pre-AI assessment
            pre_assessment = Assessment(
                user_id=user.id,
                case_id=case.id,
                is_post_ai=False,
                assessable_image_score=random.randint(1, 5),
                confidence_level_top1=random.randint(1, 5),
                management_confidence=random.randint(1, 5),
                certainty_level=random.randint(1, 5),
                ai_usefulness=None,  # No AI usefulness for pre-AI assessment
                created_at=generate_random_date()
            )
            db.add(pre_assessment)
            await db.commit()
            await db.refresh(pre_assessment)
            logger.debug(f"Created pre-AI assessment for user #{user.id}, case #{case.id}")
            result.append(pre_assessment)
            
            # Add diagnoses to pre-AI assessment
            selected_diagnoses = random_sample_from_list(diagnosis_terms, 1, 3)
            for rank, diagnosis_term in enumerate(selected_diagnoses, 1):
                is_ground_truth = (diagnosis_term.id == case.ground_truth_diagnosis_id)
                diagnosis = Diagnosis(
                    assessment_user_id=user.id,
                    assessment_case_id=case.id,
                    assessment_is_post_ai=False,
                    rank=rank,
                    diagnosis_id=diagnosis_term.id,
                    is_ground_truth=is_ground_truth,
                    diagnosis_accuracy=random.randint(1, 5) if is_ground_truth else None
                )
                db.add(diagnosis)
            
            # Add management plan to pre-AI assessment
            strategy = random.choice(management_strategies)
            management_plan = ManagementPlan(
                assessment_user_id=user.id,
                assessment_case_id=case.id,
                assessment_is_post_ai=False,
                strategy_id=strategy.id,
                free_text=f"Management plan for case #{case.id}. " + 
                          f"{'Recommend follow-up in 6 weeks.' if random.random() > 0.5 else ''}",
                quality_score=random.randint(1, 5)
            )
            db.add(management_plan)
            await db.commit()
            
            # 70% chance of also creating a post-AI assessment
            if random.random() < 0.7:
                # Get pre-assessment diagnoses for comparison
                pre_diagnoses = selected_diagnoses.copy()
                pre_strategy = strategy

                # Decide if we'll change diagnoses or management
                should_change_diagnosis = random.random() < 0.4  # 40% chance
                should_change_management = random.random() < 0.3  # 30% chance
                
                # Create post-AI assessment
                post_assessment = Assessment(
                    user_id=user.id,
                    case_id=case.id,
                    is_post_ai=True,
                    assessable_image_score=pre_assessment.assessable_image_score,  # Same as pre-assessment
                    confidence_level_top1=random.randint(1, 5),
                    management_confidence=random.randint(1, 5),
                    certainty_level=random.randint(1, 5),
                    ai_usefulness=random.choice(["very helpful", "somewhat helpful", "neutral", "not helpful"]),
                    created_at=pre_assessment.created_at + timedelta(minutes=random.randint(5, 30))
                )
                db.add(post_assessment)
                await db.commit()
                await db.refresh(post_assessment)
                logger.debug(f"Created post-AI assessment for user #{user.id}, case #{case.id}")
                result.append(post_assessment)
                
                # Add diagnoses to post-AI assessment
                if should_change_diagnosis:
                    # If diagnosis should change, select different diagnoses
                    selected_diagnoses = random_sample_from_list(
                        [d for d in diagnosis_terms if d not in pre_diagnoses],
                        1,
                        3
                    )
                
                for rank, diagnosis_term in enumerate(selected_diagnoses, 1):
                    is_ground_truth = (diagnosis_term.id == case.ground_truth_diagnosis_id)
                    diagnosis = Diagnosis(
                        assessment_user_id=user.id,
                        assessment_case_id=case.id,
                        assessment_is_post_ai=True,
                        rank=rank,
                        diagnosis_id=diagnosis_term.id,
                        is_ground_truth=is_ground_truth,
                        diagnosis_accuracy=random.randint(1, 5) if is_ground_truth else None
                    )
                    db.add(diagnosis)
                
                # Add management plan to post-AI assessment
                if should_change_management:
                    # If management should change, select a different strategy
                    strategy = random.choice([s for s in management_strategies if s.id != pre_strategy.id])
                
                management_plan = ManagementPlan(
                    assessment_user_id=user.id,
                    assessment_case_id=case.id,
                    assessment_is_post_ai=True,
                    strategy_id=strategy.id,
                    free_text=f"Post-AI management plan for case #{case.id}. " +
                              f"{'Plan modified after reviewing AI results.' if should_change_management else ''}",
                    quality_score=random.randint(1, 5)
                )
                db.add(management_plan)
            
            await db.commit()
    
    logger.info(f"Created {len(result)} assessments with diagnoses and management plans")
    return result

async def main():
    """Main function to generate mock data"""
    logger.info("Starting mock data generation...")
    
    # Create async session
    async with AsyncSessionLocal() as db:
        # Get all roles
        res = await db.execute(select(Role))
        roles = res.scalars().all()
        role_ids = [role.id for role in roles]
        
        if not role_ids:
            logger.error("No roles found. Please run init_db.py first.")
            return
        
        # Create diagnosis terms
        diagnosis_terms = await create_diagnosis_terms(db)
        
        # Create management strategies
        management_strategies = await create_management_strategies(db)
        
        # Create test users
        users = await create_test_users(db, role_ids)
        
        # Create test cases with metadata and images
        cases = await create_test_cases(db, diagnosis_terms)
        
        # Create AI outputs for cases
        ai_outputs = await create_ai_outputs(db, cases, diagnosis_terms)
        
        # Create assessments with diagnoses and management plans
        assessments = await create_assessments_and_diagnoses(
            db, users, cases, diagnosis_terms, management_strategies
        )
    
    logger.info("Mock data generation completed successfully!")

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())