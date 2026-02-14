"""
NewsAPI Client
Handles retrieval of news articles for evidence gathering.
"""

import requests
import logging
from typing import List, Dict, Optional
from app.core.settings import get_settings

logger = logging.getLogger(__name__)


class NewsAPIError(Exception):
    """Raised when NewsAPI request fails."""
    pass


def search_news(query: str) -> List[Dict]:
    """
    Search for news articles using NewsAPI.
    
    Args:
        query: Search query string
    
    Returns:
        List of normalized article dictionaries with:
        - name: Source name
        - headline: Article title
        - url: Article URL
        - snippet: Article description/content
        - publishedAt: Publication date
    
    Raises:
        NewsAPIError: If API key is missing or request fails
    
    Examples:
        >>> articles = search_news("climate change")
        >>> for article in articles:
        ...     print(article['headline'], article['url'])
    """
    settings = get_settings()
    
    if not settings.news_api_key:
        error_msg = (
            "❌ NEWS_API_KEY not configured!\n"
            "Get a free API key from: https://newsapi.org/\n\n"
            "Then set it:\n"
            "  - In .env file: NEWS_API_KEY=your_key_here\n"
            "  - Or export: export NEWS_API_KEY=your_key_here\n"
            "  - Or in PowerShell: $env:NEWS_API_KEY='your_key_here'\n"
        )
        logger.error(error_msg)
        raise NewsAPIError(error_msg)
    
    try:
        params = {
            "q": query,
            "pageSize": settings.newsapi_page_size,
            "language": settings.newsapi_language,
            "sortBy": "relevancy",
            "apiKey": settings.news_api_key,
        }
        
        response = requests.get(
            settings.newsapi_endpoint,
            params=params,
            timeout=settings.request_timeout_seconds,
        )
        
        response.raise_for_status()
        data = response.json()
        
        # Check for API errors
        if data.get("status") == "error":
            error_msg = data.get("message", "Unknown error")
            logger.error(f"NewsAPI error: {error_msg}")
            raise NewsAPIError(f"NewsAPI error: {error_msg}")
        
        articles = data.get("articles", [])
        
        # Normalize returned articles
        normalized = []
        for article in articles:
            normalized_article = {
                "name": article.get("source", {}).get("name", "Unknown Source"),
                "headline": article.get("title", "Untitled"),
                "url": article.get("url", ""),
                "snippet": article.get("description", "") or article.get("content", ""),
                "publishedAt": article.get("publishedAt", ""),
            }
            normalized.append(normalized_article)
        
        logger.info(f"Found {len(normalized)} articles for query: {query}")
        return normalized
    
    except requests.Timeout:
        error_msg = f"NewsAPI request timed out after {settings.request_timeout_seconds}s"
        logger.error(error_msg)
        raise NewsAPIError(error_msg)
    
    except requests.RequestException as e:
        error_msg = f"NewsAPI request failed: {str(e)}"
        logger.error(error_msg)
        raise NewsAPIError(error_msg)
    
    except Exception as e:
        error_msg = f"Unexpected error calling NewsAPI: {str(e)}"
        logger.error(error_msg)
        raise NewsAPIError(error_msg)


def search_news_with_fallback(query: str) -> List[Dict]:
    """
    Search for news with graceful failure.
    Returns empty list if search fails instead of raising.
    
    Args:
        query: Search query string
    
    Returns:
        List of articles, or empty list if search fails
    """
    try:
        return search_news(query)
    except NewsAPIError as e:
        logger.warning(f"News search failed, continuing without evidence: {str(e)}")
        return []
