<template>
  <div class="notification-center">
    <!-- Notification Bell Icon -->
    <div class="notification-trigger" @click="toggleNotifications">
      <NotificationBadge 
        :count="unreadCount" 
        :variant="unreadCount > 10 ? 'urgent' : 'default'"
        :pulse="hasNewNotification"
      >
        <div class="notification-bell" :class="{ 'bell-shake': hasNewNotification }">
          <svg 
            width="24" 
            height="24" 
            viewBox="0 0 24 24" 
            fill="none" 
            stroke="currentColor" 
            stroke-width="2" 
            stroke-linecap="round" 
            stroke-linejoin="round"
            class="bell-icon"
          >
            <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
            <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
          </svg>
        </div>
      </NotificationBadge>
      
      <!-- Notification Ring Animation -->
      <div 
        v-if="hasNewNotification" 
        class="notification-ring"
      ></div>
    </div>

    <!-- Notification Panel -->
    <Transition name="slide-down">
      <div v-if="isOpen" class="notification-panel">
        <!-- Header -->
        <div class="notification-header">
          <h3 class="text-lg font-semibold text-gray-900">Notifications</h3>
          <div class="header-actions">
            <button 
              v-if="unreadCount > 0"
              @click="markAllAsRead"
              class="text-sm text-blue-600 hover:text-blue-800"
            >
              Mark all read
            </button>
            <button @click="openSettings" class="text-gray-400 hover:text-gray-600">
              <span class="text-lg">⚙️</span>
            </button>
          </div>
        </div>

        <!-- Filters -->
        <div class="notification-filters">
          <button 
            v-for="filter in filters"
            :key="filter.key"
            @click="activeFilter = filter.key"
            class="filter-btn"
            :class="{ 'active': activeFilter === filter.key }"
          >
            {{ filter.label }}
            <span v-if="filter.count > 0" class="filter-count">{{ filter.count }}</span>
          </button>
        </div>

        <!-- Notifications List -->
        <div class="notification-list">
          <div v-if="loading" class="loading-state">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <span class="text-gray-500">Loading notifications...</span>
          </div>

          <div v-else-if="filteredNotifications.length === 0" class="empty-state">
            <span class="text-5xl text-gray-300 mx-auto mb-2 block">🔕</span>
            <p class="text-gray-500">No notifications</p>
          </div>

          <div v-else class="space-y-2">
            <NotificationItem
              v-for="notification in filteredNotifications"
              :key="notification.id"
              :notification="notification"
              @click="handleNotificationClick"
              @mark-read="markAsRead"
              @delete="deleteNotification"
            />
          </div>

          <!-- Load More -->
          <div v-if="hasMore && !loading" class="load-more">
            <button @click="loadMore" class="load-more-btn">
              Load more notifications
            </button>
          </div>
        </div>

        <!-- Settings Panel -->
        <NotificationSettings
          v-if="showSettings"
          :preferences="notificationPreferences"
          @update="updatePreferences"
          @close="showSettings = false"
        />
      </div>
    </Transition>

    <!-- Overlay -->
    <div 
      v-if="isOpen" 
      class="notification-overlay"
      @click="closeNotifications"
    ></div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useNotificationStore } from '@/stores/notifications'
import { useWebSocketStore } from '@/stores/websocket'
import { useAnimations } from '@/composables/useAnimations'
import { notificationSoundService } from '@/utils/notificationSound'
import { showNotificationToast, showSuccessToast } from '@/utils/toast'
import NotificationItem from './NotificationItem.vue'
import NotificationSettings from './NotificationSettings.vue'
import NotificationBadge from './NotificationBadge.vue'

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

const notificationStore = useNotificationStore()
const websocketStore = useWebSocketStore()
const { fadeIn, slideIn, morphButton, pulse } = useAnimations()

const isOpen = ref(false)
const showSettings = ref(false)
const loading = ref(false)
const hasNewNotification = ref(false)
const activeFilter = ref('all')
const notificationSound = ref<HTMLAudioElement | null>(null)

const notifications = computed(() => Array.isArray(notificationStore.notifications) ? notificationStore.notifications : [])
const unreadCount = computed(() => notificationStore.unreadCount)
const hasMore = computed(() => notificationStore.hasMore)
const notificationPreferences = computed(() => notificationStore.preferences)

const filters = computed(() => [
  { key: 'all', label: 'All', count: notifications.value.length },
  { key: 'unread', label: 'Unread', count: unreadCount.value },
  { key: 'assignments', label: 'Assignments', count: notifications.value.filter(n => n.category === 'assignment').length },
  { key: 'grades', label: 'Grades', count: notifications.value.filter(n => n.category === 'grade').length },
  { key: 'classes', label: 'Classes', count: notifications.value.filter(n => n.category === 'live_class').length },
  { key: 'system', label: 'System', count: notifications.value.filter(n => n.category === 'system').length }
])

const filteredNotifications = computed(() => {
  let filtered = Array.isArray(notifications.value) ? notifications.value : []

  switch (activeFilter.value) {
    case 'unread':
      filtered = filtered.filter(n => !n.is_read)
      break
    case 'assignments':
      filtered = filtered.filter(n => n.category === 'assignment')
      break
    case 'grades':
      filtered = filtered.filter(n => n.category === 'grade')
      break
    case 'classes':
      filtered = filtered.filter(n => n.category === 'live_class')
      break
    case 'system':
      filtered = filtered.filter(n => n.category === 'system')
      break
  }

  return filtered.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
})

const toggleNotifications = () => {
  isOpen.value = !isOpen.value
  if (isOpen.value && notifications.value.length === 0) {
    loadNotifications()
  }
  
  // Animate panel opening
  if (isOpen.value) {
    setTimeout(() => {
      const panel = document.querySelector('.notification-panel')
      if (panel) {
        slideIn(panel, 'right')
      }
    }, 50)
  }
}

const closeNotifications = () => {
  isOpen.value = false
  showSettings.value = false
}

const openSettings = () => {
  showSettings.value = true
}

const loadNotifications = async () => {
  loading.value = true
  try {
    await notificationStore.fetchNotifications()
  } finally {
    loading.value = false
  }
}

const loadMore = async () => {
  loading.value = true
  try {
    await notificationStore.fetchMoreNotifications()
  } finally {
    loading.value = false
  }
}

const markAsRead = async (notificationId: string) => {
  await notificationStore.markAsRead(notificationId)
}

const markAllAsRead = async () => {
  const unreadCountBefore = unreadCount.value
  await notificationStore.markAllAsRead()
  
  // Play success sound
  if (notificationPreferences.value.sound_enabled) {
    notificationSoundService.playSuccessSound()
  }
  
  // Show success toast
  showSuccessToast(`${unreadCountBefore} notifications marked as read`)
}

const deleteNotification = async (notificationId: string) => {
  await notificationStore.deleteNotification(notificationId)
}

const handleNotificationClick = (notification: Notification) => {
  // Mark as read if not already
  if (!notification.is_read) {
    markAsRead(notification.id)
  }

  // Handle navigation based on notification type
  handleNotificationNavigation(notification)
}

const handleNotificationNavigation = (notification: Notification) => {
  const { type, data } = notification

  switch (type) {
    case 'assignment_due':
    case 'assignment_graded':
      if (data?.assignment_id) {
        // Navigate to assignment
        window.location.href = `/assignments/${data.assignment_id}`
      }
      break
    case 'live_class_starting':
    case 'live_class_reminder':
      if (data?.live_class_id) {
        // Navigate to live class
        window.location.href = `/student/live-classes/${data.live_class_id}`
      }
      break
    case 'course_enrollment':
      if (data?.course_id) {
        // Navigate to course
        window.location.href = `/courses/${data.course_id}`
      }
      break
    case 'grade_posted':
      if (data?.course_id) {
        // Navigate to grades
        window.location.href = `/student/grades?course=${data.course_id}`
      }
      break
  }

  closeNotifications()
}

const updatePreferences = async (preferences: NotificationPreferences) => {
  await notificationStore.updatePreferences(preferences)
}

const playNotificationSound = (notification: Notification) => {
  if (notificationPreferences.value.sound_enabled) {
    // Set sound service enabled state
    notificationSoundService.setEnabled(notificationPreferences.value.sound_enabled)
    
    // Play different sounds based on notification priority
    switch (notification.priority) {
      case 'urgent':
        notificationSoundService.playUrgentNotification()
        break
      case 'high':
        notificationSoundService.playNotificationBeep()
        break
      default:
        notificationSoundService.playNotificationBeep()
        break
    }
  }
}

const showBrowserNotification = (notification: Notification) => {
  if (notificationPreferences.value.browser_notifications && 'Notification' in window) {
    if (Notification.permission === 'granted') {
      new Notification(notification.title, {
        body: notification.message,
        icon: '/favicon.ico',
        tag: notification.id
      })
    } else if (Notification.permission !== 'denied') {
      Notification.requestPermission().then(permission => {
        if (permission === 'granted') {
          showBrowserNotification(notification)
        }
      })
    }
  }
}

const handleRealtimeNotification = (notification: Notification) => {
  // Add visual indicator for new notification with animation
  hasNewNotification.value = true
  
  // Animate the notification bell
  const bellElement = document.querySelector('.notification-trigger')
  if (bellElement) {
    pulse(bellElement)
  }
  
  setTimeout(() => {
    hasNewNotification.value = false
  }, 3000)

  // Play sound if enabled
  playNotificationSound(notification)

  // Show browser notification if enabled
  showBrowserNotification(notification)
  
  // Show toast notification if panel is closed
  if (!isOpen.value) {
    showNotificationToast(notification)
  }
  
  // Add entrance animation for new notifications in the list
  setTimeout(() => {
    const newNotificationElement = document.querySelector('.notification-item:first-child')
    if (newNotificationElement) {
      fadeIn(newNotificationElement)
    }
  }, 100)
}

// WebSocket event handlers
const setupWebSocketHandlers = () => {
  const notificationWs = websocketStore.getConnection('notifications')
  
  if (notificationWs) {
    notificationWs.subscribe('notification', (data) => {
      notificationStore.addNotification(data.notification)
      handleRealtimeNotification(data.notification)
    })

    notificationWs.subscribe('unread_count', (data) => {
      notificationStore.setUnreadCount(data.count)
    })

    notificationWs.subscribe('system_message', (data) => {
      // Handle system messages
      console.log('System message:', data.message)
    })

    notificationWs.subscribe('broadcast', (data) => {
      // Handle broadcast messages
      const broadcastNotification: Notification = {
        id: `broadcast-${Date.now()}`,
        type: 'system_broadcast',
        title: data.title || 'System Announcement',
        message: data.message,
        is_read: false,
        created_at: new Date().toISOString(),
        priority: data.priority || 'normal',
        category: 'system'
      }
      
      notificationStore.addNotification(broadcastNotification)
      handleRealtimeNotification(broadcastNotification)
    })
  }
}

// Request browser notification permission on mount
const requestNotificationPermission = async () => {
  if ('Notification' in window && Notification.permission === 'default') {
    await Notification.requestPermission()
  }
}

onMounted(async () => {
  await requestNotificationPermission()
  try {
    await notificationStore.fetchPreferences()
  } catch (error) {
    console.warn('Could not load notification preferences, using defaults')
  }
  setupWebSocketHandlers()
})

onUnmounted(() => {
  // Cleanup is handled by the WebSocket store
})

// Watch for WebSocket connection changes
watch(() => (websocketStore.connections.notifications as any)?.status?.isConnected, (isConnected) => {
  if (isConnected) {
    setupWebSocketHandlers()
  }
})
</script>

<style scoped>
.notification-center {
  @apply relative;
  z-index: 1;
}

.notification-trigger {
  @apply relative p-3 rounded-full transition-all duration-200 cursor-pointer;
  background: rgba(245, 158, 11, 0.08);
  border: 1px solid rgba(245, 158, 11, 0.15);
}

.notification-trigger:hover {
  background: rgba(245, 158, 11, 0.12);
  border-color: rgba(245, 158, 11, 0.25);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.15);
}

.notification-bell-container {
  @apply relative flex items-center justify-center;
}

.notification-bell {
  color: #f59e0b;
  transition: all 0.2s ease;
}

.notification-bell:hover {
  color: #d97706;
  transform: scale(1.05);
}

.bell-icon {
  @apply w-6 h-6;
}

.bell-shake {
  animation: bellShake 0.8s ease-in-out;
}

@keyframes bellShake {
  0%, 100% { transform: rotate(0deg); }
  10%, 30%, 50%, 70%, 90% { transform: rotate(-10deg); }
  20%, 40%, 60%, 80% { transform: rotate(10deg); }
}

.notification-ring {
  @apply absolute inset-0 rounded-full border-2 border-blue-400 opacity-75 pointer-events-none;
  animation: ringExpand 2s ease-out infinite;
}

@keyframes ringExpand {
  0% {
    transform: scale(1);
    opacity: 0.7;
  }
  100% {
    transform: scale(2);
    opacity: 0;
  }
}

.notification-panel {
  position: absolute;
  top: calc(100% + 0.75rem);
  right: 0;
  background: white;
  border: 1px solid rgba(229, 231, 235, 0.6);
  border-radius: 16px;
  box-shadow: 
    0 20px 25px -5px rgba(0, 0, 0, 0.1),
    0 10px 10px -5px rgba(0, 0, 0, 0.04),
    0 0 0 1px rgba(245, 158, 11, 0.05);
  min-width: 28rem;
  width: 28rem;
  z-index: 1000;
  max-height: 32rem;
  display: flex;
  flex-direction: column;
  backdrop-filter: blur(20px);
  background: rgba(255, 255, 255, 0.98);
}

.notification-header {
  padding: 1.5rem 1.5rem 1rem;
  border-bottom: 1px solid rgba(229, 231, 235, 0.5);
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.02), rgba(255, 255, 255, 0.8));
}

.notification-header h3 {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1f2937;
  margin: 0;
  letter-spacing: -0.025em;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.header-actions button {
  color: #f59e0b;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.2s ease;
}

.header-actions button:hover {
  color: #d97706;
  background: rgba(245, 158, 11, 0.08);
  transform: scale(1.02);
}

.notification-filters {
  display: flex;
  gap: 0.5rem;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid rgba(229, 231, 235, 0.5);
  overflow-x: auto;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.notification-filters::-webkit-scrollbar {
  display: none;
}

.filter-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: #6b7280;
  background: rgba(249, 250, 251, 0.8);
  border: 1px solid rgba(229, 231, 235, 0.6);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
  backdrop-filter: blur(10px);
}

.filter-btn:hover {
  background: rgba(245, 158, 11, 0.08);
  border-color: rgba(245, 158, 11, 0.2);
  color: #f59e0b;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(245, 158, 11, 0.1);
}

.filter-btn.active {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  border-color: #d97706;
  color: white;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.25);
}

.filter-count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 1.25rem;
  height: 1.25rem;
  padding: 0 0.375rem;
  font-size: 0.75rem;
  font-weight: 600;
  background: rgba(107, 114, 128, 0.15);
  color: #6b7280;
  border-radius: 8px;
}

.filter-btn.active .filter-count {
  background: rgba(255, 255, 255, 0.25);
  color: white;
}

@keyframes countPulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.2); }
  100% { transform: scale(1); }
}

/* Ensure proper positioning */
.notification-center .notification-panel {
  position: absolute !important;
  right: 0 !important;
  top: calc(100% + 0.5rem) !important;
}

/* Mobile responsiveness */
@media (max-width: 768px) {
  .notification-panel {
    right: 0.5rem;
    left: 0.5rem;
    width: calc(100vw - 1rem);
    min-width: auto;
    max-height: 75vh;
    border-radius: 20px;
  }
  
  .notification-header {
    padding: 1.25rem 1.25rem 0.75rem;
  }
  
  .notification-filters {
    padding: 0.75rem 1.25rem;
    gap: 0.375rem;
  }
  
  .filter-btn {
    padding: 0.375rem 0.75rem;
    font-size: 0.8125rem;
  }
  
  .notification-list {
    padding: 0.375rem 0.75rem;
  }
}

@media (max-width: 480px) {
  .notification-panel {
    right: 0.25rem;
    left: 0.25rem;
    width: calc(100vw - 0.5rem);
    max-height: 85vh;
    border-radius: 16px;
  }
  
  .notification-header {
    padding: 1rem;
  }
  
  .notification-header h3 {
    font-size: 1.125rem;
  }
  
  .notification-filters {
    padding: 0.5rem 1rem;
    flex-wrap: wrap;
  }
  
  .filter-btn {
    padding: 0.25rem 0.625rem;
    font-size: 0.75rem;
  }
}

.notification-list {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
  min-height: 200px;
  max-height: 400px;
  scrollbar-width: thin;
  scrollbar-color: rgba(245, 158, 11, 0.3) transparent;
}

.notification-list::-webkit-scrollbar {
  width: 6px;
}

.notification-list::-webkit-scrollbar-track {
  background: transparent;
}

.notification-list::-webkit-scrollbar-thumb {
  background: rgba(245, 158, 11, 0.3);
  border-radius: 6px;
}

.notification-list::-webkit-scrollbar-thumb:hover {
  background: rgba(245, 158, 11, 0.5);
}

.notification-list .space-y-2 > * + * {
  margin-top: 0.5rem;
}

.loading-state {
  @apply flex flex-col items-center justify-center p-8 gap-2;
}

.loading-state .animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 2rem;
  text-align: center;
}

.empty-state span {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.6;
  animation: float 3s ease-in-out infinite;
}

.empty-state p {
  color: #6b7280;
  font-size: 0.875rem;
  font-weight: 500;
}

@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-8px); }
}

.load-more {
  padding: 1rem 1.5rem;
  border-top: 1px solid rgba(229, 231, 235, 0.5);
  background: rgba(249, 250, 251, 0.5);
}

.load-more-btn {
  width: 100%;
  padding: 0.75rem 1rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #f59e0b;
  background: rgba(245, 158, 11, 0.08);
  border: 1px solid rgba(245, 158, 11, 0.2);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.load-more-btn:hover {
  background: rgba(245, 158, 11, 0.12);
  border-color: rgba(245, 158, 11, 0.3);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(245, 158, 11, 0.15);
}

.notification-overlay {
  position: fixed;
  inset: 0;
  z-index: 40;
}

/* Transitions */
.slide-down-enter-active {
  @apply transition-all duration-300 ease-out;
}

.slide-down-leave-active {
  @apply transition-all duration-200 ease-in;
}

.slide-down-enter-from {
  @apply opacity-0;
  transform: translateY(-20px) scale(0.95);
}

.slide-down-leave-to {
  @apply opacity-0;
  transform: translateY(-10px) scale(0.98);
}

.slide-down-enter-to,
.slide-down-leave-from {
  @apply opacity-100;
  transform: translateY(0) scale(1);
}
</style>