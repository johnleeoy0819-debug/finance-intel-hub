"""Pydantic request/response schemas for API validation."""
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class ArticleListParams(BaseModel):
    category_id: Optional[int] = None
    tag: Optional[str] = None
    status: Optional[str] = None
    limit: int = Field(default=50, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class ArticleResponse(BaseModel):
    id: int
    title: str
    url: Optional[str] = None
    source: Optional[str] = None
    author: Optional[str] = None
    published_at: Optional[str] = None
    summary: Optional[str] = None
    key_points: Optional[List[str]] = None
    entities: Optional[List[str]] = None
    sentiment: Optional[str] = None
    importance: Optional[str] = None
    primary_category: Optional[str] = None
    secondary_category: Optional[str] = None
    tags: List[str] = []
    mindmap: Optional[str] = None
    status: str
    created_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CorrectionCreate(BaseModel):
    field: str
    original_value: Optional[str] = None
    corrected_value: str


class SourceCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    url: str = Field(..., min_length=1, max_length=1000)
    driver: str = Field(default="playwright", max_length=50)
    config: Optional[str] = None
    schedule: Optional[str] = None
    is_active: int = Field(default=1, ge=0, le=1)


class SourceUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=200)
    url: Optional[str] = Field(default=None, max_length=1000)
    driver: Optional[str] = Field(default=None, max_length=50)
    config: Optional[str] = None
    schedule: Optional[str] = None
    is_active: Optional[int] = Field(default=None, ge=0, le=1)


class FeedbackCreate(BaseModel):
    skill_name: Optional[str] = "econ-master"
    query: str = Field(..., min_length=1)
    response_summary: Optional[str] = None
    rating: Optional[int] = Field(default=None, ge=-1, le=1)
    comment: Optional[str] = None
