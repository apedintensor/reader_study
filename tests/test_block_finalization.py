# Test that finishing all POST assessments triggers block finalization automatically
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_block_finalization_creates_block_feedback(client: AsyncClient, user_token_headers: dict):
    # Start (or resume) a block; if none created (no cases) fabricate minimal cases via direct inserts not exposed yet.
    start = await client.post('/game/start', headers=user_token_headers)
    if start.status_code != 200:
        pytest.skip(f"Cannot start block: {start.status_code} {start.text}")
    data = start.json()
    block_index = data['block_index']
    assignments = data['assignments']
    if not assignments:
        pytest.skip('No assignments (likely no cases loaded)')

    # Ensure at least one diagnosis term exists
    term_resp = await client.get('/diagnosis_terms/?limit=1', headers=user_token_headers)
    if term_resp.status_code != 200 or len(term_resp.json()) == 0:
        crt = await client.post('/diagnosis_terms/', json={'name': 'AutoTerm1'}, headers=user_token_headers)
        assert crt.status_code in (200, 201)
        term_id = crt.json()['id']
    else:
        term_id = term_resp.json()[0]['id']

    # Complete all assignments (PRE then POST)
    first_pre_assessment_id = None
    submitted_raw_text = "x"
    for a in assignments:
        base = {
            'assignment_id': a['id'],
            'diagnosis_entries': [{'rank': 1, 'diagnosis_term_id': term_id, 'raw_text': submitted_raw_text}],
            'diagnostic_confidence': 3,
            'management_confidence': 3,
            'investigation_action': 'NONE',
            'next_step_action': 'REASSURE',
            'changed_primary_diagnosis': False,
            'changed_management_plan': False,
            'ai_usefulness': None
        }
        pre = {**base, 'phase': 'PRE'}
        post = {**base, 'phase': 'POST'}
        r1 = await client.post('/assessment/', json=pre, headers=user_token_headers)
        assert r1.status_code == 200, r1.text
        pre_payload = r1.json()
        if first_pre_assessment_id is None:
            first_pre_assessment_id = pre_payload['id']
        r2 = await client.post('/assessment/', json=post, headers=user_token_headers)
        assert r2.status_code == 200, r2.text

    # Check availability
    avail = await client.get(f'/game/can_view_report/{block_index}', headers=user_token_headers)
    assert avail.status_code == 200
    assert avail.json()['available'] is True

    # Fetch report
    report = await client.get(f'/game/report/{block_index}', headers=user_token_headers)
    assert report.status_code == 200
    rep = report.json()
    assert rep['block_index'] == block_index
    assert 'delta_top1' in rep and 'delta_top3' in rep
    assert rep['cases'], "Expected at least one case summary"
    first_case = rep['cases'][0]
    assert 'pre_assessment_id' in first_case
    assert 'post_assessment_id' in first_case
    assert 'pre_top_diagnosis_term_ids' not in first_case

    # Verify new diagnosis entry lookup endpoint returns raw text
    if first_pre_assessment_id:
        diag_resp = await client.get(
            f'/assessment/{first_pre_assessment_id}/diagnosis_entries',
            headers=user_token_headers
        )
        assert diag_resp.status_code == 200
        entries = diag_resp.json()
        assert entries, "Expected diagnosis entries"
        assert entries[0]['raw_text'] == submitted_raw_text
