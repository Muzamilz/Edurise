/**
 * Toast Notification Utility
 * Provides a simple API for showing toast notifications
 */

interface ToastOptions {
  type?: 'success' | 'error' | 'warning' | 'info'
  title?: string
  duration?: number
  dismissible?: boolean
}

export const showToast = (message: string, options: ToastOptions = {}) => {
  const event = new CustomEvent('show-toast', {
    detail: {
      type: 'info',
      duration: 5000,
      dismissible: true,
      ...options,
      message
    }
  })
  
  window.dispatchEvent(event)
}

// Convenience methods
export const showSuccessToast = (message: string, title?: string) => {
  showToast(message, { type: 'success', title })
}

export const showErrorToast = (message: string, title?: string) => {
  showToast(message, { type: 'error', title, duration: 7000 })
}

export const showWarningToast = (message: string, title?: string) => {
  showToast(message, { type: 'warning', title })
}

export const showInfoToast = (message: string, title?: string) => {
  showToast(message, { type: 'info', title })
}

// Enhanced notification toast for notification-specific messages
export const showNotificationToast = (notification: {
  title: string
  message: string
  priority?: 'low' | 'normal' | 'high' | 'urgent'
}) => {
  const type = notification.priority === 'urgent' ? 'error' : 
               notification.priority === 'high' ? 'warning' : 'info'
  
  showToast(notification.message, {
    type,
    title: notification.title,
    duration: notification.priority === 'urgent' ? 8000 : 5000
  })
}