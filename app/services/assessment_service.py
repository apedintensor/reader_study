from __future__ import annotations
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime
from app.models.models import Assessment, ReaderCaseAssignment, DiagnosisEntry, DiagnosisTerm
from app.schemas.schemas import AssessmentCreate

def create_or_replace_assessment(db: Session, payload: AssessmentCreate) -> Assessment:
    # ensure assignment exists
    assignment = db.get(ReaderCaseAssignment, payload.assignment_id)
    if not assignment:
        raise ValueError("Assignment not found")
    # enforce uniqueness (assignment_id, phase)
    existing = db.execute(select(Assessment).where(Assessment.assignment_id == payload.assignment_id, Assessment.phase == payload.phase)).scalar_one_or_none()
    if existing:
        db.delete(existing)
        db.flush()
    assessment = Assessment(
        assignment_id=payload.assignment_id,
        phase=payload.phase,
        diagnostic_confidence=payload.diagnostic_confidence,
        management_confidence=payload.management_confidence,
        biopsy_recommended=payload.biopsy_recommended,
        referral_recommended=payload.referral_recommended,
        changed_primary_diagnosis=payload.changed_primary_diagnosis,
        changed_management_plan=payload.changed_management_plan,
        ai_usefulness=payload.ai_usefulness,
    )
    db.add(assessment)
    db.flush()
    # diagnosis entries
    for entry in payload.diagnosis_entries:
        de = DiagnosisEntry(
            assessment_id=assessment.id,
            rank=entry.rank,
            raw_text=entry.raw_text,
            diagnosis_term_id=entry.diagnosis_term_id,
        )
        db.add(de)
    db.flush()
    # compute correctness (top1, top3) if ground truth exists
    if assignment.case.ground_truth_diagnosis_id:
        gt_id = assignment.case.ground_truth_diagnosis_id
        found_rank = None
        for de in assessment.diagnosis_entries:
            if de.diagnosis_term_id == gt_id:
                found_rank = de.rank
                break
        if found_rank is not None:
            assessment.top1_correct = found_rank == 1
            assessment.top3_correct = found_rank <= 3
            assessment.rank_of_truth = found_rank
        else:
            # Explicitly record incorrect outcome so averages count this case
            assessment.top1_correct = False
            assessment.top3_correct = False
            assessment.rank_of_truth = None
    # mark completion times on assignment
    now = datetime.utcnow()
    if payload.phase == 'PRE':
        assignment.completed_pre_at = now
    else:
        assignment.completed_post_at = now
    db.commit()
    db.refresh(assessment)
    return assessment
