from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from src.db.engine import get_db
from src.db.models import Article, KnowledgeEdge

router = APIRouter()


@router.get("/articles/{article_id}")
def article_graph(article_id: int, depth: int = 1, db: Session = Depends(get_db)):
    """Return knowledge graph centered on a specific article."""
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    # BFS up to given depth
    visited = {article_id}
    frontier = {article_id}
    all_ids = {article_id}
    edge_rows = []

    for _ in range(depth):
        if not frontier:
            break
        edges = db.query(KnowledgeEdge).filter(
            (KnowledgeEdge.source_article_id.in_(frontier)) |
            (KnowledgeEdge.target_article_id.in_(frontier))
        ).all()
        next_frontier = set()
        for e in edges:
            edge_rows.append(e)
            next_frontier.add(e.source_article_id)
            next_frontier.add(e.target_article_id)
        frontier = next_frontier - visited
        visited |= frontier
        all_ids |= visited

    articles = db.query(Article).filter(Article.id.in_(list(all_ids))).all()
    article_map = {a.id: a for a in articles}

    nodes = []
    for aid in all_ids:
        a = article_map.get(aid)
        if a:
            nodes.append({
                "id": a.id,
                "title": a.title,
                "category": a.primary_category_id,
                "sentiment": a.sentiment,
            })

    links = []
    seen_edges = set()
    for e in edge_rows:
        key = (e.source_article_id, e.target_article_id, e.relation_type)
        if key not in seen_edges:
            seen_edges.add(key)
            links.append({
                "source": e.source_article_id,
                "target": e.target_article_id,
                "type": e.relation_type,
                "strength": e.strength,
                "reason": e.reason,
            })

    return {"center_id": article_id, "nodes": nodes, "links": links}


@router.get("/global")
def global_graph(limit: int = 100, db: Session = Depends(get_db)):
    """Return global knowledge graph (recent articles + their edges)."""
    articles = db.query(Article).filter(Article.status == "completed").order_by(
        Article.created_at.desc()
    ).limit(limit).all()

    article_ids = {a.id for a in articles}
    edges = db.query(KnowledgeEdge).filter(
        (KnowledgeEdge.source_article_id.in_(article_ids)) |
        (KnowledgeEdge.target_article_id.in_(article_ids))
    ).all()

    # Include target nodes that might be outside the limit
    for e in edges:
        article_ids.add(e.source_article_id)
        article_ids.add(e.target_article_id)

    all_articles = db.query(Article).filter(Article.id.in_(list(article_ids))).all()
    article_map = {a.id: a for a in all_articles}

    nodes = []
    for a in all_articles:
        nodes.append({
            "id": a.id,
            "title": a.title,
            "category": a.primary_category_id,
            "sentiment": a.sentiment,
        })

    links = []
    seen = set()
    for e in edges:
        key = (e.source_article_id, e.target_article_id)
        if key not in seen:
            seen.add(key)
            links.append({
                "source": e.source_article_id,
                "target": e.target_article_id,
                "type": e.relation_type,
                "strength": e.strength,
                "reason": e.reason,
            })

    return {"nodes": nodes, "links": links}
