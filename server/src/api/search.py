from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from src.db.engine import get_db
from src.db.models import Article

router = APIRouter()


@router.get("")
def fulltext_search(q: str = Query(..., min_length=1), limit: int = 20, db: Session = Depends(get_db)):
    """Full-text search using SQLite FTS5."""
    from sqlalchemy import text

    # Use FTS5 virtual table
    sql = text("""
        SELECT a.* FROM articles a
        JOIN articles_fts fts ON a.id = fts.rowid
        WHERE articles_fts MATCH :query
        ORDER BY rank
        LIMIT :limit
    """)
    results = db.execute(sql, {"query": q, "limit": limit}).fetchall()

    # Convert to Article objects
    articles = []
    for row in results:
        articles.append(db.query(Article).filter(Article.id == row.id).first())

    return {"query": q, "items": [a for a in articles if a]}


@router.get("/semantic")
def semantic_search(q: str = Query(..., min_length=1), limit: int = 10):
    """Semantic search using ChromaDB (P1)."""
    return {"query": q, "items": [], "note": "Semantic search coming in P1"}
