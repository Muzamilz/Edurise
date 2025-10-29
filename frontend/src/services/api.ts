import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios'

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
const API_BASE_URL = (globalThis as any)?.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

// Error types for better error handling
export interface APIError {
  message: string
  code?: string
  status?: number
  errors?: Record<string, string[]>
  timestamp?: string
}

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
    if ((globalThis as any)?.DEV || process.env.NODE_ENV === 'development') {
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
    if (((globalThis as any)?.DEV || process.env.NODE_ENV === 'development') && response.config.metadata) {
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
    if ((globalThis as any)?.DEV || process.env.NODE_ENV === 'development') {
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
const transformError = (error: AxiosError): APIError => {
  if (error.response) {
    // Server responded with error status
    const responseData = error.response.data as any
    return {
      message: responseData?.message || responseData?.detail || `HTTP ${error.response.status} Error`,
      code: responseData?.code || `HTTP_${error.response.status}`,
      status: error.response.status,
      errors: responseData?.errors,
      timestamp: responseData?.timestamp || new Date().toISOString()
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
      code: 'REQUEST_ERROR'
    }
  }
}

// API Response types
export interface ApiResponse<T = any> {
  success: boolean
  data: T
  message?: string
  timestamp?: string
  meta?: {
    pagination?: {
      page: number
      total_pages: number
      count: number
      next: string | null
      previous: string | null
    }
  }
}

export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

// Enhanced API methods with better error handling
export const api = {
  get: <T = any>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<ApiResponse<T>>> =>
    apiClient.get(url, config),
    
  post: <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<ApiResponse<T>>> =>
    apiClient.post(url, data, config),
    
  put: <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<ApiResponse<T>>> =>
    apiClient.put(url, data, config),
    
  patch: <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<ApiResponse<T>>> =>
    apiClient.patch(url, data, config),
    
  delete: <T = any>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<ApiResponse<T>>> =>
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