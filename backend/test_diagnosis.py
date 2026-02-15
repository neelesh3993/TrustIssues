#!/usr/bin/env python3
"""
Diagnostic: Test why claims are returning uncertain
"""
import logging
import sys
from app.core.settings import get_settings

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)

print("=" * 80)
print("DIAGNOSIS: Why are claims returning UNCERTAIN?")
print("=" * 80)

# Check 1: API Keys
print("\n✓ Step 1: Checking API Key Configuration")
print("-" * 80)
settings = get_settings()

gemini_key = "✓ SET" if settings.gemini_api_key else "✗ MISSING"
news_key = "✓ SET" if settings.news_api_key else "✗ MISSING"
backboard_key = "✓ SET" if settings.backboard_api_key else "✗ MISSING"

print(f"GEMINI_API_KEY:     {gemini_key}")
print(f"NEWS_API_KEY:       {news_key}")
print(f"BACKBOARD_API_KEY:  {backboard_key}")

if not settings.gemini_api_key and not settings.backboard_api_key:
    print("\n⚠️  CRITICAL: No AI API key configured!")
    print("   Gemini and Backboard are both missing")

if not settings.news_api_key:
    print("\n⚠️  WARNING: NewsAPI key missing - news sources won't be retrieved")
    print("   Gemini will attempt to verify claims using its own knowledge")

# Check 2: Test NewsAPI retrieval
print("\n\n✓ Step 2: Testing NewsAPI Source Retrieval")
print("-" * 80)

try:
    from app.clients.news_client import search_news_with_fallback
    sources = search_news_with_fallback("Iran nuclear energy talks")
    print(f"✓ NewsAPI working: Found {len(sources)} sources")
    if sources:
        print(
            f"  Example: {sources[0].get('name')} - {sources[0].get('headline')[:50]}...")
except Exception as e:
    print(f"✗ NewsAPI failed: {e}")

# Check 3: Test Gemini can generate text
print("\n\n✓ Step 3: Testing Gemini AI Capability")
print("-" * 80)

try:
    from app.clients.ai_client import get_ai_client
    client = get_ai_client()
    print(f"✓ AI client initialized: {type(client).__name__}")

    # Test simple generation
    test_response = client.generate_text("Respond with YES", max_tokens=10)
    print(f"✓ AI can generate text: '{test_response.strip()}'")

except Exception as e:
    print(f"✗ AI client failed: {e}")

# Check 4: Test full verification
print("\n\n✓ Step 4: Testing Claim Verification")
print("-" * 80)

try:
    from app.pipeline.verifier import _verify_single_claim_ai

    test_claim = "Paris is the capital of France"
    print(f"Testing claim: '{test_claim}'")

    result = _verify_single_claim_ai(test_claim)

    print(f"\n✓ Result:")
    print(f"  Status: {result['status']}")
    print(f"  Rationale: {result['rationale'][:100]}...")
    print(f"  Sources: {len(result.get('sources', []))}")

    if result['status'] == 'verified':
        print("\n✓ GOOD: Claim was verified by Gemini")
    elif result['status'] == 'uncertain' and 'technical error' in result['rationale'].lower():
        print("\n⚠️  ISSUE: Got 'technical error' - verifier isn't calling Gemini properly")
    elif result['status'] == 'uncertain':
        print("\n⚠️  UNCERTAIN: Could be due to missing news sources")
        print("    This is expected if NEWS_API_KEY is not set")

except Exception as e:
    print(f"✗ Verification failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("DIAGNOSIS COMPLETE")
print("=" * 80)
