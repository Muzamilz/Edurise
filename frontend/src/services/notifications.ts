import { api } from './api'
import type { 
  Notification, 
  PaginatedResponse, 
  APIResponse, 
  EmailDeliveryLog, 
  NotificationTemplate, 
  EmailTemplate, 
  ChatMessage, 
  WebSocketConnection 
} from '../types/api'

export class NotificationService {
  // Notification CRUD operations through centralized API
  static async getNotifications(params?: {
    page?: number
    page_size?: number
    type?: string
    is_read?: boolean
  }): Promise<PaginatedResponse<Notification>> {
    const response = await api.get<APIResponse<PaginatedResponse<Notification>>>('/api/v1/notifications/', {
      params
    })
    return (response.data.data || response.data) as PaginatedResponse<Notification>
  }

  static async getUnreadNotifications(): Promise<PaginatedResponse<Notification>> {
    const response = await api.get<APIResponse<PaginatedResponse<Notification>>>('/api/v1/notifications/', {
      params: { is_read: false }
    })
    return (response.data.data || response.data) as PaginatedResponse<Notification>
  }

  static async getNotificationById(id: string): Promise<Notification> {
    const response = await api.get<APIResponse<Notification>>(`/api/v1/notifications/${id}/`)
    return response.data.data
  }

  static async markAsRead(id: string): Promise<Notification> {
    const response = await api.post<APIResponse<Notification>>(`/api/v1/notifications/${id}/mark_read/`)
    return response.data.data
  }

  static async markAllAsRead(): Promise<{ marked_count: number }> {
    const response = await api.post<APIResponse<{ marked_count: number }>>('/api/v1/notifications/mark_all_read/')
    return response.data.data
  }

  static async deleteNotification(id: string): Promise<void> {
    await api.delete(`/api/v1/notifications/${id}/`)
  }

  static async clearReadNotifications(): Promise<{ deleted_count: number }> {
    const response = await api.delete<APIResponse<{ deleted_count: number }>>('/api/v1/notifications/clear_read/')
    return response.data.data
  }

  static async getUnreadCount(): Promise<{ unread_count: number }> {
    const response = await api.get<APIResponse<{ unread_count: number }>>('/api/v1/notifications/unread_count/')
    return response.data.data
  }

  static async getNotificationStats(): Promise<{
    total_notifications: number
    unread_notifications: number
    read_notifications: number
    notifications_by_type: Record<string, number>
    recent_notifications: Notification[]
  }> {
    const response = await api.get<APIResponse<any>>('/api/v1/notifications/stats/')
    return response.data.data
  }

  static async getNotificationsByType(): Promise<Record<string, Notification[]>> {
    const response = await api.get<APIResponse<Record<string, Notification[]>>>('/api/v1/notifications/by_type/')
    return response.data.data
  }

  // Email delivery tracking
  static async getEmailDeliveryLogs(params?: {
    page?: number
    page_size?: number
  }): Promise<PaginatedResponse<EmailDeliveryLog>> {
    const response = await api.get<APIResponse<PaginatedResponse<EmailDeliveryLog>>>('/api/v1/email-delivery-logs/', {
      params
    })
    return response.data.data
  }

  static async getEmailDeliveryStats(): Promise<{
    total_emails: number
    sent_emails: number
    failed_emails: number
    delivered_emails: number
    opened_emails: number
    clicked_emails: number
    delivery_rate: number
    open_rate: number
    click_rate: number
  }> {
    const response = await api.get<APIResponse<any>>('/api/v1/email-delivery-logs/delivery_stats/')
    return response.data.data
  }

  // Email template management
  static async getNotificationTemplates(): Promise<NotificationTemplate[]> {
    const response = await api.get<APIResponse<NotificationTemplate[]>>('/api/v1/notification-templates/')
    return response.data.data
  }

  static async getAvailableEmailTemplates(): Promise<EmailTemplate[]> {
    const response = await api.get<APIResponse<EmailTemplate[]>>('/api/v1/notification-templates/available_templates/')
    return response.data.data
  }

  static async createNotificationTemplate(template: Partial<NotificationTemplate>): Promise<NotificationTemplate> {
    const response = await api.post<APIResponse<NotificationTemplate>>('/api/v1/notification-templates/', template)
    return response.data.data
  }

  static async updateNotificationTemplate(id: string, template: Partial<NotificationTemplate>): Promise<NotificationTemplate> {
    const response = await api.put<APIResponse<NotificationTemplate>>(`/api/v1/notification-templates/${id}/`, template)
    return response.data.data
  }

  static async deleteNotificationTemplate(id: string): Promise<void> {
    await api.delete(`/api/v1/notification-templates/${id}/`)
  }

  static async testEmailTemplate(id: string): Promise<{ sent: boolean }> {
    const response = await api.post<APIResponse<{ sent: boolean }>>(`/api/v1/notification-templates/${id}/test_template/`)
    return response.data.data
  }

  // Chat functionality
  static async getChatMessages(params?: {
    room?: string
    page?: number
    page_size?: number
  }): Promise<PaginatedResponse<ChatMessage>> {
    const response = await api.get<APIResponse<PaginatedResponse<ChatMessage>>>('/api/v1/chat-messages/', {
      params
    })
    return response.data.data
  }

  static async sendChatMessage(roomName: string, content: string): Promise<ChatMessage> {
    const response = await api.post<APIResponse<ChatMessage>>('/api/v1/chat-messages/', {
      room_name: roomName,
      content
    })
    return response.data.data
  }

  static async editChatMessage(id: string, content: string): Promise<ChatMessage> {
    const response = await api.put<APIResponse<ChatMessage>>(`/api/v1/chat-messages/${id}/edit_message/`, {
      content
    })
    return response.data.data
  }

  static async deleteChatMessage(id: string): Promise<void> {
    await api.delete(`/api/v1/chat-messages/${id}/delete_message/`)
  }

  static async getChatRoomHistory(roomName: string): Promise<ChatMessage[]> {
    const response = await api.get<APIResponse<ChatMessage[]>>('/api/v1/chat-messages/room_history/', {
      params: { room: roomName }
    })
    return response.data.data
  }

  // WebSocket connection management
  static async getWebSocketConnections(): Promise<WebSocketConnection[]> {
    const response = await api.get<APIResponse<WebSocketConnection[]>>('/api/v1/websocket-connections/')
    return response.data.data
  }

  static async getActiveWebSocketConnections(): Promise<WebSocketConnection[]> {
    const response = await api.get<APIResponse<WebSocketConnection[]>>('/api/v1/websocket-connections/active_connections/')
    return response.data.data
  }

  static async getWebSocketConnectionStats(): Promise<{
    total_connections: number
    active_connections: number
    connections_by_type: Record<string, number>
    average_connection_duration: number
    peak_concurrent_connections: number
    recent_connections: WebSocketConnection[]
  }> {
    const response = await api.get<APIResponse<any>>('/api/v1/websocket-connections/connection_stats/')
    return response.data.data
  }

  static async sendBroadcastMessage(message: string, title?: string, priority?: string): Promise<void> {
    await api.post('/api/v1/websocket-connections/send_broadcast/', {
      message,
      title: title || 'System Announcement',
      priority: priority || 'normal'
    })
  }

  // Notification preferences through centralized API
  static async getNotificationPreferences(): Promise<{
    email_notifications: boolean
    push_notifications: boolean
    course_enrollment_notifications: boolean
    class_reminder_notifications: boolean
    assignment_due_notifications: boolean
    payment_notifications: boolean
    system_notifications: boolean
  }> {
    const response = await api.get<APIResponse<any>>('/api/v1/notifications/preferences/')
    return response.data.data
  }

  static async updateNotificationPreferences(preferences: {
    email_notifications?: boolean
    push_notifications?: boolean
    course_enrollment_notifications?: boolean
    class_reminder_notifications?: boolean
    assignment_due_notifications?: boolean
    payment_notifications?: boolean
    system_notifications?: boolean
  }): Promise<any> {
    const response = await api.put<APIResponse<any>>('/api/v1/notifications/preferences/', preferences)
    return response.data.data
  }

  // Real-time notifications (WebSocket) through centralized API
  static connectWebSocket(): WebSocket | null {
    const token = localStorage.getItem('access_token')
    if (!token) return null

    // Use centralized API WebSocket endpoint
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsHost = import.meta.env.VITE_WS_HOST || window.location.host
    const wsUrl = `${wsProtocol}//${wsHost}/ws/notifications/?token=${token}`
    
    const ws = new WebSocket(wsUrl)

    ws.onopen = () => {
      console.log('Notification WebSocket connected to centralized API')
    }

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      this.handleRealtimeMessage(data)
    }

    ws.onclose = (event) => {
      console.log('Notification WebSocket disconnected from centralized API')
      
      // Only attempt to reconnect if it wasn't a clean close
      if (event.code !== 1000) {
        setTimeout(() => {
          this.connectWebSocket()
        }, 5000)
      }
    }

    ws.onerror = (error) => {
      console.error('Notification WebSocket error:', error)
    }

    return ws
  }

  // Chat WebSocket connection
  static connectChatWebSocket(roomName: string): WebSocket | null {
    const token = localStorage.getItem('access_token')
    if (!token) return null

    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsHost = import.meta.env.VITE_WS_HOST || window.location.host
    const wsUrl = `${wsProtocol}//${wsHost}/ws/chat/${roomName}/?token=${token}`
    
    const ws = new WebSocket(wsUrl)

    ws.onopen = () => {
      console.log(`Chat WebSocket connected to room: ${roomName}`)
    }

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      this.handleChatMessage(data)
    }

    ws.onclose = (event) => {
      console.log(`Chat WebSocket disconnected from room: ${roomName}`)
      
      if (event.code !== 1000) {
        setTimeout(() => {
          this.connectChatWebSocket(roomName)
        }, 5000)
      }
    }

    ws.onerror = (error) => {
      console.error('Chat WebSocket error:', error)
    }

    return ws
  }

  private static handleRealtimeMessage(data: any): void {
    // Handle different types of real-time messages
    switch (data.type) {
      case 'notification':
        this.handleRealtimeNotification(data.notification)
        break
      case 'system_message':
        this.handleSystemMessage(data)
        break
      case 'broadcast':
        this.handleBroadcastMessage(data)
        break
      case 'unread_count':
        this.handleUnreadCountUpdate(data)
        break
      case 'connection_established':
        console.log('WebSocket connection established:', data)
        break
      case 'pong':
        console.log('WebSocket ping response received')
        break
      default:
        console.log('Unknown WebSocket message type:', data.type)
    }
  }

  private static handleRealtimeNotification(notification: any): void {
    // Handle real-time notification
    // Show browser notification if permission granted
    if (Notification.permission === 'granted') {
      new Notification(notification.title, {
        body: notification.message,
        icon: '/favicon.ico'
      })
    }

    // Dispatch custom event for components to listen to
    window.dispatchEvent(new CustomEvent('newNotification', { detail: notification }))
  }

  private static handleSystemMessage(data: any): void {
    // Handle system messages
    console.log('System message:', data.message)
    window.dispatchEvent(new CustomEvent('systemMessage', { detail: data }))
  }

  private static handleBroadcastMessage(data: any): void {
    // Handle broadcast messages
    console.log('Broadcast message:', data.message)
    window.dispatchEvent(new CustomEvent('broadcastMessage', { detail: data }))
  }

  private static handleUnreadCountUpdate(data: any): void {
    // Handle unread count updates
    window.dispatchEvent(new CustomEvent('unreadCountUpdate', { detail: data }))
  }

  private static handleChatMessage(data: any): void {
    // Handle chat messages
    switch (data.type) {
      case 'message':
        window.dispatchEvent(new CustomEvent('chatMessage', { detail: data.message }))
        break
      case 'user_joined':
        window.dispatchEvent(new CustomEvent('userJoined', { detail: data.user }))
        break
      case 'user_left':
        window.dispatchEvent(new CustomEvent('userLeft', { detail: data.user }))
        break
      case 'typing':
        window.dispatchEvent(new CustomEvent('userTyping', { detail: data }))
        break
      default:
        console.log('Unknown chat message type:', data.type)
    }
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