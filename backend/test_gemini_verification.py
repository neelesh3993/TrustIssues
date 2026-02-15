#!/usr/bin/env python3
"""
Test claim verification to ensure Gemini is being called
"""
import logging
from app.pipeline.claim_extractor import extract_claims
from app.pipeline.verifier import verify_claims

# Enable debug logging to see Gemini calls
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Sample content with clear claims
content = """
Iran's foreign ministry said on Saturday that potential energy, mining and aircraft 
deals could be on the table in talks with the United States. The country signals 
flexibility on nuclear issues. Talks are scheduled to hold further discussions in Geneva 
on Tuesday. Iranian diplomats reported that negotiations could deliver economic benefits 
for both sides in areas with high and quick economic returns.
"""

print("=" * 70)
print("CLAIM VERIFICATION TEST - GEMINI INTEGRATION")
print("=" * 70)

print("\n1️⃣ EXTRACTING CLAIMS...")
claims = extract_claims(content)
print(f"   Extracted {len(claims)} claims:")
for i, claim in enumerate(claims, 1):
    print(f"   {i}. {claim}")

print("\n2️⃣ VERIFYING CLAIMS WITH GEMINI...")
print("   (Watch for Gemini API calls in debug output below)")
print("   " + "-" * 66)

try:
    verification_results = verify_claims(claims)

    print("\n📊 VERIFICATION RESULTS:")
    verified_count = 0
    disputed_count = 0
    uncertain_count = 0

    for result in verification_results:
        status = result.get('status', 'unknown')
        claim = result.get('claim', 'Unknown')[:60]
        sources = len(result.get('sources', []))

        print(f"\n   [{status.upper()}] {claim}...")
        print(
            f"   Rationale: {result.get('rationale', 'No rationale')[:70]}...")
        print(f"   Sources: {sources}")

        if status == "verified":
            verified_count += 1
        elif status == "disputed":
            disputed_count += 1
        elif status == "uncertain":
            uncertain_count += 1

    print("\n✅ SUMMARY:")
    print(f"   Verified: {verified_count}")
    print(f"   Disputed: {disputed_count}")
    print(f"   Uncertain: {uncertain_count}")

    if uncertain_count == len(verification_results):
        print("\n⚠️  WARNING: All claims uncertain - check if Gemini is being called")
        print("   This means NewsAPI found no sources or Gemini returned uncertain for all")
    else:
        print("\n✓ Gemini verification working - mixed results show actual classification")

except Exception as e:
    print(f"\n❌ Error during verification: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
