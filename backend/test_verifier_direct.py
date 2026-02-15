#!/usr/bin/env python3
"""
Simple test to verify that _verify_single_claim_ai calls Gemini
"""
from app.pipeline.verifier import _verify_single_claim_ai
import logging
import sys

# Set up logging to see what's happening
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s - %(name)s - %(message)s',
    stream=sys.stdout
)

print("=" * 70)
print("VERIFIER FUNCTION TEST")
print("=" * 70)

# Import after logging is set up

test_claim = "Iran signals flexibility on nuclear issues and energy deals with the US"

print(f"\n📋 Testing claim: {test_claim}\n")

try:
    result = _verify_single_claim_ai(test_claim)

    print(f"\n✅ RESULT:")
    print(f"   Status: {result.get('status')}")
    print(f"   Rationale: {result.get('rationale')}")
    print(f"   Sources: {len(result.get('sources', []))} found")

    if result.get('status') == 'uncertain' and 'technical error' in result.get('rationale', ''):
        print("\n⚠️  ISSUE: Returned 'technical error' message")
        print("    This means Gemini was NOT called successfully")
    elif result.get('status') == 'uncertain' and 'API' in result.get('rationale', ''):
        print(f"\n❌ ISSUE: {result.get('rationale')}")
    else:
        print("\n✓ Claim was classified by Gemini API")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
