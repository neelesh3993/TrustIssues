"""
Models Module
Pydantic models for request/response validation
"""

from pydantic import BaseModel
from typing import Optional

class AnalysisRequest(BaseModel):
    """Request model for content analysis"""
    url: str
    content: str
    title: str

class Source(BaseModel):
    """Source verification result"""
    name: str
    headline: str
    status: str

class AnalysisResponse(BaseModel):
    """Response model for analysis results"""
    aiGenerationLikelihood: float
    credibilityScore: float
    manipulationRisk: float
    findings: list[str]
    sources: list[Source]
    report: str
