<template>
  <div v-if="show" class="payment-modal-overlay" @click="closeModal">
    <div class="payment-modal" @click.stop>
      <div class="modal-header">
        <h3>Complete Your Enrollment</h3>
        <button @click="closeModal" class="close-btn">×</button>
      </div>
      
      <div class="modal-content">
        <!-- Course Summary -->
        <div class="course-summary">
          <div class="course-info">
            <img :src="course.thumbnail || '/placeholder-course.jpg'" :alt="course.title" class="course-image" />
            <div class="course-details">
              <h4>{{ course.title }}</h4>
              <p class="instructor">by {{ course.instructor.first_name }} {{ course.instructor.last_name }}</p>
              <div class="price">
                <span class="amount">${{ course.price }}</span>
                <span class="currency">USD</span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Payment Method Selection -->
        <div class="payment-methods">
          <h4>Choose Payment Method</h4>
          <div class="method-options">
            <label class="method-option" :class="{ active: selectedMethod === 'stripe' }">
              <input 
                type="radio" 
                value="stripe" 
                v-model="selectedMethod"
                name="paymentMethod"
              />
              <div class="method-content">
                <div class="method-icon">💳</div>
                <div class="method-info">
                  <span class="method-name">Credit/Debit Card</span>
                  <span class="method-description">Visa, Mastercard, American Express</span>
                </div>
              </div>
            </label>
            
            <label class="method-option" :class="{ active: selectedMethod === 'paypal' }">
              <input 
                type="radio" 
                value="paypal" 
                v-model="selectedMethod"
                name="paymentMethod"
              />
              <div class="method-content">
                <div class="method-icon">🅿️</div>
                <div class="method-info">
                  <span class="method-name">PayPal</span>
                  <span class="method-description">Pay with your PayPal account</span>
                </div>
              </div>
            </label>
            
            <label class="method-option" :class="{ active: selectedMethod === 'bank_transfer' }">
              <input 
                type="radio" 
                value="bank_transfer" 
                v-model="selectedMethod"
                name="paymentMethod"
              />
              <div class="method-content">
                <div class="method-icon">🏦</div>
                <div class="method-info">
                  <span class="method-name">Bank Transfer</span>
                  <span class="method-description">Manual approval required</span>
                </div>
              </div>
            </label>
          </div>
        </div>
        
        <!-- Stripe Payment Form -->
        <div v-if="selectedMethod === 'stripe'" class="payment-form">
          <div class="form-group">
            <label>Card Number</label>
            <input 
              type="text" 
              v-model="stripeData.cardNumber"
              placeholder="1234 5678 9012 3456"
              class="form-input"
              @input="formatCardNumber"
            />
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label>Expiry Date</label>
              <input 
                type="text" 
                v-model="stripeData.expiryDate"
                placeholder="MM/YY"
                class="form-input"
                @input="formatExpiryDate"
              />
            </div>
            <div class="form-group">
              <label>CVC</label>
              <input 
                type="text" 
                v-model="stripeData.cvc"
                placeholder="123"
                class="form-input"
                maxlength="4"
              />
            </div>
          </div>
          
          <div class="form-group">
            <label>Cardholder Name</label>
            <input 
              type="text" 
              v-model="stripeData.cardholderName"
              placeholder="John Doe"
              class="form-input"
            />
          </div>
        </div>
        
        <!-- PayPal Payment Info -->
        <div v-if="selectedMethod === 'paypal'" class="payment-info">
          <div class="info-card">
            <div class="info-icon">ℹ️</div>
            <div class="info-text">
              <p>You will be redirected to PayPal to complete your payment securely.</p>
            </div>
          </div>
        </div>
        
        <!-- Bank Transfer Info -->
        <div v-if="selectedMethod === 'bank_transfer'" class="payment-info">
          <div class="info-card">
            <div class="info-icon">⏳</div>
            <div class="info-text">
              <p>Bank transfer payments require manual verification and may take 1-3 business days to process.</p>
              <p>You will receive bank details and a reference number after confirming your enrollment.</p>
            </div>
          </div>
        </div>
        
        <!-- Error Display -->
        <div v-if="error" class="error-message">
          <div class="error-icon">⚠️</div>
          <span>{{ error }}</span>
        </div>
        
        <!-- Payment Actions -->
        <div class="payment-actions">
          <button @click="closeModal" class="btn btn-outline">
            Cancel
          </button>
          <button 
            @click="processPayment" 
            class="btn btn-primary"
            :disabled="processing || !isFormValid"
          >
            {{ processing ? 'Processing...' : getPaymentButtonText() }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useEnrollment } from '../../composables/useEnrollment'

interface Props {
  show: boolean
  course: {
    id: string
    title: string
    price: number
    thumbnail?: string
    instructor: {
      first_name: string
      last_name: string
    }
  }
}

interface Emits {
  (e: 'close'): void
  (e: 'success'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const { 
  processPayment: enrollmentProcessPayment,
  createStripePayment,
  createPayPalOrder,
  initiateBankTransfer,
  enrolling: processing
} = useEnrollment()

// Local state
const selectedMethod = ref<'stripe' | 'paypal' | 'bank_transfer'>('stripe')
const error = ref<string | null>(null)

const stripeData = ref({
  cardNumber: '',
  expiryDate: '',
  cvc: '',
  cardholderName: ''
})

// Computed
const isFormValid = computed(() => {
  if (selectedMethod.value === 'stripe') {
    return stripeData.value.cardNumber.length >= 16 &&
           stripeData.value.expiryDate.length === 5 &&
           stripeData.value.cvc.length >= 3 &&
           stripeData.value.cardholderName.trim().length > 0
  }
  return true
})

// Methods
const closeModal = () => {
  emit('close')
  resetForm()
}

const resetForm = () => {
  selectedMethod.value = 'stripe'
  error.value = null
  stripeData.value = {
    cardNumber: '',
    expiryDate: '',
    cvc: '',
    cardholderName: ''
  }
}

const formatCardNumber = (event: Event) => {
  const input = event.target as HTMLInputElement
  let value = input.value.replace(/\s/g, '').replace(/[^0-9]/gi, '')
  const formattedValue = value.match(/.{1,4}/g)?.join(' ') || value
  stripeData.value.cardNumber = formattedValue
}

const formatExpiryDate = (event: Event) => {
  const input = event.target as HTMLInputElement
  let value = input.value.replace(/\D/g, '')
  if (value.length >= 2) {
    value = value.substring(0, 2) + '/' + value.substring(2, 4)
  }
  stripeData.value.expiryDate = value
}

const getPaymentButtonText = () => {
  switch (selectedMethod.value) {
    case 'stripe':
      return `Pay $${props.course.price}`
    case 'paypal':
      return 'Continue with PayPal'
    case 'bank_transfer':
      return 'Get Bank Details'
    default:
      return 'Continue'
  }
}

const processPayment = async () => {
  error.value = null
  
  try {
    switch (selectedMethod.value) {
      case 'stripe':
        await processStripePayment()
        break
      case 'paypal':
        await processPayPalPayment()
        break
      case 'bank_transfer':
        await processBankTransfer()
        break
    }
    
    emit('success')
    closeModal()
    
  } catch (err: any) {
    error.value = err.message || 'Payment processing failed. Please try again.'
  }
}

const processStripePayment = async () => {
  // In a real implementation, you would use Stripe.js here
  // This is a simplified version for demonstration
  
  const paymentIntent = await createStripePayment(props.course.id, props.course.price)
  
  // Simulate Stripe payment processing
  const paymentData = {
    stripeToken: paymentIntent.client_secret,
    cardNumber: stripeData.value.cardNumber.replace(/\s/g, ''),
    expiryDate: stripeData.value.expiryDate,
    cvc: stripeData.value.cvc,
    cardholderName: stripeData.value.cardholderName
  }
  
  await enrollmentProcessPayment(props.course.id, 'stripe', paymentData)
}

const processPayPalPayment = async () => {
  const order = await createPayPalOrder(props.course.id, props.course.price)
  
  // In a real implementation, you would redirect to PayPal here
  // For now, we'll simulate the process
  
  await enrollmentProcessPayment(props.course.id, 'paypal', {
    paypalOrderId: order.id
  })
}

const processBankTransfer = async () => {
  const transfer = await initiateBankTransfer(props.course.id, props.course.price)
  
  await enrollmentProcessPayment(props.course.id, 'bank_transfer', {
    bankTransferReference: transfer.reference
  })
}

// Watch for modal show/hide
watch(() => props.show, (show) => {
  if (!show) {
    resetForm()
  }
})
</script>

<style scoped>
.payment-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.payment-modal {
  background: white;
  border-radius: 12px;
  max-width: 500px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 24px 0;
  border-bottom: 1px solid #e5e7eb;
  margin-bottom: 24px;
}

.modal-header h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #6b7280;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: #f3f4f6;
  color: #374151;
}

.modal-content {
  padding: 0 24px 24px;
}

.course-summary {
  background: linear-gradient(135deg, #fef3e2, rgba(254, 243, 226, 0.5));
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 24px;
  border: 1px solid rgba(245, 158, 11, 0.2);
}

.course-info {
  display: flex;
  gap: 12px;
  align-items: center;
}

.course-image {
  width: 60px;
  height: 60px;
  border-radius: 6px;
  object-fit: cover;
  flex-shrink: 0;
}

.course-details h4 {
  font-size: 1rem;
  font-weight: 600;
  color: #111827;
  margin: 0 0 4px 0;
}

.instructor {
  font-size: 0.875rem;
  color: #6b7280;
  margin: 0 0 8px 0;
}

.price {
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.amount {
  font-size: 1.25rem;
  font-weight: 700;
  color: #f59e0b;
}

.currency {
  font-size: 0.875rem;
  color: #6b7280;
}

.payment-methods h4 {
  font-size: 1rem;
  font-weight: 600;
  color: #111827;
  margin-bottom: 16px;
}

.method-options {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 24px;
}

.method-option {
  display: block;
  cursor: pointer;
}

.method-option input[type="radio"] {
  display: none;
}

.method-content {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.method-option:hover .method-content {
  border-color: #f59e0b;
  background: rgba(254, 243, 226, 0.3);
}

.method-option.active .method-content {
  border-color: #f59e0b;
  background: linear-gradient(135deg, #fef3e2, rgba(254, 243, 226, 0.5));
}

.method-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
}

.method-info {
  flex: 1;
}

.method-name {
  display: block;
  font-weight: 600;
  color: #111827;
  margin-bottom: 2px;
}

.method-description {
  font-size: 0.875rem;
  color: #6b7280;
}

.payment-form {
  margin-bottom: 24px;
}

.form-group {
  margin-bottom: 16px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.form-group label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  margin-bottom: 6px;
}

.form-input {
  width: 100%;
  padding: 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 1rem;
  transition: border-color 0.2s ease;
}

.form-input:focus {
  outline: none;
  border-color: #f59e0b;
  box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.1);
}

.payment-info {
  margin-bottom: 24px;
}

.info-card {
  display: flex;
  gap: 12px;
  padding: 16px;
  background: #f9fafb;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.info-icon {
  font-size: 1.25rem;
  flex-shrink: 0;
}

.info-text p {
  margin: 0 0 8px 0;
  font-size: 0.875rem;
  color: #6b7280;
  line-height: 1.5;
}

.info-text p:last-child {
  margin-bottom: 0;
}

.error-message {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 6px;
  color: #dc2626;
  font-size: 0.875rem;
  margin-bottom: 24px;
}

.error-icon {
  flex-shrink: 0;
}

.payment-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.btn {
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
  display: inline-block;
  text-align: center;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  box-shadow: 0 4px 15px rgba(245, 158, 11, 0.3);
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(245, 158, 11, 0.4);
}

.btn-outline {
  background: transparent;
  color: #6b7280;
  border: 1px solid #d1d5db;
}

.btn-outline:hover {
  background: #f9fafb;
  border-color: #9ca3af;
}

/* Responsive */
@media (max-width: 480px) {
  .payment-modal {
    margin: 10px;
    max-height: calc(100vh - 20px);
  }
  
  .modal-header {
    padding: 16px 16px 0;
  }
  
  .modal-content {
    padding: 0 16px 16px;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .payment-actions {
    flex-direction: column;
  }
  
  .course-info {
    flex-direction: column;
    text-align: center;
  }
}
</style>