/**
 * Content Script
 * Runs in the context of web pages
 * Cannot access popup directly, but can communicate via service worker
 */

// Extract page metadata
function getPageContent() {
  return {
    url: window.location.href,
    title: document.title,
    content: document.body.innerText,
  }
}

// Listen for messages from popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'REQUEST_PAGE_CONTENT') {
    sendResponse(getPageContent())
  }

  if (message.type === 'SHOW_ANALYSIS_BADGE') {
    showAnalysisBadge(message.payload)
  }
})

/**
 * Show analysis badge on page (optional enhancement)
 */
function showAnalysisBadge(result: any) {
  const badge = document.createElement('div')
  badge.id = 'trust-issues-badge'
  badge.style.cssText = `
    position: fixed;
    bottom: 20px;
    right: 20px;
    background: #0d0d0d;
    border: 1px solid #333;
    border-radius: 8px;
    padding: 12px 16px;
    color: #fff;
    font-size: 12px;
    font-family: monospace;
    z-index: 999999;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    cursor: pointer;
  `

  const credibility = result.credibilityScore
  const statusColor =
    credibility > 70 ? '#4ade80' : credibility > 40 ? '#facc15' : '#ef4444'

  badge.innerHTML = `
    <div style="display: flex; align-items: center; gap: 8px;">
      <div style="width: 8px; height: 8px; background: ${statusColor}; border-radius: 50%;"></div>
      <span>Credibility: ${credibility}%</span>
    </div>
  `

  document.body.appendChild(badge)
  badge.addEventListener('click', () => {
    chrome.runtime.sendMessage({ type: 'OPEN_POPUP' })
  })

  // Remove after 10 seconds
  setTimeout(() => badge.remove(), 10000)
}
