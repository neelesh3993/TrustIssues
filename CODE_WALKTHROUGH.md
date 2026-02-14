# Code Walkthrough — Implementation Details

This document explains the key implementation decisions and code patterns in the integration.

---

## Content Script: `src/content/content-script.ts`

### Purpose
Run in webpage context to extract content and communicate with extension

### Key Functions

#### `extractPageText(): string`

```typescript
function extractPageText(): string {
  // Clone document to avoid modifying page
  const clone = document.documentElement.cloneNode(true) as HTMLElement
  
  // Remove non-content elements
  clone.querySelectorAll('script, style, meta, noscript, svg, iframe').forEach(el => el.remove())
  
  // Get clean text
  let text = clone.innerText
    .split('\n')
    .map(line => line.trim())
    .filter(line => line.length > 0)
    .join('\n')
  
  // Truncate to 10KB
  return text.substring(0, 10000)
}
```

**Design Decisions:**
- Clone document to prevent side effects
- Remove empty lines for cleaner output
- 10,000 character limit is good compromise between:
  - Large enough for meaningful analysis
  - Small enough to avoid memory issues
  - Fast transmission to backend

#### `extractPageImages(): Promise<string[]>`

```typescript
async function extractPageImages(): Promise<string[]> {
  const images: string[] = []
  const imgElements = document.querySelectorAll('img')
  
  // Process up to 5 images
  for (let i = 0; i < Math.min(imgElements.length, 5); i++) {
    try {
      const canvas = document.createElement('canvas')
      const ctx = canvas.getContext('2d')
      
      // Resize to max 800px width
      const maxWidth = 800
      const newHeight = (img.naturalHeight / img.naturalWidth) * maxWidth
      
      canvas.width = maxWidth
      canvas.height = newHeight
      ctx.drawImage(img, 0, 0, maxWidth, newHeight)
      
      // Convert to JPEG 70% quality
      const base64 = canvas.toDataURL('image/jpeg', 0.7)
      
      // Only add if < 500KB
      if (base64.length < 500000) {
        images.push(base64)
      }
    } catch (error) {
      // Skip image on error (CORS, etc.)
      console.debug('Could not extract image:', error)
      continue
    }
  }
  
  return images
}
```

**Design Decisions:**
- Max 5 images: Balance between coverage and payload size
- Resize to 800px: Most images scaled to reasonable size
- JPEG 70% quality: Visual fidelity vs file size
- Skip on error: Gracefully handle CORS-blocked images
- 500KB limit: Prevent massive payloads

#### Message Listener

```typescript
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'REQUEST_PAGE_CONTENT') {
    // Async extraction must keep channel open
    getPageContent()
      .then(content => sendResponse(content))
      .catch(error => sendResponse({ error: error.message }))
    
    return true  // ← Critical: Keep channel open!
  }
})
```

**Why `return true`?**
- Content extraction is async (image processing)
- Must return `true` to keep message channel open
- Without this, `sendResponse` would be called too early

---

## Service Worker: `src/background/service-worker.ts`

### Purpose
Central message router and API coordinator

### Request Lifecycle

```typescript
// 1. Receive message from popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'ANALYZE_PAGE') {
    // Keep channel open for async work
    handleAnalyzeRequest(message, sender, sendResponse)
    return true
  }
})

// 2. Validate content
if (!content || content.length < 50) {
  sendResponse({ status: 'error', error: 'Content too short' })
  return
}

// 3. Health check
await ensureBackendHealthy()

// 4. Check cache
const cached = await chrome.storage.local.get(`analysis_${url}`)
if (cached && isLessThanOneHourOld(cached)) {
  sendResponse({ status: 'complete', cached: true })
  return
}

// 5. Call backend
const result = await analyzePageContent(
  { url, content, title },
  controller.signal  // For cancellation
)

// 6. Store in cache
await chrome.storage.local.set({
  [`analysis_${url}`]: {
    result,
    timestamp: Date.now()
  }
})

// 7. Notify popup
notifyPopup({
  type: 'ANALYSIS_COMPLETE',
  payload: { result, cached: false }
})
```

### Error Handling Strategy

```typescript
try {
  // Normal flow
} catch (error: any) {
  let errorMessage = 'Default error'
  
  // Handle specific error types
  if (error.name === 'AbortError') {
    if (isTimeout) {
      errorMessage = 'Analysis timeout (30 seconds)...'
    } else {
      errorMessage = 'Analysis cancelled by user'
    }
  } else if (error.message.includes('Failed to fetch')) {
    errorMessage = 'Backend unreachable. Ensure FastAPI server is running...'
  } else if (error.message.includes('400')) {
    errorMessage = 'Invalid content. Backend could not parse...'
  } else if (error.message.includes('500')) {
    errorMessage = 'Backend error. Pipeline encountered issue...'
  }
  
  // Send user-friendly message
  notifyPopup({
    type: 'ANALYSIS_ERROR',
    payload: { error: errorMessage }
  })
}
```

**Philosophy:**
- Specific error types → Specific messages
- User doesn't see "TypeError" or "Network error"
- Backend developers can debug from messages
- Users get guidance on next steps

### Cancellation Pattern

```typescript
// Create abort controller for this request
const controller = new AbortController()
activeRequests.set(tabId, controller)

try {
  // Pass signal to fetch
  const result = await analyzePageContent(
    { ... },
    controller.signal
  )
} finally {
  // Clean up
  activeRequests.delete(tabId)
}

// When user cancels
function handleCancelAnalysis(message, sendResponse) {
  const controller = activeRequests.get(message.payload.tabId)
  if (controller) {
    controller.abort()  // Aborts the fetch
    activeRequests.delete(tabId)
  }
}
```

**Benefits:**
- Fetch automatically rejects when signal aborts
- Clean promise handling
- No resource leaks

### Cache Cleanup

```typescript
// Runs on install
chrome.runtime.onInstalled.addListener(() => {
  cleanupOldCache()
})

// Runs every 24 hours
chrome.alarms.create('cleanupCache', { periodInMinutes: 24 * 60 })
chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === 'cleanupCache') {
    cleanupOldCache()
  }
})

// Remove entries older than 7 days
async function cleanupOldCache() {
  const storage = await chrome.storage.local.get()
  const sevenDaysAgo = Date.now() - (7 * 24 * 60 * 60 * 1000)
  
  for (const [key, value] of Object.entries(storage)) {
    if (key.startsWith('analysis_') && value.timestamp < sevenDaysAgo) {
      await chrome.storage.local.remove(key)
    }
  }
}
```

**Why 7 days?**
- Long enough to cache repeated analyses
- Short enough that stale results don't accumulate
- Balances storage vs relevance

---

## API Service: `src/services/api.ts`

### Connection Configuration

```typescript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000'
const ANALYSIS_TIMEOUT_MS = 30000  // 30 seconds
```

**Design:**
- Development default: localhost
- Production: set `REACT_APP_API_URL` env var
- 30s timeout: Industry standard for API calls

### Timeout Implementation

```typescript
const controller = new AbortController()
let timeoutId: NodeJS.Timeout | null = null

try {
  // Setup timeout
  timeoutId = setTimeout(() => {
    controller.abort()
  }, ANALYSIS_TIMEOUT_MS)
  
  // Fetch uses this signal
  const response = await fetch(url, {
    signal: controller.signal
  })
} finally {
  // Always cleanup
  if (timeoutId) clearTimeout(timeoutId)
}
```

**Why AbortController?**
- Standard way to cancel fetch requests
- Works with external signals too
- Avoids fetch "hanging" indefinitely

### Input Validation

```typescript
export async function analyzePageContent(
  request: AnalysisRequest,
  signal?: AbortSignal
): Promise<AnalysisResponse> {
  // Validate request
  if (!request.content || request.content.trim().length === 0) {
    throw new ValidationError('Content cannot be empty')
  }
  
  if (request.content.length < 50) {
    throw new ValidationError('Content too short (minimum 50 characters required)')
  }
  
  if (request.content.length > 50000) {
    console.warn('[API] Content exceeds 50KB, truncating')
    request.content = request.content.substring(0, 50000)
  }
}
```

**Why?**
- Fail fast before network call
- Truncate instead of reject large content
- Consistent error messages

### Error Classification

```typescript
// Transform different error types
if (error.name === 'AbortError') {
  throw new TimeoutError('Analysis timeout...')
}

if (error instanceof TypeError) {
  if (error.message.includes('Failed to fetch')) {
    throw new NetworkError(
      `Cannot reach backend at ${API_BASE_URL}`,
      'Ensure FastAPI server is running...'
    )
  }
}

// Let other errors bubble
throw error
```

**Benefits:**
- Typed error handling in catch blocks
- Service worker can respond appropriately
- UI can show specific error messages

### Signal Merging

```typescript
// Merge external signal + timeout signal
function mergeSignals(...signals: (AbortSignal | undefined)[]): AbortSignal {
  const controller = new AbortController()
  
  // If any signal aborts, abort merged signal
  signals.forEach(signal => {
    signal?.addEventListener('abort', () => controller.abort())
  })
  
  return controller.signal
}
```

**Use Cases:**
1. User presses "Cancel" → External signal aborts
2. Request takes > 30s → Timeout signal aborts
3. Both need to work → Merge them

---

## Backend Request/Response

### Request Model: `backend/app/models/schemas.py`

```python
class AnalysisRequest(BaseModel):
    url: str = Field(..., description="URL of analyzed page")
    content: str = Field(..., description="Text content extracted")
    title: str = Field(..., description="Page title")
    images: Optional[List[str]] = Field(
        default=None, description="Optional base64 images"
    )
```

**Why Pydantic?**
- Automatic request validation
- TypeScript-like type hints in Python
- Clear OpenAPI documentation
- Rejects invalid requests automatically

### Response Model

```python
class AnalysisResponse(BaseModel):
    aiGenerationLikelihood: float = Field(..., description="0-100%")
    credibilityScore: float = Field(..., description="0-100%")
    manipulationRisk: float = Field(..., description="0-100%")
    findings: List[str] = Field(default_factory=list)
    sources: List[Source] = Field(default_factory=list)
    report: str = Field(..., description="Detailed analysis")
```

**Design:**
- Structured JSON (not plain text)
- Multiple scores for nuance
- Always includes report
- Sources with verification status

### CORS Configuration

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:*", "http://127.0.0.1:*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Why?**
- Chrome extension runs on `chrome-extension://` URL
- Browser security requires explicit CORS headers
- Without this, fetch would fail
- Localhost-only (update for production)

### Endpoint Implementation

```python
@router.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_content(request: AnalysisRequest):
    """Analyze webpage content"""
    
    # Pydantic validates automatically
    # If invalid, returns 422 error automatically
    
    # Step 1: Extract claims
    claims = extract_claims(request.content)
    
    # Step 2: Verify claims
    verification_results = verify_claims(claims)
    
    # Step 3: Generate summary
    summary = generate_summary(request.content, claims, verification_results)
    
    # Step 4: Calculate scores
    response = AnalysisResponse(
        aiGenerationLikelihood=calculate_ai_likelihood(request.content),
        credibilityScore=calculate_credibility(verification_results),
        manipulationRisk=calculate_manipulation_risk(request.content),
        findings=extract_findings(request.content, claims),
        sources=format_sources(verification_results),
        report=summary
    )
    
    return response
```

**Async/Await:**
```python
@router.post(...)
async def analyze_content(...)  # ← async keyword
    # All I/O operations use await
    # Allows FastAPI to handle multiple requests concurrently
```

---

## Message Types Reference

### Request from Popup to Content Script
```typescript
{
  type: 'REQUEST_PAGE_CONTENT'
  // Response: { url, title, content, images, timestamp }
}
```

### Request from Popup to Service Worker
```typescript
{
  type: 'ANALYZE_PAGE',
  payload: {
    url: string,
    title: string,
    content: string,
    images?: string[]  // Optional
  }
}
```

### Notification from Service Worker to Popup
```typescript
{
  type: 'ANALYSIS_COMPLETE',
  payload: {
    result: AnalysisResponse,
    cached: boolean
  }
}

{
  type: 'ANALYSIS_ERROR',
  payload: {
    error: string,
    url: string
  }
}

{
  type: 'ANALYSIS_PROGRESS',
  payload: {
    status: string,
    progress: number  // 0-100
  }
}
```

### Health Check
```typescript
{
  type: 'CHECK_BACKEND_HEALTH'
  // Response: { healthy: boolean }
}
```

---

## Testing Strategy

### Content Script
```javascript
// Simulate page content extraction
const content = document.body.innerText
const images = []  // Would be populated by extractPageImages

// Send test message
chrome.runtime.sendMessage({
  type: 'REQUEST_PAGE_CONTENT'
}, (response) => {
  console.assert(response.content.length > 0, 'Content empty')
  console.assert(response.url.length > 0, 'URL empty')
  console.log('✓ Content extraction works')
})
```

### Service Worker
```javascript
// Simulate analysis request
chrome.runtime.sendMessage({
  type: 'CHECK_BACKEND_HEALTH'
}, (response) => {
  console.assert(response.healthy === true, 'Backend not healthy')
  console.log('✓ Health check works')
})
```

### Backend
```bash
# Test endpoint
curl -X POST http://127.0.0.1:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "url": "http://example.com",
    "title": "Test",
    "content": "This is test content with enough characters to pass validation"
  }'
```

---

## Performance Optimization Tips

1. **Caching:** Skip re-analysis within 1 hour
2. **Content Truncation:** Limit to 50KB to backend
3. **Image Compression:** JPEG 70% quality, 500KB max
4. **Async/Await:** Don't block popup UI during analysis
5. **Service Worker:** Keeps running, no restart overhead

---

## Common Patterns

### Try-Finally Cleanup
```typescript
try {
  // Do work
} finally {
  // Always cleanup (abort controllers, timeouts, etc.)
  controller.abort()
  clearTimeout(timeoutId)
  activeRequests.delete(tabId)
}
```

### User-Friendly Errors
```typescript
// Technical error → User message
Error: "Failed to fetch"
→ "Backend unreachable. Ensure FastAPI running at http://127.0.0.1:8000"
```

### Graceful Degradation
```typescript
// Try to get images, but don't fail if they're not available
try {
  images = await extractPageImages()
} catch {
  images = []  // Proceed without images
}
```

---

## References

- **Chrome Extension APIs:** https://developer.chrome.com/docs/extensions/reference/
- **Service Workers:** https://developer.chrome.com/docs/extensions/mv3/service_workers/
- **Fetch API Signals:** https://developer.mozilla.org/en-US/docs/Web/API/AbortController
- **FastAPI Async:** https://fastapi.tiangolo.com/async-concurrency/

