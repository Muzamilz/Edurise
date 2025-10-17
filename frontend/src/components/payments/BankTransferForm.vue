<template>
  <div class="bank-transfer-form">
    <div class="mb-4">
      <h4 class="text-lg font-medium mb-2">Bank Transfer Payment</h4>
      <p class="text-sm text-gray-600">
        Manual bank transfer requires approval from our team
      </p>
    </div>

    <!-- Bank Transfer Instructions -->
    <div class="bank-instructions bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
      <h5 class="font-medium text-blue-800 mb-3">Payment Instructions</h5>
      <div class="space-y-2 text-sm text-blue-700">
        <div class="flex justify-between">
          <span class="font-medium">Bank Name:</span>
          <span>{{ bankDetails.bank_name }}</span>
        </div>
        <div class="flex justify-between">
          <span class="font-medium">Account Name:</span>
          <span>{{ bankDetails.account_name }}</span>
        </div>
        <div class="flex justify-between">
          <span class="font-medium">Account Number:</span>
          <span class="font-mono">{{ bankDetails.account_number }}</span>
        </div>
        <div class="flex justify-between">
          <span class="font-medium">Routing Number:</span>
          <span class="font-mono">{{ bankDetails.routing_number }}</span>
        </div>
        <div v-if="bankDetails.swift_code" class="flex justify-between">
          <span class="font-medium">SWIFT Code:</span>
          <span class="font-mono">{{ bankDetails.swift_code }}</span>
        </div>
        <div class="flex justify-between">
          <span class="font-medium">Reference Number:</span>
          <span class="font-mono font-bold text-red-600">{{ referenceNumber }}</span>
        </div>
        <div class="flex justify-between">
          <span class="font-medium">Amount:</span>
          <span class="font-bold">{{ formatCurrency(amount, currency) }}</span>
        </div>
      </div>
    </div>

    <!-- Important Notice -->
    <div class="important-notice bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
      <div class="flex items-start">
        <svg class="w-5 h-5 text-yellow-600 mr-2 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
        </svg>
        <div class="text-yellow-800">
          <p class="font-medium mb-1">Important Instructions:</p>
          <ul class="text-sm space-y-1">
            <li>• Include the reference number in your transfer description</li>
            <li>• Transfer the exact amount shown above</li>
            <li>• Your enrollment will be activated after payment verification</li>
            <li>• Verification typically takes 1-3 business days</li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Transfer Confirmation Form -->
    <div class="transfer-confirmation mb-6">
      <h5 class="font-medium mb-3">Transfer Confirmation</h5>
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Transfer Date *
          </label>
          <input
            v-model="transferDetails.date"
            type="date"
            required
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Transfer Amount *
          </label>
          <input
            v-model="transferDetails.amount"
            type="number"
            step="0.01"
            required
            :placeholder="amount.toString()"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Bank Reference/Transaction ID
          </label>
          <input
            v-model="transferDetails.bankReference"
            type="text"
            placeholder="Enter your bank's transaction reference"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Additional Notes
          </label>
          <textarea
            v-model="transferDetails.notes"
            rows="3"
            placeholder="Any additional information about your transfer"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          ></textarea>
        </div>
      </div>
    </div>

    <!-- Submit Button -->
    <button
      @click="submitBankTransfer"
      :disabled="processing || !isFormValid"
      :class="[
        'w-full py-3 px-4 rounded-lg font-medium transition-all duration-200',
        processing || !isFormValid
          ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
          : 'bg-green-600 text-white hover:bg-green-700 transform hover:scale-105'
      ]"
    >
      <div v-if="processing" class="flex items-center justify-center">
        <div class="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
        Submitting...
      </div>
      <div v-else class="flex items-center justify-center">
        <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        Submit Transfer Details
      </div>
    </button>

    <!-- Copy Bank Details Button -->
    <button
      @click="copyBankDetails"
      class="w-full mt-3 py-2 px-4 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors duration-200"
    >
      <div class="flex items-center justify-center">
        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
        </svg>
        Copy Bank Details
      </div>
    </button>

    <!-- Success Message -->
    <div
      v-if="submitted"
      class="success-message bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg mt-4"
    >
      <div class="flex items-center">
        <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
        </svg>
        <div>
          <p class="font-medium">Transfer details submitted successfully!</p>
          <p class="text-sm mt-1">We'll verify your payment and activate your enrollment within 1-3 business days.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { usePayments } from '../../composables/usePayments'
import { useAnimations } from '../../composables/useAnimations'

interface Props {
  amount: number
  currency: string
  courseId?: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  paymentInitiated: [details: any]
  paymentError: [error: string]
  loading: [isLoading: boolean]
}>()

const { createCoursePayment, formatCurrency } = usePayments()
const { morphButton } = useAnimations()

const processing = ref(false)
const submitted = ref(false)
const referenceNumber = ref('')

const bankDetails = ref({
  bank_name: 'EduRise Bank',
  account_name: 'EduRise LMS Platform',
  account_number: '1234567890',
  routing_number: '021000021',
  swift_code: 'EDURISEUS33'
})

const transferDetails = ref({
  date: '',
  amount: props.amount,
  bankReference: '',
  notes: ''
})

const isFormValid = computed(() => {
  return transferDetails.value.date !== '' && 
         transferDetails.value.amount > 0 &&
         Math.abs(transferDetails.value.amount - props.amount) < 0.01
})

const generateReferenceNumber = () => {
  const timestamp = Date.now().toString().slice(-8)
  const random = Math.random().toString(36).substring(2, 6).toUpperCase()
  return `BT-${timestamp}-${random}`
}

const submitBankTransfer = async () => {
  if (!isFormValid.value || processing.value) return

  processing.value = true
  emit('loading', true)

  try {
    const paymentData = await createCoursePayment({
      course_id: props.courseId,
      amount: props.amount,
      payment_method: 'bank_transfer',
      currency: props.currency
    })

    // Animate success
    morphButton('.bank-transfer-form button')
    
    submitted.value = true
    
    emit('paymentInitiated', {
      reference_number: referenceNumber.value,
      bank_details: bankDetails.value,
      transfer_details: transferDetails.value,
      payment_id: paymentData.data.payment_id
    })

  } catch (error: any) {
    emit('paymentError', error.message || 'Failed to submit bank transfer details')
  } finally {
    processing.value = false
    emit('loading', false)
  }
}

const copyBankDetails = async () => {
  const details = `
Bank Name: ${bankDetails.value.bank_name}
Account Name: ${bankDetails.value.account_name}
Account Number: ${bankDetails.value.account_number}
Routing Number: ${bankDetails.value.routing_number}
SWIFT Code: ${bankDetails.value.swift_code}
Reference Number: ${referenceNumber.value}
Amount: ${formatCurrency(props.amount, props.currency)}
  `.trim()

  try {
    await navigator.clipboard.writeText(details)
    // Could add a toast notification here
  } catch (err) {
    console.error('Failed to copy bank details:', err)
  }
}

onMounted(() => {
  referenceNumber.value = generateReferenceNumber()
  
  // Set default transfer date to today
  const today = new Date().toISOString().split('T')[0]
  transferDetails.value.date = today
})
</script>

<style scoped>
.bank-transfer-form button:hover:not(:disabled) {
  box-shadow: 0 4px 12px rgba(34, 197, 94, 0.3);
}

.success-message {
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