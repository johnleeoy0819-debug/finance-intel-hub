#!/usr/bin/env python3
"""Generate user manual PDF with real page screenshots."""
import os
import sys
import json
import tempfile
from datetime import datetime, timedelta

# --- Step 1: Seed data via backend API ---
import requests

BASE_URL = "http://localhost:8001"
FRONTEND_URL = "http://localhost:5173"

def seed_data():
    """Create sample data for screenshots."""
    # Create categories
    cats = []
    for name, slug in [("宏观经济", "macro"), ("行业分析", "industry"), ("公司研究", "company")]:
        r = requests.post(f"{BASE_URL}/api/categories", json={"name": name, "slug": slug, "sort_order": 1})
        if r.status_code in (200, 201):
            cats.append(r.json())
        else:
            # Try to get existing
            r2 = requests.get(f"{BASE_URL}/api/categories")
            if r2.status_code == 200:
                for c in r2.json():
                    if c["slug"] == slug:
                        cats.append(c)
                        break

    cat_map = {c["slug"]: c["id"] for c in cats}

    # Create articles directly via API
    articles = []
    article_data = [
        {
            "title": "2024年央行货币政策全面解读",
            "summary": "本文深入分析2024年中国人民银行货币政策走向，包括降准降息预期、LPR调整影响及市场流动性判断。",
            "clean_content": "2024年，中国央行继续实施稳健的货币政策...",
            "key_points": json.dumps(["降准预期在二季度", "LPR下调空间约10-15bp", "结构性工具发力方向明确"]),
            "entities": json.dumps(["中国人民银行", "LPR", "降准"]),
            "sentiment": "neutral",
            "importance": "high",
            "primary_category_id": cat_map.get("macro"),
            "status": "completed",
        },
        {
            "title": "新能源汽车行业2024年展望",
            "summary": "新能源汽车渗透率突破40%，行业进入成熟期，竞争格局重塑，龙头企业优势明显。",
            "clean_content": "2024年新能源汽车行业呈现以下特征...",
            "key_points": json.dumps(["渗透率突破40%", "价格战趋缓", "出海成为新增长点"]),
            "entities": json.dumps(["新能源汽车", "比亚迪", "特斯拉"]),
            "sentiment": "positive",
            "importance": "high",
            "primary_category_id": cat_map.get("industry"),
            "status": "completed",
        },
        {
            "title": "特斯拉Q3财报深度分析",
            "summary": "特斯拉第三季度营收超预期，毛利率承压但FSD收入成为新看点， Robotaxi商业化路径清晰。",
            "clean_content": "特斯拉发布2024年Q3财报...",
            "key_points": json.dumps(["营收超预期3%", "毛利率降至17.9%", "FSD累计收入突破10亿美元"]),
            "entities": json.dumps(["特斯拉", "FSD", "Robotaxi"]),
            "sentiment": "positive",
            "importance": "medium",
            "primary_category_id": cat_map.get("company"),
            "status": "completed",
        },
    ]

    for data in article_data:
        r = requests.post(f"{BASE_URL}/api/articles", json=data)
        if r.status_code in (200, 201):
            articles.append(r.json())

    # Create wiki pages
    wikis = [
        {
            "title": "货币政策综合报告",
            "slug": "monetary-policy",
            "topic": "货币政策",
            "content": "# 货币政策综合报告\n\n## 概述\n货币政策是央行调控经济的核心工具...\n\n## 关键要点\n- 降准降息预期\n- LPR改革深化\n- 结构性货币政策工具",
            "article_count": 1,
        },
        {
            "title": "新能源行业分析",
            "slug": "new-energy",
            "topic": "新能源行业",
            "content": "# 新能源行业综合分析\n\n## 市场现状\n2024年新能源汽车渗透率持续攀升...",
            "article_count": 1,
        },
    ]
    for w in wikis:
        requests.post(f"{BASE_URL}/api/wiki/writeback", json={
            "title": w["title"],
            "content": w["content"],
        })

    return articles


def take_screenshots():
    """Use Playwright to capture key pages."""
    from playwright.sync_api import sync_playwright

    screenshots_dir = "docs/screenshots"
    os.makedirs(screenshots_dir, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()

        pages_to_capture = [
            ("", "仪表盘 - 数据总览"),  # root path
            ("library", "知识库 - 文章列表"),
            ("chat", "AI助手 - 智能问答"),
            ("wiki", "Wiki - 知识综述"),
            ("settings", "设置 - 用户规则"),
        ]

        captured = {}
        for route, title in pages_to_capture:
            try:
                url = f"{FRONTEND_URL}/{route}" if route else FRONTEND_URL
                page.goto(url, wait_until="networkidle", timeout=15000)
                page.wait_for_timeout(1200)
                filename = route if route else "dashboard"
                path = os.path.join(screenshots_dir, f"{filename}.png")
                page.screenshot(path=path, full_page=True)
                captured[route] = path
                print(f"✅ Captured: {title} -> {path}")
            except Exception as e:
                print(f"❌ Failed {route}: {e}")

        # Capture article detail (need article ID)
        try:
            r = requests.get(f"{BASE_URL}/api/articles?limit=1")
            if r.status_code == 200:
                items = r.json().get("items", [])
                if items:
                    aid = items[0]["id"]
                    page.goto(f"{FRONTEND_URL}/article/{aid}", wait_until="networkidle", timeout=15000)
                    page.wait_for_timeout(800)
                    path = os.path.join(screenshots_dir, "article_detail.png")
                    page.screenshot(path=path, full_page=True)
                    captured["article_detail"] = path
                    print(f"✅ Captured: 文章详情 -> {path}")
        except Exception as e:
            print(f"❌ Failed article_detail: {e}")

        # Capture wiki detail
        try:
            page.goto(f"{FRONTEND_URL}/wiki/monetary-policy", wait_until="networkidle", timeout=15000)
            page.wait_for_timeout(800)
            path = os.path.join(screenshots_dir, "wiki_detail.png")
            page.screenshot(path=path, full_page=True)
            captured["wiki_detail"] = path
            print(f"✅ Captured: Wiki详情 -> {path}")
        except Exception as e:
            print(f"❌ Failed wiki_detail: {e}")

        browser.close()
        return captured


def generate_pdf(captured):
    """Generate PDF manual with screenshots."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    # Try to register a Chinese font
    font_paths = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
    ]
    font_name = "Helvetica"
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                pdfmetrics.registerFont(TTFont("ChineseFont", fp))
                font_name = "ChineseFont"
                break
            except Exception:
                continue

    doc = SimpleDocTemplate(
        "docs/用户说明手册.pdf",
        pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontName=font_name,
        fontSize=24,
        textColor=colors.HexColor("#1a365d"),
        spaceAfter=30,
        alignment=1,  # center
    )
    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        fontName=font_name,
        fontSize=16,
        textColor=colors.HexColor("#2563eb"),
        spaceAfter=12,
        spaceBefore=20,
    )
    body_style = ParagraphStyle(
        "CustomBody",
        parent=styles["BodyText"],
        fontName=font_name,
        fontSize=11,
        leading=18,
        spaceAfter=10,
    )
    caption_style = ParagraphStyle(
        "Caption",
        parent=styles["Italic"],
        fontName=font_name,
        fontSize=9,
        textColor=colors.gray,
        alignment=1,
    )

    story = []

    # Cover
    story.append(Spacer(1, 4*cm))
    story.append(Paragraph("经济大师", title_style))
    story.append(Paragraph("用户说明手册", title_style))
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph(f"生成日期：{datetime.now().strftime('%Y年%m月%d日')}", body_style))
    story.append(Spacer(1, 2*cm))
    story.append(Paragraph("本手册基于系统真实页面截图制作，涵盖核心功能的使用方法。", body_style))
    story.append(PageBreak())

    # Table of Contents
    story.append(Paragraph("目录", heading_style))
    toc_items = [
        "1. 仪表盘 - 数据总览",
        "2. 知识库 - 文章列表",
        "3. 文章详情 - 深度阅读",
        "4. AI助手 - 智能问答",
        "5. Wiki - 知识综述",
        "6. 设置 - 用户规则",
    ]
    for item in toc_items:
        story.append(Paragraph(item, body_style))
    story.append(PageBreak())

    # Sections
    sections = [
        ("dashboard", "1. 仪表盘", "仪表盘展示系统核心数据指标，包括文章总量、今日新增、本周趋势、情感分布、分类分布和最新文章列表。通过顶部分类筛选可快速聚焦关注领域。"),
        ("library", "2. 知识库", "知识库是系统的核心内容入口。支持关键词全文搜索、语义搜索和混合搜索三种模式。可按照分类筛选文章，每篇文章展示标题、摘要、情感标签和重要度。"),
        ("article_detail", "3. 文章详情", "文章详情页提供四个视图：AI摘要（关键要点提取）、原文（完整内容）、思维导图（结构化大纲）、知识图谱（关联文章网络）。支持点赞/点踩反馈和返回知识库。"),
        ("chat", "4. AI助手", "AI助手基于知识库内容进行智能问答。系统会自动选择最佳策略（Wiki综述、全文搜索、RAG检索）回答你的问题。回答中会标注引用来源，可一键查看原文或保存到Wiki。"),
        ("wiki_detail", "5. Wiki综述", "Wiki将多篇文章按主题整合为结构化综述页面。支持自动编译和手动更新，是知识库的高阶组织形式。点击Wiki链接可在SPA内跳转，不会丢失当前页面状态。"),
        ("settings", "6. 设置", "设置页面允许配置用户自定义规则，这些规则会注入到AI助手的系统提示中，影响回答风格和关注点。规则长度限制5000字符，避免过度增加Prompt负担。"),
    ]

    for key, title, desc in sections:
        story.append(Paragraph(title, heading_style))
        story.append(Paragraph(desc, body_style))
        story.append(Spacer(1, 0.5*cm))

        img_path = captured.get(key)
        if img_path and os.path.exists(img_path):
            # Scale image to fit page width
            img = Image(img_path, width=16*cm, height=10*cm)
            img.hAlign = "CENTER"
            story.append(img)
            story.append(Paragraph(f"▲ {title}页面截图", caption_style))
        else:
            story.append(Paragraph("（截图暂不可用）", caption_style))

        story.append(Spacer(1, 1*cm))
        story.append(PageBreak())

    # Footer tips
    story.append(Paragraph("使用提示", heading_style))
    tips = [
        "• 所有内部链接（文章、Wiki）均采用SPA导航，点击不会刷新整页",
        "• 搜索支持三种模式切换：全文搜索（关键词匹配）、语义搜索（向量相似度）、混合搜索（综合排序）",
        "• AI助手回答失败时会显示红色提示，反馈和保存Wiki失败也有明确提示",
        "• 文章自动提取情感倾向（正面/中性/负面）和重要度（高/中/低），方便快速筛选",
        "• Wiki页面支持级联更新：新文章入库时会自动触发相关Wiki重新编译",
    ]
    for tip in tips:
        story.append(Paragraph(tip, body_style))

    doc.build(story)
    print(f"\n📄 PDF generated: docs/用户说明手册.pdf")


if __name__ == "__main__":
    print("=" * 50)
    print("Step 1: Seeding sample data...")
    print("=" * 50)
    seed_data()

    print("\n" + "=" * 50)
    print("Step 2: Taking screenshots...")
    print("=" * 50)
    captured = take_screenshots()

    print("\n" + "=" * 50)
    print("Step 3: Generating PDF...")
    print("=" * 50)
    generate_pdf(captured)

    print("\n✅ Done!")
