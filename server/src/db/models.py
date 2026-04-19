from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey,
    REAL, CheckConstraint, UniqueConstraint, create_engine
)
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()


class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, autoincrement=True)
    parent_id = Column(Integer, ForeignKey("categories.id"))
    name = Column(String, nullable=False)
    slug = Column(String, nullable=False, unique=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class Source(Base):
    __tablename__ = "sources"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    driver = Column(String, nullable=False, default="firecrawl")
    config = Column(Text)
    schedule = Column(String)
    is_active = Column(Integer, default=1)
    last_crawled_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Article(Base):
    __tablename__ = "articles"
    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("sources.id"))
    url = Column(String, unique=True)
    title = Column(String, nullable=False)
    author = Column(String)
    published_at = Column(DateTime)
    clean_content = Column(Text)
    summary = Column(Text)
    key_points = Column(Text)
    entities = Column(Text)
    sentiment = Column(String)
    importance = Column(String)
    mindmap = Column(Text)
    primary_category_id = Column(Integer, ForeignKey("categories.id"))
    secondary_category_id = Column(Integer, ForeignKey("categories.id"))
    md_file_path = Column(String)
    status = Column(String, default="pending")
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    usage_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class ArticleTag(Base):
    __tablename__ = "article_tags"
    article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)


class KnowledgeEdge(Base):
    __tablename__ = "knowledge_edges"
    id = Column(Integer, primary_key=True, autoincrement=True)
    source_article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"))
    target_article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"))
    relation_type = Column(String, nullable=False)
    strength = Column(REAL)
    reason = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class UploadTask(Base):
    __tablename__ = "upload_tasks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_size = Column(Integer)
    status = Column(String, default="pending")
    error_message = Column(Text)
    article_id = Column(Integer, ForeignKey("articles.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)


class VideoTranscript(Base):
    __tablename__ = "video_transcripts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"))
    video_path = Column(String, nullable=False)
    audio_path = Column(String)
    transcript_text = Column(Text)
    segments = Column(Text)
    language = Column(String, default="zh")
    model_used = Column(String, default="whisper-1")
    created_at = Column(DateTime, default=datetime.utcnow)


class Publication(Base):
    __tablename__ = "publications"
    id = Column(Integer, primary_key=True, autoincrement=True)
    pub_type = Column(String, nullable=False)
    title = Column(String, nullable=False)
    authors = Column(Text)
    publisher = Column(String)
    isbn = Column(String)
    doi = Column(String)
    url = Column(String)
    abstract = Column(Text)
    keywords = Column(Text)
    publication_date = Column(String)
    file_path = Column(String)
    source = Column(String)
    citation_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class PublicationChapter(Base):
    __tablename__ = "publication_chapters"
    id = Column(Integer, primary_key=True, autoincrement=True)
    publication_id = Column(Integer, ForeignKey("publications.id", ondelete="CASCADE"))
    chapter_number = Column(Integer)
    title = Column(String, nullable=False)
    summary = Column(Text)
    start_page = Column(Integer)
    end_page = Column(Integer)
    content_text = Column(Text)
    md_file_path = Column(String)
    article_id = Column(Integer, ForeignKey("articles.id"))


class SkillFeedback(Base):
    __tablename__ = "skill_feedback"
    id = Column(Integer, primary_key=True, autoincrement=True)
    skill_name = Column(String, nullable=False, default="econ-master")
    query = Column(String, nullable=False)
    response_summary = Column(Text)
    rating = Column(Integer)
    comment = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class Correction(Base):
    __tablename__ = "corrections"
    id = Column(Integer, primary_key=True, autoincrement=True)
    article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"))
    field = Column(String, nullable=False)
    original_value = Column(Text)
    corrected_value = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
