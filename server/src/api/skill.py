from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional

from src.db.engine import get_db
from src.db.models import SkillFeedback, Correction, Article
from src.core.feedback import build_fewshot_samples

router = APIRouter()


@router.post("/feedback")
def submit_feedback(feedback: dict, db: Session = Depends(get_db)):
    fb = SkillFeedback(
        skill_name=feedback.get("skill_name", "econ-master"),
        query=feedback["query"],
        response_summary=feedback.get("response_summary"),
        rating=feedback.get("rating"),
        comment=feedback.get("comment"),
    )
    db.add(fb)
    db.commit()
    db.refresh(fb)
    return fb


@router.get("/memory")
def get_memory():
    """Return user profile / memory (P1)."""
    return {
        "focus_areas": [],
        "recent_topics": [],
        "answer_preferences": {},
    }


@router.put("/memory")
def update_memory(data: dict):
    """Update user memory (P1)."""
    return {"ok": True}


@router.get("/examples")
def get_examples(field: Optional[str] = None, db: Session = Depends(get_db)):
    """Get Few-shot examples from corrections."""
    samples = build_fewshot_samples(field=field, limit=10)
    return {"samples": samples}
