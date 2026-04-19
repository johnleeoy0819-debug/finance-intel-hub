from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import json

from src.db.engine import get_db
from src.db.models import Article, Correction, Category, Tag, ArticleTag
from src.api.schemas import ArticleListParams, CorrectionCreate, ArticleResponse
from src.core.db_utils import json_loads_field
from src.core.backlinks import update_all_backlinks, get_backlinks_for_article

router = APIRouter()


def _article_to_response(db: Session, article: Article) -> ArticleResponse:
    """Convert ORM Article to frontend-friendly response schema."""
    primary_cat = None
    secondary_cat = None
    if article.primary_category_id:
        cat = db.query(Category).filter(Category.id == article.primary_category_id).first()
        primary_cat = cat.name if cat else None
    if article.secondary_category_id:
        cat = db.query(Category).filter(Category.id == article.secondary_category_id).first()
        secondary_cat = cat.name if cat else None

    tags = []
    tag_rows = db.query(Tag).join(ArticleTag).filter(ArticleTag.article_id == article.id).all()
    tags = [t.name for t in tag_rows]

    source_name = None
    if article.source_id:
        from src.db.models import Source
        src = db.query(Source).filter(Source.id == article.source_id).first()
        source_name = src.name if src else None

    backlinks = []
    if article.backlinks:
        try:
            backlinks = json.loads(article.backlinks)
        except json.JSONDecodeError:
            backlinks = []

    return ArticleResponse(
        id=article.id,
        title=article.title,
        url=article.url,
        source=source_name,
        author=article.author,
        published_at=article.published_at.isoformat() if article.published_at else None,
        summary=article.summary,
        key_points=json_loads_field(article.key_points) or [],
        entities=json_loads_field(article.entities) or [],
        sentiment=article.sentiment,
        importance=article.importance,
        primary_category=primary_cat,
        secondary_category=secondary_cat,
        tags=tags,
        mindmap=article.mindmap,
        status=article.status,
        created_at=article.created_at.isoformat() if article.created_at else None,
        backlinks=backlinks,
    )


@router.get("")
def list_articles(
    category_id: Optional[int] = None,
    tag: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(Article)
    if category_id:
        query = query.filter(
            (Article.primary_category_id == category_id) |
            (Article.secondary_category_id == category_id)
        )
    if status:
        query = query.filter(Article.status == status)
    if tag:
        tag_obj = db.query(Tag).filter(Tag.name == tag).first()
        if tag_obj:
            query = query.join(ArticleTag).filter(ArticleTag.tag_id == tag_obj.id)

    total = query.count()
    articles = query.order_by(Article.created_at.desc()).offset(offset).limit(limit).all()
    return {"total": total, "items": [_article_to_response(db, a) for a in articles]}


@router.get("/{article_id}")
def get_article(article_id: int, db: Session = Depends(get_db)):
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return _article_to_response(db, article)


@router.delete("/{article_id}")
def delete_article(article_id: int, db: Session = Depends(get_db)):
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    db.delete(article)
    db.commit()
    return {"ok": True}


@router.get("/{article_id}/related")
def get_related_articles(article_id: int, db: Session = Depends(get_db)):
    from src.db.models import KnowledgeEdge
    edges = db.query(KnowledgeEdge).filter(
        KnowledgeEdge.source_article_id == article_id
    ).all()
    related_ids = [e.target_article_id for e in edges]
    articles = db.query(Article).filter(Article.id.in_(related_ids)).all()
    return [_article_to_response(db, a) for a in articles]


@router.post("/{article_id}/correct")
def correct_article(article_id: int, correction: CorrectionCreate, db: Session = Depends(get_db)):
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    corr = Correction(
        article_id=article_id,
        field=correction.field,
        original_value=correction.original_value,
        corrected_value=correction.corrected_value,
    )
    db.add(corr)

    # Apply correction to article with type safety
    if correction.field == "primary_category":
        try:
            article.primary_category_id = int(correction.corrected_value)
        except (ValueError, TypeError):
            raise HTTPException(status_code=422, detail="primary_category must be a valid integer category ID")
    elif correction.field == "secondary_category":
        try:
            article.secondary_category_id = int(correction.corrected_value)
        except (ValueError, TypeError):
            raise HTTPException(status_code=422, detail="secondary_category must be a valid integer category ID")

    db.commit()
    return {"ok": True}


@router.post("/backlinks/update")
def update_backlinks(db: Session = Depends(get_db)):
    """Manually trigger backlinks recomputation for all articles."""
    count = update_all_backlinks(db)
    return {"updated": count}
