<template>
  <button 
    @click="createTestNotification"
    class="bg-gradient-to-r from-orange-400 to-orange-600 text-white px-4 py-2 rounded-lg font-semibold hover:from-orange-500 hover:to-orange-700 transition-all duration-200 transform hover:scale-105 shadow-lg"
  >
    🔔 Test Notification
  </button>
</template>

<script setup lang="ts">
import { useNotificationStore } from '@/stores/notifications'
import { notificationSoundService } from '@/utils/notificationSound'

const notificationStore = useNotificationStore()

const createTestNotification = () => {
  // Create a test notification
  const testNotification = {
    id: `test-${Date.now()}`,
    type: 'system',
    title: 'Test Notification',
    message: 'This is a test notification to verify the system is working!',
    data: {},
    is_read: false,
    created_at: new Date().toISOString(),
    priority: 'normal' as const,
    category: 'system'
  }

  // Add to store
  notificationStore.addNotification(testNotification)
  
  // Play sound
  notificationSoundService.playNotificationBeep()
  
  // Show browser notification if permission granted
  if ('Notification' in window && Notification.permission === 'granted') {
    new Notification(testNotification.title, {
      body: testNotification.message,
      icon: '/favicon.ico'
    })
  }
}
</script>