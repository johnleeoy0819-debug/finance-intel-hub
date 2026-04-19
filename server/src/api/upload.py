import os
import shutil
import threading
import uuid
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from pathlib import Path

from src.db.engine import get_db, SessionLocal
from src.db.models import UploadTask, Article
from src.config import settings
from src.core.operation_logger import log_operation
from src.core.video_processor import VideoProcessor
from src.core.processor import ArticleProcessor
from src.core.url_processor import process_article_url, process_video_url, _is_video_url

router = APIRouter()

UPLOAD_DIR = Path(settings.STORAGE_PATH) / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
ALLOWED_EXTENSIONS = {
    # Documents
    ".pdf", ".doc", ".docx", ".txt", ".md", ".epub", ".html", ".htm",
    # Audio / Video (Whisper supported)
    ".mp3", ".mp4", ".m4a", ".wav", ".webm", ".ogg", ".oga", ".mpeg", ".mpga",
}

# Audio/video extensions that should go through Whisper
MEDIA_EXTENSIONS = {".mp3", ".mp4", ".m4a", ".wav", ".webm", ".ogg", ".oga", ".mpeg", ".mpga"}


def _safe_filename(filename: str) -> str:
    """Sanitize upload filename: strip path components, generate UUID base name."""
    name = Path(filename).name
    ext = Path(name).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {ext}. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    return f"{uuid.uuid4().hex}{ext}"


def _check_file_size(file: UploadFile) -> None:
    file.file.seek(0, os.SEEK_END)
    size = file.file.tell()
    file.file.seek(0)
    if size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large: {size} bytes. Max: {MAX_FILE_SIZE} bytes"
        )


@router.post("")
def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    _check_file_size(file)
    safe_name = _safe_filename(file.filename)
    file_path = UPLOAD_DIR / safe_name
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    ext = Path(safe_name).suffix.lower()
    is_media = ext in MEDIA_EXTENSIONS

    task = UploadTask(
        original_filename=file.filename,
        file_path=str(file_path),
        file_type=safe_name.split(".")[-1].lower(),
        file_size=os.path.getsize(file_path),
        status="processing" if is_media else "pending",
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    # If audio/video, transcribe immediately (sync for MVP)
    if is_media:
        try:
            vp = VideoProcessor()
            result = vp.process_video_upload(task.id, str(file_path), file.filename)
            log_operation("file_uploaded", target_type="upload", target_id=task.id, details={"filename": file.filename, "type": "video"})
            return {"task": task, "result": result}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"转录失败: {e}")

    log_operation("file_uploaded", target_type="upload", target_id=task.id, details={"filename": file.filename, "type": task.file_type})
    return task


@router.get("/tasks")
def list_tasks(db: Session = Depends(get_db)):
    return db.query(UploadTask).order_by(UploadTask.created_at.desc()).all()


class UrlUploadRequest(BaseModel):
    url: str


@router.post("/url")
def upload_url(req: UrlUploadRequest, db: Session = Depends(get_db)):
    """Submit a URL for processing (article or video)."""
    url = req.url.strip()
    if not url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="Invalid URL")

    is_video = _is_video_url(url)

    task = UploadTask(
        original_filename=url,
        file_path=url,
        file_type="video" if is_video else "article",
        status="processing",
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    def _process():
        db2 = SessionLocal()
        try:
            t = db2.query(UploadTask).filter(UploadTask.id == task.id).first()
            if is_video:
                result = process_video_url(url, original_filename=url)
            else:
                result = process_article_url(url)

            if result.get("status") == "completed":
                t.status = "completed"
                t.article_id = result.get("article_id")
            elif result.get("status") == "irrelevant":
                t.status = "completed"
                t.article_id = None
            else:
                t.status = "failed"
                t.error_message = result.get("error", "Unknown error")
            db2.commit()
        except Exception as e:
            if t:
                t.status = "failed"
                t.error_message = str(e)
                db2.commit()
        finally:
            db2.close()

    threading.Thread(target=_process, daemon=True).start()

    log_operation("url_submitted", target_type="upload", target_id=task.id, details={"url": url, "type": "video" if is_video else "article"})
    return {"task_id": task.id, "status": "processing", "type": "video" if is_video else "article"}


@router.get("/tasks/{task_id}")
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(UploadTask).filter(UploadTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
