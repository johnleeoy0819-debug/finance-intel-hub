"""Wiki page API — compiled knowledge base pages."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional

from src.db.engine import get_db
from src.db.models import WikiPage
from src.core.wiki_compiler import compile_topic_async, auto_compile_top_topics, compile_index

router = APIRouter()


class CompileRequest(BaseModel):
    topic: str
    article_ids: Optional[List[int]] = None


@router.get("")
def list_wiki_pages(topic: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(WikiPage)
    if topic:
        query = query.filter(WikiPage.topic == topic)
    return query.order_by(WikiPage.updated_at.desc()).all()


@router.get("/{slug}")
def get_wiki_page(slug: str, db: Session = Depends(get_db)):
    page = db.query(WikiPage).filter(WikiPage.slug == slug).first()
    if not page:
        raise HTTPException(status_code=404, detail="Wiki page not found")
    return page


@router.post("/compile")
def compile_wiki_page(req: CompileRequest, db: Session = Depends(get_db)):
    """Trigger async compilation of a wiki page for a topic."""
    compile_topic_async(req.topic, req.article_ids)
    return {"status": "queued", "topic": req.topic}


@router.post("/auto-compile")
def auto_compile(db: Session = Depends(get_db)):
    """Auto-compile top topics from recent articles."""
    topics = auto_compile_top_topics(days=7, limit=5)
    return {"status": "queued", "topics": topics}


@router.post("/index")
def compile_wiki_index(db: Session = Depends(get_db)):
    """Manually trigger global wiki index compilation."""
    result = compile_index()
    return result


@router.delete("/{slug}")
def delete_wiki_page(slug: str, db: Session = Depends(get_db)):
    page = db.query(WikiPage).filter(WikiPage.slug == slug).first()
    if not page:
        raise HTTPException(status_code=404, detail="Wiki page not found")
    db.delete(page)
    db.commit()
    return {"ok": True}
