import os
import shutil
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from pathlib import Path

from src.db.engine import get_db
from src.db.models import UploadTask, Article
from src.config import settings

router = APIRouter()

UPLOAD_DIR = Path(settings.STORAGE_PATH) / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("")
def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    file_path = UPLOAD_DIR / file.filename
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    task = UploadTask(
        original_filename=file.filename,
        file_path=str(file_path),
        file_type=file.filename.split(".")[-1].lower(),
        file_size=os.path.getsize(file_path),
        status="pending",
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("/tasks")
def list_tasks(db: Session = Depends(get_db)):
    return db.query(UploadTask).order_by(UploadTask.created_at.desc()).all()


@router.get("/tasks/{task_id}")
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(UploadTask).filter(UploadTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
