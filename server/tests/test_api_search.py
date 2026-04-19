from unittest.mock import patch

from src.db.models import Article


def test_fulltext_search_no_results(client):
    response = client.get("/api/search?q=test")
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "test"
    assert data["items"] == []


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
        assert response.status_code == 200
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
