from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from src.db.engine import get_db
from src.db.models import Publication, PublicationChapter
from src.core.publication_fetcher import fetch_by_url

router = APIRouter()


@router.get("")
def list_publications(
    pub_type: Optional[str] = None,
    q: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    query = db.query(Publication)
    if pub_type:
        query = query.filter(Publication.pub_type == pub_type)
    if q:
        query = query.filter(
            (Publication.title.ilike(f"%{q}%")) |
            (Publication.authors.ilike(f"%{q}%")) |
            (Publication.abstract.ilike(f"%{q}%"))
        )
    total = query.count()
    items = query.order_by(Publication.created_at.desc()).offset(offset).limit(limit).all()
    return {"total": total, "items": items}


@router.get("/{pub_id}")
def get_publication(pub_id: int, db: Session = Depends(get_db)):
    pub = db.query(Publication).filter(Publication.id == pub_id).first()
    if not pub:
        raise HTTPException(status_code=404, detail="Publication not found")
    chapters = db.query(PublicationChapter).filter(PublicationChapter.publication_id == pub_id).all()
    return {"publication": pub, "chapters": chapters}


@router.post("/import")
def import_publication(url: str, db: Session = Depends(get_db)):
    """Import publication from arXiv URL or DOI."""
    try:
        meta = fetch_by_url(url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch metadata: {e}")

    # Check for duplicate by DOI or source
    existing = db.query(Publication).filter(
        (Publication.doi == meta.get("doi")) if meta.get("doi") else False
    ).first()
    if existing:
        return {"publication": existing, "created": False}

    pub = Publication(**meta)
    db.add(pub)
    db.commit()
    db.refresh(pub)
    return {"publication": pub, "created": True}


@router.delete("/{pub_id}")
def delete_publication(pub_id: int, db: Session = Depends(get_db)):
    pub = db.query(Publication).filter(Publication.id == pub_id).first()
    if not pub:
        raise HTTPException(status_code=404, detail="Publication not found")
    db.delete(pub)
    db.commit()
    return {"ok": True}
