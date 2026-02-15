"""
Quick test of the fixed phrase extraction
"""
from app.clients.news_client import search_news_with_fallback
from app.routes.analyze import _extract_key_phrases
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


test_content = """
COVID-19 Vaccines Prove Highly Effective in Latest Study

A groundbreaking new study from Johns Hopkins University shows that COVID-19 vaccines
maintain their effectiveness even against new variants. The research, published in Nature
Medicine, followed over 50,000 individuals across six countries over eighteen months.

Lead researcher Dr. Sarah Chen stated: "Our findings demonstrate that the vaccines provide
robust protection, with efficacy rates remaining above 85% even against the Omicron variant."

The study contradicts recent claims made by anti-vaccine groups that suggested vaccine 
effectiveness drops to zero after six months.
"""

print("=" * 80)
print("TESTING FIXED PHRASE EXTRACTION")
print("=" * 80)

# Extract phrases
phrases = _extract_key_phrases(test_content, num_phrases=5)

print(f"\nExtracted {len(phrases)} phrases after sanitization:\n")
for i, phrase in enumerate(phrases, 1):
    print(f"[{i}] {phrase}")

# Now test if they work with NewsAPI
print("\n" + "=" * 80)
print("SEARCHING NewsAPI FOR EACH PHRASE")
print("=" * 80)

total_found = 0
for phrase in phrases:
    print(f"\nSearching for: '{phrase}'")
    articles = search_news_with_fallback(phrase)

    if articles:
        print(f"✅ Found {len(articles)} articles")
        print(f"   Top result: {articles[0].get('headline', 'N/A')[:70]}")
        total_found += len(articles)
    else:
        print(f"⚠️  No articles found")

print("\n" + "=" * 80)
print(f"Total articles found: {total_found}")
print("=" * 80)
