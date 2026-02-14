# Trust Issues Extension — Frontend-Backend Integration Guide

## Overview

This guide explains how the Chrome extension frontend integrates with the FastAPI backend to provide real-time content analysis.

**System Type:** Browser Extension + Local API Server  
**Data Flow:** Webpage → Content Script → Service Worker → FastAPI Backend → Results Display

---

## Architecture

### High-Level Data Flow

```
User visits webpage
    ↓
User clicks "Analyze" in extension popup
    ↓
Popup requests content from Content Script
    ↓
Content Script extracts text, images, URL, title
    ↓
Popup sends to Service Worker
    ↓
Service Worker checks cache, calls FastAPI backend
    ↓
FastAPI runs analysis pipeline (claims, verification, summary)
    ↓
Backend returns structured JSON response
    ↓
Service Worker caches result, notifies popup
    ↓
Popup displays results to user
    ↓
(Optional) Content Script shows inline badge with credibility score
```

### Component Responsibilities

| Component | Purpose | Technology |
|-----------|---------|-----------|
| **Content Script** | Extract page content, inject badges | TypeScript, Chrome APIs |
| **Service Worker** | Route messages, manage API calls, handle errors | TypeScript, Chrome APIs |
| **API Service** | HTTP client with timeouts and error handling | TypeScript, Fetch API |
| **Popup UI** | Display analysis results | React, TypeScript |
| **FastAPI Backend** | Run analysis pipeline, return JSON responses | Python, Pydantic, FastAPI |

---

## File Structure & Responsibilities

### Frontend Files

```
frontend/
├── src/
│   ├── content/
│   │   └── content-script.ts          # Extract page text & images
│   ├── background/
│   │   └── service-worker.ts          # Route messages, manage requests
│   ├── services/
│   │   └── api.ts                     # HTTP client with error handling
│   ├── hooks/
│   │   └── useAnalysis.ts             # React state management
│   ├── components/
│   │   └── trust-issues/
│   │       └── popup-container.tsx    # Main UI component
│   └── popup.tsx                      # Entry point
├── public/
│   ├── manifest.json                  # Extension config + permissions
│   └── popup.html                     # Popup UI template
└── tsconfig.json
```

### Backend Files

```
backend/
├── app/
│   ├── main.py                        # FastAPI app + CORS config
│   ├── models/
│   │   └── schemas.py                 # Pydantic request/response models
│   ├── routes/
│   │   └── analyze.py                 # POST /api/analyze endpoint
│   ├── pipeline/                      # Analysis logic
│   │   ├── claim_extractor.py
│   │   ├── verifier.py
│   │   └── summarizer.py
│   └── database/
│       └── db.py                      # SQLite caching
└── requirements.txt
```

---

## Key Integration Points

### 1. Content Script ↔ Popup

**File:** [src/content/content-script.ts](frontend/src/content/content-script.ts)

When the popup needs page content:

```typescript
// Popup sends message
chrome.tabs.sendMessage(tabId, {
  type: 'REQUEST_PAGE_CONTENT'
})

// Content script responds with
{
  url: "https://example.com",
  title: "Article Title",
  content: "Full page text...",
  images: ["base64...", "base64..."],  // Optional
  timestamp: "2026-02-14T10:30:00Z"
}
```

**Error Handling:**
- Content script catches errors extracting images (CORS issues)
- Sends clean response even if images fail
- Truncates content to 10,000 chars to manage memory

---

### 2. Service Worker ↔ Backend API

**File:** [src/background/service-worker.ts](frontend/src/background/service-worker.ts)

Request flow:

```typescript
// Service worker sends
POST /api/analyze
{
  "url": "https://example.com",
  "title": "Article Title",
  "content": "Full page text...",
  "images": ["base64..."]
}

// Backend responds
{
  "aiGenerationLikelihood": 25.5,
  "credibilityScore": 72.0,
  "manipulationRisk": 15.3,
  "findings": ["claim 1", "claim 2"],
  "sources": [
    {
      "name": "Reuters",
      "headline": "Fact check...",
      "status": "verified"
    }
  ],
  "report": "Detailed analysis..."
}
```

**Timeout & Cancellation:**
- 30-second timeout for analysis requests
- User can cancel mid-analysis
- Backend continues processing (results cached)

---

### 3. Backend Configuration

**File:** [backend/app/main.py](backend/app/main.py)

Required setup:

```python
from fastapi.middleware.cors import CORSMiddleware

# Allow localhost requests (required for extension)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:*", "http://127.0.0.1:*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Endpoints:**
- `POST /api/analyze` — Main analysis endpoint
- `GET /health` — Health check
- `GET /` — Status check

---

## Error Handling Strategy

### Content Script Errors

| Error | Handling | User Impact |
|-------|----------|------------|
| Image extraction fails | Skip image, continue | Text analysis proceeds |
| DOM mutation error | Try alternate extraction | Falls back to innerText |
| CORS on images | Graceful skip | Images not sent to backend |

### Service Worker Errors

| Error | Message | Recovery |
|-------|---------|----------|
| Backend unreachable | "Backend unreachable at http://127.0.0.1:8000" | User starts FastAPI |
| Timeout (30s) | "Analysis timeout. Backend might be slow." | User can retry |
| HTTP 400 | "Invalid content. Backend could not parse." | User selects different content |
| HTTP 500 | "Backend error. Pipeline encountered issue." | User files issue report |
| Network error | "Cannot reach backend. Network error." | Check network/proxy |

### API Service Error Hierarchy

```typescript
APIError (base)
├── ValidationError     → Content too short/empty
├── NetworkError        → Cannot reach server
├── TimeoutError        → Exceeded 30 seconds
└── ServerError         → Backend returned 500
```

**Debugging:**
All errors logged to browser console with [API], [Service Worker], [Content Script] prefixes

---

## Caching Strategy

### Cache Key Format
```
analysis_{url}
```

### Cache Entry
```typescript
{
  result: AnalysisResponse,
  timestamp: number  // epoch ms
}
```

### Cache Behavior

| Scenario | Cache Used | Duration |
|----------|-----------|----------|
| User re-analyzes same URL | Yes | 1 hour TTL |
| Automatic cleanup | Old entries removed | 7 days TTL |
| User clears cache | Triggered by popup | Immediate |

**Performance Benefit:** Repeat analyses return instantly

---

## Data Sanitization

### Content Truncation
- Max 10,000 characters (memory efficient)
- Better performance, sufficient for analysis

### Image Resizing
- Max 5 images per page
- Max 800px width (JPEG 70% quality)
- Max 500KB per image
- CORS issues gracefully skipped

### Validation
- Minimum 50 characters required
- Empty submissions rejected
- Frontend validates before sending

---

## Development Workflow

### 1. Start Backend

```bash
cd backend
python -m uvicorn app.main:app --reload
# Backend runs at http://127.0.0.1:8000
```

### 2. Build Extension

```bash
cd frontend
npm run build
```

### 3. Load Extension in Chrome

1. Open `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select `frontend/dist` folder

### 4. Debug

**Browser Console (Popup):**
```javascript
// Check logs
chrome://extensions/ → Trust Issues → Inspect views → service worker
```

**Browser Console (Content Script):**
Right-click page → Inspect → Console tab

**VS Code Debugger:**
- Set breakpoints in TypeScript source
- Chrome debugging via VS Code

---

## Testing Checklist

### Content Extraction
- [ ] Extract text from article page
- [ ] Extract images (verify size < 500KB)
- [ ] Handle pages with minimal text
- [ ] Handle pages with no images

### API Communication
- [ ] Backend unreachable → Error message
- [ ] Short content (< 50 chars) → Rejected
- [ ] Long content (> 50KB) → Truncated
- [ ] Network timeout (30s) → User-friendly error

### Error Handling
- [ ] Network disconnected → Clear error
- [ ] Backend returns 500 → User-friendly message
- [ ] CORS error → Fallback gracefully
- [ ] Cancel analysis mid-request → Cleanup refs

### Caching
- [ ] First analysis: takes time
- [ ] Same URL again: instant (< 1s)
- [ ] Old cache (7+ days): removed
- [ ] User clears cache: works

### UI/UX
- [ ] Loading state shows progress
- [ ] Results display correctly
- [ ] Error messages help user debug
- [ ] Badge shows correct credibility score

---

## Debugging Tips

### Enable Detailed Logging

**Content Script:**
```typescript
// Already logs with [Content Script] prefix
// Check console after right-click → Inspect
```

**Service Worker:**
```
chrome://extensions/ → Trust Issues → Details → 
  Service worker (inspect views → service-worker.js)
```

**API Calls:**
Open DevTools → Network tab → Filter for `/api/analyze`

### Check Health Status

Open browser console in any page:
```javascript
chrome.runtime.sendMessage(
  { type: 'CHECK_BACKEND_HEALTH' },
  (response) => console.log('Backend healthy:', response.healthy)
)
```

### View Cache

```javascript
chrome.storage.local.get(null, (cache) => {
  Object.entries(cache)
    .filter(([k]) => k.startsWith('analysis_'))
    .forEach(([k, v]) => console.log(k, v))
})
```

### Clear All Cache

```javascript
chrome.storage.local.get(null, (cache) => {
  const keys = Object.keys(cache).filter(k => k.startsWith('analysis_'))
  chrome.storage.local.remove(keys);
})
```

---

## Performance Characteristics

| Operation | Typical Time |
|-----------|--------------|
| Extract page content | < 100ms |
| Send to backend | < 50ms (network dependent) |
| Backend analysis | 3-5 seconds |
| Return cached result | < 1ms |
| Show badge | < 100ms |

**Total time:** First analysis 3-6 seconds, cached 1-2 seconds

---

## Security Considerations

### CORS Configuration
- Localhost only (not production-safe)
- Update for remote backend:
  ```python
  allow_origins=["https://yourdomain.com"]
  ```

### Data in Transit
- No encryption (HTTPS recommended for production)
- Content sent to backend unencrypted

### Cache Storage
- Stored in `chrome.storage.local` (user-accessible)
- Not sensitive to expose analysis results
- Cleared after 7 days

### Images
- CORS issues prevent cross-origin images
- User's own images only (safe)

---

## Common Issues & Solutions

### "Backend unreachable" Error

**Symptom:** Every analysis fails with this error

**Solution:**
1. Check backend is running: `http://127.0.0.1:8000`
2. Verify in terminal: `python -m uvicorn app.main:app --reload`
3. Check CORS middleware in `app/main.py`
4. Verify localhost in manifest permissions

### Analysis Takes Too Long

**Symptom:** Analysis takes > 10 seconds

**Possible Causes:**
- Backend pipeline is slow
- Network latency
- Large content (auto-truncated to 50KB)

**Solution:**
- Check individual pipeline components
- Reduce content length
- Verify backend logs

### Images Not Being Sent

**Symptom:** `images: undefined` in request

**Causes:**
- Page has no images
- All images < 100px (skipped as thumbnails)
- CORS blocks image access

**Solution:**
- Check content script logs
- Verify images exist on page

### Cache Not Clearing

**Symptom:** Cleared cache but results still show

**Solution:**
```javascript
// Manual clear
chrome.storage.local.clear()
```

---

## Future Enhancements

- [ ] Offline mode with local models
- [ ] Real-time fact-checking as you browse
- [ ] Multi-language support
- [ ] Custom analysis settings
- [ ] Export analysis reports
- [ ] Share results with others
- [ ] Video content analysis
- [ ] Advanced caching with IndexedDB

---

## References

- [Chrome Extension API Docs](https://developer.chrome.com/docs/extensions/)
- [Content Scripts Guide](https://developer.chrome.com/docs/extensions/mv3/content_scripts/)
- [Service Workers Guide](https://developer.chrome.com/docs/extensions/mv3/service_workers/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Fetch API - MDN](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API)

---

## Questions?

Refer to console logs with these prefixes for debugging:
- `[Content Script]` → Content extraction issues
- `[Service Worker]` → Message routing, caching
- `[API]` → Backend communication, errors

All messages include context for debugging integration issues.
