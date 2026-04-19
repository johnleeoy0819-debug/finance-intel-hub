import pytest
from src.prompts.loader import PromptLoader


def test_loader_finds_version_directory():
    loader = PromptLoader()
    assert loader.prompts_dir.exists()
    assert (loader.prompts_dir / "cleaner.yaml").exists()


def test_load_cleaner_prompt():
    loader = PromptLoader()
    prompt = loader.load("cleaner")
    assert "version" in prompt
    assert "name" in prompt
    assert "system" in prompt
    assert "user" in prompt
    assert prompt["name"] == "content_cleaner"


def test_render_prompt_with_variables():
    loader = PromptLoader()
    prompt = loader.load("cleaner")
    rendered = loader.render(prompt, raw_content="<html>test</html>")
    assert "<html>test</html>" in rendered["user"]


def test_load_all_prompts():
    loader = PromptLoader()
    names = ["cleaner", "summarizer", "classifier", "tagger", "mindmap", "relation", "video", "publication"]
    for name in names:
        prompt = loader.load(name)
        assert prompt["name"] is not None
