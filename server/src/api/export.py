"""Export API — markdown export and git sync."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pathlib import Path

from src.db.engine import get_db
from src.core.wiki_export import export_wiki_to_markdown, export_all_to_markdown, git_commit_export
from src.config import settings

router = APIRouter()


def _export_dir() -> Path:
    return Path(settings.DATA_DIR) / "export"


@router.post("/wiki")
def export_wiki(db: Session = Depends(get_db)):
    """Export all wiki pages to markdown files."""
    out = _export_dir() / "wiki"
    count = export_wiki_to_markdown(db, str(out))
    return {"status": "completed", "files_written": count, "path": str(out)}


@router.post("/all")
def export_all(db: Session = Depends(get_db)):
    """Export wiki pages + articles to markdown files."""
    out = _export_dir()
    counts = export_all_to_markdown(db, str(out))
    return {"status": "completed", "counts": counts, "path": str(out)}


@router.post("/git")
def export_git(db: Session = Depends(get_db)):
    """Export all content and commit to git."""
    out = _export_dir()
    export_all_to_markdown(db, str(out))
    result = git_commit_export(str(out))
    return {"status": "completed", "git": result}
