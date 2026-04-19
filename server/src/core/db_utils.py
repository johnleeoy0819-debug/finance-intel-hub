"""Shared DB utilities for article ingestion: category resolution, tag saving, JSON fields."""
import json
import logging
from typing import Any, List, Optional, Tuple

from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


def json_dumps_field(value: Any) -> Optional[str]:
    """Serialize a Python object to JSON string for Text column storage."""
    if value is None:
        return None
    if isinstance(value, str):
        # Already a string — if it looks like JSON, store as-is; otherwise wrap
        try:
            json.loads(value)
            return value
        except (json.JSONDecodeError, TypeError):
            return json.dumps(value, ensure_ascii=False)
    return json.dumps(value, ensure_ascii=False)


def json_loads_field(value: Optional[str]) -> Any:
    """Deserialize a JSON string from Text column back to Python object."""
    if value is None or value == "":
        return None
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return value


def resolve_category_ids(
    db: Session,
    primary_name: Optional[str],
    secondary_name: Optional[str],
) -> Tuple[Optional[int], Optional[int]]:
    """Map category names to category IDs. Returns (primary_id, secondary_id)."""
    from src.db.models import Category

    primary_id = None
    secondary_id = None

    if primary_name:
        cat = db.query(Category).filter(Category.name == primary_name).first()
        if cat:
            primary_id = cat.id
        else:
            logger.warning(f"Primary category not found: {primary_name}")

    if secondary_name:
        cat = db.query(Category).filter(Category.name == secondary_name).first()
        if cat:
            secondary_id = cat.id
        else:
            logger.warning(f"Secondary category not found: {secondary_name}")

    return primary_id, secondary_id


def save_article_tags(db: Session, article_id: int, tag_names: List[str]) -> None:
    """Upsert tags and create ArticleTag associations."""
    from src.db.models import Tag, ArticleTag

    if not tag_names:
        return

    for name in tag_names:
        if not name or not isinstance(name, str):
            continue
        name = name.strip()
        if not name:
            continue

        tag = db.query(Tag).filter(Tag.name == name).first()
        if not tag:
            tag = Tag(name=name, usage_count=1)
            db.add(tag)
            db.commit()
            db.refresh(tag)
        else:
            tag.usage_count += 1
            db.commit()

        # Avoid duplicate associations
        exists = db.query(ArticleTag).filter(
            ArticleTag.article_id == article_id,
            ArticleTag.tag_id == tag.id,
        ).first()
        if not exists:
            db.add(ArticleTag(article_id=article_id, tag_id=tag.id))
            db.commit()
