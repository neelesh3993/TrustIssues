# 🎯 Trust Issues - Quick Reference Card

## 🚀 **First Time Setup** (Do this once)

### 1. Get Your API Keys
- **Gemini**: https://makersuite.google.com/app/apikey (Free, instant)
- **NewsAPI**: https://newsapi.org/ (Free, 100 requests/day)

### 2. Add Keys to `.env` file
```bash
# Edit: backend/.env
GEMINI_API_KEY=your_actual_gemini_key_here
NEWS_API_KEY=your_actual_news_key_here
```

### 3. Install Dependencies
```bash
cd backend
pip install -r requirements.txt

cd frontend
npm install
```

---

## 💻 **Daily Workflow** (Every time you use it)

### Start Backend (Required!)
```bash
cd backend
python -m uvicorn app.main:app --reload
```
**Or double-click:** `backend/start_server.bat` (Windows) or `backend/start_server.sh` (Mac/Linux)

### Build Extension (After code changes)
```bash
cd frontend
npm run build
```

### Load Extension in Chrome
1. Go to `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select `frontend/dist` folder

---

## ✅ **Quick Health Check**

### Is Backend Running?
Visit: http://localhost:8000/health
Should show: `{"status":"ok","backend":"ready"}`

### Test Backend Setup
```bash
cd backend
python test_setup.py
```

### Check Extension
- Click extension icon in Chrome
- Should see "Trust Issues" popup
- "Scan Now" button should be visible

---

## 🐛 **Common Issues & Fixes**

| Problem | Solution |
|---------|----------|
| **Backend won't start** | Check API keys in `.env` file |
| **"Cannot reach backend"** | Make sure backend server is running |
| **Stuck on "Analyzing..."** | Restart backend, check browser console (F12) |
| **"Module not found"** | Run `pip install -r requirements.txt` |
| **Port 8000 in use** | Use different port: `--port 8001` |
| **Extension not working** | Rebuild: `npm run build`, reload extension |

---

## 📊 **Backend Status Codes**

| URL | What It Shows |
|-----|---------------|
| http://localhost:8000 | `{"status":"backend running"}` |
| http://localhost:8000/health | `{"status":"ok","backend":"ready"}` |
| http://localhost:8000/docs | Interactive API documentation |

---

## 🎨 **Project Structure**

```
TrustIssues/
├── backend/
│   ├── .env                 ← Your API keys go here!
│   ├── start_server.bat     ← Double-click to start (Windows)
│   ├── start_server.sh      ← Run to start (Mac/Linux)
│   ├── test_setup.py        ← Run to verify setup
│   └── app/
│       ├── routes/          ← API endpoints (/api/analyze)
│       ├── pipeline/        ← Analysis logic
│       └── clients/         ← Gemini & NewsAPI wrappers
│
└── frontend/
    ├── dist/                ← Load this in Chrome!
    └── src/
        ├── background/      ← Service worker
        └── components/      ← UI components
```

---

## 🔑 **API Key Limits**

### Gemini (Free Tier)
- **Limit**: 60 requests/minute
- **Cost**: Free
- **Upgrade**: https://ai.google.dev/pricing

### NewsAPI (Free Tier)
- **Limit**: 100 requests/day
- **Cost**: Free
- **Upgrade**: https://newsapi.org/pricing

---

## 📝 **Key Files**

| File | Purpose |
|------|---------|
| `backend/.env` | **Your API keys** (never commit this!) |
| `backend/test_setup.py` | Test everything is working |
| `backend/app/main.py` | Backend server entry point |
| `backend/app/routes/analyze.py` | Main analysis endpoint |
| `frontend/src/background/service-worker.ts` | Handles extension logic |
| `frontend/src/components/popup.tsx` | Main UI component |

---

## 🎯 **Usage Example**

1. **Start backend:**
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload
   ```
   ✓ See: "✓ Backend ready!"

2. **Load extension in Chrome:**
   - Chrome → Extensions → Load unpacked → Select `frontend/dist`

3. **Test it:**
   - Visit: https://www.bbc.com/news
   - Click Trust Issues icon
   - Click "Scan Now"
   - Wait ~10-15 seconds
   - See analysis results!

---

## 🆘 **Need Help?**

1. **Run diagnostics:** `python backend/test_setup.py`
2. **Check logs:** Look at backend terminal output
3. **Browser console:** Right-click popup → Inspect → Console tab
4. **Read full guide:** `SETUP_COMPLETE.md`

---

## 🚦 **Status Indicators**

### Backend Terminal Shows:
```
✓ API keys configured correctly
✓ Backend ready!
INFO: Uvicorn running on http://0.0.0.0:8000
```
→ **Everything is good!**

### Extension Shows:
- **Idle**: "Scan Now" button visible
- **Analyzing**: Loading animation
- **Done**: Score bars, findings, sources
- **Error**: Red error message

---

## 📦 **File Sizes**

- Backend: ~50 MB (with dependencies)
- Frontend: ~200 MB (with node_modules)
- Extension: ~1 MB (built)

---

## ⚡ **Performance Tips**

- **First scan**: May take 15-20 seconds (cold start)
- **Subsequent scans**: 5-10 seconds (warm)
- **Cache**: Results cached for 1 hour per URL
- **Optimal content**: 200-2000 words

---

## 🔒 **Privacy & Security**

- **Data sent**: URL, page content, title
- **Data stored**: Analysis results (local cache only)
- **API keys**: Stored locally in `.env` (never shared)
- **No tracking**: No analytics or telemetry

---

**Version**: 1.0.0 | **Last Updated**: February 2025
