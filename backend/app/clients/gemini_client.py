"""
Gemini AI Client Wrapper - ENHANCED WITH RETRY LOGIC
Handles all interactions with Google's Gemini API.
NOW WITH: Automatic retry on 429, exponential backoff, quota management
"""

import google.generativeai as genai
import json
import logging
import time
import random
import re
from typing import Optional
from app.core.settings import get_settings

logger = logging.getLogger(__name__)


class GeminiClient:
    """
    Wrapper for Google Gemini API with retry logic and rate limit handling.
    """
    
    def __init__(self):
        """Initialize Gemini client with API key from settings."""
        settings = get_settings()
        
        if not settings.gemini_api_key:
            raise ValueError(
                "❌ GEMINI_API_KEY not configured!\n"
                "See setup instructions in README.md or .env.example"
            )
        
        genai.configure(api_key=settings.gemini_api_key)
        self.model_name = settings.gemini_model
        self.model = genai.GenerativeModel(self.model_name)
        logger.info(f"Gemini client initialized with model: {self.model_name}")
    
    def generate_text(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        max_retries: int = 3
    ) -> str:
        """
        Generate text using Gemini API with automatic retry on rate limits.
        
        Args:
            prompt: The input prompt for text generation
            temperature: Controls randomness (0.0-2.0), default 0.7
            max_tokens: Maximum tokens in response, default 1024
            max_retries: Maximum number of retries on rate limit, default 3
        
        Returns:
            Generated text response
        
        Raises:
            ValueError: If API key is invalid or API fails after retries
        """
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=temperature,
                        max_output_tokens=max_tokens,
                    )
                )
                
                if not response or not response.text:
                    raise ValueError("Empty response from Gemini API")
                
                return response.text
            
            except Exception as e:
                error_msg = str(e)
                
                # Check for rate limit errors (429)
                if self._is_rate_limit_error(error_msg):
                    retry_delay = self._parse_retry_delay(error_msg)
                    
                    if attempt < max_retries - 1:
                        wait_time = retry_delay if retry_delay else (2 ** attempt) + random.random()
                        logger.warning(
                            f"Gemini rate limit hit (429). "
                            f"Retry {attempt + 1}/{max_retries} in {wait_time:.1f}s..."
                        )
                        time.sleep(wait_time)
                        continue
                    else:
                        logger.error("Gemini rate limit: Max retries exceeded")
                        raise ValueError(
                            "Gemini API rate limit exceeded. "
                            "Please wait a few minutes or upgrade your API quota."
                        )
                
                # Check for quota exceeded
                elif "quota" in error_msg.lower() or "resource_exhausted" in error_msg.lower():
                    logger.error(f"Gemini quota exhausted: {error_msg}")
                    raise ValueError(
                        "Gemini API quota exhausted. "
                        "Please check your quota at https://aistudio.google.com/app/apikey "
                        "or upgrade to a paid plan."
                    )
                
                # Other errors
                else:
                    logger.error(f"Gemini API error: {error_msg}")
                    raise ValueError(f"Gemini API error: {error_msg}")
        
        raise ValueError("Gemini API failed after all retries")
    
    def generate_json(
        self,
        prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 1024,
        max_retries: int = 3
    ) -> dict:
        """
        Generate JSON-formatted response from Gemini with retry logic.
        
        Args:
            prompt: Prompt requesting JSON output
            temperature: Lower temperature for structured output
            max_tokens: Maximum tokens, default 1024
            max_retries: Maximum retries on rate limit
        
        Returns:
            Parsed JSON dictionary
        
        Raises:
            ValueError: If response is not valid JSON or API fails
        """
        response_text = self.generate_text(
            prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            max_retries=max_retries
        )
        
        # Try to parse as JSON
        try:
            # Remove markdown code fences if present
            text = response_text.strip()
            if text.startswith("```"):
                parts = text.split("```")
                if len(parts) >= 2:
                    text = parts[1]
                    if text.startswith("json"):
                        text = text[4:]
            
            text = text.strip()
            return json.loads(text)
        
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse Gemini JSON response: {str(e)}")
            logger.debug(f"Response text: {response_text}")
            raise ValueError(f"Invalid JSON from Gemini: {str(e)}")
    
    def _is_rate_limit_error(self, error_msg: str) -> bool:
        """
        Check if error message indicates a rate limit (429).
        
        Args:
            error_msg: Error message string
        
        Returns:
            True if this is a rate limit error
        """
        rate_limit_indicators = [
            "429",
            "rate limit",
            "too many requests",
            "quota exceeded",
            "resource_exhausted",
            "please retry"
        ]
        
        error_lower = error_msg.lower()
        return any(indicator in error_lower for indicator in rate_limit_indicators)
    
    def _parse_retry_delay(self, error_msg: str) -> Optional[float]:
        """
        Parse retry delay from error message like "Please retry in 31s".
        
        Args:
            error_msg: Error message from API
        
        Returns:
            Number of seconds to wait, or None if can't parse
        """
        try:
            # Look for patterns like "retry in 31s" or "retry after 31 seconds"
            patterns = [
                r'retry in (\d+)s',
                r'retry after (\d+) second',
                r'retry_delay["\s:]+(\d+)'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, error_msg, re.IGNORECASE)
                if match:
                    delay = float(match.group(1))
                    logger.debug(f"Parsed retry delay: {delay}s from error message")
                    return delay
        
        except Exception as e:
            logger.debug(f"Could not parse retry delay: {e}")
        
        return None


# Singleton instance
_gemini_client: Optional[GeminiClient] = None


def get_gemini_client() -> GeminiClient:
    """
    Get or create singleton Gemini client.
    
    Returns:
        GeminiClient: Singleton instance with retry logic
    
    Raises:
        ValueError: If GEMINI_API_KEY is not configured
    """
    global _gemini_client
    
    if _gemini_client is None:
        _gemini_client = GeminiClient()
    
    return _gemini_client
