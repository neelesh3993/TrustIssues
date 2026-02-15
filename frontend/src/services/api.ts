/**
 * API Service — Trust Issues Extension
 * 
 * Handles all communication with the FastAPI backend
 * Features:
 * - Timeout handling (30 seconds for analysis)
 * - Graceful error recovery
 * - Health checks
 * - Clear error messages for debugging
 * 
 * Backend URL defaults to http://127.0.0.1:8000 for local development
 */

// Configuration
const API_BASE_URL =
  process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000'
const ANALYSIS_TIMEOUT_MS = 120000 // 120 seconds
const HEALTH_CHECK_TIMEOUT_MS = 5000 // 5 seconds

// ===== Type Definitions =====

export interface AnalysisRequest {
  url: string
  content: string
  title: string
  images?: string[]
}

export interface Source {
  name: string
  headline: string
  url?: string
  snippet?: string
  status: string
}

export interface ClaimDetail {
  claim: string
  status: string
  rationale?: string
  sources: Source[]
}

export interface AnalysisResponse {
  aiGenerationLikelihood: number
  credibilityScore: number
  manipulationRisk: number
  claimBreakdown: ClaimDetail[]
  findings: string[]
  sources: Source[]
  report: string
  fromCache?: boolean
}

// ===== API Functions =====

/**
 * Analyze page content via backend API
 *
 * Flow:
 * 1. Validate request
 * 2. Send POST to /api/analyze
 * 3. Handle response or error
 * 4. Transform backend response to frontend format
 *
 * @throws Error with descriptive message for debugging
 */
export async function analyzePageContent(
  request: AnalysisRequest,
  signal?: AbortSignal
): Promise<AnalysisResponse> {
  const controller = new AbortController()
  let timeoutId: NodeJS.Timeout | null = null

  try {
    console.debug('[API] Starting analysis request', {
      url: request.url,
      contentLength: request.content.length,
      imageCount: request.images?.length ?? 0,
    })

    // Validate request content
    if (!request.content || request.content.trim().length === 0) {
      throw new ValidationError('Content cannot be empty')
    }

    if (request.content.length < 50) {
      throw new ValidationError(
        'Content too short (minimum 50 characters required)'
      )
    }

    if (request.content.length > 50000) {
      console.warn('[API] Content exceeds 50KB, truncating')
      request.content = request.content.substring(0, 50000)
    }

    // Setup timeout
    timeoutId = setTimeout(() => {
      controller.abort()
    }, ANALYSIS_TIMEOUT_MS)

    // Merge abort signals (external + timeout)
    const mergedSignal = mergeSignals(signal, controller.signal)

    // Send request to backend
    const response = await fetch(`${API_BASE_URL}/api/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
      },
      body: JSON.stringify(request),
      signal: mergedSignal,
    })

    // Handle HTTP errors
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))

      if (response.status === 400) {
        throw new ValidationError(
          errorData.detail || 'Invalid content submission'
        )
      }

      if (response.status === 500) {
        throw new ServerError(
          errorData.detail || 'Backend processing failed',
          'Try again in a moment or contact support if problem persists'
        )
      }

      throw new APIError(
        `HTTP ${response.status}: ${response.statusText}`,
        errorData.detail || 'Check backend logs for details'
      )
    }

    // Parse response
    const data = await response.json()
    console.debug('[API] Analysis complete', {
      credibilityScore: data.credibilityScore,
      findings: data.findings.length,
    })

    return data as AnalysisResponse
  } catch (error: any) {
    // Transform different error types
    if (error instanceof ValidationError || error instanceof ServerError) {
      throw error
    }

    if (error.name === 'AbortError') {
      // Distinguish between timeout and user cancellation
      const isTimeout = controller.signal.aborted && timeoutId
      throw new TimeoutError(
        isTimeout
          ? 'Analysis timeout (30 seconds). Backend might be processing slowly or unresponsive.'
          : 'Analysis cancelled by user'
      )
    }

    if (error instanceof TypeError) {
      // Network errors produce TypeError
      if (error.message.includes('Failed to fetch')) {
        throw new NetworkError(
          `Cannot reach backend at ${API_BASE_URL}`,
          'Ensure FastAPI server is running: python -m uvicorn app.main:app --reload'
        )
      }
    }

    // Unknown error
    throw new APIError(
      error.message || 'Unknown error during analysis',
      'Check browser console for stack trace'
    )
  } finally {
    if (timeoutId) clearTimeout(timeoutId)
  }
}

/**
 * Check if backend is healthy and responsive
 * Returns boolean - true if backend is reachable and responding OK
 */
export async function checkBackendHealth(): Promise<boolean> {
  try {
    console.debug('[API] Checking backend health...')

    const controller = new AbortController()
    const timeoutId = setTimeout(
      () => controller.abort(),
      HEALTH_CHECK_TIMEOUT_MS
    )

    try {
      const response = await fetch(`${API_BASE_URL}/health`, {
        method: 'GET',
        signal: controller.signal,
      })

      clearTimeout(timeoutId)
      const isHealthy = response.ok

      if (isHealthy) {
        console.debug('[API] Backend is healthy')
      } else {
        console.warn('[API] Backend returned non-OK status:', response.status)
      }

      return isHealthy
    } catch (innerError: any) {
      clearTimeout(timeoutId)
      if (innerError.name === 'AbortError') {
        console.warn('[API] Health check timed out')
      } else {
        console.warn('[API] Health check failed:', innerError.message)
      }
      return false
    }
  } catch (error) {
    console.error('[API] Unexpected error in health check:', error)
    return false
  }
}

/**
 * Get backend information/status
 * Useful for debugging and UI info display
 */
export async function getBackendInfo(): Promise<{
  status: string
  version: string
  healthy: boolean
} | null> {
  try {
    const response = await fetch(`${API_BASE_URL}/`, {
      method: 'GET',
    })

    if (!response.ok) return null

    return await response.json()
  } catch {
    return null
  }
}

// ===== Error Classes (for typed error handling) =====

class APIError extends Error {
  constructor(
    message: string,
    public userMessage: string = message,
    public details?: any
  ) {
    super(message)
    this.name = 'APIError'
  }
}

class ValidationError extends APIError {
  constructor(message: string) {
    super(message, `Invalid content: ${message}`)
    this.name = 'ValidationError'
  }
}

class NetworkError extends APIError {
  constructor(message: string, userMessage?: string) {
    super(message, userMessage || message)
    this.name = 'NetworkError'
  }
}

class TimeoutError extends APIError {
  constructor(message: string) {
    super(message, message)
    this.name = 'TimeoutError'
  }
}

class ServerError extends APIError {
  constructor(message: string, userMessage?: string) {
    super(message, userMessage || message)
    this.name = 'ServerError'
  }
}

// ===== Utility Functions =====

/**
 * Merge multiple abort signals into one
 * If any signal aborts, the merged signal aborts
 */
function mergeSignals(...signals: (AbortSignal | undefined)[]): AbortSignal {
  if (signals.length === 0) {
    return new AbortController().signal
  }

  const validSignals = signals.filter((s): s is AbortSignal => !!s)

  if (validSignals.length === 0) {
    return new AbortController().signal
  }

  if (validSignals.length === 1) {
    return validSignals[0]
  }

  const controller = new AbortController()

  validSignals.forEach((signal) => {
    signal.addEventListener('abort', () => controller.abort())
  })

  return controller.signal
}

// ===== Exports for error handling =====

export { APIError, ValidationError, NetworkError, TimeoutError, ServerError }

