from pydantic import BaseModel, Field
from typing import List, Optional


# ===== LEGACY MODELS (kept for backward compatibility) =====
class AnalyzeRequest(BaseModel):
    text: str


class Claim(BaseModel):
    claim: str
    status: str
    sources: list[str]


class AnalyzeResponse(BaseModel):
    credibility_score: int
    claims: list[Claim]
    summary: str


# ===== CHROME EXTENSION MODELS =====
class AnalysisRequest(BaseModel):
    """Request model for content analysis from Chrome extension"""
    url: str = Field(..., description="URL of the analyzed page")
    content: str = Field(..., description="Text content extracted from page")
    title: str = Field(..., description="Page title")
    images: Optional[List[str]] = Field(
        default=None, description="Optional base64-encoded images for analysis"
    )


class Source(BaseModel):
    """Source reference for credibility claims"""
    name: str = Field(..., description="Source name or domain")
    headline: str = Field(..., description="Source headline or summary")
    url: Optional[str] = Field(None, description="Source URL")
    snippet: Optional[str] = Field(None, description="Source snippet")
    status: str = Field(...,
                        description="Verification status (verified/disputed/uncertain)")


class ClaimDetail(BaseModel):
    """Detailed information about a verified claim"""
    claim: str = Field(..., description="The claim text")
    status: str = Field(...,
                        description="Verification status (verified/disputed/uncertain)")
    rationale: Optional[str] = Field(
        None, description="Explanation for the verification status"
    )
    sources: List[Source] = Field(
        default_factory=list, description="Sources supporting/contradicting this claim"
    )


class AnalysisResponse(BaseModel):
    """Response model for content analysis"""
    aiGenerationLikelihood: float = Field(
        ..., description="Probability content is AI-generated (0-100%)"
    )
    credibilityScore: float = Field(
        ..., description="Overall credibility score (0-100%)"
    )
    manipulationRisk: float = Field(
        ..., description="Risk of content manipulation (0-100%)"
    )
    claimBreakdown: List[ClaimDetail] = Field(
        default_factory=list, description="Detailed breakdown of verified claims"
    )
    findings: List[str] = Field(
        default_factory=list, description="Key findings from analysis")
    sources: List[Source] = Field(
        default_factory=list, description="Supporting/contradicting sources"
    )
    report: str = Field(..., description="Detailed analysis report")
