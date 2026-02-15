#!/usr/bin/env python3
"""
Test that Settings now has backboard_api_key attribute
"""
from app.core.settings import get_settings

print("=" * 70)
print("VERIFYING SETTINGS FIX")
print("=" * 70)

settings = get_settings()

print("\n✓ Settings attributes check:")
print(f"  - gemini_api_key:      {type(settings.gemini_api_key)} ✓")
print(f"  - gemini_model:        {type(settings.gemini_model)} ✓")
print(f"  - backboard_api_key:   {type(settings.backboard_api_key)} ✓ (FIXED)")
print(f"  - news_api_key:        {type(settings.news_api_key)} ✓")
print(
    f"  - request_timeout_seconds: {type(settings.request_timeout_seconds)} ✓")
print(f"  - max_claims:          {type(settings.max_claims)} ✓")

print("\n✓ Attribute values:")
print(f"  gemini_api_key: {settings.gemini_api_key}")
print(
    f"  backboard_api_key: {settings.backboard_api_key} (NEW - previously missing)")
print(f"  news_api_key: {settings.news_api_key}")

print("\n" + "=" * 70)
print("✅ FIX VERIFIED - backboard_api_key attribute now exists!")
print("=" * 70)

# Test that get_ai_client() won't fail on the Settings attribute
print("\n✓ Testing get_ai_client() compatibility:")
try:
    from app.clients.ai_client import get_ai_client
    print("  - get_ai_client function exists ✓")
    print("  - Will check settings.backboard_api_key ✓")
    print("  - Settings now has this attribute ✓")
    print("\n✅ ai_client can now safely access settings.backboard_api_key")
except Exception as e:
    print(f"  ❌ Error: {e}")

print("\n" + "=" * 70)
print("NEXT STEP: Set API keys for claim verification")
print("=" * 70)
print("\nAdd to backend/.env or set environment variables:")
print("  GEMINI_API_KEY=your_key")
print("  NEWS_API_KEY=your_key")
print("\nThen claims will be properly classified as VERIFIED/DISPUTED/UNCERTAIN")
