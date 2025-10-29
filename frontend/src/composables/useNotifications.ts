import { ref, computed, onMounted, onUnmounted } from 'vue'
import { NotificationService } from '@/services/notifications'
import { useToast } from '@/composables/useToast'
import { notificationSoundService } from '@/utils/notificationSound'
import { showNotificationToast } from '@/utils/toast'
import type { Notification } from '@/types/api'

export const useNotifications = () => {
  const toast = useToast()
  
  // State
  const notifications = ref<Notification[]>([])
  const unreadCount = ref(0)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const websocket = ref<WebSocket | null>(null)
  
  // Computed
  const unreadNotifications = computed(() => 
    notifications.value.filter(n => !n.is_read)
  )
  
  const readNotifications = computed(() => 
    notifications.value.filter(n => n.is_read)
  )
  
  const notificationsByType = computed(() => {
    const grouped: Record<string, Notification[]> = {}
    notifications.value.forEach(notification => {
      if (!grouped[notification.notification_type]) {
        grouped[notification.notification_type] = []
      }
      grouped[notification.notification_type].push(notification)
    })
    return grouped
  })
  
  // Methods
  const fetchNotifications = async (params?: {
    page?: number
    page_size?: number
    type?: string
    is_read?: boolean
  }) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await NotificationService.getNotifications(params)
      notifications.value = response.results
      return response
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch notifications'
      toast.error('Failed to load notifications')
      throw err
    } finally {
      loading.value = false
    }
  }
  
  const fetchUnreadCount = async () => {
    try {
      const response = await NotificationService.getUnreadCount()
      unreadCount.value = response.unread_count
      return response.unread_count
    } catch (err) {
      console.error('Failed to fetch unread count:', err)
      return 0
    }
  }
  
  const markAsRead = async (notificationId: string) => {
    try {
      const updatedNotification = await NotificationService.markAsRead(notificationId)
      
      // Update local state
      const index = notifications.value.findIndex(n => n.id === notificationId)
      if (index !== -1) {
        notifications.value[index] = updatedNotification
        unreadCount.value = Math.max(0, unreadCount.value - 1)
      }
      
      return updatedNotification
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to mark notification as read'
      toast.error('Failed to mark notification as read')
      throw err
    }
  }
  
  const markAllAsRead = async () => {
    try {
      const response = await NotificationService.markAllAsRead()
      
      // Update local state
      notifications.value = notifications.value.map(n => ({ ...n, is_read: true }))
      unreadCount.value = 0
      
      toast.success(`${response.marked_count} notifications marked as read`)
      return response
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to mark all notifications as read'
      toast.error('Failed to mark all notifications as read')
      throw err
    }
  }
  
  const deleteNotification = async (notificationId: string) => {
    try {
      await NotificationService.deleteNotification(notificationId)
      
      // Update local state
      const notification = notifications.value.find(n => n.id === notificationId)
      notifications.value = notifications.value.filter(n => n.id !== notificationId)
      
      if (notification && !notification.is_read) {
        unreadCount.value = Math.max(0, unreadCount.value - 1)
      }
      
      toast.success('Notification deleted')
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to delete notification'
      toast.error('Failed to delete notification')
      throw err
    }
  }
  
  const clearReadNotifications = async () => {
    try {
      const response = await NotificationService.clearReadNotifications()
      
      // Update local state
      notifications.value = notifications.value.filter(n => !n.is_read)
      
      toast.success(`${response.deleted_count} read notifications cleared`)
      return response
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to clear read notifications'
      toast.error('Failed to clear read notifications')
      throw err
    }
  }
  
  const getNotificationStats = async () => {
    try {
      const stats = await NotificationService.getNotificationStats()
      return stats
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch notification statistics'
      throw err
    }
  }
  
  // WebSocket connection
  const connectWebSocket = () => {
    if (websocket.value) {
      websocket.value.close()
    }
    
    websocket.value = NotificationService.connectWebSocket()
    
    if (websocket.value) {
      // Listen for new notifications
      window.addEventListener('newNotification', handleNewNotification as EventListener)
    }
  }
  
  const disconnectWebSocket = () => {
    if (websocket.value) {
      websocket.value.close()
      websocket.value = null
    }
    
    window.removeEventListener('newNotification', handleNewNotification as EventListener)
  }
  
  const handleNewNotification = (event: CustomEvent) => {
    const notification = event.detail
    
    // Add to local state
    notifications.value.unshift(notification)
    unreadCount.value += 1
    
    // Play notification sound based on priority
    if (notification.priority === 'urgent') {
      notificationSoundService.playUrgentNotification()
    } else {
      notificationSoundService.playNotificationBeep()
    }
    
    // Show toast notification with enhanced styling
    showNotificationToast(notification)
    
    // Show browser notification if permission granted
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification(notification.title, {
        body: notification.message,
        icon: '/favicon.ico',
        tag: notification.id,
        requireInteraction: notification.priority === 'urgent'
      })
    }
  }
  
  // Request notification permissions
  const requestNotificationPermission = async () => {
    if ('Notification' in window) {
      if (Notification.permission === 'default') {
        const permission = await Notification.requestPermission()
        return permission === 'granted'
      }
      return Notification.permission === 'granted'
    }
    return false
  }

  // Lifecycle
  onMounted(() => {
    fetchNotifications()
    fetchUnreadCount()
    connectWebSocket()
    requestNotificationPermission()
  })
  
  onUnmounted(() => {
    disconnectWebSocket()
  })
  
  return {
    // State
    notifications,
    unreadCount,
    loading,
    error,
    
    // Computed
    unreadNotifications,
    readNotifications,
    notificationsByType,
    
    // Methods
    fetchNotifications,
    fetchUnreadCount,
    markAsRead,
    markAllAsRead,
    deleteNotification,
    clearReadNotifications,
    getNotificationStats,
    connectWebSocket,
    disconnectWebSocket,
    requestNotificationPermission,
    
    // Refresh method
    refresh: () => {
      fetchNotifications()
      fetchUnreadCount()
    }
  }
}

// Notification preferences composable
export const useNotificationPreferences = () => {
  const preferences = ref({
    email_notifications: true,
    push_notifications: true,
    course_enrollment_notifications: true,
    class_reminder_notifications: true,
    assignment_due_notifications: true,
    payment_notifications: true,
    system_notifications: true,
  })
  
  const loading = ref(false)
  const error = ref<string | null>(null)
  const toast = useToast()
  
  const fetchPreferences = async () => {
    loading.value = true
    error.value = null
    
    try {
      const response = await NotificationService.getNotificationPreferences()
      preferences.value = response
      return response
    } catch (err) {
      // Set default preferences if API fails
      preferences.value = {
        email_notifications: true,
        push_notifications: true,
        course_enrollment_notifications: true,
        class_reminder_notifications: true,
        assignment_due_notifications: true,
        payment_notifications: true,
        system_notifications: true,
      }
      console.warn('Failed to load notification preferences, using defaults:', err)
      return preferences.value
    } finally {
      loading.value = false
    }
  }
  
  const updatePreferences = async (newPreferences: Partial<typeof preferences.value>) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await NotificationService.updateNotificationPreferences(newPreferences)
      preferences.value = { ...preferences.value, ...response }
      toast.success('Notification preferences updated')
      return response
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to update preferences'
      toast.error('Failed to update notification preferences')
      throw err
    } finally {
      loading.value = false
    }
  }
  
  onMounted(() => {
    fetchPreferences()
  })
  
  return {
    preferences,
    loading,
    error,
    fetchPreferences,
    updatePreferences
  }
}