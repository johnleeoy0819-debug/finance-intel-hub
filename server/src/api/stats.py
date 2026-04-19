from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from src.db.engine import get_db
from src.db.models import Article, Source

router = APIRouter()


@router.get("/dashboard")
def dashboard_stats(db: Session = Depends(get_db)):
    today = datetime.utcnow().date()
    week_ago = today - timedelta(days=7)

    today_count = db.query(Article).filter(
        Article.created_at >= today
    ).count()

    week_count = db.query(Article).filter(
        Article.created_at >= week_ago
    ).count()

    pending_count = db.query(Article).filter(
        Article.status == "pending"
    ).count()

    source_count = db.query(Source).filter(
        Source.is_active == True
    ).count()

    # Category distribution
    from sqlalchemy import func
    cat_dist = db.query(
        Article.primary_category_id,
        func.count(Article.id)
    ).group_by(Article.primary_category_id).all()

    return {
        "today_count": today_count,
        "week_count": week_count,
        "pending_count": pending_count,
        "source_count": source_count,
        "category_distribution": [
            {"category_id": c[0], "count": c[1]} for c in cat_dist
        ],
    }
