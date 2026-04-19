from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional

from src.db.engine import get_db
from src.db.models import Category, Tag

router = APIRouter()


@router.get("/categories")
def list_categories(parent_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Category)
    if parent_id is not None:
        query = query.filter(Category.parent_id == parent_id)
    return query.order_by(Category.sort_order, Category.name).all()


@router.get("/tags")
def list_tags(q: Optional[str] = None, limit: int = 100, db: Session = Depends(get_db)):
    query = db.query(Tag)
    if q:
        query = query.filter(Tag.name.ilike(f"%{q}%"))
    return query.order_by(Tag.usage_count.desc()).limit(limit).all()
