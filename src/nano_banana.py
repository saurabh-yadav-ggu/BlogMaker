from __future__ import annotations

from typing import Any

import requests

from .config import get_settings


class NanoBananaClient:
    def __init__(self) -> None:
        settings = get_settings()
        self.base_url = settings.nano_banana_base_url
        self.api_key = settings.nano_banana_api_key

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
        if not response.ok:
            raise RuntimeError(f"Nano Banana request failed: {response.status_code} {response.text[:250]}")

        payload = response.json()
        if not isinstance(payload, dict):
            raise RuntimeError("Nano Banana returned unexpected response shape")
        return payload
