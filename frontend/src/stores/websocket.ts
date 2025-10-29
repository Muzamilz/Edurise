import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { 
  WebSocketService, 
  // WebSocketManager, // Unused
  websocketManager,
  getAuthenticatedWebSocketUrl,
  type ConnectionStatus,
  type WebSocketConfig 
} from '@/services/websocket'
import { useAuthStore } from '@/stores/auth'

interface WebSocketConnection {
  id: string
  service: WebSocketService
  config: WebSocketConfig
  autoReconnect: boolean
}

export const useWebSocketStore = defineStore('websocket', () => {
  // State
  const connections = ref<Record<string, WebSocketConnection>>({})
  const globalStatus = ref<Record<string, ConnectionStatus>>({})
  const isInitialized = ref(false)

  // Computed
  const isAnyConnected = computed(() => 
    Object.values(globalStatus.value).some(status => status.isConnected)
  )

  const isAllConnected = computed(() => 
    Object.keys(connections.value).length > 0 &&
    Object.values(globalStatus.value).every(status => status.isConnected)
  )

  const connectionCount = computed(() => Object.keys(connections.value).length)

  const healthyConnections = computed(() => 
    Object.entries(globalStatus.value).filter(([_, status]) => status.isConnected).length
  )

  // Actions
  const initialize = () => {
    if (isInitialized.value) return

    // Set up global status monitoring
    websocketManager.onGlobalStatusChange((statuses) => {
      globalStatus.value = statuses
    })

    isInitialized.value = true
  }

  const createConnection = (
    id: string, 
    path: string, 
    options: Partial<WebSocketConfig> = {}
  ): WebSocketService => {
    const authStore = useAuthStore()
    
    const config: WebSocketConfig = {
      url: getAuthenticatedWebSocketUrl(
        path, 
        authStore.accessToken || undefined, 
        authStore.currentTenant?.id
      ),
      reconnectInterval: 5000,
      maxReconnectAttempts: 5,
      heartbeatInterval: 30000,
      enableReconnect: true,
      debug: import.meta.env.DEV,
      ...options
    }

    const service = websocketManager.createConnection(id, config)
    
    connections.value[id] = {
      id,
      service,
      config,
      autoReconnect: options.enableReconnect !== false
    }

    return service
  }

  const getConnection = (id: string): WebSocketService | undefined => {
    return connections.value[id]?.service
  }

  const removeConnection = (id: string) => {
    if (connections.value[id]) {
      websocketManager.removeConnection(id)
      delete connections.value[id]
    }
  }

  const connectAll = async () => {
    const promises = Object.values(connections.value).map(async (conn) => {
      try {
        await conn.service.connect()
      } catch (error) {
        console.error(`Failed to connect WebSocket ${conn.id}:`, error)
      }
    })

    await Promise.allSettled(promises)
  }

  const disconnectAll = () => {
    Object.values(connections.value).forEach(conn => {
      conn.service.disconnect()
    })
  }

  const destroyAll = () => {
    Object.keys(connections.value).forEach(id => {
      removeConnection(id)
    })
    websocketManager.destroy()
    globalStatus.value = {}
  }

  const reconnectConnection = async (id: string) => {
    const connection = connections.value[id]
    if (connection) {
      try {
        await connection.service.connect()
      } catch (error) {
        console.error(`Failed to reconnect WebSocket ${id}:`, error)
        throw error
      }
    }
  }

  const getConnectionStatus = (id: string): ConnectionStatus | undefined => {
    return globalStatus.value[id]
  }

  const getConnectionHealth = (id: string) => {
    const connection = connections.value[id]
    return connection?.service.getConnectionHealth()
  }

  // Setup default connections
  const setupDefaultConnections = () => {
    const authStore = useAuthStore()
    
    if (!authStore.isAuthenticated) {
      console.warn('Cannot setup WebSocket connections: user not authenticated')
      return
    }

    // Notifications WebSocket
    createConnection('notifications', '/ws/notifications/', {
      heartbeatInterval: 30000,
      maxReconnectAttempts: 10
    })

    // Chat WebSocket (if needed)
    // createConnection('chat', '/ws/chat/general/', {
    //   heartbeatInterval: 60000
    // })
  }

  const connectDefaultConnections = async () => {
    setupDefaultConnections()
    await connectAll()
  }

  // Connection management utilities
  const isConnectionHealthy = (id: string): boolean => {
    const status = globalStatus.value[id]
    return status?.isConnected && !status.error
  }

  const getUnhealthyConnections = (): string[] => {
    return Object.entries(globalStatus.value)
      .filter(([_, status]) => !status.isConnected || status.error)
      .map(([id]) => id)
  }

  const retryUnhealthyConnections = async () => {
    const unhealthy = getUnhealthyConnections()
    
    const promises = unhealthy.map(async (id) => {
      try {
        await reconnectConnection(id)
      } catch (error) {
        console.error(`Failed to retry connection ${id}:`, error)
      }
    })

    await Promise.allSettled(promises)
  }

  // Live class specific connection
  const connectToLiveClass = (liveClassId: string): WebSocketService => {
    const connectionId = `live-class-${liveClassId}`
    
    return createConnection(
      connectionId,
      `/ws/live-class/${liveClassId}/`,
      {
        heartbeatInterval: 15000, // More frequent for live classes
        maxReconnectAttempts: 20   // More attempts for critical connections
      }
    )
  }

  const disconnectFromLiveClass = (liveClassId: string) => {
    const connectionId = `live-class-${liveClassId}`
    removeConnection(connectionId)
  }

  // Instructor live class connection
  const connectToInstructorLiveClass = (liveClassId: string): WebSocketService => {
    const connectionId = `instructor-live-class-${liveClassId}`
    
    return createConnection(
      connectionId,
      `/ws/live-class/${liveClassId}/instructor/`,
      {
        heartbeatInterval: 10000, // Very frequent for instructor dashboard
        maxReconnectAttempts: 30   // Maximum attempts for instructor
      }
    )
  }

  const disconnectFromInstructorLiveClass = (liveClassId: string) => {
    const connectionId = `instructor-live-class-${liveClassId}`
    removeConnection(connectionId)
  }

  // Debug utilities
  const getDebugInfo = () => {
    return {
      connections: Object.keys(connections.value),
      statuses: globalStatus.value,
      isInitialized: isInitialized.value,
      healthyCount: healthyConnections.value,
      totalCount: connectionCount.value
    }
  }

  return {
    // State
    connections: computed(() => connections.value),
    globalStatus: computed(() => globalStatus.value),
    isInitialized: computed(() => isInitialized.value),

    // Computed
    isAnyConnected,
    isAllConnected,
    connectionCount,
    healthyConnections,

    // Actions
    initialize,
    createConnection,
    getConnection,
    removeConnection,
    connectAll,
    disconnectAll,
    destroyAll,
    reconnectConnection,
    getConnectionStatus,
    getConnectionHealth,
    setupDefaultConnections,
    connectDefaultConnections,
    isConnectionHealthy,
    getUnhealthyConnections,
    retryUnhealthyConnections,
    connectToLiveClass,
    disconnectFromLiveClass,
    connectToInstructorLiveClass,
    disconnectFromInstructorLiveClass,
    getDebugInfo
  }
})