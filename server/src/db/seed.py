"""Seed default categories and initial data."""
import logging

from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


DEFAULT_CATEGORIES = [
    # 宏观经济
    {"name": "宏观经济", "slug": "macro-economy", "sort_order": 1, "children": [
        {"name": "货币政策", "slug": "monetary-policy", "sort_order": 1},
        {"name": "财政政策", "slug": "fiscal-policy", "sort_order": 2},
        {"name": "国际贸易", "slug": "international-trade", "sort_order": 3},
        {"name": "GDP/就业/通胀", "slug": "gdp-employment-inflation", "sort_order": 4},
        {"name": "全球经济", "slug": "global-economy", "sort_order": 5},
    ]},
    # 金融市场
    {"name": "金融市场", "slug": "financial-markets", "sort_order": 2, "children": [
        {"name": "股票市场", "slug": "stock-market", "sort_order": 1},
        {"name": "债券市场", "slug": "bond-market", "sort_order": 2},
        {"name": "外汇市场", "slug": "forex", "sort_order": 3},
        {"name": "大宗商品", "slug": "commodities", "sort_order": 4},
        {"name": "加密货币", "slug": "crypto", "sort_order": 5},
        {"name": "市场策略", "slug": "market-strategy", "sort_order": 6},
    ]},
    # 行业分析
    {"name": "行业分析", "slug": "industry-analysis", "sort_order": 3, "children": [
        {"name": "科技互联网", "slug": "tech-internet", "sort_order": 1},
        {"name": "房地产", "slug": "real-estate", "sort_order": 2},
        {"name": "制造业", "slug": "manufacturing", "sort_order": 3},
        {"name": "医疗健康", "slug": "healthcare", "sort_order": 4},
        {"name": "新能源", "slug": "new-energy", "sort_order": 5},
        {"name": "消费零售", "slug": "consumer-retail", "sort_order": 6},
    ]},
    # 商业模型
    {"name": "商业模型", "slug": "business-model", "sort_order": 4, "children": [
        {"name": "商业模式创新", "slug": "business-innovation", "sort_order": 1},
        {"name": "企业战略", "slug": "corporate-strategy", "sort_order": 2},
        {"name": "投资并购", "slug": "m-a", "sort_order": 3},
        {"name": "创业融资", "slug": "startup-funding", "sort_order": 4},
        {"name": "公司治理", "slug": "corporate-governance", "sort_order": 5},
    ]},
    # 公司研究
    {"name": "公司研究", "slug": "company-research", "sort_order": 5, "children": [
        {"name": "财报解读", "slug": "earnings-analysis", "sort_order": 1},
        {"name": "竞争分析", "slug": "competitive-analysis", "sort_order": 2},
        {"name": "管理层动态", "slug": "management-dynamics", "sort_order": 3},
        {"name": "估值分析", "slug": "valuation-analysis", "sort_order": 4},
    ]},
    # 监管政策
    {"name": "监管政策", "slug": "regulatory-policy", "sort_order": 6, "children": [
        {"name": "金融监管", "slug": "financial-regulation", "sort_order": 1},
        {"name": "行业监管", "slug": "industry-regulation", "sort_order": 2},
        {"name": "反垄断", "slug": "antitrust", "sort_order": 3},
        {"name": "数据合规", "slug": "data-compliance", "sort_order": 4},
    ]},
    # 学术文献
    {"name": "学术文献", "slug": "academic-literature", "sort_order": 7, "children": [
        {"name": "经典著作", "slug": "classic-works", "sort_order": 1},
        {"name": "工作论文", "slug": "working-papers", "sort_order": 2},
        {"name": "期刊论文", "slug": "journal-articles", "sort_order": 3},
        {"name": "行业报告", "slug": "industry-reports", "sort_order": 4},
    ]},
]


def seed_categories(db: Session) -> None:
    """Insert default categories if none exist."""
    from src.db.models import Category

    existing = db.query(Category).first()
    if existing:
        logger.info("Categories already seeded, skipping.")
        return

    for parent_data in DEFAULT_CATEGORIES:
        parent = Category(
            name=parent_data["name"],
            slug=parent_data["slug"],
            sort_order=parent_data["sort_order"],
        )
        db.add(parent)
        db.commit()
        db.refresh(parent)

        for child_data in parent_data.get("children", []):
            child = Category(
                name=child_data["name"],
                slug=child_data["slug"],
                sort_order=child_data["sort_order"],
                parent_id=parent.id,
            )
            db.add(child)
        db.commit()

    logger.info(f"Seeded {len(DEFAULT_CATEGORIES)} top-level categories.")


def run_seed() -> None:
    """Manual entrypoint for seeding."""
    from src.db.engine import SessionLocal
    db = SessionLocal()
    try:
        seed_categories(db)
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
