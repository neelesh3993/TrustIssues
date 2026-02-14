# Quick Start Guide - Trust Issues Browser Extension

## 🎯 What You Now Have

A fully functional browser extension architecture that:
- Extracts webpage content
- Sends it to a backend API for analysis
- Returns credibility scores, AI detection, findings, and source verification
- Caches results to avoid redundant analysis
- Works offline with cached data

## ⚡ 5-Minute Setup

### 1️⃣ Start the Backend

```bash
# Open Terminal 1
cd TrustIssues/backend

# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start server
python -m uvicorn app.main:app --reload --port 8000
```

✅ You should see: `Uvicorn running on http://127.0.0.1:8000`

### 2️⃣ Build the Extension

```bash
# Open Terminal 2
cd TrustIssues/frontend

# Install dependencies (first time only)
# Ensure you install new devDeps (Vite + plugin) after package.json was updated
npm install

# Build extension files (Vite bundles popup/background/content into public/src)
npm run build:extension
```

✅ Check: `frontend/public/` now contains `.js` files

### 3️⃣ Load in Chrome

1. Open **chrome://extensions/**
2. Toggle **Developer mode** (top right)
3. Click **Load unpacked**
4. Select: `TrustIssues/frontend/public/`
5. ✅ Extension appears in toolbar!

## 🧪 Test It Out

1. Go to any webpage (e.g., Google, Wikipedia, Medium)
2. Click the **Trust Issues** icon (should be in top right)
3. Click **"Scan This Page"**
4. Wait ~2-3 seconds for backend response
5. See results: scores, findings, sources, report

## 📊 What the Backend Does

When you click "Scan":
- Extracts claims from the page
- Checks against fact-checking sources
- Analyzes for AI-generated patterns
- Calculates manipulation risk
- Returns all findings in 1 response

**API Endpoint:** `POST /api/analyze`

Try it manually:
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "content": "This is an example article about important news with multiple sentences...",
    "title": "Example Article"
  }'
```

## 🔧 Troubleshooting

### Extension not showing results?
1. Check backend is running: Visit `http://localhost:8000/docs`
2. Open popup DevTools: Right-click extension → Inspect popup
3. Check Network tab: Is API call succeeding?

### Backend error?
1. Check console output (any Python errors?)
2. Verify `.env` file has correct settings
3. Try health check: `curl http://localhost:8000/health`

### Extension not loading?
1. Clear cache: chrome://extensions/ → Clear data
2. Rebuild extension: `npm run build:extension`
3. Reload extension (⟲ button in chrome://extensions/)

## 📁 Key Files Explained

| File | Purpose |
|------|---------|
| `manifest.json` | Extension configuration (permissions, UI) |
| `service-worker.ts` | Message handler, API calls, caching |
| `content-script.ts` | Extracts page content & data |
| `popup.tsx` | React component shown in extension |
| `api.ts` | Backend API communication |
| `main.py` | FastAPI app & `/api/analyze` endpoint |

## 🚀 Next: What to Implement

1. **Improve ML Models** (in pipeline/):
   - Use transformers for actual AI detection
   - Integrate real fact-checking APIs (NewsAPI, FactCheck.org)
   - Add NLP for claim extraction

2. **Backend Enhancements**:
   - Database for storing analysis history
   - Rate limiting to prevent abuse
   - User authentication

3. **Extension UI**:
   - Settings page (configure API, notifications)
   - History of scanned pages
   - Keyboard shortcuts (Ctrl+Shift+X)
   - Export analysis as PDF

4. **Security**:
   - API key management
   - HTTPS in production
   - CSP headers

## 📚 Useful Links

- [Chrome Extension Docs](https://developer.chrome.com/docs/extensions/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [React Hooks Guide](https://react.dev/reference/react)
- [Manifest v3 Tutorial](https://developer.chrome.com/docs/extensions/mv3/getstarted/)

## ✨ You're Ready!

Your extension is functional and connected. Now you can:
- Add real ML models for better analysis
- Integrate actual fact-checking APIs
- Build out the UI/UX features
- Test with real-world articles

Questions? Check `EXTENSION_SETUP.md` for detailed architecture info.
