import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import type { APIError } from '@/services/api'

// Error types and interfaces
export interface AppError {
  id: string
  type: 'api' | 'validation' | 'network' | 'auth' | 'permission' | 'system'
  message: string
  code?: string
  status?: number
  timestamp: Date
  context?: Record<string, any>
  retryable?: boolean
  userFriendly?: boolean
}

export interface ErrorHandlerOptions {
  showToast?: boolean
  logError?: boolean
  retryable?: boolean
  context?: Record<string, any>
}

// Error store for global error state management
export const useErrorStore = defineStore('error', () => {
  const errors = ref<AppError[]>([])
  const maxErrors = 50 // Maximum number of errors to keep

  // Add error to store
  const addError = (error: AppError) => {
    errors.value.unshift(error)
    
    // Keep only the most recent errors
    if (errors.value.length > maxErrors) {
      errors.value = errors.value.slice(0, maxErrors)
    }
  }

  // Remove error by ID
  const removeError = (id: string) => {
    const index = errors.value.findIndex(error => error.id === id)
    if (index > -1) {
      errors.value.splice(index, 1)
    }
  }

  // Clear all errors
  const clearErrors = () => {
    errors.value = []
  }

  // Clear errors by type
  const clearErrorsByType = (type: AppError['type']) => {
    errors.value = errors.value.filter(error => error.type !== type)
  }

  // Get errors by type
  const getErrorsByType = (type: AppError['type']) => {
    return errors.value.filter(error => error.type === type)
  }

  // Computed properties
  const hasErrors = computed(() => errors.value.length > 0)
  const criticalErrors = computed(() => 
    errors.value.filter(error => 
      error.type === 'system' || 
      error.type === 'auth' || 
      (error.status && error.status >= 500)
    )
  )
  const userFriendlyErrors = computed(() => 
    errors.value.filter(error => error.userFriendly !== false)
  )

  return {
    errors: computed(() => errors.value),
    hasErrors,
    criticalErrors,
    userFriendlyErrors,
    addError,
    removeError,
    clearErrors,
    clearErrorsByType,
    getErrorsByType
  }
})

// Main error handler composable
export const useErrorHandler = () => {
  const errorStore = useErrorStore()

  // Generate unique error ID
  const generateErrorId = () => `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`

  // Transform API error to app error
  const transformApiError = (apiError: APIError, context?: Record<string, any>): AppError => {
    let type: AppError['type'] = 'api'
    let userFriendly = true
    let retryable = false

    // Determine error type based on status code
    if (apiError.status === 0) {
      type = 'network'
      retryable = true
    } else if (apiError.status === 401) {
      type = 'auth'
      userFriendly = false // Auth errors are handled by auth system
    } else if (apiError.status === 403) {
      type = 'permission'
    } else if (apiError.status && apiError.status >= 400 && apiError.status < 500) {
      type = 'validation'
    } else if (apiError.status && apiError.status >= 500) {
      type = 'system'
      retryable = true
    }

    return {
      id: generateErrorId(),
      type,
      message: getUserFriendlyMessage(apiError),
      code: apiError.code,
      status: apiError.status,
      timestamp: new Date(),
      context,
      retryable,
      userFriendly
    }
  }

  // Get user-friendly error message
  const getUserFriendlyMessage = (apiError: APIError): string => {
    // Check for specific error codes first
    if (apiError.code) {
      const friendlyMessages: Record<string, string> = {
        'VALIDATION_ERROR': 'Please check your input and try again.',
        'PERMISSION_DENIED': 'You don\'t have permission to perform this action.',
        'NOT_FOUND': 'The requested resource was not found.',
        'RATE_LIMIT_EXCEEDED': 'Too many requests. Please wait a moment and try again.',
        'NETWORK_ERROR': 'Connection problem. Please check your internet connection.',
        'SERVER_ERROR': 'Server error. Please try again later.',
        'TENANT_ACCESS_ERROR': 'Access denied for this organization.',
        'BAD_REQUEST': 'Invalid request. Please check your input and try again.',
        'CONFLICT': 'This action conflicts with existing data. Please refresh and try again.',
        'UNAUTHORIZED': 'Authentication required. Please log in again.',
        'ENROLLMENT_ERROR': 'Unable to enroll in course. Please try again.',
        'PAYMENT_ERROR': 'Payment processing failed. Please check your payment details.',
        'COURSE_ACCESS_ERROR': 'You don\'t have access to this course.',
        'LIVE_CLASS_ERROR': 'Unable to join live class. Please try again.',
        'FILE_UPLOAD_ERROR': 'File upload failed. Please check file size and format.'
      }

      if (friendlyMessages[apiError.code]) {
        return friendlyMessages[apiError.code]
      }
    }

    // Fallback to status-based messages
    if (apiError.status) {
      if (apiError.status === 0) {
        return 'Connection problem. Please check your internet connection.'
      } else if (apiError.status === 400) {
        return 'Invalid request. Please check your input.'
      } else if (apiError.status === 401) {
        return 'Authentication required. Please log in.'
      } else if (apiError.status === 403) {
        return 'You don\'t have permission to access this resource.'
      } else if (apiError.status === 404) {
        return 'The requested resource was not found.'
      } else if (apiError.status === 429) {
        return 'Too many requests. Please wait a moment and try again.'
      } else if (apiError.status >= 500) {
        return 'Server error. Please try again later.'
      }
    }

    // Use the original message if available, otherwise generic message
    return apiError.message || 'An unexpected error occurred. Please try again.'
  }

  // Handle API errors
  const handleApiError = (
    apiError: APIError, 
    options: ErrorHandlerOptions = {}
  ): AppError => {
    const {
      showToast = true,
      logError = true,
      context
    } = options

    const appError = transformApiError(apiError, context)

    // Add to error store
    errorStore.addError(appError)

    // Log error in development or if explicitly requested
    if (logError && (import.meta.env.DEV || import.meta.env.VITE_DEBUG)) {
      console.group(`🚨 Error [${appError.id}]`)
      console.error('Type:', appError.type)
      console.error('Message:', appError.message)
      console.error('Code:', appError.code)
      console.error('Status:', appError.status)
      console.error('Context:', appError.context)
      console.error('Original Error:', apiError)
      console.groupEnd()
    }

    // Show toast notification if requested and error is user-friendly
    if (showToast && appError.userFriendly) {
      showErrorToast(appError)
    }

    // Send to monitoring service in production
    if (import.meta.env.PROD) {
      sendToMonitoring(appError, apiError)
    }

    return appError
  }

  // Handle validation errors
  const handleValidationErrors = (
    errors: Record<string, string[]>,
    options: ErrorHandlerOptions = {}
  ): AppError[] => {
    const appErrors: AppError[] = []

    Object.entries(errors).forEach(([field, messages]) => {
      messages.forEach(message => {
        const appError: AppError = {
          id: generateErrorId(),
          type: 'validation',
          message: `${field}: ${message}`,
          timestamp: new Date(),
          context: { field, ...options.context },
          retryable: false,
          userFriendly: true
        }

        appErrors.push(appError)
        errorStore.addError(appError)

        if (options.showToast !== false) {
          showErrorToast(appError)
        }
      })
    })

    return appErrors
  }

  // Handle generic errors
  const handleError = (
    error: Error | string,
    type: AppError['type'] = 'system',
    options: ErrorHandlerOptions = {}
  ): AppError => {
    const message = typeof error === 'string' ? error : error.message
    
    const appError: AppError = {
      id: generateErrorId(),
      type,
      message,
      timestamp: new Date(),
      context: options.context,
      retryable: options.retryable || false,
      userFriendly: true
    }

    errorStore.addError(appError)

    if (options.logError !== false) {
      console.error(`Error [${appError.id}]:`, error)
    }

    if (options.showToast !== false) {
      showErrorToast(appError)
    }

    return appError
  }

  // Show error toast (placeholder - would integrate with actual toast system)
  const showErrorToast = (error: AppError) => {
    // This would integrate with your toast notification system
    console.log(`🍞 Toast: ${error.message}`)
    
    // Example integration with a toast library:
    // toast.error(error.message, {
    //   id: error.id,
    //   duration: error.type === 'network' ? 5000 : 4000,
    //   action: error.retryable ? {
    //     label: 'Retry',
    //     onClick: () => handleRetry(error)
    //   } : undefined
    // })
  }

  // Send error to monitoring service
  const sendToMonitoring = (appError: AppError, _originalError?: any) => {
    // This would integrate with your monitoring service (Sentry, LogRocket, etc.)
    console.log('📊 Sending to monitoring:', appError)
    
    // Example integration:
    // Sentry.captureException(originalError || new Error(appError.message), {
    //   tags: {
    //     errorType: appError.type,
    //     errorCode: appError.code
    //   },
    //   extra: {
    //     errorId: appError.id,
    //     context: appError.context
    //   }
    // })
  }

  // Retry error handler (unused for now)
  // const handleRetry = (_error: AppError) => {
  //   console.log(`🔄 Retrying error: ${_error.id}`)
  //   // This would trigger the retry logic for the failed operation
  //   // The specific retry implementation would depend on the context
  // }

  // Clear error by ID
  const clearError = (errorId: string) => {
    errorStore.removeError(errorId)
  }

  // Check if error is retryable
  const isRetryable = (error: AppError): boolean => {
    return !!(error.retryable || error.type === 'network' || (error.status && error.status >= 500))
  }

  return {
    // Error handling methods
    handleApiError,
    handleValidationErrors,
    handleError,
    clearError,
    
    // Utility methods
    isRetryable,
    getUserFriendlyMessage,
    
    // Store access
    errors: errorStore.errors,
    hasErrors: errorStore.hasErrors,
    criticalErrors: errorStore.criticalErrors,
    userFriendlyErrors: errorStore.userFriendlyErrors,
    
    // Store methods
    clearAllErrors: errorStore.clearErrors,
    clearErrorsByType: errorStore.clearErrorsByType,
    getErrorsByType: errorStore.getErrorsByType
  }
}

// Global error handler for unhandled promise rejections and errors
export const setupGlobalErrorHandler = () => {
  const { handleError, handleApiError } = useErrorHandler()

  // Handle unhandled promise rejections
  window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason)
    
    // Check if it's an API error
    if (event.reason && typeof event.reason === 'object' && 'status' in event.reason) {
      handleApiError(event.reason as APIError, {
        context: { source: 'unhandledrejection' }
      })
    } else {
      handleError(
        event.reason instanceof Error ? event.reason : new Error(String(event.reason)),
        'system',
        { context: { source: 'unhandledrejection' } }
      )
    }
    
    // Prevent the default browser error handling
    event.preventDefault()
  })

  // Handle uncaught errors
  window.addEventListener('error', (event) => {
    console.error('Uncaught error:', event.error)
    
    handleError(
      event.error || new Error(event.message),
      'system',
      { 
        context: { 
          source: 'uncaught',
          filename: event.filename,
          lineno: event.lineno,
          colno: event.colno
        } 
      }
    )
  })

  console.log('🛡️ Global error handler setup complete')
}