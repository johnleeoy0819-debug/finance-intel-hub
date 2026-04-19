from src.db.models import Article, Category, Tag, ArticleTag, KnowledgeEdge


def test_list_articles_empty(client):
    response = client.get("/api/articles")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["items"] == []


def test_list_articles_pagination(client, db):
    for i in range(5):
        db.add(Article(title=f"Article {i}", status="completed"))
    db.commit()

    response = client.get("/api/articles?limit=2&offset=0")
    data = response.json()
    assert data["total"] == 5
    assert len(data["items"]) == 2

    response = client.get("/api/articles?limit=2&offset=4")
    data = response.json()
    assert len(data["items"]) == 1


def test_list_articles_category_filter(client, db):
    cat = Category(name="Macro", slug="macro")
    db.add(cat)
    db.commit()

    db.add(Article(title="In Category", primary_category_id=cat.id, status="completed"))
    db.add(Article(title="No Category", status="completed"))
    db.commit()

    response = client.get(f"/api/articles?category_id={cat.id}")
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "In Category"


def test_list_articles_tag_filter(client, db):
    article = Article(title="Tagged Article", status="completed")
    tag = Tag(name="finance")
    db.add_all([article, tag])
    db.commit()

    db.add(ArticleTag(article_id=article.id, tag_id=tag.id))
    db.commit()

    response = client.get("/api/articles?tag=finance")
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Tagged Article"


def test_list_articles_status_filter(client, db):
    db.add(Article(title="Pending", status="pending"))
    db.add(Article(title="Completed", status="completed"))
    db.commit()

    response = client.get("/api/articles?status=pending")
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Pending"


def test_list_articles_invalid_limit(client):
    response = client.get("/api/articles?limit=0")
    assert response.status_code == 422


def test_get_article_success(client, db):
    article = Article(title="Test Article", status="completed")
    db.add(article)
    db.commit()

    response = client.get(f"/api/articles/{article.id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Test Article"


def test_get_article_not_found(client):
    response = client.get("/api/articles/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Article not found"


def test_delete_article_success(client, db):
    article = Article(title="To Delete", status="completed")
    db.add(article)
    db.commit()

    response = client.delete(f"/api/articles/{article.id}")
    assert response.status_code == 200
    assert response.json() == {"ok": True}

    assert db.query(Article).filter(Article.id == article.id).first() is None


def test_delete_article_not_found(client):
    response = client.delete("/api/articles/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Article not found"


def test_get_related_articles(client, db):
    a1 = Article(title="Article 1", status="completed")
    a2 = Article(title="Article 2", status="completed")
    db.add_all([a1, a2])
    db.commit()

    edge = KnowledgeEdge(source_article_id=a1.id, target_article_id=a2.id, relation_type="related")
    db.add(edge)
    db.commit()

    response = client.get(f"/api/articles/{a1.id}/related")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Article 2"


def test_get_related_articles_empty(client, db):
    article = Article(title="Lonely", status="completed")
    db.add(article)
    db.commit()

    response = client.get(f"/api/articles/{article.id}/related")
    assert response.status_code == 200
    assert response.json() == []


def test_correct_article_success(client, db):
    article = Article(title="Test", status="completed")
    db.add(article)
    db.commit()

    payload = {
        "field": "primary_category",
        "original_value": "old",
        "corrected_value": "1",
    }
    response = client.post(f"/api/articles/{article.id}/correct", json=payload)
    assert response.status_code == 200
    assert response.json() == {"ok": True}

    db.refresh(article)
    assert article.primary_category_id == 1


def test_correct_article_not_found(client):
    payload = {"field": "title", "corrected_value": "New Title"}
    response = client.post("/api/articles/9999/correct", json=payload)
    assert response.status_code == 404
