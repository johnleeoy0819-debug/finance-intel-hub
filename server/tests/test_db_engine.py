import os
import tempfile
from pathlib import Path

from src.db.engine import engine, SessionLocal, get_db
from src.config import Settings


def test_engine_creates_sqlite_db():
    """验证引擎能连接并创建数据库文件"""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        url = f"sqlite:///{db_path}"
        from sqlalchemy import create_engine as ce
        test_engine = ce(url)
        # 连接即创建文件
        assert not db_path.exists()  # 连接前不存在
        conn = test_engine.connect()
        conn.close()
        assert db_path.exists()  # 连接后存在


def test_session_local():
    """验证 SessionLocal 能创建会话"""
    from sqlalchemy.orm import Session
    db = SessionLocal()
    assert isinstance(db, Session)
    db.close()
