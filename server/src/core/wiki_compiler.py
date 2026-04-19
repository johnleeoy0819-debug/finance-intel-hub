"""Wiki compiler: compile multiple articles into a structured wiki page."""
import json
import logging
import re
import threading
from typing import List, Dict, Any, Optional

from src.core.ai_client import AIClient
from src.core.db_utils import json_dumps_field
from src.db.engine import SessionLocal
from src.db.models import Article, WikiPage

logger = logging.getLogger(__name__)


def _slugify(text: str) -> str:
    """Convert text to URL-friendly slug."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text[:100]


def _build_compile_prompt(articles: List[Article], topic: str) -> str:
    """Build system prompt for wiki compilation."""
    system = f"""你是一位专业的知识编辑，负责将多篇相关文章编译成一篇结构化的 Wiki 综述页面。

你的任务：
1. 阅读所有提供的文章
2. 提取核心观点、关键数据、时间线
3. 识别观点之间的矛盾和共识
4. 生成一篇结构清晰、内容全面的 Wiki 页面

输出格式（严格遵循）：

# {topic} 综合报告

## 概述
（100-200 字的核心摘要）

## 关键要点
- 要点 1
- 要点 2
- ...

## 详细分析
### 子主题 A
（综合分析）

### 子主题 B
（综合分析）

## 观点对比
| 观点 | 支持方 | 反对/质疑 |
|---|---|---|
| ... | ... | ... |

## 时间线
- YYYY-MM-DD: 事件描述
- ...

## 引用来源
1. [文章标题 1]
2. [文章标题 2]
3. ...

规则：
- 使用中文撰写
- 必须标注信息来源（文章标题）
- 发现矛盾观点时必须列出双方论据
- 不要编造数据，只使用文章中的信息
- 字数控制在 2000-5000 字"""

    # Build articles context
    context_parts = []
    for i, a in enumerate(articles, 1):
        ctx = f"""【文章 {i}】{a.title}
分类: {a.primary_category_id or '未分类'}
摘要: {a.summary or '无摘要'}
内容: {(a.clean_content or '')[:2000]}
情感: {a.sentiment or '中性'} | 重要度: {a.importance or '中'}
---"""
        context_parts.append(ctx)

    user = f"请将以下 {len(articles)} 篇关于「{topic}」的文章编译成一篇 Wiki 综述页面：\n\n"
    user += "\n".join(context_parts)

    return system, user


def compile_topic(topic: str, article_ids: Optional[List[int]] = None) -> Dict[str, Any]:
    """Compile articles on a topic into a wiki page. Returns wiki page dict."""
    db = SessionLocal()
    try:
        # Fetch articles
        if article_ids:
            articles = db.query(Article).filter(Article.id.in_(article_ids)).all()
        else:
            # Auto-discover: search for articles matching topic via vector + title
            from src.core.vector_store import VectorStore
            vs = VectorStore()
            hits = vs.search(topic, limit=20)
            ids = [h["article_id"] for h in hits]
            articles = db.query(Article).filter(Article.id.in_(ids)).all() if ids else []

        if not articles:
            return {"status": "error", "message": "No articles found for topic"}

        # Limit to 20 articles to control token usage
        articles = articles[:20]

        # Call AI to compile
        ai = AIClient()
        system_prompt, user_prompt = _build_compile_prompt(articles, topic)

        response = ai.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=8000,
        )
        content = response.choices[0].message.content

        # Extract title from first heading
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else f"{topic} 综合报告"

        slug = _slugify(topic)

        # Check for existing wiki page
        existing = db.query(WikiPage).filter(WikiPage.slug == slug).first()
        if existing:
            existing.title = title
            existing.content = content
            existing.source_article_ids = json_dumps_field([a.id for a in articles])
            existing.article_count = len(articles)
            existing.compiled_at = db.func.now()
            db.commit()
            db.refresh(existing)
            page = existing
        else:
            page = WikiPage(
                title=title,
                slug=slug,
                topic=topic,
                content=content,
                source_article_ids=json_dumps_field([a.id for a in articles]),
                article_count=len(articles),
            )
            db.add(page)
            db.commit()
            db.refresh(page)

        logger.info(f"Compiled wiki page '{title}' from {len(articles)} articles")
        return {
            "status": "completed",
            "wiki_page_id": page.id,
            "title": page.title,
            "slug": page.slug,
            "article_count": len(articles),
        }
    except Exception as e:
        logger.error(f"Wiki compilation failed for topic '{topic}': {e}")
        return {"status": "error", "message": str(e)}
    finally:
        db.close()


def compile_topic_async(topic: str, article_ids: Optional[List[int]] = None) -> None:
    """Run compilation in background thread."""
    thread = threading.Thread(
        target=compile_topic,
        args=(topic, article_ids),
        daemon=True,
    )
    thread.start()


def auto_compile_top_topics(days: int = 7, limit: int = 5) -> List[str]:
    """Find top topics by recent article count and compile them."""
    from datetime import datetime, timedelta
    from sqlalchemy import func

    db = SessionLocal()
    try:
        since = datetime.utcnow() - timedelta(days=days)
        # Group by primary category and count
        results = db.query(
            Article.primary_category_id,
            func.count(Article.id).label("count")
        ).filter(
            Article.created_at >= since,
            Article.status == "completed"
        ).group_by(Article.primary_category_id).order_by(func.count(Article.id).desc()).limit(limit).all()

        compiled_topics = []
        for cat_id, count in results:
            if not cat_id:
                continue
            cat = db.query(Article).filter(Article.id == cat_id).first()
            # Get category name
            from src.db.models import Category
            category = db.query(Category).filter(Category.id == cat_id).first()
            if category:
                topic = category.name
                # Find articles in this category
                articles = db.query(Article).filter(
                    (Article.primary_category_id == cat_id) | (Article.secondary_category_id == cat_id),
                    Article.status == "completed",
                ).order_by(Article.created_at.desc()).limit(20).all()
                if articles:
                    article_ids = [a.id for a in articles]
                    compile_topic_async(topic, article_ids)
                    compiled_topics.append(topic)

        return compiled_topics
    finally:
        db.close()
