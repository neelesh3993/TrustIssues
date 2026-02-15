#!/usr/bin/env python3
"""Test the updated analyze endpoint with claim breakdown"""
from app.routes.analyze import analyze_content
from app.models.schemas import AnalysisRequest
import asyncio
import json


async def test_analyze():
    request = AnalysisRequest(
        url="https://example.com/test-article",
        content="""
        The economy grew by 3% last year. Unemployment fell to 4.2%. 
        The central bank increased interest rates by 0.5%.
        These measures were taken to combat inflation. Experts predict continued growth.
        Several economists believe this trend will persist through 2025.
        """,
        title="Economic Growth Report"
    )

    response = await analyze_content(request)

    print("=" * 70)
    print("ANALYSIS ENDPOINT TEST RESULTS")
    print("=" * 70)

    print(f"\n✓ Response Fields Check:")
    print(
        f"  - aiGenerationLikelihood: {response.aiGenerationLikelihood:.1f}%")
    print(f"  - credibilityScore: {response.credibilityScore:.1f}%")
    print(f"  - manipulationRisk: {response.manipulationRisk:.1f}%")
    print(f"  - claimBreakdown: {len(response.claimBreakdown)} claims")
    print(f"  - findings: {len(response.findings)} findings")
    print(f"  - sources: {len(response.sources)} sources")
    print(f"  - report: {len(response.report)} chars")

    if response.claimBreakdown:
        print(f"\n✓ Claim Breakdown Details:")
        for i, claim in enumerate(response.claimBreakdown, 1):
            print(f"  {i}. [{claim.status.upper()}] {claim.claim[:60]}...")
            if claim.sources:
                print(f"     Sources: {len(claim.sources)}")
    else:
        print(f"\n⚠ No claims in breakdown")

    print(f"\n✓ Sample Findings:")
    for finding in response.findings[:3]:
        print(f"  - {finding}")

    return response

if __name__ == "__main__":
    result = asyncio.run(test_analyze())
