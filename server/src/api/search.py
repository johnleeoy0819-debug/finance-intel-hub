from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict

from src.db.engine import get_db
from src.db.models import Article
from src.core.vector_store import VectorStore
from src.api.articles import _article_to_response

router = APIRouter()


def _search_items(db: Session, articles: List[Article], mode: str, scores: Optional[Dict[int, float]] = None):
    """Uniform search result wrapper."""
    items = []
    for a in articles:
        item = {
            "article": _article_to_response(db, a),
            "score": round(scores.get(a.id, 0), 4) if scores else None,
            "mode": mode,
        }
        items.append(item)
    return items


@router.get("")
def fulltext_search(q: str = Query(..., min_length=1), limit: int = Query(default=20, ge=1, le=100), db: Session = Depends(get_db)):
    """Full-text search using SQLite FTS5."""
    from sqlalchemy import text

    try:
        sql = text("""
            SELECT a.* FROM articles a
            JOIN articles_fts fts ON a.id = fts.rowid
            WHERE articles_fts MATCH :query
            ORDER BY rank
            LIMIT :limit
        """)
        results = db.execute(sql, {"query": q, "limit": limit}).fetchall()
    except Exception as e:
        # Malformed FTS5 query — fall back to simple LIKE search
        results = db.execute(
            text("SELECT * FROM articles WHERE title LIKE :query OR summary LIKE :query ORDER BY created_at DESC LIMIT :limit"),
            {"query": f"%{q}%", "limit": limit}
        ).fetchall()

    # Convert rows to Article objects via IN query to avoid N+1
    row_ids = [r.id for r in results]
    if not row_ids:
        return {"query": q, "items": [], "mode": "fulltext"}

    articles = db.query(Article).filter(Article.id.in_(row_ids)).all()
    # Preserve order from FTS5 rank
    article_map = {a.id: a for a in articles}
    ordered = [article_map[r.id] for r in results if r.id in article_map]
    return {"query": q, "items": _search_items(db, ordered, "fulltext"), "mode": "fulltext"}


@router.get("/semantic")
def semantic_search(q: str = Query(..., min_length=1), limit: int = Query(default=10, ge=1, le=50), db: Session = Depends(get_db)):
    """Semantic search using ChromaDB vector similarity."""
    vs = VectorStore()
    hits = vs.search(q, limit=limit)
    if not hits:
        return {"query": q, "items": [], "mode": "semantic"}

    article_ids = [h["article_id"] for h in hits]
    articles = db.query(Article).filter(Article.id.in_(article_ids)).all()
    article_map = {a.id: a for a in articles}

    # Preserve similarity order and inject distance score
    scores = {h["article_id"]: h.get("distance", 0) for h in hits}
    ordered = [article_map[h["article_id"]] for h in hits if h["article_id"] in article_map]
    return {"query": q, "items": _search_items(db, ordered, "semantic", scores), "mode": "semantic"}


@router.get("/hybrid")
def hybrid_search(q: str = Query(..., min_length=1), limit: int = Query(default=20, ge=1, le=100), db: Session = Depends(get_db)):
    """Combine FTS5 + semantic: deduplicate and merge rankings (P1)."""
    # FTS5 results
    try:
        from sqlalchemy import text
        fts_results = db.execute(
            text("""
                SELECT a.id FROM articles a
                JOIN articles_fts fts ON a.id = fts.rowid
                WHERE articles_fts MATCH :query
                ORDER BY rank
                LIMIT :limit
            """),
            {"query": q, "limit": limit}
        ).fetchall()
        fts_ids = {r.id: i for i, r in enumerate(fts_results)}
    except Exception:
        fts_ids = {}

    # Semantic results
    vs = VectorStore()
    sem_results = vs.search(q, limit=limit)
    sem_ids = {h["article_id"]: i for i, h in enumerate(sem_results)}
    sem_scores = {h["article_id"]: h.get("distance", 0) for h in sem_results}

    # Merge: take union, score = min(fts_rank, semantic_rank)
    all_ids = set(fts_ids.keys()) | set(sem_ids.keys())
    if not all_ids:
        return {"query": q, "items": [], "mode": "hybrid"}

    articles = db.query(Article).filter(Article.id.in_(list(all_ids))).all()
    article_map = {a.id: a for a in articles}

    # Score: lower is better; if missing from one source, penalize
    scored = []
    for aid in all_ids:
        fts_score = fts_ids.get(aid, 999)
        sem_score = sem_ids.get(aid, 999)
        combined = min(fts_score, sem_score * 2)  # weight semantic slightly lower
        scored.append((combined, aid))

    scored.sort()
    ordered = [article_map[aid] for _, aid in scored if aid in article_map]
    scores = {aid: sem_scores.get(aid, 0) for aid in all_ids}
    return {"query": q, "items": _search_items(db, ordered[:limit], "hybrid", scores), "mode": "hybrid"}
