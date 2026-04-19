import json
from unittest.mock import MagicMock, patch
import pytest

from src.core.processor import ArticleProcessor


@pytest.fixture
def processor():
    with patch("src.core.ai_client.OpenAI"):
        p = ArticleProcessor()
        p.ai = MagicMock()
        return p


def test_clean_content(processor):
    processor.ai.run_prompt.return_value = "Clean article text"
    result = processor.clean("<html>raw</html>")
    assert result == "Clean article text"
    processor.ai.run_prompt.assert_called_once()


def test_summarize(processor):
    processor.ai.run_prompt_json.return_value = {
        "title": "Test Title",
        "summary": "Test summary",
        "key_points": ["point 1", "point 2"],
        "entities": ["Company A"],
        "sentiment": "positive",
        "importance": "high",
    }
    result = processor.summarize("some content")
    assert result["title"] == "Test Title"
    assert result["sentiment"] == "positive"


def test_classify(processor):
    processor.ai.run_prompt_json.return_value = {
        "primary_category": "宏观经济",
        "secondary_category": "货币政策",
        "confidence": 0.9,
        "reason": "关于降准",
    }
    result = processor.classify("Title", "Summary", ["point"], "宏观经济\n金融市场")
    assert result["primary_category"] == "宏观经济"
    assert result["secondary_category"] == "货币政策"


def test_extract_tags(processor):
    processor.ai.run_prompt_json.return_value = ["降准", "央行", "LPR"]
    result = processor.extract_tags("Title", "Summary", ["央行"])
    assert "降准" in result


def test_process_pipeline(processor):
    processor.ai.run_prompt.return_value = "Clean text"
    processor.ai.run_prompt_json.side_effect = [
        {  # summarize
            "title": "Test",
            "summary": "Summary",
            "key_points": ["p1"],
            "entities": ["E1"],
            "sentiment": "positive",
            "importance": "high",
        },
        {  # classify
            "primary_category": "宏观经济",
            "secondary_category": "货币政策",
            "confidence": 0.9,
            "reason": "test",
        },
        ["tag1", "tag2"],  # tags
    ]

    result = processor.process("<html>raw</html>", "http://example.com")

    assert result["status"] == "completed"
    assert result["clean_content"] == "Clean text"
    assert result["primary_category"] == "宏观经济"
    assert "tag1" in result["tags"]


def test_process_irrelevant(processor):
    processor.ai.run_prompt.return_value = "[IRRELEVANT]"
    result = processor.process("<html>raw</html>", "http://example.com")
    assert result["status"] == "irrelevant"
