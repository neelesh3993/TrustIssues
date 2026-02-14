# API Contract & Message Reference

Quick reference for all communication protocols between extension components and backend.

---

## Chrome Extension Message Protocol

### Content Script → Service Worker

#### REQUEST_PAGE_CONTENT
Extract current webpage content and metadata

**Request:**
```typescript
chrome.tabs.sendMessage(tabId, {
  type: 'REQUEST_PAGE_CONTENT'
})
```

**Response:**
```typescript
{
  url: string,              // Current page URL
  title: string,            // Page title
  content: string,          // Extracted text (≤10KB)
  images?: string[],        // Base64-encoded images (optional)
  timestamp: string,        // ISO timestamp
  error?: string            // If extraction failed
}
```

**Errors:**
- CORS issues on images: Images are skipped, rest proceeds
- DOM mutation: Falls back to alternative extraction
- Very large page: Content truncated to 10,000 characters

---

### Popup → Service Worker

#### ANALYZE_PAGE
Request analysis of page content

**Request:**
```typescript
chrome.runtime.sendMessage({
  type: 'ANALYZE_PAGE',
  payload: {
    url: string,           // Page URL
    title: string,         // Page title
    content: string,       // Text content (≥50 chars, ≤50KB)
    images?: string[]      // Optional images (base64)
  }
})
```

**Response:**
```typescript
{
  status: 'analyzing' | 'complete' | 'error',
  message?: string,
  cached?: boolean,        // true if result from cache
  error?: string           // Error message if status='error'
}
```

**Errors:**
- Content too short: `{ status: 'error', error: 'Content too short...' }`
- Backend unreachable: `{ status: 'error', error: 'Backend unreachable...' }`
- Timeout: `{ status: 'error', error: 'Analysis timeout...' }`
- Network error: `{ status: 'error', error: 'Cannot reach backend...' }`

---

#### GET_CACHED_ANALYSIS
Retrieve previously cached analysis

**Request:**
```typescript
chrome.runtime.sendMessage({
  type: 'GET_CACHED_ANALYSIS',
  payload: {
    url: string  // Page URL to look up
  }
})
```

**Response:**
```typescript
{
  found: boolean,
  data?: AnalysisResponse   // If found
}
```

---

#### CANCEL_ANALYSIS
Stop an ongoing analysis

**Request:**
```typescript
chrome.runtime.sendMessage({
  type: 'CANCEL_ANALYSIS',
  payload: {
    tabId: number  // Tab ID of analysis to cancel
  }
})
```

**Response:**
```typescript
{
  status: 'cancelled' | 'no_active_request'
}
```

---

#### CHECK_BACKEND_HEALTH
Check if backend is online and healthy

**Request:**
```typescript
chrome.runtime.sendMessage({
  type: 'CHECK_BACKEND_HEALTH'
})
```

**Response:**
```typescript
{
  healthy: boolean
}
```

---

#### CLEAR_CACHE
Clear all cached analysis results

**Request:**
```typescript
chrome.runtime.sendMessage({
  type: 'CLEAR_CACHE'
})
```

**Response:**
```typescript
{
  cleared: number  // Number of entries removed
}
```

---

### Service Worker → Popup (Notifications)

#### ANALYSIS_COMPLETE
Analysis finished successfully

```typescript
{
  type: 'ANALYSIS_COMPLETE',
  payload: {
    result: AnalysisResponse,
    cached: boolean
  }
}
```

---

#### ANALYSIS_ERROR
Analysis failed

```typescript
{
  type: 'ANALYSIS_ERROR',
  payload: {
    error: string,        // User-friendly error message
    url: string           // URL that failed
  }
}
```

---

#### ANALYSIS_PROGRESS
Progress update during analysis

```typescript
{
  type: 'ANALYSIS_PROGRESS',
  payload: {
    status: string,       // "Checking cache...", "Analyzing content..."
    progress: number      // 0-100 percentage
  }
}
```

---

### Service Worker → Content Script

#### SHOW_ANALYSIS_BADGE
Display credibility badge on page

```typescript
{
  type: 'SHOW_ANALYSIS_BADGE',
  payload: AnalysisResponse
}
```

---

#### HIGHLIGHT_FINDINGS
Highlight suspicious findings on page

```typescript
{
  type: 'HIGHLIGHT_FINDINGS',
  payload: string[]  // Array of phrases to highlight
}
```

---

## Backend REST API

### POST /api/analyze

Analyze page content and return credibility assessment

**Request Headers:**
```
Content-Type: application/json
X-Requested-With: XMLHttpRequest
```

**Request Body:**
```json
{
  "url": "https://example.com/article",
  "title": "Article Title",
  "content": "Full text content of the page...",
  "images": ["base64_encoded_image_1", "base64_encoded_image_2"]
}
```

**Response (200 OK):**
```json
{
  "aiGenerationLikelihood": 25.5,
  "credibilityScore": 72.0,
  "manipulationRisk": 15.3,
  "findings": [
    "Unverified claim about X",
    "Misleading statistical framing",
    "Missing context on Y"
  ],
  "sources": [
    {
      "name": "Reuters",
      "headline": "Fact check on X",
      "status": "verified"
    },
    {
      "name": "PolitiFact",
      "headline": "Claim about Y rated false",
      "status": "disputed"
    }
  ],
  "report": "Detailed analysis explaining the credibility assessment and findings..."
}
```

**Error Responses:**

**400 Bad Request:**
```json
{
  "detail": "Content too short for analysis (minimum 50 characters)"
}
```

**422 Unprocessable Entity:**
```json
{
  "detail": [
    {
      "loc": ["body", "content"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Analysis pipeline encountered an error: ..."
}
```

---

### GET /health

Health check endpoint

**Response (200 OK):**
```json
{
  "status": "ok",
  "backend": "ready"
}
```

---

### GET /

Server status

**Response (200 OK):**
```json
{
  "status": "backend running"
}
```

---

## Type Definitions

### AnalysisRequest
```typescript
interface AnalysisRequest {
  url: string           // Required: webpage URL
  content: string       // Required: extracted text (50-50000 chars)
  title: string         // Required: page title
  images?: string[]     // Optional: base64-encoded images
}
```

### Source
```typescript
interface Source {
  name: string          // Source name/domain
  headline: string      // Source headline or summary
  status: string        // "verified", "disputed", or "uncertain"
}
```

### AnalysisResponse
```typescript
interface AnalysisResponse {
  aiGenerationLikelihood: number  // 0-100, percentage
  credibilityScore: number        // 0-100, percentage
  manipulationRisk: number        // 0-100, percentage
  findings: string[]              // Array of identified issues
  sources: Source[]               // Supporting/contradicting sources
  report: string                  // Detailed human-readable analysis
}
```

---

## Error Hierarchy

```
Error
├── ValidationError
│   ├── "Content too short"
│   ├── "Content cannot be empty"
│   └── "Invalid content format"
├── NetworkError
│   ├── "Cannot reach backend at http://127.0.0.1:8000"
│   └── "Network timeout"
├── TimeoutError
│   └── "Analysis timeout (30 seconds)"
└── ServerError
    ├── "Backend error. Pipeline failed"
    └── "Invalid response from backend"
```

---

## Validation Rules

### Content
- **Minimum:** 50 characters
- **Maximum:** 50,000 characters
- **Required:** Must be non-empty string

### Images
- **Maximum per request:** 5 images
- **Maximum per image:** 500 KB
- **Allowed formats:** JPEG, PNG, WebP
- **Minimum dimensions:** 100x100 pixels
- **Processing:** Resized to max 800px width

### URL
- **Required:** Must be valid HTTP/HTTPS URL
- **Format:** Full URL with protocol

### Title
- **Required:** Must be non-empty string
- **Maximum:** 500 characters

---

## Cache Schema

### Storage Key
```
analysis_{url}
```

### Cache Entry
```typescript
{
  result: AnalysisResponse,
  timestamp: number  // ISO timestamp in milliseconds
}
```

### TTL
- **1 hour:** Results are considered fresh
- **7 days:** Old entries are automatically removed

---

## Rate Limiting (Reserved)

Currently no rate limiting. For production, add:

```typescript
// Per extension ID: 100 requests per hour
// Per backend: Implement request signing
// Per IP: Configure in reverse proxy
```

---

## CORS Headers (Required)

### Request
```
Origin: chrome-extension://extension-id
```

### Response
```
Access-Control-Allow-Origin: http://127.0.0.1:*
Access-Control-Allow-Methods: POST, GET, OPTIONS
Access-Control-Allow-Headers: Content-Type, X-Requested-With
Access-Control-Allow-Credentials: true
```

---

## Timeout Behavior

| Operation | Timeout | Behavior |
|-----------|---------|----------|
| Analysis request | 30 seconds | Abort fetch, show error |
| Health check | 5 seconds | Return false if no response |
| Content extraction | No limit | Async, parallel processing |
| Image resize | Per image | Skip on timeout |

---

## Logging Levels

### Console Prefixes
- `[Content Script]` - Page content extraction
- `[Service Worker]` - Message routing, API calls
- `[API]` - HTTP communication details

### Log Examples
```
[Content Script] Received page content request
[Content Script] Extracting 5 images...
[Service Worker] Cache hit for https://example.com
[Service Worker] Starting analysis for https://example.com
[API] Validation error: Content too short
[API] POST /api/analyze 200ms
[API] Backend unreachable
```

---

## Testing Examples

### Test Content Extraction
```javascript
chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
  chrome.tabs.sendMessage(tabs[0].id, {
    type: 'REQUEST_PAGE_CONTENT'
  }, (response) => {
    console.log('Extracted:', response)
  })
})
```

### Test Analysis
```javascript
chrome.runtime.sendMessage({
  type: 'ANALYZE_PAGE',
  payload: {
    url: 'https://example.com',
    title: 'Test',
    content: 'This is a test with enough characters to pass validation checks and actually submit to backend'
  }
}, (response) => {
  console.log('Analysis result:', response)
})
```

### Test Backend Health
```bash
curl http://127.0.0.1:8000/health
```

### Test Analysis Endpoint
```bash
curl -X POST http://127.0.0.1:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "title": "Test Article",
    "content": "This is a test article with sufficient content for analysis..."
  }'
```

---

## Debugging Checklist

- [ ] All error messages are user-friendly
- [ ] All API calls include timestamps
- [ ] All timeouts are configurable
- [ ] All messages include context
- [ ] All errors are catchable/retryable
- [ ] Cache is inspectable
- [ ] Health check is reliable
- [ ] Network requests are visible in DevTools

---

## Migration Notes

### From Localhost to Production

1. Update backend URL:
   ```typescript
   const API_BASE_URL = 'https://api.yourdomain.com'
   ```

2. Update CORS in backend:
   ```python
   allow_origins=["https://yourdomain.com"]
   ```

3. Update manifest permissions:
   ```json
   "host_permissions": ["https://yourdomain.com/*"]
   ```

4. Add authentication:
   ```typescript
   headers: {
     'Authorization': `Bearer ${apiKey}`
   }
   ```

5. Enable HTTPS:
   ```typescript
   // Use https:// in all URLs
   ```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-02-14 | Initial release with localhost support |

---

## References

- [Chrome Extension Messages API](https://developer.chrome.com/docs/extensions/reference/runtime/#method-sendMessage)
- [Fetch API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Validation](https://pydantic-docs.helpmanual.io/)
