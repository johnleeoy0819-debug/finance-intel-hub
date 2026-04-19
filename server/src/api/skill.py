"""Skill API — AI assistant, feedback, memory, and chat."""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional

from src.db.engine import get_db
from src.db.models import SkillFeedback, Correction, Article, WikiPage, UserRule
from src.core.feedback import build_fewshot_samples
from src.api.schemas import FeedbackCreate
from src.core.vector_store import VectorStore
from src.core.ai_client import AIClient

router = APIRouter()


class ChatRequest(BaseModel):
    query: str


@router.post("/feedback")
def submit_feedback(feedback: FeedbackCreate, db: Session = Depends(get_db)):
    fb = SkillFeedback(
        skill_name=feedback.skill_name or "econ-master",
        query=feedback.query,
        response_summary=feedback.response_summary,
        rating=feedback.rating,
        comment=feedback.comment,
    )
    db.add(fb)
    db.commit()
    db.refresh(fb)
    return fb


@router.get("/memory")
def get_memory():
    """Return user profile / memory (P1)."""
    return {
        "focus_areas": [],
        "recent_topics": [],
        "answer_preferences": {},
    }


@router.put("/memory")
def update_memory(data: dict):
    """Update user memory (P1)."""
    return {"ok": True}


@router.get("/examples")
def get_examples(field: Optional[str] = None, db: Session = Depends(get_db)):
    """Get Few-shot examples from corrections."""
    samples = build_fewshot_samples(field=field, limit=10)
    return {"samples": samples}


@router.post("/chat")
def chat(req: ChatRequest, db: Session = Depends(get_db)):
    """Chat with AI assistant using hybrid retrieval strategy."""
    ai = AIClient()
    query = req.query

    # ── Strategy 1: Wiki Page (highest quality, least tokens) ──
    wiki_page = db.query(WikiPage).filter(
        WikiPage.topic.ilike(f"%{query[:20]}%")
    ).order_by(WikiPage.article_count.desc()).first()

    if not wiki_page:
        # Try broader match on title/content
        wiki_page = db.query(WikiPage).filter(
            WikiPage.title.ilike(f"%{query[:20]}%")
        ).order_by(WikiPage.article_count.desc()).first()

    if wiki_page:
        system_prompt = f"""你是"经济大师"，一位专业的财经知识库助手。

规则：
1. 基于以下 Wiki 综述回答用户问题
2. 回答要结构化、有逻辑，必要时分点说明
3. 保持专业但易懂的风格

【Wiki 综述】
{wiki_page.content}
"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ]
        response = ai.client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.5,
        )
        return {
            "query": query,
            "answer": response.choices[0].message.content,
            "strategy": "wiki",
            "wiki_slug": wiki_page.slug,
            "sources": [],
        }

    # ── Strategy 2: Count related articles ──
    vs = VectorStore()
    hits = vs.search(query, limit=60)  # Check up to 60 to decide strategy
    article_ids = [h["article_id"] for h in hits]

    # ── Strategy 2a: Full-text loading (Karpathy style, <50 articles) ──
    if len(article_ids) <= 50 and article_ids:
        articles = db.query(Article).filter(Article.id.in_(article_ids)).all()
        context_parts = []
        for a in articles:
            ctx = f"【{a.title}】\n{a.summary or '无摘要'}\n{a.clean_content or ''}"[:1500]
            context_parts.append(ctx)
        context = "\n\n---\n\n".join(context_parts)

        system_prompt = f"""你是"经济大师"，一位专业的财经知识库助手。

规则：
1. 基于以下知识库文章回答用户问题
2. 回答要结构化、有逻辑，必要时分点说明
3. 如果引用了知识库文章，在回答末尾列出引用来源（文章标题）
4. 保持专业但易懂的风格

【知识库文章】（共 {len(articles)} 篇）
{context}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ]
        response = ai.client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.5,
        )
        return {
            "query": query,
            "answer": response.choices[0].message.content,
            "strategy": "fulltext",
            "sources": [{"id": a.id, "title": a.title} for a in articles],
        }

    # ── Strategy 2b: RAG (≥50 articles or no hits) ──
    hits = vs.search(query, limit=5)
    article_ids = [h["article_id"] for h in hits]
    articles = db.query(Article).filter(Article.id.in_(article_ids)).all() if article_ids else []

    context_parts = []
    for a in articles:
        ctx = f"【文章】{a.title}\n【摘要】{a.summary or '无摘要'}\n"
        context_parts.append(ctx)
    context = "\n".join(context_parts) if context_parts else "知识库中暂无相关内容。"

    # Inject few-shot samples
    fewshot_samples = build_fewshot_samples(limit=3)
    fewshot_text = ""
    if fewshot_samples:
        fewshot_text = "\n\n以下是你之前修正过的案例，请优先遵循这些风格：\n"
        for s in fewshot_samples:
            fewshot_text += f"- 输入：{s['input'][:100]}...\n  正确输出：{s['output'][:100]}...\n"

    system_prompt = f"""你是"经济大师"，一位专业的财经知识库助手。你会基于知识库中的文章回答用户问题。

规则：
1. 优先使用知识库中的信息回答，如果没有直接相关内容，可以基于通用财经知识回答，但要说明。
2. 回答要结构化、有逻辑，必要时分点说明。
3. 如果引用了知识库文章，在回答末尾列出引用来源（文章标题）。
4. 保持专业但易懂的风格。
{fewshot_text}

知识库相关内容：
{context}"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": query},
    ]

    response = ai.client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.5,
    )
    answer = response.choices[0].message.content

    return {
        "query": query,
        "answer": answer,
        "strategy": "rag",
        "sources": [{"id": a.id, "title": a.title} for a in articles],
    }
