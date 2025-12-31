import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios'
import type { ApiError } from '../types/api'

// Extend AxiosRequestConfig to include metadata
declare module 'axios' {
  interface AxiosRequestConfig {
    metadata?: {
      requestId: string
      startTime: number
    }
    _retry?: boolean
    _retryCount?: number
  }
}

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

// Error types for better error handling
// Re-export from types/api.ts for consistency
export type { ApiError as APIError } from '../types/api'

// Retry configuration
interface RetryConfig {
  retries: number
  retryDelay: number
  retryCondition?: (error: AxiosError) => boolean
}

const defaultRetryConfig: RetryConfig = {
  retries: 3,
  retryDelay: 1000,
  retryCondition: (error: AxiosError) => {
    // Retry on network errors or 5xx server errors
    return !error.response || (error.response.status >= 500 && error.response.status < 600)
  }
}

// Create axios instance with enhanced configuration
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000, // Increased timeout
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add request ID for tracking
let requestId = 0
const generateRequestId = () => `req_${Date.now()}_${++requestId}`

// Exponential backoff delay calculation
const calculateRetryDelay = (retryCount: number, baseDelay: number = 1000): number => {
  return Math.min(baseDelay * Math.pow(2, retryCount), 10000) // Max 10 seconds
}

// Request interceptor with enhanced logging and headers
apiClient.interceptors.request.use(
  (config) => {
    // Add request ID for tracking
    const reqId = generateRequestId()
    config.metadata = { requestId: reqId, startTime: Date.now() }
    
    // Add auth token
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    // Add tenant info if available
    const tenant = localStorage.getItem('tenant_id')
    if (tenant) {
      config.headers['X-Tenant-ID'] = tenant
    }
    
    // Add request tracking header
    config.headers['X-Request-ID'] = reqId
    
    // Log request in development
    if (import.meta.env.DEV || import.meta.env.MODE === 'development') {
      console.log(`🚀 API Request [${reqId}]:`, {
        method: config.method?.toUpperCase(),
        url: config.url,
        baseURL: config.baseURL,
        headers: config.headers,
        data: config.data
      })
    }
    
    return config
  },
  (error) => {
    console.error('❌ Request interceptor error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor with advanced error handling and retry logic
apiClient.interceptors.response.use(
  (response) => {
    // Log successful response in development
    if ((import.meta.env.DEV || import.meta.env.MODE === 'development') && response.config.metadata) {
      const duration = Date.now() - response.config.metadata.startTime
      console.log(`✅ API Response [${response.config.metadata.requestId}]:`, {
        status: response.status,
        duration: `${duration}ms`,
        data: response.data
      })
    }
    return response
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as any
    
    // Log error in development
    if (import.meta.env.DEV || import.meta.env.MODE === 'development') {
      const requestId = originalRequest?.metadata?.requestId || 'unknown'
      const duration = originalRequest?.metadata?.startTime 
        ? Date.now() - originalRequest.metadata.startTime 
        : 0
      
      console.error(`❌ API Error [${requestId}]:`, {
        status: error.response?.status,
        duration: `${duration}ms`,
        message: error.message,
        response: error.response?.data,
        url: originalRequest?.url
      })
    }
    
    // Handle token refresh for 401 errors
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      
      try {
        const refreshToken = localStorage.getItem('refresh_token')
        if (refreshToken) {
          console.log('🔄 Attempting token refresh...')
          const response = await axios.post(`${API_BASE_URL}/accounts/auth/token/refresh/`, {
            refresh: refreshToken
          })
          
          // Handle both direct token response and wrapped response
          const responseData = response.data
          const access = responseData.access || responseData.data?.access
          const refresh = responseData.refresh || responseData.data?.refresh
          
          if (access) {
            localStorage.setItem('access_token', access)
            
            // Update refresh token if provided
            if (refresh) {
              localStorage.setItem('refresh_token', refresh)
            }
            
            // Retry original request with new token
            originalRequest.headers.Authorization = `Bearer ${access}`
            console.log('✅ Token refreshed, retrying request...')
            return apiClient(originalRequest)
          } else {
            throw new Error('No access token in refresh response')
          }
        }
      } catch (refreshError) {
        console.error('❌ Token refresh failed:', refreshError)
        // Clear auth data and redirect to login
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('user')
        localStorage.removeItem('tenant_id')
        
        // Dispatch custom event for auth failure
        window.dispatchEvent(new CustomEvent('auth:logout', { 
          detail: { reason: 'token_refresh_failed' } 
        }))
        
        // Redirect to login if not already there
        if (!window.location.pathname.includes('/auth/login')) {
          window.location.href = '/auth/login'
        }
        return Promise.reject(refreshError)
      }
    }
    
    // Implement retry logic for network errors and 5xx errors
    if (shouldRetry(error, originalRequest)) {
      return retryRequest(originalRequest, error)
    }
    
    // Transform error to standardized format
    const apiError = transformError(error)
    return Promise.reject(apiError)
  }
)

// Helper function to determine if request should be retried
const shouldRetry = (error: AxiosError, config: any): boolean => {
  if (!config || config._retryCount >= defaultRetryConfig.retries) {
    return false
  }
  
  // Don't retry if it's a client error (4xx) except 401 (handled separately)
  if (error.response && error.response.status >= 400 && error.response.status < 500 && error.response.status !== 401) {
    return false
  }
  
  return defaultRetryConfig.retryCondition ? defaultRetryConfig.retryCondition(error) : true
}

// Retry request with exponential backoff
const retryRequest = async (config: any, _error: AxiosError): Promise<AxiosResponse> => {
  config._retryCount = config._retryCount || 0
  config._retryCount++
  
  const delay = calculateRetryDelay(config._retryCount - 1, defaultRetryConfig.retryDelay)
  
  console.log(`🔄 Retrying request (${config._retryCount}/${defaultRetryConfig.retries}) after ${delay}ms...`)
  
  await new Promise(resolve => setTimeout(resolve, delay))
  
  return apiClient(config)
}

// Transform axios error to standardized API error
const transformError = (error: AxiosError): import('../types/api').ApiError => {
  if (error.response) {
    // Server responded with error status
    const responseData = error.response.data as Record<string, unknown>
    return {
      message: (responseData?.message as string) || (responseData?.detail as string) || `HTTP ${error.response.status} Error`,
      code: (responseData?.code as string) || `HTTP_${error.response.status}`,
      status: error.response.status,
      errors: responseData?.errors as Record<string, string[]> | undefined,
      timestamp: (responseData?.timestamp as string) || new Date().toISOString(),
      detail: responseData?.detail as string | undefined
    }
  } else if (error.request) {
    // Network error
    return {
      message: 'Network error - please check your connection',
      code: 'NETWORK_ERROR',
      status: 0
    }
  } else {
    // Request setup error
    return {
      message: error.message || 'An unexpected error occurred',
      code: 'REQUEST_ERROR',
      status: 0
    }
  }
}

// Import response types from centralized location
import type { APIResponse, PaginatedResponse, ErrorResponse } from '../types/api'

// Re-export for backward compatibility
export type { APIResponse as ApiResponse, PaginatedResponse, ErrorResponse }

/**
 * Enhanced API methods with better error handling and type safety
 * 
 * All methods return Promise<AxiosResponse<APIResponse<T>>> where T is the expected data type.
 * The actual data is accessed via response.data.data
 * 
 * @example
 * const response = await api.get<User>('/users/123/')
 * const user: User = response.data.data
 */
export const api = {
  /**
   * GET request
   * @param url - API endpoint URL
   * @param config - Optional Axios request configuration
   * @returns Promise with typed response
   */
  get: <T = unknown>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<APIResponse<T>>> =>
    apiClient.get(url, config),
    
  /**
   * POST request
   * @param url - API endpoint URL
   * @param data - Request body data
   * @param config - Optional Axios request configuration
   * @returns Promise with typed response
   */
  post: <T = unknown>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<AxiosResponse<APIResponse<T>>> =>
    apiClient.post(url, data, config),
    
  /**
   * PUT request
   * @param url - API endpoint URL
   * @param data - Request body data
   * @param config - Optional Axios request configuration
   * @returns Promise with typed response
   */
  put: <T = unknown>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<AxiosResponse<APIResponse<T>>> =>
    apiClient.put(url, data, config),
    
  /**
   * PATCH request
   * @param url - API endpoint URL
   * @param data - Request body data
   * @param config - Optional Axios request configuration
   * @returns Promise with typed response
   */
  patch: <T = unknown>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<AxiosResponse<APIResponse<T>>> =>
    apiClient.patch(url, data, config),
    
  /**
   * DELETE request
   * @param url - API endpoint URL
   * @param config - Optional Axios request configuration
   * @returns Promise with typed response
   */
  delete: <T = unknown>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<APIResponse<T>>> =>
    apiClient.delete(url, config),

  // Health check method
  healthCheck: async (): Promise<boolean> => {
    try {
      const response = await apiClient.get('/health/')
      return response.status === 200
    } catch (error) {
      console.error('Health check failed:', error)
      return false
    }
  },

  // Method to test connectivity
  testConnection: async (): Promise<{ connected: boolean; latency?: number; error?: string }> => {
    const startTime = Date.now()
    try {
      await api.healthCheck()
      const latency = Date.now() - startTime
      return { connected: true, latency }
    } catch (error) {
      return { 
        connected: false, 
        error: error instanceof Error ? error.message : 'Unknown error' 
      }
    }
  }
}

// Export the enhanced axios instance
export default apiClient

// Export utility functions for external use
export { 
  transformError, 
  calculateRetryDelay, 
  defaultRetryConfig,
  type RetryConfig 
}
/**

 * Type-safe response data extractor
 * Extracts the data from an API response with proper typing
 * 
 * @param response - Axios response with APIResponse wrapper
 * @returns The unwrapped data with proper type
 * 
 * @example
 * const response = await api.get<User>('/users/123/')
 * const user = extractData(response) // Type: User
 */
export function extractData<T>(response: AxiosResponse<APIResponse<T>>): T {
  return response.data.data
}

/**
 * Type-safe paginated response data extractor
 * Extracts the results array from a paginated API response
 * 
 * @param response - Axios response with paginated data
 * @returns The results array with proper typing
 * 
 * @example
 * const response = await api.get<PaginatedResponse<User>>('/users/')
 * const users = extractPaginatedData(response) // Type: User[]
 */
export function extractPaginatedData<T>(response: AxiosResponse<APIResponse<PaginatedResponse<T>>>): T[] {
  return response.data.data.results
}

/**
 * Type-safe error checker
 * Checks if a response is an error response
 * 
 * @param response - Any API response
 * @returns True if the response is an error
 */
export function isErrorResponse(response: unknown): response is ErrorResponse {
  return (
    typeof response === 'object' &&
    response !== null &&
    'error' in response &&
    'success' in response &&
    (response as ErrorResponse).success === false
  )
}

/**
 * Type guard for API errors
 * Checks if an error is an ApiError
 * 
 * @param error - Any error object
 * @returns True if the error is an ApiError
 */
export function isAPIError(error: unknown): error is ApiError {
  return (
    typeof error === 'object' &&
    error !== null &&
    'message' in error &&
    'status' in error
  )
}

/**
 * Format API error for display
 * Converts an API error to a user-friendly message
 * 
 * @param error - API error object
 * @returns Formatted error message
 */
export function formatAPIError(error: ApiError): string {
  if (error.errors) {
    // Format validation errors
    const errorMessages = Object.entries(error.errors)
      .map(([field, messages]: [string, string[]]) => `${field}: ${messages.join(', ')}`)
      .join('; ')
    return errorMessages || error.message
  }
  return error.detail || error.message
}
