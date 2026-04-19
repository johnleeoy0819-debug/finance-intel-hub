"""Process URLs: articles via crawler, videos via yt-dlp + Whisper."""
import asyncio
import logging
import os
import tempfile
import uuid
from pathlib import Path
from typing import Dict, Any
from urllib.parse import urlparse

from src.core.crawler import SmartCrawler, CrawlError
from src.core.processor import ArticleProcessor
from src.core.video_processor import VideoProcessor
from src.core.db_utils import resolve_category_ids, save_article_tags, json_dumps_field
from src.db.engine import SessionLocal
from src.db.models import Article, UploadTask

logger = logging.getLogger(__name__)

# Domains commonly used for video content
VIDEO_DOMAINS = {
    "youtube.com", "youtu.be", "bilibili.com", "b23.tv",
    "vimeo.com", "tiktok.com", "douyin.com", "ixigua.com",
    "kuaishou.com", "youtube-nocookie.com",
}


def _is_video_url(url: str) -> bool:
    """Heuristic: check if URL points to a known video platform."""
    domain = urlparse(url).netloc.lower()
    # Strip www. prefix for matching
    if domain.startswith("www."):
        domain = domain[4:]
    return any(vd in domain for vd in VIDEO_DOMAINS)


def _download_audio(url: str, output_dir: Path) -> str:
    """Download audio from video URL using yt-dlp. Returns path to audio file."""
    try:
        import yt_dlp
    except ImportError:
        raise RuntimeError("yt-dlp is not installed. Run: pip install yt-dlp")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": str(output_dir / "%(title)s.%(ext)s"),
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "quiet": True,
        "no_warnings": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        # Find the downloaded mp3 file
        base = ydl.prepare_filename(info)
        mp3_path = Path(base).with_suffix(".mp3")
        if mp3_path.exists():
            return str(mp3_path)
        # Fallback: original extension
        orig = Path(base)
        if orig.exists():
            return str(orig)
        raise FileNotFoundError(f"Download completed but file not found: {base}")


def process_article_url(url: str) -> Dict[str, Any]:
    """Crawl an article URL, process with AI, and save to DB."""
    loop = asyncio.new_event_loop()
    try:
        crawler = SmartCrawler()
        result = loop.run_until_complete(crawler.crawl(url))
        loop.run_until_complete(crawler.close())

        if not result.content:
            raise ValueError("No content extracted from URL")

        processor = ArticleProcessor()
        processed = processor.process(
            raw_content=result.content,
            source_url=url,
            title=result.title,
        )

        if processed.get("status") == "irrelevant":
            return {"status": "irrelevant", "url": url}

        db = SessionLocal()
        try:
            primary_id, secondary_id = resolve_category_ids(
                db,
                processed.get("primary_category"),
                processed.get("secondary_category"),
            )

            article = Article(
                title=processed.get("title", result.title) or "Untitled",
                url=url,
                status="completed",
                clean_content=processed.get("clean_content", ""),
                summary=processed.get("summary", ""),
                key_points=json_dumps_field(processed.get("key_points", [])),
                entities=json_dumps_field(processed.get("entities", [])),
                sentiment=processed.get("sentiment", "neutral"),
                importance=processed.get("importance", "medium"),
                primary_category_id=primary_id,
                secondary_category_id=secondary_id,
            )
            db.add(article)
            db.commit()
            db.refresh(article)

            save_article_tags(db, article.id, processed.get("tags", []))

            return {
                "status": "completed",
                "article_id": article.id,
                "title": article.title,
            }
        finally:
            db.close()
    except CrawlError as e:
        logger.error(f"Failed to crawl article URL {url}: {e}")
        raise
    finally:
        loop.close()


def process_video_url(url: str, original_filename: str = None) -> Dict[str, Any]:
    """Download video audio, transcribe with Whisper, process with AI, save to DB."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        audio_path = _download_audio(url, output_dir)

        vp = VideoProcessor()
        task = UploadTask(
            original_filename=original_filename or url,
            file_path=audio_path,
            file_type="mp3",
            status="processing",
        )
        db = SessionLocal()
        try:
            db.add(task)
            db.commit()
            db.refresh(task)
        finally:
            db.close()

        result = vp.process_video_upload(task.id, audio_path, original_filename or url)
        return result
