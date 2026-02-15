# 🛡️ Trust Issues - Web Content Credibility Analyzer

A Chrome extension that analyzes web content for credibility, AI-generation likelihood, and manipulation risk using Gemini AI and NewsAPI.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.10+-blue)
![Node](https://img.shields.io/badge/node-18+-green)

## 🎯 What It Does

Trust Issues scans any webpage and provides:
- **AI Generation Detection**: Estimates likelihood content was AI-written (0-100%)
- **Credibility Scoring**: Verifies claims against trusted news sources (0-100%)
- **Manipulation Risk**: Detects emotional language and bias patterns (0-100%)
- **Fact Checking**: Extracts claims and validates them with NewsAPI
- **Source Analysis**: Lists supporting/contradicting sources
- **Detailed Report**: Human-readable summary of findings

## 📸 Screenshot

```
┌─────────────────────────────────────┐
│ TRUST ISSUES                        │
│ Web Content Investigation Tool      │
├─────────────────────────────────────┤
│ AI-Generated Content   [████░░] 78% │
│ Credibility Score      [██░░░░] 42% │
│ Manipulation Risk      [████░░] 65% │
├─────────────────────────────────────┤
│ CASE REPORT                         │
│ Subject page contains content with  │
│ high probability of AI-assisted     │
│ generation. Cross-referencing with  │
│ verified news agencies yields...    │
├─────────────────────────────────────┤
│ SOURCES CHECKED                     │
│ ✓ Reuters - Fact-check database     │
│ ⚠ BBC News - Partial match          │
│ ✗ Snopes - No matching claim        │
└─────────────────────────────────────┘
```

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- Python 3.10+
- Node.js 18+
- Chrome browser
- API keys (free!)

### 1. Get API Keys

**Gemini API** (Free - 60 requests/minute)
- Visit: https://makersuite.google.com/app/apikey
- Click "Create API Key"
- Copy the key

**NewsAPI** (Free - 100 requests/day)
- Visit: https://newsapi.org/
- Sign up for free
- Copy your API key

### 2. Configure Backend

```bash
# Navigate to backend directory
cd backend

# Edit .env file and add your keys:
GEMINI_API_KEY=your_actual_gemini_key_here
NEWS_API_KEY=your_actual_news_key_here
```

### 3. Install & Run Backend

```bash
# Install dependencies
pip install -r requirements.txt

# Test setup (optional but recommended)
python test_setup.py

# Start server
python -m uvicorn app.main:app --reload
```

You should see:
```
✓ API keys configured correctly
✓ Backend ready!
INFO: Uvicorn running on http://0.0.0.0:8000
```

**Keep this terminal window open!**

### 4. Build Extension

```bash
# In a new terminal, navigate to frontend
cd frontend

# Install dependencies
npm install

# Build extension
npm run build
```

### 5. Load Extension in Chrome

1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode" (toggle in top right)
3. Click "Load unpacked"
4. Select the `frontend/dist` folder
5. Pin the extension to your toolbar

### 6. Test It!

1. Visit any news website (e.g., https://www.bbc.com/news)
2. Click the Trust Issues extension icon
3. Click "Scan Now"
4. Wait ~10-15 seconds
5. View the analysis results!

## 🏗️ Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Browser    │────▶│   Chrome     │────▶│   FastAPI    │
│   Content    │     │  Extension   │     │   Backend    │
└──────────────┘     └──────────────┘     └──────────────┘
                            │                     │
                            │                     ▼
                            │              ┌─────────────┐
                            │              │  Gemini AI  │
                            │              └─────────────┘
                            │                     │
                            │                     ▼
                            │              ┌─────────────┐
                            └──────────────│  NewsAPI    │
                                          └─────────────┘
```

### Data Flow

1. **User Action**: Clicks "Scan Now" on any webpage
2. **Content Extraction**: Content script grabs page text
3. **Background Processing**: Service worker sends to backend
4. **AI Analysis**: 
   - Gemini extracts factual claims
   - NewsAPI retrieves evidence
   - Gemini verifies each claim
   - Gemini generates summary
5. **Results Display**: Popup shows scores, sources, findings

## 📁 Project Structure

```
TrustIssues/
├── backend/                        # FastAPI Backend
│   ├── app/
│   │   ├── routes/
│   │   │   └── analyze.py          # Main API endpoint
│   │   ├── pipeline/
│   │   │   ├── claim_extractor.py  # Extracts claims (Gemini)
│   │   │   ├── verifier.py         # Verifies claims (NewsAPI + Gemini)
│   │   │   └── summarizer.py       # Generates report (Gemini)
│   │   ├── clients/
│   │   │   ├── gemini_client.py    # Gemini API wrapper
│   │   │   └── news_client.py      # NewsAPI wrapper
│   │   ├── models/
│   │   │   └── schemas.py          # Pydantic models
│   │   └── core/
│   │       └── settings.py         # Configuration management
│   ├── .env                        # API keys (YOU ADD THESE!)
│   ├── requirements.txt            # Python dependencies
│   ├── test_setup.py               # Setup verification script
│   ├── start_server.bat            # Windows start script
│   └── start_server.sh             # Mac/Linux start script
│
├── frontend/                       # Chrome Extension
│   ├── src/
│   │   ├── background/
│   │   │   └── service-worker.ts   # Extension background logic
│   │   ├── components/
│   │   │   └── popup.tsx           # Main UI
│   │   ├── services/
│   │   │   └── api.ts              # Backend communication
│   │   └── hooks/
│   │       └── useAnalysis.ts      # Analysis state management
│   ├── public/
│   │   ├── manifest.json           # Extension manifest
│   │   └── dist/                   # Built extension (load this!)
│   └── package.json
│
├── SETUP_COMPLETE.md               # Detailed setup guide
├── QUICK_REFERENCE.md              # Quick reference card
└── README.md                       # This file
```

## 🔬 How It Works (Technical)

### Backend Pipeline

1. **Claim Extraction** (`claim_extractor.py`)
   ```
   Input: Raw page content
   Process: Gemini AI identifies 3-5 factual claims
   Output: ["Claim 1", "Claim 2", ...]
   ```

2. **Claim Verification** (`verifier.py`)
   ```
   For each claim:
     1. Search NewsAPI for evidence
     2. Gemini analyzes evidence
     3. Classify as: verified | disputed | uncertain
   ```

3. **Summary Generation** (`summarizer.py`)
   ```
   Input: Original content + verification results
   Process: Gemini generates human-readable report
   Output: "Content analysis identified: 2 verified claims..."
   ```

### API Endpoint

```http
POST /api/analyze
Content-Type: application/json

{
  "url": "https://example.com/article",
  "content": "The article text...",
  "title": "Article Title",
  "images": []  // Optional
}
```

**Response:**
```json
{
  "aiGenerationLikelihood": 78.0,
  "credibilityScore": 42.0,
  "manipulationRisk": 65.0,
  "findings": [
    "⚠️ DISPUTED: The Eiffel Tower is 500 meters tall",
    "✓ VERIFIED: Paris is the capital of France"
  ],
  "sources": [
    {
      "name": "Reuters",
      "headline": "Fact-check: Eiffel Tower height",
      "status": "disputed"
    }
  ],
  "report": "Content analysis identified: 1 verified claim(s)..."
}
```

## 🛠️ Development

### Backend Development

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

# Start with auto-reload
python -m uvicorn app.main:app --reload --log-level debug
```

### Frontend Development

```bash
# Install dependencies
npm install

# Development build (with watch)
npm run dev

# Production build
npm run build

# Type checking
npm run type-check
```

## 🧪 Testing

### Test Backend Setup
```bash
cd backend
python test_setup.py
```

This will verify:
- ✓ All packages installed
- ✓ .env file configured
- ✓ API keys valid
- ✓ Gemini API working
- ✓ NewsAPI working
- ✓ Pipeline functional

### Manual Testing

1. **Health Check**: Visit http://localhost:8000/health
2. **API Docs**: Visit http://localhost:8000/docs
3. **Test Analysis**: Use the interactive API docs

## 🐛 Troubleshooting

### Backend Issues

**Problem**: Server won't start
```
Error: MISSING REQUIRED API KEYS
```
**Solution**: Add real API keys to `backend/.env`

---

**Problem**: "Port 8000 already in use"
```bash
# Use different port
python -m uvicorn app.main:app --port 8001
```
Then update frontend: `REACT_APP_API_URL=http://localhost:8001` in `frontend/.env.local`

---

**Problem**: "Module not found"
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

### Extension Issues

**Problem**: Stuck on "Analyzing..."

**Check 1**: Is backend running?
- Open: http://localhost:8000/health
- Should show: `{"status":"ok","backend":"ready"}`

**Check 2**: Browser console errors
- Right-click popup → Inspect → Console tab
- Look for "Cannot reach backend" error

**Check 3**: Rebuild extension
```bash
cd frontend
npm run build
```
Then reload extension in Chrome

---

**Problem**: Extension not appearing

**Solution**: 
1. Go to `chrome://extensions/`
2. Enable "Developer mode"
3. Reload the extension
4. Check for errors

## 📊 API Key Limits

### Gemini API (Free Tier)
- **Requests**: 60 per minute
- **Tokens**: 1,500 requests per day
- **Cost**: Free
- **Upgrade**: https://ai.google.dev/pricing

### NewsAPI (Free Tier)
- **Requests**: 100 per day
- **Results**: Up to 100 per request
- **Cost**: Free (for development)
- **Upgrade**: https://newsapi.org/pricing

## 🔒 Privacy & Security

- **Data Sent to APIs**: URL, page content, and title only
- **Data Storage**: Analysis results cached locally (1 hour)
- **API Keys**: Stored in `.env` file (never committed to git)
- **No Tracking**: No analytics, telemetry, or third-party tracking
- **No Server Storage**: Results not stored on backend server

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Credits

- **Gemini AI**: Google's generative AI for claim extraction and analysis
- **NewsAPI**: News aggregation for fact verification
- **FastAPI**: Modern Python web framework
- **React**: UI framework
- **Vite**: Build tool

## 📚 Additional Resources

- [Detailed Setup Guide](SETUP_COMPLETE.md)
- [Quick Reference Card](QUICK_REFERENCE.md)
- [API Documentation](http://localhost:8000/docs) (when server is running)
- [Gemini AI Documentation](https://ai.google.dev/docs)
- [NewsAPI Documentation](https://newsapi.org/docs)

## 🆘 Support

1. **Run Diagnostics**: `python backend/test_setup.py`
2. **Check Logs**: Look at backend terminal output
3. **Browser Console**: Right-click popup → Inspect → Console
4. **Read Guides**: `SETUP_COMPLETE.md` and `QUICK_REFERENCE.md`

## 🎯 Roadmap

- [ ] Support for more languages
- [ ] Image analysis capabilities
- [ ] PDF document analysis
- [ ] Browser integration (Firefox, Edge)
- [ ] Advanced ML models for AI detection
- [ ] Real-time monitoring mode
- [ ] Export reports as PDF
- [ ] Custom fact-checking sources

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

---

**Made with ❤️ for truth and transparency**

**Version**: 1.0.0 | **Updated**: February 2025
