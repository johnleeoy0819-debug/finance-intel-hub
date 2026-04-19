import tempfile
from pathlib import Path
from unittest.mock import patch

from fastapi import HTTPException

from src.db.models import UploadTask


def test_upload_file(client):
    with tempfile.TemporaryDirectory() as tmpdir:
        upload_dir = Path(tmpdir)
        with patch("src.api.upload.UPLOAD_DIR", upload_dir):
            response = client.post(
                "/api/upload",
                files={"file": ("test.txt", b"hello world", "text/plain")},
            )
            assert response.status_code == 200
            data = response.json()
            assert data["original_filename"] == "test.txt"
            assert data["status"] == "pending"


def test_upload_file_unsupported_type(client):
    response = client.post(
        "/api/upload",
        files={"file": ("test.exe", b"bad data", "application/octet-stream")},
    )
    assert response.status_code == 400


def test_upload_file_too_large(client):
    with patch("src.api.upload._check_file_size") as mock_check:
        mock_check.side_effect = HTTPException(
            status_code=413, detail="File too large"
        )
        response = client.post(
            "/api/upload",
            files={"file": ("test.txt", b"hello", "text/plain")},
        )
        assert response.status_code == 413


def test_upload_media_file(client):
    with tempfile.TemporaryDirectory() as tmpdir:
        upload_dir = Path(tmpdir)
        with patch("src.api.upload.UPLOAD_DIR", upload_dir):
            with patch("src.api.upload.VideoProcessor") as MockVP:
                MockVP.return_value.process_video_upload.return_value = {
                    "transcript": "test transcript"
                }
                response = client.post(
                    "/api/upload",
                    files={"file": ("test.mp3", b"fake audio", "audio/mpeg")},
                )
                assert response.status_code == 200
                data = response.json()
                assert data["task"]["status"] == "processing"
                assert data["result"]["transcript"] == "test transcript"


def test_list_upload_tasks(client, db):
    db.add(
        UploadTask(
            original_filename="a.txt",
            file_path="/tmp/a.txt",
            file_type="txt",
            status="pending",
        )
    )
    db.add(
        UploadTask(
            original_filename="b.txt",
            file_path="/tmp/b.txt",
            file_type="txt",
            status="completed",
        )
    )
    db.commit()

    response = client.get("/api/upload/tasks")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["original_filename"] == "b.txt"


def test_get_upload_task(client, db):
    task = UploadTask(
        original_filename="a.txt",
        file_path="/tmp/a.txt",
        file_type="txt",
        status="pending",
    )
    db.add(task)
    db.commit()

    response = client.get(f"/api/upload/tasks/{task.id}")
    assert response.status_code == 200
    assert response.json()["original_filename"] == "a.txt"


def test_get_upload_task_not_found(client):
    response = client.get("/api/upload/tasks/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"
