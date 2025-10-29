import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/services/api'

interface Notification {
  id: string
  type: string
  title: string
  message: string
  data?: any
  is_read: boolean
  created_at: string
  priority: 'low' | 'normal' | 'high' | 'urgent'
  category: string
}

interface NotificationPreferences {
  sound_enabled: boolean
  browser_notifications: boolean
  email_notifications: boolean
  quiet_hours_enabled: boolean
  quiet_hours_start: string
  quiet_hours_end: string
  categories: Record<string, boolean>
}

// Remove unused interface - using the one from types/api instead

export const useNotificationStore = defineStore('notifications', () => {
  // State
  const notifications = ref<Notification[]>([])
  const unreadCount = ref(0)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const nextPage = ref<string | null>(null)
  const preferences = ref<NotificationPreferences>({
    sound_enabled: true,
    browser_notifications: true,
    email_notifications: true,
    quiet_hours_enabled: false,
    quiet_hours_start: '22:00',
    quiet_hours_end: '08:00',
    categories: {
      assignment: true,
      grade: true,
      live_class: true,
      course: true,
      system: true,
      announcement: true,
      reminder: true
    }
  })

  // Computed
  const hasMore = computed(() => nextPage.value !== null)
  const unreadNotifications = computed(() =>
    notifications.value.filter(n => !n.is_read)
  )

  // Actions
  const fetchNotifications = async (page = 1, pageSize = 20) => {
    loading.value = true
    error.value = null

    try {
      const response = await api.get('/notifications/', {
        params: { page, page_size: pageSize }
      })

      // Handle different response structures
      let notificationData = []
      if (response.data && typeof response.data === 'object') {
        if (Array.isArray(response.data)) {
          notificationData = response.data
        } else if ((response.data as any).results && Array.isArray((response.data as any).results)) {
          notificationData = (response.data as any).results
        } else if (response.data.data && Array.isArray(response.data.data)) {
          notificationData = response.data.data
        } else {
          console.warn('Unexpected notification data structure:', response.data)
          notificationData = []
        }
      }

      if (page === 1) {
        notifications.value = notificationData
      } else {
        notifications.value.push(...notificationData)
      }

      nextPage.value = (response.data as any).next || null

      // Update unread count
      unreadCount.value = notifications.value.filter(n => !n.is_read).length

    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to fetch notifications'
      console.error('Error fetching notifications:', err)
      // Ensure notifications is always an array
      notifications.value = []
    } finally {
      loading.value = false
    }
  }

  const fetchMoreNotifications = async () => {
    if (!hasMore.value || loading.value) return

    const url = new URL(nextPage.value!)
    const page = url.searchParams.get('page')

    if (page) {
      await fetchNotifications(parseInt(page))
    }
  }

  const markAsRead = async (notificationId: string) => {
    try {
      await api.post(`/notifications/${notificationId}/mark_read/`, {
        is_read: true
      })

      // Update local state
      const notification = notifications.value.find(n => n.id === notificationId)
      if (notification && !notification.is_read) {
        notification.is_read = true
        unreadCount.value = Math.max(0, unreadCount.value - 1)
      }

    } catch (err: any) {
      console.error('Error marking notification as read:', err)
      throw new Error(err.response?.data?.message || 'Failed to mark notification as read')
    }
  }

  const markAllAsRead = async () => {
    try {
      await api.post('/notifications/mark_all_read/')

      // Update local state
      notifications.value.forEach(notification => {
        notification.is_read = true
      })
      unreadCount.value = 0

    } catch (err: any) {
      console.error('Error marking all notifications as read:', err)
      throw new Error(err.response?.data?.message || 'Failed to mark all notifications as read')
    }
  }

  const deleteNotification = async (notificationId: string) => {
    try {
      await api.delete(`/notifications/${notificationId}/`)

      // Update local state
      const index = notifications.value.findIndex(n => n.id === notificationId)
      if (index > -1) {
        const notification = notifications.value[index]
        if (!notification.is_read) {
          unreadCount.value = Math.max(0, unreadCount.value - 1)
        }
        notifications.value.splice(index, 1)
      }

    } catch (err: any) {
      console.error('Error deleting notification:', err)
      throw new Error(err.response?.data?.message || 'Failed to delete notification')
    }
  }

  const addNotification = (notification: Notification) => {
    // Add to the beginning of the list
    notifications.value.unshift(notification)

    // Update unread count if notification is unread
    if (!notification.is_read) {
      unreadCount.value++
    }

    // Limit the number of notifications in memory
    if (notifications.value.length > 100) {
      notifications.value = notifications.value.slice(0, 100)
    }
  }

  const setUnreadCount = (count: number) => {
    unreadCount.value = count
  }

  const fetchPreferences = async () => {
    try {
      const response = await api.get('/notifications/preferences/')
      preferences.value = { ...preferences.value, ...response.data }
    } catch (err: any) {
      console.warn('Notification preferences not available, using defaults:', err)
      // Use default preferences if API fails
      preferences.value = {
        sound_enabled: true,
        browser_notifications: true,
        email_notifications: true,
        quiet_hours_enabled: false,
        quiet_hours_start: '22:00',
        quiet_hours_end: '08:00',
        categories: {
          assignment: true,
          grade: true,
          live_class: true,
          course: true,
          system: true,
          announcement: true,
          reminder: true
        }
      }
    }
  }

  const updatePreferences = async (newPreferences: NotificationPreferences) => {
    try {
      const response = await api.put('/notifications/preferences/', newPreferences)
      preferences.value = (response.data as any).data || response.data

      // Request browser notification permission if enabled
      if (newPreferences.browser_notifications && 'Notification' in window) {
        if (Notification.permission === 'default') {
          await Notification.requestPermission()
        }
      }

    } catch (err: any) {
      console.error('Error updating notification preferences:', err)
      throw new Error(err.response?.data?.message || 'Failed to update preferences')
    }
  }

  const isInQuietHours = (): boolean => {
    if (!preferences.value.quiet_hours_enabled) return false

    const now = new Date()
    const currentTime = now.getHours() * 60 + now.getMinutes()

    const [startHour, startMinute] = preferences.value.quiet_hours_start.split(':').map(Number)
    const [endHour, endMinute] = preferences.value.quiet_hours_end.split(':').map(Number)

    const startTime = startHour * 60 + startMinute
    const endTime = endHour * 60 + endMinute

    if (startTime <= endTime) {
      // Same day range (e.g., 9:00 to 17:00)
      return currentTime >= startTime && currentTime <= endTime
    } else {
      // Overnight range (e.g., 22:00 to 08:00)
      return currentTime >= startTime || currentTime <= endTime
    }
  }

  const shouldShowNotification = (notification: Notification): boolean => {
    // Check if category is enabled
    if (!preferences.value.categories[notification.category]) {
      return false
    }

    // Check quiet hours
    if (isInQuietHours()) {
      // Only show urgent notifications during quiet hours
      return notification.priority === 'urgent'
    }

    return true
  }

  const getNotificationsByCategory = (category: string) => {
    return notifications.value.filter(n => n.category === category)
  }

  const getNotificationsByPriority = (priority: string) => {
    return notifications.value.filter(n => n.priority === priority)
  }

  const clearAll = () => {
    notifications.value = []
    unreadCount.value = 0
    nextPage.value = null
    error.value = null
  }

  return {
    // State
    notifications,
    unreadCount,
    loading,
    error,
    preferences,

    // Computed
    hasMore,
    unreadNotifications,

    // Actions
    fetchNotifications,
    fetchMoreNotifications,
    markAsRead,
    markAllAsRead,
    deleteNotification,
    addNotification,
    setUnreadCount,
    fetchPreferences,
    updatePreferences,
    isInQuietHours,
    shouldShowNotification,
    getNotificationsByCategory,
    getNotificationsByPriority,
    clearAll
  }
})