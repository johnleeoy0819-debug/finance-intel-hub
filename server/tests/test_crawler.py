import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.core.crawler import (
    PlaywrightDriver,
    JinaReaderDriver,
    FirecrawlDriver,
    SmartCrawler,
    CrawlResult,
    is_duplicate,
    url_hash,
    normalize_url,
    CrawlError,
)


# ───────── Jina Reader ─────────
class TestJinaReaderDriver:
    @patch("src.core.crawler.requests.get")
    def test_crawl_returns_markdown(self, mock_get):
        mock_get.return_value = MagicMock(
            status_code=200,
            text=(
                "Title: Test Article\n"
                "URL Source: http://example.com\n"
                "Markdown Content:\n# Hello\n\nThis is content.\n\n"
                "[link](https://other.com/page)"
            ),
        )
        driver = JinaReaderDriver()
        result = driver.crawl("http://example.com")
        assert result.title == "Test Article"
        assert "Hello" in result.content
        assert result.driver_used == "jina"
        assert "https://other.com/page" in result.links


# ───────── Firecrawl ─────────
class TestFirecrawlDriver:
    @patch("src.core.crawler.requests.post")
    def test_crawl_success(self, mock_post):
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {
                "data": {
                    "markdown": "# Title\n\nBody text.",
                    "html": "<h1>Title</h1><p>Body text.</p>",
                    "metadata": {"title": "Fire Title"},
                }
            },
        )
        driver = FirecrawlDriver(api_key="test_key")
        result = driver.crawl("http://example.com")
        assert result.title == "Fire Title"
        assert "Body text." in result.content
        assert result.driver_used == "firecrawl"


# ───────── Playwright (mocked) ─────────
class TestPlaywrightDriver:
    @pytest.mark.asyncio
    async def test_crawl_extracts_content(self):
        mock_page = AsyncMock()
        mock_page.title.return_value = "Page Title"
        mock_page.content.return_value = "<html><body>Hello</body></html>"
        mock_page.evaluate.side_effect = [
            "Hello World",
            ["https://a.com", "https://b.com"],
        ]
        mock_resp = MagicMock(status=200)
        mock_page.goto = AsyncMock(return_value=mock_resp)

        mock_browser = AsyncMock()
        mock_browser.new_page = AsyncMock(return_value=mock_page)

        mock_pw = AsyncMock()
        mock_pw.chromium.launch = AsyncMock(return_value=mock_browser)

        with patch("playwright.async_api.async_playwright", return_value=AsyncMock(start=AsyncMock(return_value=mock_pw))):
            driver = PlaywrightDriver()
            result = await driver.crawl("http://example.com")
            assert result.title == "Page Title"
            assert result.content == "Hello World"
            assert result.driver_used == "playwright"
            assert result.status_code == 200


# ───────── SmartCrawler ─────────
class TestSmartCrawler:
    def test_select_order_for_news(self):
        crawler = SmartCrawler()
        order = crawler._select_order("https://finance.sina.com.cn/china/")
        assert order[0] == "jina"

    def test_select_order_for_academic(self):
        crawler = SmartCrawler()
        order = crawler._select_order("https://arxiv.org/abs/2401.00001")
        assert order[0] == "playwright"

    def test_select_order_default(self):
        crawler = SmartCrawler()
        order = crawler._select_order("https://example.com")
        assert order == SmartCrawler.DEFAULT_ORDER

    @pytest.mark.asyncio
    @patch.object(JinaReaderDriver, "crawl")
    @patch.object(SmartCrawler, "_random_delay")
    async def test_crawl_uses_fallback(self, mock_delay, mock_jina):
        mock_jina.side_effect = Exception("blocked")

        crawler = SmartCrawler()
        crawler.drivers["playwright"] = MagicMock()
        crawler.drivers["playwright"].crawl.return_value = CrawlResult(
            url="http://test.com",
            title="Test",
            content="content",
            driver_used="playwright",
        )

        result = await crawler.crawl("http://test.com")
        assert result.driver_used == "playwright"

    @pytest.mark.asyncio
    @patch.object(JinaReaderDriver, "crawl")
    @patch.object(SmartCrawler, "_random_delay")
    async def test_crawl_retries_then_fallback(self, mock_delay, mock_jina):
        mock_jina.side_effect = Exception("blocked")

        crawler = SmartCrawler()
        crawler.drivers["playwright"] = MagicMock()
        crawler.drivers["playwright"].crawl.return_value = CrawlResult(
            url="http://test.com",
            title="Test",
            content="content",
            driver_used="playwright",
        )

        result = await crawler.crawl("http://test.com")
        assert mock_jina.call_count == 3
        assert result.driver_used == "playwright"

    @pytest.mark.asyncio
    @patch.object(JinaReaderDriver, "crawl")
    @patch.object(PlaywrightDriver, "crawl")
    @patch.object(FirecrawlDriver, "crawl")
    @patch.object(SmartCrawler, "_random_delay")
    async def test_crawl_all_fail_raises(self, mock_delay, mock_fc, mock_pw, mock_jina):
        mock_jina.side_effect = Exception("jina fail")
        mock_pw.side_effect = Exception("pw fail")
        mock_fc.side_effect = Exception("fc fail")

        crawler = SmartCrawler()
        with pytest.raises(CrawlError):
            await crawler.crawl("http://test.com")


# ───────── Utilities ─────────
class TestUtilities:
    def test_url_hash(self):
        h = url_hash("https://example.com")
        assert len(h) == 16
        assert isinstance(h, str)

    def test_normalize_url(self):
        assert normalize_url("https://example.com/page?q=1#frag") == "https://example.com/page"


# ───────── Deduplication ─────────
class TestIsDuplicate:
    def test_is_duplicate_by_url(self, db_session):
        from src.db.models import Article
        article = Article(title="Test", url="http://example.com", status="completed")
        db_session.add(article)
        db_session.commit()

        assert is_duplicate("http://example.com", session=db_session) is True
        assert is_duplicate("http://new.com", session=db_session) is False
