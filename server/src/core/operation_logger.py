"""Operation logger — append-only log of key system events."""
import json
from typing import Optional
from sqlalchemy.orm import Session

from src.db.engine import SessionLocal
from src.db.models import OperationLog


def log_operation(
    operation_type: str,
    target_type: Optional[str] = None,
    target_id: Optional[str] = None,
    details: Optional[dict] = None,
    db: Optional[Session] = None,
) -> None:
    """Log an operation. Creates its own session if db not provided."""
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True
    try:
        entry = OperationLog(
            operation_type=operation_type,
            target_type=target_type,
            target_id=str(target_id) if target_id is not None else None,
            details=json.dumps(details, ensure_ascii=False) if details else None,
        )
        db.add(entry)
        db.commit()
    except Exception:
        db.rollback()
    finally:
        if close_db:
            db.close()
