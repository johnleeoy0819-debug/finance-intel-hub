from src.db.models import Article, KnowledgeEdge


def test_article_graph(client, db):
    a1 = Article(title="Center", status="completed")
    a2 = Article(title="Related", status="completed")
    db.add_all([a1, a2])
    db.commit()

    edge = KnowledgeEdge(
        source_article_id=a1.id,
        target_article_id=a2.id,
        relation_type="cites",
        strength=0.9,
    )
    db.add(edge)
    db.commit()

    response = client.get(f"/api/graph/articles/{a1.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["center_id"] == a1.id
    assert len(data["nodes"]) == 2
    assert len(data["links"]) == 1
    assert data["links"][0]["type"] == "cites"


def test_article_graph_not_found(client):
    response = client.get("/api/graph/articles/9999")
    assert response.status_code == 404


def test_global_graph(client, db):
    a1 = Article(title="Global 1", status="completed")
    a2 = Article(title="Global 2", status="completed")
    db.add_all([a1, a2])
    db.commit()

    edge = KnowledgeEdge(
        source_article_id=a1.id,
        target_article_id=a2.id,
        relation_type="related",
    )
    db.add(edge)
    db.commit()

    response = client.get("/api/graph/global")
    assert response.status_code == 200
    data = response.json()
    assert len(data["nodes"]) >= 2
    assert len(data["links"]) == 1


def test_global_graph_empty(client):
    response = client.get("/api/graph/global")
    assert response.status_code == 200
    data = response.json()
    assert data["nodes"] == []
    assert data["links"] == []
