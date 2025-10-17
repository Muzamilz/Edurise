<template>
  <div class="invoice-display">
    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center h-64">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
    </div>

    <!-- Invoice Content -->
    <div v-else-if="invoice" class="invoice-content bg-white">
      <!-- Invoice Header -->
      <div class="invoice-header border-b border-gray-200 pb-6 mb-6">
        <div class="flex justify-between items-start">
          <div>
            <h1 class="text-3xl font-bold text-gray-900 mb-2">INVOICE</h1>
            <div class="text-lg text-gray-600">{{ invoice.invoice_number }}</div>
          </div>
          <div class="text-right">
            <div class="text-sm text-gray-600 mb-1">Issue Date</div>
            <div class="font-medium">{{ formatDate(invoice.issue_date) }}</div>
            <div class="text-sm text-gray-600 mb-1 mt-2">Due Date</div>
            <div class="font-medium">{{ formatDate(invoice.due_date) }}</div>
          </div>
        </div>

        <!-- Status Badge -->
        <div class="mt-4">
          <span
            :class="[
              'px-3 py-1 rounded-full text-sm font-medium',
              getInvoiceStatusColor(invoice.status)
            ]"
          >
            {{ invoice.status.charAt(0).toUpperCase() + invoice.status.slice(1) }}
          </span>
        </div>
      </div>

      <!-- Billing Information -->
      <div class="billing-info grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
        <!-- From -->
        <div>
          <h3 class="text-lg font-semibold text-gray-900 mb-3">From</h3>
          <div class="text-gray-700">
            <div class="font-medium text-lg">EduRise LMS Platform</div>
            <div>123 Education Street</div>
            <div>Learning City, LC 12345</div>
            <div>United States</div>
            <div class="mt-2">
              <div>Email: billing@edurise.com</div>
              <div>Phone: +1 (555) 123-4567</div>
            </div>
          </div>
        </div>

        <!-- To -->
        <div>
          <h3 class="text-lg font-semibold text-gray-900 mb-3">Bill To</h3>
          <div class="text-gray-700">
            <div class="font-medium text-lg">{{ invoice.billing_name }}</div>
            <div>{{ invoice.billing_email }}</div>
            <div v-if="invoice.billing_address_line1">{{ invoice.billing_address_line1 }}</div>
            <div v-if="invoice.billing_address_line2">{{ invoice.billing_address_line2 }}</div>
            <div v-if="invoice.billing_city || invoice.billing_state || invoice.billing_postal_code">
              {{ invoice.billing_city }}{{ invoice.billing_state ? ', ' + invoice.billing_state : '' }}
              {{ invoice.billing_postal_code }}
            </div>
            <div v-if="invoice.billing_country">{{ invoice.billing_country }}</div>
          </div>
        </div>
      </div>

      <!-- Invoice Description -->
      <div v-if="invoice.description" class="invoice-description mb-8">
        <h3 class="text-lg font-semibold text-gray-900 mb-3">Description</h3>
        <p class="text-gray-700">{{ invoice.description }}</p>
      </div>

      <!-- Line Items -->
      <div class="line-items mb-8">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Items</h3>
        <div class="overflow-x-auto">
          <table class="w-full border border-gray-200 rounded-lg">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-4 py-3 text-left text-sm font-medium text-gray-700">Description</th>
                <th class="px-4 py-3 text-center text-sm font-medium text-gray-700">Quantity</th>
                <th class="px-4 py-3 text-right text-sm font-medium text-gray-700">Unit Price</th>
                <th class="px-4 py-3 text-right text-sm font-medium text-gray-700">Total</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200">
              <tr v-for="item in invoice.line_items" :key="item.id">
                <td class="px-4 py-3">
                  <div class="font-medium text-gray-900">{{ item.description }}</div>
                  <div v-if="item.course_title" class="text-sm text-gray-600">
                    Course: {{ item.course_title }}
                  </div>
                </td>
                <td class="px-4 py-3 text-center text-gray-700">
                  {{ item.quantity }}
                </td>
                <td class="px-4 py-3 text-right text-gray-700">
                  {{ formatCurrency(item.unit_price, invoice.currency) }}
                </td>
                <td class="px-4 py-3 text-right font-medium text-gray-900">
                  {{ formatCurrency(item.total_price, invoice.currency) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Totals -->
      <div class="totals">
        <div class="flex justify-end">
          <div class="w-full max-w-sm">
            <div class="space-y-2">
              <div class="flex justify-between text-gray-700">
                <span>Subtotal:</span>
                <span>{{ formatCurrency(invoice.subtotal, invoice.currency) }}</span>
              </div>
              
              <div v-if="invoice.tax_amount > 0" class="flex justify-between text-gray-700">
                <span>Tax ({{ (invoice.tax_rate * 100).toFixed(2) }}%):</span>
                <span>{{ formatCurrency(invoice.tax_amount, invoice.currency) }}</span>
              </div>
              
              <div v-if="invoice.discount_amount > 0" class="flex justify-between text-green-600">
                <span>Discount:</span>
                <span>-{{ formatCurrency(invoice.discount_amount, invoice.currency) }}</span>
              </div>
              
              <hr class="border-gray-300">
              
              <div class="flex justify-between text-lg font-bold text-gray-900">
                <span>Total:</span>
                <span>{{ formatCurrency(invoice.total_amount, invoice.currency) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Notes -->
      <div v-if="invoice.notes" class="notes mt-8 pt-6 border-t border-gray-200">
        <h3 class="text-lg font-semibold text-gray-900 mb-3">Notes</h3>
        <p class="text-gray-700">{{ invoice.notes }}</p>
      </div>

      <!-- Payment Information -->
      <div v-if="invoice.status !== 'paid'" class="payment-info mt-8 pt-6 border-t border-gray-200">
        <h3 class="text-lg font-semibold text-gray-900 mb-3">Payment Information</h3>
        <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p class="text-blue-800 mb-2">
            <strong>Payment Due:</strong> {{ formatDate(invoice.due_date) }}
          </p>
          <p class="text-blue-700 text-sm">
            Please include invoice number {{ invoice.invoice_number }} with your payment.
          </p>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="actions mt-8 pt-6 border-t border-gray-200 flex flex-wrap gap-3">
        <button
          @click="downloadInvoice"
          :disabled="downloading"
          class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
        >
          <div v-if="downloading" class="flex items-center">
            <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
            Downloading...
          </div>
          <div v-else class="flex items-center">
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Download PDF
          </div>
        </button>

        <button
          @click="printInvoice"
          class="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition-colors"
        >
          <div class="flex items-center">
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
            </svg>
            Print
          </div>
        </button>

        <button
          v-if="invoice.status === 'overdue' || invoice.status === 'sent'"
          @click="payNow"
          class="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
        >
          <div class="flex items-center">
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
            </svg>
            Pay Now
          </div>
        </button>

        <button
          v-if="showBackButton"
          @click="$emit('back')"
          class="bg-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-400 transition-colors"
        >
          Back to List
        </button>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="text-center py-12">
      <div class="text-red-600 mb-4">
        <svg class="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
      <h3 class="text-lg font-medium text-gray-900 mb-2">Failed to Load Invoice</h3>
      <p class="text-gray-600">{{ error }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { usePayments } from '../../composables/usePayments'
import type { Invoice } from '../../types/payments'

interface Props {
  invoiceId?: string
  invoice?: Invoice
  showBackButton?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showBackButton: false
})

const emit = defineEmits<{
  back: []
  paymentInitiated: [invoice: Invoice]
}>()

const {
  currentInvoice,
  loading,
  error,
  fetchInvoice,
  downloadInvoice: downloadInvoicePdf,
  formatCurrency
} = usePayments()

const downloading = ref(false)

const invoice = computed(() => props.invoice || currentInvoice.value)

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

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

const downloadInvoice = async () => {
  if (!invoice.value) return

  downloading.value = true
  try {
    await downloadInvoicePdf(invoice.value.id)
  } catch (err) {
    console.error('Failed to download invoice:', err)
  } finally {
    downloading.value = false
  }
}

const printInvoice = () => {
  window.print()
}

const payNow = () => {
  if (invoice.value) {
    emit('paymentInitiated', invoice.value)
  }
}

onMounted(async () => {
  if (props.invoiceId && !props.invoice) {
    await fetchInvoice(props.invoiceId)
  }
})
</script>

<style scoped>
.invoice-display {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
}

.invoice-content {
  padding: 2rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  border-radius: 0.5rem;
}

@media print {
  .invoice-display {
    padding: 0;
  }
  
  .invoice-content {
    box-shadow: none;
    padding: 1rem;
  }
  
  .actions {
    display: none;
  }
}

.invoice-header {
  animation: fadeInUp 0.6s ease-out;
}

.billing-info {
  animation: fadeInUp 0.6s ease-out 0.1s both;
}

.line-items {
  animation: fadeInUp 0.6s ease-out 0.2s both;
}

.totals {
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