<template>
  <div class="live-class-join-interface">
    <!-- Class Information Header -->
    <div class="class-header bg-gradient-to-r from-blue-600 to-blue-700 text-white p-6 rounded-t-lg">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold mb-2">{{ liveClass?.title }}</h1>
          <p class="text-blue-100 mb-1">{{ liveClass?.description }}</p>
          <div class="flex items-center space-x-4 text-sm text-blue-100">
            <span class="flex items-center">
              <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clip-rule="evenodd" />
              </svg>
              {{ formatDateTime(liveClass?.scheduled_at) }}
            </span>
            <span class="flex items-center">
              <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd" />
              </svg>
              {{ liveClass?.duration_minutes }} minutes
            </span>
          </div>
        </div>
        <div class="text-right">
          <div class="status-badge" :class="statusClasses">
            {{ statusText }}
          </div>
          <div v-if="timeUntilClass" class="text-sm text-blue-100 mt-2">
            {{ timeUntilClass }}
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="p-6 bg-white rounded-b-lg shadow-lg">
      <!-- Pre-class State -->
      <div v-if="liveClass?.status === 'scheduled'" class="text-center">
        <div class="mb-6">
          <svg class="w-16 h-16 mx-auto text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h3 class="text-lg font-medium text-gray-900 mb-2">Class Not Started Yet</h3>
          <p class="text-gray-600">
            The instructor will start the class at the scheduled time. You'll be able to join once it begins.
          </p>
        </div>

        <!-- Pre-join Actions -->
        <div class="space-y-4">
          <button
            v-if="canTestConnection"
            @click="testZoomConnection"
            :disabled="isTestingConnection"
            class="w-full sm:w-auto px-6 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors disabled:opacity-50"
          >
            <span v-if="isTestingConnection" class="flex items-center justify-center">
              <svg class="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Testing Connection...
            </span>
            <span v-else>Test Zoom Connection</span>
          </button>

          <div class="text-sm text-gray-500">
            <p>Make sure you have:</p>
            <ul class="list-disc list-inside mt-2 space-y-1">
              <li>Zoom client installed or browser ready</li>
              <li>Stable internet connection</li>
              <li>Camera and microphone permissions enabled</li>
            </ul>
          </div>
        </div>
      </div>

      <!-- Live Class State -->
      <div v-else-if="liveClass?.status === 'live'" class="text-center">
        <div class="mb-6">
          <div class="relative inline-block">
            <svg class="w-16 h-16 mx-auto text-green-500 mb-4" fill="currentColor" viewBox="0 0 20 20">
              <path d="M2 6a2 2 0 012-2h6a2 2 0 012 2v6a2 2 0 01-2 2H4a2 2 0 01-2-2V6zM14.553 7.106A1 1 0 0014 8v4a1 1 0 00.553.894l2 1A1 1 0 0018 13V7a1 1 0 00-1.447-.894l-2 1z" />
            </svg>
            <div class="absolute -top-1 -right-1 w-4 h-4 bg-red-500 rounded-full animate-pulse"></div>
          </div>
          <h3 class="text-lg font-medium text-gray-900 mb-2">Class is Live!</h3>
          <p class="text-gray-600 mb-6">
            Join the class now to participate in the live session.
          </p>
        </div>

        <!-- Join Actions -->
        <div class="space-y-4">
          <button
            @click="joinClass"
            :disabled="!liveClass?.join_url || isJoining"
            class="w-full sm:w-auto px-8 py-4 bg-green-600 text-white text-lg font-semibold rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="isJoining" class="flex items-center justify-center">
              <svg class="animate-spin -ml-1 mr-2 h-5 w-5" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Joining...
            </span>
            <span v-else class="flex items-center justify-center">
              <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path d="M2 6a2 2 0 012-2h6a2 2 0 012 2v6a2 2 0 01-2 2H4a2 2 0 01-2-2V6zM14.553 7.106A1 1 0 0014 8v4a1 1 0 00.553.894l2 1A1 1 0 0018 13V7a1 1 0 00-1.447-.894l-2 1z" />
              </svg>
              Join Class
            </span>
          </button>

          <!-- Alternative Join Options -->
          <div class="flex flex-col sm:flex-row gap-2 justify-center">
            <button
              @click="joinByPhone"
              class="px-4 py-2 text-sm text-blue-600 hover:text-blue-800 transition-colors"
            >
              Join by Phone
            </button>
            <button
              @click="copyJoinUrl"
              class="px-4 py-2 text-sm text-blue-600 hover:text-blue-800 transition-colors"
            >
              Copy Join URL
            </button>
          </div>

          <!-- Meeting Details -->
          <div v-if="showMeetingDetails" class="mt-6 p-4 bg-gray-50 rounded-lg text-left">
            <h4 class="font-medium text-gray-900 mb-3">Meeting Details</h4>
            <div class="space-y-2 text-sm">
              <div v-if="liveClass?.zoom_meeting_id">
                <span class="font-medium">Meeting ID:</span>
                <span class="ml-2 font-mono">{{ formatMeetingId(liveClass.zoom_meeting_id) }}</span>
                <button
                  @click="copyToClipboard(liveClass.zoom_meeting_id)"
                  class="ml-2 text-blue-600 hover:text-blue-800"
                >
                  Copy
                </button>
              </div>
              <div v-if="liveClass?.password">
                <span class="font-medium">Password:</span>
                <span class="ml-2 font-mono">{{ liveClass.password }}</span>
                <button
                  @click="copyToClipboard(liveClass.password)"
                  class="ml-2 text-blue-600 hover:text-blue-800"
                >
                  Copy
                </button>
              </div>
            </div>
          </div>

          <button
            @click="showMeetingDetails = !showMeetingDetails"
            class="text-sm text-gray-500 hover:text-gray-700 transition-colors"
          >
            {{ showMeetingDetails ? 'Hide' : 'Show' }} Meeting Details
          </button>
        </div>
      </div>

      <!-- Completed Class State -->
      <div v-else-if="liveClass?.status === 'completed'" class="text-center">
        <div class="mb-6">
          <svg class="w-16 h-16 mx-auto text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h3 class="text-lg font-medium text-gray-900 mb-2">Class Completed</h3>
          <p class="text-gray-600">
            This live class has ended. Check if a recording is available.
          </p>
        </div>

        <div v-if="liveClass?.recording_url" class="space-y-4">
          <button
            @click="watchRecording"
            class="w-full sm:w-auto px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <svg class="w-5 h-5 mr-2 inline" fill="currentColor" viewBox="0 0 20 20">
              <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
              <path fill-rule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clip-rule="evenodd" />
            </svg>
            Watch Recording
          </button>
        </div>
      </div>

      <!-- Cancelled Class State -->
      <div v-else-if="liveClass?.status === 'cancelled'" class="text-center">
        <div class="mb-6">
          <svg class="w-16 h-16 mx-auto text-red-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h3 class="text-lg font-medium text-gray-900 mb-2">Class Cancelled</h3>
          <p class="text-gray-600">
            This live class has been cancelled by the instructor.
          </p>
        </div>
      </div>

      <!-- Connection Status -->
      <div v-if="isConnected" class="mt-6 flex items-center justify-center text-sm text-green-600">
        <div class="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></div>
        Connected to live updates
      </div>
    </div>

    <!-- Toast Notifications -->
    <div v-if="notification" class="fixed top-4 right-4 z-50">
      <div class="bg-white border border-gray-200 rounded-lg shadow-lg p-4 max-w-sm">
        <div class="flex items-start">
          <div class="flex-shrink-0">
            <svg v-if="notification.type === 'success'" class="h-5 w-5 text-green-400" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
            </svg>
            <svg v-else-if="notification.type === 'error'" class="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
            </svg>
            <svg v-else class="h-5 w-5 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="ml-3 flex-1">
            <p class="text-sm font-medium text-gray-900">{{ notification.title }}</p>
            <p class="text-sm text-gray-500">{{ notification.message }}</p>
          </div>
          <button
            @click="notification = null"
            class="ml-4 flex-shrink-0 text-gray-400 hover:text-gray-600"
          >
            <svg class="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useZoom } from '@/composables/useZoom'
// import type { LiveClass } from '@/types/api'

interface Props {
  liveClassId: string
}

const props = defineProps<Props>()

const {
  currentLiveClass: liveClass,
  fetchLiveClass,
  joinZoomMeeting,
  connectWebSocket,
  disconnectWebSocket,
  isConnected,
  // error
} = useZoom()

// Local state
const isJoining = ref(false)
const isTestingConnection = ref(false)
const showMeetingDetails = ref(false)
const notification = ref<{
  type: 'success' | 'error' | 'info'
  title: string
  message: string
} | null>(null)

// Computed properties
const statusClasses = computed(() => {
  switch (liveClass.value?.status) {
    case 'scheduled':
      return 'bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full text-sm font-medium'
    case 'live':
      return 'bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium'
    case 'completed':
      return 'bg-gray-100 text-gray-800 px-3 py-1 rounded-full text-sm font-medium'
    case 'cancelled':
      return 'bg-red-100 text-red-800 px-3 py-1 rounded-full text-sm font-medium'
    default:
      return 'bg-gray-100 text-gray-800 px-3 py-1 rounded-full text-sm font-medium'
  }
})

const statusText = computed(() => {
  switch (liveClass.value?.status) {
    case 'scheduled':
      return 'Scheduled'
    case 'live':
      return 'Live Now'
    case 'completed':
      return 'Completed'
    case 'cancelled':
      return 'Cancelled'
    default:
      return 'Unknown'
  }
})

const timeUntilClass = computed(() => {
  if (!liveClass.value?.scheduled_at) return null
  
  const now = new Date()
  const scheduledTime = new Date(liveClass.value.scheduled_at)
  const diff = scheduledTime.getTime() - now.getTime()
  
  if (diff <= 0) return null
  
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
  
  if (hours > 0) {
    return `Starts in ${hours}h ${minutes}m`
  } else {
    return `Starts in ${minutes}m`
  }
})

const canTestConnection = computed(() => {
  return liveClass.value?.join_url && liveClass.value.status === 'scheduled'
})

// Methods
const formatDateTime = (dateString?: string) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString()
}

const formatMeetingId = (meetingId: string) => {
  // Format meeting ID with spaces for readability
  return meetingId.replace(/(\d{3})(\d{3})(\d{4})/, '$1 $2 $3')
}

const joinClass = async () => {
  if (!liveClass.value?.join_url) return
  
  isJoining.value = true
  
  try {
    joinZoomMeeting(liveClass.value.join_url)
    
    showNotification('success', 'Joining Class', 'Opening Zoom meeting...')
    
    // Mark attendance as present when joining
    // This would typically be handled by Zoom webhooks
    setTimeout(() => {
      isJoining.value = false
    }, 2000)
  } catch (err) {
    console.error('Error joining class:', err)
    showNotification('error', 'Join Failed', 'Failed to join the class. Please try again.')
    isJoining.value = false
  }
}

const testZoomConnection = async () => {
  if (!liveClass.value?.join_url) return
  
  isTestingConnection.value = true
  
  try {
    // Open Zoom test URL
    const testUrl = 'https://zoom.us/test'
    window.open(testUrl, '_blank', 'noopener,noreferrer')
    
    showNotification('info', 'Connection Test', 'Zoom connection test opened in new tab')
  } catch (err) {
    console.error('Error testing connection:', err)
    showNotification('error', 'Test Failed', 'Failed to open connection test')
  } finally {
    isTestingConnection.value = false
  }
}

const joinByPhone = () => {
  if (!liveClass.value?.zoom_meeting_id) return
  
  const phoneNumbers = [
    '+1 669 900 6833',
    '+1 929 205 6099',
    '+1 253 215 8782'
  ]
  
  const phoneInfo = `
Meeting ID: ${liveClass.value.zoom_meeting_id}
${liveClass.value.password ? `Password: ${liveClass.value.password}` : ''}

US Phone Numbers:
${phoneNumbers.join('\n')}
  `.trim()
  
  showNotification('info', 'Phone Join Info', 'Phone numbers copied to clipboard')
  copyToClipboard(phoneInfo)
}

const copyJoinUrl = () => {
  if (liveClass.value?.join_url) {
    copyToClipboard(liveClass.value.join_url)
    showNotification('success', 'URL Copied', 'Join URL copied to clipboard')
  }
}

const watchRecording = () => {
  if (liveClass.value?.recording_url) {
    window.open(liveClass.value.recording_url, '_blank', 'noopener,noreferrer')
  }
}

const copyToClipboard = async (text: string) => {
  try {
    await navigator.clipboard.writeText(text)
  } catch (err) {
    console.error('Failed to copy to clipboard:', err)
    // Fallback for older browsers
    const textArea = document.createElement('textarea')
    textArea.value = text
    document.body.appendChild(textArea)
    textArea.select()
    document.execCommand('copy')
    document.body.removeChild(textArea)
  }
}

const showNotification = (type: 'success' | 'error' | 'info', title: string, message: string) => {
  notification.value = { type, title, message }
  
  // Auto-hide after 5 seconds
  setTimeout(() => {
    notification.value = null
  }, 5000)
}

// Lifecycle
onMounted(async () => {
  await fetchLiveClass(props.liveClassId)
  connectWebSocket(props.liveClassId)
})

onUnmounted(() => {
  disconnectWebSocket()
})
</script>

<style scoped>
.live-class-join-interface {
  @apply max-w-2xl mx-auto;
}

.status-badge {
  @apply inline-flex items-center px-3 py-1 rounded-full text-sm font-medium;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>