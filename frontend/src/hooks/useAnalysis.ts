/**
 * useAnalysis Hook - WITH DEBUGGING
 * Manages analysis state and communication with background service worker
 */

import { useState, useCallback, useEffect, useRef } from 'react'
import { AnalysisResponse } from '../services/api'

interface CachedAnalysis {
  result: AnalysisResponse
}

type AnalysisStatus = 'idle' | 'analyzing' | 'done' | 'error'

interface UseAnalysisReturn {
  status: AnalysisStatus
  data: AnalysisResponse | null
  error: string | null
  analyze: () => Promise<void>
  cancel: () => void
  reset: () => void
}

export function useAnalysis(): UseAnalysisReturn {
  const [status, setStatus] = useState<AnalysisStatus>('idle')
  const [data, setData] = useState<AnalysisResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const timeoutRef = useRef<NodeJS.Timeout | null>(null)
  const isWaitingRef = useRef(false)

  // Add global message listener to catch ALL messages
  useEffect(() => {
    const globalListener = (message: any) => {
      console.log('🔔 [Popup] Received message:', message.type, message)
      
      if (message.type === 'ANALYSIS_COMPLETE') {
        console.log('✅ [Popup] Analysis complete, setting data:', message.payload.result)
        setData(message.payload.result)
        setStatus('done')
      } else if (message.type === 'ANALYSIS_ERROR') {
        console.error('❌ [Popup] Analysis error:', message.payload.error)
        setError(message.payload.error)
        setStatus('error')
      } else if (message.type === 'ANALYSIS_PROGRESS') {
        console.log('⏳ [Popup] Progress:', message.payload.status, message.payload.progress + '%')
      }
    }

    chrome?.runtime?.onMessage?.addListener(globalListener)

    return () => {
      chrome?.runtime?.onMessage?.removeListener(globalListener)
    }
  }, [])

  const analyze = useCallback(async () => {
    console.log('🚀 [Popup] Starting analysis...')
    setStatus('analyzing')
    setError(null)
    setData(null)

    try {
      // Ensure Chrome extension APIs are available
      if (typeof chrome === 'undefined' || !chrome.tabs || !chrome.tabs.query) {
        throw new Error(
          'Chrome extension APIs unavailable. Load this app as a browser extension.'
        )
      }

      // Get current tab
      console.log('📑 [Popup] Getting current tab...')
      const [tab] = (await chrome.tabs.query({ active: true, currentWindow: true })) as any[]
      if (!tab || !tab.id) throw new Error('No active tab found')
      console.log('✓ [Popup] Current tab:', tab.url)

      // Request page content from content script
      console.log('📨 [Popup] Requesting page content from content script...')
      let pageContent: any
      try {
        pageContent = await chrome.tabs.sendMessage(tab.id, {
          type: 'REQUEST_PAGE_CONTENT',
        })
        console.log('✓ [Popup] Got page content:', pageContent.url, 'Length:', pageContent.content?.length)
      } catch (sendErr: any) {
        console.warn('⚠ [Popup] Content script not responding, attempting injection...')
        
        const msg = String(sendErr?.message || sendErr)
        if (msg.includes('Receiving end does not exist') || msg.includes('Could not establish connection')) {
          try {
            if (chrome.scripting && chrome.scripting.executeScript) {
              console.log('💉 [Popup] Injecting content script...')
              await chrome.scripting.executeScript({
                target: { tabId: tab.id },
                files: ['src/content.js'],
              })
              pageContent = await chrome.tabs.sendMessage(tab.id, {
                type: 'REQUEST_PAGE_CONTENT',
              })
              console.log('✓ [Popup] Content script injected and responded')
            } else {
              throw new Error('Content script missing and chrome.scripting API unavailable')
            }
          } catch (injectErr: any) {
            throw new Error('Failed to inject content script: ' + (injectErr?.message || injectErr))
          }
        } else {
          throw sendErr
        }
      }

      if (!pageContent || !pageContent.content || pageContent.content.length < 50) {
        throw new Error('Page content too short or unavailable. Need at least 50 characters.')
      }

      // Check cache first
      console.log('💾 [Popup] Checking cache...')
      const cacheKey = `analysis_${pageContent.url}`

      const cached = await chrome.storage.local.get(cacheKey) as Record<string, CachedAnalysis>

      if (cached[cacheKey]) {
        setData(cached[cacheKey].result)
        setStatus('done')
        return
      }
      console.log('○ [Popup] No cache found, requesting fresh analysis')

      // Send analysis request to background worker
      console.log('📤 [Popup] Sending ANALYZE_PAGE to service worker...')
      console.log('   URL:', pageContent.url)
      console.log('   Content length:', pageContent.content.length)
      console.log('   Title:', pageContent.title)

      // Set up timeout BEFORE sending message
      console.log('⏳ [Popup] Waiting for response (with 120s timeout)...')
      isWaitingRef.current = true
      
      timeoutRef.current = setTimeout(() => {
        if (isWaitingRef.current) {
          console.error('⏰ [Popup] Timeout: No response after 120 seconds')
          setError('Analysis timeout. Service worker did not respond.')
          setStatus('error')
          isWaitingRef.current = false
        }
      }, 120000)

      // Send message with callback
      chrome.runtime.sendMessage({
        type: 'ANALYZE_PAGE',
        payload: {
          ...pageContent,
          tabId: tab.id,
        },
      }, (response: any) => {
        console.log('📥 [Popup] Service worker responded via callback:', response)
        
        // Clear timeout since we got a response
        if (timeoutRef.current) {
          clearTimeout(timeoutRef.current)
          timeoutRef.current = null
        }
        isWaitingRef.current = false
        
        if (chrome.runtime.lastError) {
          console.error('❌ [Popup] Runtime error:', chrome.runtime.lastError)
          setError(chrome.runtime.lastError.message || 'Failed to communicate with service worker')
          setStatus('error')
          return
        }
        
        if (response) {
          if (response.type === 'ANALYSIS_COMPLETE') {
            console.log('✅ [Popup] Analysis complete, setting data')
            setData(response.payload.result)
            setStatus('done')
          } else if (response.type === 'ANALYSIS_ERROR') {
            console.error('❌ [Popup] Analysis error:', response.payload.error)
            setError(response.payload.error)
            setStatus('error')
          } else if (response.status === 'error') {
            const errorMessage = response.error || 'Service worker returned an error'
            console.error('❌ [Popup] Analysis error:', errorMessage)
            setError(errorMessage)
            setStatus('error')
          } else if (response.status === 'complete') {
            // Backward compatibility with older worker response shape.
            if (response.cached) {
              ;(async () => {
                const cacheKey = `analysis_${pageContent.url}`
                const cached = await chrome.storage.local.get(cacheKey) as Record<string, CachedAnalysis>
                if (cached[cacheKey]?.result) {
                  setData(cached[cacheKey].result)
                  setStatus('done')
                } else {
                  setError('Analysis completed but cached result was not found')
                  setStatus('error')
                }
              })()
            } else {
              setError('Service worker returned an incomplete response')
              setStatus('error')
            }
          } else {
            setError('Unexpected response from service worker')
            setStatus('error')
          }
        } else {
          console.error('❌ [Popup] Empty response from service worker')
          setError('Service worker returned no response')
          setStatus('error')
        }
      })

    } catch (err: any) {
      console.error('❌ [Popup] Analysis failed:', err)
      setError(err.message || 'Analysis failed')
      setStatus('error')
    }
  }, [status])

  const cancel = useCallback(() => {
    console.log('🛑 [Popup] Cancelling...')
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
      timeoutRef.current = null
    }
    isWaitingRef.current = false
    ;(async () => {
      try {
        if (typeof chrome !== 'undefined' && chrome.tabs) {
          const [tab] = (await chrome.tabs.query({ active: true, currentWindow: true })) as any[]
          chrome.runtime.sendMessage({
            type: 'CANCEL_ANALYSIS',
            payload: { tabId: tab?.id },
          })
        }
      } catch {} finally {
        setStatus('idle')
        setError(null)
      }
    })()
  }, [])

  const reset = useCallback(() => {
    console.log('🔄 [Popup] Resetting...')
    setStatus('idle')
    setData(null)
    setError(null)
  }, [])

  return { status, data, error, analyze, cancel, reset }
}
