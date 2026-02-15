"""
Claim Verifier
Verifies claims against news sources using Gemini AI and NewsAPI.
"""

import json
import logging
from typing import List, Dict, Optional
from app.clients.ai_client import get_ai_client
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
    claims_to_verify = claims[: settings.max_claims]

    for claim in claims_to_verify:
        result = _verify_single_claim_ai(claim)
        verification_results.append(result)

    logger.info(
        f"Verification complete: "
        f"verified={sum(1 for r in verification_results if r['status'] == 'verified')}, "
        f"disputed={sum(1 for r in verification_results if r['status'] == 'disputed')}, "
        f"uncertain={sum(1 for r in verification_results if r['status'] == 'uncertain')}"
    )

    return verification_results


def _verify_single_claim_ai(claim: str) -> Dict:
    """
    Use the Gemini AI model to verify a claim, reasoning with news evidence.

    Steps:
    1. Search for news evidence using NewsAPI
    2. Format evidence for AI analysis
    3. Use Gemini to classify as verified/disputed/uncertain
    4. Return structured result with sources
    """
    try:
        # Step 1: Get news evidence
        logger.info(f"Verifying claim: {claim}")
        sources = search_news_with_fallback(claim)

        # Step 2: Format evidence for Gemini
        source_text = ""
        if sources:
            logger.info(f"Found {len(sources)} sources for claim verification")
            source_text = "Retrieved evidence:\n"
            for i, source in enumerate(sources[:5], 1):
                source_text += (
                    f"{i}. [{source.get('name', 'Unknown')}] {source.get('headline', 'No headline')}\n"
                    f"   {source.get('snippet', 'No snippet')}\n"
                    f"   URL: {source.get('url', 'No URL')}\n\n"
                )
        else:
            logger.warning(f"No news sources found for claim: {claim}")
            source_text = "No supporting evidence found from news sources. Use your own knowledge and reasoning.\n"

        # Step 3: Use Gemini to classify the claim
        result = _classify_claim_with_gemini(claim, source_text, sources)
        return result

    except Exception as e:
        logger.error(
            f"Error verifying claim '{claim}': {str(e)}", exc_info=True)
        return {
            "claim": claim,
            "status": "uncertain",
            "rationale": f"Verification error: {str(e)}. Manual verification recommended.",
            "sources": []
        }


def _classify_claim_with_gemini(claim: str, source_text: str, sources: List[Dict]) -> Dict:
    """
    Use Gemini to classify a claim based on evidence or own knowledge.

    Args:
        claim: The claim to classify
        source_text: Formatted evidence from NewsAPI (or empty if none)
        sources: Raw source list for output

    Returns:
        Classification result with status and rationale
    """
    prompt = f"""You are a fact-checking expert. Classify the following claim as VERIFIED, DISPUTED, or UNCERTAIN.

If news evidence is provided, use it. If not, use your own knowledge and reasoning to make a decision.
Be decisive: only use UNCERTAIN if the claim is truly ambiguous or unknowable.

CLAIM: {claim}

EVIDENCE:
{source_text if source_text.strip() else "No news sources available. Use your own knowledge."}

Respond with ONLY a JSON object (no markdown, no explanation):
{{
  "status": "verified" or "disputed" or "uncertain",
  "rationale": "1-2 sentence explanation"
}}

Be specific and direct."""

    try:
        client = get_ai_client()
        logger.debug(f"Calling Gemini to classify claim: {claim[:60]}...")
        response_text = client.generate_text(
            prompt, temperature=0.2, max_tokens=256)

        logger.debug(f"Gemini response: {response_text}")

        # Parse JSON response
        parsed = _parse_classification_json(response_text)

        status = parsed.get("status", "uncertain").lower()
        if status not in ["verified", "disputed", "uncertain"]:
            logger.warning(
                f"Invalid status from Gemini: {status}, defaulting to uncertain")
            status = "uncertain"

        result = {
            "claim": claim,
            "status": status,
            "rationale": parsed.get("rationale", "Could not determine verification status."),
            "sources": sources[:3] if sources else []  # Include top 3 sources
        }

        logger.info(f"Claim classified as {status}: {claim[:60]}...")
        return result

    except Exception as e:
        logger.error(f"Gemini classification failed: {str(e)}", exc_info=True)
        return {
            "claim": claim,
            "status": "uncertain",
            "rationale": f"AI verification failed: {str(e)}. Please verify manually.",
            "sources": sources[:3] if sources else []
        }


def _parse_classification_json(response_text: str) -> Dict:
    """
    Parse classification JSON from AI response with robust error handling.

    Args:
        response_text: Raw response from AI

    Returns:
        Parsed classification dictionary or safe default
    """
    try:
        # Remove markdown code fences if present
        text = response_text.strip()
        if text.startswith("```"):
            # Extract content between markdown fences
            parts = text.split("```")  # Split by triple backticks
            if len(parts) > 1:
                text = parts[1]  # Get the content between fences
            if text.startswith("json"):
                text = text[4:]  # Remove 'json' language tag
        
        text = text.strip()
        
        # Try to parse JSON
        parsed = json.loads(text)
        
        # Validate required fields
        if "status" in parsed and "rationale" in parsed:
            return parsed
        else:
            logger.warning("Parsed JSON missing required fields")
            return {
                "status": "uncertain",
                "rationale": "Could not parse AI response completely."
            }

    except (json.JSONDecodeError, ValueError, AttributeError) as e:
        logger.warning(f"Failed to parse classification JSON: {str(e)}")
        logger.debug(f"Raw response: {response_text[:200]}...")
        # Return safe default
        return {
            "status": "uncertain",
            "rationale": "Could not parse AI response. Please verify manually."
        }
