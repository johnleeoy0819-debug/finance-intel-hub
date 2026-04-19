import sqlite3
from pathlib import Path
from src.config import settings


def test_all_tables_exist():
    """验证迁移后所有表都存在"""
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cursor.fetchall()}
    conn.close()

    expected = {
        "alembic_version",
        "categories", "sources", "articles", "tags",
        "article_tags", "knowledge_edges", "corrections",
        "upload_tasks", "video_transcripts",
        "publications", "publication_chapters",
        "skill_feedback",
    }
    assert expected.issubset(tables), f"Missing tables: {expected - tables}"
