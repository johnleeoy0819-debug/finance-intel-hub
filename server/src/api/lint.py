"""Lint report API — self-maintenance audit reports."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional

from src.db.engine import get_db
from src.db.models import LintReport
from src.core.lint_engine import run_all_lints

router = APIRouter()


class LintUpdateRequest(BaseModel):
    status: str


@router.post("/run")
def run_lint(db: Session = Depends(get_db)):
    """Trigger async lint audit."""
    import threading
    thread = threading.Thread(target=run_all_lints, daemon=True)
    thread.start()
    return {"status": "queued"}


@router.get("/reports")
def list_lint_reports(
    lint_type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(LintReport)
    if lint_type:
        query = query.filter(LintReport.lint_type == lint_type)
    if status:
        query = query.filter(LintReport.status == status)
    return query.order_by(LintReport.created_at.desc()).all()


@router.get("/summary")
def lint_summary(db: Session = Depends(get_db)):
    from sqlalchemy import func
    total = db.query(LintReport).filter(LintReport.status == "open").count()
    by_type = db.query(
        LintReport.lint_type,
        func.count(LintReport.id).label("count")
    ).filter(LintReport.status == "open").group_by(LintReport.lint_type).all()
    return {
        "total_open": total,
        "by_type": {t: c for t, c in by_type},
    }


@router.put("/reports/{report_id}")
def update_lint_report(report_id: int, req: LintUpdateRequest, db: Session = Depends(get_db)):
    report = db.query(LintReport).filter(LintReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Lint report not found")
    report.status = req.status
    if req.status == "resolved":
        from datetime import datetime
        report.resolved_at = datetime.utcnow()
    db.commit()
    return report
