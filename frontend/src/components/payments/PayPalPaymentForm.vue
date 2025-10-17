<template>
  <div class="paypal-payment-form">
    <div class="mb-4">
      <h4 class="text-lg font-medium mb-2">PayPal Payment</h4>
      <p class="text-sm text-gray-600">Pay securely with your PayPal account</p>
    </div>

    <!-- PayPal Button Container -->
    <div
      ref="paypalButtonContainer"
      class="paypal-button-container mb-4"
    ></div>

    <!-- Alternative: Manual PayPal Flow -->
    <div v-if="showManualFlow" class="manual-paypal-flow">
      <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
        <div class="flex items-center mb-2">
          <svg class="w-5 h-5 text-blue-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
          </svg>
          <span class="font-medium text-blue-800">PayPal Payment Instructions</span>
        </div>
        <p class="text-blue-700 text-sm">
          Click the button below to be redirected to PayPal to complete your payment.
          You'll be brought back here once the payment is complete.
        </p>
      </div>

      <button
        @click="initiatePayPalPayment"
        :disabled="processing"
        :class="[
          'w-full py-3 px-4 rounded-lg font-medium transition-all duration-200',
          processing
            ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
            : 'bg-blue-600 text-white hover:bg-blue-700 transform hover:scale-105'
        ]"
      >
        <div v-if="processing" class="flex items-center justify-center">
          <div class="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
          Creating PayPal order...
        </div>
        <div v-else class="flex items-center justify-center">
          <span class="text-2xl mr-2">🅿️</span>
          Pay with PayPal - {{ formatCurrency(amount, currency) }}
        </div>
      </button>
    </div>

    <!-- Payment Status -->
    <div v-if="paymentStatus" class="payment-status mt-4">
      <div
        v-if="paymentStatus === 'success'"
        class="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg"
      >
        <div class="flex items-center">
          <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
          </svg>
          Payment completed successfully!
        </div>
      </div>
      
      <div
        v-else-if="paymentStatus === 'cancelled'"
        class="bg-yellow-50 border border-yellow-200 text-yellow-700 px-4 py-3 rounded-lg"
      >
        <div class="flex items-center">
          <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
          </svg>
          Payment was cancelled. You can try again.
        </div>
      </div>
    </div>

    <!-- Security Notice -->
    <div class="mt-4 text-center">
      <div class="flex items-center justify-center text-sm text-gray-500">
        <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd" />
        </svg>
        Protected by PayPal Buyer Protection
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { usePayments } from '../../composables/usePayments'
import { useAnimations } from '../../composables/useAnimations'

interface Props {
  amount: number
  currency: string
  courseId?: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  paymentSuccess: [payment: any]
  paymentError: [error: string]
  loading: [isLoading: boolean]
}>()

const { createCoursePayment, formatCurrency } = usePayments()
const { morphButton } = useAnimations()

const paypalButtonContainer = ref<HTMLElement>()
const processing = ref(false)
const paymentStatus = ref<'success' | 'cancelled' | null>(null)
const showManualFlow = ref(false)

let paypal: any = null

const loadPayPal = async () => {
  try {
    // Load PayPal SDK
    if (!(window as any).paypal) {
      const script = document.createElement('script')
      script.src = `https://www.paypal.com/sdk/js?client-id=${import.meta.env.VITE_PAYPAL_CLIENT_ID}&currency=${props.currency}`
      script.async = true
      document.head.appendChild(script)
      
      await new Promise((resolve, reject) => {
        script.onload = resolve
        script.onerror = reject
      })
    }

    paypal = (window as any).paypal

    // Render PayPal button
    await nextTick()
    if (paypalButtonContainer.value && paypal) {
      renderPayPalButton()
    }

  } catch (error) {
    console.error('Failed to load PayPal SDK:', error)
    showManualFlow.value = true
  }
}

const renderPayPalButton = () => {
  if (!paypal || !paypalButtonContainer.value) return

  paypal.Buttons({
    style: {
      layout: 'vertical',
      color: 'blue',
      shape: 'rect',
      label: 'paypal'
    },

    createOrder: async (_data: any, _actions: any) => {
      try {
        emit('loading', true)
        
        const paymentData = await createCoursePayment({
          course_id: props.courseId,
          amount: props.amount,
          payment_method: 'paypal',
          currency: props.currency
        })

        return paymentData.data.order_id
      } catch (error: any) {
        emit('paymentError', error.message || 'Failed to create PayPal order')
        throw error
      } finally {
        emit('loading', false)
      }
    },

    onApprove: async (_data: any, actions: any) => {
      try {
        emit('loading', true)
        processing.value = true

        // Capture the payment
        const details = await actions.order.capture()
        
        paymentStatus.value = 'success'
        
        // Animate success
        morphButton('.paypal-payment-form button')
        
        emit('paymentSuccess', {
          id: details.id,
          amount: details.purchase_units[0].amount.value,
          currency: details.purchase_units[0].amount.currency_code,
          status: details.status,
          payer: details.payer
        })

      } catch (error: any) {
        paymentStatus.value = 'cancelled'
        emit('paymentError', error.message || 'PayPal payment failed')
      } finally {
        processing.value = false
        emit('loading', false)
      }
    },

    onCancel: (_data: any) => {
      paymentStatus.value = 'cancelled'
      emit('paymentError', 'Payment was cancelled')
    },

    onError: (err: any) => {
      console.error('PayPal error:', err)
      emit('paymentError', 'PayPal payment error occurred')
    }

  }).render(paypalButtonContainer.value)
}

const initiatePayPalPayment = async () => {
  if (processing.value) return

  processing.value = true
  emit('loading', true)

  try {
    const paymentData = await createCoursePayment({
      course_id: props.courseId,
      amount: props.amount,
      payment_method: 'paypal',
      currency: props.currency
    })

    // Redirect to PayPal approval URL
    window.location.href = paymentData.data.approval_url

  } catch (error: any) {
    emit('paymentError', error.message || 'Failed to initiate PayPal payment')
  } finally {
    processing.value = false
    emit('loading', false)
  }
}

// Handle return from PayPal
const handlePayPalReturn = () => {
  const urlParams = new URLSearchParams(window.location.search)
  const paymentId = urlParams.get('paymentId')
  const payerId = urlParams.get('PayerID')
  // const token = urlParams.get('token') // Unused for now

  if (paymentId && payerId) {
    // Payment was approved, capture it
    capturePayPalPayment(paymentId, payerId)
  } else if (urlParams.get('cancelled') === 'true') {
    paymentStatus.value = 'cancelled'
  }
}

const capturePayPalPayment = async (paymentId: string, payerId: string) => {
  try {
    emit('loading', true)
    
    // Call backend to capture PayPal payment
    const response = await fetch('/api/payments/capture-paypal/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        payment_id: paymentId,
        payer_id: payerId
      })
    })

    const result = await response.json()

    if (response.ok) {
      paymentStatus.value = 'success'
      emit('paymentSuccess', result)
    } else {
      throw new Error(result.message || 'Failed to capture PayPal payment')
    }

  } catch (error: any) {
    emit('paymentError', error.message || 'Failed to complete PayPal payment')
  } finally {
    emit('loading', false)
  }
}

onMounted(() => {
  loadPayPal()
  handlePayPalReturn()
})

onUnmounted(() => {
  // Cleanup if needed
})
</script>

<style scoped>
.paypal-button-container {
  min-height: 50px;
}

.paypal-payment-form button:hover:not(:disabled) {
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.payment-status {
  animation: slideInUp 0.3s ease-out;
}

@keyframes slideInUp {
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