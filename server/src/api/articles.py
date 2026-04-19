from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from src.db.engine import get_db
from src.db.models import Article, Correction, Category, Tag, ArticleTag
from src.api.schemas import ArticleListParams, CorrectionCreate

router = APIRouter()


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
    return {"total": total, "items": articles}


@router.get("/{article_id}")
def get_article(article_id: int, db: Session = Depends(get_db)):
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


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
    return articles


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

    # Apply correction to article
    if correction.field == "primary_category":
        article.primary_category_id = correction.corrected_value
    elif correction.field == "secondary_category":
        article.secondary_category_id = correction.corrected_value

    db.commit()
    return {"ok": True}
