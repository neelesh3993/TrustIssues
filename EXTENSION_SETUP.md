# Trust Issues - Browser Extension Conversion Guide

## 📋 Completed Setup

### Phase 1: Extension Foundation ✅
- [x] Manifest v3 configuration
- [x] Background service worker (message handling, caching)
- [x] Content script (page interaction)
- [x] Popup HTML template
- [x] TypeScript configuration for extension

### Phase 2: Backend API ✅
- [x] FastAPI setup with CORS configuration
- [x] `/api/analyze` endpoint structure
- [x] Pipeline modules (claim extraction, verification, summarization)
- [x] Response models and validation
- [x] Error handling

### Supporting Infrastructure ✅
- [x] API service layer (`src/services/api.ts`)
- [x] `useAnalysis` hook for React components
- [x] Build configuration for extension bundling
- [x] Environment configuration (`.env.local`, `.env`)

---

## 🚀 Next Steps to Run the Extension

### Backend Setup (Terminal 1)
```bash
cd backend
python -m venv venv

# Activate venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

**Expected output:** `Uvicorn running on http://127.0.0.1:8000`

### Frontend Setup (Terminal 2)
```bash
cd frontend

# Install dependencies
npm install
# or
pnpm install

# Build extension
npm run build:extension

# For development with watch mode
npm run dev:extension
```

### Load Extension in Chrome
1. Open `chrome://extensions/`
2. Enable **Developer mode** (top right)
3. Click **Load unpacked**
4. Select: `frontend/public/` folder (or `frontend/dist-extension/` after build)
5. Extension should appear in your toolbar

---

## 📝 Architecture Overview

### Browser Extension Flow
```
User Action (Scan Button)
    ↓
Popup Component (React UI)
    ↓
useAnalysis Hook
    ↓
Background Service Worker
    ↓
API Service → Backend API
    ↓
Analysis Pipeline (Claims → Verify → Summarize)
    ↓
Results returned & cached in chrome.storage.local
```

### File Structure
```
frontend/
├── src/
│   ├── background/
│   │   └── service-worker.ts      # Extension message handler
│   ├── content/
│   │   └── content-script.ts      # Page interaction
│   ├── services/
│   │   └── api.ts                 # Backend communication
│   ├── hooks/
│   │   └── useAnalysis.ts         # React hook for analysis
│   └── components/
│       └── popup.tsx              # Extension popup component
├── public/
│   ├── manifest.json              # Extension manifest
│   └── popup.html                 # Popup container
└── tsconfig.extension.json        # Extension build config

backend/
├── app/
│   ├── main.py                    # FastAPI app
│   ├── routes/
│   │   └── analyze.py             # Analysis endpoint
│   ├── models/
│   │   └── schemas.py             # Pydantic models
│   └── pipeline/
│       ├── claim_extractor.py
│       ├── verifier.py
│       └── summarizer.py
└── requirements.txt               # Python dependencies
```

---

## 🔧 Important Environment Variables

**`.env.local` (Frontend)**
```
REACT_APP_API_URL=http://localhost:8000
NODE_ENV=development
ENABLE_CACHE=true
```

**`.env` (Backend)**
```
HOST=0.0.0.0
PORT=8000
DEBUG=True
```

---

## ✨ Key Features Implemented

### Backend API (`/api/analyze`)
- Accepts URL, content, and title
- Returns scores: AI generation likelihood, credibility, manipulation risk
- Includes findings, verified sources, and detailed report
- Request validation (minimum 50 characters)
- 30-second request timeout
- Comprehensive error handling

### Extension Integration
- **Caching**: Results cached in `chrome.storage.local` (7-day TTL)
- **Message Passing**: Secure communication via Chrome extension APIs
- **Content Access**: Content script extracts page data
- **Background Processing**: Async analysis without blocking UI
- **Error Recovery**: Graceful error handling with user feedback

### React Hook (`useAnalysis`)
```typescript
const { status, data, error, analyze, cancel, reset } = useAnalysis()
// status: 'idle' | 'analyzing' | 'done' | 'error'
```

---

## 🐛 Testing

### Test Backend
```bash
# From backend directory
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "content": "This is a test article with multiple sentences and claims...",
    "title": "Test Article"
  }'
```

### Test Extension
1. Open any webpage
2. Click the **Trust Issues** icon in toolbar
3. Click **"Scan This Page"**
4. Backend should receive request (check `http://localhost:8000/docs` for API docs)
5. Results should appear in popup after ~6 seconds

---

## 📦 Build & Package

### Production Build
```bash
npm run build:all
npm run extension:pack
```

Outputs:
- `dist-extension/` - Ready-to-load extension folder
- Can be zipped for distribution

### Chrome Web Store (Future)
- Use `dist-extension/` folder for submission
- Ensure all scripts are bundled (no npm modules)

---

## 🔒 Security Checklist

- [x] Content Security Policy configured
- [x] Request validation (content length, type checking)
- [x] CORS restricted to extension origin
- [x] Timeout handling (prevents hanging requests)
- [x] No credentials in logs
- [x] Chrome extension manifest permissions restricted

---

## ⚙️ Troubleshooting

### Extension not loading?
1. Check browser console for errors: press F12 in popup
2. Verify manifest.json is valid: `npm run extension:test`
3. Ensure TypeScript compilation succeeded

### API connection failed?
1. Backend running? Check `http://localhost:8000/health`
2. CORS issue? Verify `Allow-Origin` headers from FastAPI
3. Wrong URL? Check `REACT_APP_API_URL` in `.env.local`

### Results not showing?
1. Check cache: `chrome://extensions` → Details → Clear data
2. Open DevTools (F12) → check Console for errors
3. Verify backend response format in Network tab

---

## 📚 Next Phase (Phase 3): UX Enhancements

When ready, implement:
- Settings page for API configuration
- Scan history and bookmarks
- Keyboard shortcut (e.g., Ctrl+Shift+X)
- Notifications on completion
- Batch analysis for multiple articles
- Export analysis as PDF

See original phase breakdown for more details!
