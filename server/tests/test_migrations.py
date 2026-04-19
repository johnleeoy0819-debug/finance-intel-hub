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


def test_fts5_table_exists():
    """验证 FTS5 虚拟表和触发器已创建"""
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='articles_fts'")
    assert cursor.fetchone() is not None, "articles_fts table missing"

    cursor.execute("SELECT name FROM sqlite_master WHERE type='trigger' AND name LIKE 'articles_fts_%'")
    triggers = {row[0] for row in cursor.fetchall()}
    expected_triggers = {"articles_fts_insert", "articles_fts_update", "articles_fts_delete"}
    assert expected_triggers.issubset(triggers), f"Missing FTS triggers: {expected_triggers - triggers}"

    conn.close()
