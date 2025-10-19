from __future__ import annotations
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from app.models.models import (
    ReaderCaseAssignment, Case, BlockFeedback
)
from datetime import datetime
from app.core.config import settings
from sqlalchemy import text

# Cache schema inspection (legacy deployments may lack new peer_avg_* columns)
_checked_schema = False
_has_peer_avg_cols = False

def _ensure_schema_flags(db: Session):
    global _checked_schema, _has_peer_avg_cols
    if _checked_schema:
        return
    try:
        # Works for SQLite / Postgres (SQLite PRAGMA; Postgres information_schema)
        dialect = db.bind.dialect.name if db.bind else ""
        cols: list[str] = []
        if dialect == "sqlite":
            rows = db.execute(text("PRAGMA table_info(block_feedback)")).fetchall()
            cols = [r[1] for r in rows]
        else:
            q = text("SELECT column_name FROM information_schema.columns WHERE table_name='block_feedback'")
            cols = [r[0] for r in db.execute(q).fetchall()]
        needed = {"peer_avg_top1_pre","peer_avg_top1_post","peer_avg_top3_pre","peer_avg_top3_post"}
        _has_peer_avg_cols = needed.issubset(set(cols))
    except Exception:
        _has_peer_avg_cols = False
    finally:
        _checked_schema = True

# Use configurable block size
def get_block_size() -> int:
    return max(1, settings.GAME_BLOCK_SIZE)


def _next_block_index(db: Session, user_id: int) -> int:
    stmt = select(ReaderCaseAssignment.block_index).where(ReaderCaseAssignment.user_id == user_id).order_by(ReaderCaseAssignment.block_index.desc()).limit(1)
    row = db.execute(stmt).scalar_one_or_none()
    return 0 if row is None else row + 1


def start_block(db: Session, user_id: int) -> List[ReaderCaseAssignment]:
    """Create a new block of assignments (if the previous is finished).

    Maintains previous behavior when unfinished block exists.
    New behavior: random selection of unassigned cases, size = settings.GAME_BLOCK_SIZE.
    """
    # ensure no active (unfinished) assignments remain
    if get_active_block(db, user_id):
        active = get_active_block(db, user_id)
        return active

    block_index = _next_block_index(db, user_id)
    # gather already assigned case ids for this user
    assigned_case_ids = [cid for (cid,) in db.execute(select(ReaderCaseAssignment.case_id).where(ReaderCaseAssignment.user_id == user_id)).all()]
    # random selection differs by backend; SQLite supports RANDOM()
    block_size = get_block_size()
    candidates_query = select(Case).where(~Case.id.in_(assigned_case_ids))
    # If using SQLite/Postgres, func.random works; fallback to ordered if driver lacks random
    candidates_query = candidates_query.order_by(func.random()).limit(block_size)
    candidates = db.execute(candidates_query).scalars().all()
    if not candidates:
        return []
    assignments: List[ReaderCaseAssignment] = []
    for idx, c in enumerate(candidates):
        a = ReaderCaseAssignment(
            user_id=user_id,
            case_id=c.id,
            display_order=idx,
            block_index=block_index,
            started_at=datetime.utcnow(),
        )
        db.add(a)
        assignments.append(a)
    db.commit()
    for a in assignments:
        db.refresh(a)
    return assignments


def get_next_incomplete_assignment(db: Session, user_id: int) -> Optional[ReaderCaseAssignment]:
    """Return the next (lowest display_order) assignment in the active block missing POST completion."""
    block = get_active_block(db, user_id)
    if not block:
        return None
    for a in sorted(block, key=lambda x: x.display_order):
        if a.completed_post_at is None:
            return a
    return None


def start_or_continue_game(db: Session, user_id: int) -> Tuple[int | None, Optional[ReaderCaseAssignment]]:
    """Return (block_index, next_assignment) creating a new block if previous finished.

    If no more cases available returns (None, None).
    """
    block = get_active_block(db, user_id)
    if block:
        next_assignment = get_next_incomplete_assignment(db, user_id)
        return block[0].block_index if block else None, next_assignment
    # need new block
    new_block = start_block(db, user_id)
    if not new_block:
        return None, None
    return new_block[0].block_index, get_next_incomplete_assignment(db, user_id)


def get_active_block(db: Session, user_id: int) -> List[ReaderCaseAssignment]:
    stmt = select(ReaderCaseAssignment).where(ReaderCaseAssignment.user_id == user_id).order_by(ReaderCaseAssignment.block_index.desc(), ReaderCaseAssignment.display_order.asc())
    all_assignments = db.execute(stmt).scalars().all()
    if not all_assignments:
        return []
    latest_block_index = all_assignments[0].block_index
    block = [a for a in all_assignments if a.block_index == latest_block_index]
    # check if fully completed post phase
    if all(a.completed_post_at for a in block):
        return []
    return block


def finalize_block_if_complete(db: Session, user_id: int, block_index: int):
    block_assignments = db.execute(select(ReaderCaseAssignment).where(ReaderCaseAssignment.user_id == user_id, ReaderCaseAssignment.block_index == block_index)).scalars().all()
    if not block_assignments:
        return None
    _ensure_schema_flags(db)
    # If feedback already exists return it (idempotent fast path)
    existing = db.execute(
        select(BlockFeedback).where(BlockFeedback.user_id == user_id, BlockFeedback.block_index == block_index)
    ).scalar_one_or_none()
    if existing and all(a.completed_post_at for a in block_assignments):
        return existing
    if not all(a.completed_post_at for a in block_assignments):
        return None
    stats_payload = {
        "cases_completed": len(block_assignments),
        "accuracy_metrics_computed": False,
    }

    kwargs = dict(
        user_id=user_id,
        block_index=block_index,
        top1_accuracy_pre=None,
        top1_accuracy_post=None,
        top3_accuracy_pre=None,
        top3_accuracy_post=None,
        delta_top1=None,
        delta_top3=None,
        stats_json=stats_payload,
    )
    if _has_peer_avg_cols:
        kwargs.update(
            peer_avg_top1_pre=None,
            peer_avg_top1_post=None,
            peer_avg_top3_pre=None,
            peer_avg_top3_post=None,
        )
    else:
        stats_payload.update(
            peer_avg_top1_pre=None,
            peer_avg_top1_post=None,
            peer_avg_top3_pre=None,
            peer_avg_top3_post=None,
        )
    feedback = BlockFeedback(**kwargs)
    db.add(feedback)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        # Another request created it first; return the existing row
        existing = db.execute(
            select(BlockFeedback).where(
                BlockFeedback.user_id == user_id, BlockFeedback.block_index == block_index
            )
        ).scalar_one_or_none()
        return existing
    db.refresh(feedback)
    return feedback
