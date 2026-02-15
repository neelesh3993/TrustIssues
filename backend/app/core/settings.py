"""
Configuration settings using Pydantic BaseSettings.
Loads configuration from environment variables and .env files.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional
import os


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables and .env file.
    
    Attributes:
        gemini_api_key: Google Gemini API key (required for production)
        gemini_model: Model name for Gemini API (default: "gemini-1.5-flash")
        news_api_key: NewsAPI key (required for article retrieval)
        newsapi_endpoint: NewsAPI endpoint URL (default: official endpoint)
        newsapi_page_size: Number of articles per NewsAPI request (default: 5)
        newsapi_language: Language for NewsAPI search (default: "en")
        request_timeout_seconds: HTTP request timeout in seconds (default: 20)
        max_claims: Maximum number of claims to extract (default: 5)
    """
    
    gemini_api_key: Optional[str] = None
    gemini_model: str = "gemini-1.5-flash"
    news_api_key: Optional[str] = None
    newsapi_endpoint: str = "https://newsapi.org/v2/everything"
    newsapi_page_size: int = 5
    newsapi_language: str = "en"
    request_timeout_seconds: int = 20
    max_claims: int = 5
    
    class Config:
        """Pydantic config to load from .env file."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False  # Allow GEMINI_API_KEY and gemini_api_key
        extra = "ignore"  # Ignore extra fields in .env file


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Uses LRU cache to ensure only one Settings object is created.
    
    Returns:
        Settings: Singleton settings instance
    """
    return Settings()


def validate_required_keys():
    """
    Validate that required API keys are set.
    Raises ValueError with clear instructions if keys are missing.
    
    Raises:
        ValueError: If required keys are not configured
    """
    settings = get_settings()
    
    missing_keys = []
    
    if not settings.gemini_api_key:
        missing_keys.append("GEMINI_API_KEY")
    
    if not settings.news_api_key:
        missing_keys.append("NEWS_API_KEY")
    
    if missing_keys:
        keys_str = ", ".join(missing_keys)
        raise ValueError(
            f"\n\n❌ MISSING REQUIRED API KEYS: {keys_str}\n\n"
            f"Please set these environment variables:\n"
            f"  1. Get GEMINI_API_KEY from: https://makersuite.google.com/app/apikey\n"
            f"  2. Get NEWS_API_KEY from: https://newsapi.org/\n\n"
            f"Options to set them:\n"
            f"  A) Create a .env file in the backend directory with:\n"
            f"     GEMINI_API_KEY=your_key_here\n"
            f"     NEWS_API_KEY=your_key_here\n\n"
            f"  B) Export as environment variables:\n"
            f"     export GEMINI_API_KEY=your_key_here\n"
            f"     export NEWS_API_KEY=your_key_here\n\n"
            f"  C) Set in Windows PowerShell:\n"
            f"     $env:GEMINI_API_KEY='your_key_here'\n"
            f"     $env:NEWS_API_KEY='your_key_here'\n\n"
            f"See .env.example for a template.\n"
        )
