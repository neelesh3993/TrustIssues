/**
 * Background Service Worker
 * Handles extension-level logic, API calls, and message passing
 */

import { analyzePageContent } from '../services/api'

// Track active analysis requests
const activeRequests = new Map<number, AbortController>()

/**
 * Handle messages from content scripts and popup
 */
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'ANALYZE_PAGE') {
    handleAnalyzeRequest(message, sender, sendResponse)
    return true // Keep channel open for async response
  }

  if (message.type === 'CACHE_ANALYSIS') {
    handleCacheAnalysis(message)
  }

  if (message.type === 'GET_CACHED_ANALYSIS') {
    handleGetCachedAnalysis(message, sendResponse)
    return true
  }

  if (message.type === 'CANCEL_ANALYSIS') {
    handleCancelAnalysis(message)
  }
})

/**
 * Analyze page content
 */
async function handleAnalyzeRequest(
  message: any,
  sender: chrome.runtime.MessageSender,
  sendResponse: (response: any) => void
) {
  const { url, content, title } = message.payload
  const tabId = sender.tab?.id

  // Create abort controller for this request
  if (tabId) {
    activeRequests.set(tabId, new AbortController())
  }

  try {
    sendResponse({ status: 'analyzing', message: 'Starting analysis...' })

    const result = await analyzePageContent(
      {
        url,
        content,
        title,
      },
      tabId ? activeRequests.get(tabId)?.signal : undefined
    )

    // Cache the result
    if (tabId) {
      await chrome.storage.local.set({
        [`analysis_${url}`]: {
          result,
          timestamp: Date.now(),
        },
      })
    }

    // Notify popup and content script of completion
    chrome.runtime.sendMessage({
      type: 'ANALYSIS_COMPLETE',
      payload: { url, result },
    }).catch(() => {
      // Popup might not be open, this is fine
    })

    activeRequests.delete(tabId)
  } catch (error: any) {
    const errorMessage =
      error.name === 'AbortError'
        ? 'Analysis cancelled'
        : error.message || 'Failed to analyze page'

    if (tabId) {
      activeRequests.delete(tabId)
    }

    chrome.runtime.sendMessage({
      type: 'ANALYSIS_ERROR',
      payload: { url, error: errorMessage },
    }).catch(() => {
      // Popup might not be open, this is fine
    })
  }
}

/**
 * Store analysis result in cache
 */
async function handleCacheAnalysis(message: any) {
  const { url, result } = message.payload
  await chrome.storage.local.set({
    [`analysis_${url}`]: {
      result,
      timestamp: Date.now(),
    },
  })
}

/**
 * Retrieve cached analysis
 */
async function handleGetCachedAnalysis(
  message: any,
  sendResponse: (response: any) => void
) {
  const { url } = message.payload
  const cached = await chrome.storage.local.get(`analysis_${url}`)

  if (cached[`analysis_${url}`]) {
    sendResponse({ found: true, data: cached[`analysis_${url}`].result })
  } else {
    sendResponse({ found: false })
  }
}

/**
 * Cancel ongoing analysis
 */
function handleCancelAnalysis(message: any) {
  const { tabId } = message.payload
  const controller = activeRequests.get(tabId)
  if (controller) {
    controller.abort()
    activeRequests.delete(tabId)
  }
}

/**
 * Clean up old cache entries (older than 7 days)
 */
async function cleanupOldCache() {
  const storage = await chrome.storage.local.get()
  const sevenDaysAgo = Date.now() - 7 * 24 * 60 * 60 * 1000

  for (const [key, value] of Object.entries(storage)) {
    if (key.startsWith('analysis_')) {
      const data = value as { timestamp: number }
      if (data.timestamp < sevenDaysAgo) {
        await chrome.storage.local.remove(key)
      }
    }
  }
}

// Run cleanup on install
chrome.runtime.onInstalled.addListener(() => {
  cleanupOldCache()
})

// Run cleanup periodically (24 hours)
chrome.alarms.create('cleanupCache', { periodInMinutes: 24 * 60 })
chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === 'cleanupCache') {
    cleanupOldCache()
  }
})
