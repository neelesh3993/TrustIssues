/**
 * Background Service Worker — Trust Issues Extension
 * 
 * Responsibilities:
 * - Receives page content from content script
 * - Routes analysis requests to backend API
 * - Manages request cancellation & timeouts
 * - Caches results for repeated analysis
 * - Converts errors to user-friendly messages
 * - Removes old cache entries
 * 
 * Data Flow:
 * Content Script → Service Worker → FastAPI Backend → Service Worker → Popup UI
 */

import { analyzePageContent, checkBackendHealth } from '../services/api'

interface CachedAnalysisEntry {
  result: any
  timestamp: number
}

// ====================
// State Management
// ====================

// Track active analysis requests for cancellation support
const activeRequests = new Map<number, AbortController>()

// Track the popup's sender info so we can send responses back
const popupSenders = new Map<number, chrome.runtime.MessageSender>()

// Backend health status
let backendHealthy = false
let lastHealthCheckTime = 0
const HEALTH_CHECK_INTERVAL = 60000 // Check every minute

// ====================
// Message Routing
// ====================

/**
 * Main message listener
 * Routes incoming messages to appropriate handlers
 */
chrome.runtime.onMessage.addListener((message: any, sender: chrome.runtime.MessageSender, sendResponse: (response?: any) => void) => {
  console.debug('[Service Worker] Received message:', message.type)
  console.debug('[Service Worker] Message from:', sender.tab?.url || sender.url || 'unknown')

  if (message.type === 'ANALYZE_PAGE') {
    handleAnalyzeRequest(message, sender, sendResponse)
    return true // Keep channel open for async response
  }

  if (message.type === 'GET_CACHED_ANALYSIS') {
    handleGetCachedAnalysis(message, sendResponse)
    return true
  }

  if (message.type === 'CANCEL_ANALYSIS') {
    handleCancelAnalysis(message, sendResponse)
    return true
  }

  if (message.type === 'CHECK_BACKEND_HEALTH') {
    handleHealthCheck(sendResponse)
    return true
  }

  if (message.type === 'CLEAR_CACHE') {
    handleClearCache(sendResponse)
    return true
  }
})

// ====================
// Request Handlers
// ====================

/**
 * Handle analysis request from content script
 * Coordinates between popup, content script, and backend API
 * Includes error recovery and user-friendly messaging
 */
async function handleAnalyzeRequest(
  message: any,
  sender: chrome.runtime.MessageSender,
  sendResponse: (response: any) => void
) {
  const { url, content, title, images } = message.payload
  const tabId = sender.tab?.id ?? message.payload?.tabId

  // Validate input
  if (!content || content.trim().length < 50) {
    const error = 'Content too short. Please select at least 50 characters.'
    console.warn('[Service Worker] Validation error:', error)
    sendResponse({
      type: 'ANALYSIS_ERROR',
      payload: { error, url },
    })
    return
  }

  if (!tabId) {
    console.warn('[Service Worker] No tab ID found')
    sendResponse({
      type: 'ANALYSIS_ERROR',
      payload: { error: 'Could not identify active tab', url },
    })
    return
  }

  // Create abort controller for cancellation support
  const controller = new AbortController()
  activeRequests.set(tabId, controller)

  // Store sender info for sending responses back
  const senderTabId = sender.tab?.id ?? -1 // -1 for popup (non-tab sender)
  popupSenders.set(senderTabId, sender)

  try {
    console.log(`[Service Worker] Starting analysis for ${url}`)
    console.debug(`[Service Worker] Content length: ${content.length} chars`)

    // Check backend health first
    await ensureBackendHealthy()

    // Show progress to user
    notifyPopup({
      type: 'ANALYSIS_PROGRESS',
      payload: { status: 'Checking cache...', progress: 10 },
    })

    // Check if we have a cached result
    const cacheKey = `analysis_${url}`

    const cached = await chrome.storage.local.get(cacheKey) as Record<
      string,
      CachedAnalysisEntry
    >
    if (cached[`analysis_${url}`]) {
      const cacheAge = Date.now() - cached[`analysis_${url}`].timestamp
      // Use cache if less than 1 hour old
      if (cacheAge < 3600000) {
        console.log('[Service Worker] Using cached result')
        notifyPopup({
          type: 'ANALYSIS_COMPLETE',
          payload: { result: cached[`analysis_${url}`].result, cached: true },
        })
        activeRequests.delete(tabId)
        sendResponse({
          type: 'ANALYSIS_COMPLETE',
          payload: { result: cached[`analysis_${url}`].result, cached: true },
        })
        return
      }
    }

    // Update progress
    notifyPopup({
      type: 'ANALYSIS_PROGRESS',
      payload: { status: 'Analyzing content...', progress: 20 },
    })

    // Call backend API
    const result = await analyzePageContent(
      {
        url,
        content,
        title,
        images,
      },
      controller.signal
    )

    // Update progress
    notifyPopup({
      type: 'ANALYSIS_PROGRESS',
      payload: { status: 'Processing results...', progress: 90 },
    })

    // Cache the result
    await chrome.storage.local.set({
      [`analysis_${url}`]: {
        result,
        timestamp: Date.now(),
      },
    })

    console.log('[Service Worker] Analysis complete')

    // Notify popup of completion via sendResponse (direct callback)
    console.log('[Service Worker] Sending ANALYSIS_COMPLETE via sendResponse')
    sendResponse({
      type: 'ANALYSIS_COMPLETE',
      payload: { result, cached: false },
    })
  } catch (error: any) {
    console.error('[Service Worker] Analysis error:', error)

    // Format error message
    let errorMessage =
      error.message || 'Analysis failed. Please try again.'

    // Handle specific error types
    if (error.name === 'AbortError') {
      errorMessage = 'Analysis cancelled'
    } else if (error.message.includes('Failed to fetch')) {
      errorMessage =
        'Backend unreachable. Ensure FastAPI server is running at http://localhost:8000'
    } else if (error.message.includes('timeout')) {
      errorMessage =
        'Analysis timeout. The content might be too complex or the backend is slow.'
    } else if (error.message.includes('400')) {
      errorMessage =
        'Invalid content. The backend could not parse the submission.'
    } else if (error.message.includes('500')) {
      errorMessage =
        'Backend error. The analysis pipeline encountered an issue.'
    }

    console.error('[Service Worker] Error message for user:', errorMessage)

    // Notify popup of error via sendResponse (direct callback)
    console.log('[Service Worker] Sending ANALYSIS_ERROR via sendResponse')
    sendResponse({
      type: 'ANALYSIS_ERROR',
      payload: { error: errorMessage, url },
    })
  } finally {
    // Always clean up the abort controller
    activeRequests.delete(tabId)
    popupSenders.delete(senderTabId)
  }
}

/**
 * Retrieve cached analysis result
 */
async function handleGetCachedAnalysis(
  message: any,
  sendResponse: (response: any) => void
) {
  const { url } = message.payload
  const cacheKey = `analysis_${url}`

  const cached = await chrome.storage.local.get(cacheKey) as Record<
    string,
    CachedAnalysisEntry
  >

  if (cached[`analysis_${url}`]) {
    sendResponse({ found: true, data: cached[`analysis_${url}`].result })
  } else {
    sendResponse({ found: false })
  }
}

/**
 * Cancel ongoing analysis
 */
function handleCancelAnalysis(
  message: any,
  sendResponse: (response: any) => void
) {
  const { tabId } = message.payload
  const controller = activeRequests.get(tabId)

  if (controller) {
    controller.abort()
    activeRequests.delete(tabId)
    console.log('[Service Worker] Analysis cancelled')
    sendResponse({ status: 'cancelled' })
  } else {
    sendResponse({ status: 'no_active_request' })
  }
}

/**
 * Check backend health status
 */
async function handleHealthCheck(sendResponse: (response: any) => void) {
  try {
    const healthy = await checkBackendHealth()
    console.log('[Service Worker] Backend health:', healthy ? 'OK' : 'FAILED')
    sendResponse({ healthy })
  } catch (error) {
    console.error('[Service Worker] Health check error:', error)
    sendResponse({ healthy: false })
  }
}

/**
 * Clear all cached analysis data
 */
async function handleClearCache(sendResponse: (response: any) => void) {
  const storage = await chrome.storage.local.get()

  const keysToRemove = Object.keys(storage).filter((key) =>
    key.startsWith('analysis_')
  )

  await chrome.storage.local.remove(keysToRemove)

  console.log(`[Service Worker] Cleared ${keysToRemove.length} cache entries`)
  sendResponse({ cleared: keysToRemove.length })
}

// ====================
// Utility Functions
// ====================

/**
 * Helper: Check and update backend health status
 */
async function ensureBackendHealthy() {
  const now = Date.now()

  // Check every minute
  if (now - lastHealthCheckTime < HEALTH_CHECK_INTERVAL) {
    if (!backendHealthy) {
      throw new Error('Backend is unreachable')
    }
    return
  }

  lastHealthCheckTime = now

  try {
    backendHealthy = await checkBackendHealth()
    if (!backendHealthy) {
      throw new Error('Backend health check failed')
    }
    console.log('[Service Worker] Backend is healthy')
  } catch (error) {
    console.error('[Service Worker] Backend health check failed:', error)
    throw new Error(
      'Backend unreachable at http://127.0.0.1:8000. Is FastAPI running?'
    )
  }
}

/**
 * Helper: Send message to popup (fails silently if popup not open)
 */
function notifyPopup(message: any) {
  chrome.runtime.sendMessage(message).catch(() => {
    console.debug('[Service Worker] Popup not open, message not delivered')
  })
}

// ====================
// Lifecycle Management
// ====================

/**
 * Clean up old cache entries on install
 */
chrome.runtime.onInstalled.addListener(async () => {
  console.log('[Service Worker] Extension installed')
  await cleanupOldCache()
})

/**
 * Periodic cache cleanup (every 24 hours)
 */
chrome.alarms.create('cleanupCache', { periodInMinutes: 24 * 60 })
chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === 'cleanupCache') {
    console.log('[Service Worker] Running scheduled cache cleanup')
    cleanupOldCache()
  }
})

/**
 * Remove cache entries older than 7 days
 */
async function cleanupOldCache() {
  const storage = await chrome.storage.local.get()
  const sevenDaysAgo = Date.now() - 7 * 24 * 60 * 60 * 1000
  let removed = 0

  for (const [key, value] of Object.entries(storage)) {
    if (key.startsWith('analysis_')) {
      const data = value as { timestamp?: number }
      if (data.timestamp && data.timestamp < sevenDaysAgo) {
        await chrome.storage.local.remove(key)
        removed++
      }
    }
  }

  if (removed > 0) {
    console.log(
      `[Service Worker] Cache cleanup: removed ${removed} old entries`
    )
  }
}

console.log('[Service Worker] Trust Issues service worker loaded')
