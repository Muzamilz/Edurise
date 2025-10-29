<template>
  <div 
    class="notification-item"
    :class="itemClasses"
    @click="$emit('click', notification)"
  >
    <!-- Icon -->
    <div class="notification-icon" :class="iconClasses">
      <span class="text-lg">{{ notificationIcon }}</span>
    </div>

    <!-- Content -->
    <div class="notification-content">
      <div class="notification-header">
        <h4 class="notification-title">{{ notification.title }}</h4>
        <div class="notification-meta">
          <span class="notification-time">{{ formatTime(notification.created_at) }}</span>
          <div v-if="notification.priority === 'urgent'" class="priority-badge urgent">
            Urgent
          </div>
          <div v-else-if="notification.priority === 'high'" class="priority-badge high">
            High
          </div>
        </div>
      </div>
      
      <p class="notification-message">{{ notification.message }}</p>
      
      <!-- Additional data display -->
      <div v-if="hasAdditionalData" class="notification-data">
        <div v-if="notification.data?.due_date" class="data-item">
          <span class="text-gray-400">📅</span>
          <span>Due: {{ formatDate(notification.data.due_date) }}</span>
        </div>
        <div v-if="notification.data?.grade" class="data-item">
          <span class="text-gray-400">🎓</span>
          <span>Grade: {{ notification.data.grade }}</span>
        </div>
        <div v-if="notification.data?.class_time" class="data-item">
          <span class="text-gray-400">🕐</span>
          <span>{{ formatTime(notification.data.class_time) }}</span>
        </div>
      </div>
    </div>

    <!-- Actions -->
    <div class="notification-actions">
      <button 
        v-if="!notification.is_read"
        @click.stop="$emit('mark-read', notification.id)"
        class="action-btn mark-read"
        title="Mark as read"
      >
        <span>✓</span>
      </button>
      
      <button 
        @click.stop="$emit('delete', notification.id)"
        class="action-btn delete"
        title="Delete notification"
      >
        <span>✕</span>
      </button>
    </div>

    <!-- Unread indicator -->
    <div v-if="!notification.is_read" class="unread-indicator"></div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
// import {
//   BellIcon,
//   AcademicCapIcon,
//   BookOpenIcon,
//   CalendarIcon,
//   ClockIcon,
//   ExclamationTriangleIcon,
//   InformationCircleIcon,
//   CheckIcon,
//   XMarkIcon,
//   VideoCameraIcon,
//   DocumentTextIcon,
//   UserGroupIcon
// } from '@heroicons/vue/24/outline'

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

interface Props {
  notification: Notification
}

const props = defineProps<Props>()

// const emit = defineEmits<{
//   click: [notification: Notification]
//   'mark-read': [id: string]
//   delete: [id: string]
// }>() // Used via $emit in template
defineEmits<{
  click: [notification: Notification]
  'mark-read': [id: string]
  delete: [id: string]
}>()

const itemClasses = computed(() => ({
  'notification-item--unread': !props.notification.is_read,
  'notification-item--urgent': props.notification.priority === 'urgent',
  'notification-item--high': props.notification.priority === 'high'
}))

const iconClasses = computed(() => {
  const baseClasses = 'notification-icon'
  
  switch (props.notification.category) {
    case 'assignment':
      return `${baseClasses} notification-icon--assignment`
    case 'grade':
      return `${baseClasses} notification-icon--grade`
    case 'live_class':
      return `${baseClasses} notification-icon--class`
    case 'system':
      return `${baseClasses} notification-icon--system`
    case 'course':
      return `${baseClasses} notification-icon--course`
    default:
      return `${baseClasses} notification-icon--default`
  }
})

const notificationIcon = computed(() => {
  switch (props.notification.category) {
    case 'assignment':
      return '📄'
    case 'grade':
      return '🎓'
    case 'live_class':
      return '📹'
    case 'course':
      return '📚'
    case 'system':
      return props.notification.priority === 'urgent' ? '⚠️' : 'ℹ️'
    default:
      return '🔔'
  }
})

const hasAdditionalData = computed(() => {
  return props.notification.data && (
    props.notification.data.due_date ||
    props.notification.data.grade ||
    props.notification.data.class_time
  )
})

const formatTime = (dateString: string) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60))
  
  if (diffInMinutes < 1) {
    return 'Just now'
  } else if (diffInMinutes < 60) {
    return `${diffInMinutes}m ago`
  } else if (diffInMinutes < 1440) { // 24 hours
    const hours = Math.floor(diffInMinutes / 60)
    return `${hours}h ago`
  } else if (diffInMinutes < 10080) { // 7 days
    const days = Math.floor(diffInMinutes / 1440)
    return `${days}d ago`
  } else {
    return date.toLocaleDateString()
  }
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>
.notification-item {
  position: relative;
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 1rem;
  margin: 0.5rem;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
}

.notification-item:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  background: rgba(255, 255, 255, 0.95);
  border-color: rgba(245, 158, 11, 0.1);
}

.notification-item--unread {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.05), rgba(255, 255, 255, 0.9));
  border-color: rgba(245, 158, 11, 0.2);
  box-shadow: 0 2px 8px rgba(245, 158, 11, 0.1);
}

.notification-item--urgent {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.05), rgba(255, 255, 255, 0.9));
  border-color: rgba(239, 68, 68, 0.2);
  animation: urgentGlow 2s ease-in-out infinite;
}

.notification-item--high {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.08), rgba(255, 255, 255, 0.9));
  border-color: rgba(245, 158, 11, 0.25);
}

@keyframes slideInFromLeft {
  0% {
    transform: translateX(-20px);
    opacity: 0;
  }
  100% {
    transform: translateX(0);
    opacity: 1;
  }
}

@keyframes urgentGlow {
  0%, 100% {
    box-shadow: 0 2px 8px rgba(239, 68, 68, 0.1);
  }
  50% {
    box-shadow: 0 4px 16px rgba(239, 68, 68, 0.2);
    border-color: rgba(239, 68, 68, 0.3);
  }
}

.notification-icon {
  @apply flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center;
}

.notification-icon--assignment {
  @apply bg-blue-100 text-blue-600;
}

.notification-icon--grade {
  @apply bg-green-100 text-green-600;
}

.notification-icon--class {
  @apply bg-purple-100 text-purple-600;
}

.notification-icon--course {
  @apply bg-indigo-100 text-indigo-600;
}

.notification-icon--system {
  @apply bg-gray-100 text-gray-600;
}

.notification-icon--default {
  @apply bg-gray-100 text-gray-600;
}

.notification-content {
  @apply flex-1 min-w-0;
}

.notification-header {
  @apply flex items-start justify-between gap-2 mb-1;
}

.notification-title {
  @apply text-sm font-medium text-gray-900 truncate;
}

.notification-meta {
  @apply flex items-center gap-2 flex-shrink-0;
}

.notification-time {
  @apply text-xs text-gray-500;
}

.priority-badge {
  @apply text-xs px-2 py-0.5 rounded-full font-medium;
}

.priority-badge.urgent {
  @apply bg-red-100 text-red-700;
}

.priority-badge.high {
  @apply bg-orange-100 text-orange-700;
}

.notification-message {
  @apply text-sm text-gray-600 line-clamp-2;
}

.notification-data {
  @apply mt-2 space-y-1;
}

.data-item {
  @apply flex items-center gap-1 text-xs text-gray-500;
}

.notification-actions {
  @apply flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-all duration-200;
  transform: translateX(10px);
}

.notification-item:hover .notification-actions {
  @apply opacity-100;
  transform: translateX(0);
}

.action-btn {
  @apply p-1 rounded hover:bg-gray-200 transition-all duration-200 cursor-pointer;
  transform: scale(1);
}

.action-btn:hover {
  transform: scale(1.1);
}

.action-btn.mark-read {
  @apply text-green-600 hover:bg-green-100;
}

.action-btn.mark-read:hover {
  box-shadow: 0 2px 4px rgba(34, 197, 94, 0.2);
}

.action-btn.delete {
  @apply text-red-600 hover:bg-red-100;
}

.action-btn.delete:hover {
  box-shadow: 0 2px 4px rgba(239, 68, 68, 0.2);
}

.unread-indicator {
  @apply absolute top-3 right-3 w-2 h-2 bg-blue-500 rounded-full;
  animation: unreadPulse 2s ease-in-out infinite;
}

@keyframes unreadPulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.6;
    transform: scale(1.2);
  }
}
</style>