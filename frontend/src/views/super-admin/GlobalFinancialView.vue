<template>
  <div class="global-financial-view">
    <div class="page-header">
      <h1>Global Financial Overview</h1>
      <p>Monitor platform-wide financial metrics and revenue across all organizations</p>
    </div>

    <!-- Financial Summary Cards -->
    <div class="summary-cards">
      <div class="summary-card revenue">
        <div class="card-icon">💰</div>
        <div class="card-content">
          <h3>Total Platform Revenue</h3>
          <p class="amount">${{ formatCurrency(financialData?.total_revenue || 0) }}</p>
          <span class="change positive">+{{ financialData?.revenue_growth || 0 }}% this month</span>
        </div>
      </div>
      
      <div class="summary-card transactions">
        <div class="card-icon">💳</div>
        <div class="card-content">
          <h3>Total Transactions</h3>
          <p class="amount">{{ formatNumber(financialData?.total_transactions || 0) }}</p>
          <span class="change positive">+{{ financialData?.transaction_growth || 0 }}% this month</span>
        </div>
      </div>
      
      <div class="summary-card commission">
        <div class="card-icon">📊</div>
        <div class="card-content">
          <h3>Platform Commission</h3>
          <p class="amount">${{ formatCurrency(financialData?.platform_commission || 0) }}</p>
          <span class="change">{{ financialData?.commission_rate || 10 }}% commission rate</span>
        </div>
      </div>
      
      <div class="summary-card pending">
        <div class="card-icon">⏳</div>
        <div class="card-content">
          <h3>Pending Payouts</h3>
          <p class="amount">${{ formatCurrency(financialData?.pending_payouts || 0) }}</p>
          <span class="change">{{ financialData?.pending_count || 0 }} organizations</span>
        </div>
      </div>
    </div>

    <!-- Revenue Chart -->
    <div class="chart-section">
      <div class="chart-header">
        <h2>Revenue Trends</h2>
        <div class="chart-controls">
          <select v-model="chartPeriod" @change="updateChartData">
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
            <option value="90d">Last 90 Days</option>
            <option value="1y">Last Year</option>
          </select>
        </div>
      </div>
      <div class="chart-container">
        <canvas ref="revenueChart" width="800" height="400"></canvas>
      </div>
    </div>

    <!-- Organization Financial Performance -->
    <div class="organizations-section">
      <div class="section-header">
        <h2>Organization Performance</h2>
        <div class="filters">
          <select v-model="sortBy" @change="sortOrganizations">
            <option value="revenue">Sort by Revenue</option>
            <option value="growth">Sort by Growth</option>
            <option value="transactions">Sort by Transactions</option>
            <option value="name">Sort by Name</option>
          </select>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Loading financial data...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="error-state">
        <div class="error-icon">⚠️</div>
        <h3>Failed to load financial data</h3>
        <p>{{ error.message }}</p>
        <button @click="handleRetry" class="retry-btn">Try Again</button>
      </div>

      <!-- Organizations Table -->
      <div v-else class="organizations-table">
        <table>
          <thead>
            <tr>
              <th>Organization</th>
              <th>Total Revenue</th>
              <th>Monthly Growth</th>
              <th>Transactions</th>
              <th>Commission Earned</th>
              <th>Pending Payout</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="org in sortedOrganizations" :key="org.id" class="org-row">
              <td class="org-info">
                <div class="org-logo">
                  <img :src="org.logo || '/default-org.jpg'" :alt="org.name" />
                </div>
                <div class="org-details">
                  <h4>{{ org.name }}</h4>
                  <p>{{ org.domain }}</p>
                </div>
              </td>
              <td class="revenue">
                <span class="amount">${{ formatCurrency(org.total_revenue || 0) }}</span>
              </td>
              <td class="growth">
                <span :class="{ positive: org.growth_rate > 0, negative: org.growth_rate < 0 }">
                  {{ org.growth_rate > 0 ? '+' : '' }}{{ org.growth_rate || 0 }}%
                </span>
              </td>
              <td>{{ formatNumber(org.transaction_count || 0) }}</td>
              <td class="commission">
                <span class="amount">${{ formatCurrency(org.commission_earned || 0) }}</span>
              </td>
              <td class="pending">
                <span class="amount">${{ formatCurrency(org.pending_payout || 0) }}</span>
              </td>
              <td>
                <span class="status-badge" :class="org.payout_status">
                  {{ formatPayoutStatus(org.payout_status) }}
                </span>
              </td>
              <td class="actions">
                <button @click="viewOrgDetails(org)" class="action-btn view">
                  View Details
                </button>
                <button 
                  @click="processPayout(org)" 
                  :disabled="!org.pending_payout || org.payout_status === 'processing'"
                  class="action-btn payout"
                >
                  Process Payout
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Transaction History -->
    <div class="transactions-section">
      <div class="section-header">
        <h2>Recent Transactions</h2>
        <div class="filters">
          <select v-model="transactionFilter">
            <option value="">All Transactions</option>
            <option value="completed">Completed</option>
            <option value="pending">Pending</option>
            <option value="failed">Failed</option>
            <option value="refunded">Refunded</option>
          </select>
        </div>
      </div>

      <div class="transactions-table">
        <table>
          <thead>
            <tr>
              <th>Transaction ID</th>
              <th>Organization</th>
              <th>Course</th>
              <th>Student</th>
              <th>Amount</th>
              <th>Commission</th>
              <th>Status</th>
              <th>Date</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="transaction in filteredTransactions" :key="transaction.id" class="transaction-row">
              <td class="transaction-id">
                <code>{{ transaction.id }}</code>
              </td>
              <td>{{ transaction.organization?.name }}</td>
              <td>{{ transaction.course?.title }}</td>
              <td>{{ transaction.student?.first_name }} {{ transaction.student?.last_name }}</td>
              <td class="amount">${{ formatCurrency(transaction.amount) }}</td>
              <td class="commission">${{ formatCurrency(transaction.commission) }}</td>
              <td>
                <span class="status-badge" :class="transaction.status">
                  {{ formatTransactionStatus(transaction.status) }}
                </span>
              </td>
              <td>{{ formatDate(transaction.created_at) }}</td>
              <td class="actions">
                <button @click="viewTransaction(transaction)" class="action-btn view">
                  View
                </button>
                <button 
                  v-if="transaction.status === 'failed'"
                  @click="retryTransaction(transaction)" 
                  class="action-btn retry"
                >
                  Retry
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div class="pagination">
        <button 
          @click="currentPage--" 
          :disabled="currentPage === 1"
          class="pagination-btn"
        >
          Previous
        </button>
        <span class="pagination-info">
          Page {{ currentPage }} of {{ totalPages }}
        </span>
        <button 
          @click="currentPage++" 
          :disabled="currentPage === totalPages"
          class="pagination-btn"
        >
          Next
        </button>
      </div>
    </div>

    <!-- Payout Processing Modal -->
    <div v-if="processingPayout" class="modal-overlay" @click="closePayoutModal">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>Process Payout: {{ processingPayout.name }}</h3>
          <button @click="closePayoutModal" class="close-btn">×</button>
        </div>
        <div class="modal-body">
          <div class="payout-details">
            <div class="detail-row">
              <span class="label">Organization:</span>
              <span class="value">{{ processingPayout.name }}</span>
            </div>
            <div class="detail-row">
              <span class="label">Pending Amount:</span>
              <span class="value">${{ formatCurrency(processingPayout.pending_payout) }}</span>
            </div>
            <div class="detail-row">
              <span class="label">Commission Deduction:</span>
              <span class="value">${{ formatCurrency(processingPayout.pending_payout * 0.1) }}</span>
            </div>
            <div class="detail-row total">
              <span class="label">Net Payout:</span>
              <span class="value">${{ formatCurrency(processingPayout.pending_payout * 0.9) }}</span>
            </div>
          </div>
          <div class="form-group">
            <label>Payout Method</label>
            <select v-model="payoutMethod">
              <option value="bank_transfer">Bank Transfer</option>
              <option value="paypal">PayPal</option>
              <option value="stripe">Stripe</option>
            </select>
          </div>
          <div class="form-group">
            <label>Notes (Optional)</label>
            <textarea v-model="payoutNotes" placeholder="Add any notes about this payout..."></textarea>
          </div>
          <div class="form-actions">
            <button @click="closePayoutModal" class="cancel-btn">Cancel</button>
            <button @click="confirmPayout" class="confirm-btn">
              Process Payout
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { useApiData, useApiMutation } from '@/composables/useApiData'
import { useErrorHandler } from '@/composables/useErrorHandler'

const { handleApiError } = useErrorHandler()

// Data fetching
const { data: financialData, loading, error, refresh } = useApiData('/analytics/financial/global/')
const { data: organizations } = useApiData('/organizations/financial/')
const { data: transactions } = useApiData('/payments/transactions/')

// Chart and filters
const chartPeriod = ref('30d')
const sortBy = ref('revenue')
const transactionFilter = ref('')
const currentPage = ref(1)
const itemsPerPage = 20

// Payout processing
const processingPayout = ref(null)
const payoutMethod = ref('bank_transfer')
const payoutNotes = ref('')

// Chart reference
const revenueChart = ref(null)

// Payout mutation
const { mutate: processPayoutMutation } = useApiMutation(
  ({ orgId, method, notes }) => ({ 
    method: 'POST', 
    url: `/organizations/${orgId}/process-payout/`, 
    data: { method, notes } 
  }),
  {
    onSuccess: () => {
      closePayoutModal()
      refresh()
    },
    onError: (error) => handleApiError(error, { context: { action: 'process_payout' } })
  }
)

// Computed properties
const sortedOrganizations = computed(() => {
  if (!organizations.value) return []
  
  const sorted = [...organizations.value].sort((a, b) => {
    switch (sortBy.value) {
      case 'revenue':
        return (b.total_revenue || 0) - (a.total_revenue || 0)
      case 'growth':
        return (b.growth_rate || 0) - (a.growth_rate || 0)
      case 'transactions':
        return (b.transaction_count || 0) - (a.transaction_count || 0)
      case 'name':
        return a.name.localeCompare(b.name)
      default:
        return 0
    }
  })
  
  return sorted
})

const filteredTransactions = computed(() => {
  if (!transactions.value) return []
  
  let filtered = transactions.value
  
  if (transactionFilter.value) {
    filtered = filtered.filter(t => t.status === transactionFilter.value)
  }
  
  return filtered
})

const totalPages = computed(() => Math.ceil(filteredTransactions.value.length / itemsPerPage))

// Methods
const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(amount)
}

const formatNumber = (num) => {
  return new Intl.NumberFormat('en-US').format(num)
}

const formatDate = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleDateString()
}

const formatPayoutStatus = (status) => {
  return status?.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()) || 'Pending'
}

const formatTransactionStatus = (status) => {
  return status?.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()) || 'Unknown'
}

const sortOrganizations = () => {
  // Trigger reactivity
  sortBy.value = sortBy.value
}

const viewOrgDetails = (org) => {
  window.open(`/super-admin/organizations/${org.id}`, '_blank')
}

const processPayout = (org) => {
  processingPayout.value = org
  payoutMethod.value = 'bank_transfer'
  payoutNotes.value = ''
}

const closePayoutModal = () => {
  processingPayout.value = null
  payoutMethod.value = 'bank_transfer'
  payoutNotes.value = ''
}

const confirmPayout = async () => {
  if (!processingPayout.value) return
  
  await processPayoutMutation({
    orgId: processingPayout.value.id,
    method: payoutMethod.value,
    notes: payoutNotes.value
  })
}

const viewTransaction = (transaction) => {
  // Open transaction details in modal or new page
  console.log('View transaction:', transaction)
}

const retryTransaction = async (transaction) => {
  // Implement transaction retry logic
  console.log('Retry transaction:', transaction)
}

const updateChartData = async () => {
  // Update chart based on selected period
  await nextTick()
  initializeChart()
}

const initializeChart = () => {
  if (!revenueChart.value) return
  
  // Initialize chart with Chart.js or similar library
  // This is a placeholder for actual chart implementation
  const ctx = revenueChart.value.getContext('2d')
  ctx.fillStyle = '#f59e0b'
  ctx.fillRect(0, 0, 800, 400)
  ctx.fillStyle = 'white'
  ctx.font = '20px Arial'
  ctx.textAlign = 'center'
  ctx.fillText('Revenue Chart Placeholder', 400, 200)
}

const handleRetry = async () => {
  try {
    await refresh()
  } catch (err) {
    handleApiError(err, { context: { action: 'retry_financial_load' } })
  }
}

onMounted(() => {
  refresh()
  nextTick(() => {
    initializeChart()
  })
})
</script>

<style scoped>
.global-financial-view {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
}

.page-header {
  margin-bottom: 2rem;
}

.page-header h1 {
  font-size: 2rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.page-header p {
  color: #6b7280;
  font-size: 1.125rem;
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.summary-card {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 1rem;
}

.card-icon {
  font-size: 2.5rem;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  background: linear-gradient(135deg, #f59e0b, #d97706);
}

.card-content h3 {
  font-size: 0.875rem;
  font-weight: 500;
  color: #6b7280;
  margin: 0 0 0.5rem 0;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.card-content .amount {
  font-size: 1.875rem;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 0.25rem 0;
}

.card-content .change {
  font-size: 0.875rem;
  color: #6b7280;
}

.card-content .change.positive {
  color: #059669;
}

.card-content .change.negative {
  color: #dc2626;
}

.chart-section {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.chart-header h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.chart-controls select {
  padding: 0.5rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
}

.chart-container {
  width: 100%;
  height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.organizations-section,
.transactions-section {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
  overflow: hidden;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.section-header h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.filters select {
  padding: 0.5rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
}

.organizations-table,
.transactions-table {
  overflow-x: auto;
}

.organizations-table table,
.transactions-table table {
  width: 100%;
  border-collapse: collapse;
}

.organizations-table th,
.transactions-table th {
  background: #f9fafb;
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: #374151;
  border-bottom: 1px solid #e5e7eb;
}

.organizations-table td,
.transactions-table td {
  padding: 1rem;
  border-bottom: 1px solid #f3f4f6;
}

.org-row:hover,
.transaction-row:hover {
  background: #f9fafb;
}

.org-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.org-logo {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
}

.org-logo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.org-details h4 {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 0.25rem 0;
}

.org-details p {
  font-size: 0.875rem;
  color: #6b7280;
  margin: 0;
}

.amount {
  font-weight: 600;
  color: #1f2937;
}

.growth .positive {
  color: #059669;
}

.growth .negative {
  color: #dc2626;
}

.transaction-id code {
  background: #f3f4f6;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  color: #374151;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
}

.status-badge.completed,
.status-badge.current {
  background: #dcfce7;
  color: #166534;
}

.status-badge.pending,
.status-badge.processing {
  background: #fef3c7;
  color: #92400e;
}

.status-badge.failed,
.status-badge.overdue {
  background: #fee2e2;
  color: #dc2626;
}

.status-badge.refunded {
  background: #f3e8ff;
  color: #5b21b6;
}

.actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.action-btn.view {
  background: #dbeafe;
  color: #1e40af;
}

.action-btn.view:hover {
  background: #bfdbfe;
}

.action-btn.payout {
  background: #dcfce7;
  color: #166534;
}

.action-btn.payout:hover:not(:disabled) {
  background: #bbf7d0;
}

.action-btn.retry {
  background: #fef3c7;
  color: #92400e;
}

.action-btn.retry:hover {
  background: #fde68a;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  border-top: 1px solid #e5e7eb;
}

.pagination-btn {
  padding: 0.5rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: white;
  color: #374151;
  cursor: pointer;
  transition: all 0.3s ease;
}

.pagination-btn:hover:not(:disabled) {
  background: #f9fafb;
  border-color: #f59e0b;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-info {
  font-size: 0.875rem;
  color: #6b7280;
}

/* Modal Styles */
.modal-overlay {
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
}

.modal {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #6b7280;
  cursor: pointer;
  padding: 0.25rem;
}

.close-btn:hover {
  color: #374151;
}

.modal-body {
  padding: 1.5rem;
}

.payout-details {
  background: #f9fafb;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.detail-row.total {
  border-top: 1px solid #e5e7eb;
  padding-top: 0.5rem;
  margin-top: 0.5rem;
  font-weight: 600;
}

.detail-row .label {
  color: #6b7280;
}

.detail-row .value {
  color: #1f2937;
  font-weight: 500;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.5rem;
}

.form-group select,
.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 1rem;
}

.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #f59e0b;
  box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.1);
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1.5rem;
}

.cancel-btn {
  padding: 0.75rem 1.5rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: white;
  color: #374151;
  cursor: pointer;
  font-weight: 500;
}

.cancel-btn:hover {
  background: #f9fafb;
}

.confirm-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  cursor: pointer;
  font-weight: 600;
}

.confirm-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
}

/* Loading and Error States */
.loading-state, .error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f4f6;
  border-top: 4px solid #f59e0b;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-state p {
  color: #6b7280;
  font-size: 1rem;
  margin: 0;
}

.error-state .error-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.error-state h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #dc2626;
  margin-bottom: 0.5rem;
}

.error-state p {
  color: #6b7280;
  margin-bottom: 1.5rem;
  max-width: 400px;
}

.retry-btn {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.retry-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(245, 158, 11, 0.4);
}
</style>