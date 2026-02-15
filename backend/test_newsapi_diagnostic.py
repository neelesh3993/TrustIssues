"""
NewsAPI Diagnostic Test
Tests if NewsAPI is properly configured and functioning
"""

from app.clients.news_client import search_news, search_news_with_fallback, NewsAPIError
from app.core.settings import get_settings
import os
import sys
from pprint import pprint

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))


def test_api_key():
    """Check if NEWS_API_KEY is configured"""
    print("\n" + "="*80)
    print("1. TESTING API KEY CONFIGURATION")
    print("="*80)

    settings = get_settings()

    if not settings.news_api_key:
        print("❌ ERROR: NEWS_API_KEY is NOT configured!")
        print("\nTo fix:")
        print("  1. Set env var: export NEWS_API_KEY='your_key_here'")
        print("  2. Or add to .env file: NEWS_API_KEY=your_key_here")
        print("  3. Get free key from: https://newsapi.org/\n")
        return False

    print(
        f"✅ API Key found: {settings.news_api_key[:10]}...{settings.news_api_key[-6:]}")
    print(f"   Endpoint: {settings.newsapi_endpoint}")
    print(f"   Page size: {settings.newsapi_page_size}")
    print(f"   Language: {settings.newsapi_language}")
    return True


def test_single_search(query: str):
    """Test a single NewsAPI search"""
    print(f"\n   Testing search: '{query}'")

    try:
        articles = search_news(query)

        if not articles:
            print(f"   ⚠️  No articles found for '{query}'")
            return []

        print(f"   ✅ Found {len(articles)} articles:")
        for i, article in enumerate(articles[:3], 1):
            print(f"\n      [{i}] {article.get('headline', 'N/A')[:70]}")
            print(f"          Source: {article.get('name', 'Unknown')}")
            print(
                f"          Snippet: {article.get('snippet', 'N/A')[:80]}...")

        return articles

    except NewsAPIError as e:
        print(f"   ❌ NewsAPI Error: {str(e)[:100]}")
        return []
    except Exception as e:
        print(f"   ❌ Unexpected error: {str(e)[:100]}")
        return []


def test_basic_searches():
    """Test basic searches with common terms"""
    print("\n" + "="*80)
    print("2. TESTING BASIC SEARCHES")
    print("="*80)

    test_queries = [
        "climate change",
        "technology",
        "economy",
        "health news",
    ]

    for query in test_queries:
        articles = test_single_search(query)
        if articles:
            print(f"   Result: ✅ Success")
        else:
            print(f"   Result: ⚠️  No results")


def test_key_phrase_extraction():
    """Test the key phrase extraction logic"""
    print("\n" + "="*80)
    print("3. TESTING KEY PHRASE EXTRACTION")
    print("="*80)

    # Sample content
    sample_content = """
    The new vaccine has been shown to reduce infection rates by 95 percent according to recent studies.
    Climate scientists warn that global temperatures are rising faster than previously predicted.
    The stock market reached all-time highs this week despite economic concerns.
    """

    # Extract phrases using the same logic as analyze.py
    from app.routes.analyze import _extract_key_phrases

    phrases = _extract_key_phrases(sample_content, num_phrases=3)

    print(f"Content: {sample_content[:100]}...")
    print(f"\nExtracted phrases ({len(phrases)}):")
    for i, phrase in enumerate(phrases, 1):
        print(f"  [{i}] {phrase}")

    # Now search for each
    print(f"\nSearching for each phrase on NewsAPI:")
    for phrase in phrases:
        test_single_search(phrase)


def test_actual_analysis():
    """Test with real article content"""
    print("\n" + "="*80)
    print("4. TESTING WITH SAMPLE ARTICLE CONTENT")
    print("="*80)

    test_article = """
    COVID-19 Vaccines Prove Highly Effective in Latest Study
    
    A groundbreaking new study from Johns Hopkins University shows that COVID-19 vaccines
    maintain their effectiveness even against new variants. The research, published in Nature
    Medicine, followed over 50,000 individuals across six countries over eighteen months.
    
    Lead researcher Dr. Sarah Chen stated: "Our findings demonstrate that the vaccines provide
    robust protection, with efficacy rates remaining above 85% even against the Omicron variant."
    
    The study contradicts recent claims made by anti-vaccine groups that suggested vaccine 
    effectiveness drops to zero after six months. Regulatory bodies worldwide are reviewing
    the data for updated booster recommendations.
    """

    print("Test content:")
    print(test_article[:200] + "...\n")

    # Extract phrases
    from app.routes.analyze import _extract_key_phrases
    phrases = _extract_key_phrases(test_article, num_phrases=5)

    print(f"Extracted {len(phrases)} phrases:")
    for i, phrase in enumerate(phrases, 1):
        print(f"  [{i}] {phrase}")

    # Search for each phrase
    print("\n\nSearching NewsAPI for these phrases:")
    total_articles_found = 0
    for phrase in phrases:
        articles = test_single_search(phrase)
        total_articles_found += len(articles)

    print(f"\nTotal articles found across all phrases: {total_articles_found}")


def test_fallback():
    """Test the fallback behavior"""
    print("\n" + "="*80)
    print("5. TESTING FALLBACK BEHAVIOR (search_news_with_fallback)")
    print("="*80)

    # This should never raise an error, always return list
    try:
        result = search_news_with_fallback(
            "this is definitely not a real claim xxxyyy")
        print(
            f"✅ Fallback function returned: {type(result)} with {len(result)} items")
        if not result:
            print("   (Empty list = graceful fallback when no results)")
    except Exception as e:
        print(f"❌ Fallback failed: {str(e)}")


if __name__ == "__main__":
    print("\n" + "█"*80)
    print("█ NewsAPI DIAGNOSTIC TEST")
    print("█"*80)

    try:
        # Test 1: API Key
        if not test_api_key():
            print("\n⚠️  Cannot continue without API key. Please configure NEWS_API_KEY.")
            sys.exit(1)

        # Test 2: Basic searches
        test_basic_searches()

        # Test 3: Phrase extraction
        test_key_phrase_extraction()

        # Test 4: Actual analysis
        test_actual_analysis()

        # Test 5: Fallback
        test_fallback()

        print("\n" + "█"*80)
        print("█ DIAGNOSTIC TEST COMPLETE")
        print("█"*80 + "\n")

    except Exception as e:
        print(f"\n\n❌ FATAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
