/**
 * useHighlight Hook
 * Provides functions to highlight claims and findings on the webpage
 */

import { useCallback } from 'react'

export function useHighlight() {
  const highlightClaims = useCallback(async (claims: string[]) => {
    console.log('[useHighlight] Highlighting claims:', claims.length)
    if (!claims || claims.length === 0) {
      console.warn('[useHighlight] No claims to highlight')
      return
    }

    try {
      const tabs = await chrome.tabs.query({ active: true, currentWindow: true })
      console.log('[useHighlight] Active tabs:', tabs)
      
      if (!tabs || tabs.length === 0) {
        console.error('[useHighlight] No active tabs found')
        return
      }
      
      const tab = tabs[0]
      if (!tab?.id) {
        console.error('[useHighlight] Tab has no ID', tab)
        return
      }

      console.log('[useHighlight] Sending HIGHLIGHT_CLAIMS to tab', tab.id, 'with', claims.length, 'claims')
      await chrome.tabs.sendMessage(tab.id, {
        type: 'HIGHLIGHT_CLAIMS',
        payload: claims,
      })
      console.log('[useHighlight] HIGHLIGHT_CLAIMS message sent successfully')
    } catch (error: any) {
      console.error('[useHighlight] Failed to highlight claims:', error?.message, error)
    }
  }, [])

  const highlightFindings = useCallback(async (findings: string[]) => {
    console.log('[useHighlight] Highlighting findings:', findings.length)
    if (!findings || findings.length === 0) {
      console.warn('[useHighlight] No findings to highlight')
      return
    }

    try {
      const tabs = await chrome.tabs.query({ active: true, currentWindow: true })
      console.log('[useHighlight] Active tabs:', tabs)
      
      if (!tabs || tabs.length === 0) {
        console.error('[useHighlight] No active tabs found')
        return
      }
      
      const tab = tabs[0]
      if (!tab?.id) {
        console.error('[useHighlight] Tab has no ID', tab)
        return
      }

      console.log('[useHighlight] Sending HIGHLIGHT_FINDINGS to tab', tab.id, 'with', findings.length, 'findings')
      await chrome.tabs.sendMessage(tab.id, {
        type: 'HIGHLIGHT_FINDINGS',
        payload: findings,
      })
      console.log('[useHighlight] HIGHLIGHT_FINDINGS message sent successfully')
    } catch (error: any) {
      console.error('[useHighlight] Failed to highlight findings:', error?.message, error)
    }
  }, [])

  const clearHighlights = useCallback(async () => {
    console.log('[useHighlight] Clearing highlights')
    try {
      const tabs = await chrome.tabs.query({ active: true, currentWindow: true })
      if (!tabs?.[0]?.id) {
        console.error('[useHighlight] Could not find active tab for clearing')
        return
      }

      console.log('[useHighlight] Sending CLEAR_HIGHLIGHTS to tab', tabs[0].id)
      await chrome.tabs.sendMessage(tabs[0].id, {
        type: 'CLEAR_HIGHLIGHTS',
        payload: {},
      })
      console.log('[useHighlight] CLEAR_HIGHLIGHTS message sent successfully')
    } catch (error: any) {
      console.error('[useHighlight] Failed to clear highlights:', error?.message, error)
    }
  }, [])

  return { highlightClaims, highlightFindings, clearHighlights }
}
