"""
Claim Extractor
Extracts factual claims from content using Gemini AI.
"""

import json
import logging
from typing import List
from app.clients.gemini_client import get_gemini_client
from app.core.settings import get_settings

logger = logging.getLogger(__name__)


def extract_claims(content: str) -> List[str]:
    """
    Extract 3-5 verifiable factual claims from content using Gemini AI.
    
    Uses a Gemini prompt to identify specific, factual claims that can be
    verified against external sources. Returns a list of claim strings.
    
    The function includes robust JSON parsing with fallback to heuristics
    if JSON parsing fails.
    
    Args:
        content: Raw text content to analyze (minimum ~50 chars)
    
    Returns:
        List of extracted claims (up to MAX_CLAIMS from settings)
    
    Examples:
        >>> content = "The Eiffel Tower is 330 meters tall. Paris was founded in 259 BC."
        >>> claims = extract_claims(content)
        >>> print(len(claims))  # 2
        >>> print(claims[0])    # The Eiffel Tower is 330 meters tall.
    """
    settings = get_settings()
    max_claims = settings.max_claims
    
    prompt = f"""Extract exactly {max_claims} specific, verifiable factual claims from the following content.
Each claim should be:
- A single factual statement (not an opinion)
- Specific and concrete (includes facts, numbers, dates, or attributions)
- Capable of being verified against external sources

Return the claims as a JSON array of strings ONLY. No explanations.
Example format:
```json
["Claim 1", "Claim 2", "Claim 3"]
```

Content:
{content}"""
    
    try:
        client = get_gemini_client()
        response_text = client.generate_text(prompt, temperature=0.3, max_tokens=512)
        
        # Parse JSON response
        claims = _parse_claims_json(response_text, max_claims)
        
        if claims:
            logger.info(f"Extracted {len(claims)} claims from content")
            return claims
        
    except Exception as e:
        logger.warning(f"Gemini claim extraction failed: {str(e)}, falling back to heuristics")
    
    # Fallback: heuristic extraction
    return _extract_claims_heuristic(content, max_claims)


def _parse_claims_json(response_text: str, max_claims: int) -> List[str]:
    """
    Parse JSON claims from Gemini response with error handling.
    
    Args:
        response_text: Raw response from Gemini
        max_claims: Maximum claims to return
    
    Returns:
        List of claims, or empty list if parsing fails
    """
    try:
        # Remove markdown code fences if present
        text = response_text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        text = text.strip()
        
        # Parse JSON
        claims_list = json.loads(text)
        
        # Validate it's a list of strings
        if not isinstance(claims_list, list):
            raise ValueError("JSON is not a list")
        
        claims = [str(c).strip() for c in claims_list if c]
        
        logger.debug(f"Parsed {len(claims)} claims from JSON")
        return claims[:max_claims]
    
    except (json.JSONDecodeError, ValueError, TypeError) as e:
        logger.debug(f"JSON parsing failed: {str(e)}")
        return []


def _extract_claims_heuristic(content: str, max_claims: int) -> List[str]:
    """
    Fallback heuristic extraction if Gemini or JSON parsing fails.
    Extracts sentences containing numbers, dates, or attribution keywords.
    
    Args:
        content: Text content to analyze
        max_claims: Maximum claims to extract
    
    Returns:
        List of extracted claims
    """
    claims = []
    sentences = content.split(".")
    keywords = ["said", "reported", "claimed", "stated", "announced", "found", "discovered",
                "published", "released", "revealed", "confirmed", "estimated", "reported that"]
    
    for sentence in sentences:
        sentence = sentence.strip()
        
        # Look for sentences with numbers/dates or attribution keywords
        has_number = any(char.isdigit() for char in sentence)
        has_keyword = any(word in sentence.lower() for word in keywords)
        
        if sentence and (has_number or has_keyword):
            claims.append(sentence)
    
    logger.info(f"Extracted {len(claims)} claims using heuristics (Gemini unavailable)")
    return claims[:max_claims]
