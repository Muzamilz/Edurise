export interface WebSocketMessage {
  type: string
  data: any
  timestamp: string
  tenant_id?: string
  user_id?: string
}

export interface WebSocketConfig {
  url: string
  reconnectInterval?: number
  maxReconnectAttempts?: number
  heartbeatInterval?: number
  authToken?: string
  tenantId?: string
  enableReconnect?: boolean
  debug?: boolean
}

export interface ConnectionStatus {
  isConnected: boolean
  isConnecting: boolean
  lastConnected?: Date
  lastDisconnected?: Date
  reconnectAttempts: number
  error?: string
}

export class WebSocketService {
  private ws: WebSocket | null = null
  private config: WebSocketConfig
  private reconnectAttempts = 0
  private heartbeatTimer: number | null = null
  private reconnectTimer: number | null = null
  private isConnecting = false
  private isDestroyed = false
  private messageHandlers = new Map<string, ((data: any) => void)[]>()
  private connectionHandlers: (() => void)[] = []
  private disconnectionHandlers: (() => void)[] = []
  private errorHandlers: ((error: Event) => void)[] = []
  private statusChangeHandlers: ((status: ConnectionStatus) => void)[] = []
  private connectionStatus: ConnectionStatus = {
    isConnected: false,
    isConnecting: false,
    reconnectAttempts: 0
  }

  constructor(config: WebSocketConfig) {
    this.config = {
      reconnectInterval: 5000,
      maxReconnectAttempts: 5,
      heartbeatInterval: 30000,
      enableReconnect: true,
      debug: false,
      ...config
    }
    
    // Add authentication token to URL if provided
    if (this.config.authToken) {
      const separator = this.config.url.includes('?') ? '&' : '?'
      this.config.url += `${separator}token=${this.config.authToken}`
    }
    
    // Add tenant ID to URL if provided
    if (this.config.tenantId) {
      const separator = this.config.url.includes('?') ? '&' : '?'
      this.config.url += `${separator}tenant=${this.config.tenantId}`
    }
  }

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.isDestroyed) {
        reject(new Error('WebSocket service has been destroyed'))
        return
      }

      if (this.ws?.readyState === WebSocket.OPEN) {
        resolve()
        return
      }

      if (this.isConnecting) {
        reject(new Error('Connection already in progress'))
        return
      }

      this.updateConnectionStatus({
        isConnecting: true,
        isConnected: false,
        error: undefined
      })

      try {
        this.ws = new WebSocket(this.config.url)

        const connectionTimeout = setTimeout(() => {
          if (this.ws?.readyState === WebSocket.CONNECTING) {
            this.ws.close()
            this.updateConnectionStatus({
              isConnecting: false,
              isConnected: false,
              error: 'Connection timeout'
            })
            reject(new Error('WebSocket connection timeout'))
          }
        }, 10000) // 10 second timeout

        this.ws.onopen = () => {
          clearTimeout(connectionTimeout)
          this.log('WebSocket connected to:', this.config.url)
          
          this.updateConnectionStatus({
            isConnecting: false,
            isConnected: true,
            lastConnected: new Date(),
            reconnectAttempts: 0,
            error: undefined
          })
          
          this.startHeartbeat()
          this.connectionHandlers.forEach(handler => {
            try {
              handler()
            } catch (error) {
              console.error('Error in connection handler:', error)
            }
          })
          resolve()
        }

        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data)
            
            // Handle heartbeat responses
            if (message.type === 'pong') {
              this.log('Received heartbeat response')
              return
            }
            
            this.handleMessage(message)
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error)
          }
        }

        this.ws.onclose = (event) => {
          clearTimeout(connectionTimeout)
          this.log('WebSocket disconnected:', event.code, event.reason)
          
          this.updateConnectionStatus({
            isConnecting: false,
            isConnected: false,
            lastDisconnected: new Date(),
            error: event.wasClean ? undefined : `Connection closed: ${event.reason || 'Unknown reason'}`
          })
          
          this.stopHeartbeat()
          this.disconnectionHandlers.forEach(handler => {
            try {
              handler()
            } catch (error) {
              console.error('Error in disconnection handler:', error)
            }
          })

          if (!event.wasClean && !this.isDestroyed && this.shouldReconnect()) {
            this.scheduleReconnect()
          }
        }

        this.ws.onerror = (error) => {
          clearTimeout(connectionTimeout)
          console.error('WebSocket error:', error)
          
          this.updateConnectionStatus({
            isConnecting: false,
            isConnected: false,
            error: 'WebSocket connection error'
          })
          
          this.errorHandlers.forEach(handler => {
            try {
              handler(error)
            } catch (handlerError) {
              console.error('Error in error handler:', handlerError)
            }
          })
          reject(error)
        }
      } catch (error) {
        this.updateConnectionStatus({
          isConnecting: false,
          isConnected: false,
          error: error instanceof Error ? error.message : 'Unknown error'
        })
        reject(error)
      }
    })
  }

  disconnect(): void {
    this.isDestroyed = false // Allow reconnection after manual disconnect
    this.clearReconnectTimer()
    
    if (this.ws) {
      this.ws.close(1000, 'Client disconnect')
      this.ws = null
    }
    this.stopHeartbeat()
    
    this.updateConnectionStatus({
      isConnecting: false,
      isConnected: false,
      lastDisconnected: new Date()
    })
  }

  destroy(): void {
    this.isDestroyed = true
    this.clearReconnectTimer()
    this.disconnect()
    
    // Clear all handlers
    this.messageHandlers.clear()
    this.connectionHandlers = []
    this.disconnectionHandlers = []
    this.errorHandlers = []
    this.statusChangeHandlers = []
  }

  send(type: string, data: any): boolean {
    if (this.ws?.readyState === WebSocket.OPEN) {
      try {
        const message: WebSocketMessage = {
          type,
          data,
          timestamp: new Date().toISOString(),
          tenant_id: this.config.tenantId,
          user_id: this.getCurrentUserId()
        }
        this.ws.send(JSON.stringify(message))
        this.log('Sent message:', type, data)
        return true
      } catch (error) {
        console.error('Failed to send WebSocket message:', error)
        return false
      }
    } else {
      console.warn('WebSocket not connected, cannot send message:', type)
      return false
    }
  }

  subscribe(messageType: string, handler: (data: any) => void): () => void {
    if (!this.messageHandlers.has(messageType)) {
      this.messageHandlers.set(messageType, [])
    }
    this.messageHandlers.get(messageType)!.push(handler)

    // Return unsubscribe function
    return () => {
      const handlers = this.messageHandlers.get(messageType)
      if (handlers) {
        const index = handlers.indexOf(handler)
        if (index > -1) {
          handlers.splice(index, 1)
        }
      }
    }
  }

  onConnect(handler: () => void): () => void {
    this.connectionHandlers.push(handler)
    return () => {
      const index = this.connectionHandlers.indexOf(handler)
      if (index > -1) {
        this.connectionHandlers.splice(index, 1)
      }
    }
  }

  onDisconnect(handler: () => void): () => void {
    this.disconnectionHandlers.push(handler)
    return () => {
      const index = this.disconnectionHandlers.indexOf(handler)
      if (index > -1) {
        this.disconnectionHandlers.splice(index, 1)
      }
    }
  }

  onError(handler: (error: Event) => void): () => void {
    this.errorHandlers.push(handler)
    return () => {
      const index = this.errorHandlers.indexOf(handler)
      if (index > -1) {
        this.errorHandlers.splice(index, 1)
      }
    }
  }

  onStatusChange(handler: (status: ConnectionStatus) => void): () => void {
    this.statusChangeHandlers.push(handler)
    // Immediately call with current status
    handler(this.connectionStatus)
    return () => {
      const index = this.statusChangeHandlers.indexOf(handler)
      if (index > -1) {
        this.statusChangeHandlers.splice(index, 1)
      }
    }
  }

  get isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN
  }

  get readyState(): number | undefined {
    return this.ws?.readyState
  }

  get status(): ConnectionStatus {
    return { ...this.connectionStatus }
  }

  getConnectionHealth(): {
    status: 'healthy' | 'degraded' | 'unhealthy'
    details: string
    lastHeartbeat?: Date
  } {
    if (!this.isConnected) {
      return {
        status: 'unhealthy',
        details: this.connectionStatus.error || 'Not connected'
      }
    }

    if (this.reconnectAttempts > 0) {
      return {
        status: 'degraded',
        details: `Recently reconnected (${this.reconnectAttempts} attempts)`
      }
    }

    return {
      status: 'healthy',
      details: 'Connection stable'
    }
  }

  private handleMessage(message: WebSocketMessage): void {
    const handlers = this.messageHandlers.get(message.type)
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(message.data)
        } catch (error) {
          console.error('Error in message handler:', error)
        }
      })
    }
  }

  private shouldReconnect(): boolean {
    return this.config.enableReconnect !== false && 
           this.reconnectAttempts < (this.config.maxReconnectAttempts || 5)
  }

  private scheduleReconnect(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
    }

    this.reconnectAttempts++
    const baseDelay = this.config.reconnectInterval || 5000
    const delay = Math.min(baseDelay * Math.pow(2, this.reconnectAttempts - 1), 30000) // Max 30 seconds

    this.log(`Scheduling reconnect attempt ${this.reconnectAttempts} in ${delay}ms`)

    this.updateConnectionStatus({
      reconnectAttempts: this.reconnectAttempts
    })

    this.reconnectTimer = window.setTimeout(() => {
      if (!this.isConnected && !this.isDestroyed) {
        this.log(`Attempting reconnect ${this.reconnectAttempts}/${this.config.maxReconnectAttempts}`)
        this.connect().catch(error => {
          console.error('Reconnect failed:', error)
          if (this.shouldReconnect()) {
            this.scheduleReconnect()
          } else {
            this.updateConnectionStatus({
              error: 'Max reconnection attempts reached'
            })
          }
        })
      }
    }, delay)
  }

  private clearReconnectTimer(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }
  }

  private startHeartbeat(): void {
    if (this.config.heartbeatInterval && this.config.heartbeatInterval > 0) {
      this.heartbeatTimer = window.setInterval(() => {
        if (this.isConnected) {
          this.send('ping', { timestamp: Date.now() })
        } else {
          this.stopHeartbeat()
        }
      }, this.config.heartbeatInterval)
    }
  }

  private stopHeartbeat(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer)
      this.heartbeatTimer = null
    }
  }

  private updateConnectionStatus(updates: Partial<ConnectionStatus>): void {
    this.connectionStatus = {
      ...this.connectionStatus,
      ...updates
    }
    
    // Update internal state
    this.isConnecting = this.connectionStatus.isConnecting
    this.reconnectAttempts = this.connectionStatus.reconnectAttempts
    
    // Notify status change handlers
    this.statusChangeHandlers.forEach(handler => {
      try {
        handler(this.connectionStatus)
      } catch (error) {
        console.error('Error in status change handler:', error)
      }
    })
  }

  private getCurrentUserId(): string | undefined {
    // This would typically come from your auth store
    // For now, return undefined - can be enhanced later
    return undefined
  }

  private log(...args: any[]): void {
    if (this.config.debug) {
      console.log('[WebSocket]', ...args)
    }
  }
}

// Enhanced WebSocket Manager for handling multiple connections
export class WebSocketManager {
  private connections = new Map<string, WebSocketService>()
  private globalStatusHandlers: ((status: Record<string, ConnectionStatus>) => void)[] = []

  createConnection(id: string, config: WebSocketConfig): WebSocketService {
    if (this.connections.has(id)) {
      this.connections.get(id)?.destroy()
    }

    const service = new WebSocketService(config)
    
    // Monitor connection status changes
    service.onStatusChange((_status) => {
      this.notifyGlobalStatusChange()
    })

    this.connections.set(id, service)
    return service
  }

  getConnection(id: string): WebSocketService | undefined {
    return this.connections.get(id)
  }

  removeConnection(id: string): void {
    const connection = this.connections.get(id)
    if (connection) {
      connection.destroy()
      this.connections.delete(id)
      this.notifyGlobalStatusChange()
    }
  }

  getAllConnections(): Record<string, WebSocketService> {
    return Object.fromEntries(this.connections)
  }

  getConnectionStatuses(): Record<string, ConnectionStatus> {
    const statuses: Record<string, ConnectionStatus> = {}
    this.connections.forEach((service, id) => {
      statuses[id] = service.status
    })
    return statuses
  }

  onGlobalStatusChange(handler: (statuses: Record<string, ConnectionStatus>) => void): () => void {
    this.globalStatusHandlers.push(handler)
    // Immediately call with current statuses
    handler(this.getConnectionStatuses())
    return () => {
      const index = this.globalStatusHandlers.indexOf(handler)
      if (index > -1) {
        this.globalStatusHandlers.splice(index, 1)
      }
    }
  }

  private notifyGlobalStatusChange(): void {
    const statuses = this.getConnectionStatuses()
    this.globalStatusHandlers.forEach(handler => {
      try {
        handler(statuses)
      } catch (error) {
        console.error('Error in global status change handler:', error)
      }
    })
  }

  destroy(): void {
    this.connections.forEach(connection => connection.destroy())
    this.connections.clear()
    this.globalStatusHandlers = []
  }
}

// Global WebSocket manager instance
export const websocketManager = new WebSocketManager()

// Factory function for creating WebSocket connections
export const createWebSocketConnection = (config: WebSocketConfig): WebSocketService => {
  return new WebSocketService(config)
}

// Utility function to get WebSocket URL from environment
export const getWebSocketUrl = (path: string): string => {
  const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const wsHost = import.meta.env.VITE_WS_HOST || window.location.host
  return `${wsProtocol}//${wsHost}${path}`
}

// Utility function to get authenticated WebSocket URL
export const getAuthenticatedWebSocketUrl = (path: string, token?: string, tenantId?: string): string => {
  let url = getWebSocketUrl(path)
  const params = new URLSearchParams()
  
  if (token) {
    params.append('token', token)
  }
  
  if (tenantId) {
    params.append('tenant', tenantId)
  }
  
  if (params.toString()) {
    url += `?${params.toString()}`
  }
  
  return url
}