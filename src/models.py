from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class BlogRequest(BaseModel):
    topic: str = Field(..., min_length=5, description="Primary blog topic")
    target_words: int = Field(default=1600, ge=600, le=4000)
    tone: str = Field(default="authoritative")
    audience: str = Field(default="marketing professionals")


class BlogState(BaseModel):
    request: BlogRequest
    research: dict[str, Any] = Field(default_factory=dict)
    outline: dict[str, Any] = Field(default_factory=dict)
    draft: dict[str, Any] = Field(default_factory=dict)
    seo: dict[str, Any] = Field(default_factory=dict)
    image_prompts: list[str] = Field(default_factory=list)
    images: list[dict[str, Any]] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)


class FinalBlogPackage(BaseModel):
    title: str
    slug: str
    meta_description: str
    markdown: str
    keywords: list[str]
    seo_score: float
    images: list[dict[str, Any]]
    debug: dict[str, Any]
