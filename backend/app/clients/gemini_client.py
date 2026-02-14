"""
Gemini AI Client Wrapper
Handles all interactions with Google's Gemini API.
"""

import google.generativeai as genai
import json
import logging
from typing import Optional
from app.core.settings import get_settings, validate_required_keys

logger = logging.getLogger(__name__)


class GeminiClient:
    """
    Wrapper for Google Gemini API.
    Handles text generation with proper error handling and timeouts.
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
    ) -> str:
        """
        Generate text using Gemini API.
        
        Args:
            prompt: The input prompt for text generation
            temperature: Controls randomness (0.0-2.0), default 0.7
            max_tokens: Maximum tokens in response, default 1024
        
        Returns:
            Generated text response
        
        Raises:
            ValueError: If API key is invalid or API fails
            TimeoutError: If request exceeds timeout
        """
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
        
        except ValueError as e:
            logger.error(f"Gemini API key invalid or request failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error from Gemini API: {str(e)}")
            raise ValueError(f"Gemini API error: {str(e)}")
    
    def generate_json(
        self,
        prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> dict:
        """
        Generate JSON-formatted response from Gemini.
        
        Args:
            prompt: Prompt requesting JSON output
            temperature: Lower temperature for structured output
            max_tokens: Maximum tokens, default 1024
        
        Returns:
            Parsed JSON dictionary
        
        Raises:
            ValueError: If response is not valid JSON
        """
        response_text = self.generate_text(
            prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        # Try to parse as JSON
        try:
            # Remove markdown code fences if present
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
            
            response_text = response_text.strip()
            return json.loads(response_text)
        
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse Gemini JSON response: {str(e)}")
            logger.debug(f"Response text: {response_text}")
            raise ValueError(f"Invalid JSON from Gemini: {str(e)}")


# Singleton instance
_gemini_client: Optional[GeminiClient] = None


def get_gemini_client() -> GeminiClient:
    """
    Get or create singleton Gemini client.
    
    Returns:
        GeminiClient: Singleton instance
    
    Raises:
        ValueError: If GEMINI_API_KEY is not configured
    """
    global _gemini_client
    
    if _gemini_client is None:
        _gemini_client = GeminiClient()
    
    return _gemini_client
