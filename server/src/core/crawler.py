from typing import List, Dict, Any, Optional
from urllib.parse import urlparse

from firecrawl import FirecrawlApp
from sqlalchemy.orm import Session

from src.config import settings
from src.db.models import Source, Article
from src.db.engine import SessionLocal


class FirecrawlDriver:
    def __init__(self):
        self.app = FirecrawlApp(api_key=settings.FIRECRAWL_API_KEY)

    def crawl(self, source: Source) -> List[Dict[str, Any]]:
        """Crawl a source and return list of article dicts."""
        config = source.config or "{}"
        import json
        cfg = json.loads(config) if isinstance(config, str) else config

        url = cfg.get("url", source.url)
        limit = cfg.get("limit", 10)

        try:
            result = self.app.scrape_url(url, params={"formats": ["markdown"]})
            if not result or not result.get("markdown"):
                return []

            return [{
                "url": url,
                "title": result.get("metadata", {}).get("title", "Untitled"),
                "author": result.get("metadata", {}).get("author"),
                "content": result["markdown"],
                "published_at": result.get("metadata", {}).get("publishedDate"),
            }]
        except Exception as e:
            print(f"Firecrawl error for {url}: {e}")
            return []


def is_duplicate(url: str, title: str = "") -> bool:
    """Check if article already exists by URL or title similarity."""
    db = SessionLocal()
    try:
        # Exact URL match
        if url and db.query(Article).filter(Article.url == url).first():
            return True
        return False
    finally:
        db.close()


def crawl_source(source_id: int) -> List[int]:
    """Crawl a source and process articles. Returns list of article IDs."""
    from src.core.processor import ArticleProcessor

    db = SessionLocal()
    try:
        source = db.query(Source).filter(Source.id == source_id).first()
        if not source or not source.is_active:
            return []

        driver = FirecrawlDriver()
        articles = driver.crawl(source)

        processor = ArticleProcessor()
        article_ids = []

        for art in articles:
            if is_duplicate(art.get("url", ""), art.get("title", "")):
                continue

            result = processor.process(
                raw_content=art["content"],
                source_url=art.get("url", ""),
                title=art.get("title"),
                author=art.get("author"),
            )

            if result.get("status") == "irrelevant":
                continue

            article = Article(
                source_id=source.id,
                url=art.get("url"),
                title=result["title"],
                author=art.get("author"),
                published_at=art.get("published_at"),
                clean_content=result["clean_content"],
                summary=result["summary"],
                key_points=json.dumps(result["key_points"], ensure_ascii=False),
                entities=json.dumps(result["entities"], ensure_ascii=False),
                sentiment=result["sentiment"],
                importance=result["importance"],
                status="completed",
            )
            db.add(article)
            db.commit()
            db.refresh(article)
            article_ids.append(article.id)

        source.last_crawled_at = datetime.utcnow()
        db.commit()

        return article_ids
    finally:
        db.close()


from datetime import datetime
import json
