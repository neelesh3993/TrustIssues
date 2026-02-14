"""
Claim Verifier
Verifies claims against news sources using Gemini AI and NewsAPI.
"""

import json
import logging
from typing import List, Dict, Optional
from app.clients.gemini_client import get_gemini_client
from app.clients.news_client import search_news_with_fallback
from app.core.settings import get_settings

logger = logging.getLogger(__name__)


def verify_claims(claims: List[str]) -> List[Dict]:
    """
    Verify claims by retrieving evidence from NewsAPI and using Gemini for reasoning.
    
    For each claim:
    1. Searches for supporting/contradicting evidence using NewsAPI
    2. Uses Gemini to classify as: "verified" | "disputed" | "uncertain"
    3. Returns structured evidence with sources
    
    Args:
        claims: List of claims to verify
    
    Returns:
        List of verification result dictionaries with structure:
        {
            "claim": str,
            "status": "verified" | "disputed" | "uncertain",
            "rationale": str (1-2 sentences grounded in sources),
            "sources": [
                {
                    "name": str,
                    "headline": str,
                    "url": str,
                    "snippet": str,
                    "publishedAt": str
                }
            ]
        }
    
    Examples:
        >>> claims = ["Paris is the capital of France"]
        >>> results = verify_claims(claims)
        >>> print(results[0]["status"])  # "verified"
    """
    if not claims:
        logger.info("No claims to verify")
        return []
    
    settings = get_settings()
    verification_results = []
    
    for claim in claims:
        result = _verify_single_claim(claim)
        verification_results.append(result)
    
    logger.info(
        f"Verification complete: "
        f"verified={sum(1 for r in verification_results if r['status'] == 'verified')}, "
        f"disputed={sum(1 for r in verification_results if r['status'] == 'disputed')}, "
        f"uncertain={sum(1 for r in verification_results if r['status'] == 'uncertain')}"
    )
    
    return verification_results


def _verify_single_claim(claim: str) -> Dict:
    """
    Verify a single claim using NewsAPI retrieval and Gemini reasoning.
    
    Args:
        claim: The claim to verify
    
    Returns:
        Verification result dictionary
    """
    # Step 1: Retrieve supporting/contradicting evidence
    logger.debug(f"Retrieving evidence for claim: {claim}")
    
    sources = search_news_with_fallback(claim)
    
    # Prepare source snippets for Gemini
    source_text = ""
    if sources:
        source_text = "Retrieved evidence:\n"
        for i, source in enumerate(sources, 1):
            source_text += (
                f"{i}. [{source['name']}] {source['headline']}\n"
                f"   {source['snippet']}\n"
                f"   URL: {source['url']}\n\n"
            )
    else:
        source_text = "No supporting evidence found from reliable news sources.\n"
    
    # Step 2: Use Gemini to classify the claim
    try:
        result = _classify_claim_with_gemini(claim, source_text, sources)
        return result
    
    except Exception as e:
        logger.error(f"Gemini verification failed for claim: {str(e)}, marking uncertain")
        return {
            "claim": claim,
            "status": "uncertain",
            "rationale": "Could not retrieve verification sources due to technical error. Manual verification recommended.",
            "sources": sources[:3] if sources else []
        }


def _classify_claim_with_gemini(claim: str, source_text: str, sources: List[Dict]) -> Dict:
    """
    Use Gemini to classify a claim based on retrieved evidence.
    
    Args:
        claim: The claim to classify
        source_text: Formatted evidence from NewsAPI
        sources: Raw source list for output
    
    Returns:
        Classification result with status and rationale
    """
    prompt = f"""You are a fact-checking expert. Classify the following claim as VERIFIED, DISPUTED, or UNCERTAIN based ONLY on the provided evidence.

CLAIM: {claim}

EVIDENCE:
{source_text}

Respond with ONLY a JSON object (no markdown, no explanation):
{{
  "status": "verified" or "disputed" or "uncertain",
  "rationale": "1-2 sentence explanation grounded ONLY in the provided evidence, or 'No evidence found' if none provided"
}}

IMPORTANT: Do NOT hallucinate sources. Only cite what is provided above."""
    
    try:
        client = get_gemini_client()
        response_text = client.generate_text(prompt, temperature=0.2, max_tokens=256)
        
        # Parse JSON response
        parsed = _parse_classification_json(response_text)
        
        status = parsed.get("status", "uncertain").lower()
        if status not in ["verified", "disputed", "uncertain"]:
            status = "uncertain"
        
        result = {
            "claim": claim,
            "status": status,
            "rationale": parsed.get("rationale", "Could not determine verification status."),
            "sources": sources[:3] if sources else []  # Include top 3 sources
        }
        
        logger.debug(f"Claim classified as {status}: {claim}")
        return result
    
    except Exception as e:
        logger.error(f"Gemini classification failed: {str(e)}")
        raise


def _parse_classification_json(response_text: str) -> Dict:
    """
    Parse classification JSON from Gemini response.
    
    Args:
        response_text: Raw response from Gemini
    
    Returns:
        Parsed classification dictionary
    """
    try:
        # Remove markdown code fences if present
        text = response_text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        text = text.strip()
        
        parsed = json.loads(text)
        return parsed
    
    except (json.JSONDecodeError, ValueError) as e:
        logger.warning(f"Failed to parse classification JSON: {str(e)}")
        logger.debug(f"Response: {response_text}")
        # Return default uncertain response
        return {
            "status": "uncertain",
            "rationale": "Could not retrieve verification sources."
        }
