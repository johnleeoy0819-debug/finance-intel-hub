"""Tests for wiki markdown export."""
import tempfile
from pathlib import Path

from src.db.models import WikiPage, Article
from src.core.wiki_export import export_wiki_to_markdown, export_all_to_markdown, git_commit_export


def test_export_wiki_to_markdown(db):
    db.add(WikiPage(title="Test Wiki", slug="test-wiki", topic="test", content="# Hello\n\nWorld", article_count=2))
    db.commit()

    with tempfile.TemporaryDirectory() as tmpdir:
        count = export_wiki_to_markdown(db, tmpdir)
        assert count == 1
        file_path = Path(tmpdir) / "test-wiki.md"
        assert file_path.exists()
        content = file_path.read_text()
        assert "---" in content
        assert "title: Test Wiki" in content
        assert "# Hello" in content


def test_export_articles_to_markdown(db):
    db.add(Article(title="Article One", status="completed", clean_content="Content one"))
    db.commit()

    with tempfile.TemporaryDirectory() as tmpdir:
        counts = export_all_to_markdown(db, tmpdir)
        assert counts["wiki"] == 0
        assert counts["articles"] == 1
        article_dir = Path(tmpdir) / "articles"
        assert any(article_dir.iterdir())


def test_git_commit_export():
    with tempfile.TemporaryDirectory() as tmpdir:
        Path(tmpdir).joinpath("test.md").write_text("# Test")
        result = git_commit_export(tmpdir)
        assert result["committed"] is True
        assert result["commit_hash"] is not None
        assert len(result["commit_hash"]) == 40
