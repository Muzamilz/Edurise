import { zoomService } from '@/services/zoom'
import { api } from '@/services/api'

export interface ConnectionTestResult {
  endpoint: string
  status: 'success' | 'error' | 'pending'
  message: string
  responseTime?: number
}

export class ConnectionTester {
  private results: ConnectionTestResult[] = []

  async testBackendConnection(): Promise<ConnectionTestResult[]> {
    this.results = []

    // Test basic API connection
    await this.testEndpoint('API Health Check', async () => {
      const response = await api.get('/api/v1/courses/')
      return response.status === 200
    })

    // Test live classes endpoint
    await this.testEndpoint('Live Classes API', async () => {
      const response = await zoomService.getLiveClasses()
      return response !== null
    })

    // Test attendance endpoint
    await this.testEndpoint('Attendance API', async () => {
      const response = await api.get('/api/v1/classes/attendance/')
      return response.status === 200
    })

    // Test Zoom webhook endpoint
    await this.testEndpoint('Zoom Webhook', async () => {
      const response = await api.post('/api/v1/classes/zoom/webhook/', {
        event: 'test',
        payload: { test: true }
      })
      return response.status === 200
    })

    return this.results
  }

  private async testEndpoint(name: string, testFn: () => Promise<boolean>): Promise<void> {
    const startTime = Date.now()
    
    try {
      const success = await testFn()
      const responseTime = Date.now() - startTime
      
      this.results.push({
        endpoint: name,
        status: success ? 'success' : 'error',
        message: success ? 'Connected successfully' : 'Connection failed',
        responseTime
      })
    } catch (error: any) {
      const responseTime = Date.now() - startTime
      
      this.results.push({
        endpoint: name,
        status: 'error',
        message: error.message || 'Connection failed',
        responseTime
      })
    }
  }

  async testWebSocketConnection(liveClassId: string): Promise<ConnectionTestResult> {
    const startTime = Date.now()
    
    try {
      const { createWebSocketConnection, getWebSocketUrl } = await import('@/services/websocket')
      const wsUrl = getWebSocketUrl(`/ws/live-class/${liveClassId}/`)
      
      const ws = createWebSocketConnection({ url: wsUrl })
      
      return new Promise((resolve) => {
        const timeout = setTimeout(() => {
          resolve({
            endpoint: 'WebSocket Connection',
            status: 'error',
            message: 'Connection timeout',
            responseTime: Date.now() - startTime
          })
        }, 5000)

        ws.onConnect(() => {
          clearTimeout(timeout)
          ws.disconnect()
          resolve({
            endpoint: 'WebSocket Connection',
            status: 'success',
            message: 'WebSocket connected successfully',
            responseTime: Date.now() - startTime
          })
        })

        ws.onError(() => {
          clearTimeout(timeout)
          resolve({
            endpoint: 'WebSocket Connection',
            status: 'error',
            message: 'WebSocket connection failed',
            responseTime: Date.now() - startTime
          })
        })

        ws.connect().catch(() => {
          clearTimeout(timeout)
          resolve({
            endpoint: 'WebSocket Connection',
            status: 'error',
            message: 'Failed to establish WebSocket connection',
            responseTime: Date.now() - startTime
          })
        })
      })
    } catch (error: any) {
      return {
        endpoint: 'WebSocket Connection',
        status: 'error',
        message: error.message || 'WebSocket test failed',
        responseTime: Date.now() - startTime
      }
    }
  }

  getConnectionSummary(): { total: number; success: number; errors: number } {
    return {
      total: this.results.length,
      success: this.results.filter(r => r.status === 'success').length,
      errors: this.results.filter(r => r.status === 'error').length
    }
  }
}

export const connectionTester = new ConnectionTester()