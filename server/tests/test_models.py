import pytest

from src.db.models import (
    Category, Source, Article, Tag, ArticleTag,
    KnowledgeEdge, UploadTask, SkillFeedback, Correction,
)


class TestCategory:
    def test_create_category(self, db_session):
        cat = Category(name="宏观经济", slug="macro_economy")
        db_session.add(cat)
        db_session.commit()
        assert cat.id is not None
        assert cat.name == "宏观经济"

    def test_category_hierarchy(self, db_session):
        parent = Category(name="宏观经济", slug="macro")
        db_session.add(parent)
        db_session.commit()

        child = Category(name="货币政策", slug="monetary_policy", parent_id=parent.id)
        db_session.add(child)
        db_session.commit()

        assert child.parent_id == parent.id


class TestSource:
    def test_create_source(self, db_session):
        source = Source(name="新浪财经", url="https://finance.sina.com.cn", driver="firecrawl")
        db_session.add(source)
        db_session.commit()
        assert source.id is not None
        assert source.is_active == 1


class TestArticle:
    def test_create_article(self, db_session):
        article = Article(title="测试文章", status="pending")
        db_session.add(article)
        db_session.commit()
        assert article.id is not None
        assert article.status == "pending"

    def test_article_with_category(self, db_session):
        cat = Category(name="宏观经济", slug="macro")
        db_session.add(cat)
        db_session.commit()

        article = Article(title="测试", primary_category_id=cat.id, status="completed")
        db_session.add(article)
        db_session.commit()

        assert article.primary_category_id == cat.id


class TestTag:
    def test_create_tag(self, db_session):
        tag = Tag(name="降准")
        db_session.add(tag)
        db_session.commit()
        assert tag.id is not None
        assert tag.usage_count == 0

    def test_article_tag_association(self, db_session):
        article = Article(title="测试文章", status="completed")
        tag = Tag(name="央行")
        db_session.add_all([article, tag])
        db_session.commit()

        assoc = ArticleTag(article_id=article.id, tag_id=tag.id)
        db_session.add(assoc)
        db_session.commit()

        assert assoc.article_id == article.id
        assert assoc.tag_id == tag.id


class TestSkillFeedback:
    def test_create_feedback(self, db_session):
        fb = SkillFeedback(skill_name="econ-master", query="测试问题", rating=1)
        db_session.add(fb)
        db_session.commit()
        assert fb.id is not None
        assert fb.rating == 1


class TestCorrection:
    def test_create_correction(self, db_session):
        article = Article(title="测试", status="completed")
        db_session.add(article)
        db_session.commit()

        corr = Correction(
            article_id=article.id,
            field="primary_category",
            original_value="宏观经济",
            corrected_value="金融市场",
        )
        db_session.add(corr)
        db_session.commit()

        assert corr.corrected_value == "金融市场"
