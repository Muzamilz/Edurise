<template>
  <div class="invoices-list">
    <!-- Header with Filters -->
    <div class="list-header mb-6">
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-semibold text-gray-900">Invoices</h3>
        <button
          @click="refreshInvoices"
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
            <option value="draft">Draft</option>
            <option value="sent">Sent</option>
            <option value="paid">Paid</option>
            <option value="overdue">Overdue</option>
            <option value="cancelled">Cancelled</option>
            <option value="void">Void</option>
          </select>
        </div>

        <div class="filter-group">
          <label class="block text-sm font-medium text-gray-700 mb-1">Type</label>
          <select
            v-model="filters.invoice_type"
            @change="applyFilters"
            class="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">All Types</option>
            <option value="payment">Payment Invoice</option>
            <option value="subscription">Subscription Invoice</option>
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
            placeholder="Search invoices..."
            class="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
      </div>
    </div>

    <!-- Invoices Table -->
    <div class="invoices-table bg-white rounded-lg shadow-md border border-gray-200">
      <div v-if="loading && invoices.length === 0" class="p-8 text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p class="text-gray-600">Loading invoices...</p>
      </div>

      <div v-else-if="invoices.length === 0" class="p-8 text-center">
        <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <h3 class="text-lg font-medium text-gray-900 mb-2">No invoices found</h3>
        <p class="text-gray-600">No invoices match your current filters.</p>
      </div>

      <div v-else class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Invoice
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Customer
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Amount
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Due Date
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr
              v-for="invoice in invoices"
              :key="invoice.id"
              class="hover:bg-gray-50 transition-colors"
            >
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="flex-shrink-0 w-8 h-8">
                    <div
                      :class="[
                        'w-8 h-8 rounded-full flex items-center justify-center text-sm',
                        getInvoiceStatusColor(invoice.status)
                      ]"
                    >
                      📄
                    </div>
                  </div>
                  <div class="ml-4">
                    <div class="text-sm font-medium text-gray-900">
                      {{ invoice.invoice_number }}
                    </div>
                    <div class="text-sm text-gray-500">
                      {{ invoice.description }}
                    </div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">
                  {{ invoice.billing_name }}
                </div>
                <div class="text-sm text-gray-500">
                  {{ invoice.billing_email }}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">
                  {{ formatCurrency(invoice.total_amount, invoice.currency) }}
                </div>
                <div class="text-sm text-gray-500 capitalize">
                  {{ invoice.invoice_type.replace('_', ' ') }}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  :class="[
                    'px-2 py-1 rounded-full text-xs font-medium',
                    getInvoiceStatusColor(invoice.status)
                  ]"
                >
                  {{ invoice.status.charAt(0).toUpperCase() + invoice.status.slice(1) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">
                  {{ formatDate(invoice.due_date) }}
                </div>
                <div
                  v-if="isOverdue(invoice)"
                  class="text-xs text-red-600 font-medium"
                >
                  {{ getDaysOverdue(invoice) }} days overdue
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <div class="flex space-x-2">
                  <button
                    @click="viewInvoice(invoice)"
                    class="text-blue-600 hover:text-blue-900"
                  >
                    View
                  </button>
                  <button
                    @click="downloadInvoice(invoice.id)"
                    class="text-green-600 hover:text-green-900"
                  >
                    Download
                  </button>
                  <button
                    v-if="invoice.status === 'overdue' || invoice.status === 'sent'"
                    @click="payInvoice(invoice)"
                    class="text-purple-600 hover:text-purple-900"
                  >
                    Pay Now
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
        of {{ pagination.total }} invoices
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

    <!-- Invoice Detail Modal -->
    <div
      v-if="selectedInvoice"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click="selectedInvoice = null"
    >
      <div
        class="bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-screen overflow-y-auto"
        @click.stop
      >
        <InvoiceDisplay
          :invoice="selectedInvoice"
          :show-back-button="true"
          @back="selectedInvoice = null"
          @payment-initiated="handlePaymentInitiated"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { usePayments } from '../../composables/usePayments'
import InvoiceDisplay from './InvoiceDisplay.vue'
import type { Invoice } from '../../types/payments'

const {
  invoices,
  loading,
  fetchInvoices,
  downloadInvoice,
  formatCurrency
} = usePayments()

const selectedInvoice = ref<Invoice | null>(null)

const filters = ref({
  status: '',
  invoice_type: '',
  date_range: '',
  search: ''
})

const pagination = ref({
  offset: 0,
  limit: 20,
  total: 0
})

let searchTimeout: NodeJS.Timeout | null = null

const getInvoiceStatusColor = (status: string) => {
  const colors = {
    draft: 'text-gray-600 bg-gray-100',
    sent: 'text-blue-600 bg-blue-100',
    paid: 'text-green-600 bg-green-100',
    overdue: 'text-red-600 bg-red-100',
    cancelled: 'text-gray-600 bg-gray-100',
    void: 'text-gray-600 bg-gray-100'
  }
  return colors[status as keyof typeof colors] || 'text-gray-600 bg-gray-100'
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const isOverdue = (invoice: Invoice) => {
  return invoice.status === 'overdue' || 
         (invoice.status === 'sent' && new Date(invoice.due_date) < new Date())
}

const getDaysOverdue = (invoice: Invoice) => {
  const dueDate = new Date(invoice.due_date)
  const today = new Date()
  const diffTime = today.getTime() - dueDate.getTime()
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24))
}

const applyFilters = async () => {
  pagination.value.offset = 0
  await loadInvoices()
}

const debounceSearch = () => {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
  searchTimeout = setTimeout(() => {
    applyFilters()
  }, 500)
}

const loadInvoices = async () => {
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
    const response = await fetchInvoices(filterParams)
    pagination.value.total = response.data.count
  } catch (error) {
    console.error('Failed to load invoices:', error)
  }
}

const refreshInvoices = () => {
  loadInvoices()
}

const previousPage = () => {
  if (pagination.value.offset > 0) {
    pagination.value.offset -= pagination.value.limit
    loadInvoices()
  }
}

const nextPage = () => {
  if (pagination.value.offset + pagination.value.limit < pagination.value.total) {
    pagination.value.offset += pagination.value.limit
    loadInvoices()
  }
}

const viewInvoice = (invoice: Invoice) => {
  selectedInvoice.value = invoice
}

const payInvoice = (invoice: Invoice) => {
  console.log('Pay invoice:', invoice.id)
  // Navigate to payment page or open payment modal
}

const handlePaymentInitiated = (invoice: Invoice) => {
  selectedInvoice.value = null
  console.log('Payment initiated for invoice:', invoice.id)
  // Handle payment initiation
}

onMounted(() => {
  loadInvoices()
})
</script>

<style scoped>
.invoices-list {
  animation: fadeInUp 0.6s ease-out;
}

.invoices-table tbody tr {
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