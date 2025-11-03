import uuid

import pytest
from sqlalchemy import delete, select

from app.core.config import settings
from app.models.models import Case, DiagnosisTerm, ReaderCaseAssignment


@pytest.mark.asyncio
async def test_start_block_produces_unique_ground_truths(client, db_session):
    original_block_size = settings.GAME_BLOCK_SIZE
    settings.GAME_BLOCK_SIZE = 3
    try:
        # Clear existing assignments and cases for deterministic setup
        await db_session.execute(delete(ReaderCaseAssignment))
        await db_session.execute(delete(Case))
        await db_session.execute(delete(DiagnosisTerm))
        await db_session.commit()

        # Seed three unique diagnosis terms with extra cases sharing diagnoses to trigger dedup logic
        terms = [DiagnosisTerm(name=f"Term-{i}") for i in range(3)]
        db_session.add_all(terms)
        await db_session.flush()

        cases = [
            Case(ground_truth_diagnosis_id=terms[0].id),
            Case(ground_truth_diagnosis_id=terms[0].id),
            Case(ground_truth_diagnosis_id=terms[1].id),
            Case(ground_truth_diagnosis_id=terms[2].id),
        ]
        db_session.add_all(cases)
        await db_session.commit()

        # Register and authenticate a fresh user
        email = f"player-{uuid.uuid4()}@example.com"
        password = "testpass123"
        register_resp = await client.post(
            "/auth/register",
            json={"email": email, "password": password},
        )
        assert register_resp.status_code in (200, 201, 400)

        login_resp = await client.post(
            "/auth/jwt/login",
            data={"username": email, "password": password},
        )
        assert login_resp.status_code == 200, login_resp.text
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Start a new game block; expect unique ground-truth diagnoses in assignments
        start_resp = await client.post("/game/start", headers=headers)
        assert start_resp.status_code == 200, start_resp.text
        assignments = start_resp.json()["assignments"]
        assert assignments, "Expected at least one assignment"
        assert len(assignments) <= 3

        case_ids = [a["case_id"] for a in assignments]
        result = await db_session.execute(select(Case).where(Case.id.in_(case_ids)))
        assigned_cases = result.scalars().all()
        gt_ids = [c.ground_truth_diagnosis_id for c in assigned_cases if c.ground_truth_diagnosis_id is not None]
        assert len(gt_ids) == len(set(gt_ids)), "Assignments should not repeat ground-truth diagnoses"
    finally:
        settings.GAME_BLOCK_SIZE = original_block_size
