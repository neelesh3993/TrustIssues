"""
API Routes
Main endpoint handlers
"""

from fastapi import APIRouter, HTTPException
from app.models.schemas import AnalysisRequest, AnalysisResponse
from app.pipeline.claim_extractor import extract_claims
from app.pipeline.verifier import verify_claims
from app.pipeline.summarizer import generate_summary
import logging

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
        from app.main import (
            calculate_ai_likelihood,
            calculate_credibility,
            calculate_manipulation_risk,
            extract_findings,
            format_sources
        )
        
        response = AnalysisResponse(
            aiGenerationLikelihood=calculate_ai_likelihood(request.content),
            credibilityScore=calculate_credibility(verification_results),
            manipulationRisk=calculate_manipulation_risk(request.content),
            findings=extract_findings(request.content, claims),
            sources=format_sources(verification_results),
            report=summary
        )
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )
