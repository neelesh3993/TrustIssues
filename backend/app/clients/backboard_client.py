"""
Backboard client - minimal HTTP wrapper
"""

import logging
import json
import requests
from typing import Optional
from app.core.settings import get_settings

logger = logging.getLogger(__name__)


class BackboardClient:
    def __init__(self):
        settings = get_settings()
        if not settings.backboard_api_key:
            raise ValueError("BACKBOARD_API_KEY not configured")
        self.api_key = settings.backboard_api_key
        self.model = settings.backboard_model
        self.endpoint = settings.backboard_endpoint.rstrip("/")

    def _post(self, path: str, payload: dict, timeout: int = 30):
        url = f"{self.endpoint}{path}"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
        try:
            return resp.json()
        except Exception:
            logger.error("Backboard non-json response: %s", resp.text)
            resp.raise_for_status()

    def generate_text(self, prompt: str, temperature: float = 0.0, max_tokens: int = 1024) -> str:
        payload = {"model": self.model, "input": prompt, "temperature": temperature, "max_tokens": max_tokens}
        data = self._post("/generate", payload)
        # tolerant extraction
        if isinstance(data, dict):
            if "output" in data and isinstance(data["output"], str):
                return data["output"]
            if "text" in data and isinstance(data["text"], str):
                return data["text"]
            if "choices" in data and isinstance(data["choices"], list) and data["choices"]:
                c = data["choices"][0]
                for k in ("text", "output", "content"):
                    if k in c and isinstance(c[k], str):
                        return c[k]
        return json.dumps(data)

    def generate_json(self, prompt: str, temperature: float = 0.0, max_tokens: int = 1024) -> dict:
        text = self.generate_text(prompt, temperature=temperature, max_tokens=max_tokens)
        if text.startswith("```"):
            parts = text.split("```")
            if len(parts) > 1:
                text = parts[1]
        return json.loads(text)


_backboard_client: Optional[BackboardClient] = None


def get_backboard_client() -> BackboardClient:
    global _backboard_client
    if _backboard_client is None:
        _backboard_client = BackboardClient()
    return _backboard_client
