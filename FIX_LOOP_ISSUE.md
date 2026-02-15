# 🚨 STUCK IN LOOP? READ THIS FIRST!

## The Problem

Your extension shows "Analyzing..." forever and never completes.

## The Root Cause

**99% of the time, this means the backend API server is not running or cannot be reached.**

---

## ✅ THE FIX (5 Minutes)

### Step 1: Fix CORS Issue (Already Done!)

I've updated `backend/app/main.py` to fix CORS. The backend can now accept requests from the extension.

### Step 2: Start Backend Server

```powershell
cd C:\Users\moksh\OneDrive\Documents\GitHub\TrustIssues\backend
python -m uvicorn app.main:app --reload
```

**YOU MUST SEE THIS:**
```
✓ API keys configured correctly
✓ Backend ready!
INFO: Uvicorn running on http://0.0.0.0:8000
```

**KEEP THIS WINDOW OPEN!** The backend must stay running.

### Step 3: Verify Backend Works

Open in Chrome: **http://localhost:8000/health**

Should show:
```json
{"status":"ok","backend":"ready"}
```

### Step 4: Test Backend Thoroughly

Open in Chrome: `backend/test_backend.html`

**All tests should be GREEN ✓**

If any are RED ✗, fix those issues first!

### Step 5: Rebuild Extension (If Needed)

```powershell
cd C:\Users\moksh\OneDrive\Documents\GitHub\TrustIssues\frontend
npm run build
```

### Step 6: Reload Extension in Chrome

1. Go to `chrome://extensions/`
2. Find "Trust Issues"
3. Click the **reload icon** (circular arrow)

### Step 7: Test It!

1. Visit: https://www.bbc.com/news
2. Click Trust Issues extension icon
3. Click "Scan Now"
4. **Watch the backend terminal** - you should see:
   ```
   INFO: 127.0.0.1:xxxxx - "POST /api/analyze HTTP/1.1" 200 OK
   ```
5. Wait 10-15 seconds
6. Results should appear!

---

## 🔍 Still Stuck? Debug It:

### Check #1: Backend Terminal

Look at the terminal running the backend. Do you see error messages when you click "Scan Now"?

**Common errors:**
- `Invalid API key` → Add real keys to `backend/.env`
- `Port 8000 already in use` → Kill other process or use different port
- `Module not found` → Run `pip install -r requirements.txt`

### Check #2: Extension Console

1. Right-click extension icon → "Inspect popup"
2. Go to Console tab
3. Click "Scan Now"
4. Look for errors

**What you should see:**
```
[Service Worker] Starting analysis...
[API] Starting analysis request
[Service Worker] Analysis complete
```

**Bad signs:**
```
Failed to fetch
NetworkError  
Cannot reach backend
```

→ This means backend isn't running or CORS is blocking it.

### Check #3: Service Worker Console

1. Go to `chrome://extensions/`
2. Find "Trust Issues"
3. Click "service worker" (blue link)
4. Check Console tab

**What you should see:**
```
[Service Worker] Backend is healthy
[Service Worker] Received message: ANALYZE_PAGE
[Service Worker] Starting analysis for https://...
[Service Worker] Analysis complete
```

---

## 🎯 Expected Full Flow

### 1. Backend Terminal Shows:
```
✓ Backend ready!
INFO: Uvicorn running on http://0.0.0.0:8000
```

### 2. Click "Scan Now" in Extension

### 3. Backend Terminal Shows:
```
INFO: 127.0.0.1:55001 - "POST /api/analyze HTTP/1.1" 200 OK
[Gemini] Extracting claims from content...
[NewsAPI] Searching for evidence...
[Gemini] Generating summary...
```

### 4. Extension Shows Results:
- Score bars animate
- Sources listed
- Findings shown
- Report displayed

---

## 📋 Pre-Flight Checklist

Before clicking "Scan Now":

- ☐ Backend running? (Check terminal shows "Backend ready!")
- ☐ http://localhost:8000/health works?
- ☐ test_backend.html all green ✓?
- ☐ API keys added to backend/.env?
- ☐ Extension loaded in chrome://extensions/?
- ☐ Extension enabled?

---

## 🚀 Quick Start Script

For easiest setup, just run:

```powershell
START_ALL.bat
```

This will:
1. Check your API keys
2. Start backend
3. Test backend
4. Open diagnostic tool
5. Tell you next steps

---

## 📊 Diagnostic Tool Results

Open `backend/test_backend.html` and check results:

| Test | Expected Result |
|------|----------------|
| Backend Root | ✓ GREEN |
| Backend Health | ✓ GREEN |
| CORS Headers | ✓ GREEN |
| Analysis API | ✓ GREEN |
| API Docs | ✓ GREEN |

If ANY are RED, fix that issue before proceeding!

---

## 💡 Common Mistakes

### Mistake #1: Backend Not Running
**Symptom:** Extension stuck on "Analyzing..."
**Fix:** Start backend server (see Step 2)

### Mistake #2: Wrong API Keys
**Symptom:** Backend shows "Invalid API key" error
**Fix:** Add REAL keys to `backend/.env`

### Mistake #3: Old Extension Build
**Symptom:** Changes don't take effect
**Fix:** `npm run build` and reload extension

### Mistake #4: Firewall Blocking
**Symptom:** Backend running but extension can't reach it
**Fix:** Allow port 8000 in firewall

### Mistake #5: Port Already in Use
**Symptom:** Backend won't start, says "port in use"
**Fix:** Kill other process or use `--port 8001`

---

## 🆘 Emergency Reset

If nothing works, do a full reset:

```powershell
# Stop everything (Ctrl+C in all terminals)

# Backend: Clean install
cd backend
pip install --upgrade pip
pip install fastapi uvicorn pydantic pydantic-settings python-dotenv requests google-generativeai

# Add API keys to .env

# Start backend
python -m uvicorn app.main:app --reload

# Frontend: Clean build
cd frontend
Remove-Item -Recurse -Force node_modules, dist
npm install --legacy-peer-deps
npm run build

# Chrome: Remove and re-add extension
# chrome://extensions/ → Remove → Load unpacked → Select frontend/dist
```

---

## ✅ Success Looks Like This:

**Backend Terminal:**
```
✓ Backend ready!
INFO: Uvicorn running on http://0.0.0.0:8000
INFO: 127.0.0.1:55001 - "POST /api/analyze HTTP/1.1" 200 OK
```

**Extension:**
```
[Scan Now button] → [Analyzing...] → [Score bars appear] → [Sources and findings shown]
```

**Time:** 10-15 seconds from click to results

---

## 📖 More Help

- **Full setup guide:** `SETUP_COMPLETE.md`
- **Detailed debugging:** `DEBUGGING_LOOP_ISSUE.md`
- **Quick commands:** `QUICK_REFERENCE.md`
- **Troubleshooting:** `TROUBLESHOOTING.md`

---

**Remember:** The backend is a separate server that MUST be running for the extension to work. Think of it like this:

- Extension = The UI (what you see)
- Backend = The brain (does the analysis)

If the brain isn't running, the UI can't get answers!

**Key Insight:** When you click "Scan Now", the extension sends the page content to `http://localhost:8000/api/analyze`. If that server isn't running, the request fails and you get stuck in a loop.

---

**Next:** Run `START_ALL.bat` to start everything automatically!
