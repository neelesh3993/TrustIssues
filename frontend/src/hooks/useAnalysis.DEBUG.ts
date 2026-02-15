/**
 * useAnalysis Hook - WITH DEBUGGING
 * Manages analysis state and communication with background service worker
 */

import { useState, useCallback, useEffect } from 'react'
import { AnalysisResponse } from '../services/api'

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
        
        // If the content script isn't present, try injecting it then retry
        const msg = String(sendErr?.message || sendErr)
        if (msg.includes('Receiving end does not exist') || msg.includes('Could not establish connection')) {
          try {
            // Inject content script into the page (MV3)
            if (chrome.scripting && chrome.scripting.executeScript) {
              console.log('💉 [Popup] Injecting content script...')
              await chrome.scripting.executeScript({
                target: { tabId: tab.id },
                files: ['src/content.js'],
              })
              // Retry sendMessage
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
      const cached = await chrome.storage.local.get(`analysis_${pageContent.url}`)
      if (cached[`analysis_${pageContent.url}`]) {
        console.log('✓ [Popup] Using cached result')
        setData(cached[`analysis_${pageContent.url}`].result)
        setStatus('done')
        return
      }
      console.log('○ [Popup] No cache found, requesting fresh analysis')

      // Send analysis request to background worker
      console.log('📤 [Popup] Sending ANALYZE_PAGE to service worker...')
      console.log('   URL:', pageContent.url)
      console.log('   Content length:', pageContent.content.length)
      console.log('   Title:', pageContent.title)

      chrome.runtime.sendMessage({
        type: 'ANALYZE_PAGE',
        payload: pageContent,
      }, (response: any) => {
        console.log('📥 [Popup] Service worker responded:', response)
        
        if (chrome.runtime.lastError) {
          console.error('❌ [Popup] Runtime error:', chrome.runtime.lastError)
          setError(chrome.runtime.lastError.message || 'Failed to communicate with service worker')
          setStatus('error')
        }
        
        if (response && response.status === 'error') {
          console.error('❌ [Popup] Service worker returned error:', response.error)
          setError(response.error)
          setStatus('error')
        }
      })

      // Note: The actual result will come via the message listener above
      // This is handled by the global listener we set up in useEffect
      console.log('⏳ [Popup] Waiting for ANALYSIS_COMPLETE message from service worker...')

      // Set a timeout to catch if we never receive a response
      setTimeout(() => {
        if (status === 'analyzing') {
          console.error('⏰ [Popup] Timeout: No response from service worker after 45 seconds')
          setError('Analysis timeout. The service worker did not respond. Try refreshing the page.')
          setStatus('error')
        }
      }, 45000)

    } catch (err: any) {
      console.error('❌ [Popup] Analysis failed:', err)
      setError(err.message || 'Analysis failed')
      setStatus('error')
    }
  }, [status])

  const cancel = useCallback(() => {
    console.log('🛑 [Popup] Cancelling analysis...')
    ;(async () => {
      try {
        if (typeof chrome === 'undefined' || !chrome.tabs || !chrome.tabs.query) {
          setStatus('idle')
          setError(null)
          return
        }

        const [tab] = (await chrome.tabs.query({ active: true, currentWindow: true })) as any[]
        const tabId = tab?.id
        chrome.runtime.sendMessage({
          type: 'CANCEL_ANALYSIS',
          payload: { tabId },
        })
      } catch {
        // Ignore cancellation errors
      } finally {
        setStatus('idle')
        setError(null)
      }
    })()
  }, [])

  const reset = useCallback(() => {
    console.log('🔄 [Popup] Resetting analysis state...')
    setStatus('idle')
    setData(null)
    setError(null)
  }, [])

  return { status, data, error, analyze, cancel, reset }
}
