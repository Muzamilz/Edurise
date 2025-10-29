<template>
  <div class="user-status-indicator">
    <!-- Single User Status -->
    <div v-if="!showList" class="flex items-center space-x-2">
      <div class="relative">
        <div class="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
          <span class="text-sm font-medium text-gray-700">
            {{ getInitials(user?.name || '') }}
          </span>
        </div>
        <div 
          class="absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full border-2 border-white"
          :class="getStatusClasses(user?.status || 'offline')"
        ></div>
      </div>
      <div v-if="showName" class="flex flex-col">
        <span class="text-sm font-medium text-gray-900">{{ user?.name }}</span>
        <span class="text-xs text-gray-500">{{ getStatusText(user?.status || 'offline') }}</span>
      </div>
    </div>

    <!-- User List with Status -->
    <div v-else class="user-status-list">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-semibold text-gray-900">
          {{ title || 'Online Users' }}
        </h3>
        <div class="flex items-center space-x-2">
          <div class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
          <span class="text-sm text-gray-600">{{ onlineCount }} online</span>
        </div>
      </div>

      <!-- Status Filter -->
      <div v-if="showFilter" class="mb-4">
        <div class="flex space-x-2">
          <button
            v-for="status in statusFilters"
            :key="status.value"
            @click="activeFilter = status.value"
            class="px-3 py-1 text-sm rounded-full border transition-colors"
            :class="activeFilter === status.value 
              ? 'bg-blue-50 border-blue-200 text-blue-700' 
              : 'bg-white border-gray-200 text-gray-600 hover:bg-gray-50'"
          >
            <div class="flex items-center space-x-1">
              <div 
                class="w-2 h-2 rounded-full"
                :class="getStatusClasses(status.value)"
              ></div>
              <span>{{ status.label }}</span>
              <span class="text-xs opacity-75">({{ getStatusCount(status.value) }})</span>
            </div>
          </button>
        </div>
      </div>

      <!-- Users List -->
      <div class="space-y-2 max-h-64 overflow-y-auto">
        <div 
          v-for="user in filteredUsers" 
          :key="user.id"
          class="flex items-center justify-between p-3 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
        >
          <div class="flex items-center space-x-3">
            <div class="relative">
              <div class="w-10 h-10 bg-gray-300 rounded-full flex items-center justify-center">
                <span class="text-sm font-medium text-gray-700">
                  {{ getInitials(user.name) }}
                </span>
              </div>
              <div 
                class="absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full border-2 border-white"
                :class="getStatusClasses(user.status)"
              ></div>
            </div>
            <div>
              <p class="text-sm font-medium text-gray-900">{{ user.name }}</p>
              <p class="text-xs text-gray-500">{{ user.role || 'Student' }}</p>
            </div>
          </div>
          <div class="flex items-center space-x-2">
            <span 
              class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium"
              :class="getStatusBadgeClasses(user.status)"
            >
              {{ getStatusText(user.status) }}
            </span>
            <div v-if="user.lastSeen && user.status === 'offline'" class="text-xs text-gray-400">
              {{ formatLastSeen(user.lastSeen) }}
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="filteredUsers.length === 0" class="text-center py-8">
        <div class="w-12 h-12 mx-auto bg-gray-100 rounded-full flex items-center justify-center mb-3">
          <span class="text-2xl text-gray-400">👥</span>
        </div>
        <p class="text-sm text-gray-500">No users {{ activeFilter !== 'all' ? getStatusText(activeFilter).toLowerCase() : 'found' }}</p>
      </div>
    </div>

    <!-- Real-time Activity Feed -->
    <div v-if="showActivity && recentActivity.length > 0" class="mt-6">
      <h4 class="text-sm font-medium text-gray-900 mb-3">Recent Activity</h4>
      <div class="space-y-2">
        <div 
          v-for="activity in recentActivity.slice(0, 5)" 
          :key="activity.id"
          class="flex items-center space-x-2 text-xs text-gray-600 p-2 bg-gray-50 rounded"
        >
          <div 
            class="w-2 h-2 rounded-full"
            :class="getActivityTypeClasses(activity.type)"
          ></div>
          <span>{{ activity.message }}</span>
          <span class="text-gray-400">{{ formatTimeAgo(activity.timestamp) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
// import { UserGroupIcon } from '@heroicons/vue/24/outline'
import { useWebSocketStore } from '@/stores/websocket'

interface User {
  id: string
  name: string
  status: 'online' | 'away' | 'busy' | 'offline'
  role?: string
  lastSeen?: string
}

interface Activity {
  id: string
  type: 'join' | 'leave' | 'status_change'
  message: string
  timestamp: string
}

interface Props {
  user?: User
  users?: User[]
  showList?: boolean
  showName?: boolean
  showFilter?: boolean
  showActivity?: boolean
  title?: string
  autoUpdate?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showList: false,
  showName: true,
  showFilter: true,
  showActivity: true,
  autoUpdate: true
})

const websocketStore = useWebSocketStore()

// State
const activeFilter = ref('all')
const recentActivity = ref<Activity[]>([])
const userStatuses = ref<Record<string, User>>(
  props.users?.reduce((acc, user) => {
    acc[user.id] = user
    return acc
  }, {} as Record<string, User>) || {}
)

// WebSocket connection
let statusWs: any = null

const statusFilters = [
  { value: 'all', label: 'All' },
  { value: 'online', label: 'Online' },
  { value: 'away', label: 'Away' },
  { value: 'busy', label: 'Busy' },
  { value: 'offline', label: 'Offline' }
]

// Computed
const allUsers = computed(() => Object.values(userStatuses.value))

const filteredUsers = computed(() => {
  if (activeFilter.value === 'all') {
    return allUsers.value.sort((a, b) => {
      // Sort by status priority: online > away > busy > offline
      const statusPriority: Record<string, number> = { online: 4, away: 3, busy: 2, offline: 1 }
      return (statusPriority[b.status] || 0) - (statusPriority[a.status] || 0)
    })
  }
  return allUsers.value.filter(user => user.status === activeFilter.value)
})

const onlineCount = computed(() => 
  allUsers.value.filter(user => user.status !== 'offline').length
)

const getStatusCount = (status: string) => {
  if (status === 'all') return allUsers.value.length
  return allUsers.value.filter(user => user.status === status).length
}

// Methods
const getInitials = (name: string) => {
  return name.split(' ').map(n => n.charAt(0)).join('').toUpperCase().slice(0, 2)
}

const getStatusClasses = (status: string) => {
  switch (status) {
    case 'online':
      return 'bg-green-500'
    case 'away':
      return 'bg-yellow-500'
    case 'busy':
      return 'bg-red-500'
    case 'offline':
    default:
      return 'bg-gray-400'
  }
}

const getStatusBadgeClasses = (status: string) => {
  switch (status) {
    case 'online':
      return 'bg-green-100 text-green-800'
    case 'away':
      return 'bg-yellow-100 text-yellow-800'
    case 'busy':
      return 'bg-red-100 text-red-800'
    case 'offline':
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

const getStatusText = (status: string) => {
  switch (status) {
    case 'online':
      return 'Online'
    case 'away':
      return 'Away'
    case 'busy':
      return 'Busy'
    case 'offline':
    default:
      return 'Offline'
  }
}

const getActivityTypeClasses = (type: string) => {
  switch (type) {
    case 'join':
      return 'bg-green-500'
    case 'leave':
      return 'bg-red-500'
    case 'status_change':
      return 'bg-blue-500'
    default:
      return 'bg-gray-500'
  }
}

const formatTimeAgo = (dateString: string) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60))
  
  if (diffInMinutes < 1) {
    return 'now'
  } else if (diffInMinutes < 60) {
    return `${diffInMinutes}m`
  } else if (diffInMinutes < 1440) {
    const hours = Math.floor(diffInMinutes / 60)
    return `${hours}h`
  } else {
    const days = Math.floor(diffInMinutes / 1440)
    return `${days}d`
  }
}

const formatLastSeen = (dateString: string) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60))
  
  if (diffInMinutes < 60) {
    return `${diffInMinutes}m ago`
  } else if (diffInMinutes < 1440) {
    const hours = Math.floor(diffInMinutes / 60)
    return `${hours}h ago`
  } else {
    const days = Math.floor(diffInMinutes / 1440)
    return `${days}d ago`
  }
}

const addActivity = (type: 'join' | 'leave' | 'status_change', message: string) => {
  recentActivity.value.unshift({
    id: Date.now().toString(),
    type,
    message,
    timestamp: new Date().toISOString()
  })
  
  // Keep only last 20 activities
  if (recentActivity.value.length > 20) {
    recentActivity.value = recentActivity.value.slice(0, 20)
  }
}

const updateUserStatus = (userId: string, status: string, userData?: Partial<User>) => {
  const existingUser = userStatuses.value[userId]
  
  if (existingUser) {
    const oldStatus = existingUser.status
    userStatuses.value[userId] = {
      ...existingUser,
      status: status as User['status'],
      ...userData
    }
    
    if (oldStatus !== status) {
      addActivity('status_change', `${existingUser.name} is now ${getStatusText(status).toLowerCase()}`)
    }
  } else if (userData) {
    userStatuses.value[userId] = {
      id: userId,
      status: status as User['status'],
      ...userData
    } as User
    
    if (status !== 'offline') {
      addActivity('join', `${userData.name} joined`)
    }
  }
}

// const removeUser = (userId: string) => {
//   const user = userStatuses.value[userId]
//   if (user) {
//     addActivity('leave', `${user.name} left`)
//     delete userStatuses.value[userId]
//   }
// }

// WebSocket setup
const connectToUserStatus = () => {
  if (!props.autoUpdate) return
  
  statusWs = websocketStore.getConnection('notifications')
  
  if (statusWs) {
    statusWs.subscribe('user_status_update', (data: any) => {
      updateUserStatus(data.user_id, data.status, {
        name: data.user_name,
        role: data.user_role
      })
    })

    statusWs.subscribe('user_joined', (data: any) => {
      updateUserStatus(data.user_id, 'online', {
        name: data.user_name,
        role: data.user_role
      })
    })

    statusWs.subscribe('user_left', (data: any) => {
      updateUserStatus(data.user_id, 'offline', {
        lastSeen: new Date().toISOString()
      })
    })
  }
}

// Lifecycle
onMounted(() => {
  connectToUserStatus()
})

onUnmounted(() => {
  // Cleanup handled by WebSocket store
})
</script>

<style scoped>
.user-status-indicator {
  @apply w-full;
}

.user-status-list {
  @apply bg-white rounded-lg border border-gray-200 p-4;
}
</style>