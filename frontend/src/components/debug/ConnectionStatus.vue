<template>
  <div class="connection-status">
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-medium text-gray-900">Backend Connection Status</h3>
        <button
          @click="runTests"
          :disabled="isRunning"
          class="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 disabled:opacity-50 transition-colors"
        >
          <span v-if="isRunning" class="flex items-center">
            <svg class="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Testing...
          </span>
          <span v-else>Test Connection</span>
        </button>
      </div>

      <!-- Summary -->
      <div v-if="testResults.length > 0" class="mb-6">
        <div class="grid grid-cols-3 gap-4">
          <div class="text-center">
            <div class="text-2xl font-bold text-gray-900">{{ summary.total }}</div>
            <div class="text-sm text-gray-500">Total Tests</div>
          </div>
          <div class="text-center">
            <div class="text-2xl font-bold text-green-600">{{ summary.success }}</div>
            <div class="text-sm text-gray-500">Successful</div>
          </div>
          <div class="text-center">
            <div class="text-2xl font-bold text-red-600">{{ summary.errors }}</div>
            <div class="text-sm text-gray-500">Failed</div>
          </div>
        </div>
      </div>

      <!-- Test Results -->
      <div v-if="testResults.length > 0" class="space-y-3">
        <div
          v-for="result in testResults"
          :key="result.endpoint"
          class="flex items-center justify-between p-3 rounded-lg border"
          :class="getResultClasses(result.status)"
        >
          <div class="flex items-center">
            <div class="flex-shrink-0 mr-3">
              <svg
                v-if="result.status === 'success'"
                class="w-5 h-5 text-green-500"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
              </svg>
              <svg
                v-else-if="result.status === 'error'"
                class="w-5 h-5 text-red-500"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
              </svg>
              <svg
                v-else
                class="w-5 h-5 text-yellow-500 animate-spin"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </div>
            <div>
              <div class="font-medium text-gray-900">{{ result.endpoint }}</div>
              <div class="text-sm text-gray-500">{{ result.message }}</div>
            </div>
          </div>
          <div v-if="result.responseTime" class="text-sm text-gray-500">
            {{ result.responseTime }}ms
          </div>
        </div>
      </div>

      <!-- WebSocket Test -->
      <div v-if="showWebSocketTest" class="mt-6 pt-6 border-t border-gray-200">
        <div class="flex items-center justify-between mb-4">
          <h4 class="font-medium text-gray-900">WebSocket Connection</h4>
          <div class="flex items-center space-x-2">
            <input
              v-model="testLiveClassId"
              type="text"
              placeholder="Live Class ID"
              class="px-3 py-1 text-sm border border-gray-300 rounded-md"
            />
            <button
              @click="testWebSocket"
              :disabled="isTestingWebSocket || !testLiveClassId"
              class="px-3 py-1 bg-purple-600 text-white text-sm font-medium rounded-md hover:bg-purple-700 disabled:opacity-50"
            >
              Test WS
            </button>
          </div>
        </div>
        
        <div v-if="webSocketResult" class="p-3 rounded-lg border" :class="getResultClasses(webSocketResult.status)">
          <div class="flex items-center justify-between">
            <div class="flex items-center">
              <div class="flex-shrink-0 mr-3">
                <svg
                  v-if="webSocketResult.status === 'success'"
                  class="w-5 h-5 text-green-500"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                </svg>
                <svg
                  v-else
                  class="w-5 h-5 text-red-500"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                </svg>
              </div>
              <div>
                <div class="font-medium text-gray-900">{{ webSocketResult.endpoint }}</div>
                <div class="text-sm text-gray-500">{{ webSocketResult.message }}</div>
              </div>
            </div>
            <div v-if="webSocketResult.responseTime" class="text-sm text-gray-500">
              {{ webSocketResult.responseTime }}ms
            </div>
          </div>
        </div>
      </div>

      <!-- Connection Guide -->
      <div class="mt-6 pt-6 border-t border-gray-200">
        <h4 class="font-medium text-gray-900 mb-3">Connection Requirements</h4>
        <div class="text-sm text-gray-600 space-y-2">
          <div class="flex items-start">
            <div class="w-2 h-2 bg-blue-500 rounded-full mt-2 mr-3 flex-shrink-0"></div>
            <div>
              <strong>Backend Server:</strong> Django server running on port 8000
              <div class="text-xs text-gray-500 mt-1">
                Start with: <code class="bg-gray-100 px-1 rounded">python manage.py runserver</code>
              </div>
            </div>
          </div>
          <div class="flex items-start">
            <div class="w-2 h-2 bg-green-500 rounded-full mt-2 mr-3 flex-shrink-0"></div>
            <div>
              <strong>Database:</strong> Migrations applied and database accessible
              <div class="text-xs text-gray-500 mt-1">
                Run: <code class="bg-gray-100 px-1 rounded">python manage.py migrate</code>
              </div>
            </div>
          </div>
          <div class="flex items-start">
            <div class="w-2 h-2 bg-purple-500 rounded-full mt-2 mr-3 flex-shrink-0"></div>
            <div>
              <strong>WebSocket:</strong> Channels/WebSocket server for real-time updates
              <div class="text-xs text-gray-500 mt-1">
                Optional for basic functionality
              </div>
            </div>
          </div>
          <div class="flex items-start">
            <div class="w-2 h-2 bg-orange-500 rounded-full mt-2 mr-3 flex-shrink-0"></div>
            <div>
              <strong>CORS:</strong> Cross-origin requests enabled for frontend
              <div class="text-xs text-gray-500 mt-1">
                Check CORS_ALLOWED_ORIGINS in Django settings
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { connectionTester, type ConnectionTestResult } from '@/utils/connectionTest'

// State
const isRunning = ref(false)
const isTestingWebSocket = ref(false)
const testResults = ref<ConnectionTestResult[]>([])
const webSocketResult = ref<ConnectionTestResult | null>(null)
const testLiveClassId = ref('')
const showWebSocketTest = ref(true)

// Computed
const summary = computed(() => {
  return {
    total: testResults.value.length,
    success: testResults.value.filter(r => r.status === 'success').length,
    errors: testResults.value.filter(r => r.status === 'error').length
  }
})

// Methods
const runTests = async () => {
  isRunning.value = true
  testResults.value = []
  
  try {
    testResults.value = await connectionTester.testBackendConnection()
  } catch (error) {
    console.error('Connection test failed:', error)
  } finally {
    isRunning.value = false
  }
}

const testWebSocket = async () => {
  if (!testLiveClassId.value) return
  
  isTestingWebSocket.value = true
  webSocketResult.value = null
  
  try {
    webSocketResult.value = await connectionTester.testWebSocketConnection(testLiveClassId.value)
  } catch (error) {
    console.error('WebSocket test failed:', error)
    webSocketResult.value = {
      endpoint: 'WebSocket Connection',
      status: 'error',
      message: 'Test failed with error'
    }
  } finally {
    isTestingWebSocket.value = false
  }
}

const getResultClasses = (status: string) => {
  switch (status) {
    case 'success':
      return 'bg-green-50 border-green-200'
    case 'error':
      return 'bg-red-50 border-red-200'
    case 'pending':
      return 'bg-yellow-50 border-yellow-200'
    default:
      return 'bg-gray-50 border-gray-200'
  }
}
</script>

<style scoped>
.connection-status {
  @apply max-w-4xl mx-auto;
}

code {
  @apply font-mono text-xs;
}
</style>