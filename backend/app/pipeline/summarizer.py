"""
Analysis Summarizer
Generates human-readable summaries using Gemini AI.
"""

from app.clients.ai_client import get_ai_client
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


def generate_summary(
    content: str,
    claims: List[str],
    verification_results: List[Dict]
) -> str:
    """
    Generate a concise summary focused on key findings and recommendations.

    Args:
        content: Original content analyzed
        claims: Extracted claims
        verification_results: Results from verification pipeline

    Returns:
        Summary string (2-3 sentences)
    """
    if not verification_results:
        logger.warning("No verification results provided for summary")
        return _generate_fallback_summary(None, None, None)

    # Count verification statuses
    verified_count = sum(
        1 for r in verification_results if r.get("status") == "verified")
    disputed_count = sum(
        1 for r in verification_results if r.get("status") == "disputed")
    uncertain_count = sum(
        1 for r in verification_results if r.get("status") == "uncertain")

    # Get disputed claims for emphasis
    disputed_claims = [r.get("claim") for r in verification_results if r.get("status") == "disputed"]

    try:
        prompt = f"""Generate a concise, expert assessment (2-3 sentences max) focusing on key findings and recommendations.

CLAIM VERIFICATION SUMMARY:
- Verified: {verified_count}
- Disputed: {disputed_count}
- Uncertain: {uncertain_count}

{f'Disputed claims to highlight: {disputed_claims}' if disputed_claims else ''}

Provide:
1. KEY FINDING: Overall credibility assessment (HIGH/MIXED/LOW)
2. CRITICAL ISSUES: If there are disputed claims, what they are
3. RECOMMENDATION: What the reader should do (trust/verify further/be skeptical)

Be direct, clear, and concise. No hedging."""

        client = get_ai_client()
        summary = client.generate_text(prompt, temperature=0.3, max_tokens=200)
        
        if summary and summary.strip():
            logger.info("Summary generated successfully")
            return summary.strip()
        else:
            raise ValueError("Empty summary from AI")

    except Exception as e:
        logger.error(
            f"Summary generation failed: {str(e)}, using fallback")
        return _generate_fallback_summary(verified_count, disputed_count, uncertain_count)


def _format_evidence_summary(verification_results: List[Dict]) -> str:
    """
    Format verification results into a readable evidence summary.

    Args:
        verification_results: List of verification result dictionaries

    Returns:
        Formatted string with key findings
    """
    summary = ""
    verified = [r for r in verification_results if r.get("status") == "verified"]
    disputed = [r for r in verification_results if r.get("status") == "disputed"]

    if verified:
        summary += f"VERIFIED ({len(verified)}): "
        summary += ", ".join([v.get("claim")[:50] for v in verified[:2]])
        summary += "\n"

    if disputed:
        summary += f"DISPUTED ({len(disputed)}): "
        summary += ", ".join([d.get("claim")[:50] for d in disputed[:2]])
        summary += "\n"

    return summary if summary else "No claims analyzed."


def _generate_fallback_summary(
    verified_count: int = None,
    disputed_count: int = None,
    uncertain_count: int = None
) -> str:
    """
    Generate a fallback summary if Gemini is unavailable.

    Args:
        verified_count: Number of verified claims (optional)
        disputed_count: Number of disputed claims (optional)
        uncertain_count: Number of uncertain claims (optional)

    Returns:
        Fallback summary string
    """
    if verified_count is None:
        return (
            "Analysis could not be completed due to a technical issue. "
            "Please ensure API keys are configured and try again. "
            "See README.md for setup instructions."
        )

    total = (verified_count or 0) + \
        (disputed_count or 0) + (uncertain_count or 0)

    if total == 0:
        return "No claims were extracted for analysis."

    # Determine overall credibility based on counts
    if verified_count and verified_count / total >= 0.7:
        credibility = "HIGH"
    elif disputed_count and disputed_count / total >= 0.5:
        credibility = "LOW"
    else:
        credibility = "MIXED"

    parts = []
    if verified_count:
        parts.append(f"{verified_count} verified claim(s)")
    if disputed_count:
        parts.append(f"{disputed_count} disputed claim(s)")
    if uncertain_count:
        parts.append(f"{uncertain_count} uncertain claim(s)")

    claims_str = ", ".join(parts)

    fallback = (
        f"Content analysis identified: {claims_str}. "
        f"Overall credibility assessment: {credibility}. "
        f"Recommend independent verification of disputed claims."
    )

    logger.info(f"Using fallback summary: {fallback}")
    return fallback
