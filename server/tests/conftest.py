import os
os.environ.setdefault("OPENAI_API_KEY", "test-key")

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.main import app
from src.db.engine import get_db
from src.db.models import Base


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture(scope="function")
def api_engine():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine


@pytest.fixture
def db(api_engine):
    Session = sessionmaker(bind=api_engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def client(api_engine):
    SessionLocal = sessionmaker(bind=api_engine)

    def override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with patch("src.main.start_scheduler"), patch("src.main.shutdown_scheduler"):
        with patch("src.core.vector_store.VectorStore") as MockVS:
            MockVS.return_value.search.return_value = []
            MockVS.return_value.add_article.return_value = None
            with patch("src.api.search.VectorStore", new=MockVS):
                with TestClient(app) as client:
                    yield client

    app.dependency_overrides.clear()
