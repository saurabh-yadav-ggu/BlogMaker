from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
NANO_BANANA_API_KEY = os.getenv("NANO_BANANA_API_KEY", "")
NANO_BANANA_BASE_URL = os.getenv("NANO_BANANA_BASE_URL", "https://api.nanobanana.ai/v1")
BLOG_TARGET_WORDS = int(os.getenv("BLOG_TARGET_WORDS", "1600"))
