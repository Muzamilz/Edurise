<template>
  <div class="notification-demo">
    <div class="demo-header">
      <h2 class="text-2xl font-bold text-gray-900 mb-4">Notification System Demo</h2>
      <p class="text-gray-600 mb-6">Test all notification features including sounds, animations, and different priority levels.</p>
    </div>

    <div class="demo-grid">
      <!-- Notification Types -->
      <div class="demo-section">
        <h3 class="section-title">Notification Types</h3>
        <div class="demo-buttons">
          <button @click="showInfoNotification" class="demo-btn demo-btn--info">
            ℹ️ Info Notification
          </button>
          <button @click="showSuccessNotification" class="demo-btn demo-btn--success">
            ✅ Success Notification
          </button>
          <button @click="showWarningNotification" class="demo-btn demo-btn--warning">
            ⚠️ Warning Notification
          </button>
          <button @click="showUrgentNotification" class="demo-btn demo-btn--urgent">
            🚨 Urgent Notification
          </button>
        </div>
      </div>

      <!-- Sound Tests -->
      <div class="demo-section">
        <h3 class="section-title">Sound Effects</h3>
        <div class="demo-buttons">
          <button @click="playNotificationSound" class="demo-btn">
            🔊 Notification Beep
          </button>
          <button @click="playUrgentSound" class="demo-btn">
            📢 Urgent Sound
          </button>
          <button @click="playSuccessSound" class="demo-btn">
            🎵 Success Sound
          </button>
        </div>
      </div>

      <!-- Badge Tests -->
      <div class="demo-section">
        <h3 class="section-title">Badge Variants</h3>
        <div class="badge-demos">
          <div class="badge-demo-item">
            <NotificationBadge :count="3" variant="default">
              <div class="demo-icon">🔔</div>
            </NotificationBadge>
            <span>Default</span>
          </div>
          <div class="badge-demo-item">
            <NotificationBadge :count="15" variant="urgent" :pulse="true">
              <div class="demo-icon">🚨</div>
            </NotificationBadge>
            <span>Urgent</span>
          </div>
          <div class="badge-demo-item">
            <NotificationBadge :count="5" variant="success">
              <div class="demo-icon">✅</div>
            </NotificationBadge>
            <span>Success</span>
          </div>
          <div class="badge-demo-item">
            <NotificationBadge :count="8" variant="warning">
              <div class="demo-icon">⚠️</div>
            </NotificationBadge>
            <span>Warning</span>
          </div>
        </div>
      </div>

      <!-- Animation Tests -->
      <div class="demo-section">
        <h3 class="section-title">Animations</h3>
        <div class="demo-buttons">
          <button @click="triggerBellShake" class="demo-btn">
            🔔 Bell Shake
          </button>
          <button @click="triggerPulseAnimation" class="demo-btn">
            💫 Pulse Effect
          </button>
          <button @click="triggerRingAnimation" class="demo-btn">
            ⭕ Ring Expand
          </button>
        </div>
      </div>

      <!-- Bulk Actions -->
      <div class="demo-section">
        <h3 class="section-title">Bulk Actions</h3>
        <div class="demo-buttons">
          <button @click="createMultipleNotifications" class="demo-btn">
            📚 Create 5 Notifications
          </button>
          <button @click="simulateRealTimeNotifications" class="demo-btn">
            ⚡ Simulate Real-time
          </button>
          <button @click="clearAllNotifications" class="demo-btn demo-btn--danger">
            🗑️ Clear All
          </button>
        </div>
      </div>
    </div>

    <!-- Demo Animation Elements -->
    <div class="demo-animations">
      <div ref="demobell" class="demo-bell">🔔</div>
      <div ref="demoring" class="demo-ring"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { notificationSoundService } from '@/utils/notificationSound'
import { showToast, showSuccessToast, showErrorToast, showWarningToast, showInfoToast } from '@/utils/toast'
import { useAnimations } from '@/composables/useAnimations'
import NotificationBadge from './NotificationBadge.vue'

const { pulse, shake, fadeIn } = useAnimations()

const demobell = ref<HTMLElement>()
const demoring = ref<HTMLElement>()

// Notification type demos
const showInfoNotification = () => {
  showInfoToast('This is an informational notification', 'Info')
}

const showSuccessNotification = () => {
  showSuccessToast('Operation completed successfully!', 'Success')
}

const showWarningNotification = () => {
  showWarningToast('Please review your settings', 'Warning')
}

const showUrgentNotification = () => {
  showErrorToast('Immediate attention required!', 'Urgent')
}

// Sound effect demos
const playNotificationSound = () => {
  notificationSoundService.playNotificationBeep()
}

const playUrgentSound = () => {
  notificationSoundService.playUrgentNotification()
}

const playSuccessSound = () => {
  notificationSoundService.playSuccessSound()
}

// Animation demos
const triggerBellShake = () => {
  if (demobell.value) {
    shake(demobell.value)
  }
}

const triggerPulseAnimation = () => {
  if (demobell.value) {
    pulse(demobell.value)
  }
}

const triggerRingAnimation = () => {
  if (demoring.value) {
    fadeIn(demoring.value)
  }
}

// Bulk action demos
const createMultipleNotifications = () => {
  const notifications = [
    { message: 'Assignment due tomorrow', title: 'Reminder', type: 'warning' },
    { message: 'New course material available', title: 'Course Update', type: 'info' },
    { message: 'Grade posted for Quiz 3', title: 'Grade Update', type: 'success' },
    { message: 'Live class starting in 10 minutes', title: 'Class Reminder', type: 'warning' },
    { message: 'Payment processed successfully', title: 'Payment', type: 'success' }
  ]

  notifications.forEach((notif, index) => {
    setTimeout(() => {
      showToast(notif.message, { 
        title: notif.title, 
        type: notif.type as any 
      })
    }, index * 500)
  })
}

const simulateRealTimeNotifications = () => {
  let count = 0
  const interval = setInterval(() => {
    count++
    showToast(`Real-time notification #${count}`, {
      title: 'Live Update',
      type: 'info'
    })
    
    if (count >= 3) {
      clearInterval(interval)
    }
  }, 2000)
}

const clearAllNotifications = () => {
  showToast('All notifications cleared', {
    title: 'Cleared',
    type: 'success'
  })
}
</script>

<style scoped>
.notification-demo {
  @apply max-w-4xl mx-auto p-6;
}

.demo-header {
  @apply text-center mb-8;
}

.demo-grid {
  @apply grid grid-cols-1 md:grid-cols-2 gap-6 mb-8;
}

.demo-section {
  @apply bg-white rounded-lg p-6 shadow-sm border border-gray-200;
}

.section-title {
  @apply text-lg font-semibold text-gray-900 mb-4;
}

.demo-buttons {
  @apply flex flex-wrap gap-3;
}

.demo-btn {
  @apply px-4 py-2 rounded-lg font-medium transition-all duration-200 border;
}

.demo-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.demo-btn--info {
  @apply bg-blue-50 text-blue-700 border-blue-200 hover:bg-blue-100;
}

.demo-btn--success {
  @apply bg-green-50 text-green-700 border-green-200 hover:bg-green-100;
}

.demo-btn--warning {
  @apply bg-yellow-50 text-yellow-700 border-yellow-200 hover:bg-yellow-100;
}

.demo-btn--urgent {
  @apply bg-red-50 text-red-700 border-red-200 hover:bg-red-100;
}

.demo-btn--danger {
  @apply bg-red-50 text-red-700 border-red-200 hover:bg-red-100;
}

.demo-btn:not([class*="--"]) {
  @apply bg-gray-50 text-gray-700 border-gray-200 hover:bg-gray-100;
}

.badge-demos {
  @apply flex flex-wrap gap-6;
}

.badge-demo-item {
  @apply flex flex-col items-center gap-2;
}

.demo-icon {
  @apply text-2xl p-3 bg-gray-100 rounded-full;
}

.demo-animations {
  @apply fixed top-4 left-4 pointer-events-none z-50;
}

.demo-bell {
  @apply text-4xl mb-4;
}

.demo-ring {
  @apply w-12 h-12 border-2 border-blue-400 rounded-full opacity-0;
}
</style>