"""
Trust Issues Backend API
Analyzes web content for credibility and AI generation likelihood
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Trust Issues API",
    description="Web content authenticity and credibility analysis",
    version="1.0.0"
)

# CORS configuration - allow extension
allowed_origins = [
    "chrome-extension://*",
    "http://localhost:3000",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Request/Response Models
# ============================================================================

class AnalysisRequest(BaseModel):
    url: str
    content: str
    title: str

class Source(BaseModel):
    name: str
    headline: str
    status: str

class AnalysisResponse(BaseModel):
    aiGenerationLikelihood: float
    credibilityScore: float
    manipulationRisk: float
    findings: list[str]
    sources: list[Source]
    report: str

# ============================================================================
# Routes
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.post("/api/analyze", response_model=AnalysisResponse)
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
        
        # Import pipeline modules
        from pipeline.claim_extractor import extract_claims
        from pipeline.verifier import verify_claims
        from pipeline.summarizer import generate_summary
        
        # Run analysis pipeline
        logger.info(f"Analyzing: {request.url}")
        
        # Step 1: Extract claims
        claims = extract_claims(request.content)
        
        # Step 2: Verify claims against sources
        verification_results = verify_claims(claims)
        
        # Step 3: Generate summary
        summary = generate_summary(request.content, claims, verification_results)
        
        # Build response
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

# ============================================================================
# Helper Functions (Placeholders)
# ============================================================================

def calculate_ai_likelihood(content: str) -> float:
    """
    Calculate likelihood of AI-generated content
    (Implement with NLP model)
    """
    # Placeholder logic
    return 42.0

def calculate_credibility(verification_results: dict) -> float:
    """
    Calculate credibility score based on verification results
    (Implement with verification logic)
    """
    # Placeholder logic
    return 65.0

def calculate_manipulation_risk(content: str) -> float:
    """
    Calculate risk of content manipulation
    (Implement with linguistic analysis)
    """
    # Placeholder logic
    return 35.0

def extract_findings(content: str, claims: list) -> list[str]:
    """
    Extract key findings from analysis
    """
    return [
        "AI-generated writing patterns detected",
        "Claim partially supported by external sources",
        "Emotional language present in headline",
        "Image context could not be verified",
    ]

def format_sources(verification_results: dict) -> list[Source]:
    """
    Format verification results as sources
    """
    sources = [
        {"name": "Reuters", "headline": "Fact-check database cross-referenced", "status": "verified"},
        {"name": "BBC News", "headline": "Related reporting found — partial match", "status": "partial"},
        {"name": "Associated Press", "headline": "Wire service corroboration pending", "status": "pending"},
        {"name": "Snopes", "headline": "No matching claim investigation found", "status": "not_found"},
        {"name": "PolitiFact", "headline": "Claim rating unavailable", "status": "unavailable"},
    ]
    
    return [Source(**s) for s in sources]

# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return {
        "status": "error",
        "message": exc.detail,
        "status_code": exc.status_code
    }

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}")
    return {
        "status": "error",
        "message": "Internal server error",
        "status_code": 500
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000))
    )
