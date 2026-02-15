# 🚀 Trust Issues - Complete Setup Guide

## Quick Start (5 minutes)

### Step 1: Get API Keys (2 minutes)

1. **Gemini API Key** (Free!)
   - Visit: https://makersuite.google.com/app/apikey
   - Click "Create API Key"
   - Copy the key

2. **News API Key** (Free!)
   - Visit: https://newsapi.org/
   - Click "Get API Key"
   - Sign up (free tier: 100 requests/day)
   - Copy your API key

### Step 2: Configure Backend (1 minute)

1. Open `backend/.env` file
2. Replace the placeholders:
   ```env
   GEMINI_API_KEY=paste_your_actual_gemini_key_here
   NEWS_API_KEY=paste_your_actual_news_api_key_here
   ```
3. Save the file

### Step 3: Install Backend Dependencies (1 minute)

```bash
cd backend
pip install -r requirements.txt
```

Or if you prefer using a virtual environment:
```bash
# Windows
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# macOS/Linux
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 4: Start Backend Server (30 seconds)

```bash
# Make sure you're in the backend directory
cd backend

# Start the server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
✓ API keys configured correctly
✓ Backend ready!
```

Keep this terminal window open - the backend must be running!

### Step 5: Build & Load Extension (1 minute)

1. **Build the extension:**
   ```bash
   cd frontend
   npm install
   npm run build
   ```

2. **Load in Chrome:**
   - Open Chrome
   - Go to `chrome://extensions/`
   - Enable "Developer mode" (top right toggle)
   - Click "Load unpacked"
   - Select the `frontend/dist` folder

3. **Test it:**
   - Visit any news website (e.g., https://www.bbc.com/news)
   - Click the Trust Issues extension icon
   - Click "Scan Now"
   - Wait ~10-15 seconds for analysis

## ✅ Verification Checklist

### Backend is working if you see:
- ✓ Server starts without errors
- ✓ "API keys configured correctly" message
- ✓ Can access http://localhost:8000 in browser (shows `{"status":"backend running"}`)
- ✓ http://localhost:8000/health shows `{"status":"ok","backend":"ready"}`

### Extension is working if:
- ✓ Extension icon appears in Chrome toolbar
- ✓ Popup opens when clicked
- ✓ "Scan Now" button is visible
- ✓ After scanning, you see score bars and analysis

## 🔧 Troubleshooting

### Backend won't start?

**Error: "MISSING REQUIRED API KEYS"**
- Solution: Make sure you added real API keys to `backend/.env`

**Error: "Port 8000 is already in use"**
- Solution: Either kill the process using port 8000, or use a different port:
  ```bash
  python -m uvicorn app.main:app --reload --port 8001
  ```
  Then update `frontend/.env.local` with `REACT_APP_API_URL=http://localhost:8001`

**Error: "Module not found"**
- Solution: Make sure you installed dependencies: `pip install -r requirements.txt`

### Extension stuck on "Analyzing..."?

**Check 1: Is backend running?**
- Open http://localhost:8000/health in browser
- Should show: `{"status":"ok","backend":"ready"}`
- If not, restart the backend

**Check 2: Check browser console**
- Right-click extension popup → Inspect
- Look for errors in Console tab
- Common error: "Cannot reach backend" → Backend is not running

**Check 3: Rebuild extension**
```bash
cd frontend
npm run build
```
Then reload the extension in Chrome (click the reload icon on the extension card)

### Analysis fails with errors?

**Error: "Content too short"**
- Solution: You need at least 50 characters of text on the page

**Error: "Gemini API error"**
- Solution: Check your GEMINI_API_KEY is valid and has not exceeded free tier limits

**Error: "NewsAPI error"**
- Solution: Check your NEWS_API_KEY is valid (free tier: 100 requests/day)

## 📁 Project Structure

```
TrustIssues/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── routes/          # API endpoints
│   │   ├── pipeline/        # Analysis pipeline
│   │   │   ├── claim_extractor.py   # Extracts claims from content
│   │   │   ├── verifier.py          # Verifies claims with NewsAPI
│   │   │   └── summarizer.py        # Generates summary report
│   │   ├── clients/         # API clients
│   │   │   ├── gemini_client.py     # Gemini AI wrapper
│   │   │   └── news_client.py       # NewsAPI wrapper
│   │   └── core/            # Configuration
│   ├── .env                 # ← PUT YOUR API KEYS HERE!
│   └── requirements.txt
│
└── frontend/                # Browser extension
    ├── src/
    │   ├── background/      # Service worker
    │   ├── components/      # UI components
    │   └── services/        # API communication
    ├── public/
    │   └── dist/            # ← Load this in Chrome!
    └── package.json
```

## 🎯 How It Works

1. **User clicks "Scan Now"**
   - Extension captures current page content
   - Sends to background service worker

2. **Background worker requests analysis**
   - Calls backend API: POST /api/analyze
   - Passes page content, URL, title

3. **Backend processes content**
   - Extracts factual claims (using Gemini AI)
   - Verifies each claim (using NewsAPI)
   - Calculates credibility scores
   - Checks for AI-generated content patterns
   - Generates summary report

4. **Results displayed**
   - Score bars animate
   - Sources listed
   - Findings shown
   - Full report available

## 🔑 API Keys Explained

### Gemini API (Free Tier)
- **What it does**: Extracts claims, analyzes content, generates summaries
- **Free tier**: 60 requests/minute
- **Get it**: https://makersuite.google.com/app/apikey

### NewsAPI (Free Tier)
- **What it does**: Finds news articles to verify claims
- **Free tier**: 100 requests/day
- **Get it**: https://newsapi.org/

## 💡 Tips

1. **Keep backend running** - The extension won't work without it
2. **Check backend logs** - They show what's happening during analysis
3. **Use good content** - Try scanning news articles, blog posts (at least 50 chars)
4. **Free tier limits** - Be mindful of API usage limits

## 🐛 Still Having Issues?

1. Check backend terminal for error messages
2. Check browser console (F12) for frontend errors
3. Verify API keys are correct in `.env` file
4. Make sure both backend AND extension are running
5. Try a full rebuild:
   ```bash
   # Backend
   cd backend
   pip install -r requirements.txt --upgrade
   
   # Frontend
   cd frontend
   rm -rf node_modules dist
   npm install
   npm run build
   ```

## 📚 Additional Resources

- Backend API docs: http://localhost:8000/docs (when server is running)
- Gemini AI docs: https://ai.google.dev/docs
- NewsAPI docs: https://newsapi.org/docs
