# 🐛 Trust Issues - Stuck in Loop? Fix It Now!

## Issue: Extension Stuck on "Analyzing..."

This usually means the frontend can't reach the backend. Let's fix it step by step.

---

## 🔍 Step 1: Is Backend Running?

Open a browser and visit: **http://localhost:8000/health**

### ✅ If you see: `{"status":"ok","backend":"ready"}`
→ Backend is running! Go to Step 2.

### ❌ If you see: "This site can't be reached" or similar error
→ Backend is NOT running!

**Fix:**
```powershell
cd backend
python -m uvicorn app.main:app --reload
```

Keep this terminal open! You should see:
```
✓ API keys configured correctly
✓ Backend ready!
INFO: Uvicorn running on http://0.0.0.0:8000
```

---

## 🔍 Step 2: Test Backend with Diagnostic Tool

1. **Open this file in Chrome:**
   ```
   backend/test_backend.html
   ```
   
2. **Wait for automatic tests to run**

3. **Check the results:**
   - All green ✓ = Backend working perfectly!
   - Any red ✗ = There's an issue

### Common Issues Found by Diagnostic Tool:

**❌ "Cannot connect to backend"**
→ Backend not running. Start it with:
```powershell
cd backend
python -m uvicorn app.main:app --reload
```

**❌ "Analysis failed with status 500"**
→ API keys not configured. Edit `backend/.env` and add:
```env
GEMINI_API_KEY=your_real_gemini_key
NEWS_API_KEY=your_real_news_key
```

**❌ "CORS blocking"**
→ Already fixed in the code! Just restart backend.

---

## 🔍 Step 3: Check Extension Console

1. **Right-click extension icon → "Inspect popup"**
2. **Go to "Console" tab**
3. **Look for errors**

### What to Look For:

**✅ Good messages:**
```
[Service Worker] Starting analysis...
[Service Worker] Analysis complete
```

**❌ Bad messages:**
```
Failed to fetch
NetworkError
Cannot reach backend
```

### Fix for "Failed to fetch":
- Make sure backend is running (Step 1)
- Restart backend after CORS fix
- Clear browser cache: Ctrl+Shift+Delete → Clear data

---

## 🔍 Step 4: Check Service Worker Console

1. Go to: **chrome://extensions/**
2. Find "Trust Issues"
3. Click "service worker" (blue link)
4. Check Console tab

### What to Look For:

**✅ Good:**
```
[Service Worker] Backend is healthy
[Service Worker] Analysis complete
```

**❌ Bad:**
```
Backend unreachable
Health check failed
Analysis timeout
```

---

## 🔧 Quick Fix Checklist

Try these in order:

### Fix 1: Restart Backend (Most Common Fix!)
```powershell
# Stop backend (Ctrl+C)
cd backend
python -m uvicorn app.main:app --reload
```

### Fix 2: Add API Keys
Edit `backend/.env`:
```env
GEMINI_API_KEY=paste_your_real_key_here
NEWS_API_KEY=paste_your_real_key_here
```

Then restart backend.

### Fix 3: Rebuild Extension
```powershell
cd frontend
npm run build
```

Then reload extension in Chrome (click reload icon in chrome://extensions/).

### Fix 4: Clear Everything and Start Fresh
```powershell
# Stop backend (Ctrl+C)

# Restart backend
cd backend
python -m uvicorn app.main:app --reload --log-level debug

# In a new terminal, rebuild extension
cd frontend  
npm run build

# Reload extension in Chrome
# chrome://extensions/ → Click reload icon
```

### Fix 5: Check Firewall
Make sure Windows Firewall isn't blocking port 8000:
```powershell
# In Admin PowerShell:
netsh advfirewall firewall add rule name="Trust Issues Backend" dir=in action=allow protocol=TCP localport=8000
```

---

## 🧪 Manual Test

Once backend is running, test it manually:

### Test 1: Backend Health
```powershell
curl http://localhost:8000/health
```

Should return: `{"status":"ok","backend":"ready"}`

### Test 2: Analysis Endpoint
```powershell
curl -X POST http://localhost:8000/api/analyze `
  -H "Content-Type: application/json" `
  -d '{\"url\":\"https://example.com\",\"content\":\"The Eiffel Tower is 330 meters tall and located in Paris, France.\",\"title\":\"Test\"}'
```

Should return JSON with scores and findings.

---

## 📋 Complete Startup Checklist

Use this every time:

1. ☐ **Backend running?**
   ```powershell
   cd backend
   python -m uvicorn app.main:app --reload
   ```

2. ☐ **API keys added to backend/.env?**
   - GEMINI_API_KEY=...
   - NEWS_API_KEY=...

3. ☐ **Backend responds to http://localhost:8000/health?**

4. ☐ **Extension built?**
   ```powershell
   cd frontend
   npm run build
   ```

5. ☐ **Extension loaded in Chrome?**
   - chrome://extensions/
   - Load unpacked → Select frontend/dist

6. ☐ **Extension enabled?**

---

## 🎯 Expected Behavior

When everything works:

1. **Click extension icon** → Popup opens
2. **Click "Scan Now"** → Shows "Analyzing..."
3. **Wait 10-15 seconds** → Loading animation
4. **Results appear** → Score bars, sources, findings

### Backend Terminal Should Show:
```
INFO: 127.0.0.1:xxxxx - "POST /api/analyze HTTP/1.1" 200 OK
[Analysis] Analyzing: https://example.com
[Analysis] Extracted 3 claims
[Analysis] Verification complete
```

---

## 🆘 Still Stuck?

### Check These Files:

1. **Backend logs** - Look at terminal running backend
2. **Extension console** - Right-click popup → Inspect → Console
3. **Service worker console** - chrome://extensions/ → service worker link

### Common Root Causes:

| Symptom | Cause | Fix |
|---------|-------|-----|
| Popup shows "Analyzing..." forever | Backend not running | Start backend |
| "Cannot reach backend" error | Wrong port / CORS issue | Restart backend after CORS fix |
| "Invalid API key" in backend logs | API keys wrong/missing | Add real keys to .env |
| Extension icon doesn't appear | Extension not loaded | Load in chrome://extensions/ |
| "Content too short" error | Page has < 50 characters | Try a news article |

---

## 💡 Pro Tips

1. **Keep backend terminal visible** - You'll see errors immediately
2. **Use test_backend.html** - Quick way to verify backend
3. **Check both consoles** - Popup AND service worker
4. **Try a known-good page** - Like https://www.bbc.com/news
5. **Wait full 15 seconds** - First analysis takes longer

---

## 📞 Debug Command Summary

```powershell
# Check if backend is reachable
curl http://localhost:8000/health

# View API docs
start http://localhost:8000/docs

# Restart backend with debug logs
cd backend
python -m uvicorn app.main:app --reload --log-level debug

# Rebuild extension
cd frontend
npm run build

# Test backend
start backend/test_backend.html
```

---

**Remember:** Backend MUST be running for extension to work!

If you've tried everything and it's still stuck, run the diagnostic tool (`test_backend.html`) and check what specific errors you're getting.
