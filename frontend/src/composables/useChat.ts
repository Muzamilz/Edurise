import { ref, computed, onMounted, onUnmounted } from 'vue'
import { NotificationService } from '@/services/notifications'
import { useToast } from '@/composables/useToast'
import type { ChatMessage, WebSocketConnection } from '@/types/api'

export const useChat = (roomName: string) => {
  const toast = useToast()
  
  // State
  const messages = ref<ChatMessage[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const websocket = ref<WebSocket | null>(null)
  const isConnected = ref(false)
  const isTyping = ref(false)
  const typingUsers = ref<Set<string>>(new Set())
  const connectedUsers = ref<Set<string>>(new Set())
  
  // Computed
  const sortedMessages = computed(() => 
    [...messages.value].sort((a, b) => 
      new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
    )
  )
  
  const typingUsersList = computed(() => Array.from(typingUsers.value))
  const connectedUsersList = computed(() => Array.from(connectedUsers.value))
  
  // Methods
  const loadChatHistory = async () => {
    loading.value = true
    error.value = null
    
    try {
      const history = await NotificationService.getChatRoomHistory(roomName)
      messages.value = history
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to load chat history'
      toast.error('Failed to load chat history')
    } finally {
      loading.value = false
    }
  }
  
  const sendMessage = async (content: string) => {
    if (!content.trim()) return
    
    try {
      // Send via API (will also trigger WebSocket broadcast)
      const message = await NotificationService.sendChatMessage(roomName, content.trim())
      
      // Add to local messages if not already there (in case WebSocket is slow)
      if (!messages.value.find(m => m.id === message.id)) {
        messages.value.push(message)
      }
      
      return message
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to send message'
      toast.error('Failed to send message')
      throw err
    }
  }
  
  const editMessage = async (messageId: string, newContent: string) => {
    try {
      const updatedMessage = await NotificationService.editChatMessage(messageId, newContent)
      
      // Update local message
      const index = messages.value.findIndex(m => m.id === messageId)
      if (index !== -1) {
        messages.value[index] = updatedMessage
      }
      
      toast.success('Message edited successfully')
      return updatedMessage
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to edit message'
      toast.error('Failed to edit message')
      throw err
    }
  }
  
  const deleteMessage = async (messageId: string) => {
    try {
      await NotificationService.deleteChatMessage(messageId)
      
      // Remove from local messages
      messages.value = messages.value.filter(m => m.id !== messageId)
      
      toast.success('Message deleted successfully')
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to delete message'
      toast.error('Failed to delete message')
      throw err
    }
  }
  
  const sendTypingIndicator = (typing: boolean) => {
    if (websocket.value && isConnected.value) {
      websocket.value.send(JSON.stringify({
        type: 'typing',
        is_typing: typing
      }))
    }
  }
  
  // WebSocket connection
  const connectWebSocket = () => {
    if (websocket.value) {
      websocket.value.close()
    }
    
    websocket.value = NotificationService.connectChatWebSocket(roomName)
    
    if (websocket.value) {
      websocket.value.addEventListener('open', () => {
        isConnected.value = true
      })
      
      websocket.value.addEventListener('close', () => {
        isConnected.value = false
      })
      
      // Listen for chat events
      window.addEventListener('chatMessage', handleNewMessage as EventListener)
      window.addEventListener('userJoined', handleUserJoined as EventListener)
      window.addEventListener('userLeft', handleUserLeft as EventListener)
      window.addEventListener('userTyping', handleUserTyping as EventListener)
    }
  }
  
  const disconnectWebSocket = () => {
    if (websocket.value) {
      websocket.value.close()
      websocket.value = null
    }
    
    isConnected.value = false
    
    // Remove event listeners
    window.removeEventListener('chatMessage', handleNewMessage as EventListener)
    window.removeEventListener('userJoined', handleUserJoined as EventListener)
    window.removeEventListener('userLeft', handleUserLeft as EventListener)
    window.removeEventListener('userTyping', handleUserTyping as EventListener)
  }
  
  // Event handlers
  const handleNewMessage = (event: CustomEvent) => {
    const message = event.detail
    
    // Add message if not already in list
    if (!messages.value.find(m => m.id === message.id)) {
      messages.value.push(message)
    }
  }
  
  const handleUserJoined = (event: CustomEvent) => {
    const user = event.detail
    connectedUsers.value.add(user.name)
    toast.info(`${user.name} joined the chat`)
  }
  
  const handleUserLeft = (event: CustomEvent) => {
    const user = event.detail
    connectedUsers.value.delete(user.name)
    typingUsers.value.delete(user.name)
    toast.info(`${user.name} left the chat`)
  }
  
  const handleUserTyping = (event: CustomEvent) => {
    const { user, is_typing } = event.detail
    
    if (is_typing) {
      typingUsers.value.add(user.name)
    } else {
      typingUsers.value.delete(user.name)
    }
  }
  
  // Lifecycle
  onMounted(() => {
    loadChatHistory()
    connectWebSocket()
  })
  
  onUnmounted(() => {
    disconnectWebSocket()
  })
  
  return {
    // State
    messages: sortedMessages,
    loading,
    error,
    isConnected,
    isTyping,
    typingUsers: typingUsersList,
    connectedUsers: connectedUsersList,
    
    // Methods
    sendMessage,
    editMessage,
    deleteMessage,
    sendTypingIndicator,
    loadChatHistory,
    connectWebSocket,
    disconnectWebSocket,
    
    // Refresh method
    refresh: loadChatHistory
  }
}

// WebSocket connection monitoring composable
export const useWebSocketMonitoring = () => {
  const connections = ref<WebSocketConnection[]>([])
  const stats = ref({
    total_connections: 0,
    active_connections: 0,
    connections_by_type: {} as Record<string, number>,
    average_connection_duration: 0,
    peak_concurrent_connections: 0,
    recent_connections: [] as WebSocketConnection[]
  })
  const loading = ref(false)
  const error = ref<string | null>(null)
  const toast = useToast()
  
  const fetchConnections = async () => {
    loading.value = true
    error.value = null
    
    try {
      const response = await NotificationService.getWebSocketConnections()
      connections.value = response
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch connections'
      toast.error('Failed to load WebSocket connections')
    } finally {
      loading.value = false
    }
  }
  
  const fetchActiveConnections = async () => {
    try {
      const response = await NotificationService.getActiveWebSocketConnections()
      return response
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch active connections'
      throw err
    }
  }
  
  const fetchConnectionStats = async () => {
    loading.value = true
    error.value = null
    
    try {
      const response = await NotificationService.getWebSocketConnectionStats()
      stats.value = response
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch connection stats'
      toast.error('Failed to load connection statistics')
    } finally {
      loading.value = false
    }
  }
  
  const sendBroadcast = async (message: string, title?: string, priority?: string) => {
    try {
      await NotificationService.sendBroadcastMessage(message, title, priority)
      toast.success('Broadcast message sent successfully')
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to send broadcast'
      toast.error('Failed to send broadcast message')
      throw err
    }
  }
  
  onMounted(() => {
    fetchConnections()
    fetchConnectionStats()
  })
  
  return {
    connections,
    stats,
    loading,
    error,
    fetchConnections,
    fetchActiveConnections,
    fetchConnectionStats,
    sendBroadcast,
    refresh: () => {
      fetchConnections()
      fetchConnectionStats()
    }
  }
}