from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from src.db.engine import get_db
from src.db.models import Article, Source, Category, KnowledgeEdge

router = APIRouter()


@router.get("/dashboard")
def dashboard_stats(db: Session = Depends(get_db)):
    today = datetime.utcnow().date()
    week_ago = today - timedelta(days=7)
    thirty_days_ago = today - timedelta(days=30)

    # Basic counts
    total_count = db.query(Article).count()
    today_count = db.query(Article).filter(Article.created_at >= today).count()
    week_count = db.query(Article).filter(Article.created_at >= week_ago).count()
    pending_count = db.query(Article).filter(Article.status == "pending").count()
    source_count = db.query(Source).filter(Source.is_active == True).count()
    edge_count = db.query(KnowledgeEdge).count()

    # 7-day trend
    from sqlalchemy import func
    trend = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        next_day = day + timedelta(days=1)
        count = db.query(Article).filter(
            Article.created_at >= day,
            Article.created_at < next_day
        ).count()
        trend.append({"date": day.isoformat(), "count": count})

    # Sentiment distribution
    sentiment_dist = db.query(
        Article.sentiment,
        func.count(Article.id)
    ).filter(Article.sentiment.isnot(None)).group_by(Article.sentiment).all()

    # Category distribution with names
    cat_rows = db.query(
        Article.primary_category_id,
        func.count(Article.id)
    ).filter(Article.primary_category_id.isnot(None)).group_by(Article.primary_category_id).all()

    category_distribution = []
    for cat_id, count in cat_rows:
        cat = db.query(Category).filter(Category.id == cat_id).first()
        category_distribution.append({
            "category_id": cat_id,
            "name": cat.name if cat else "未知",
            "count": count,
        })

    # Recent articles
    recent = db.query(Article).filter(
        Article.status == "completed"
    ).order_by(Article.created_at.desc()).limit(5).all()

    return {
        "total_count": total_count,
        "today_count": today_count,
        "week_count": week_count,
        "pending_count": pending_count,
        "source_count": source_count,
        "edge_count": edge_count,
        "trend": trend,
        "sentiment_distribution": [
            {"sentiment": s[0], "count": s[1]} for s in sentiment_dist
        ],
        "category_distribution": category_distribution,
        "recent_articles": [
            {"id": a.id, "title": a.title, "sentiment": a.sentiment, "created_at": a.created_at.isoformat() if a.created_at else None}
            for a in recent
        ],
    }
