"""Tests for the backlinks engine."""
from src.db.models import Article, KnowledgeEdge
from src.core.backlinks import update_all_backlinks, get_backlinks_for_article


def test_update_all_backlinks_from_edges(db):
    a1 = Article(title="Source Article", status="completed")
    a2 = Article(title="Target Article", status="completed")
    db.add_all([a1, a2])
    db.commit()

    edge = KnowledgeEdge(
        source_article_id=a1.id,
        target_article_id=a2.id,
        relation_type="references",
        reason="cited in summary",
    )
    db.add(edge)
    db.commit()

    updated = update_all_backlinks(db)
    assert updated == 1

    backlinks = get_backlinks_for_article(db, a2.id)
    assert len(backlinks) == 1
    assert backlinks[0]["id"] == a1.id
    assert backlinks[0]["title"] == "Source Article"
    assert backlinks[0]["reason"] == "cited in summary"


def test_update_all_backlinks_no_edges(db):
    a1 = Article(title="Orphan", status="completed")
    db.add(a1)
    db.commit()

    updated = update_all_backlinks(db)
    assert updated == 0

    backlinks = get_backlinks_for_article(db, a1.id)
    assert backlinks == []


def test_update_all_backlinks_deduplicates(db):
    a1 = Article(title="Source", status="completed")
    a2 = Article(title="Target", status="completed")
    db.add_all([a1, a2])
    db.commit()

    # Two edges from same source should dedupe
    db.add_all([
        KnowledgeEdge(source_article_id=a1.id, target_article_id=a2.id, relation_type="related"),
        KnowledgeEdge(source_article_id=a1.id, target_article_id=a2.id, relation_type="similar"),
    ])
    db.commit()

    update_all_backlinks(db)
    backlinks = get_backlinks_for_article(db, a2.id)
    assert len(backlinks) == 1


def test_api_article_includes_backlinks(client, db):
    a1 = Article(title="Source", status="completed")
    a2 = Article(title="Target", status="completed")
    db.add_all([a1, a2])
    db.commit()

    db.add(KnowledgeEdge(source_article_id=a1.id, target_article_id=a2.id, relation_type="related"))
    db.commit()

    # Trigger update
    response = client.post("/api/articles/backlinks/update")
    assert response.status_code == 200
    assert response.json()["updated"] == 1

    # Verify article response includes backlinks
    response = client.get(f"/api/articles/{a2.id}")
    assert response.status_code == 200
    data = response.json()
    assert "backlinks" in data
    assert len(data["backlinks"]) == 1
    assert data["backlinks"][0]["title"] == "Source"
