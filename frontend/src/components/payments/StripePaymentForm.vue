<template>
  <div class="stripe-payment-form">
    <div class="mb-4">
      <h4 class="text-lg font-medium mb-2">Credit/Debit Card Payment</h4>
      <p class="text-sm text-gray-600">Your payment is secured by Stripe</p>
    </div>

    <!-- Card Element Container -->
    <div class="card-element-container mb-4">
      <div
        ref="cardElement"
        class="card-element p-3 border border-gray-300 rounded-lg bg-white"
      ></div>
    </div>

    <!-- Billing Information -->
    <div class="billing-info mb-4">
      <h5 class="font-medium mb-3">Billing Information</h5>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Full Name *
          </label>
          <input
            v-model="billingInfo.name"
            type="text"
            required
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="John Doe"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Email *
          </label>
          <input
            v-model="billingInfo.email"
            type="email"
            required
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="john@example.com"
          />
        </div>
        <div class="md:col-span-2">
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Address
          </label>
          <input
            v-model="billingInfo.address"
            type="text"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="123 Main St"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            City
          </label>
          <input
            v-model="billingInfo.city"
            type="text"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="New York"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Postal Code
          </label>
          <input
            v-model="billingInfo.postalCode"
            type="text"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="10001"
          />
        </div>
      </div>
    </div>

    <!-- Save Payment Method -->
    <div class="mb-4">
      <label class="flex items-center">
        <input
          v-model="savePaymentMethod"
          type="checkbox"
          class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
        />
        <span class="ml-2 text-sm text-gray-700">
          Save payment method for future purchases
        </span>
      </label>
    </div>

    <!-- Payment Button -->
    <button
      @click="processPayment"
      :disabled="processing || !isFormValid"
      :class="[
        'w-full py-3 px-4 rounded-lg font-medium transition-all duration-200',
        processing || !isFormValid
          ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
          : 'bg-blue-600 text-white hover:bg-blue-700 transform hover:scale-105'
      ]"
    >
      <div v-if="processing" class="flex items-center justify-center">
        <div class="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
        Processing...
      </div>
      <div v-else class="flex items-center justify-center">
        <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
        </svg>
        Pay {{ formatCurrency(amount, currency) }}
      </div>
    </button>

    <!-- Security Notice -->
    <div class="mt-4 text-center">
      <div class="flex items-center justify-center text-sm text-gray-500">
        <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd" />
        </svg>
        Secured by 256-bit SSL encryption
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
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

// Stripe elements
const cardElement = ref<HTMLElement>()
let stripe: any = null
let elements: any = null
let card: any = null

const processing = ref(false)
const savePaymentMethod = ref(false)

const billingInfo = ref({
  name: '',
  email: '',
  address: '',
  city: '',
  postalCode: ''
})

const isFormValid = computed(() => {
  return billingInfo.value.name.trim() !== '' && 
         billingInfo.value.email.trim() !== '' &&
         billingInfo.value.email.includes('@')
})

const loadStripe = async () => {
  try {
    // Load Stripe.js
    if (!(window as any).Stripe) {
      const script = document.createElement('script')
      script.src = 'https://js.stripe.com/v3/'
      script.async = true
      document.head.appendChild(script)
      
      await new Promise((resolve) => {
        script.onload = resolve
      })
    }

    // Initialize Stripe
    stripe = (window as any).Stripe(import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY)
    elements = stripe.elements()

    // Create card element
    card = elements.create('card', {
      style: {
        base: {
          fontSize: '16px',
          color: '#424770',
          '::placeholder': {
            color: '#aab7c4',
          },
        },
        invalid: {
          color: '#9e2146',
        },
      },
    })

    // Mount card element
    await nextTick()
    if (cardElement.value) {
      card.mount(cardElement.value)
    }

    // Handle card changes
    card.on('change', (event: any) => {
      if (event.error) {
        emit('paymentError', event.error.message)
      }
    })

  } catch (error) {
    console.error('Failed to load Stripe:', error)
    emit('paymentError', 'Failed to load payment system')
  }
}

const processPayment = async () => {
  if (!stripe || !card || !isFormValid.value) return

  processing.value = true
  emit('loading', true)

  try {
    // Create payment intent
    const paymentData = await createCoursePayment({
      course_id: props.courseId,
      amount: props.amount,
      payment_method: 'stripe',
      currency: props.currency
    })

    // Confirm payment with Stripe
    const { error, paymentIntent } = await stripe.confirmCardPayment(
      paymentData.data.client_secret,
      {
        payment_method: {
          card: card,
          billing_details: {
            name: billingInfo.value.name,
            email: billingInfo.value.email,
            address: {
              line1: billingInfo.value.address,
              city: billingInfo.value.city,
              postal_code: billingInfo.value.postalCode,
            },
          },
        },
        setup_future_usage: savePaymentMethod.value ? 'off_session' : undefined,
      }
    )

    if (error) {
      throw new Error(error.message)
    }

    if (paymentIntent.status === 'succeeded') {
      // Animate success
      morphButton('.stripe-payment-form button')
      
      emit('paymentSuccess', {
        id: paymentIntent.id,
        amount: paymentIntent.amount,
        currency: paymentIntent.currency,
        status: paymentIntent.status
      })
    }

  } catch (error: any) {
    emit('paymentError', error.message || 'Payment failed')
  } finally {
    processing.value = false
    emit('loading', false)
  }
}

onMounted(() => {
  loadStripe()
})

onUnmounted(() => {
  if (card) {
    card.destroy()
  }
})
</script>

<style scoped>
.card-element {
  min-height: 40px;
}

.card-element:focus-within {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.stripe-payment-form button:hover:not(:disabled) {
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}
</style>