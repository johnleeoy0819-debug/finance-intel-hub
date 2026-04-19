"""Operations API — read-only access to operation logs."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from src.db.engine import get_db
from src.db.models import OperationLog

router = APIRouter()


@router.get("")
def list_operations(
    operation_type: Optional[str] = None,
    target_type: Optional[str] = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(OperationLog).order_by(OperationLog.created_at.desc())
    if operation_type:
        query = query.filter(OperationLog.operation_type == operation_type)
    if target_type:
        query = query.filter(OperationLog.target_type == target_type)
    total = query.count()
    items = query.offset(offset).limit(limit).all()
    return {"total": total, "items": items}
