"""Tests for skill/chat hybrid strategy routing."""
from unittest.mock import patch, MagicMock
from src.db.models import Article, WikiPage, UserRule


def _mock_chat_response(content: str):
    """Build a mock OpenAI chat completion response."""
    mock = MagicMock()
    mock.choices = [MagicMock()]
    mock.choices[0].message.content = content
    return mock


@patch("src.api.skill.settings")
@patch("src.api.skill.AIClient")
def test_chat_strategy_wiki(mock_ai_cls, mock_settings, client, db):
    """Strategy 1: query matches a WikiPage → wiki strategy."""
    mock_settings.OPENAI_MODEL_FAST = "gpt-4o-mini"
    mock_ai = MagicMock()
    mock_ai_cls.return_value = mock_ai
    mock_ai.client.chat.completions.create.return_value = _mock_chat_response("Wiki answer")

    wiki = WikiPage(
        title="央行降息",
        slug="central-bank-rate-cut",
        topic="央行降息",
        content="央行降息是指...",
        article_count=5,
    )
    db.add(wiki)
    db.commit()

    response = client.post("/api/skill/chat", json={"query": "央行降息的影响"})
    assert response.status_code == 200
    data = response.json()
    assert data["strategy"] == "wiki"
    assert data["wiki_slug"] == "central-bank-rate-cut"
    assert data["answer"] == "Wiki answer"

    # Verify user rules not present → still works
    call_args = mock_ai.client.chat.completions.create.call_args
    assert call_args.kwargs["model"] == "gpt-4o-mini"


@patch("src.api.skill.settings")
@patch("src.api.skill.AIClient")
def test_chat_strategy_wiki_with_user_rules(mock_ai_cls, mock_settings, client, db):
    """User rules are injected into wiki strategy system prompt."""
    mock_settings.OPENAI_MODEL_FAST = "gpt-4o-mini"
    mock_ai = MagicMock()
    mock_ai_cls.return_value = mock_ai
    mock_ai.client.chat.completions.create.return_value = _mock_chat_response("Answer with rules")

    wiki = WikiPage(
        title="Test Wiki",
        slug="test-wiki",
        topic="test",
        content="Content",
        article_count=3,
    )
    db.add(wiki)
    db.add(UserRule(rules="## 规则\n- 必须使用中文回答"))
    db.commit()

    response = client.post("/api/skill/chat", json={"query": "test topic"})
    assert response.status_code == 200

    call_args = mock_ai.client.chat.completions.create.call_args
    messages = call_args.kwargs["messages"]
    assert any("必须使用中文回答" in m["content"] for m in messages if m["role"] == "system")


@patch("src.api.skill.settings")
@patch("src.api.skill.VectorStore")
@patch("src.api.skill.AIClient")
def test_chat_strategy_fulltext(mock_ai_cls, mock_vs_cls, mock_settings, client, db):
    """Strategy 2a: 1-50 matching articles → fulltext strategy."""
    mock_settings.OPENAI_MODEL_FAST = "gpt-4o-mini"
    mock_ai = MagicMock()
    mock_ai_cls.return_value = mock_ai
    mock_ai.client.chat.completions.create.return_value = _mock_chat_response("Fulltext answer")

    mock_vs = MagicMock()
    mock_vs_cls.return_value = mock_vs
    # Simulate 3 articles matched
    articles = []
    for i in range(3):
        a = Article(title=f"Article {i}", status="completed", summary=f"Summary {i}")
        db.add(a)
        articles.append(a)
    db.commit()
    mock_vs.search.return_value = [{"article_id": a.id} for a in articles]

    response = client.post("/api/skill/chat", json={"query": "新能源行业"})
    assert response.status_code == 200
    data = response.json()
    assert data["strategy"] == "fulltext"
    assert len(data["sources"]) == 3


@patch("src.api.skill.settings")
@patch("src.api.skill.VectorStore")
@patch("src.api.skill.AIClient")
def test_chat_strategy_rag(mock_ai_cls, mock_vs_cls, mock_settings, client, db):
    """Strategy 2b: >50 articles → rag strategy with top-5."""
    mock_settings.OPENAI_MODEL_FAST = "gpt-4o-mini"
    mock_ai = MagicMock()
    mock_ai_cls.return_value = mock_ai
    mock_ai.client.chat.completions.create.return_value = _mock_chat_response("RAG answer")

    mock_vs = MagicMock()
    mock_vs_cls.return_value = mock_vs
    # First search returns 60 articles (triggers RAG)
    # Second search returns 5 articles
    articles = []
    for i in range(55):
        a = Article(title=f"Article {i}", status="completed", summary=f"Summary {i}")
        db.add(a)
        articles.append(a)
    db.commit()
    mock_vs.search.side_effect = [
        [{"article_id": a.id} for a in articles[:60]],
        [{"article_id": a.id} for a in articles[:5]],
    ]

    response = client.post("/api/skill/chat", json={"query": "宏观经济"})
    assert response.status_code == 200
    data = response.json()
    assert data["strategy"] == "rag"
    assert len(data["sources"]) == 5


@patch("src.api.skill.settings")
@patch("src.api.skill.VectorStore")
@patch("src.api.skill.AIClient")
def test_chat_strategy_rag_no_hits(mock_ai_cls, mock_vs_cls, mock_settings, client, db):
    """Strategy 2b: no vector hits → rag with empty context."""
    mock_settings.OPENAI_MODEL_FAST = "gpt-4o-mini"
    mock_ai = MagicMock()
    mock_ai_cls.return_value = mock_ai
    mock_ai.client.chat.completions.create.return_value = _mock_chat_response("No context answer")

    mock_vs = MagicMock()
    mock_vs_cls.return_value = mock_vs
    mock_vs.search.return_value = []

    response = client.post("/api/skill/chat", json={"query": "完全无关的查询"})
    assert response.status_code == 200
    data = response.json()
    assert data["strategy"] == "rag"
    assert data["sources"] == []
