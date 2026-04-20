"""Video/audio transcription via local Whisper (openai-whisper).

NOTE: This module uses local Whisper for zero-cost transcription.
      No ffmpeg required — audio loading is patched to use soundfile + scipy.
      To switch to OpenAI Whisper API (for commercial use):
      1. Set WHISPER_API_KEY in .env
      2. Restore the OpenAI-based transcribe() implementation
"""
import json
import logging
from typing import Any, Dict, List, Optional

import numpy as np
import soundfile as sf
from scipy import signal

# Patch whisper.audio.load_audio to bypass ffmpeg requirement
import whisper as _whisper
import whisper.audio as _whisper_audio

_orig_load_audio = _whisper_audio.load_audio


def _patched_load_audio(file: str, sr: int = 16000) -> np.ndarray:
    """Load audio using soundfile + scipy, no ffmpeg needed."""
    audio, orig_sr = sf.read(file, dtype="float32")
    if audio.ndim > 1:
        audio = audio.mean(axis=1)
    if orig_sr != sr:
        num_samples = int(len(audio) * sr / orig_sr)
        audio = signal.resample(audio, num_samples)
    return audio


_whisper_audio.load_audio = _patched_load_audio

from src.config import settings
from src.core.db_utils import json_dumps_field

logger = logging.getLogger(__name__)

# Load local Whisper model once at module level.
# Model sizes: tiny < base < small < medium < large
# For production accuracy, consider "small" or "medium".
# For commercial API mode, delete this and use OpenAI client instead.
_WHISPER_MODEL_NAME = getattr(settings, "LOCAL_WHISPER_MODEL", "base")
_whisper_model = None


def _get_whisper_model():
    """Lazy-load local Whisper model."""
    global _whisper_model
    if _whisper_model is None:
        logger.info(f"Loading local Whisper model: {_WHISPER_MODEL_NAME}")
        _whisper_model = _whisper.load_model(_WHISPER_MODEL_NAME)
    return _whisper_model


class VideoProcessor:
    """Transcribe audio/video files using local Whisper and convert to article text."""

    MAX_FILE_MB = 25

    def transcribe(self, file_path: str) -> Dict[str, Any]:
        """Transcribe an audio/video file locally. Returns {text, segments, language}."""
        import os

        size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if size_mb > self.MAX_FILE_MB:
            raise ValueError(f"File too large: {size_mb:.1f}MB. Max: {self.MAX_FILE_MB}MB")

        logger.info(f"Transcribing {file_path} ({size_mb:.1f}MB) with local Whisper")
        model = _get_whisper_model()
        result = model.transcribe(file_path, language="zh")

        segments = []
        for seg in result.get("segments", []):
            segments.append(
                {
                    "start": round(seg["start"], 2),
                    "end": round(seg["end"], 2),
                    "text": seg["text"].strip(),
                }
            )

        return {
            "text": result["text"].strip(),
            "segments": segments,
            "language": result.get("language", "zh"),
        }

    def process_video_upload(self, task_id: int, file_path: str, original_filename: str) -> Dict[str, Any]:
        """Full pipeline: transcribe → process as article. Returns article dict."""
        from src.core.processor import ArticleProcessor
        from src.db.engine import SessionLocal
        from src.db.models import Article, UploadTask, VideoTranscript

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
                segments=json_dumps_field(transcript["segments"]),
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

            # 4. Resolve categories
            from src.core.db_utils import resolve_category_ids, save_article_tags
            primary_id, secondary_id = resolve_category_ids(
                db,
                processed.get("primary_category"),
                processed.get("secondary_category"),
            )

            # 5. Create Article
            article = Article(
                title=processed.get("title", original_filename) or original_filename,
                url=f"file://{original_filename}",
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

            # 6. Save tags via association table
            save_article_tags(db, article.id, processed.get("tags", []))

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
