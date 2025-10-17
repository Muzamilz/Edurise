<template>
  <div class="payments-list">
    <!-- Header with Filters -->
    <div class="list-header mb-6">
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-semibold text-gray-900">Payment History</h3>
        <button
          @click="refreshPayments"
          :disabled="loading"
          class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
        >
          <div v-if="loading" class="flex items-center">
            <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
            Loading...
          </div>
          <span v-else>Refresh</span>
        </button>
      </div>

      <!-- Filters -->
      <div class="filters flex flex-wrap gap-4">
        <div class="filter-group">
          <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
          <select
            v-model="filters.status"
            @change="applyFilters"
            class="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">All Statuses</option>
            <option value="pending">Pending</option>
            <option value="processing">Processing</option>
            <option value="completed">Completed</option>
            <option value="failed">Failed</option>
            <option value="cancelled">Cancelled</option>
            <option value="refunded">Refunded</option>
          </select>
        </div>

        <div class="filter-group">
          <label class="block text-sm font-medium text-gray-700 mb-1">Payment Method</label>
          <select
            v-model="filters.payment_method"
            @change="applyFilters"
            class="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">All Methods</option>
            <option value="stripe">Credit/Debit Card</option>
            <option value="paypal">PayPal</option>
            <option value="bank_transfer">Bank Transfer</option>
          </select>
        </div>

        <div class="filter-group">
          <label class="block text-sm font-medium text-gray-700 mb-1">Date Range</label>
          <select
            v-model="filters.date_range"
            @change="applyFilters"
            class="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">All Time</option>
            <option value="today">Today</option>
            <option value="week">This Week</option>
            <option value="month">This Month</option>
            <option value="quarter">This Quarter</option>
            <option value="year">This Year</option>
          </select>
        </div>

        <div class="filter-group">
          <label class="block text-sm font-medium text-gray-700 mb-1">Search</label>
          <input
            v-model="filters.search"
            @input="debounceSearch"
            type="text"
            placeholder="Search payments..."
            class="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
      </div>
    </div>

    <!-- Payments Table -->
    <div class="payments-table bg-white rounded-lg shadow-md border border-gray-200">
      <div v-if="loading && payments.length === 0" class="p-8 text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p class="text-gray-600">Loading payments...</p>
      </div>

      <div v-else-if="payments.length === 0" class="p-8 text-center">
        <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
          </svg>
        </div>
        <h3 class="text-lg font-medium text-gray-900 mb-2">No payments found</h3>
        <p class="text-gray-600">No payments match your current filters.</p>
      </div>

      <div v-else class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Payment
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Amount
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Method
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Date
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr
              v-for="payment in payments"
              :key="payment.id"
              class="hover:bg-gray-50 transition-colors"
            >
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="flex-shrink-0 w-8 h-8">
                    <div
                      :class="[
                        'w-8 h-8 rounded-full flex items-center justify-center text-sm',
                        getPaymentStatusColor(payment.status)
                      ]"
                    >
                      {{ getPaymentMethodIcon(payment.payment_method) }}
                    </div>
                  </div>
                  <div class="ml-4">
                    <div class="text-sm font-medium text-gray-900">
                      {{ payment.id.substring(0, 8) }}...
                    </div>
                    <div class="text-sm text-gray-500">
                      {{ payment.course_title || payment.subscription_plan || payment.description }}
                    </div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">
                  {{ formatCurrency(payment.amount, payment.currency) }}
                </div>
                <div class="text-sm text-gray-500">
                  {{ payment.payment_type.charAt(0).toUpperCase() + payment.payment_type.slice(1) }}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <span class="text-lg mr-2">{{ getPaymentMethodIcon(payment.payment_method) }}</span>
                  <span class="text-sm text-gray-900 capitalize">
                    {{ payment.payment_method.replace('_', ' ') }}
                  </span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  :class="[
                    'px-2 py-1 rounded-full text-xs font-medium',
                    getPaymentStatusColor(payment.status)
                  ]"
                >
                  {{ payment.status.charAt(0).toUpperCase() + payment.status.slice(1) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                <div>{{ formatDate(payment.created_at) }}</div>
                <div v-if="payment.completed_at" class="text-xs text-gray-500">
                  Completed: {{ formatDate(payment.completed_at) }}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <div class="flex space-x-2">
                  <button
                    @click="viewPayment(payment)"
                    class="text-blue-600 hover:text-blue-900"
                  >
                    View
                  </button>
                  <button
                    v-if="payment.status === 'failed'"
                    @click="retryPayment(payment)"
                    class="text-green-600 hover:text-green-900"
                  >
                    Retry
                  </button>
                  <button
                    v-if="payment.status === 'pending' || payment.status === 'processing'"
                    @click="cancelPayment(payment)"
                    class="text-red-600 hover:text-red-900"
                  >
                    Cancel
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="pagination.total > pagination.limit" class="pagination mt-6 flex justify-between items-center">
      <div class="text-sm text-gray-700">
        Showing {{ pagination.offset + 1 }} to {{ Math.min(pagination.offset + pagination.limit, pagination.total) }} 
        of {{ pagination.total }} payments
      </div>
      <div class="flex space-x-2">
        <button
          @click="previousPage"
          :disabled="pagination.offset === 0"
          class="px-3 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Previous
        </button>
        <button
          @click="nextPage"
          :disabled="pagination.offset + pagination.limit >= pagination.total"
          class="px-3 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Next
        </button>
      </div>
    </div>

    <!-- Payment Detail Modal -->
    <div
      v-if="selectedPayment"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click="selectedPayment = null"
    >
      <div
        class="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-screen overflow-y-auto"
        @click.stop
      >
        <div class="p-6">
          <div class="flex justify-between items-center mb-6">
            <h3 class="text-lg font-semibold text-gray-900">Payment Details</h3>
            <button
              @click="selectedPayment = null"
              class="text-gray-400 hover:text-gray-600"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          <PaymentStatusTracker
            :payment="selectedPayment"
            @retry-requested="handleRetryPayment"
            @cancel-requested="handleCancelPayment"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { usePayments } from '../../composables/usePayments'
import PaymentStatusTracker from './PaymentStatusTracker.vue'
import type { Payment } from '../../types/payments'

const {
  payments,
  loading,
  fetchPayments,
  formatCurrency,
  getPaymentStatusColor,
  getPaymentMethodIcon
} = usePayments()

const selectedPayment = ref<Payment | null>(null)

const filters = ref({
  status: '',
  payment_method: '',
  date_range: '',
  search: ''
})

const pagination = ref({
  offset: 0,
  limit: 20,
  total: 0
})

let searchTimeout: NodeJS.Timeout | null = null

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const applyFilters = async () => {
  pagination.value.offset = 0
  await loadPayments()
}

const debounceSearch = () => {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
  searchTimeout = setTimeout(() => {
    applyFilters()
  }, 500)
}

const loadPayments = async () => {
  const filterParams = {
    ...filters.value,
    offset: pagination.value.offset,
    limit: pagination.value.limit
  }
  
  // Remove empty filters
  Object.keys(filterParams).forEach(key => {
    if (filterParams[key as keyof typeof filterParams] === '') {
      delete filterParams[key as keyof typeof filterParams]
    }
  })

  try {
    const response = await fetchPayments(filterParams)
    pagination.value.total = response.data.count
  } catch (error) {
    console.error('Failed to load payments:', error)
  }
}

const refreshPayments = () => {
  loadPayments()
}

const previousPage = () => {
  if (pagination.value.offset > 0) {
    pagination.value.offset -= pagination.value.limit
    loadPayments()
  }
}

const nextPage = () => {
  if (pagination.value.offset + pagination.value.limit < pagination.value.total) {
    pagination.value.offset += pagination.value.limit
    loadPayments()
  }
}

const viewPayment = (payment: Payment) => {
  selectedPayment.value = payment
}

const retryPayment = (payment: Payment) => {
  console.log('Retry payment:', payment.id)
  // Implement retry logic
}

const cancelPayment = (payment: Payment) => {
  console.log('Cancel payment:', payment.id)
  // Implement cancel logic
}

const handleRetryPayment = () => {
  if (selectedPayment.value) {
    retryPayment(selectedPayment.value)
    selectedPayment.value = null
  }
}

const handleCancelPayment = () => {
  if (selectedPayment.value) {
    cancelPayment(selectedPayment.value)
    selectedPayment.value = null
  }
}

onMounted(() => {
  loadPayments()
})
</script>

<style scoped>
.payments-list {
  animation: fadeInUp 0.6s ease-out;
}

.payments-table tbody tr {
  animation: slideInLeft 0.3s ease-out;
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

@keyframes slideInLeft {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}
</style>