"""Smart Crawler - Triple fallback: Playwright → Jina Reader → Firecrawl."""
from __future__ import annotations

import asyncio
import hashlib
import logging
import random
import re
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from urllib.parse import urlparse

import httpx
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


@dataclass
class CrawlResult:
    """Unified crawl result across all drivers."""

    url: str
    title: str = ""
    content: str = ""
    html: str = ""
    links: List[str] = field(default_factory=list)
    driver_used: str = ""
    status_code: int = 200
    crawled_at: datetime = field(default_factory=datetime.utcnow)


# ────────────────────────
# Driver 1: Playwright (Browser)
# ────────────────────────
class PlaywrightDriver:
    """Headless browser extraction via Playwright."""

    def __init__(self, timeout: int = 90_000):
        self.timeout = timeout
        self._browser = None
        self._playwright = None

    async def _get_browser(self):
        """Lazy-init browser instance."""
        if self._browser is None:
            from playwright.async_api import async_playwright
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(headless=True)
        return self._browser

    async def crawl(self, url: str) -> CrawlResult:
        browser = await self._get_browser()
        page = await browser.new_page()
        try:
            resp = await page.goto(url, wait_until="domcontentloaded", timeout=self.timeout)
            # Wait a bit for lazy-loaded content
            await asyncio.sleep(1.5)
            title = await page.title()
            html = await page.content()
            # Extract text from article/main/body
            text = await page.evaluate(
                """() => {
                    const el = document.querySelector('article') 
                              || document.querySelector('main') 
                              || document.querySelector('[role="main"]')
                              || document.body;
                    return el ? el.innerText.replace(/\\s+/g, ' ').trim() : '';
                }"""
            )
            links = await page.evaluate(
                """() => Array.from(document.querySelectorAll('a[href]'))
                         .map(a => a.href)
                         .filter(h => h.startsWith('http'))"""
            )
            return CrawlResult(
                url=url,
                title=title or "",
                content=text or "",
                html=html or "",
                links=list(set(links))[:100],
                driver_used="playwright",
                status_code=resp.status if resp else 200,
            )
        finally:
            await page.close()

    async def close(self):
        if self._browser:
            await self._browser.close()
            self._browser = None
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None

    def __del__(self):
        if self._browser or self._playwright:
            try:
                asyncio.get_event_loop().create_task(self.close())
            except Exception:
                pass


# ────────────────────────
# Driver 2: Jina Reader (Free API)
# ────────────────────────
class JinaReaderDriver:
    """https://r.jina.ai/http://URL — fast static extraction."""

    async def crawl(self, url: str) -> CrawlResult:
        jina_url = f"https://r.jina.ai/http://{url}"
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.get(jina_url)
            r.raise_for_status()
            text = r.text

        # Parse Jina output: Title: X\nURL Source: X\nMarkdown Content:\n...
        title = ""
        content = text
        if "Markdown Content:" in text:
            parts = text.split("Markdown Content:", 1)
            header = parts[0]
            content = parts[1].strip()
            for line in header.splitlines():
                if line.startswith("Title:"):
                    title = line.replace("Title:", "").strip()

        # Extract links from markdown
        links = re.findall(r'\[.*?\]\((https?://[^\)]+)\)', content)

        return CrawlResult(
            url=url,
            title=title,
            content=content,
            links=list(set(links))[:100],
            driver_used="jina",
        )


# ────────────────────────
# Driver 3: Firecrawl (Tertiary)
# ────────────────────────
class FirecrawlDriver:
    """Existing Firecrawl API driver."""

    def __init__(self, api_key: str | None = None):
        from src.config import settings
        self.api_key = api_key or settings.FIRECRAWL_API_KEY

    async def crawl(self, url: str) -> CrawlResult:
        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(
                "https://api.firecrawl.dev/v1/scrape",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json={"url": url, "formats": ["markdown", "html"]},
            )
            r.raise_for_status()
            data = r.json().get("data", {})
        md = data.get("markdown", "")
        html = data.get("html", "")
        title = data.get("metadata", {}).get("title", "")
        links = re.findall(r'\[.*?\]\((https?://[^\)]+)\)', md)
        return CrawlResult(
            url=url,
            title=title,
            content=md,
            html=html,
            links=list(set(links))[:100],
            driver_used="firecrawl",
        )


# ────────────────────────
# Smart Crawler — Orchestrator
# ────────────────────────
class SmartCrawler:
    """Orchestrates drivers with retry + fallback + anti-crawl delays."""

    DELAY_MIN = 1.0
    DELAY_MAX = 3.0
    MAX_RETRIES = 3

    # Default priority order
    DEFAULT_ORDER = ["jina", "playwright", "firecrawl"]
    # News sites: Jina first (fast), then browser
    NEWS_ORDER = ["jina", "playwright", "firecrawl"]
    # Academic / JS-heavy: Playwright first
    ACADEMIC_ORDER = ["playwright", "jina", "firecrawl"]

    def __init__(self):
        self.drivers: dict[str, object] = {
            "playwright": PlaywrightDriver(),
            "jina": JinaReaderDriver(),
            "firecrawl": FirecrawlDriver(),
        }

    @staticmethod
    def _is_news_site(url: str) -> bool:
        domain = urlparse(url).netloc.lower()
        news_domains = [
            "sina.com.cn", "163.com", "qq.com", "sohu.com", "ifeng.com",
            "caijing.com.cn", "ce.cn", "stcn.com", "cs.com.cn",
            "economist.com", "ft.com", "bloomberg.com", "reuters.com",
            "wsj.com", "cnbc.com", "marketwatch.com",
            "zhihu.com", "xueqiu.com", "wallstreetcn.com",
            "36kr.com", "cls.cn", "thepaper.cn",
        ]
        return any(nd in domain for nd in news_domains)

    @staticmethod
    def _is_academic(url: str) -> bool:
        domain = urlparse(url).netloc.lower()
        return any(
            x in domain
            for x in ["arxiv.org", "ssrn.com", "jstor.org", "sciencedirect.com", "springer.com", "ncbi.nlm.nih.gov"]
        )

    def _select_order(self, url: str) -> list[str]:
        if self._is_academic(url):
            return list(self.ACADEMIC_ORDER)
        if self._is_news_site(url):
            return list(self.NEWS_ORDER)
        return list(self.DEFAULT_ORDER)

    async def _random_delay(self):
        delay = random.uniform(self.DELAY_MIN, self.DELAY_MAX)
        await asyncio.sleep(delay)

    async def crawl(self, url: str) -> CrawlResult:
        order = self._select_order(url)
        errors: list[str] = []

        for driver_name in order:
            driver = self.drivers[driver_name]
            for attempt in range(1, self.MAX_RETRIES + 1):
                try:
                    await self._random_delay()
                    logger.info(f"[{driver_name}] attempt {attempt}/{self.MAX_RETRIES} for {url}")
                    result = await driver.crawl(url)
                    logger.info(f"[{driver_name}] success for {url}")
                    return result
                except Exception as e:
                    logger.warning(f"[{driver_name}] attempt {attempt} failed: {e}")
                    if attempt == self.MAX_RETRIES:
                        errors.append(f"{driver_name}: {e}")

        # All drivers failed
        raise CrawlError(f"All drivers failed for {url}. Errors: {'; '.join(errors)}")

    async def close(self):
        for d in self.drivers.values():
            if hasattr(d, "close"):
                await d.close()


class CrawlError(Exception):
    pass


# ────────────────────────
# Source-level crawling
# ────────────────────────
def crawl_source(source_id: int) -> list[int]:
    """Crawl all articles from a source. Returns list of new article IDs."""
    import feedparser
    from src.db.engine import SessionLocal
    from src.db.models import Article, Source
    from src.core.processor import ArticleProcessor

    db = SessionLocal()
    crawler = SmartCrawler()
    loop = asyncio.new_event_loop()
    try:
        source = db.query(Source).filter(Source.id == source_id).first()
        if not source or not source.is_active:
            return []

        # Collect URLs to crawl
        urls: list[str] = []
        feed = feedparser.parse(source.url)
        if feed.entries:
            urls = [entry.link for entry in feed.entries if entry.get("link")]
        else:
            urls = [source.url]

        processor = ArticleProcessor()
        new_ids: list[int] = []

        for url in urls:
            if is_duplicate(url, session=db):
                continue

            try:
                result = loop.run_until_complete(crawler.crawl(url))
            except Exception as e:
                logger.warning(f"Crawl failed for {url}: {e}")
                continue

            if not result.content:
                continue

            # Process with AI pipeline
            processed = processor.process(
                raw_content=result.content,
                source_url=url,
                title=result.title,
            )
            if processed.get("status") == "irrelevant":
                continue

            article = Article(
                title=processed.get("title", result.title) or "Untitled",
                url=url,
                source_id=source_id,
                status="completed",
                clean_content=processed.get("clean_content", ""),
                summary=processed.get("summary", ""),
                key_points=processed.get("key_points", []),
                entities=processed.get("entities", []),
                sentiment=processed.get("sentiment", "neutral"),
                importance=processed.get("importance", "medium"),
                tags=processed.get("tags", []),
            )
            db.add(article)
            db.commit()
            db.refresh(article)
            new_ids.append(article.id)

        source.last_crawled_at = datetime.utcnow()
        db.commit()
        return new_ids
    finally:
        db.close()
        try:
            loop.run_until_complete(crawler.close())
        except Exception as e:
            logger.warning(f"Error closing crawler: {e}")
        loop.close()


# ────────────────────────
# Deduplication helpers
# ────────────────────────
def url_hash(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()[:16]


def is_duplicate(url: str, session=None) -> bool:
    """Check if article with this URL already exists in DB."""
    from src.db.models import Article

    if session is not None:
        return session.query(Article).filter(Article.url == url).first() is not None

    from src.db.engine import SessionLocal
    with SessionLocal() as db:
        return db.query(Article).filter(Article.url == url).first() is not None


def normalize_url(url: str) -> str:
    """Strip fragments and query params for dedup."""
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
