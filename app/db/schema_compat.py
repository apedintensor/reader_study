from __future__ import annotations
from typing import Iterable
from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import OperationalError


_DIAGNOSIS_TERM_COLUMN = "diagnosis_term_id"


def _list_columns(conn, table_name: str) -> Iterable[str]:
    dialect = conn.dialect.name
    if dialect == "sqlite":
        rows = conn.execute(text(f"PRAGMA table_info('{table_name}')")).fetchall()
        for row in rows:
            yield row[1]
    else:
        rows = conn.execute(
            text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name = :table"
            ),
            {"table": table_name},
        ).fetchall()
        for row in rows:
            yield row[0]


def ensure_diagnosis_entries_has_term_column(db: Session) -> bool:
    """Ensure diagnosis_entries table has diagnosis_term_id column (legacy DB compatibility)."""
    bind = db.get_bind()
    if bind is None:
        return True

    # Fast path: column already present
    with bind.connect() as conn:
        if _DIAGNOSIS_TERM_COLUMN in set(_list_columns(conn, "diagnosis_entries")):
            return True

    # Attempt to add the column. Use standalone connection/transaction so we do not
    # interfere with the caller's session state.
    try:
        with bind.begin() as conn:
            conn.execute(
                text(
                    "ALTER TABLE diagnosis_entries "
                    "ADD COLUMN diagnosis_term_id INTEGER"
                )
            )
    except OperationalError as exc:
        message = str(exc).lower()
        # If another process already added the column, treat as success
        if "duplicate" in message or "already exists" in message:
            return True
        # For backends that do not support ALTER (very old), surface the failure but
        # allow the app to continue by returning False so callers can degrade.
        return False
    except Exception:
        return False

    return True
