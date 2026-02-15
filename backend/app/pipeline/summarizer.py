"""
Analysis Summarizer
Generates human-readable summaries using Gemini AI.
"""

from app.clients.ai_client import get_ai_client
import logging
from typing import List, Dict
from app.clients.gemini_client import get_gemini_client

logger = logging.getLogger(__name__)


def generate_summary(
    content: str,
    claims: List[str],
    verification_results: List[Dict]
) -> str:
    """
    Generate a human-readable summary of the analysis using Gemini.

    The summary is grounded in the verification results and includes:
    - Overview of verified/disputed/uncertain claims
    - Key findings
    - Recommendations

    Includes fallback to manual summary if Gemini fails.

    Args:
        content: Original content analyzed
        claims: Extracted claims
        verification_results: Results from verification pipeline

    Returns:
        Summary string (2-4 sentences)

    Examples:
        >>> content = "Climate change is real and accelerating."
        >>> claims = ["Climate change is accelerating"]
        >>> results = [{"status": "verified", "rationale": "Supported by scientific consensus"}]
        >>> summary = generate_summary(content, claims, results)
        >>> print(summary)
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

    # Create evidence summary for Gemini
    evidence_summary = _format_evidence_summary(verification_results)

    try:
        prompt = f"""Analyze the following content analysis results and generate a concise, expert summary.
The summary should be grounded ONLY in the provided verification results.

ORIGINAL CONTENT:
{content[:500]}...

VERIFICATION RESULTS SUMMARY:
- Verified claims: {verified_count}
- Disputed claims: {disputed_count}
- Uncertain claims: {uncertain_count}

DETAILED EVIDENCE:
{evidence_summary}

Generate a 2-4 sentence expert summary that:
1. Explains the overall credibility based on verified/disputed/uncertain counts
2. Highlights any key disputed claims (if any)
3. Recommends next steps

Be direct and avoid hedging language."""

        client = get_ai_client()
        summary = client.generate_text(prompt, temperature=0.5, max_tokens=256)

        logger.info("Summary generated successfully")
        return summary.strip()

    except Exception as e:
        logger.error(
            f"Gemini summary generation failed: {str(e)}, using fallback")
        return _generate_fallback_summary(verified_count, disputed_count, uncertain_count)


def _format_evidence_summary(verification_results: List[Dict]) -> str:
    """
    Format verification results into a readable evidence summary for Gemini.

    Args:
        verification_results: List of verification result dictionaries

    Returns:
        Formatted string for Gemini prompt
    """
    summary = ""

    for i, result in enumerate(verification_results, 1):
        claim = result.get("claim", "Unknown")
        status = result.get("status", "uncertain")
        rationale = result.get("rationale", "No information")
        sources = result.get("sources", [])

        summary += f"{i}. [{status.upper()}] {claim}\n"
        summary += f"   Reason: {rationale}\n"

        if sources:
            summary += f"   Sources: {len(sources)} retrieved\n"

        summary += "\n"

    return summary


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
