# 🔧 Trust Issues - Troubleshooting Checklist

## 📋 Use This Checklist When Things Don't Work

### ✅ Pre-Flight Checklist

Run through this **BEFORE** reporting issues:

- [ ] **1. API Keys Added?**
  - Open `backend/.env` file
  - Check `GEMINI_API_KEY=` has real key (not placeholder)
  - Check `NEWS_API_KEY=` has real key (not placeholder)
  
- [ ] **2. Dependencies Installed?**
  ```bash
  cd backend
  pip install -r requirements.txt
  
  cd frontend
  npm install
  ```

- [ ] **3. Backend Running?**
  - Look for terminal with: `INFO: Uvicorn running on http://0.0.0.0:8000`
  - Visit: http://localhost:8000/health
  - Should show: `{"status":"ok","backend":"ready"}`

- [ ] **4. Extension Built?**
  ```bash
  cd frontend
  npm run build
  ```

- [ ] **5. Extension Loaded in Chrome?**
  - Go to: chrome://extensions/
  - See "Trust Issues" card?
  - Extension enabled?
  - Click extension icon - does popup open?

---

## 🔍 Diagnostic Steps

### Step 1: Test Backend Setup
```bash
cd backend
python test_setup.py
```

**All tests should pass!** If not:
- Failed: Package Imports → `pip install -r requirements.txt`
- Failed: API Keys → Add real keys to `.env` file
- Failed: Gemini Connection → Check key is valid at https://makersuite.google.com/
- Failed: NewsAPI Connection → Check key is valid at https://newsapi.org/

### Step 2: Check Backend Logs

Start backend with:
```bash
python -m uvicorn app.main:app --reload --log-level debug
```

**What to look for:**
- ✓ Good: `✓ API keys configured correctly`
- ✓ Good: `✓ Backend ready!`
- ✗ Bad: `❌ MISSING REQUIRED API KEYS`
- ✗ Bad: `ValueError: Invalid API key`

### Step 3: Check Browser Console

1. Click extension icon to open popup
2. Right-click on popup → "Inspect"
3. Go to "Console" tab

**What to look for:**
- ✗ Bad: `Failed to fetch` → Backend not running
- ✗ Bad: `NetworkError` → Backend not reachable
- ✗ Bad: `500 Internal Server Error` → Backend error (check backend logs)

---

## 🚨 Common Issues & Solutions

### Issue #1: Extension Stuck on "Analyzing..."

**Symptoms:**
- Click "Scan Now"
- Shows loading animation
- Never completes
- No error message

**Debug Steps:**

1. **Is backend running?**
   ```bash
   # Check if backend server is running
   # You should see a terminal window with:
   INFO: Uvicorn running on http://0.0.0.0:8000
   ```
   
   **Fix**: Start backend server
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload
   ```

2. **Can backend be reached?**
   - Open: http://localhost:8000/health
   - Should show: `{"status":"ok","backend":"ready"}`
   
   **Fix if not working**:
   - Check firewall isn't blocking port 8000
   - Try: `http://127.0.0.1:8000/health`

3. **Check browser console**
   - Right-click popup → Inspect → Console
   - Look for red errors
   
   **Common errors:**
   - `Cannot reach backend` → Backend not running
   - `Connection refused` → Backend crashed
   - `Timeout` → Backend too slow (check backend logs)

4. **Check backend logs**
   - Look at terminal running backend
   - Any errors when you clicked "Scan Now"?
   
   **Common errors:**
   - `Invalid API key` → Check `.env` file
   - `Rate limit exceeded` → Wait a minute, try again
   - `NewsAPI error` → Check NewsAPI key

---

### Issue #2: Backend Won't Start

**Error Message:** `❌ MISSING REQUIRED API KEYS`

**Solution:**
1. Open `backend/.env`
2. Make sure it has:
   ```
   GEMINI_API_KEY=actual_key_here
   NEWS_API_KEY=actual_key_here
   ```
3. Save file
4. Restart backend

---

**Error Message:** `Port 8000 is already in use`

**Solution Option A (Recommended):**
Kill the process using port 8000:

**Windows:**
```cmd
netstat -ano | findstr :8000
taskkill /PID <PID_NUMBER> /F
```

**Mac/Linux:**
```bash
lsof -ti:8000 | xargs kill -9
```

**Solution Option B (Alternative):**
Use a different port:
```bash
python -m uvicorn app.main:app --reload --port 8001
```

Then update `frontend/.env.local`:
```
REACT_APP_API_URL=http://localhost:8001
```

And rebuild frontend:
```bash
cd frontend
npm run build
```

---

**Error Message:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
```bash
cd backend
pip install -r requirements.txt
```

If still fails:
```bash
pip install fastapi uvicorn pydantic pydantic-settings python-dotenv requests google-generativeai
```

---

### Issue #3: API Errors

**Error:** `Gemini API error: Invalid API key`

**Solution:**
1. Go to: https://makersuite.google.com/app/apikey
2. Create a NEW API key
3. Copy it
4. Update `backend/.env`:
   ```
   GEMINI_API_KEY=your_new_key_here
   ```
5. Restart backend

---

**Error:** `NewsAPI error: apiKey parameter is missing`

**Solution:**
1. Go to: https://newsapi.org/
2. Login and get your API key
3. Update `backend/.env`:
   ```
   NEWS_API_KEY=your_key_here
   ```
4. Restart backend

---

**Error:** `Rate limit exceeded`

**Solution:**
- Gemini: Wait 1 minute (60 requests/minute limit)
- NewsAPI: Wait until tomorrow (100 requests/day limit on free tier)

---

### Issue #4: Extension Not Working

**Symptom:** Extension icon doesn't appear in Chrome

**Solution:**
1. Go to: `chrome://extensions/`
2. Enable "Developer mode" (top right toggle)
3. Click "Load unpacked"
4. Select `frontend/dist` folder
5. Check extension is enabled

---

**Symptom:** Popup doesn't open when clicking icon

**Solution:**
1. Go to: `chrome://extensions/`
2. Find "Trust Issues"
3. Click "Remove"
4. Rebuild extension:
   ```bash
   cd frontend
   rm -rf dist
   npm run build
   ```
5. Re-load extension

---

**Symptom:** "Scan Now" button does nothing

**Solution:**
1. Right-click popup → Inspect → Console
2. Look for errors
3. Check if backend is running
4. Rebuild extension:
   ```bash
   cd frontend
   npm run build
   ```

---

## 🧪 Test Your Setup

### Quick Test Commands

```bash
# Test 1: Backend health
curl http://localhost:8000/health

# Test 2: Backend root
curl http://localhost:8000/

# Test 3: API test (requires backend running)
cd backend
python test_setup.py
```

---

## 📊 Status Checks

### ✅ Everything Working If:

**Backend:**
```
$ python -m uvicorn app.main:app --reload
INFO:     Uvicorn running on http://0.0.0.0:8000
Initializing TrustIssues backend...
✓ API keys configured correctly
✓ Backend ready!
```

**Health Check:**
```
$ curl http://localhost:8000/health
{"status":"ok","backend":"ready"}
```

**Extension:**
- Extension icon visible in toolbar
- Popup opens when clicked
- "Scan Now" button present
- After scan: See scores, sources, findings

---

## 🔄 Nuclear Option (Full Reset)

If nothing works, try this:

```bash
# 1. Stop backend (Ctrl+C)

# 2. Clean backend
cd backend
rm -rf __pycache__ app/__pycache__
pip uninstall -y fastapi uvicorn pydantic requests google-generativeai
pip install -r requirements.txt

# 3. Clean frontend
cd frontend
rm -rf node_modules dist .next
npm install
npm run build

# 4. Remove extension from Chrome
# chrome://extensions/ → Remove "Trust Issues"

# 5. Re-add API keys to backend/.env

# 6. Start backend
cd backend
python test_setup.py  # Verify first
python -m uvicorn app.main:app --reload

# 7. Re-load extension
# chrome://extensions/ → Load unpacked → Select frontend/dist
```

---

## 📞 Still Not Working?

**Before asking for help, provide:**

1. **Output of:**
   ```bash
   cd backend
   python test_setup.py
   ```

2. **Backend logs** (copy terminal output when starting server)

3. **Browser console errors** (Right-click popup → Inspect → Console)

4. **What you were doing** when it failed

5. **Operating System** (Windows 10, macOS 13, Ubuntu 22.04, etc.)

6. **Python version:**
   ```bash
   python --version
   ```

7. **Node version:**
   ```bash
   node --version
   ```

---

## ✅ Final Checklist Before Reporting Issue

- [ ] Ran `python backend/test_setup.py` - ALL tests pass?
- [ ] Backend server is running (terminal shows "Backend ready!")?
- [ ] Can access http://localhost:8000/health ?
- [ ] Tried rebuilding extension (`npm run build`)?
- [ ] Tried reloading extension in Chrome?
- [ ] Checked browser console for errors?
- [ ] Tried the "Nuclear Option" full reset?

If ALL checked and still broken → then ask for help! 🆘

---

**Quick Reference:** See `QUICK_REFERENCE.md` for daily workflow
**Setup Guide:** See `SETUP_COMPLETE.md` for detailed setup instructions
