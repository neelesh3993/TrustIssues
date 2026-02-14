/**
 * useAnalysis Hook
 * Manages analysis state and communication with background service worker
 */

import { useState, useCallback } from 'react'
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

  const analyze = useCallback(async () => {
    setStatus('analyzing')
    setError(null)

    try {
      // Ensure Chrome extension APIs are available
      if (typeof chrome === 'undefined' || !chrome.tabs || !chrome.tabs.query) {
        throw new Error(
          'Chrome extension APIs unavailable. Load this app as a browser extension (see QUICKSTART.md) or run the extension dev build.'
        )
      }

      // Get current tab
      const [tab] = (await chrome.tabs.query({ active: true, currentWindow: true })) as any[]
      if (!tab || !tab.id) throw new Error('No active tab found')

      // Request page content from content script
      let pageContent: any
      try {
        pageContent = await chrome.tabs.sendMessage(tab.id, {
          type: 'REQUEST_PAGE_CONTENT',
        })
      } catch (sendErr: any) {
        // If the content script isn't present, try injecting it then retry
        const msg = String(sendErr?.message || sendErr)
        if (msg.includes('Receiving end does not exist') || msg.includes('Could not establish connection')) {
          try {
            // Inject content script into the page (MV3)
            if (chrome.scripting && chrome.scripting.executeScript) {
              await chrome.scripting.executeScript({
                target: { tabId: tab.id },
                files: ['src/content.js'],
              })
              // Retry sendMessage
              pageContent = await chrome.tabs.sendMessage(tab.id, {
                type: 'REQUEST_PAGE_CONTENT',
              })
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

      // Check cache first
      const cached = await chrome.storage.local.get(`analysis_${pageContent.url}`)
      if (cached[`analysis_${pageContent.url}`]) {
        setData(cached[`analysis_${pageContent.url}`].result)
        setStatus('done')
        return
      }

      // Send analysis request to background worker
      const result = await new Promise<AnalysisResponse>((resolve, reject) => {
        const listener = (message: any) => {
          if (message.type === 'ANALYSIS_COMPLETE') {
            chrome.runtime.onMessage.removeListener(listener)
            resolve(message.payload.result)
          } else if (message.type === 'ANALYSIS_ERROR') {
            chrome.runtime.onMessage.removeListener(listener)
            reject(new Error(message.payload.error))
          }
        }

        chrome.runtime.onMessage.addListener(listener)

        chrome.runtime.sendMessage({
          type: 'ANALYZE_PAGE',
          payload: pageContent,
        })
      })

      setData(result)
      setStatus('done')
    } catch (err: any) {
      setError(err.message || 'Analysis failed')
      setStatus('error')
    }
  }, [])

  const cancel = useCallback(() => {
    ;(async () => {
      try {
        if (typeof chrome === 'undefined' || !chrome.tabs || !chrome.tabs.query) {
          // Nothing to cancel in non-extension environment
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
    setStatus('idle')
    setData(null)
    setError(null)
  }, [])

  return { status, data, error, analyze, cancel, reset }
}
