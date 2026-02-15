"""
NewsAPI Diagnostic Script
Check if NewsAPI is configured correctly and returning results
"""

import os
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

NEWS_API_KEY = os.getenv('NEWS_API_KEY')

print("=" * 60)
print("NEWSAPI CONFIGURATION CHECK")
print("=" * 60)

# Check 1: API Key exists
if not NEWS_API_KEY:
    print("\n❌ NEWS_API_KEY not found in .env file!")
    print("   Get a free key from: https://newsapi.org/register")
    print("   Then add to backend/.env:")
    print("   NEWS_API_KEY=your_key_here")
    exit(1)
else:
    print(f"\n✓ NEWS_API_KEY found: {NEWS_API_KEY[:10]}...{NEWS_API_KEY[-4:]}")

# Check 2: Test API connection
print("\n" + "=" * 60)
print("TESTING NEWSAPI CONNECTION")
print("=" * 60)

test_query = "climate change"
url = f"https://newsapi.org/v2/everything?q={test_query}&language=en&pageSize=5&apiKey={NEWS_API_KEY}"

try:
    response = requests.get(url, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        articles = data.get('articles', [])
        
        print(f"\n✅ NewsAPI is working!")
        print(f"   Query: '{test_query}'")
        print(f"   Found: {len(articles)} articles")
        
        if articles:
            print("\n📰 Sample Articles:")
            for i, article in enumerate(articles[:3], 1):
                print(f"\n{i}. {article.get('title')}")
                print(f"   Source: {article.get('source', {}).get('name')}")
                print(f"   URL: {article.get('url')}")
        else:
            print("\n⚠️  No articles found for this query")
            print("   This might happen with very specific queries")
    
    elif response.status_code == 401:
        print(f"\n❌ API Key Invalid!")
        print(f"   Status: {response.status_code}")
        print(f"   Message: {response.json().get('message')}")
        print("\n   Solutions:")
        print("   1. Verify your key at: https://newsapi.org/account")
        print("   2. Make sure there are no extra spaces in .env")
        print("   3. Try regenerating your API key")
    
    elif response.status_code == 429:
        print(f"\n⚠️  Rate Limit Exceeded!")
        print(f"   Status: {response.status_code}")
        print("\n   Free tier limits:")
        print("   - 100 requests per day")
        print("   - 1 request per second")
        print("\n   Solutions:")
        print("   1. Wait 24 hours for limit reset")
        print("   2. Upgrade to paid plan")
        print("   3. Use a different API key")
    
    else:
        print(f"\n❌ NewsAPI Error!")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")

except requests.exceptions.Timeout:
    print("\n❌ Request Timeout")
    print("   NewsAPI took too long to respond")
    print("   Check your internet connection")

except requests.exceptions.ConnectionError:
    print("\n❌ Connection Error")
    print("   Cannot reach NewsAPI")
    print("   Check your internet connection")

except Exception as e:
    print(f"\n❌ Error: {str(e)}")

print("\n" + "=" * 60)
print("\nNext Steps:")
print("1. If API key is invalid → Get new key from newsapi.org")
print("2. If rate limited → Wait or upgrade plan")
print("3. If working → Backend should now find sources!")
print("=" * 60)
