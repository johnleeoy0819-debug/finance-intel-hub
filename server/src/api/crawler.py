from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from src.db.engine import get_db
from src.db.models import Source
from src.core.crawler import crawl_source
from src.core.scheduler import add_crawl_job, remove_crawl_job

router = APIRouter()


@router.post("/sources")
def create_source(source: dict, db: Session = Depends(get_db)):
    db_source = Source(**source)
    db.add(db_source)
    db.commit()
    db.refresh(db_source)
    if db_source.schedule:
        add_crawl_job(db_source.id, db_source.schedule)
    return db_source


@router.get("/sources")
def list_sources(db: Session = Depends(get_db)):
    return db.query(Source).all()


@router.put("/sources/{source_id}")
def update_source(source_id: int, source: dict, db: Session = Depends(get_db)):
    db_source = db.query(Source).filter(Source.id == source_id).first()
    if not db_source:
        raise HTTPException(status_code=404, detail="Source not found")
    for key, value in source.items():
        setattr(db_source, key, value)
    db.commit()
    db.refresh(db_source)
    if db_source.schedule:
        add_crawl_job(db_source.id, db_source.schedule)
    else:
        remove_crawl_job(source_id)
    return db_source


@router.delete("/sources/{source_id}")
def delete_source(source_id: int, db: Session = Depends(get_db)):
    db_source = db.query(Source).filter(Source.id == source_id).first()
    if not db_source:
        raise HTTPException(status_code=404, detail="Source not found")
    remove_crawl_job(source_id)
    db.delete(db_source)
    db.commit()
    return {"ok": True}


@router.post("/trigger/{source_id}")
def trigger_crawl(source_id: int, db: Session = Depends(get_db)):
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    article_ids = crawl_source(source_id)
    return {"article_ids": article_ids}
