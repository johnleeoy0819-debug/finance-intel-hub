import logging
from unittest.mock import patch

from sqlalchemy.orm import Session
from src.db.models import Article


def test_fulltext_search_no_results(client):
    response = client.get("/api/search?q=test")
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "test"
    assert data["items"] == []


def test_fulltext_search_fts_fallback_logs_warning(client, db, caplog):
    """Regression: FTS5 failure must log a warning before falling back to LIKE."""
    db.add(Article(title="FTS Fallback Test", summary="test", status="completed"))
    db.commit()

    call_count = [0]
    orig_execute = Session.execute

    def fake_execute(self, stmt, *args, **kwargs):
        call_count[0] += 1
        sql_str = str(stmt)
        if "articles_fts MATCH" in sql_str and call_count[0] == 1:
            raise Exception("no such table: articles_fts")
        return orig_execute(self, stmt, *args, **kwargs)

    with caplog.at_level(logging.WARNING):
        with patch.object(Session, "execute", fake_execute):
            response = client.get("/api/search?q=test")

    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "test"
    assert any("FTS5 query failed" in r.message for r in caplog.records)


def test_fulltext_search_with_results(client, db):
    db.add(Article(title="Hello World", summary="test summary", status="completed"))
    db.commit()

    response = client.get("/api/search?q=Hello")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["article"]["title"] == "Hello World"


def test_search_missing_query(client):
    response = client.get("/api/search")
    assert response.status_code == 422


def test_semantic_search(client, db):
    article = Article(title="AI Finance", status="completed")
    db.add(article)
    db.commit()

    with patch("src.api.search.VectorStore") as MockVS:
        MockVS.return_value.search.return_value = [
            {"article_id": article.id, "distance": 0.1, "title": "AI Finance"}
        ]
        response = client.get("/api/search/semantic?q=artificial intelligence")
        data = response.json()
        assert data["mode"] == "semantic"
        assert len(data["items"]) == 1
        assert data["items"][0]["article"]["title"] == "AI Finance"
        assert data["items"][0]["score"] == 0.1


def test_semantic_search_no_results(client):
    with patch("src.api.search.VectorStore") as MockVS:
        MockVS.return_value.search.return_value = []
        response = client.get("/api/search/semantic?q=xyz")
        data = response.json()
        assert data["items"] == []


def test_hybrid_search(client, db):
    article = Article(title="Hybrid Test", status="completed")
    db.add(article)
    db.commit()

    with patch("src.api.search.VectorStore") as MockVS:
        MockVS.return_value.search.return_value = [
            {"article_id": article.id, "distance": 0.2, "title": "Hybrid Test"}
        ]
        response = client.get("/api/search/hybrid?q=test")
        assert response.status_code == 200
        data = response.json()
        assert data["mode"] == "hybrid"


def test_hybrid_search_no_results(client):
    with patch("src.api.search.VectorStore") as MockVS:
        MockVS.return_value.search.return_value = []
        response = client.get("/api/search/hybrid?q=nonexistent")
        data = response.json()
        assert data["items"] == []
