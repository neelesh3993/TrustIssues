/**
 * API Service
 * Handles communication with backend
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000'
const TIMEOUT_MS = 30000 // 30 seconds

export interface AnalysisRequest {
  url: string
  content: string
  title: string
}

export interface AnalysisResponse {
  aiGenerationLikelihood: number
  credibilityScore: number
  manipulationRisk: number
  findings: string[]
  sources: Array<{
    name: string
    headline: string
    status: string
  }>
  report: string
}

/**
 * Analyze page content via backend
 */
export async function analyzePageContent(
  request: AnalysisRequest,
  signal?: AbortSignal
): Promise<AnalysisResponse> {
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), TIMEOUT_MS)

  try {
    // Merge signals if provided
    const mergedSignal = signal
      ? (() => {
          const merged = new AbortController()
          signal.addEventListener('abort', () => merged.abort())
          controller.signal.addEventListener('abort', () => merged.abort())
          return merged.signal
        })()
      : controller.signal

    const response = await fetch(`${API_BASE_URL}/api/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest',
      },
      body: JSON.stringify(request),
      signal: mergedSignal,
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({}))
      throw new Error(
        error.message || `API error: ${response.status} ${response.statusText}`
      )
    }

    const data: AnalysisResponse = await response.json()
    return data
  } catch (error: any) {
    if (error.name === 'AbortError') {
      throw new Error('Request timeout or cancelled')
    }
    throw error
  } finally {
    clearTimeout(timeoutId)
  }
}

/**
 * Health check for backend
 */
export async function checkBackendHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`, {
      timeout: 5000,
    })
    return response.ok
  } catch {
    return false
  }
}
