import asyncio
from typing import Any, Dict, List, Optional

from src.core.ai_client import AIClient
from src.db.engine import SessionLocal
from src.db.models import Article, Category, Correction
from src.config import settings


class ArticleProcessor:
    def __init__(self):
        self.ai = AIClient()

    def clean(self, raw_content: str) -> str:
        """Extract clean text from raw HTML/content."""
        return self.ai.run_prompt("cleaner", raw_content=raw_content, fewshot_field="clean_content")

    def summarize(self, clean_content: str) -> Dict[str, Any]:
        """Generate structured summary."""
        return self.ai.run_prompt_json("summarizer", clean_content=clean_content, fewshot_field="summary")

    def classify(self, title: str, summary: str, key_points: List[str], categories: str) -> Dict[str, Any]:
        """Classify article into primary + secondary category."""
        return self.ai.run_prompt_json(
            "classifier",
            title=title,
            summary=summary,
            key_points="\n".join(key_points) if isinstance(key_points, list) else key_points,
            categories=categories,
            fewshot_field="primary_category",
        )

    def extract_tags(self, title: str, summary: str, entities: List[str]) -> List[str]:
        """Extract keyword tags."""
        result = self.ai.run_prompt_json("tagger", title=title, summary=summary, entities=entities, fewshot_field="tags")
        if isinstance(result, list):
            return result
        return result.get("tags", [])

    def generate_mindmap(self, title: str, clean_content: str) -> str:
        """Generate mindmap structure."""
        return self.ai.run_prompt("mindmap", title=title, clean_content=clean_content)

    def analyze_relations(self, article_id: int, title: str, summary: str, category: str, tags: List[str]) -> List[Dict]:
        """Find relations with existing articles."""
        db = SessionLocal()
        try:
            # Get recent articles as candidates
            existing = db.query(Article).filter(
                Article.id != article_id,
                Article.status == "completed"
            ).order_by(Article.created_at.desc()).limit(20).all()

            if not existing:
                return []

            articles_text = "\n".join([
                f"- ID: {a.id}, 标题: {a.title}, 分类: {a.primary_category_id}, 标签: {a.entities or ''}"
                for a in existing
            ])

            result = self.ai.run_prompt_json(
                "relation",
                current_title=title,
                current_summary=summary,
                current_category=category,
                current_tags=", ".join(tags),
                existing_articles=articles_text,
            )
            return result.get("related_articles", [])
        finally:
            db.close()

    def process(self, raw_content: str, source_url: str, title: str = None, author: str = None) -> Dict[str, Any]:
        """Run full processing pipeline on an article."""
        # Step 1: Clean
        clean = self.clean(raw_content)
        if clean == "[IRRELEVANT]":
            return {"status": "irrelevant"}

        # Step 2: Summarize
        summary_result = self.summarize(clean)

        # Step 3: Get categories list from DB
        db = SessionLocal()
        try:
            cats = db.query(Category).all()
            categories_text = "\n".join([
                f"- {c.name}" + (f" ({c.parent.name})" if hasattr(c, 'parent') and c.parent else "")
                for c in cats
            ]) if cats else "宏观经济 / 金融市场 / 行业分析 / 商业模型 / 公司研究 / 监管政策"
        finally:
            db.close()

        # Step 4: Classify (parallel-ready but sync for simplicity)
        classification = self.classify(
            title=title or summary_result.get("title", ""),
            summary=summary_result.get("summary", ""),
            key_points=summary_result.get("key_points", []),
            categories=categories_text,
        )

        # Step 5: Tags
        tags = self.extract_tags(
            title=title or summary_result.get("title", ""),
            summary=summary_result.get("summary", ""),
            entities=summary_result.get("entities", []),
        )

        return {
            "status": "completed",
            "clean_content": clean,
            "title": summary_result.get("title", title or ""),
            "summary": summary_result.get("summary", ""),
            "key_points": summary_result.get("key_points", []),
            "entities": summary_result.get("entities", []),
            "sentiment": summary_result.get("sentiment", "neutral"),
            "importance": summary_result.get("importance", "medium"),
            "primary_category": classification.get("primary_category", ""),
            "secondary_category": classification.get("secondary_category", ""),
            "tags": tags,
        }
