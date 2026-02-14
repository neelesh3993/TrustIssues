#!/usr/bin/env python3
"""
Verification script for TrustIssues backend setup.
Tests that all required dependencies and configuration are available.
"""

import sys
import os


def check_python_version():
    """Verify Python version >= 3.8."""
    print("Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"  ✗ Python 3.8+ required, found {version.major}.{version.minor}")
        return False
    print(f"  ✓ Python {version.major}.{version.minor}")
    return True


def check_dependencies():
    """Verify required packages are installed."""
    print("\nChecking dependencies...")
    required = {
        "fastapi": "FastAPI",
        "uvicorn": "Uvicorn",
        "pydantic": "Pydantic",
        "pydantic_settings": "Pydantic Settings",
        "dotenv": "python-dotenv",
        "requests": "Requests",
        "google.generativeai": "Google Generative AI",
    }
    
    all_ok = True
    for module, name in required.items():
        try:
            __import__(module)
            print(f"  ✓ {name}")
        except ImportError:
            print(f"  ✗ {name} - Install with: pip install -r requirements.txt")
            all_ok = False
    
    return all_ok


def check_env_file():
    """Check if .env file exists and has required variables."""
    print("\nChecking environment configuration...")
    
    from pathlib import Path
    env_file = Path(".env")
    
    if not env_file.exists():
        print("  ⚠ .env file not found")
        print("    - Create it from .env.example: cp .env.example .env")
        return False
    
    # Read and check variables
    has_gemini = False
    has_newsapi = False
    
    with open(".env", "r") as f:
        for line in f:
            if "GEMINI_API_KEY" in line and "=" in line:
                key_val = line.split("=", 1)[1].strip()
                if key_val and not key_val.startswith("your_"):
                    has_gemini = True
            if "NEWS_API_KEY" in line and "=" in line:
                key_val = line.split("=", 1)[1].strip()
                if key_val and not key_val.startswith("your_"):
                    has_newsapi = True
    
    if has_gemini:
        print("  ✓ GEMINI_API_KEY configured")
    else:
        print("  ✗ GEMINI_API_KEY not set in .env")
        print("    - Get from: https://makersuite.google.com/app/apikey")
    
    if has_newsapi:
        print("  ✓ NEWS_API_KEY configured")
    else:
        print("  ✗ NEWS_API_KEY not set in .env")
        print("    - Get from: https://newsapi.org/")
    
    return has_gemini and has_newsapi


def check_env_variables():
    """Check if API keys are set as environment variables."""
    print("\nChecking environment variables...")
    
    gemini_key = os.getenv("GEMINI_API_KEY")
    news_key = os.getenv("NEWS_API_KEY")
    
    if gemini_key:
        print("  ✓ GEMINI_API_KEY environment variable set")
    else:
        print("  - GEMINI_API_KEY not set (check .env file)")
    
    if news_key:
        print("  ✓ NEWS_API_KEY environment variable set")
    else:
        print("  - NEWS_API_KEY not set (check .env file)")
    
    return gemini_key or news_key  # At least one should be set


def check_settings_module():
    """Verify settings module can be imported."""
    print("\nChecking settings module...")
    try:
        from app.core.settings import get_settings, Settings
        settings = get_settings()
        print(f"  ✓ Settings loaded successfully")
        print(f"    - Model: {settings.gemini_model}")
        print(f"    - Endpoint: {settings.newsapi_endpoint}")
        print(f"    - Timeout: {settings.request_timeout_seconds}s")
        print(f"    - Max claims: {settings.max_claims}")
        return True
    except Exception as e:
        print(f"  ✗ Failed to load settings: {str(e)}")
        return False


def main():
    """Run all checks."""
    print("=" * 60)
    print("TrustIssues Backend Setup Verification")
    print("=" * 60)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Settings Module", check_settings_module),
        ("Environment File", check_env_file),
        ("Environment Variables", check_env_variables),
    ]
    
    results = []
    for name, check_func in checks:
        print()
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    critical_passed = all(r for _, r in results[:3])  # Python, dependencies, settings
    config_ready = results[3][1] or results[4][1]  # Either .env or env vars
    
    for name, result in results:
        status = "✓" if result else "✗"
        print(f"{status} {name}")
    
    print("\n" + "=" * 60)
    
    if critical_passed and config_ready:
        print("✓ All checks passed! Ready to run backend.")
        print("\nStart the server with:")
        print("  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        return 0
    else:
        print("✗ Some checks failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
