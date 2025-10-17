<template>
  <div class="financial-view">
    <div class="page-header">
      <h1>Financial Reports</h1>
      <p>Monitor revenue, payments, and financial analytics</p>
    </div>

    <!-- Financial Overview -->
    <div class="financial-overview">
      <div class="overview-cards">
        <div class="overview-card">
          <div class="card-icon">💰</div>
          <div class="card-content">
            <h3>Total Revenue</h3>
            <div class="card-value">${{ formatNumber(totalRevenue) }}</div>
            <div class="card-change positive">+12.5% from last month</div>
          </div>
        </div>
        
        <div class="overview-card">
          <div class="card-icon">📊</div>
          <div class="card-content">
            <h3>Monthly Revenue</h3>
            <div class="card-value">${{ formatNumber(monthlyRevenue) }}</div>
            <div class="card-change positive">+8.3% from last month</div>
          </div>
        </div>
        
        <div class="overview-card">
          <div class="card-icon">💳</div>
          <div class="card-content">
            <h3>Total Transactions</h3>
            <div class="card-value">{{ formatNumber(totalTransactions) }}</div>
            <div class="card-change positive">+15.2% from last month</div>
          </div>
        </div>
        
        <div class="overview-card">
          <div class="card-icon">📈</div>
          <div class="card-content">
            <h3>Average Order Value</h3>
            <div class="card-value">${{ formatNumber(averageOrderValue) }}</div>
            <div class="card-change negative">-2.1% from last month</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Revenue Chart -->
    <div class="chart-section">
      <div class="chart-container">
        <div class="chart-header">
          <h3>Revenue Trend</h3>
          <select v-model="chartPeriod" class="period-select">
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
          </select>
        </div>
        <div class="chart-placeholder">
          <p>Revenue chart would be displayed here</p>
        </div>
      </div>
    </div>

    <!-- Recent Transactions -->
    <div class="transactions-section">
      <div class="section-header">
        <h3>Recent Transactions</h3>
        <button class="export-btn">Export CSV</button>
      </div>
      
      <div class="transactions-table">
        <table>
          <thead>
            <tr>
              <th>Date</th>
              <th>User</th>
              <th>Course</th>
              <th>Amount</th>
              <th>Status</th>
              <th>Payment Method</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="transaction in recentTransactions" :key="transaction.id">
              <td>{{ formatDate(transaction.date) }}</td>
              <td>{{ transaction.user }}</td>
              <td>{{ transaction.course }}</td>
              <td class="amount">${{ transaction.amount }}</td>
              <td>
                <span :class="['status-badge', transaction.status]">
                  {{ transaction.status }}
                </span>
              </td>
              <td>{{ transaction.paymentMethod }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const chartPeriod = ref('30d')

// Mock data
const totalRevenue = ref(125000)
const monthlyRevenue = ref(15000)
const totalTransactions = ref(1250)
const averageOrderValue = ref(100)

const recentTransactions = ref([
  {
    id: 1,
    date: '2024-01-15',
    user: 'John Doe',
    course: 'Web Development Basics',
    amount: 99,
    status: 'completed',
    paymentMethod: 'Credit Card'
  },
  {
    id: 2,
    date: '2024-01-14',
    user: 'Jane Smith',
    course: 'Advanced JavaScript',
    amount: 149,
    status: 'completed',
    paymentMethod: 'PayPal'
  }
])

const formatNumber = (num) => {
  return new Intl.NumberFormat().format(num)
}

const formatDate = (date) => {
  return new Date(date).toLocaleDateString()
}

onMounted(() => {
  // Load financial data
})
</script>

<style scoped>
.financial-view {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
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
  margin-bottom: 2rem;
}

.financial-overview {
  margin-bottom: 2rem;
}

.overview-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.overview-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.card-icon {
  font-size: 2rem;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f59e0b;
  border-radius: 12px;
}

.card-content h3 {
  font-size: 0.875rem;
  font-weight: 500;
  color: #6b7280;
  margin-bottom: 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.card-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 0.25rem;
}

.card-change {
  font-size: 0.875rem;
  font-weight: 500;
}

.card-change.positive {
  color: #10b981;
}

.card-change.negative {
  color: #ef4444;
}

.chart-section {
  margin-bottom: 2rem;
}

.chart-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.chart-header h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.period-select {
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
}

.chart-placeholder {
  height: 300px;
  background: #f9fafb;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6b7280;
}

.transactions-section {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.section-header h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.export-btn {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.export-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
}

.transactions-table {
  overflow-x: auto;
}

.transactions-table table {
  width: 100%;
  border-collapse: collapse;
}

.transactions-table th {
  background: #f9fafb;
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: #374151;
  border-bottom: 1px solid #e5e7eb;
}

.transactions-table td {
  padding: 1rem;
  border-bottom: 1px solid #f3f4f6;
}

.amount {
  font-weight: 600;
  color: #10b981;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
}

.status-badge.completed {
  background: #dcfce7;
  color: #166534;
}

.status-badge.pending {
  background: #fef3c7;
  color: #92400e;
}

.status-badge.failed {
  background: #fee2e2;
  color: #dc2626;
}
</style>