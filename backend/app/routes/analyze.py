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
        ai_likelihood = _calculate_ai_likelihood(request.content)
        manipulation_risk = _calculate_manipulation_risk(request.content)

        # Check for low-credibility sources (user-generated content)
        source_url = request.url.lower() if request.url else ""
        credibility_penalty = _get_source_credibility_penalty(source_url)

        credibility_score = _calculate_credibility_integrated(
            verification_results, ai_likelihood, manipulation_risk, credibility_penalty)
        findings = _extract_findings(verification_results)
        sources = _format_sources(verification_results)
        claim_breakdown = _format_claims(verification_results)

        response = AnalysisResponse(
            aiGenerationLikelihood=ai_likelihood,
            credibilityScore=credibility_score,
            manipulationRisk=manipulation_risk,
            claimBreakdown=claim_breakdown,
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


def _get_source_credibility_penalty(url: str) -> float:
    """
    Determine credibility penalty based on source domain.

    User-generated content sites and opinion forums should have lower credibility ceilings.

    Args:
        url: The page URL

    Returns:
        Penalty multiplier (0.0-1.0) where 1.0 = no penalty, 0.2 = 80% penalty
    """
    url_lower = url.lower()

    # Low-credibility sources: user-generated or opinion-based
    # These should have credibility capped well below 50
    low_credibility_domains = [
        'quora.com',
        'reddit.com',
        'medium.com',
        'stackoverflow.com',
        'twitter.com',
        'x.com',
        'facebook.com',
        'instagram.com',
        'tiktok.com',
        'threads.net',
        'bluesky.social',
        'mastodon.',
        'substack.com',
        'patreon.com',
        'wordpress.com',  # Personal blogs
        'blogger.com',    # Personal blogs
        'wix.com',        # Personal sites
        '.substack.',     # Substack newsletters
        'blog.',          # Generic blogs
    ]

    # Check if URL matches low-credibility domain
    for domain in low_credibility_domains:
        if domain in url_lower:
            logger.debug(f"Detected low-credibility source: {domain}")
            return 0.25  # 75% penalty - max credibility will be ~25

    # Medium-credibility sources: opinion journalism, blogs
    medium_credibility_domains = [
        'medium.com/p/',  # Medium published articles (better than blog)
        'substack.com/p/',  # Substack articles
    ]

    for domain in medium_credibility_domains:
        if domain in url_lower:
            logger.debug(f"Detected medium-credibility source: {domain}")
            return 0.40  # 60% penalty

    # News and reputable sources - no penalty
    return 1.0  # Full credibility possible


def _calculate_credibility_integrated(verification_results: List[dict], ai_likelihood: float, manipulation_risk: float, source_penalty: float = 1.0) -> float:
    """
    Calculate credibility by integrating verification results with AI likelihood and manipulation risk.

    Logic:
    - Low AI generation + Low manipulation + Good verification = HIGH credibility
    - High AI generation OR High manipulation = LOWER credibility
    - Authentic human-written content with low manipulation = strong credibility signal
    - User-generated content (Quora, Reddit, etc.) has lower credibility ceiling

    Args:
        verification_results: List of verification results
        ai_likelihood: AI generation likelihood (0-100)
        manipulation_risk: Manipulation risk score (0-100)
        source_penalty: Multiplier for source credibility (0.0-1.0)

    Returns:
        Integrated credibility score (0-100)
    """
    # Factor 1: Verification strength (increased to 50% - most important)
    # This captures claim verification, source authority, agreement
    verification_strength = _calculate_credibility(verification_results)

    # Factor 2: AI authenticity (inverted - low AI = high trust)
    # Reduced from 40% to 25% - less important than verification
    ai_authenticity = 100 - ai_likelihood  # 0-100: higher is better

    # Factor 3: Manipulation resistance (inverted - low manipulation = high trust)
    # Kept at 25% - important but not as important as verification
    manipulation_resistance = 100 - manipulation_risk  # 0-100: higher is better

    # Integrated formula: Prioritize verification for credibility
    # 50% Verification + 25% AI Authenticity + 25% Non-manipulation
    integrated_score = (
        verification_strength * 0.50 +
        ai_authenticity * 0.25 +
        manipulation_resistance * 0.25
    )

    # Apply source-based penalty (e.g., Quora user content gets capped)
    # This ensures user-generated content is never rated as highly credible
    final_score = integrated_score * source_penalty

    logger.debug(
        f"Integrated Credibility: "
        f"verification={verification_strength:.1f}% (50% weight), "
        f"ai_authenticity={ai_authenticity:.1f}% (25% weight), "
        f"manipulation_resistance={manipulation_resistance:.1f}% (25% weight), "
        f"before_penalty={integrated_score:.1f}%, "
        f"penalty={source_penalty:.2f}x, "
        f"final_score={final_score:.1f}%"
    )

    return max(0.0, min(100.0, final_score))


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
        "corrupt", "evil", "disaster", "exposed", "amazing",
        "extremely", "absolutely", "ridiculous", "disgusting"
    ]
    emotional_count = sum(
        content.lower().count(w) for w in emotional_words)
    emotional_score = min(100, emotional_count * 12)

    # ---- Layer 2: Certainty language (false confidence) ----
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

    # ---- Layer 4: Subjective opinion markers (NEW) ----
    # High presence of opinion language indicates speculative/unverified content
    opinion_markers = [
        "i think", "i believe", "i would say", "in my opinion",
        "in my experience", "from my perspective", "i would argue",
        "i personally", "i feel", "i think that", "arguably",
        "it seems", "it appears", "one could say", "one might argue"
    ]
    opinion_count = sum(
        1 for marker in opinion_markers if marker in content.lower())
    # Increased multiplier - high opinion content = high manipulation risk
    # Allow scores to go above 100 when there's extreme opinion language
    opinion_score = min(110, opinion_count * 25)

    # ---- Layer 5: Speculation and uncertainty markers (NEW) ----
    # These indicate unverified claims and speculation
    speculation_markers = [
        "maybe", "probably", "possibly", "perhaps", "might be",
        "could be", "seems like", "appears to be", "supposedly",
        "allegedly", "supposedly", "so called", "claimed"
    ]
    speculation_count = sum(
        1 for marker in speculation_markers if marker in content.lower())
    # Increased multiplier - speculation = high manipulation risk
    speculation_score = min(100, speculation_count * 15)

    # ---- Layer 6: Punctuation pressure ----
    exclamations = content.count("!")
    caps_words = sum(1 for w in words if w.isupper() and len(w) > 3)
    # Questions indicate uncertainty/engagement bait
    question_marks = content.count("?") * 5
    punctuation_score = min(
        100,
        exclamations * 4 + caps_words * 2 + question_marks
    )

    manipulation = (
        0.05 * emotional_score +
        0.05 * certainty_score +
        0.05 * conspiracy_score +
        0.60 * opinion_score +
        0.20 * speculation_score +
        0.05 * punctuation_score
    )

    logger.debug(
        f"Manipulation Risk Breakdown: "
        f"emotional={emotional_score:.1f}, "
        f"certainty={certainty_score:.1f}, "
        f"conspiracy={conspiracy_score:.1f}, "
        f"opinion={opinion_score:.1f}, "
        f"speculation={speculation_score:.1f}, "
        f"punctuation={punctuation_score:.1f}, "
        f"final={manipulation:.1f}"
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


def _format_claims(verification_results: List[dict]) -> List:
    """
    Format verification results as ClaimDetail objects for API response.

    Args:
        verification_results: List of verification result dicts

    Returns:
        List of ClaimDetail objects
    """
    from app.models.schemas import ClaimDetail, Source

    claims = []

    for result in verification_results:
        # Format sources for this claim
        claim_sources = []
        for source in result.get("sources", []):
            source_obj = Source(
                name=source.get("name", "Unknown"),
                headline=source.get("headline", ""),
                url=source.get("url"),
                snippet=source.get("snippet"),
                status=result.get("status", "uncertain")
            )
            claim_sources.append(source_obj)

        claim_detail = ClaimDetail(
            claim=result.get("claim", ""),
            status=result.get("status", "uncertain"),
            rationale=result.get("rationale", ""),
            sources=claim_sources
        )
        claims.append(claim_detail)

    return claims
