"""
API Routes
Main endpoint handlers
"""

import logging
from typing import List
from fastapi import APIRouter, HTTPException
from app.models.schemas import AnalysisRequest, AnalysisResponse, Source
from app.pipeline.claim_extractor import extract_claims
from app.pipeline.verifier import verify_claims
from app.pipeline.summarizer import generate_summary
from app.core.settings import validate_required_keys

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
        summary = generate_summary(request.content, claims, verification_results)
        
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
    """
    Calculate credibility score from verification results.
    
    Args:
        verification_results: List of verification result dicts
    
    Returns:
        Credibility score 0-100
    """
    if not verification_results:
        return 50.0  # Neutral if no claims
    
    verified = sum(1 for r in verification_results if r.get("status") == "verified")
    disputed = sum(1 for r in verification_results if r.get("status") == "disputed")
    uncertain = sum(1 for r in verification_results if r.get("status") == "uncertain")
    
    total = len(verification_results)
    
    # Formula: 100 * verified - 50 * disputed + 0 * uncertain, normalized to 0-100
    score = (verified * 100 - disputed * 50) / max(total, 1)
    return max(0.0, min(100.0, score))


def _calculate_ai_likelihood(content: str) -> float:
    """
    Estimate likelihood content is AI-generated based on length and patterns.
    
    Args:
        content: Text content to analyze
    
    Returns:
        Likelihood score 0-100
    """
    # Placeholder: base on content characteristics
    # Could be enhanced with actual ML model
    
    # Very short content less likely to be AI-generated
    if len(content) < 100:
        return 20.0
    elif len(content) < 500:
        return 30.0
    
    # Moderate content
    return 40.0


def _calculate_manipulation_risk(content: str) -> float:
    """
    Estimate manipulation risk based on content characteristics.
    
    Args:
        content: Text content to analyze
    
    Returns:
        Risk score 0-100
    """
    # Placeholder: base on linguistic patterns
    risk = 45.0
    
    # Increase risk if content has many exclamation marks or all caps
    exclamation_count = content.count("!")
    caps_words = sum(1 for word in content.split() if word.isupper() and len(word) > 2)
    
    if exclamation_count > len(content) / 100:
        risk += 10.0
    if caps_words > len(content.split()) * 0.1:
        risk += 10.0
    
    return min(100.0, risk)


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
            findings.append(f"⚠️ DISPUTED: {result.get('claim', 'Unknown claim')}")
        elif result.get("status") == "verified":
            findings.append(f"✓ VERIFIED: {result.get('claim', 'Unknown claim')}")
    
    # Add summary finding
    verified_count = sum(1 for r in verification_results if r.get("status") == "verified")
    disputed_count = sum(1 for r in verification_results if r.get("status") == "disputed")
    total = len(verification_results)
    
    if total > 0:
        if verified_count / total >= 0.7:
            findings.insert(0, f"Majority of claims ({verified_count}/{total}) were verified.")
        elif disputed_count / total >= 0.5:
            findings.insert(0, f"Many claims ({disputed_count}/{total}) were disputed.")
        else:
            findings.insert(0, f"Mixed results: {verified_count} verified, {disputed_count} disputed, {total - verified_count - disputed_count} uncertain.")
    
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
