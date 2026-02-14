# Quick Start: Setting Up TrustIssues Backend

## 1-Minute Setup (For Experienced Developers)

### Get API Keys
```bash
# Gemini - Quick 2-minute setup
# https://makersuite.google.com/app/apikey (click button, copy key)

# NewsAPI - Quick 1-minute signup  
# https://newsapi.org/ (sign up, copy key)
```

### Configure Backend
```bash
cd backend
cp .env.example .env
# Edit .env and add your two API keys

# Verify setup
python verify_setup.py

# Install dependencies
pip install -r requirements.txt

# Run backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Test It Works
```bash
# In another terminal
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "content": "Paris is the capital of France and has a population of about 2 million people. The Eiffel Tower stands 330 meters tall.",
    "title": "Paris Facts"
  }'
```

## File Structure Quick Reference

```
backend/
├── app/
│   ├── core/
│   │   └── settings.py          ← Configuration settings
│   ├── clients/
│   │   ├── gemini_client.py     ← LLM wrapper
│   │   └── news_client.py       ← NewsAPI wrapper
│   ├── pipeline/
│   │   ├── claim_extractor.py   ← Extract claims (Gemini)
│   │   ├── verifier.py          ← Verify claims (Gemini + NewsAPI)
│   │   └── summarizer.py        ← Generate summary (Gemini)
│   ├── routes/
│   │   └── analyze.py           ← /api/analyze endpoint
│   └── main.py                  ← FastAPI app
├── requirements.txt             ← Dependencies
├── verify_setup.py              ← Verification script
└── .env                         ← Your API keys (created by you)

.env.example                     ← Template for .env
README.md                        ← Full setup guide
```

## What Each File Does

### Core Pipeline
- **claim_extractor.py**: Uses Gemini to find 3-5 verifiable claims
- **verifier.py**: Uses NewsAPI to find evidence, Gemini to classify
- **summarizer.py**: Uses Gemini to write human-readable summary

### Smart Features
- ✓ **Fallbacks**: Works even if Gemini/NewsAPI temporarily fails
- ✓ **JSON Parsing**: Automatically handles Gemini's various response formats
- ✓ **Error Messages**: Clear instructions if API keys are missing
- ✓ **Rate Limiting**: Respects API limits gracefully
- ✓ **Logging**: Detailed logs for debugging

## Common Issues & Fixes

### "MISSING REQUIRED API KEYS"
```
Solution: Add keys to .env file (you created via .env.example)
```

### "No module named 'google.generativeai'"
```
Solution: Run: pip install -r requirements.txt
```

### "Connection refused" (can't connect to backend)
```
Solution: Make sure you ran: uvicorn app.main:app --reload
```

### News search returns no results
```
Solution: This is expected sometimes. The system continues gracefully.
         The verification will mark the claim as "uncertain".
```

## Testing the Pipeline

### Extract a claim
```python
from app.pipeline.claim_extractor import extract_claims
claims = extract_claims("Paris is the capital of France with 2 million people.")
# Returns: ["Paris is the capital of France with 2 million people."]
```

### Verify a claim
```python
from app.pipeline.verifier import verify_claims
results = verify_claims(["Paris is the capital of France"])
# Returns: [{"status": "verified", "rationale": "...", "sources": [...]}]
```

### Generate a summary
```python
from app.pipeline.summarizer import generate_summary
summary = generate_summary(content, claims, verification_results)
# Returns: "Most claims were verified. Content is credible."
```

## Settings Reference

All these can be set in `.env` or as environment variables:

| Setting | Default | Example | Purpose |
|---------|---------|---------|---------|
| GEMINI_API_KEY | Required | sk-xxx... | Your Gemini API key |
| NEWS_API_KEY | Required | abc123... | Your NewsAPI key |
| GEMINI_MODEL | gemini-1.5-flash | gemini-pro | Which Gemini model to use |
| NEWSAPI_ENDPOINT | official URL | https://... | Where to call NewsAPI |
| NEWSAPI_PAGE_SIZE | 5 | 10 | Articles per search |
| NEWSAPI_LANGUAGE | en | es | Language for searches |
| REQUEST_TIMEOUT_SECONDS | 20 | 30 | API timeout limit |
| MAX_CLAIMS | 5 | 10 | Max claims to extract |

## Running Tests

```bash
# Run all tests
pytest app/test/ -v

# Run specific test
pytest app/test/test_integration.py::TestSettings -v

# Run with coverage
pytest app/test/ --cov=app
```

## Docker Setup (Optional)

```dockerfile
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
ENV GEMINI_API_KEY=your_key_here
ENV NEWS_API_KEY=your_key_here
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
```

```bash
docker build -t trustissues .
docker run -p 8000:8000 -e GEMINI_API_KEY=xxx -e NEWS_API_KEY=yyy trustissues
```

## Next Steps

1. ✓ Set up backend (you're here)
2. → Follow frontend setup in main README.md
3. → Load extension in Chrome
4. → Test with real webpages
5. → Share feedback!

## Documentation Links

- [Full Setup Guide](README.md)
- [Implementation Details](IMPLEMENTATION_NOTES.md)
- [File Checklist](FILE_CHECKLIST.md)
- [API Contract](API_CONTRACT.md)

## Support

- Run `python verify_setup.py` for diagnostics
- Check logs in terminal where uvicorn is running
- Review `README.md` Troubleshooting section
