<template>
  <div class="payment-checkout">
    <!-- Payment Method Selection -->
    <div class="payment-methods mb-6">
      <h3 class="text-lg font-semibold mb-4">Select Payment Method</h3>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <button
          v-for="method in paymentMethods"
          :key="method.id"
          @click="selectedMethod = method.id"
          :class="[
            'payment-method-card p-4 border-2 rounded-lg transition-all duration-200',
            selectedMethod === method.id
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-200 hover:border-gray-300'
          ]"
        >
          <div class="flex items-center justify-center mb-2">
            <span class="text-2xl">{{ method.icon }}</span>
          </div>
          <div class="text-center">
            <div class="font-medium">{{ method.name }}</div>
            <div class="text-sm text-gray-500">{{ method.description }}</div>
          </div>
        </button>
      </div>
    </div>

    <!-- Payment Amount Summary -->
    <div class="payment-summary bg-gray-50 p-4 rounded-lg mb-6">
      <div class="flex justify-between items-center mb-2">
        <span class="text-gray-600">Subtotal:</span>
        <span class="font-medium">{{ formatCurrency(amount) }}</span>
      </div>
      <div v-if="taxAmount > 0" class="flex justify-between items-center mb-2">
        <span class="text-gray-600">Tax:</span>
        <span class="font-medium">{{ formatCurrency(taxAmount) }}</span>
      </div>
      <div v-if="discountAmount > 0" class="flex justify-between items-center mb-2">
        <span class="text-green-600">Discount:</span>
        <span class="font-medium text-green-600">-{{ formatCurrency(discountAmount) }}</span>
      </div>
      <hr class="my-2">
      <div class="flex justify-between items-center text-lg font-semibold">
        <span>Total:</span>
        <span>{{ formatCurrency(totalAmount) }}</span>
      </div>
    </div>

    <!-- Payment Forms -->
    <div class="payment-forms">
      <!-- Stripe Payment Form -->
      <StripePaymentForm
        v-if="selectedMethod === 'stripe'"
        :amount="totalAmount"
        :currency="currency"
        :course-id="courseId"
        @payment-success="handlePaymentSuccess"
        @payment-error="handlePaymentError"
        @loading="handleLoadingChange"
      />

      <!-- PayPal Payment Form -->
      <PayPalPaymentForm
        v-else-if="selectedMethod === 'paypal'"
        :amount="totalAmount"
        :currency="currency"
        :course-id="courseId"
        @payment-success="handlePaymentSuccess"
        @payment-error="handlePaymentError"
        @loading="handleLoadingChange"
      />

      <!-- Bank Transfer Form -->
      <BankTransferForm
        v-else-if="selectedMethod === 'bank_transfer'"
        :amount="totalAmount"
        :currency="currency"
        :course-id="courseId"
        @payment-initiated="handleBankTransferInitiated"
        @payment-error="handlePaymentError"
        @loading="handleLoadingChange"
      />
    </div>

    <!-- Loading Overlay -->
    <div
      v-if="loading"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
      <div class="bg-white p-6 rounded-lg shadow-lg">
        <div class="flex items-center space-x-3">
          <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
          <span class="text-gray-700">Processing payment...</span>
        </div>
      </div>
    </div>

    <!-- Error Message -->
    <div
      v-if="error"
      class="error-message bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mt-4"
    >
      <div class="flex items-center">
        <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
        </svg>
        {{ error }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { usePayments } from '../../composables/usePayments'
import { useAnimations } from '../../composables/useAnimations'
import StripePaymentForm from './StripePaymentForm.vue'
import PayPalPaymentForm from './PayPalPaymentForm.vue'
import BankTransferForm from './BankTransferForm.vue'

interface Props {
  courseId?: string
  amount: number
  currency?: string
  taxRate?: number
  discountAmount?: number
}

const props = withDefaults(defineProps<Props>(), {
  currency: 'USD',
  taxRate: 0,
  discountAmount: 0
})

const emit = defineEmits<{
  paymentSuccess: [payment: any]
  paymentError: [error: string]
  paymentInitiated: [details: any]
}>()

const { formatCurrency, loading, error, clearError } = usePayments()
const { fadeIn, slideIn } = useAnimations()

const selectedMethod = ref<string>('stripe')

const paymentMethods = [
  {
    id: 'stripe',
    name: 'Credit/Debit Card',
    description: 'Visa, Mastercard, American Express',
    icon: '💳'
  },
  {
    id: 'paypal',
    name: 'PayPal',
    description: 'Pay with your PayPal account',
    icon: '🅿️'
  },
  {
    id: 'bank_transfer',
    name: 'Bank Transfer',
    description: 'Direct bank transfer (manual approval)',
    icon: '🏦'
  }
]

const taxAmount = computed(() => props.amount * props.taxRate)
const totalAmount = computed(() => props.amount + taxAmount.value - props.discountAmount)

const handlePaymentSuccess = (payment: any) => {
  clearError()
  emit('paymentSuccess', payment)
}

const handlePaymentError = (errorMessage: string) => {
  emit('paymentError', errorMessage)
}

const handleBankTransferInitiated = (details: any) => {
  clearError()
  emit('paymentInitiated', details)
}

const handleLoadingChange = (isLoading: boolean) => {
  loading.value = isLoading
}

onMounted(() => {
  // Animate payment method cards
  fadeIn('.payment-method-card')
  slideIn('.payment-summary', 'right')
})
</script>

<style scoped>
.payment-checkout {
  max-width: 600px;
  margin: 0 auto;
}

.payment-method-card {
  cursor: pointer;
  transform: translateY(0);
  transition: all 0.2s ease;
}

.payment-method-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.payment-method-card.selected {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
}

.payment-summary {
  backdrop-filter: blur(10px);
}

.error-message {
  animation: shake 0.5s ease-in-out;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px); }
  75% { transform: translateX(5px); }
}
</style>