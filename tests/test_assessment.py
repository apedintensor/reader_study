# backend/tests/test_assessment.py
import pytest
from httpx import AsyncClient
from fastapi import status

@pytest.mark.asyncio
async def create_diagnosis_term(client: AsyncClient, user_token_headers: dict):
    """Test creating a diagnosis term (needed for test case creation)."""
    # Use current timestamp to ensure uniqueness
    import time
    unique_name = f"Test Diagnosis Term {time.time()}"
    diagnosis_term_data = {"name": unique_name}
    
    response = await client.post(
        "/diagnosis_terms/",  # Removed /api/v1 prefix
        headers=user_token_headers,
        json=diagnosis_term_data
    )
    assert response.status_code == 201, f"Failed to create diagnosis term: {response.text}"
    return response.json()

@pytest.mark.asyncio
async def create_case(client: AsyncClient, user_token_headers: dict):
    """Create a test case for assessment tests."""
    # First create a diagnosis term
    diagnosis_term = await create_diagnosis_term(client, user_token_headers)
    
    # Now create a case
    case_data = {
        "ground_truth_diagnosis_id": diagnosis_term["id"],
        "typical_diagnosis": True
    }
    
    response = await client.post(
        "/cases/",  # Removed /api/v1 prefix
        headers=user_token_headers,
        json=case_data
    )
    assert response.status_code == 201, f"Failed to create case: {response.text}"
    return response.json()

@pytest.mark.asyncio
async def test_create_assessment(client: AsyncClient, user_token_headers: dict):
    """Test creating a new assessment."""
    # First create a case
    case = await create_case(client, user_token_headers)
    
    # Get user ID from profile
    response = await client.get("/auth/me", headers=user_token_headers)
    user_data = response.json()
    user_id = user_data["id"]
    
    # Now create an assessment
    assessment_data = {
        "user_id": user_id,
        "case_id": case["id"],
        "is_post_ai": False,
        "assessable_image_score": 4,
        "confidence_level_top1": 3,
        "management_confidence": 4,
        "certainty_level": 3
    }
    
    response = await client.post(
        "/assessments/",  # Removed /api/v1 prefix
        headers=user_token_headers,
        json=assessment_data
    )
    assert response.status_code == 201, f"Failed to create assessment: {response.text}"
    data = response.json()
    assert "id" in data, "Assessment id not found in response"
    assert data["user_id"] == user_id
    assert data["case_id"] == case["id"]
    assert data["is_post_ai"] == False
    assert "created_at" in data
    
    return data

@pytest.mark.asyncio
async def test_get_assessment(client: AsyncClient, user_token_headers: dict):
    """Test retrieving an assessment by ID."""
    # First create an assessment
    assessment = await test_create_assessment(client, user_token_headers)
    
    # Now retrieve it
    response = await client.get(
        f"/assessments/{assessment['id']}",  # Removed /api/v1 prefix
        headers=user_token_headers
    )
    assert response.status_code == 200, f"Failed to get assessment: {response.text}"
    data = response.json()
    assert data["id"] == assessment["id"]
    assert data["user_id"] == assessment["user_id"]
    assert data["case_id"] == assessment["case_id"]
    assert data["is_post_ai"] == assessment["is_post_ai"]

@pytest.mark.asyncio
async def test_get_assessments_by_user(client: AsyncClient, user_token_headers: dict):
    """Test retrieving assessments for specific user."""
    # First create an assessment
    assessment = await test_create_assessment(client, user_token_headers)
    
    # Get user ID
    user_id = assessment["user_id"]
    
    # Now get assessments for this user
    response = await client.get(
        f"/assessments/user/{user_id}",  # Removed /api/v1 prefix
        headers=user_token_headers
    )
    assert response.status_code == 200, f"Failed to get user assessments: {response.text}"
    data = response.json()
    assert isinstance(data, list), "Expected a list of assessments"
    assert len(data) > 0, "Expected at least one assessment"
    assert data[0]["user_id"] == user_id, "Assessment should belong to specified user"

@pytest.mark.asyncio
async def test_create_ai_output(client: AsyncClient, user_token_headers: dict):
    """Test creating AI output for a case."""
    # First create a case
    case = await create_case(client, user_token_headers)
    
    # And create a diagnosis term for the AI prediction with a unique name
    import time
    unique_name = f"AI Predicted Diagnosis {time.time()}"
    diagnosis_term_data = {
        "name": unique_name
    }
    response = await client.post(
        "/diagnosis_terms/",
        headers=user_token_headers,
        json=diagnosis_term_data
    )
    
    assert response.status_code == 201, f"Failed to create diagnosis term: {response.text}"
    diagnosis_term = response.json()
    assert "id" in diagnosis_term, "Diagnosis term id not found in response"
    
    # Now create an AI output for the case
    ai_output_data = {
        "case_id": case["id"],
        "prediction_id": diagnosis_term["id"],
        "rank": 1,
        "confidence_score": 0.95
    }
    
    response = await client.post(
        "/ai_outputs/",  # Removed /api/v1 prefix
        headers=user_token_headers,
        json=ai_output_data
    )
    assert response.status_code == 201, f"Failed to create AI output: {response.text}"
    data = response.json()
    assert "id" in data, "AI output id not found in response"
    assert data["case_id"] == case["id"]
    assert data["prediction_id"] == diagnosis_term["id"]
    assert data["rank"] == 1
    assert data["confidence_score"] == 0.95
    
    return data

@pytest.mark.asyncio
async def test_get_ai_outputs_for_case(client: AsyncClient, user_token_headers: dict):
    """Test retrieving AI outputs for a case."""
    # First create AI output for a case
    ai_output = await test_create_ai_output(client, user_token_headers)
    case_id = ai_output["case_id"]
    
    # Now get AI outputs for this case
    response = await client.get(
        f"/ai_outputs/case/{case_id}",  # Removed /api/v1 prefix
        headers=user_token_headers
    )
    assert response.status_code == 200, f"Failed to get AI outputs: {response.text}"
    data = response.json()
    assert isinstance(data, list), "Expected a list of AI outputs"
    assert len(data) > 0, "Expected at least one AI output"
    assert data[0]["case_id"] == case_id, "AI output should belong to specified case"
    assert "prediction" in data[0], "AI output should include nested prediction data"

@pytest.mark.asyncio
async def test_create_diagnosis(client: AsyncClient, user_token_headers: dict):
    """Test creating a diagnosis for an assessment."""
    # First create an assessment
    assessment = await test_create_assessment(client, user_token_headers)
    
    # Create a diagnosis term with a unique name
    import time
    unique_name = f"Test Diagnosis for Assessment {time.time()}"
    diagnosis_term_data = {
        "name": unique_name
    }
    response = await client.post(
        "/diagnosis_terms/",  # Removed /api/v1 prefix
        headers=user_token_headers,
        json=diagnosis_term_data
    )
    diagnosis_term = response.json()
    assert "id" in diagnosis_term, "Diagnosis term id not found in response"
    
    # Now create a diagnosis for the assessment
    diagnosis_data = {
        "assessment_id": assessment["id"],
        "diagnosis_id": diagnosis_term["id"],
        "rank": 1,
        "is_ground_truth": True,
        "diagnosis_accuracy": 5
    }
    
    response = await client.post(
        "/diagnoses/",  # Removed /api/v1 prefix
        headers=user_token_headers,
        json=diagnosis_data
    )
    assert response.status_code == 201, f"Failed to create diagnosis: {response.text}"
    data = response.json()
    assert "id" in data, "Diagnosis id not found in response"
    assert data["assessment_id"] == assessment["id"]
    assert data["diagnosis_id"] == diagnosis_term["id"]
    assert data["rank"] == 1
    
    return data