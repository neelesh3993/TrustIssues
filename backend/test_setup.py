"""
Backend Quick Test Script
Tests all backend components before starting the server.
Run this to verify your setup!
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def print_header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def print_success(text):
    print(f"✓ {text}")

def print_error(text):
    print(f"✗ {text}")

def print_warning(text):
    print(f"⚠ {text}")

def test_imports():
    """Test if all required packages are installed"""
    print_header("Testing Package Imports")
    
    required_packages = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("pydantic", "Pydantic"),
        ("pydantic_settings", "Pydantic Settings"),
        ("requests", "Requests"),
        ("google.generativeai", "Google Generative AI"),
    ]
    
    all_ok = True
    for package, name in required_packages:
        try:
            __import__(package)
            print_success(f"{name} installed")
        except ImportError:
            print_error(f"{name} NOT installed")
            all_ok = False
    
    return all_ok

def test_env_file():
    """Check if .env file exists and has API keys"""
    print_header("Checking Configuration")
    
    env_path = Path(__file__).parent / ".env"
    
    if not env_path.exists():
        print_error(".env file not found!")
        print("   Create a .env file in the backend directory")
        return False
    
    print_success(".env file exists")
    
    # Read .env file
    with open(env_path) as f:
        content = f.read()
    
    has_gemini = "GEMINI_API_KEY=" in content
    has_news = "NEWS_API_KEY=" in content
    
    if has_gemini:
        print_success("GEMINI_API_KEY found in .env")
    else:
        print_error("GEMINI_API_KEY not found in .env")
    
    if has_news:
        print_success("NEWS_API_KEY found in .env")
    else:
        print_error("NEWS_API_KEY not found in .env")
    
    return has_gemini and has_news

def test_api_keys():
    """Test if API keys are configured (not just placeholders)"""
    print_header("Validating API Keys")
    
    try:
        from app.core.settings import get_settings
        
        settings = get_settings()
        
        all_ok = True
        
        # Check Gemini key
        if not settings.gemini_api_key:
            print_error("GEMINI_API_KEY is empty")
            all_ok = False
        elif "your_" in settings.gemini_api_key.lower() or "here" in settings.gemini_api_key.lower():
            print_error("GEMINI_API_KEY is still a placeholder!")
            print("   Get your key from: https://makersuite.google.com/app/apikey")
            all_ok = False
        else:
            print_success("GEMINI_API_KEY configured")
        
        # Check News API key
        if not settings.news_api_key:
            print_error("NEWS_API_KEY is empty")
            all_ok = False
        elif "your_" in settings.news_api_key.lower() or "here" in settings.news_api_key.lower():
            print_error("NEWS_API_KEY is still a placeholder!")
            print("   Get your key from: https://newsapi.org/")
            all_ok = False
        else:
            print_success("NEWS_API_KEY configured")
        
        return all_ok
        
    except Exception as e:
        print_error(f"Could not load settings: {str(e)}")
        return False

def test_gemini_connection():
    """Test if Gemini API key works"""
    print_header("Testing Gemini API Connection")
    
    try:
        from app.clients.gemini_client import get_gemini_client
        
        client = get_gemini_client()
        print_success("Gemini client initialized")
        
        # Try a simple request
        try:
            response = client.generate_text("Say 'Hello, backend is working!'", temperature=0.5, max_tokens=50)
            if response:
                print_success(f"Gemini API responding: {response[:50]}...")
                return True
            else:
                print_error("Gemini returned empty response")
                return False
        except Exception as e:
            print_error(f"Gemini API call failed: {str(e)}")
            print("   Check if your GEMINI_API_KEY is valid")
            return False
            
    except Exception as e:
        print_error(f"Could not initialize Gemini client: {str(e)}")
        return False

def test_news_api():
    """Test if News API key works"""
    print_header("Testing NewsAPI Connection")
    
    try:
        from app.clients.news_client import search_news
        
        # Try a simple search
        try:
            results = search_news("technology")
            if results:
                print_success(f"NewsAPI responding: {len(results)} articles found")
                return True
            else:
                print_warning("NewsAPI returned no results (might be rate limited)")
                return True  # Not necessarily an error
        except Exception as e:
            error_msg = str(e)
            if "apiKey" in error_msg or "unauthorized" in error_msg.lower():
                print_error("NewsAPI key is invalid")
                print("   Get your key from: https://newsapi.org/")
            else:
                print_error(f"NewsAPI call failed: {error_msg}")
            return False
            
    except Exception as e:
        print_error(f"Could not test NewsAPI: {str(e)}")
        return False

def test_pipeline():
    """Test the analysis pipeline"""
    print_header("Testing Analysis Pipeline")
    
    try:
        from app.pipeline.claim_extractor import extract_claims
        from app.pipeline.verifier import verify_claims
        from app.pipeline.summarizer import generate_summary
        
        # Test with sample content
        sample_content = "The Eiffel Tower is located in Paris, France. It was completed in 1889 and stands approximately 330 meters tall."
        
        print("Running claim extraction...")
        claims = extract_claims(sample_content)
        if claims:
            print_success(f"Extracted {len(claims)} claims")
        else:
            print_warning("No claims extracted (Gemini might need more content)")
        
        if claims:
            print("Running claim verification...")
            verification = verify_claims(claims[:1])  # Just verify first claim
            if verification:
                print_success("Claim verification working")
            else:
                print_warning("Verification returned no results")
            
            print("Generating summary...")
            summary = generate_summary(sample_content, claims, verification)
            if summary:
                print_success("Summary generation working")
            else:
                print_warning("No summary generated")
        
        return True
        
    except Exception as e:
        print_error(f"Pipeline test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("\n" + "🚀" * 30)
    print("  TRUST ISSUES BACKEND - SETUP VERIFICATION")
    print("🚀" * 30)
    
    results = []
    
    # Run tests
    results.append(("Package Imports", test_imports()))
    results.append(("Environment File", test_env_file()))
    results.append(("API Key Configuration", test_api_keys()))
    results.append(("Gemini Connection", test_gemini_connection()))
    results.append(("NewsAPI Connection", test_news_api()))
    results.append(("Analysis Pipeline", test_pipeline()))
    
    # Summary
    print_header("Test Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your backend is ready!")
        print("\nNext steps:")
        print("1. Start the backend server:")
        print("   python -m uvicorn app.main:app --reload")
        print("\n2. Build and load the Chrome extension")
        print("   See SETUP_COMPLETE.md for details")
    else:
        print("\n⚠ Some tests failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("• Missing packages: pip install -r requirements.txt")
        print("• Missing API keys: Add them to backend/.env")
        print("• Invalid API keys: Get new ones from the provider websites")

if __name__ == "__main__":
    main()
