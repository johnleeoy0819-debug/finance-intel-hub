"""Video/audio transcription via OpenAI Whisper API."""
import json
import logging
from typing import Any, Dict, List, Optional

from openai import OpenAI
from src.config import settings

logger = logging.getLogger(__name__)


class VideoProcessor:
    """Transcribe audio/video files using Whisper and convert to article text."""

    WHISPER_MODEL = "whisper-1"
    MAX_FILE_MB = 25

    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def transcribe(self, file_path: str) -> Dict[str, Any]:
        """Transcribe an audio/video file. Returns {text, segments, language}."""
        import os
        size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if size_mb > self.MAX_FILE_MB:
            raise ValueError(f"File too large: {size_mb:.1f}MB. Max: {self.MAX_FILE_MB}MB")

        logger.info(f"Transcribing {file_path} ({size_mb:.1f}MB)")
        with open(file_path, "rb") as audio:
            transcript = self.client.audio.transcriptions.create(
                model=self.WHISPER_MODEL,
                file=audio,
                language="zh",
                response_format="verbose_json",
            )

        segments = []
        if hasattr(transcript, "segments") and transcript.segments:
            segments = [
                {
                    "start": s.start,
                    "end": s.end,
                    "text": s.text,
                }
                for s in transcript.segments
            ]

        return {
            "text": transcript.text,
            "segments": segments,
            "language": getattr(transcript, "language", "zh"),
        }

    def process_video_upload(self, task_id: int, file_path: str, original_filename: str) -> Dict[str, Any]:
        """Full pipeline: transcribe → process as article. Returns article dict."""
        from src.core.processor import ArticleProcessor
        from src.db.engine import SessionLocal
        from src.db.models import UploadTask, VideoTranscript

        db = SessionLocal()
        try:
            task = db.query(UploadTask).filter(UploadTask.id == task_id).first()
            if task:
                task.status = "processing"
                db.commit()

            # 1. Transcribe
            transcript = self.transcribe(file_path)

            # 2. Save transcript record
            vt = VideoTranscript(
                video_path=file_path,
                transcript_text=transcript["text"],
                segments=transcript["segments"],
                language=transcript["language"],
            )
            db.add(vt)
            db.commit()
            db.refresh(vt)

            # 3. Process transcript through AI pipeline
            processor = ArticleProcessor()
            processed = processor.process(
                raw_content=transcript["text"],
                source_url=f"file://{original_filename}",
                title=original_filename,
            )

            if processed.get("status") == "irrelevant":
                if task:
                    task.status = "completed"
                    task.article_id = None
                    db.commit()
                return {"status": "irrelevant", "transcript_id": vt.id}

            # 4. Create Article
            article = Article(
                title=processed.get("title", original_filename) or original_filename,
                url=f"file://{original_filename}",
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

            # Link transcript to article
            vt.article_id = article.id
            db.commit()

            if task:
                task.status = "completed"
                task.article_id = article.id
                db.commit()

            return {
                "status": "completed",
                "article_id": article.id,
                "transcript_id": vt.id,
                "title": article.title,
            }
        except Exception as e:
            logger.error(f"Video processing failed for task {task_id}: {e}")
            if task:
                task.status = "failed"
                task.error_message = str(e)
                db.commit()
            raise
        finally:
            db.close()
