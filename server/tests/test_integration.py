"""End-to-end integration tests across modules."""
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import sessionmaker

from src.db.models import Article, KnowledgeEdge, WikiPage, LintReport, UserRule


def _mock_ai_response(content: str):
    mock = MagicMock()
    mock.choices = [MagicMock()]
    mock.choices[0].message.content = content
    return mock


def test_article_graph_backlinks_flow(client, db, api_engine):
    """Scenario 1: Article → KnowledgeEdge → Backlinks → Graph."""
    # Create articles and edge directly in test DB
    a1 = Article(title="Source Article", status="completed", summary="Summary A")
    a2 = Article(title="Target Article", status="completed", summary="Summary B")
    db.add_all([a1, a2])
    db.commit()

    edge = KnowledgeEdge(
        source_article_id=a1.id,
        target_article_id=a2.id,
        relation_type="references",
        reason="cited in summary",
    )
    db.add(edge)
    db.commit()

    # Update backlinks via API
    response = client.post("/api/articles/backlinks/update")
    assert response.status_code == 200
    assert response.json()["updated"] == 1

    # Verify backlinks in article response
    response = client.get(f"/api/articles/{a2.id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data["backlinks"]) == 1
    assert data["backlinks"][0]["title"] == "Source Article"

    # Verify related articles
    response = client.get(f"/api/articles/{a1.id}/related")
    assert response.status_code == 200
    related = response.json()
    assert len(related) == 1
    assert related[0]["title"] == "Target Article"

    # Verify knowledge graph
    response = client.get(f"/api/graph/articles/{a1.id}")
    assert response.status_code == 200
    graph = response.json()
    node_ids = {n["id"] for n in graph["nodes"]}
    assert a1.id in node_ids
    assert a2.id in node_ids
    assert any(l["source"] == a1.id and l["target"] == a2.id for l in graph["links"])


def test_settings_chat_rules_flow(client, db):
    """Scenario 2: User Rules → Chat system prompt injection."""
    # Set user rules
    response = client.put("/api/settings/rules", json={"rules": "## 规则\n- 必须使用中文回答"})
    assert response.status_code == 200

    # Create a wiki page so chat uses wiki strategy (easiest to inspect system prompt)
    wiki = WikiPage(
        title="货币政策",
        slug="monetary-policy",
        topic="货币政策",
        content="货币政策是...",
        article_count=3,
    )
    db.add(wiki)
    db.commit()

    with patch("src.api.skill.AIClient") as MockAI:
        MockAI.return_value.client.chat.completions.create.return_value = _mock_ai_response("Answer")
        response = client.post("/api/skill/chat", json={"query": "货币政策是什么"})
        assert response.status_code == 200
        data = response.json()
        assert data["strategy"] == "wiki"

        # Verify user rules were injected into system prompt
        call_args = MockAI.return_value.client.chat.completions.create.call_args
        messages = call_args.kwargs["messages"]
        system_msg = next(m["content"] for m in messages if m["role"] == "system")
        assert "必须使用中文回答" in system_msg


def test_lint_audit_flow(client, db, api_engine):
    """Scenario 3: Create problematic articles → run lint → verify reports."""
    # Orphan article (no category, no tags)
    orphan = Article(title="Orphan Article", status="completed", summary="No category")
    db.add(orphan)

    # Duplicate-like articles
    dup1 = Article(title="Market Outlook 2024", status="completed", summary="Outlook")
    dup2 = Article(title="Market Outlook 2024 Update", status="completed", summary="Updated outlook")
    db.add_all([dup1, dup2])

    # Outdated article (>90 days with prediction keyword)
    old = Article(
        title="Old Prediction",
        status="completed",
        summary="预计明年经济增长5%",
        created_at=datetime.utcnow() - timedelta(days=100),
    )
    db.add(old)
    db.commit()

    # Run lint with patched SessionLocal and AIClient
    TestSession = sessionmaker(bind=api_engine)
    with patch("src.core.lint_engine.SessionLocal", TestSession):
        with patch("src.core.lint_engine.AIClient") as MockAI:
            MockAI.return_value.client.chat.completions.create.return_value = _mock_ai_response(
                '{"contradictions": []}'
            )
            from src.core.lint_engine import run_all_lints
            summary = run_all_lints()

    assert summary["orphan"] >= 1
    assert summary["duplicate"] >= 1
    assert summary["outdated"] >= 1

    # Verify reports via API
    response = client.get("/api/lint/reports")
    assert response.status_code == 200
    reports = response.json()
    types = {r["lint_type"] for r in reports}
    assert "orphan" in types
    assert "duplicate" in types
    assert "outdated" in types


def test_wiki_compile_chat_flow(client, db, api_engine):
    """Scenario 4: Articles → Wiki Compile → Chat uses Wiki strategy."""
    # Create articles on same topic
    articles = []
    for i in range(3):
        a = Article(
            title=f"新能源行业分析 {i+1}",
            status="completed",
            summary=f"Summary {i+1}",
            clean_content=f"Content {i+1}",
        )
        db.add(a)
        articles.append(a)
    db.commit()

    # Compile wiki with patched SessionLocal and AIClient
    TestSession = sessionmaker(bind=api_engine)
    with patch("src.core.wiki_compiler.SessionLocal", TestSession):
        with patch("src.core.wiki_compiler.AIClient") as MockAI:
            MockAI.return_value.client.chat.completions.create.return_value = _mock_ai_response(
                "# 新能源行业综合报告\n\n## 概述\n新能源行业正在快速发展。"
            )
            from src.core.wiki_compiler import compile_topic
            result = compile_topic("新能源行业", [a.id for a in articles])

    assert result["status"] == "completed"
    assert result["article_count"] == 3

    # Verify wiki page exists via API
    response = client.get(f"/api/wiki/{result['slug']}")
    assert response.status_code == 200
    wiki_data = response.json()
    assert wiki_data["title"] == "新能源行业综合报告"
    assert wiki_data["topic"] == "新能源行业"

    # Chat on the same topic should use wiki strategy
    with patch("src.api.skill.AIClient") as MockAI:
        MockAI.return_value.client.chat.completions.create.return_value = _mock_ai_response("Wiki-based answer")
        response = client.post("/api/skill/chat", json={"query": "新能源行业怎么样"})
        assert response.status_code == 200
        data = response.json()
        assert data["strategy"] == "wiki"
        assert data["wiki_slug"] == result["slug"]


def test_cascade_wiki_updates(client, db, api_engine):
    """Scenario 5: New article triggers cascading wiki recompile."""
    # Create a wiki page on "新能源"
    db.add(WikiPage(
        title="新能源综合报告",
        slug="xin-neng-yuan-xing-ye",
        topic="新能源行业",
        content="新能源行业内容",
        article_count=2,
    ))
    db.commit()

    # Verify wiki exists
    response = client.get("/api/wiki/xin-neng-yuan-xing-ye")
    assert response.status_code == 200

    # Create a new article matching the wiki topic
    article = Article(
        title="新能源行业技术突破",
        status="completed",
        summary="新能源行业取得重大突破",
        clean_content="新能源行业内容",
        primary_category_id=None,
    )
    db.add(article)
    db.commit()

    # Trigger cascade update
    TestSession = sessionmaker(bind=api_engine)
    from src.core.wiki_compiler import _cascade_wiki_updates
    with patch("src.core.wiki_compiler.SessionLocal", TestSession):
        with patch("src.core.wiki_compiler.compile_topic_async") as mock_compile:
            _cascade_wiki_updates(article.id)
            mock_compile.assert_called_once()


def test_wiki_index_compilation(client, db, api_engine):
    """Scenario 6: Compile global wiki index."""
    # Create wiki pages
    db.add(WikiPage(title="Page A", slug="page-a", topic="a", content="Content A", article_count=2))
    db.add(WikiPage(title="Page B", slug="page-b", topic="b", content="Content B", article_count=3))
    db.commit()

    TestSession = sessionmaker(bind=api_engine)
    with patch("src.core.wiki_compiler.SessionLocal", TestSession):
        from src.core.wiki_compiler import compile_index
        result = compile_index()

    assert result["status"] == "completed"
    assert result["pages_count"] == 2

    # Verify index page exists
    response = client.get("/api/wiki/index")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Wiki 索引"
    assert "Page A" in data["content"]
    assert "Page B" in data["content"]


def test_missing_concepts_lint(client, db, api_engine):
    """Scenario 7: Wiki references a concept with no dedicated page."""
    db.add(WikiPage(
        title="Main Page",
        slug="main-page",
        topic="main",
        content="This page discusses [[quantum-computing|量子计算]] and **人工智能**.",
        article_count=1,
    ))
    db.commit()

    TestSession = sessionmaker(bind=api_engine)
    with patch("src.core.lint_engine.SessionLocal", TestSession):
        from src.core.lint_engine import lint_missing_concepts
        missing = lint_missing_concepts()

    assert len(missing) >= 2
    concepts = {m["concept"] for m in missing}
    assert "量子计算" in concepts or "quantum-computing" in concepts
    assert "人工智能" in concepts
