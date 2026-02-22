from __future__ import annotations

from typing import Any

import requests

from .config import NANO_BANANA_API_KEY, NANO_BANANA_BASE_URL


class NanoBananaClient:
    def __init__(self) -> None:
        self.base_url = NANO_BANANA_BASE_URL.rstrip("/")
        self.api_key = NANO_BANANA_API_KEY

    def generate_image(self, prompt: str, aspect_ratio: str = "16:9") -> dict[str, Any]:
        if not self.api_key:
            raise ValueError("NANO_BANANA_API_KEY is required.")

        response = requests.post(
            f"{self.base_url}/images/generate",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "prompt": prompt,
                "aspect_ratio": aspect_ratio,
                "style": "photorealistic editorial",
            },
            timeout=60,
        )
        response.raise_for_status()
        return response.json()
