"""Lint engine: self-maintenance audits for the knowledge base."""
import json
import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta

from src.core.ai_client import AIClient
from src.core.db_utils import json_loads_field
from src.db.engine import SessionLocal
from src.db.models import Article, Tag, ArticleTag, KnowledgeEdge, LintReport

logger = logging.getLogger(__name__)


def lint_orphans() -> List[Dict[str, Any]]:
    """Find articles with no tags, no category, no knowledge edges."""
    db = SessionLocal()
    try:
        # Articles with no primary category
        orphan_articles = db.query(Article).filter(
            Article.primary_category_id.is_(None),
            Article.status == "completed"
        ).all()

        # Articles with no tags
        from sqlalchemy import func
        untagged = db.query(Article).outerjoin(ArticleTag).group_by(Article.id).having(
            func.count(ArticleTag.tag_id) == 0
        ).filter(Article.status == "completed").all()

        reports = []
        for a in set(orphan_articles + untagged):
            reports.append({
                "article_id": a.id,
                "title": a.title,
                "issue": "无分类或标签",
                "suggestion": "手动分配分类和标签，或触发重新处理",
            })
        return reports
    finally:
        db.close()


def lint_duplicates() -> List[Dict[str, Any]]:
    """Find articles with highly similar titles."""
    db = SessionLocal()
    try:
        articles = db.query(Article).filter(Article.status == "completed").all()
        duplicates = []
        seen = set()
        for i, a1 in enumerate(articles):
            if a1.id in seen:
                continue
            for a2 in articles[i + 1:]:
                if a2.id in seen:
                    continue
                # Simple title similarity: common substring ratio
                title1 = a1.title.lower()
                title2 = a2.title.lower()
                if len(title1) < 5 or len(title2) < 5:
                    continue
                # Check if titles share >70% words
                words1 = set(title1.split())
                words2 = set(title2.split())
                if not words1 or not words2:
                    continue
                intersection = words1 & words2
                union = words1 | words2
                similarity = len(intersection) / len(union) if union else 0
                if similarity > 0.6:
                    duplicates.append({
                        "article_id_1": a1.id,
                        "title_1": a1.title,
                        "article_id_2": a2.id,
                        "title_2": a2.title,
                        "similarity": round(similarity, 2),
                    })
                    seen.add(a1.id)
                    seen.add(a2.id)
        return duplicates
    finally:
        db.close()


def lint_contradictions() -> List[Dict[str, Any]]:
    """Use LLM to find contradictions between articles."""
    db = SessionLocal()
    try:
        # Get recent articles with summaries
        articles = db.query(Article).filter(
            Article.status == "completed",
            Article.summary.isnot(None)
        ).order_by(Article.created_at.desc()).limit(30).all()

        if len(articles) < 2:
            return []

        # Build context for LLM
        context = ""
        for a in articles:
            context += f"【{a.title}】{a.summary[:200]}\n"

        ai = AIClient()
        system = """你是一位知识审计员。你的任务是检查以下文章中是否存在观点矛盾、数据冲突或结论相反的情况。

输出格式（严格JSON）：
{
  "contradictions": [
    {
      "article_1": "文章1标题",
      "article_2": "文章2标题",
      "conflict": "矛盾的具体描述",
      "severity": "high|medium|low"
    }
  ]
}

如果没有发现矛盾，返回 {"contradictions": []}。"""

        response = ai.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": context},
            ],
            temperature=0.2,
            max_tokens=2000,
        )
        content = response.choices[0].message.content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        result = json.loads(content)
        return result.get("contradictions", [])
    except Exception as e:
        logger.error(f"Contradiction lint failed: {e}")
        return []
    finally:
        db.close()


def lint_outdated() -> List[Dict[str, Any]]:
    """Find potentially outdated articles (time-sensitive predictions/forecasts)."""
    db = SessionLocal()
    try:
        # Articles older than 90 days that mention future predictions
        cutoff = datetime.utcnow() - timedelta(days=90)
        old_articles = db.query(Article).filter(
            Article.created_at < cutoff,
            Article.status == "completed"
        ).all()

        # Use keyword heuristic for predictions
        prediction_keywords = ["预计", "预测", "预期", "将", "有望", "可能", "或", "料将", "料", "forecast", "predict", "expect"]
        outdated = []
        for a in old_articles:
            text = f"{a.title} {a.summary or ''} {a.clean_content or ''}"
            if any(kw in text for kw in prediction_keywords):
                outdated.append({
                    "article_id": a.id,
                    "title": a.title,
                    "created_at": a.created_at.isoformat() if a.created_at else None,
                    "issue": "文章包含时间敏感型预测，可能已过时",
                    "suggestion": "检查预测是否应验，更新或归档",
                })
        return outdated
    finally:
        db.close()


def run_all_lints() -> Dict[str, Any]:
    """Run all lint checks and save reports to database."""
    logger.info("Starting lint audit...")
    db = SessionLocal()
    try:
        # Clear old open reports
        db.query(LintReport).filter(LintReport.status == "open").delete()
        db.commit()

        all_reports = []

        # 1. Orphans
        orphans = lint_orphans()
        for o in orphans:
            all_reports.append(LintReport(
                lint_type="orphan",
                severity="warning",
                details=json.dumps(o, ensure_ascii=False),
                status="open",
            ))

        # 2. Duplicates
        duplicates = lint_duplicates()
        for d in duplicates:
            all_reports.append(LintReport(
                lint_type="duplicate",
                severity="warning",
                details=json.dumps(d, ensure_ascii=False),
                status="open",
            ))

        # 3. Contradictions
        contradictions = lint_contradictions()
        for c in contradictions:
            severity = c.get("severity", "medium")
            all_reports.append(LintReport(
                lint_type="contradiction",
                severity=severity,
                details=json.dumps(c, ensure_ascii=False),
                status="open",
            ))

        # 4. Outdated
        outdated = lint_outdated()
        for o in outdated:
            all_reports.append(LintReport(
                lint_type="outdated",
                severity="warning",
                details=json.dumps(o, ensure_ascii=False),
                status="open",
            ))

        db.add_all(all_reports)
        db.commit()

        summary = {
            "total": len(all_reports),
            "orphan": len(orphans),
            "duplicate": len(duplicates),
            "contradiction": len(contradictions),
            "outdated": len(outdated),
        }
        logger.info(f"Lint audit complete: {summary}")
        return summary
    finally:
        db.close()
