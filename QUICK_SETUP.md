# Quick Setup Guide — Trust Issues Extension

## Prerequisites

- Node.js 18+ (for building extension)
- Python 3.9+ (for backend)
- Chrome browser (for testing)
- Git

## Backend Setup (5 minutes)

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Run Server

```bash
python -m uvicorn app.main:app --reload
```

**Expected Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

### 3. Verify Health

```bash
# In another terminal
curl http://127.0.0.1:8000/health
# Response: {"status":"ok","backend":"ready"}
```

**If this fails:**
- Port 8000 might be in use: `lsof -i :8000` (macOS/Linux) or `netstat -ano | findstr :8000` (Windows)
- If so, kill the process or use different port: `--port 8001`

---

## Frontend Setup (10 minutes)

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Build Extension

```bash
npm run build
```

**Output:** Files in `frontend/dist/` folder

### 3. Load in Chrome

1. Open `chrome://extensions/`
2. Enable **Developer mode** (top right toggle)
3. Click **Load unpacked**
4. Select the `frontend/dist` folder
5. Verify "Trust Issues" extension appears

**Extension should show:**
- Icon in toolbar
- Available on all websites

---

## First Test (2 minutes)

### 1. Test Webpage

Navigate to any webpage with text content (e.g., news article)

### 2. Click Extension Icon

- Popup should open
- Should show "Analyze" button

### 3. Click "Analyze"

**Expected:**
- Loading state appears
- After 3-6 seconds, results show
- Credibility score displayed in popup

**If it fails:**
- See "Troubleshooting" section below

### 4. Verify Badge

- Look for badge in bottom-right with credibility score
- Click badge to re-open popup
- Badge disappears after 10 seconds

---

## Development Workflow

### Hot Reload (Backend)

Backend auto-reloads on file changes:

```bash
python -m uvicorn app.main:app --reload
```

### Rebuild Extension (Frontend)

```bash
npm run build
# Then in Chrome: chrome://extensions/ → reload Trust Issues
```

Or for continuous watch:

```bash
npm run watch  # If available in package.json
```

---

## Troubleshooting

### Issue: "Backend unreachable" Error

**Checklist:**
```bash
# 1. Verify backend is running
curl http://127.0.0.1:8000/health
# ✅ Should return {"status":"ok","backend":"ready"}
# ❌ If error, restart: python -m uvicorn app.main:app --reload

# 2. Check CORS in backend/app/main.py
# Should include localhost in allow_origins

# 3. Check extension manifest.json
# Should have "http://127.0.0.1/*" in host_permissions
```

### Issue: "Content too short" Error

**Solution:**
- Select more text (minimum 50 characters)
- On very short pages, scroll down to find more content

### Issue: Analysis Takes 30+ Seconds (Timeout)

**Possible Causes:**
- Backend pipeline is slow (check pipeline logs)
- Network latency
- Backend unreachable

**Solution:**
- Check backend terminal for errors
- Verify no other processes blocking port 8000
- Try smaller content

### Issue: Extension Shows Blank Popup

**Checklist:**
```bash
# 1. Rebuild extension
npm run build

# 2. Reload in Chrome
chrome://extensions/ → find Trust Issues → reload button

# 3. Check console error
# Open popup, right-click → Inspect → Console tab
# Look for red errors

# 4. Check service worker logs
# chrome://extensions/ → Trust Issues → 
#   Details → Service worker → Inspect views
```

### Issue: Content Not Being Extracted

**Verify Content Script:**

Open browser DevTools (F12) on any webpage:

```javascript
// In console, verify content script loaded
chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
  chrome.tabs.sendMessage(tabs[0].id, {
    type: 'REQUEST_PAGE_CONTENT'
  }, (response) => {
    console.log('Content extracted:', {
      url: response.url,
      contentLength: response.content.length,
      imageCount: response.images?.length || 0
    })
  })
})
```

**If this returns `undefined`:**
- Content script didn't load
- Check manifest.json `content_scripts` section
- Content script must match page URL

---

## Debug Mode

### Enable Verbose Logging

**Backend:**
```python
# In app/main.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Frontend Console:**

```javascript
// In popup, open DevTools and paste:
const originalLog = console.log;
console.log = function(...args) {
  originalLog('[POPUP]', ...args);
};
chrome.runtime.sendMessage({type: 'DEBUG_MODE'});
```

### View All Logs

**Service Worker Logs:**
```
chrome://extensions/ 
  → Trust Issues 
  → Service worker 
  → (inspect views link)
```

**Content Script Logs:**
1. Open any webpage
2. Right-click → Inspect
3. Console tab
4. Reload page with extension active

**API Traffic:**
1. Open DevTools (F12)
2. Network tab
3. Perform analysis
4. Look for requests to `/api/analyze`
5. Click to see request/response bodies

---

## Environment Variables

### Frontend (.env or .env.local)

```bash
# Optional: Override backend URL
REACT_APP_API_URL=http://127.0.0.1:8000
```

Default: `http://127.0.0.1:8000` (localhost)

### Backend (.env)

```bash
# Optional configuration
LOG_LEVEL=DEBUG
DATABASE_URL=sqlite:///./cache.db
```

---

## Common Commands

```bash
# Backend
cd backend
python -m uvicorn app.main:app --reload           # Start with auto-reload
python -m uvicorn app.main:app --port 8001        # Use different port
python -m pytest app/test/                        # Run tests

# Frontend
cd frontend
npm run build                                      # Build extension
npm run dev                                        # Dev mode (if available)
npm run lint                                       # Lint code
npm test                                           # Run tests

# Chrome Extensions
chrome://extensions/                               # Manage extensions
chrome://extensions/shortcut/                      # Set keyboard shortcut
```

---

## Next Steps

1. **Read [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)** for architecture details
2. **Check logs** when something breaks (always check logs first!)
3. **Modify backend pipeline** to customize analysis
4. **Add UI components** to customize popup display
5. **Deploy** (beyond scope of this guide)

---

## Support

**Check these in order:**

1. Browser console (DevTools → Console)
2. Service worker logs (chrome://extensions/ → inspect)
3. Backend terminal output
4. [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) troubleshooting section

All errors are logged with context for debugging!
