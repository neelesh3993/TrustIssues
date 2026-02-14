# ✅ Getting Started Checklist

## Phase 1: Prepare API Keys (5-10 minutes)

- [ ] **Get Gemini API Key**
  - [ ] Visit https://makersuite.google.com/app/apikey
  - [ ] Click "Create API Key"
  - [ ] Copy the key to a safe place
  - [ ] Note: Free tier, no credit card needed

- [ ] **Get NewsAPI Key**
  - [ ] Visit https://newsapi.org/
  - [ ] Click "Get API Key"
  - [ ] Sign up with email
  - [ ] Copy the API key
  - [ ] Note: Free tier = 100 requests/day

## Phase 2: Configure Backend (5 minutes)

- [ ] **Create .env file**
  ```bash
  cd backend
  cp .env.example .env
  ```

- [ ] **Add API keys to .env**
  ```
  GEMINI_API_KEY=<paste your key here>
  NEWS_API_KEY=<paste your key here>
  ```

- [ ] **Optional: Configure other settings**
  - [ ] GEMINI_MODEL (default: gemini-1.5-flash - recommended)
  - [ ] MAX_CLAIMS (default: 5 - good for MVP)
  - [ ] NEWSAPI_PAGE_SIZE (default: 5 - good for MVP)

## Phase 3: Verify Setup (2 minutes)

- [ ] **Run verification script**
  ```bash
  python verify_setup.py
  ```

- [ ] **Expected output**
  - ✓ Python 3.8+ check
  - ✓ All dependencies found
  - ✓ .env file exists
  - ✓ Settings loaded successfully
  - ✓ "All checks passed!"

## Phase 4: Install Dependencies (2 minutes)

- [ ] **Install Python packages**
  ```bash
  pip install -r requirements.txt
  ```

- [ ] **Verify installation**
  ```bash
  python -c "import google.generativeai; print('✓ Gemini SDK installed')"
  python -c "import requests; print('✓ Requests installed')"
  python -c "from app.core.settings import get_settings; print('✓ Settings module works')"
  ```

## Phase 5: Run Backend (1 minute)

- [ ] **Start the server**
  ```bash
  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
  ```

- [ ] **Expected output**
  ```
  INFO:     Uvicorn running on http://0.0.0.0:8000
  INFO:     Application startup complete
  ✓ API keys configured correctly
  ✓ Backend ready!
  ```

- [ ] **In another terminal, test health check**
  ```bash
  curl http://localhost:8000/health
  ```
  Should return: `{"status":"ok","backend":"ready"}`

## Phase 6: Test the Pipeline (2-3 minutes)

- [ ] **Test analyze endpoint**
  ```bash
  curl -X POST http://localhost:8000/api/analyze \
    -H "Content-Type: application/json" \
    -d '{
      "url": "https://example.com",
      "content": "Paris is the capital of France and has about 2 million residents. The Eiffel Tower is 330 meters tall. Climate scientists say global temperatures are rising.",
      "title": "Paris and Climate Facts"
    }'
  ```

- [ ] **Expected response**
  - [ ] Status code: 200
  - [ ] Includes credibilityScore (0-100)
  - [ ] Includes findings array
  - [ ] Includes sources array
  - [ ] Includes report (summary)
  - [ ] Response looks valid JSON

- [ ] **Sample response structure**
  ```json
  {
    "aiGenerationLikelihood": 35.0,
    "credibilityScore": 75.5,
    "manipulationRisk": 40.0,
    "findings": [
      "✓ VERIFIED: Paris is the capital of France",
      "Mixed results in other claims"
    ],
    "sources": [
      {
        "name": "BBC",
        "headline": "About Paris",
        "status": "verified"
      }
    ],
    "report": "Analysis summary here..."
  }
  ```

## Phase 7: Run Tests (optional, 2 minutes)

- [ ] **Run test suite**
  ```bash
  pytest app/test/test_integration.py -v
  ```

- [ ] **Expected output**
  - [ ] Multiple test functions run
  - [ ] All tests pass (or most pass)
  - [ ] Test coverage shown

## Phase 8: Setup Extension Frontend (5-10 minutes)

- [ ] **Install frontend dependencies**
  ```bash
  cd frontend
  npm install
  ```

- [ ] **Build extension**
  ```bash
  npm run build
  ```

- [ ] **Load in Chrome**
  - [ ] Open `chrome://extensions/`
  - [ ] Toggle "Developer mode" (top right)
  - [ ] Click "Load unpacked"
  - [ ] Select your `frontend` folder
  - [ ] Extension should appear in list

- [ ] **Test extension**
  - [ ] Navigate to any website
  - [ ] Highlight some text (50+ characters)
  - [ ] Click extension icon
  - [ ] Click "Scan Text"
  - [ ] Should see analysis results

## Phase 9: Demo Preparation (optional)

### Test with Different Content

- [ ] **Test 1: News-like content**
  ```
  This content will likely be "verified" 
  because it mirrors real news sources
  ```

- [ ] **Test 2: False/disputed claims**
  ```
  This content will likely be "disputed" 
  when it contradicts known information
  ```

- [ ] **Test 3: Vague claims**
  ```
  This content will likely be "uncertain" 
  when evidence is inconclusive
  ```

### Performance Notes

- [ ] First request: ~15-20 seconds (API calls in sequence)
- [ ] Typical request: ~8-15 seconds
- [ ] Subsequent requests with same claim: Might be faster (if cached)

### Known Limitations

- [ ] NewsAPI free tier: 100 requests/day limit
- [ ] Gemini responses sometimes need refinement (see logs)
- [ ] Evidence quality depends on what's in news
- [ ] First setup takes slightly longer for API warmup

## 🆘 Troubleshooting Checklist

### API Keys Not Recognized

- [ ] Verify .env file exists in `backend/` directory
- [ ] Check for extra spaces in .env file
- [ ] Verify keys don't have quotes around them
- [ ] Run `python verify_setup.py` to diagnose
- [ ] Try setting as environment variables instead

### Backend Won't Start

- [ ] Run `python verify_setup.py`
- [ ] Check Python version: `python --version` (need 3.8+)
- [ ] Check dependencies: `pip list | grep fastapi`
- [ ] Try: `pip install -r requirements.txt --force-reinstall`

### Health Check Fails

- [ ] Verify backend is running
- [ ] Check if port 8000 is in use: `lsof -i :8000`
- [ ] Try different port: `uvicorn app.main:app --port 8001`

### Analyze Endpoint Returns 500

- [ ] Check backend terminal for error message
- [ ] Run `python verify_setup.py` to check config
- [ ] Verify API keys are valid
- [ ] Check API rate limits (NewsAPI: 100/day free)

### Extension Not Loading

- [ ] Verify `frontend/` folder exists
- [ ] Check `developer mode` is enabled in Chrome
- [ ] Try: `npm run build` in frontend folder
- [ ] Check Chrome extensions page for errors

### No Results Returned

- [ ] Content must be minimum 50 characters
- [ ] Ensure backend is running and healthy
- [ ] Check NewsAPI daily limit (100 requests/day)
- [ ] Look at backend terminal for error logs

## 📋 Configuration Verification

After each phase, verify:

- [ ] Backend runs without crashing
- [ ] Health check returns 200 status
- [ ] Analyze endpoint works (returns 200, valid JSON)
- [ ] Results include all required fields
- [ ] No error message in console

## 🎉 Success Indicators

You know everything is working when:

1. ✅ `python verify_setup.py` shows all checks pass
2. ✅ Health check returns `{"status":"ok","backend":"ready"}`
3. ✅ Analyze endpoint returns meaningful scores (0-100)
4. ✅ API response includes verified/disputed/uncertain claims
5. ✅ Extension loads in Chrome without errors
6. ✅ Highlighting text and clicking extension works
7. ✅ Analysis appears in extension popup (no errors)

## 📚 Documentation to Review

After setup works:

1. **[README.md](README.md)** - Complete setup & troubleshooting
2. **[CODE_REFERENCES.md](CODE_REFERENCES.md)** - Code examples
3. **[IMPLEMENTATION_NOTES.md](IMPLEMENTATION_NOTES.md)** - Architecture
4. **[backend/QUICKSTART.md](backend/QUICKSTART.md)** - Quick reference

## 🚀 Ready to Demo?

Once all checks pass:

1. Open a webpage with interesting content
2. Highlight a paragraph
3. Click the extension icon
4. Watch it analyze in real-time
5. Share the clean interface showing credibility

## 📞 Quick Commands Reference

```bash
# Verify setup
python verify_setup.py

# Install dependencies
pip install -r requirements.txt

# Run backend
uvicorn app.main:app --reload

# Test health
curl http://localhost:8000/health

# Run tests
pytest app/test/test_integration.py -v

# Check Python version
python --version

# Check installed packages
pip list | grep -E "fastapi|pydantic|google|requests"
```

## ⏱️ Time Estimates

| Phase | Time | Status |
|-------|------|--------|
| Get API keys | 5-10 min | - |
| Configure backend | 5 min | - |
| Verify setup | 2 min | - |
| Install dependencies | 2 min | - |
| Run backend | 1 min | - |
| Test pipeline | 2-3 min | - |
| Run tests | 2 min | - |
| Setup extension | 5-10 min | - |
| **TOTAL** | **25-35 min** | - |

## 🏁 Final Verification

When ready, run:

```bash
# Terminal 1: Backend
cd backend
python verify_setup.py
uvicorn app.main:app --reload

# Terminal 2: Test
curl http://localhost:8000/health
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"url":"https://test.com","content":"Paris is the capital of France and has 2 million people.","title":"Test"}'
```

**If both commands succeed, you're ready to go!** 🎉

---

**Next steps:** Follow the integration guide to connect the extension to this backend.

Questions? See [README.md](README.md) Troubleshooting section.
