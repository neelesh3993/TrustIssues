# 🔍 Frontend Debugging - Step by Step

Based on your backend logs, the backend IS working and receiving requests successfully:
```
POST /api/analyze - 6476.55 ms
INFO: 127.0.0.1:53002 - "POST /api/analyze HTTP/1.1" 200 OK
```

This means the request is reaching the backend! Let's trace where the issue is.

## 🎯 Debug Steps:

### Step 1: Check Extension Console

1. **Open extension popup**
2. **Right-click on popup → "Inspect"**
3. **Go to Console tab**
4. **Click "Scan Now"**
5. **Watch for messages**

**What you should see:**
```javascript
[Content Script] Trust Issues content script loaded
[Service Worker] Received message: ANALYZE_PAGE
[Service Worker] Starting analysis for https://...
[API] Starting analysis request
[API] Analysis complete
[Service Worker] Analysis complete
```

**If you see errors, copy them here!**

### Step 2: Check Service Worker Console

1. Go to `chrome://extensions/`
2. Find "Trust Issues"
3. Click **"service worker"** (blue link under extension)
4. Check Console tab
5. Click "Scan Now" in extension popup

**What you should see:**
```javascript
[Service Worker] Trust Issues service worker loaded
[Service Worker] Received message: ANALYZE_PAGE
[Service Worker] Starting analysis for https://...
[Service Worker] Backend is healthy
[API] Starting analysis request
[API] Analysis complete
[Service Worker] Analysis complete
```

**Copy any errors you see!**

### Step 3: Check Content Script Console

1. **Go to the webpage you're scanning (like BBC News)**
2. **Press F12 to open DevTools**
3. **Go to Console tab**
4. **Filter by "Content Script" or "Trust Issues"**
5. **Click "Scan Now"**

**What you should see:**
```javascript
[Content Script] Trust Issues content script loaded
[Content Script] Received page content request
[Content Script] Sending page content: {url: "...", contentLength: 1234, imageCount: 0}
```

### Step 4: Network Tab

1. **Open extension popup**
2. **Right-click → Inspect**
3. **Go to Network tab**
4. **Click "Scan Now"**
5. **Look for request to http://127.0.0.1:8000/api/analyze**

**Check:**
- Is the request showing up?
- What's the status? (should be 200)
- What's the response?

## 🐛 Common Issues:

### Issue A: Extension Shows "Analyzing..." Forever

**Likely causes:**
1. Response is coming back but not being displayed
2. Message passing between popup and service worker broken
3. Cache issue

**Debug:**
- Check service worker console
- Look for "ANALYSIS_COMPLETE" message
- Check if response has all required fields

### Issue B: No Request in Network Tab

**Likely causes:**
1. Content script not injecting
2. Service worker not receiving messages

**Debug:**
- Check content script console on the webpage
- Reload extension and try again

### Issue C: Request Succeeds but No Display

**Likely causes:**
1. Response format mismatch
2. React state not updating
3. Component rendering issue

**Debug:**
- Check popup console for React errors
- Check if data is present in console logs

## 🧪 Manual Test:

Let's test if the backend response is correct:

1. Open browser console (F12)
2. Paste this code:
```javascript
fetch('http://127.0.0.1:8000/api/analyze', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    url: 'https://example.com',
    content: 'The Eiffel Tower is 330 meters tall and located in Paris, France. It was built in 1889.',
    title: 'Test Article'
  })
})
.then(r => r.json())
.then(d => console.log('SUCCESS:', d))
.catch(e => console.error('ERROR:', e))
```

**Expected result:**
```javascript
SUCCESS: {
  aiGenerationLikelihood: 40,
  credibilityScore: 75,
  manipulationRisk: 45,
  findings: [...],
  sources: [...],
  report: "..."
}
```

## 📊 Required Response Fields

The backend MUST return these fields (check in Network tab response):
- `aiGenerationLikelihood` (number)
- `credibilityScore` (number)
- `manipulationRisk` (number)
- `findings` (array of strings)
- `sources` (array of objects)
- `report` (string)

## 🔧 Quick Fixes to Try:

### Fix 1: Clear Extension Cache
```javascript
// Open service worker console and run:
chrome.storage.local.clear()
```

### Fix 2: Reload Extension
1. `chrome://extensions/`
2. Click reload icon on Trust Issues
3. Try again

### Fix 3: Check Popup State
```javascript
// In popup console, check:
console.log('Popup state:', window)
```

### Fix 4: Force Rebuild
```powershell
cd frontend
Remove-Item -Recurse -Force dist
npm run build
```

## 📝 What to Report Back:

Please provide:

1. **Extension popup console** output when clicking "Scan Now"
2. **Service worker console** output
3. **Content script console** output (on the webpage)
4. **Network tab** - screenshot of the request/response
5. Any **error messages** in red

This will help me pinpoint exactly where the flow is breaking!

## 🎯 Expected Full Flow:

```
[User clicks "Scan Now"]
        ↓
[Popup: useAnalysis.analyze()]
        ↓
[Content Script: Extracts page content]
        ↓
[Service Worker: Receives ANALYZE_PAGE message]
        ↓
[Service Worker: Calls backend API]
        ↓
[Backend: Processes and returns 200 OK] ← YOU ARE HERE (this works!)
        ↓
[Service Worker: Sends ANALYSIS_COMPLETE message]
        ↓
[Popup: Displays results]
```

Your backend is working (step 5)! We need to check steps 6 and 7.

---

**Next:** Open the extension popup console and service worker console, click "Scan Now", and copy all the output!
