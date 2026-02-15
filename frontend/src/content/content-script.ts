/**
 * Content Script — Trust Issues Extension
 * 
 * Data Flow:
 * 1. User visits webpage
 * 2. Content script runs in page context
 * 3. Popup requests page content via chrome.tabs.sendMessage()
 * 4. This script extracts and returns text, images, URL, title
 * 5. Background service worker sends data to FastAPI backend
 * 6. Results displayed in popup UI
 */

/**
 * Check if current frame is an ad or tracking iframe
 * Returns true if this is NOT a legitimate content frame
 */
function isAdFrame(): boolean {
  const url = window.location.href
  const hostname = window.location.hostname

  // List of known ad/tracking/bot-detection domains to skip
  const adDomains = [
    'doubleclick.net',
    'googleadservices.com',
    'pagead',
    'ads.',
    'adserver',
    'adservice',
    'analytics',
    'tracking',
    'facebook.com/tr',
    'twitter.com/i/',
    'pubmatic',
    'openx',
    'criteo',
    'appnexus',
    'amazon-adsystem',
    'scorecardresearch',
    'quantserve',
    'chartbeat',
    'outbrain',
    'taboola',
    'sharethis',
    'addthis',
    'js/showad',
    'pixeltrack',
    'beacon',
    'dpm.demdex',
    // Bot detection & challenge iframes
    'recaptcha',
    'challenges.cloudflare',
    'challenge.cloudflare',
    'captcha',
    'turnstile',
    // Other common iframes
    'facebook.com/plugins',
    'instagram.com/embed',
    'twitter.com/embed',
    'youtube.com/embed',
    'youtube-nocookie.com'
  ]

  // Check if URL or hostname matches ad patterns
  for (const adDomain of adDomains) {
    if (url.toLowerCase().includes(adDomain) || hostname.toLowerCase().includes(adDomain)) {
      console.debug(`[Content Script] 🚫 Detected ad/iframe frame: ${hostname} (matched: ${adDomain})`)
      return true
    }
  }

  // Check if page has no visible content (typical of ad iframes)
  if (document.body.innerText.length < 10 && url !== window.top?.location.href) {
    console.debug(`[Content Script] 🚫 Detected empty iframe (likely ad)`)
    return true
  }

  return false
}

/**
 * Check if we are in the main frame (not an iframe)
 */
function isMainFrame(): boolean {
  try {
    return window.self === window.top
  } catch (e) {
    // Cross-origin, assume not main frame
    return false
  }
}

/**
 * Extract plain text content from page
 * Removes scripts, styles, and cleans up whitespace
 * Includes fallback extraction methods if primary fails
 */
function extractPageText(): string {
  console.debug('[Content Script] Starting text extraction...')

  let text = ''

  // Method 1: Try to find main article/content area (most reliable)
  console.debug('[Content Script] Attempting article-specific extraction...')
  const articleSelectors = [
    'article',
    '[role="main"]',
    'main',
    '.article-content',
    '.post-content',
    '.entry-content',
    '.content',
    '.page-content',
    '[class*="article"]',
    '[class*="content"]'
  ]

  for (const selector of articleSelectors) {
    const element = document.querySelector(selector)
    if (element) {
      const extracted = element.innerText
        ?.split('\n')
        .map((line) => line.trim())
        .filter((line) => line.length > 0)
        .join('\n') || ''

      if (extracted.length > text.length) {
        text = extracted
        console.debug(`[Content Script] Found content via selector "${selector}": ${text.length} chars`)
      }
    }
  }

  // Fallback Method 2: Clone and extract
  if (text.length < 100) {
    console.debug('[Content Script] Article selector failed, trying clone method...')
    const clone = document.documentElement.cloneNode(true) as HTMLElement

    // Remove script, style, and other non-content elements
    const elementsToRemove = clone.querySelectorAll(
      'script, style, meta, noscript, svg, iframe, [style*="display:none"], nav, header, footer, .ad, .advertisement'
    )
    elementsToRemove.forEach((element) => element.remove())

    const cloneText = clone.innerText
      ?.split('\n')
      .map((line) => line.trim())
      .filter((line) => line.length > 0)
      .join('\n') || ''

    console.debug(`[Content Script] Clone method: ${cloneText.length} chars`)

    if (cloneText.length > text.length) {
      text = cloneText
    }
  }

  // Fallback Method 3: Direct document.body.innerText
  if (text.length < 100) {
    console.debug('[Content Script] Still <100 chars, trying body.innerText...')
    const bodyText = document.body.innerText
      ?.split('\n')
      .map((line) => line.trim())
      .filter((line) => line.length > 0)
      .join('\n') || ''

    console.debug(`[Content Script] Body method: ${bodyText.length} chars`)

    if (bodyText.length > text.length) {
      text = bodyText
    }
  }

  // Fallback Method 4: textContent (more raw, less formatted)
  if (text.length < 100) {
    console.debug('[Content Script] Still <100 chars, trying textContent...')
    const textContent = document.body.textContent
      ?.split('\n')
      .map((line) => line.trim())
      .filter((line) => line.length > 0)
      .join('\n') || ''

    console.debug(`[Content Script] TextContent method: ${textContent.length} chars`)

    if (textContent.length > text.length) {
      text = textContent
    }
  }

  console.debug(`[Content Script] Final extracted text: ${text.length} chars`)
  if (text.length < 200) {
    console.warn(`[Content Script] ⚠️  WARNING: Only ${text.length} chars extracted!`)
    console.debug(`[Content Script] First 100 chars: "${text.substring(0, 100)}"`)
    console.debug(`[Content Script] Page title: "${document.title}"`)
    console.debug(`[Content Script] Page URL: "${window.location.href}"`)
  }

  // Limit to 10,000 characters for backend processing
  return text.substring(0, 10000)
}

/**
 * Extract images from page (up to 5 large images)
 * Converts to base64 for transmission to backend
 * 
 * Note: Large images are resized to save bandwidth
 */
async function extractPageImages(): Promise<string[]> {
  const images: string[] = []
  const imgElements = document.querySelectorAll('img')

  // Process up to 5 images to keep payload reasonable
  for (let i = 0; i < Math.min(imgElements.length, 5); i++) {
    const img = imgElements[i] as HTMLImageElement

    // Skip small images (likely icons or decorative)
    if (img.width < 100 || img.height < 100) continue

    try {
      const canvas = document.createElement('canvas')
      const ctx = canvas.getContext('2d')

      if (!ctx) continue

      // Resize large images to max 800px width
      const maxWidth = 800
      const ratio = img.naturalHeight / img.naturalWidth
      const newWidth = Math.min(img.naturalWidth, maxWidth)
      const newHeight = newWidth * ratio

      canvas.width = newWidth
      canvas.height = newHeight

      // Load image CORS-safe (might fail for cross-origin images)
      const tempImg = new Image()
      tempImg.crossOrigin = 'anonymous'
      tempImg.onload = () => {
        ctx.drawImage(tempImg, 0, 0, newWidth, newHeight)
        const base64 = canvas.toDataURL('image/jpeg', 0.7)
        if (base64.length < 500000) {
          // Only add if under 500KB
          images.push(base64)
        }
      }
      tempImg.src = img.src
    } catch (error) {
      console.debug('Could not extract image:', error)
      // Continue with next image on error
    }
  }

  return images
}

/**
 * Get complete page content object
 * Called by popup or background script
 */
async function getPageContent() {
  const images = await extractPageImages()

  return {
    url: window.location.href,
    title: document.title,
    content: extractPageText(),
    images: images.length > 0 ? images : undefined,
    timestamp: new Date().toISOString(),
  }
}

/**
 * Message listener
 * Responds to requests from popup and background script
 */
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  // Handle page content request from popup
  if (message.type === 'REQUEST_PAGE_CONTENT') {
    const frameUrl = window.location.href
    const isMain = isMainFrame()
    console.debug(`[Content Script] Received page content request from frameId ${sender.frameId} (main: ${isMain}, url: ${frameUrl})`)

    // CRITICAL: Don't respond if we're in an ad/tracking frame
    if (isAdFrame()) {
      console.debug('[Content Script] 🚫 Ignoring request - running in ad frame, not responding')
      return false // Don't respond, let popup try other frames
    }

    // Log if not main frame but still responding
    if (!isMain) {
      console.debug('[Content Script] ⚠️  Running in iframe (not main frame): ' + frameUrl)
      console.debug('[Content Script] Still responding because it passed ad frame check')
      // Still try to extract, but log it
    }

    getPageContent()
      .then((content) => {
        console.debug('[Content Script] Sending page content:', {
          url: content.url,
          contentLength: content.content.length,
          imageCount: content.images?.length ?? 0,
        })
        sendResponse(content)
      })
      .catch((error) => {
        console.error('[Content Script] Error extracting content:', error)
        sendResponse({
          error: 'Failed to extract page content',
          details: error.message,
        })
      })
    return true // Keep channel open for async response
  }

  // Handle showing analysis results badge
  if (message.type === 'SHOW_ANALYSIS_BADGE') {
    showAnalysisBadge(message.payload)
  }

  // Handle injection of content analysis highlighting
  if (message.type === 'HIGHLIGHT_FINDINGS') {
    console.log('[Content Script] Received HIGHLIGHT_FINDINGS message:', message.payload)
    highlightFindings(message.payload)
    sendResponse({ success: true })
    return true
  }

  // Handle highlighting of claims
  if (message.type === 'HIGHLIGHT_CLAIMS') {
    console.log('[Content Script] Received HIGHLIGHT_CLAIMS message:', message.payload)
    highlightClaims(message.payload)
    sendResponse({ success: true })
    return true
  }

  // Handle clearing all highlights
  if (message.type === 'CLEAR_HIGHLIGHTS') {
    console.log('[Content Script] Received CLEAR_HIGHLIGHTS message')
    clearAllHighlights()
    sendResponse({ success: true })
    return true
  }
})

/**
 * Show credibility badge on page
 * Appears for 10 seconds in bottom-right corner
 */
function showAnalysisBadge(result: any) {
  console.debug('[Content Script] Showing analysis badge')

  // Avoid duplicate badges
  if (document.getElementById('trust-issues-badge')) {
    return
  }

  const badge = document.createElement('div')
  badge.id = 'trust-issues-badge'

  const credibility = Math.round(result.credibilityScore)
  const statusColor =
    credibility > 70 ? '#4ade80' : credibility > 40 ? '#facc15' : '#ef4444'
  const riskLevel = Math.round(result.manipulationRisk)

  badge.style.cssText = `
    position: fixed;
    bottom: 20px;
    right: 20px;
    background: #0d0d0d;
    border: 2px solid ${statusColor};
    border-radius: 8px;
    padding: 12px 16px;
    color: #fff;
    font-size: 12px;
    font-family: system-ui, -apple-system, sans-serif;
    z-index: 999999;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    cursor: pointer;
    font-weight: 500;
  `

  badge.innerHTML = `
    <div style="display: flex; flex-direction: column; gap: 8px;">
      <div style="display: flex; align-items: center; gap: 8px;">
        <div style="
          width: 12px;
          height: 12px;
          background: ${statusColor};
          border-radius: 50%;
        "></div>
        <span style="font-weight: bold;">Credibility: ${credibility}%</span>
      </div>
      <div style="font-size: 11px; opacity: 0.8;">
        Risk: ${riskLevel}% | AI: ${Math.round(result.aiGenerationLikelihood)}%
      </div>
    </div>
  `

  document.body.appendChild(badge)

  badge.addEventListener('click', () => {
    console.debug('[Content Script] Badge clicked, opening popup')
    chrome.runtime.sendMessage({ type: 'OPEN_POPUP' }).catch(() => {
      // Popup might not be open
    })
  })

  // Remove badge after 10 seconds
  setTimeout(() => {
    badge.remove()
  }, 10000)
}

/**
 * Clear all highlights from the page
 */
function clearAllHighlights() {
  console.debug('[Content Script] Clearing all highlights')
  const highlights = document.querySelectorAll('mark[data-trust-highlight]')
  highlights.forEach((mark) => {
    const parent = mark.parentNode
    if (parent) {
      while (mark.firstChild) {
        parent.insertBefore(mark.firstChild, mark)
      }
      parent.removeChild(mark)
    }
  })
}

/**
 * Highlight claims in the page
 * Marks claims with blue backgrounds
 */
function highlightClaims(claims: string[]) {
  console.debug('[Content Script] Highlighting claims:', claims.length)
  console.debug('[Content Script] Claims to highlight:', claims)

  if (!claims || claims.length === 0) {
    console.warn('[Content Script] No claims provided')
    return
  }

  const walker = document.createTreeWalker(
    document.body,
    NodeFilter.SHOW_TEXT,
    null,
    false
  )

  const nodesToReplace: Array<[Node, DocumentFragment]> = []
  let totalMatches = 0

  let node: Node | null
  while ((node = walker.nextNode())) {
    let hasMatch = false
    let fragment = document.createDocumentFragment()
    let lastIndex = 0

    claims.forEach((claim) => {
      if (!claim || claim.length < 5) return // Skip very short claims
      
      const lowerText = node!.textContent!.toLowerCase()
      const lowerClaim = claim.toLowerCase()
      let index = lowerText.indexOf(lowerClaim)

      while (index !== -1) {
        hasMatch = true
        totalMatches++
        // Add text before match
        if (index > lastIndex) {
          fragment.appendChild(
            document.createTextNode(node!.textContent!.substring(lastIndex, index))
          )
        }

        // Add highlighted match
        const highlight = document.createElement('mark')
        highlight.setAttribute('data-trust-highlight', 'claim')
        highlight.style.cssText = `
          background-color: #3b82f6;
          color: white;
          text-decoration: none;
          cursor: pointer;
          padding: 2px 4px;
          border-radius: 2px;
          font-weight: 500;
        `
        highlight.textContent = node!.textContent!.substring(
          index,
          index + lowerClaim.length
        )
        fragment.appendChild(highlight)

        lastIndex = index + lowerClaim.length
        index = lowerText.indexOf(lowerClaim, lastIndex)
      }
    })

    if (hasMatch) {
      // Add remaining text
      if (lastIndex < node.textContent!.length) {
        fragment.appendChild(
          document.createTextNode(node.textContent!.substring(lastIndex))
        )
      }
      nodesToReplace.push([node, fragment])
    }
  }

  // Replace nodes (do this after walking to avoid modifying tree during iteration)
  nodesToReplace.forEach(([originalNode, fragment]) => {
    originalNode.parentNode?.replaceChild(fragment, originalNode)
  })
  
  console.debug('[Content Script] Highlighted claims complete. Total matches:', totalMatches)
}

/**
 * Highlight findings in the page
 * Marks findings with yellow backgrounds and red underlines
 */
function highlightFindings(findings: string[]) {
  console.debug('[Content Script] Highlighting findings:', findings.length)

  const walker = document.createTreeWalker(
    document.body,
    NodeFilter.SHOW_TEXT,
    null,
    false
  )

  const nodesToReplace: Array<[Node, DocumentFragment]> = []

  let node: Node | null
  while ((node = walker.nextNode())) {
    let hasMatch = false
    let fragment = document.createDocumentFragment()
    let lastIndex = 0

    findings.forEach((finding) => {
      if (!finding || finding.length < 5) return // Skip very short findings
      
      const lowerText = node.textContent.toLowerCase()
      const lowerFinding = finding.toLowerCase()
      let index = lowerText.indexOf(lowerFinding)

      while (index !== -1) {
        hasMatch = true
        // Add text before match
        if (index > lastIndex) {
          fragment.appendChild(
            document.createTextNode(node.textContent.substring(lastIndex, index))
          )
        }

        // Add highlighted match
        const highlight = document.createElement('mark')
        highlight.setAttribute('data-trust-highlight', 'finding')
        highlight.style.cssText = `
          background-color: #fef08a;
          text-decoration: underline wavy #ef4444;
          cursor: pointer;
          padding: 2px 4px;
          border-radius: 2px;
        `
        highlight.textContent = node.textContent.substring(
          index,
          index + lowerFinding.length
        )
        fragment.appendChild(highlight)

        lastIndex = index + lowerFinding.length
        index = lowerText.indexOf(lowerFinding, lastIndex)
      }
    })

    if (hasMatch) {
      // Add remaining text
      if (lastIndex < node.textContent.length) {
        fragment.appendChild(
          document.createTextNode(node.textContent.substring(lastIndex))
        )
      }
      nodesToReplace.push([node, fragment])
    }
  }

  // Replace nodes (do this after walking to avoid modifying tree during iteration)
  nodesToReplace.forEach(([originalNode, fragment]) => {
    originalNode.parentNode?.replaceChild(fragment, originalNode)
  })
}

console.log('[Content Script] Trust Issues content script loaded')
