"""
AI Client selector
Uses Gemini client for all AI operations.
"""

from typing import Optional
import logging
from app.core.settings import get_settings

logger = logging.getLogger(__name__)

_client = None


def get_ai_client():
    global _client
    if _client is not None:
        return _client

    try:
        from app.clients.gemini_client import get_gemini_client
        logger.info("Using Gemini client")
        _client = get_gemini_client()
        return _client
    except Exception:
        logger.exception("Failed to initialize Gemini client")
        raise RuntimeError("Gemini client unavailable. Configure GEMINI_API_KEY")
