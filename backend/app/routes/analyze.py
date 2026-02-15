"""
API Routes
Main endpoint handlers
"""
import statistics
from collections import Counter
import logging
import re
from typing import List
from fastapi import APIRouter, HTTPException
from app.models.schemas import AnalysisRequest, AnalysisResponse, Source
from app.pipeline.claim_extractor import extract_claims
from app.pipeline.verifier import verify_claims
from app.pipeline.summarizer import generate_summary
from app.core.settings import validate_required_keys
from app.clients.news_client import search_news_with_fallback

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["analysis"])


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_content(request: AnalysisRequest):
    """
    Analyze webpage content for credibility and AI-generation likelihood

    Args:
        request: AnalysisRequest with url, content, and title

    Returns:
        AnalysisResponse with scores, findings, and sources
    """
    try:
        # Validate required API keys are configured
        validate_required_keys()

    except ValueError as e:
        logger.error(f"Configuration error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    try:
        if not request.content or len(request.content.strip()) < 50:
            raise HTTPException(
                status_code=400,
                detail="Content too short for analysis (minimum 50 characters)"
            )

        logger.info(f"Analyzing: {request.url}")

        # Step 1: Extract claims
        claims = extract_claims(request.content)

        # Step 2: Verify claims
        verification_results = verify_claims(claims)

        # Step 3: Generate summary
        summary = generate_summary(
            request.content, claims, verification_results)

        # Calculate scores
        credibility_score = _calculate_credibility(verification_results)
        findings = _extract_findings(verification_results)
        sources = _format_sources(verification_results)

        response = AnalysisResponse(
            aiGenerationLikelihood=_calculate_ai_likelihood(request.content),
            credibilityScore=credibility_score,
            manipulationRisk=_calculate_manipulation_risk(request.content),
            findings=findings,
            sources=sources,
            report=summary
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


def _calculate_credibility(verification_results: List[dict]) -> float:
    if not verification_results:
        return 50.0

    total = len(verification_results)

    # ---- Layer 1: Veracity Strength (40%) ----
    weight_map = {
        "verified": 1.0,
        "uncertain": 0.2,
        "disputed": -1.0
    }

    veracity_raw = sum(weight_map.get(r.get("status"), 0)
                       for r in verification_results) / total
    veracity_score = ((veracity_raw + 1) / 2) * 100

    # ---- Layer 2: Source Authority (25%) ----
    HIGH_TIER = {"reuters", "ap", "bbc", "new york times"}
    MID_TIER = {"cnn", "fox", "guardian", "washington post"}

    authority_scores = []

    for result in verification_results:
        for s in result.get("sources", []):
            name = s.get("name", "").lower()

            if any(h in name for h in HIGH_TIER):
                authority_scores.append(1.0)
            elif any(m in name for m in MID_TIER):
                authority_scores.append(0.6)
            elif name:
                authority_scores.append(0.3)
            else:
                authority_scores.append(0.2)

    source_authority = (
        (sum(authority_scores) / len(authority_scores)) * 100
        if authority_scores else 50
    )

    # ---- Layer 3: Cross-source agreement (20%) ----
    outlets = set()
    for result in verification_results:
        for s in result.get("sources", []):
            outlets.add(s.get("name"))

    agreement_score = min(100, (len(outlets) / max(total, 1)) * 100)

    # ---- Layer 4: Claim volume confidence (15%) ----
    volume_score = min(100, total * 12)

    credibility = (
        0.4 * veracity_score +
        0.25 * source_authority +
        0.2 * agreement_score +
        0.15 * volume_score
    )

    return max(0.0, min(100.0, credibility))


def _calculate_ai_likelihood(content: str) -> float:
    sentences = re.split(r'[.!?]+', content)
    sentences = [s.strip() for s in sentences if len(s.split()) > 3]

    if not sentences:
        return 40.0

    # ---- Layer 1: Sentence length variance ----
    lengths = [len(s.split()) for s in sentences]
    variance = statistics.variance(lengths) if len(lengths) > 1 else 0
    variance_score = max(0, min(100, 60 - variance))

    # ---- Layer 2: Lexical diversity ----
    words = re.findall(r'\w+', content.lower())
    unique_ratio = len(set(words)) / max(len(words), 1)
    diversity_score = (1 - unique_ratio) * 100

    # ---- Layer 3: Repetition detection ----
    phrase_counts = Counter([" ".join(words[i:i+3])
                             for i in range(len(words) - 2)])
    repeated = sum(1 for c in phrase_counts.values() if c > 2)
    repetition_score = min(100, repeated * 5)

    # ---- Layer 4: Structural uniformity ----
    avg_len = sum(lengths) / len(lengths)
    uniformity_score = max(0, 100 - abs(avg_len - 18) * 4)

    ai_score = (
        0.4 * variance_score +
        0.2 * diversity_score +
        0.2 * repetition_score +
        0.2 * uniformity_score
    )

    return max(0.0, min(100.0, ai_score))


def _calculate_manipulation_risk(content: str) -> float:
    words = content.split()
    total_words = len(words)

    # ---- Layer 1: Emotional intensity ----
    emotional_words = [
        "outrage", "shocking", "incredible", "unbelievable",
        "corrupt", "evil", "disaster", "exposed"
    ]
    emotional_count = sum(
        content.lower().count(w) for w in emotional_words)
    emotional_score = min(100, emotional_count * 12)

    # ---- Layer 2: Certainty language ----
    certainty_words = ["prove", "guarantee", "undeniable", "always", "never"]
    certainty_count = sum(content.lower().count(w)
                          for w in certainty_words)
    certainty_score = min(100, certainty_count * 10)

    # ---- Layer 3: Conspiracy phrasing ----
    conspiracy_patterns = [
        "they don't want you to know",
        "mainstream media won't",
        "hidden truth",
        "cover-up"
    ]
    conspiracy_score = 30 if any(
        p in content.lower() for p in conspiracy_patterns) else 0

    # ---- Layer 4: punctuation pressure ----
    exclamations = content.count("!")
    caps_words = sum(1 for w in words if w.isupper() and len(w) > 3)

    punctuation_score = min(
        100,
        exclamations * 4 + caps_words * 2
    )

    manipulation = (
        0.25 * emotional_score +
        0.25 * certainty_score +
        0.25 * conspiracy_score +
        0.25 * punctuation_score
    )

    return max(0.0, min(100.0, manipulation))


def _extract_key_phrases(content: str, num_phrases: int = 3) -> List[str]:
    """
    Extract key phrases/sentences from content for NewsAPI searches.

    Sanitizes phrases to remove punctuation and special characters that
    cause NewsAPI 400 errors.

    Args:
        content: Text content to analyze
        num_phrases: Number of phrases to extract

    Returns:
        List of cleaned key phrases for NewsAPI search
    """
    try:
        import re

        # Split into sentences
        sentences = content.replace(".", ".\n").split("\n")
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]

        if not sentences:
            return []

        # Extract longest/most substantial sentences (likely to contain key facts)
        sentences_by_length = sorted(
            sentences,
            key=lambda s: len(s.split()),
            reverse=True
        )

        # Take phrases with 5-20 words (good for search queries)
        key_phrases = []
        for sentence in sentences_by_length:
            words = sentence.split()
            if 5 <= len(words) <= 20:
                # Get first ~8 words as search phrase
                raw_phrase = " ".join(words[:8])

                # SANITIZE: Remove problematic characters for NewsAPI
                # Remove quotes, colons, parentheses, slashes, etc.
                cleaned_phrase = re.sub(r'["\':()\/\[\]\{\}]', '', raw_phrase)

                # Remove extra whitespace
                cleaned_phrase = " ".join(cleaned_phrase.split())

                # Skip if too short after cleaning
                if len(cleaned_phrase.split()) >= 3:
                    key_phrases.append(cleaned_phrase)

                if len(key_phrases) >= num_phrases:
                    break

        logger.debug(
            f"Extracted {len(key_phrases)} sanitized phrases for NewsAPI search")
        return key_phrases[:num_phrases]

    except Exception as e:
        logger.debug(f"Error extracting key phrases: {str(e)}")
        return []


def _extract_findings(verification_results: List[dict]) -> List[str]:
    """
    Extract key findings from verification results.

    Args:
        verification_results: List of verification result dicts

    Returns:
        List of finding strings
    """
    findings = []

    for result in verification_results:
        if result.get("status") == "disputed":
            findings.append(
                f"⚠️ DISPUTED: {result.get('claim', 'Unknown claim')}")
        elif result.get("status") == "verified":
            findings.append(
                f"✓ VERIFIED: {result.get('claim', 'Unknown claim')}")

    # Add summary finding
    verified_count = sum(
        1 for r in verification_results if r.get("status") == "verified")
    disputed_count = sum(
        1 for r in verification_results if r.get("status") == "disputed")
    total = len(verification_results)

    if total > 0:
        if verified_count / total >= 0.7:
            findings.insert(
                0, f"Majority of claims ({verified_count}/{total}) were verified.")
        elif disputed_count / total >= 0.5:
            findings.insert(
                0, f"Many claims ({disputed_count}/{total}) were disputed.")
        else:
            findings.insert(
                0, f"Mixed results: {verified_count} verified, {disputed_count} disputed, {total - verified_count - disputed_count} uncertain.")

    return findings if findings else ["No significant findings."]


def _format_sources(verification_results: List[dict]) -> List[Source]:
    """
    Format verification sources for API response.

    Args:
        verification_results: List of verification result dicts

    Returns:
        List of Source objects for AnalysisResponse
    """
    sources = []

    for result in verification_results:
        # Add sources from each verification result
        for source in result.get("sources", [])[:2]:  # Top 2 per claim
            source_obj = Source(
                name=source.get("name", "Unknown"),
                headline=source.get("headline", ""),
                status=result.get("status", "uncertain")
            )
            sources.append(source_obj)

    return sources
