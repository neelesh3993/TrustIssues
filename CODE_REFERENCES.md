# Code Implementation Reference

This document provides quick access to the implementation details and key code sections.

## Configuration System (`app/core/settings.py`)

### What It Does
- Centralizes all configuration in one place
- Loads from environment variables or .env file
- Provides typed settings with Pydantic
- Cached singleton instance

### Usage
```python
from app.core.settings import get_settings, validate_required_keys

# Get settings
settings = get_settings()
print(settings.gemini_api_key)  # Your API key
print(settings.max_claims)       # Default: 5

# Validate on startup
try:
    validate_required_keys()
except ValueError as e:
    print(f"Configuration error: {e}")
```

### Environment Variables Supported
```
GEMINI_API_KEY=your_key              # Required
NEWS_API_KEY=your_key                # Required
GEMINI_MODEL=gemini-1.5-flash        # Optional
NEWSAPI_PAGE_SIZE=5                  # Optional
NEWSAPI_LANGUAGE=en                  # Optional
REQUEST_TIMEOUT_SECONDS=20           # Optional
MAX_CLAIMS=5                         # Optional
```

## Gemini Client (`app/clients/gemini_client.py`)

### What It Does
- Wraps Google's generativeai SDK
- Handles API initialization and error cases
- Provides text and JSON generation methods
- Automatic token management

### Usage
```python
from app.clients.gemini_client import get_gemini_client

client = get_gemini_client()

# Generate text
response = client.generate_text(
    "Extract claims from: ...",
    temperature=0.3,
    max_tokens=512
)

# Generate JSON
json_response = client.generate_json(
    "Return JSON array of claims",
    temperature=0.2
)
```

### Error Handling
- Raises `ValueError` if API key missing
- Clear error messages with setup instructions
- Automatic retry logic built-in

## NewsAPI Client (`app/clients/news_client.py`)

### What It Does
- Searches for news articles related to claims
- Normalizes responses to consistent format
- Handles rate limits and timeouts gracefully

### Usage
```python
from app.clients.news_client import search_news, search_news_with_fallback

# Standard search (may fail)
try:
    articles = search_news("climate change")
except NewsAPIError as e:
    print(f"Search failed: {e}")

# Fallback search (never fails)
articles = search_news_with_fallback("climate change")  # Returns [] on failure
```

### Returned Article Format
```python
{
    "name": "BBC News",                    # Publication name
    "headline": "New Climate Report",      # Article title
    "url": "https://example.com/...",      # Article URL
    "snippet": "Scientists report...",     # Article description
    "publishedAt": "2024-01-15T10:00:00Z"  # Publication timestamp
}
```

## Claim Extraction (`app/pipeline/claim_extractor.py`)

### What It Does
- Extracts 3-5 verifiable factual claims from text
- Uses Gemini AI for intelligent extraction
- Falls back to heuristics if Gemini fails
- Respects MAX_CLAIMS setting

### Usage
```python
from app.pipeline.claim_extractor import extract_claims

content = "Paris is the capital of France. The Eiffel Tower is 330 meters tall."
claims = extract_claims(content)
# Returns: ["Paris is the capital of France", "The Eiffel Tower is 330 meters"]
```

### How It Works
1. Sends prompt to Gemini asking for JSON array of claims
2. Parses JSON response
3. If parsing fails, falls back to heuristic extraction
4. Returns up to MAX_CLAIMS claims

### Quality Output
- Claims are specific and verifiable
- Claims contain facts, numbers, or attributions
- Claims are reasonably balanced difficulty

## Verification (`app/pipeline/verifier.py`)

### What It Does
- Classifies each claim as "verified", "disputed", or "uncertain"
- Retrieves evidence from NewsAPI
- Uses Gemini to reason about evidence
- Returns structured results with sources

### Usage
```python
from app.pipeline.verifier import verify_claims

claims = [
    "Paris is the capital of France",
    "The Earth is flat"
]

results = verify_claims(claims)
# Returns:
# [
#    {
#        "claim": "Paris is the capital of France",
#        "status": "verified",
#        "rationale": "Confirmed by multiple reliable sources",
#        "sources": [...]
#    },
#    ...
# ]
```

### Result Structure
```python
{
    "claim": "Original claim text",
    "status": "verified|disputed|uncertain",  # Classification
    "rationale": "Why this classification",    # 1-2 sentences grounded in sources
    "sources": [                               # Evidence sources
        {
            "name": "BBC",
            "headline": "Article about claim",
            "url": "https://...",
            "snippet": "Relevant excerpt",
            "publishedAt": "2024-01-15T..."
        }
    ]
}
```

### How It Works
1. For each claim, search NewsAPI for articles
2. Format retrieved articles as evidence
3. Send to Gemini: "Given this evidence, is this claim verified/disputed/uncertain?"
4. Parse Gemini's JSON response
5. Return with sources

## Summarization (`app/pipeline/summarizer.py`)

### What It Does
- Generates human-readable analysis summary
- Grounded in actual verification results
- Uses Gemini for natural language generation
- Falls back to formula-based summary if needed

### Usage
```python
from app.pipeline.summarizer import generate_summary

content = "..."
claims = [...]
verification_results = [...]

summary = generate_summary(content, claims, verification_results)
# Returns: "3 of 5 claims were verified, 1 was disputed..."
```

### Output Quality
- 2-4 sentences total
- Professional tone
- Action-oriented recommendations
- No hallucinated sources

## Analyze Endpoint (`app/routes/analyze.py`)

### What It Does
- Main API endpoint: POST /api/analyze
- Orchestrates the full pipeline
- Returns AnalysisResponse with structured results
- Handles errors gracefully

### Request Format
```json
{
    "url": "https://example.com",
    "content": "Text to analyze (min 50 chars)",
    "title": "Page title",
    "images": []  // Optional
}
```

### Response Format
```json
{
    "aiGenerationLikelihood": 45.0,
    "credibilityScore": 78.5,
    "manipulationRisk": 32.0,
    "findings": [
        "✓ VERIFIED: Claim 1",
        "⚠ DISPUTED: Claim 2"
    ],
    "sources": [
        {
            "name": "BBC",
            "headline": "Supporting article",
            "status": "verified"
        }
    ],
    "report": "Detailed analysis summary"
}
```

### Helper Functions
```python
_calculate_credibility(results)      # Score 0-100 based on verified/disputed
_calculate_ai_likelihood(content)    # Estimate AI-generation probability
_calculate_manipulation_risk(content) # Analyze for manipulation indicators
_extract_findings(results)           # Convert results to bullet points
_format_sources(results)             # Convert to Source schema objects
```

## Complete Request-Response Example

### Client Code
```python
import requests

response = requests.post(
    "http://localhost:8000/api/analyze",
    json={
        "url": "https://example.com/article",
        "content": "Paris is the capital of France with approximately 2 million residents. "
                   "The Eiffel Tower stands 330 meters tall. President Macron has served "
                   "since 2017. Climate scientists report temperatures rising.",
        "title": "Facts about Paris and Climate"
    }
)

result = response.json()
print(f"Credibility: {result['credibilityScore']}%")
print(f"\nFindings:")
for finding in result['findings']:
    print(f"  {finding}")
print(f"\nSummary: {result['report']}")
```

### Backend Flow
```
1. validate_required_keys()
   └─ Checks GEMINI_API_KEY and NEWS_API_KEY set

2. extract_claims(content)
   ├─ Send to Gemini: "Extract 5 verifiable claims"
   ├─ Parse JSON response
   └─ Return ["claim1", "claim2", ...]

3. verify_claims(claims)
   └─ For each claim:
      ├─ search_news(claim) → Get articles
      ├─ Call Gemini: "Classify as verified/disputed/uncertain"
      └─ Return {"claim", "status", "rationale", "sources"}

4. generate_summary(content, claims, results)
   ├─ Tally verified/disputed/uncertain counts
   ├─ Send to Gemini: "Write summary based on results"
   └─ Return summary string

5. Calculate scores and format response
   └─ Return AnalysisResponse JSON
```

## Testing

### Run All Tests
```bash
cd backend
pytest app/test/test_integration.py -v
```

### Available Tests
- `TestSettings` - Configuration loading
- `TestClaimExtractor` - Claim extraction and parsing
- `TestNewsClient` - NewsAPI integration
- `TestVerifier` - Claim verification
- `TestSummarizer` - Summary generation
- `TestAnalyzeRoute` - Endpoint helpers

## Verification Script

### Run Setup Verification
```bash
python backend/verify_setup.py
```

### Checks Performed
✓ Python version (3.8+)
✓ All dependencies installed
✓ .env file exists
✓ Settings module loads
✓ Environment variables set

### Example Output
```
============================================================
TrustIssues Backend Setup Verification
============================================================

Checking Python version...
  ✓ Python 3.10

Checking dependencies...
  ✓ FastAPI
  ✓ Uvicorn
  ✓ Pydantic
  [etc...]

Checking environment configuration...
  ✓ GEMINI_API_KEY configured
  ✓ NEWS_API_KEY configured

============================================================
Summary
============================================================
✓ All checks passed! Ready to run backend.

Start the server with:
  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Troubleshooting

### Missing Module Errors
```
Solution: pip install -r backend/requirements.txt
```

### KeyError for API Keys
```
Solution: Create .env file in backend directory and add:
  GEMINI_API_KEY=your_key_here
  NEWS_API_KEY=your_key_here
```

### Connection Errors to Backend
```
Solution: Ensure backend is running:
  cd backend
  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Timeouts
```
Solution: Increase REQUEST_TIMEOUT_SECONDS in .env:
  REQUEST_TIMEOUT_SECONDS=30
```

## Performance Notes

- Claim extraction: ~2-3 seconds (Gemini API call)
- Evidence retrieval: ~1-2 seconds (NewsAPI call)
- Verification: ~3-4 seconds (per claim, Gemini call)
- Summarization: ~2-3 seconds (Gemini API call)
- **Total per request**: ~8-15 seconds typical

### Optimization Tips
- Reduce MAX_CLAIMS to run faster (fewer Gemini calls)
- Use gemini-1.5-flash (faster than gemini-pro)
- Increase NEWSAPI_PAGE_SIZE for less evidence per claim
- Use fallback functions when speed > accuracy needed

## Rate Limits

### NewsAPI
- Free tier: 100 requests/day
- Paid: 250-1000/day depends on plan

### Gemini
- Free tier: Generally no hard limit, but may throttle
- Paid: Check your billing account

### Recommendations
- Monitor API usage in dashboards
- Add request queuing for high load
- Cache results when possible
- Set up alerts for rate limit approaches

---

For more details, see:
- [README.md](README.md) - Full setup guide
- [IMPLEMENTATION_NOTES.md](IMPLEMENTATION_NOTES.md) - Architecture details  
- [FILE_CHECKLIST.md](FILE_CHECKLIST.md) - File listing
- [backend/QUICKSTART.md](backend/QUICKSTART.md) - Quick start guide
