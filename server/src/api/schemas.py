"""Pydantic request/response schemas for API validation."""
from typing import Optional
from pydantic import BaseModel, Field


class ArticleListParams(BaseModel):
    category_id: Optional[int] = None
    tag: Optional[str] = None
    status: Optional[str] = None
    limit: int = Field(default=50, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


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
    rating: Optional[int] = Field(default=None, ge=1, le=5)
    comment: Optional[str] = None
