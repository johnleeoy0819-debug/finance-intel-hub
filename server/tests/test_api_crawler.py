from unittest.mock import patch

from src.db.models import Source


def test_create_source(client):
    with patch("src.api.crawler.add_crawl_job"):
        payload = {
            "name": "Test Source",
            "url": "https://example.com",
            "driver": "playwright",
            "is_active": 1,
        }
        response = client.post("/api/crawler/sources", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Source"
        assert data["url"] == "https://example.com"


def test_create_source_with_schedule(client):
    with patch("src.api.crawler.add_crawl_job") as mock_add:
        payload = {
            "name": "Scheduled Source",
            "url": "https://example.com",
            "schedule": "0 0 * * *",
        }
        response = client.post("/api/crawler/sources", json=payload)
        assert response.status_code == 200
        mock_add.assert_called_once()


def test_create_source_validation_error(client):
    response = client.post(
        "/api/crawler/sources",
        json={"name": "", "url": "https://example.com"},
    )
    assert response.status_code == 422


def test_list_sources(client, db):
    db.add(Source(name="Source 1", url="https://a.com", driver="firecrawl"))
    db.add(Source(name="Source 2", url="https://b.com", driver="jina"))
    db.commit()

    response = client.get("/api/crawler/sources")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_update_source(client, db):
    source = Source(name="Old", url="https://old.com", driver="firecrawl")
    db.add(source)
    db.commit()

    with patch("src.api.crawler.remove_crawl_job"), patch("src.api.crawler.add_crawl_job"):
        payload = {"name": "New"}
        response = client.put(f"/api/crawler/sources/{source.id}", json=payload)
        assert response.status_code == 200
        assert response.json()["name"] == "New"


def test_update_source_not_found(client):
    with patch("src.api.crawler.remove_crawl_job"), patch("src.api.crawler.add_crawl_job"):
        response = client.put("/api/crawler/sources/9999", json={"name": "New"})
        assert response.status_code == 404


def test_delete_source(client, db):
    source = Source(name="To Delete", url="https://del.com", driver="firecrawl")
    db.add(source)
    db.commit()

    with patch("src.api.crawler.remove_crawl_job"):
        response = client.delete(f"/api/crawler/sources/{source.id}")
        assert response.status_code == 200
        assert response.json() == {"ok": True}
        assert db.query(Source).filter(Source.id == source.id).first() is None


def test_delete_source_not_found(client):
    with patch("src.api.crawler.remove_crawl_job"):
        response = client.delete("/api/crawler/sources/9999")
        assert response.status_code == 404


def test_trigger_crawl(client, db):
    source = Source(name="Test", url="https://example.com", driver="firecrawl")
    db.add(source)
    db.commit()

    with patch("src.api.crawler.crawl_source", return_value=[1, 2, 3]) as mock_crawl:
        response = client.post(f"/api/crawler/trigger/{source.id}")
        assert response.status_code == 200
        assert response.json() == {"article_ids": [1, 2, 3]}
        mock_crawl.assert_called_once_with(source.id)


def test_trigger_crawl_not_found(client):
    with patch("src.api.crawler.crawl_source"):
        response = client.post("/api/crawler/trigger/9999")
        assert response.status_code == 404


def test_crawl_source_saves_tags_and_categories(db):
    """Bug 2/4/5 fix: verify category resolution, tag saving, and JSON serialization."""
    from src.core.db_utils import resolve_category_ids, save_article_tags, json_dumps_field
    from src.db.models import Article, Tag, ArticleTag, Category

    cat = Category(name="TestCat", slug="test-cat")
    db.add(cat)
    db.commit()

    # Test category resolution
    primary_id, secondary_id = resolve_category_ids(db, "TestCat", None)
    assert primary_id == cat.id
    assert secondary_id is None

    # Test JSON serialization
    assert json_dumps_field(["a", "b"]) == '["a", "b"]'
    assert json_dumps_field(None) is None

    # Test tag saving
    article = Article(title="Tag Test", status="completed")
    db.add(article)
    db.commit()

    save_article_tags(db, article.id, ["tagA", "tagB"])
    tags = db.query(Tag).join(ArticleTag).filter(ArticleTag.article_id == article.id).all()
    tag_names = {t.name for t in tags}
    assert tag_names == {"tagA", "tagB"}
