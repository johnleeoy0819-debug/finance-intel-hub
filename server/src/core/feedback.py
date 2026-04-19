"""SKILL feedback loop: corrections → few-shot examples."""
from typing import List, Dict, Any, Optional


def build_fewshot_samples(field: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
    """Build few-shot samples from user corrections.

    Each sample contains:
    - input: article title + summary context
    - output: corrected_value
    - field: which field was corrected
    """
    from src.db.engine import SessionLocal
    from src.db.models import Correction, Article

    db = SessionLocal()
    try:
        query = db.query(Correction, Article).join(Article, Correction.article_id == Article.id)
        if field:
            query = query.filter(Correction.field == field)
        rows = query.order_by(Correction.created_at.desc()).limit(limit).all()

        samples = []
        for corr, article in rows:
            input_ctx = f"标题: {article.title}\n摘要: {article.summary or ''}".strip()
            samples.append({
                "input": input_ctx,
                "output": str(corr.corrected_value or ""),
                "field": corr.field,
                "original": str(corr.original_value or ""),
            })
        return samples
    finally:
        db.close()


def get_recent_feedback_summary(limit: int = 20) -> Dict[str, Any]:
    """Aggregate recent feedback for skill evolution reports."""
    from src.db.engine import SessionLocal
    from src.db.models import SkillFeedback

    db = SessionLocal()
    try:
        fbs = db.query(SkillFeedback).order_by(SkillFeedback.created_at.desc()).limit(limit).all()
        ratings = [fb.rating for fb in fbs if fb.rating is not None]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0
        return {
            "total": len(fbs),
            "avg_rating": round(avg_rating, 2),
            "positive": len([r for r in ratings if r and r >= 4]),
            "negative": len([r for r in ratings if r and r <= 2]),
        }
    finally:
        db.close()
