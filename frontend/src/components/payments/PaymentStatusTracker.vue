<template>
  <div class="payment-status-tracker">
    <!-- Header -->
    <div class="tracker-header mb-6">
      <h3 class="text-lg font-semibold text-gray-900 mb-2">Payment Status</h3>
      <p class="text-gray-600">Track your payment progress</p>
    </div>

    <!-- Status Steps -->
    <div class="status-steps">
      <div class="flex items-center justify-between mb-8">
        <div
          v-for="(step, index) in steps"
          :key="step.id"
          class="flex flex-col items-center relative"
          :class="{ 'flex-1': index < steps.length - 1 }"
        >
          <!-- Step Circle -->
          <div
            :class="[
              'w-10 h-10 rounded-full flex items-center justify-center border-2 transition-all duration-300',
              getStepClasses(step.status)
            ]"
          >
            <svg
              v-if="step.status === 'completed'"
              class="w-5 h-5 text-white"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
            </svg>
            <svg
              v-else-if="step.status === 'failed'"
              class="w-5 h-5 text-white"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
            </svg>
            <div
              v-else-if="step.status === 'processing'"
              class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"
            ></div>
            <span
              v-else
              class="text-sm font-medium"
            >
              {{ index + 1 }}
            </span>
          </div>

          <!-- Step Label -->
          <div class="mt-2 text-center">
            <div
              :class="[
                'text-sm font-medium',
                step.status === 'completed' || step.status === 'processing'
                  ? 'text-gray-900'
                  : step.status === 'failed'
                  ? 'text-red-600'
                  : 'text-gray-500'
              ]"
            >
              {{ step.title }}
            </div>
            <div
              v-if="step.timestamp"
              class="text-xs text-gray-500 mt-1"
            >
              {{ formatTime(step.timestamp) }}
            </div>
          </div>

          <!-- Connecting Line -->
          <div
            v-if="index < steps.length - 1"
            :class="[
              'absolute top-5 left-full w-full h-0.5 transition-all duration-300',
              step.status === 'completed'
                ? 'bg-green-500'
                : 'bg-gray-300'
            ]"
            style="transform: translateX(-50%); z-index: -1;"
          ></div>
        </div>
      </div>
    </div>

    <!-- Current Status Details -->
    <div class="status-details bg-gray-50 rounded-lg p-4 mb-6">
      <div class="flex items-start space-x-3">
        <div
          :class="[
            'flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center',
            getCurrentStatusColor()
          ]"
        >
          <svg
            v-if="currentStep?.status === 'completed'"
            class="w-4 h-4"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
          </svg>
          <svg
            v-else-if="currentStep?.status === 'failed'"
            class="w-4 h-4"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
          </svg>
          <div
            v-else-if="currentStep?.status === 'processing'"
            class="w-3 h-3 border-2 border-current border-t-transparent rounded-full animate-spin"
          ></div>
          <svg
            v-else
            class="w-4 h-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        
        <div class="flex-1">
          <h4 class="font-medium text-gray-900">{{ currentStep?.title }}</h4>
          <p class="text-sm text-gray-600 mt-1">{{ currentStep?.description }}</p>
          
          <!-- Error Message -->
          <div
            v-if="currentStep?.status === 'failed' && currentStep?.error"
            class="mt-2 text-sm text-red-600 bg-red-50 border border-red-200 rounded p-2"
          >
            {{ currentStep.error }}
          </div>
          
          <!-- Estimated Time -->
          <div
            v-if="currentStep?.status === 'processing' && currentStep?.estimatedTime"
            class="mt-2 text-sm text-blue-600"
          >
            Estimated time: {{ currentStep.estimatedTime }}
          </div>
        </div>
      </div>
    </div>

    <!-- Payment Information -->
    <div v-if="payment" class="payment-info bg-white border border-gray-200 rounded-lg p-4">
      <h4 class="font-medium text-gray-900 mb-3">Payment Details</h4>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
        <div>
          <span class="text-gray-600">Payment ID:</span>
          <span class="font-medium ml-2">{{ payment.id }}</span>
        </div>
        <div>
          <span class="text-gray-600">Amount:</span>
          <span class="font-medium ml-2">{{ formatCurrency(payment.amount, payment.currency) }}</span>
        </div>
        <div>
          <span class="text-gray-600">Method:</span>
          <span class="font-medium ml-2 capitalize">{{ payment.payment_method.replace('_', ' ') }}</span>
        </div>
        <div>
          <span class="text-gray-600">Status:</span>
          <span
            :class="[
              'ml-2 px-2 py-1 rounded-full text-xs font-medium',
              getPaymentStatusColor(payment.status)
            ]"
          >
            {{ payment.status.charAt(0).toUpperCase() + payment.status.slice(1) }}
          </span>
        </div>
      </div>
    </div>

    <!-- Action Buttons -->
    <div v-if="showActions" class="actions mt-6 flex space-x-3">
      <button
        v-if="currentStep?.status === 'failed'"
        @click="retryPayment"
        class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
      >
        Retry Payment
      </button>
      
      <button
        v-if="canCancel"
        @click="cancelPayment"
        class="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors"
      >
        Cancel Payment
      </button>
      
      <button
        @click="refreshStatus"
        :disabled="refreshing"
        class="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition-colors disabled:opacity-50"
      >
        <div v-if="refreshing" class="flex items-center">
          <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
          Refreshing...
        </div>
        <span v-else>Refresh Status</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { usePayments } from '../../composables/usePayments'
import type { Payment } from '../../types/payments'

interface PaymentStep {
  id: string
  title: string
  description: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  timestamp?: string
  error?: string
  estimatedTime?: string
}

interface Props {
  paymentId?: string
  payment?: Payment
  showActions?: boolean
  autoRefresh?: boolean
  refreshInterval?: number
}

const props = withDefaults(defineProps<Props>(), {
  showActions: true,
  autoRefresh: true,
  refreshInterval: 5000
})

const emit = defineEmits<{
  statusChanged: [status: string]
  paymentCompleted: [payment: Payment]
  paymentFailed: [error: string]
  retryRequested: []
  cancelRequested: []
}>()

const { fetchPayment, formatCurrency } = usePayments()

const refreshing = ref(false)
let refreshTimer: NodeJS.Timeout | null = null

const steps = ref<PaymentStep[]>([
  {
    id: 'initiated',
    title: 'Payment Initiated',
    description: 'Payment request has been created',
    status: 'completed',
    timestamp: new Date().toISOString()
  },
  {
    id: 'processing',
    title: 'Processing Payment',
    description: 'Your payment is being processed by the payment provider',
    status: 'processing',
    estimatedTime: '1-2 minutes'
  },
  {
    id: 'verification',
    title: 'Verification',
    description: 'Payment is being verified and confirmed',
    status: 'pending'
  },
  {
    id: 'completed',
    title: 'Payment Complete',
    description: 'Payment has been successfully processed',
    status: 'pending'
  }
])

const payment = ref<Payment | null>(props.payment || null)

const currentStep = computed(() => {
  return steps.value.find(step => 
    step.status === 'processing' || 
    (step.status === 'failed' && !steps.value.some(s => s.status === 'processing'))
  ) || steps.value[steps.value.length - 1]
})

const canCancel = computed(() => {
  return payment.value?.status === 'pending' || payment.value?.status === 'processing'
})

const getStepClasses = (status: string) => {
  switch (status) {
    case 'completed':
      return 'bg-green-500 border-green-500 text-white'
    case 'processing':
      return 'bg-blue-500 border-blue-500 text-white'
    case 'failed':
      return 'bg-red-500 border-red-500 text-white'
    default:
      return 'bg-white border-gray-300 text-gray-500'
  }
}

const getCurrentStatusColor = () => {
  switch (currentStep.value?.status) {
    case 'completed':
      return 'bg-green-100 text-green-600'
    case 'processing':
      return 'bg-blue-100 text-blue-600'
    case 'failed':
      return 'bg-red-100 text-red-600'
    default:
      return 'bg-gray-100 text-gray-600'
  }
}

const getPaymentStatusColor = (status: string) => {
  const colors = {
    pending: 'text-yellow-600 bg-yellow-100',
    processing: 'text-blue-600 bg-blue-100',
    completed: 'text-green-600 bg-green-100',
    failed: 'text-red-600 bg-red-100',
    cancelled: 'text-gray-600 bg-gray-100',
    refunded: 'text-purple-600 bg-purple-100'
  }
  return colors[status as keyof typeof colors] || 'text-gray-600 bg-gray-100'
}

const formatTime = (timestamp: string) => {
  return new Date(timestamp).toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

const updateStepsFromPayment = (paymentData: Payment) => {
  const status = paymentData.status
  
  // Reset all steps to pending first
  steps.value.forEach(step => {
    if (step.status !== 'completed') {
      step.status = 'pending'
    }
  })

  switch (status) {
    case 'pending':
      steps.value[0].status = 'completed'
      steps.value[1].status = 'processing'
      break
    case 'processing':
      steps.value[0].status = 'completed'
      steps.value[1].status = 'completed'
      steps.value[1].timestamp = new Date().toISOString()
      steps.value[2].status = 'processing'
      break
    case 'completed':
      steps.value.forEach((step) => {
        step.status = 'completed'
        if (!step.timestamp) {
          step.timestamp = paymentData.completed_at || new Date().toISOString()
        }
      })
      emit('paymentCompleted', paymentData)
      break
    case 'failed':
      steps.value[0].status = 'completed'
      const failedStepIndex = steps.value.findIndex(s => s.status === 'processing') || 1
      steps.value[failedStepIndex].status = 'failed'
      steps.value[failedStepIndex].error = 'Payment processing failed. Please try again.'
      steps.value[failedStepIndex].timestamp = paymentData.failed_at || new Date().toISOString()
      emit('paymentFailed', 'Payment processing failed')
      break
  }

  emit('statusChanged', status)
}

const refreshStatus = async () => {
  if (!props.paymentId && !payment.value) return

  refreshing.value = true
  try {
    const paymentData = await fetchPayment(props.paymentId || payment.value!.id)
    payment.value = paymentData.data
    updateStepsFromPayment(paymentData.data)
  } catch (error) {
    console.error('Failed to refresh payment status:', error)
  } finally {
    refreshing.value = false
  }
}

const retryPayment = () => {
  emit('retryRequested')
}

const cancelPayment = () => {
  emit('cancelRequested')
}

const startAutoRefresh = () => {
  if (props.autoRefresh && !refreshTimer) {
    refreshTimer = setInterval(() => {
      if (payment.value?.status === 'pending' || payment.value?.status === 'processing') {
        refreshStatus()
      }
    }, props.refreshInterval)
  }
}

const stopAutoRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
}

onMounted(async () => {
  if (props.paymentId && !payment.value) {
    await refreshStatus()
  } else if (payment.value) {
    updateStepsFromPayment(payment.value)
  }
  
  startAutoRefresh()
})

onUnmounted(() => {
  stopAutoRefresh()
})
</script>

<style scoped>
.payment-status-tracker {
  max-width: 600px;
}

.status-steps {
  position: relative;
}

.tracker-header {
  animation: fadeInUp 0.6s ease-out;
}

.status-steps {
  animation: fadeInUp 0.6s ease-out 0.1s both;
}

.status-details {
  animation: fadeInUp 0.6s ease-out 0.2s both;
}

.payment-info {
  animation: fadeInUp 0.6s ease-out 0.3s both;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>