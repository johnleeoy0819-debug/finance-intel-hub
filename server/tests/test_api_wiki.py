"""Tests for wiki API endpoints."""
from src.db.models import WikiPage


def test_writeback_to_wiki(client, db):
    response = client.post("/api/wiki/writeback", json={
        "title": "Chat Answer Summary",
        "content": "# Summary\n\nThis is a valuable chat answer.",
        "source_query": "What is AI?",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["slug"] == "chat-answer-summary"

    # Verify page exists
    page = db.query(WikiPage).filter(WikiPage.slug == "chat-answer-summary").first()
    assert page is not None
    assert page.title == "Chat Answer Summary"
    assert page.topic == "What is AI?"


def test_writeback_unique_slug(client, db):
    db.add(WikiPage(title="Chat Answer Summary", slug="chat-answer-summary", topic="t", content="c"))
    db.commit()

    response = client.post("/api/wiki/writeback", json={
        "title": "Chat Answer Summary",
        "content": "Another answer.",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["slug"] == "chat-answer-summary-1"
