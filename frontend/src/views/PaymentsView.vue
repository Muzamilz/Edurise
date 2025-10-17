<template>
  <div class="payments-view">
    <!-- Header -->
    <div class="payments-header mb-8">
      <div class="flex justify-between items-center">
        <div>
          <h1 class="text-3xl font-bold text-gray-900">Payments & Billing</h1>
          <p class="text-gray-600 mt-1">Manage your payments, subscriptions, and invoices</p>
        </div>
        
        <!-- Quick Actions -->
        <div class="flex space-x-3">
          <button
            @click="activeTab = 'notifications'"
            class="relative bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200 transition-colors"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-5 5v-5zM4 19h6v-2H4v2zM4 15h8v-2H4v2zM4 11h8V9H4v2zM4 7h8V5H4v2z" />
            </svg>
            <span
              v-if="unreadNotifications.length > 0"
              class="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center"
            >
              {{ unreadNotifications.length }}
            </span>
          </button>
          <button
            @click="showPaymentModal = true"
            class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Make Payment
          </button>
        </div>
      </div>
    </div>

    <!-- Navigation Tabs -->
    <div class="tabs-navigation mb-8">
      <nav class="flex space-x-8 border-b border-gray-200">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="[
            'py-2 px-1 border-b-2 font-medium text-sm transition-colors',
            activeTab === tab.id
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          ]"
        >
          {{ tab.name }}
        </button>
      </nav>
    </div>

    <!-- Tab Content -->
    <div class="tab-content">
      <!-- Overview Tab -->
      <div v-if="activeTab === 'overview'" class="overview-tab">
        <!-- Quick Stats -->
        <div class="stats-grid grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div class="stat-card bg-white p-6 rounded-lg shadow-md border border-gray-200">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <div class="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                  <svg class="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M4 4a2 2 0 00-2 2v4a2 2 0 002 2V6h10a2 2 0 00-2-2H4zm2 6a2 2 0 012-2h8a2 2 0 012 2v4a2 2 0 01-2 2H8a2 2 0 01-2-2v-4zm6 4a2 2 0 100-4 2 2 0 000 4z" clip-rule="evenodd" />
                  </svg>
                </div>
              </div>
              <div class="ml-4">
                <div class="text-sm font-medium text-gray-500">Total Spent</div>
                <div class="text-2xl font-bold text-gray-900">{{ formatCurrency(totalRevenue) }}</div>
              </div>
            </div>
          </div>

          <div class="stat-card bg-white p-6 rounded-lg shadow-md border border-gray-200">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <div class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                  <svg class="w-4 h-4 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clip-rule="evenodd" />
                  </svg>
                </div>
              </div>
              <div class="ml-4">
                <div class="text-sm font-medium text-gray-500">Active Subscription</div>
                <div class="text-2xl font-bold text-gray-900">
                  {{ activeSubscription?.plan ? (activeSubscription.plan.charAt(0).toUpperCase() + activeSubscription.plan.slice(1)) : 'None' }}
                </div>
              </div>
            </div>
          </div>

          <div class="stat-card bg-white p-6 rounded-lg shadow-md border border-gray-200">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <div class="w-8 h-8 bg-yellow-100 rounded-full flex items-center justify-center">
                  <svg class="w-4 h-4 text-yellow-600" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                  </svg>
                </div>
              </div>
              <div class="ml-4">
                <div class="text-sm font-medium text-gray-500">Pending Payments</div>
                <div class="text-2xl font-bold text-gray-900">{{ pendingPayments.length }}</div>
              </div>
            </div>
          </div>

          <div class="stat-card bg-white p-6 rounded-lg shadow-md border border-gray-200">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <div class="w-8 h-8 bg-red-100 rounded-full flex items-center justify-center">
                  <svg class="w-4 h-4 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M4 4a2 2 0 00-2 2v4a2 2 0 002 2V6h10a2 2 0 00-2-2H4zm2 6a2 2 0 012-2h8a2 2 0 012 2v4a2 2 0 01-2 2H8a2 2 0 01-2-2v-4zm6 4a2 2 0 100-4 2 2 0 000 4z" clip-rule="evenodd" />
                  </svg>
                </div>
              </div>
              <div class="ml-4">
                <div class="text-sm font-medium text-gray-500">Overdue Invoices</div>
                <div class="text-2xl font-bold text-gray-900">{{ overdueInvoices.length }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Recent Activity -->
        <div class="recent-activity mb-8">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
          <PaymentNotifications :limit="5" :show-actions="false" />
        </div>

        <!-- Quick Actions -->
        <div class="quick-actions">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button
              @click="activeTab = 'subscriptions'"
              class="action-card bg-white p-6 rounded-lg shadow-md border border-gray-200 hover:shadow-lg transition-shadow text-left"
            >
              <div class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center mb-3">
                <svg class="w-4 h-4 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clip-rule="evenodd" />
                </svg>
              </div>
              <h4 class="font-medium text-gray-900 mb-1">Manage Subscription</h4>
              <p class="text-sm text-gray-600">View and modify your subscription plan</p>
            </button>

            <button
              @click="activeTab = 'invoices'"
              class="action-card bg-white p-6 rounded-lg shadow-md border border-gray-200 hover:shadow-lg transition-shadow text-left"
            >
              <div class="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center mb-3">
                <svg class="w-4 h-4 text-purple-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clip-rule="evenodd" />
                </svg>
              </div>
              <h4 class="font-medium text-gray-900 mb-1">View Invoices</h4>
              <p class="text-sm text-gray-600">Download and manage your invoices</p>
            </button>

            <button
              @click="showPaymentModal = true"
              class="action-card bg-white p-6 rounded-lg shadow-md border border-gray-200 hover:shadow-lg transition-shadow text-left"
            >
              <div class="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center mb-3">
                <svg class="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M4 4a2 2 0 00-2 2v4a2 2 0 002 2V6h10a2 2 0 00-2-2H4zm2 6a2 2 0 012-2h8a2 2 0 012 2v4a2 2 0 01-2 2H8a2 2 0 01-2-2v-4zm6 4a2 2 0 100-4 2 2 0 000 4z" clip-rule="evenodd" />
                </svg>
              </div>
              <h4 class="font-medium text-gray-900 mb-1">Make Payment</h4>
              <p class="text-sm text-gray-600">Pay for courses or subscriptions</p>
            </button>
          </div>
        </div>
      </div>

      <!-- Payments Tab -->
      <div v-else-if="activeTab === 'payments'" class="payments-tab">
        <PaymentsList />
      </div>

      <!-- Subscriptions Tab -->
      <div v-else-if="activeTab === 'subscriptions'" class="subscriptions-tab">
        <SubscriptionDashboard />
      </div>

      <!-- Invoices Tab -->
      <div v-else-if="activeTab === 'invoices'" class="invoices-tab">
        <InvoicesList />
      </div>

      <!-- Notifications Tab -->
      <div v-else-if="activeTab === 'notifications'" class="notifications-tab">
        <PaymentNotifications />
      </div>
    </div>

    <!-- Payment Modal -->
    <div
      v-if="showPaymentModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click="showPaymentModal = false"
    >
      <div
        class="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-screen overflow-y-auto"
        @click.stop
      >
        <div class="p-6">
          <div class="flex justify-between items-center mb-6">
            <h3 class="text-lg font-semibold text-gray-900">Make a Payment</h3>
            <button
              @click="showPaymentModal = false"
              class="text-gray-400 hover:text-gray-600"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          <PaymentCheckout
            :amount="100"
            :course-id="'sample-course'"
            @payment-success="handlePaymentSuccess"
            @payment-error="handlePaymentError"
            @payment-initiated="handlePaymentInitiated"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { usePayments } from '../composables/usePayments'
import PaymentCheckout from '../components/payments/PaymentCheckout.vue'
import SubscriptionDashboard from '../components/payments/SubscriptionDashboard.vue'
import PaymentNotifications from '../components/payments/PaymentNotifications.vue'
import PaymentsList from '../components/payments/PaymentsList.vue'
import InvoicesList from '../components/payments/InvoicesList.vue'

const {
  // payments, // Unused for now
  // subscriptions, // Unused for now
  // invoices, // Unused for now
  // loading, // Unused for now
  totalRevenue,
  pendingPayments,
  activeSubscription,
  overdueInvoices,
  unreadNotifications,
  formatCurrency,
  fetchPayments,
  fetchSubscriptions,
  fetchInvoices
} = usePayments()

const activeTab = ref('overview')
const showPaymentModal = ref(false)

const tabs = [
  { id: 'overview', name: 'Overview' },
  { id: 'payments', name: 'Payments' },
  { id: 'subscriptions', name: 'Subscriptions' },
  { id: 'invoices', name: 'Invoices' },
  { id: 'notifications', name: 'Notifications' }
]

const handlePaymentSuccess = (payment: any) => {
  showPaymentModal.value = false
  // Refresh data
  fetchPayments()
  fetchInvoices()
  // Show success notification
  console.log('Payment successful:', payment)
}

const handlePaymentError = (error: string) => {
  console.error('Payment error:', error)
  // Show error notification
}

const handlePaymentInitiated = (details: any) => {
  console.log('Payment initiated:', details)
  // Show initiated notification
}

onMounted(async () => {
  // Load initial data
  await Promise.all([
    fetchPayments(),
    fetchSubscriptions(),
    fetchInvoices()
  ])
})
</script>

<style scoped>
.payments-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.payments-header {
  animation: fadeInUp 0.6s ease-out;
}

.tabs-navigation {
  animation: fadeInUp 0.6s ease-out 0.1s both;
}

.tab-content {
  animation: fadeInUp 0.6s ease-out 0.2s both;
}

.stats-grid .stat-card {
  animation: fadeInUp 0.6s ease-out calc(0.3s + var(--delay, 0s)) both;
}

.stats-grid .stat-card:nth-child(1) { --delay: 0s; }
.stats-grid .stat-card:nth-child(2) { --delay: 0.1s; }
.stats-grid .stat-card:nth-child(3) { --delay: 0.2s; }
.stats-grid .stat-card:nth-child(4) { --delay: 0.3s; }

.action-card {
  transition: all 0.2s ease;
}

.action-card:hover {
  transform: translateY(-2px);
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