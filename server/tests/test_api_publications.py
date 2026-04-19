from unittest.mock import patch

from src.db.models import Publication


def test_list_publications_empty(client):
    response = client.get("/api/publications")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["items"] == []


def test_list_publications(client, db):
    db.add(Publication(pub_type="arxiv", title="Paper 1", authors="Alice"))
    db.add(Publication(pub_type="journal", title="Paper 2", authors="Bob"))
    db.commit()

    response = client.get("/api/publications")
    data = response.json()
    assert data["total"] == 2


def test_list_publications_filter_by_type(client, db):
    db.add(Publication(pub_type="arxiv", title="ArXiv Paper"))
    db.add(Publication(pub_type="journal", title="Journal Paper"))
    db.commit()

    response = client.get("/api/publications?pub_type=arxiv")
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "ArXiv Paper"


def test_list_publications_search(client, db):
    db.add(Publication(pub_type="arxiv", title="Quantum Computing", authors="Alice"))
    db.add(Publication(pub_type="arxiv", title="Biology", authors="Bob"))
    db.commit()

    response = client.get("/api/publications?q=Quantum")
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Quantum Computing"


def test_import_publication(client, db):
    with patch("src.api.publications.fetch_by_url") as mock_fetch:
        mock_fetch.return_value = {
            "pub_type": "arxiv",
            "title": "New Paper",
            "authors": "Alice",
            "doi": "10.1234/test",
            "url": "https://arxiv.org/abs/2401.00001",
        }
        response = client.post(
            "/api/publications/import",
            params={"url": "https://arxiv.org/abs/2401.00001"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["created"] is True
        assert data["publication"]["title"] == "New Paper"


def test_import_publication_duplicate(client, db):
    existing = Publication(pub_type="arxiv", title="Existing", doi="10.1234/test")
    db.add(existing)
    db.commit()

    with patch("src.api.publications.fetch_by_url") as mock_fetch:
        mock_fetch.return_value = {
            "pub_type": "arxiv",
            "title": "Existing",
            "doi": "10.1234/test",
        }
        response = client.post(
            "/api/publications/import",
            params={"url": "https://arxiv.org/abs/2401.00001"},
        )
        assert response.status_code == 200
        assert response.json()["created"] is False


def test_import_publication_fetch_error(client):
    with patch(
        "src.api.publications.fetch_by_url",
        side_effect=Exception("network error"),
    ):
        response = client.post(
            "/api/publications/import",
            params={"url": "https://bad.url"},
        )
        assert response.status_code == 400
        assert "Failed to fetch metadata" in response.json()["detail"]


def test_delete_publication(client, db):
    pub = Publication(pub_type="arxiv", title="To Delete")
    db.add(pub)
    db.commit()

    response = client.delete(f"/api/publications/{pub.id}")
    assert response.status_code == 200
    assert response.json() == {"ok": True}
    assert db.query(Publication).filter(Publication.id == pub.id).first() is None


def test_delete_publication_not_found(client):
    response = client.delete("/api/publications/9999")
    assert response.status_code == 404


def test_import_publication_duplicate_without_doi(client, db):
    """Bug 11 fix: fallback dedup by title+authors+source when DOI is absent."""
    existing = Publication(pub_type="arxiv", title="No DOI Paper", authors="Alice", source="arxiv")
    db.add(existing)
    db.commit()

    with patch("src.api.publications.fetch_by_url") as mock_fetch:
        mock_fetch.return_value = {
            "pub_type": "arxiv",
            "title": "No DOI Paper",
            "authors": "Alice",
            "source": "arxiv",
        }
        response = client.post(
            "/api/publications/import",
            params={"url": "https://arxiv.org/abs/2401.00002"},
        )
        assert response.status_code == 200
        assert response.json()["created"] is False
