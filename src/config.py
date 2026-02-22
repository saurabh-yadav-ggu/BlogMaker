from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    gemini_api_key: str
    gemini_model: str
    nano_banana_api_key: str
    nano_banana_base_url: str
    blog_target_words: int


def _safe_int(value: str, default: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return parsed if parsed > 0 else default


def get_settings() -> Settings:
    return Settings(
        gemini_api_key=os.getenv("GEMINI_API_KEY", "").strip(),
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-1.5-pro").strip() or "gemini-1.5-pro",
        nano_banana_api_key=os.getenv("NANO_BANANA_API_KEY", "").strip(),
        nano_banana_base_url=os.getenv("NANO_BANANA_BASE_URL", "https://api.nanobanana.ai/v1").strip().rstrip("/"),
        blog_target_words=_safe_int(os.getenv("BLOG_TARGET_WORDS", "1600"), 1600),
    )
