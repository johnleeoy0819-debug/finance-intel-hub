"""Tests for operation logs API."""
from src.db.models import OperationLog


def test_list_operations_empty(client):
    response = client.get("/api/operations")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["items"] == []


def test_list_operations_filter_by_type(client, db):
    db.add(OperationLog(operation_type="wiki_compiled", target_type="wiki_page", target_id="1"))
    db.add(OperationLog(operation_type="lint_run", target_type="system"))
    db.commit()

    response = client.get("/api/operations?operation_type=wiki_compiled")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["operation_type"] == "wiki_compiled"


def test_list_operations_pagination(client, db):
    for i in range(5):
        db.add(OperationLog(operation_type="test_op", target_id=str(i)))
    db.commit()

    response = client.get("/api/operations?limit=2&offset=0")
    data = response.json()
    assert len(data["items"]) == 2
    assert data["total"] == 5


def test_settings_update_creates_log(client, db):
    """Settings update should auto-log via operation_logger."""
    response = client.put("/api/settings/rules", json={"rules": "# test rules"})
    assert response.status_code == 200

    response = client.get("/api/operations?operation_type=rules_updated")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["target_type"] == "user_rule"
