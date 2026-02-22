from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator


class BlogRequest(BaseModel):
    topic: str = Field(..., min_length=5, description="Primary blog topic")
    target_words: int = Field(default=1600, ge=600, le=4000)
    tone: str = Field(default="authoritative")
    audience: str = Field(default="marketing professionals")

    @field_validator("topic")
    @classmethod
    def validate_topic(cls, value: str) -> str:
        cleaned = value.strip()
        if len(cleaned) < 5:
            raise ValueError("Topic must be at least 5 characters long")
        return cleaned


class FinalBlogPackage(BaseModel):
    title: str
    slug: str
    meta_description: str
    markdown: str
    keywords: list[str]
    seo_score: float
    images: list[dict[str, Any]]
    debug: dict[str, Any]
