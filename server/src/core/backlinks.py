"""Backlinks engine — updates Article.backlinks from KnowledgeEdges and mentions."""
import json
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from src.db.models import Article, KnowledgeEdge


def update_all_backlinks(db: Session) -> int:
    """Recompute backlinks for all articles. Returns number of articles updated."""
    articles = db.query(Article).all()
    updated = 0

    for article in articles:
        backlinks: List[Dict[str, Any]] = []

        # 1. KnowledgeEdge reverse edges
        edges = db.query(KnowledgeEdge).filter(
            KnowledgeEdge.target_article_id == article.id
        ).all()
        for edge in edges:
            src = db.query(Article).filter(Article.id == edge.source_article_id).first()
            if src:
                backlinks.append({
                    "id": src.id,
                    "title": src.title,
                    "reason": edge.reason or f"related via {edge.relation_type}",
                })

        # 2. Deduplicate by id
        seen = set()
        deduped = []
        for b in backlinks:
            if b["id"] not in seen:
                seen.add(b["id"])
                deduped.append(b)

        # 3. Save
        new_val = json.dumps(deduped) if deduped else None
        if article.backlinks != new_val:
            article.backlinks = new_val
            updated += 1

    db.commit()
    return updated


def get_backlinks_for_article(db: Session, article_id: int) -> List[Dict[str, Any]]:
    """Get parsed backlinks for an article."""
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article or not article.backlinks:
        return []
    try:
        return json.loads(article.backlinks)
    except json.JSONDecodeError:
        return []


def update_backlinks(db: Session, article_id: int, source_article_ids: List[int]) -> None:
    """Update backlinks for a specific article by adding new source articles."""
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        return

    backlinks = []
    if article.backlinks:
        try:
            backlinks = json.loads(article.backlinks)
        except json.JSONDecodeError:
            backlinks = []

    existing_ids = {b["id"] for b in backlinks}
    for src_id in source_article_ids:
        if src_id in existing_ids:
            continue
        src = db.query(Article).filter(Article.id == src_id).first()
        if src:
            backlinks.append({
                "id": src.id,
                "title": src.title,
                "reason": "related article",
            })
            existing_ids.add(src.id)

    article.backlinks = json.dumps(backlinks, ensure_ascii=False) if backlinks else None
