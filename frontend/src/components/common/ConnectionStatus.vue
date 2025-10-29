<template>
  <div class="connection-status" :class="statusClass">
    <div class="status-indicator" :class="indicatorClass">
      <div class="status-dot" :class="dotClass"></div>
      <span class="status-text">{{ statusText }}</span>
    </div>
    
    <div v-if="showDetails" class="status-details">
      <div class="detail-item">
        <span class="label">Status:</span>
        <span class="value">{{ connectionHealth.status }}</span>
      </div>
      <div class="detail-item">
        <span class="label">Details:</span>
        <span class="value">{{ connectionHealth.details }}</span>
      </div>
      <div v-if="status.lastConnected" class="detail-item">
        <span class="label">Last Connected:</span>
        <span class="value">{{ formatTime(status.lastConnected) }}</span>
      </div>
      <div v-if="status.reconnectAttempts > 0" class="detail-item">
        <span class="label">Reconnect Attempts:</span>
        <span class="value">{{ status.reconnectAttempts }}</span>
      </div>
    </div>
    
    <button 
      v-if="!status.isConnected && !status.isConnecting" 
      @click="$emit('reconnect')"
      class="reconnect-btn"
    >
      Reconnect
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { ConnectionStatus } from '@/services/websocket'

interface Props {
  status: ConnectionStatus
  showDetails?: boolean
  compact?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showDetails: false,
  compact: false
})

// const emit = defineEmits<{
//   reconnect: []
// }>() // Unused for now

const connectionHealth = computed(() => {
  if (!props.status.isConnected) {
    return {
      status: 'unhealthy' as const,
      details: props.status.error || 'Not connected'
    }
  }

  if (props.status.reconnectAttempts > 0) {
    return {
      status: 'degraded' as const,
      details: `Recently reconnected (${props.status.reconnectAttempts} attempts)`
    }
  }

  return {
    status: 'healthy' as const,
    details: 'Connection stable'
  }
})

const statusClass = computed(() => ({
  'connection-status--compact': props.compact,
  'connection-status--healthy': connectionHealth.value.status === 'healthy',
  'connection-status--degraded': connectionHealth.value.status === 'degraded',
  'connection-status--unhealthy': connectionHealth.value.status === 'unhealthy'
}))

const indicatorClass = computed(() => ({
  'status-indicator--connecting': props.status.isConnecting,
  'status-indicator--connected': props.status.isConnected,
  'status-indicator--disconnected': !props.status.isConnected && !props.status.isConnecting
}))

const dotClass = computed(() => ({
  'status-dot--green': props.status.isConnected && connectionHealth.value.status === 'healthy',
  'status-dot--yellow': props.status.isConnected && connectionHealth.value.status === 'degraded',
  'status-dot--red': !props.status.isConnected && !props.status.isConnecting,
  'status-dot--pulse': props.status.isConnecting
}))

const statusText = computed(() => {
  if (props.status.isConnecting) return 'Connecting...'
  if (props.status.isConnected) {
    return connectionHealth.value.status === 'healthy' ? 'Connected' : 'Connected (Unstable)'
  }
  return 'Disconnected'
})

const formatTime = (date: Date) => {
  return new Intl.DateTimeFormat('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  }).format(date)
}
</script>

<style scoped>
.connection-status {
  @apply bg-white border border-gray-200 rounded-lg p-3 shadow-sm;
}

.connection-status--compact {
  @apply p-2;
}

.connection-status--healthy {
  @apply border-green-200 bg-green-50;
}

.connection-status--degraded {
  @apply border-yellow-200 bg-yellow-50;
}

.connection-status--unhealthy {
  @apply border-red-200 bg-red-50;
}

.status-indicator {
  @apply flex items-center gap-2;
}

.status-dot {
  @apply w-3 h-3 rounded-full;
}

.status-dot--green {
  @apply bg-green-500;
}

.status-dot--yellow {
  @apply bg-yellow-500;
}

.status-dot--red {
  @apply bg-red-500;
}

.status-dot--pulse {
  @apply bg-blue-500 animate-pulse;
}

.status-text {
  @apply text-sm font-medium text-gray-700;
}

.status-details {
  @apply mt-3 space-y-1;
}

.detail-item {
  @apply flex justify-between text-xs;
}

.label {
  @apply text-gray-500 font-medium;
}

.value {
  @apply text-gray-700;
}

.reconnect-btn {
  @apply mt-2 px-3 py-1 bg-blue-500 text-white text-xs rounded hover:bg-blue-600 transition-colors;
}
</style>