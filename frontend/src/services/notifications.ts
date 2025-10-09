import { api } from './api'
import type { Notification, PaginatedResponse } from '../types/api'

export class NotificationService {
  // Notification CRUD operations
  static async getNotifications(): Promise<PaginatedResponse<Notification>> {
    const response = await api.get<PaginatedResponse<Notification>>('/notifications/notifications/')
    return response.data
  }

  static async getUnreadNotifications(): Promise<PaginatedResponse<Notification>> {
    const response = await api.get<PaginatedResponse<Notification>>('/notifications/notifications/', {
      params: { is_read: false }
    })
    return response.data
  }

  static async markAsRead(id: string): Promise<Notification> {
    const response = await api.patch<Notification>(`/notifications/notifications/${id}/`, {
      is_read: true
    })
    return response.data
  }

  static async markAllAsRead(): Promise<void> {
    await api.post('/notifications/notifications/mark_all_read/')
  }

  static async deleteNotification(id: string): Promise<void> {
    await api.delete(`/notifications/notifications/${id}/`)
  }

  static async clearAllNotifications(): Promise<void> {
    await api.post('/notifications/notifications/clear_all/')
  }

  // Notification preferences
  static async getNotificationPreferences(): Promise<{
    email_notifications: boolean
    push_notifications: boolean
    course_updates: boolean
    assignment_reminders: boolean
    marketing_emails: boolean
    live_class_reminders: boolean
  }> {
    const response = await api.get('/notifications/preferences/')
    return response.data
  }

  static async updateNotificationPreferences(preferences: {
    email_notifications?: boolean
    push_notifications?: boolean
    course_updates?: boolean
    assignment_reminders?: boolean
    marketing_emails?: boolean
    live_class_reminders?: boolean
  }): Promise<any> {
    const response = await api.patch('/notifications/preferences/', preferences)
    return response.data
  }

  // Real-time notifications (WebSocket)
  static connectWebSocket(): WebSocket | null {
    const token = localStorage.getItem('access_token')
    if (!token) return null

    const wsUrl = `ws://localhost:8000/ws/notifications/?token=${token}`
    const ws = new WebSocket(wsUrl)

    ws.onopen = () => {
      console.log('Notification WebSocket connected')
    }

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      this.handleRealtimeNotification(data)
    }

    ws.onclose = () => {
      console.log('Notification WebSocket disconnected')
      // Attempt to reconnect after 5 seconds
      setTimeout(() => {
        this.connectWebSocket()
      }, 5000)
    }

    ws.onerror = (error) => {
      console.error('Notification WebSocket error:', error)
    }

    return ws
  }

  private static handleRealtimeNotification(data: any): void {
    // Handle real-time notification
    // This could trigger UI updates, show toast notifications, etc.
    
    // Example: Show browser notification if permission granted
    if (Notification.permission === 'granted') {
      new Notification(data.title, {
        body: data.message,
        icon: '/favicon.ico'
      })
    }

    // Dispatch custom event for components to listen to
    window.dispatchEvent(new CustomEvent('newNotification', { detail: data }))
  }

  // Browser notifications
  static async requestNotificationPermission(): Promise<NotificationPermission> {
    if (!('Notification' in window)) {
      console.log('This browser does not support notifications')
      return 'denied'
    }

    if (Notification.permission === 'granted') {
      return 'granted'
    }

    if (Notification.permission !== 'denied') {
      const permission = await Notification.requestPermission()
      return permission
    }

    return Notification.permission
  }

  static showBrowserNotification(title: string, options?: NotificationOptions): void {
    if (Notification.permission === 'granted') {
      new Notification(title, {
        icon: '/favicon.ico',
        ...options
      })
    }
  }

  // Push notifications (Service Worker)
  static async subscribeToPushNotifications(): Promise<PushSubscription | null> {
    if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
      console.log('Push notifications not supported')
      return null
    }

    try {
      const registration = await navigator.serviceWorker.register('/sw.js')
      const subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: this.urlBase64ToUint8Array(
          process.env.VITE_VAPID_PUBLIC_KEY || ''
        )
      })

      // Send subscription to backend
      await api.post('/notifications/push_subscription/', {
        subscription: subscription.toJSON()
      })

      return subscription
    } catch (error) {
      console.error('Error subscribing to push notifications:', error)
      return null
    }
  }

  static async unsubscribeFromPushNotifications(): Promise<void> {
    if (!('serviceWorker' in navigator)) return

    try {
      const registration = await navigator.serviceWorker.getRegistration()
      if (registration) {
        const subscription = await registration.pushManager.getSubscription()
        if (subscription) {
          await subscription.unsubscribe()
          
          // Remove subscription from backend
          await api.delete('/notifications/push_subscription/', {
            data: { subscription: subscription.toJSON() }
          })
        }
      }
    } catch (error) {
      console.error('Error unsubscribing from push notifications:', error)
    }
  }

  private static urlBase64ToUint8Array(base64String: string): BufferSource {
    const padding = '='.repeat((4 - base64String.length % 4) % 4)
    const base64 = (base64String + padding)
      .replace(/-/g, '+')
      .replace(/_/g, '/')

    const rawData = window.atob(base64)
    const outputArray = new Uint8Array(rawData.length)

    for (let i = 0; i < rawData.length; ++i) {
      outputArray[i] = rawData.charCodeAt(i)
    }
    return outputArray
  }

  // Notification templates
  static createCourseUpdateNotification(courseTitle: string): Partial<Notification> {
    return {
      title: 'Course Updated',
      message: `New content available in "${courseTitle}"`,
      type: 'info'
    }
  }

  static createAssignmentReminderNotification(assignmentTitle: string, dueDate: Date): Partial<Notification> {
    const timeUntilDue = Math.ceil((dueDate.getTime() - Date.now()) / (1000 * 60 * 60 * 24))
    return {
      title: 'Assignment Due Soon',
      message: `"${assignmentTitle}" is due in ${timeUntilDue} day(s)`,
      type: 'warning'
    }
  }

  static createLiveClassReminderNotification(classTitle: string, startTime: Date): Partial<Notification> {
    return {
      title: 'Live Class Starting Soon',
      message: `"${classTitle}" starts at ${startTime.toLocaleTimeString()}`,
      type: 'info'
    }
  }

  // Utility methods
  static getNotificationIcon(type: string): string {
    const icons = {
      info: 'ℹ️',
      success: '✅',
      warning: '⚠️',
      error: '❌'
    }
    return icons[type as keyof typeof icons] || 'ℹ️'
  }

  static getNotificationColor(type: string): string {
    const colors = {
      info: 'text-blue-600 bg-blue-100',
      success: 'text-green-600 bg-green-100',
      warning: 'text-yellow-600 bg-yellow-100',
      error: 'text-red-600 bg-red-100'
    }
    return colors[type as keyof typeof colors] || 'text-gray-600 bg-gray-100'
  }

  static formatNotificationTime(timestamp: string): string {
    const date = new Date(timestamp)
    const now = new Date()
    const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60))

    if (diffInMinutes < 1) return 'Just now'
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}h ago`
    if (diffInMinutes < 10080) return `${Math.floor(diffInMinutes / 1440)}d ago`
    
    return date.toLocaleDateString()
  }
}