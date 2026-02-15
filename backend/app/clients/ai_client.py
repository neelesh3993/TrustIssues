"""
AI Client selector
Returns Backboard client if configured, otherwise falls back to Gemini client.
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

    settings = get_settings()

    if settings.backboard_api_key:
        try:
            from app.clients.backboard_client import get_backboard_client
            logger.info("Using Backboard client")
            _client = get_backboard_client()
            return _client
        except Exception:
            logger.exception("Failed to initialize Backboard client")

    # Fallback to Gemini
    try:
        from app.clients.gemini_client import get_gemini_client
        logger.info("Using Gemini client")
        _client = get_gemini_client()
        return _client
    except Exception:
        logger.exception("Failed to initialize Gemini client")
        raise RuntimeError("No AI client available. Configure BACKBOARD_API_KEY or GEMINI_API_KEY")
