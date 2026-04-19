"""Export wiki pages and articles to markdown files."""
import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

from sqlalchemy.orm import Session

from src.db.models import WikiPage, Article
from src.core.db_utils import json_loads_field


def _build_frontmatter(page: WikiPage) -> str:
    """Build YAML frontmatter for a wiki page."""
    lines = ["---"]
    lines.append(f"title: {page.title}")
    lines.append(f"topic: {page.topic}")
    lines.append(f"slug: {page.slug}")
    if page.compiled_at:
        lines.append(f"compiled_at: {page.compiled_at.isoformat()}")
    lines.append(f"article_count: {page.article_count}")
    if page.source_article_ids:
        try:
            ids = json.loads(page.source_article_ids)
            lines.append(f"source_article_ids: {ids}")
        except json.JSONDecodeError:
            pass
    lines.append("---")
    return "\n".join(lines)


def export_wiki_to_markdown(db: Session, export_dir: str) -> int:
    """Export all wiki pages to markdown files. Returns file count."""
    out = Path(export_dir)
    out.mkdir(parents=True, exist_ok=True)

    pages = db.query(WikiPage).all()
    for page in pages:
        frontmatter = _build_frontmatter(page)
        content = f"{frontmatter}\n\n{page.content or ''}\n"
        file_path = out / f"{page.slug}.md"
        file_path.write_text(content, encoding="utf-8")

    return len(pages)


def export_articles_to_markdown(db: Session, export_dir: str) -> int:
    """Export all completed articles to markdown files. Returns file count."""
    out = Path(export_dir) / "articles"
    out.mkdir(parents=True, exist_ok=True)

    articles = db.query(Article).filter(Article.status == "completed").all()
    for article in articles:
        lines = ["---"]
        lines.append(f"title: {article.title}")
        if article.url:
            lines.append(f"url: {article.url}")
        if article.author:
            lines.append(f"author: {article.author}")
        if article.summary:
            lines.append(f"summary: {article.summary}")
        lines.append(f"status: {article.status}")
        lines.append("---")
        frontmatter = "\n".join(lines)

        slug = article.title[:50].replace(" ", "-").replace("/", "-") if article.title else f"article-{article.id}"
        content = f"{frontmatter}\n\n{article.clean_content or ''}\n"
        file_path = out / f"{article.id}_{slug}.md"
        file_path.write_text(content, encoding="utf-8")

    return len(articles)


def export_all_to_markdown(db: Session, base_dir: str) -> Dict[str, int]:
    """Export wiki + articles. Returns counts."""
    wiki_count = export_wiki_to_markdown(db, str(Path(base_dir) / "wiki"))
    article_count = export_articles_to_markdown(db, str(Path(base_dir) / "articles"))
    return {"wiki": wiki_count, "articles": article_count}


def git_commit_export(export_dir: str) -> Dict[str, Any]:
    """Git init (if needed), add, commit in export dir."""
    repo = Path(export_dir)
    repo.mkdir(parents=True, exist_ok=True)

    # Init if needed
    git_dir = repo / ".git"
    if not git_dir.exists():
        subprocess.run(["git", "init"], cwd=str(repo), capture_output=True, check=True)

    # Configure git user if not set
    for key, val in [("user.email", "kb@local"), ("user.name", "KnowledgeBase")]:
        result = subprocess.run(
            ["git", "config", key],
            cwd=str(repo), capture_output=True, text=True
        )
        if not result.stdout.strip():
            subprocess.run(["git", "config", key, val], cwd=str(repo), capture_output=True, check=True)

    # Add and commit
    subprocess.run(["git", "add", "."], cwd=str(repo), capture_output=True, check=True)
    commit_msg = f"Export {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    result = subprocess.run(
        ["git", "commit", "-m", commit_msg],
        cwd=str(repo), capture_output=True, text=True
    )

    # Get commit hash
    hash_result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=str(repo), capture_output=True, text=True
    )
    commit_hash = hash_result.stdout.strip() if hash_result.returncode == 0 else None

    return {
        "committed": result.returncode == 0 or "nothing to commit" in result.stdout.lower() or "nothing to commit" in result.stderr.lower(),
        "commit_hash": commit_hash,
        "message": commit_msg,
    }
