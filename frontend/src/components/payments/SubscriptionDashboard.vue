<template>
  <div class="subscription-dashboard">
    <!-- Header -->
    <div class="dashboard-header mb-8">
      <div class="flex justify-between items-center">
        <div>
          <h2 class="text-2xl font-bold text-gray-900">Subscription Management</h2>
          <p class="text-gray-600 mt-1">Manage your organization's subscription plan and billing</p>
        </div>
        <button
          v-if="!activeSubscription"
          @click="showPlanSelector = true"
          class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
        >
          Subscribe Now
        </button>
      </div>
    </div>

    <!-- Current Subscription Card -->
    <div v-if="activeSubscription" class="current-subscription mb-8">
      <div class="bg-white rounded-lg shadow-md border border-gray-200 p-6">
        <div class="flex justify-between items-start mb-4">
          <div>
            <h3 class="text-xl font-semibold text-gray-900 mb-2">Current Plan</h3>
            <div class="flex items-center space-x-3">
              <span class="text-2xl font-bold text-blue-600">
                {{ activeSubscription.plan.charAt(0).toUpperCase() + activeSubscription.plan.slice(1) }}
              </span>
              <span
                :class="[
                  'px-2 py-1 rounded-full text-xs font-medium',
                  getSubscriptionStatusColor(activeSubscription.status)
                ]"
              >
                {{ activeSubscription.status.charAt(0).toUpperCase() + activeSubscription.status.slice(1) }}
              </span>
            </div>
          </div>
          <div class="text-right">
            <div class="text-2xl font-bold text-gray-900">
              {{ formatCurrency(activeSubscription.amount, activeSubscription.currency) }}
            </div>
            <div class="text-sm text-gray-500">
              per {{ activeSubscription.billing_cycle }}
            </div>
          </div>
        </div>

        <!-- Subscription Details -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div class="bg-gray-50 p-4 rounded-lg">
            <div class="text-sm text-gray-600">Current Period</div>
            <div class="font-medium">
              {{ formatDate(activeSubscription.current_period_start) }} - 
              {{ formatDate(activeSubscription.current_period_end) }}
            </div>
          </div>
          <div class="bg-gray-50 p-4 rounded-lg">
            <div class="text-sm text-gray-600">Next Billing</div>
            <div class="font-medium">
              {{ formatDate(activeSubscription.current_period_end) }}
            </div>
          </div>
          <div class="bg-gray-50 p-4 rounded-lg">
            <div class="text-sm text-gray-600">Organization</div>
            <div class="font-medium">
              {{ activeSubscription.organization_name }}
            </div>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="flex space-x-3">
          <button
            @click="showPlanSelector = true"
            class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Change Plan
          </button>
          <button
            @click="renewSubscription"
            :disabled="loading"
            class="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50"
          >
            Renew Now
          </button>
          <button
            @click="showCancelDialog = true"
            class="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors"
          >
            Cancel Subscription
          </button>
        </div>
      </div>
    </div>

    <!-- No Subscription State -->
    <div v-else class="no-subscription mb-8">
      <div class="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-8 text-center">
        <div class="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg class="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4" />
          </svg>
        </div>
        <h3 class="text-xl font-semibold text-gray-900 mb-2">No Active Subscription</h3>
        <p class="text-gray-600 mb-6">Choose a subscription plan to unlock premium features for your organization</p>
        <button
          @click="showPlanSelector = true"
          class="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
        >
          View Plans
        </button>
      </div>
    </div>

    <!-- Billing History -->
    <div class="billing-history mb-8">
      <h3 class="text-lg font-semibold text-gray-900 mb-4">Billing History</h3>
      <div class="bg-white rounded-lg shadow-md border border-gray-200">
        <div v-if="loading" class="p-8 text-center">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p class="text-gray-600 mt-2">Loading billing history...</p>
        </div>
        
        <div v-else-if="invoices.length === 0" class="p-8 text-center text-gray-500">
          No billing history available
        </div>
        
        <div v-else class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Invoice
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Date
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Amount
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="invoice in invoices" :key="invoice.id" class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm font-medium text-gray-900">
                    {{ invoice.invoice_number }}
                  </div>
                  <div class="text-sm text-gray-500">
                    {{ invoice.description }}
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ formatDate(invoice.issue_date) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ formatCurrency(invoice.total_amount, invoice.currency) }}
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
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button
                    @click="downloadInvoice(invoice.id)"
                    class="text-blue-600 hover:text-blue-900 mr-3"
                  >
                    Download
                  </button>
                  <button
                    v-if="invoice.status === 'overdue'"
                    @click="payInvoice(invoice)"
                    class="text-green-600 hover:text-green-900"
                  >
                    Pay Now
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Plan Selector Modal -->
    <div
      v-if="showPlanSelector"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click="showPlanSelector = false"
    >
      <div
        class="bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-screen overflow-y-auto"
        @click.stop
      >
        <SubscriptionPlans
          :current-plan="activeSubscription?.plan"
          @plan-selected="handlePlanSelection"
          @close="showPlanSelector = false"
        />
      </div>
    </div>

    <!-- Cancel Confirmation Dialog -->
    <div
      v-if="showCancelDialog"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click="showCancelDialog = false"
    >
      <div
        class="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 p-6"
        @click.stop
      >
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Cancel Subscription</h3>
        <p class="text-gray-600 mb-6">
          Are you sure you want to cancel your subscription? You'll lose access to premium features at the end of your current billing period.
        </p>
        <div class="flex space-x-3">
          <button
            @click="cancelSubscription"
            :disabled="loading"
            class="flex-1 bg-red-600 text-white py-2 px-4 rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50"
          >
            Yes, Cancel
          </button>
          <button
            @click="showCancelDialog = false"
            class="flex-1 bg-gray-300 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-400 transition-colors"
          >
            Keep Subscription
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { usePayments } from '../../composables/usePayments'
import SubscriptionPlans from './SubscriptionPlans.vue'

const {
  subscriptions,
  invoices,
  loading,
  // error, // Unused for now
  fetchSubscriptions,
  fetchInvoices,
  cancelSubscription: cancelSub,
  renewSubscription: renewSub,
  downloadInvoice,
  formatCurrency,
  getSubscriptionStatusColor
} = usePayments()

const showPlanSelector = ref(false)
const showCancelDialog = ref(false)

const activeSubscription = computed(() => 
  subscriptions.value.find(s => s.is_active_status)
)

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
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

const handlePlanSelection = async (planData: any) => {
  showPlanSelector.value = false
  // Handle plan selection logic here
  console.log('Selected plan:', planData)
}

const renewSubscription = async () => {
  if (!activeSubscription.value) return
  
  try {
    await renewSub(activeSubscription.value.id)
    await fetchSubscriptions()
  } catch (err) {
    console.error('Failed to renew subscription:', err)
  }
}

const cancelSubscription = async () => {
  if (!activeSubscription.value) return
  
  try {
    await cancelSub(activeSubscription.value.id)
    await fetchSubscriptions()
    showCancelDialog.value = false
  } catch (err) {
    console.error('Failed to cancel subscription:', err)
  }
}

const payInvoice = (invoice: any) => {
  // Navigate to payment page for this invoice
  console.log('Pay invoice:', invoice)
}

onMounted(async () => {
  await Promise.all([
    fetchSubscriptions(),
    fetchInvoices({ invoice_type: 'subscription' })
  ])
})
</script>

<style scoped>
.subscription-dashboard {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.dashboard-header {
  animation: fadeInUp 0.6s ease-out;
}

.current-subscription {
  animation: fadeInUp 0.6s ease-out 0.1s both;
}

.billing-history {
  animation: fadeInUp 0.6s ease-out 0.2s both;
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