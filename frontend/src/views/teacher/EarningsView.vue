<template>
  <div class="earnings-view">
    <div class="page-header">
      <h1>Earnings Dashboard</h1>
      <p>Track your teaching income and payment history</p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>Loading earnings data...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-state">
      <div class="error-icon">⚠️</div>
      <h3>Failed to load earnings</h3>
      <p>{{ error.message }}</p>
      <button @click="handleRetry" class="retry-btn">Try Again</button>
    </div>

    <!-- Earnings Content -->
    <div v-else class="earnings-content">
      <!-- Earnings Overview -->
      <div class="earnings-overview">
        <div class="stats-grid">
          <div class="stat-card primary">
            <div class="stat-icon">💰</div>
            <h3>Total Earnings</h3>
            <p class="stat-number">${{ totalEarnings }}</p>
            <span class="stat-change positive">+15% this month</span>
          </div>
          <div class="stat-card">
            <div class="stat-icon">📅</div>
            <h3>This Month</h3>
            <p class="stat-number">${{ monthlyEarnings }}</p>
            <span class="stat-change positive">+8% from last month</span>
          </div>
          <div class="stat-card">
            <div class="stat-icon">⏳</div>
            <h3>Pending Payments</h3>
            <p class="stat-number">${{ pendingPayments }}</p>
            <span class="stat-change neutral">{{ pendingCount }} transactions</span>
          </div>
          <div class="stat-card">
            <div class="stat-icon">📊</div>
            <h3>Average per Course</h3>
            <p class="stat-number">${{ averagePerCourse }}</p>
            <span class="stat-change neutral">Based on {{ totalCourses }} courses</span>
          </div>
        </div>
      </div>

      <!-- Earnings Chart -->
      <div class="earnings-chart">
        <div class="chart-header">
          <h2>Earnings Trend</h2>
          <div class="chart-filters">
            <select v-model="chartPeriod" @change="updateChart">
              <option value="6months">Last 6 Months</option>
              <option value="12months">Last 12 Months</option>
              <option value="year">This Year</option>
            </select>
          </div>
        </div>
        <div class="chart-container">
          <AnalyticsChart 
            :data="earningsChartData" 
            type="line"
            :height="300"
          />
        </div>
      </div>

      <!-- Payment History -->
      <div class="payment-history">
        <div class="section-header">
          <h2>Payment History</h2>
          <div class="history-filters">
            <select v-model="statusFilter" @change="filterPayments">
              <option value="">All Payments</option>
              <option value="completed">Completed</option>
              <option value="pending">Pending</option>
              <option value="failed">Failed</option>
            </select>
            <input 
              type="month" 
              v-model="monthFilter" 
              @change="filterPayments"
              class="month-filter"
            >
          </div>
        </div>
        
        <div class="payments-table">
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Course</th>
                <th>Student</th>
                <th>Amount</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="payment in filteredPayments" :key="payment.id">
                <td>{{ formatDate(payment.date) }}</td>
                <td>{{ payment.course_title }}</td>
                <td>{{ payment.student_name }}</td>
                <td class="amount">${{ payment.amount }}</td>
                <td>
                  <span class="status-badge" :class="payment.status">
                    {{ formatStatus(payment.status) }}
                  </span>
                </td>
                <td>
                  <button @click="viewPaymentDetails(payment)" class="view-btn">
                    View
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Course Revenue Breakdown -->
      <div class="course-revenue">
        <h2>Revenue by Course</h2>
        <div class="course-revenue-list">
          <div v-for="course in courseRevenue" :key="course.id" class="course-revenue-card">
            <div class="course-info">
              <img :src="course.thumbnail || '/placeholder-course.jpg'" :alt="course.title" class="course-thumbnail" />
              <div class="course-details">
                <h4>{{ course.title }}</h4>
                <p>{{ course.enrollments }} enrollments</p>
              </div>
            </div>
            <div class="revenue-info">
              <div class="revenue-amount">${{ course.revenue }}</div>
              <div class="revenue-stats">
                <span>Avg: ${{ course.averageRevenue }}</span>
                <span>Growth: {{ course.growth }}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Payout Settings -->
      <div class="payout-settings">
        <h2>Payout Settings</h2>
        <div class="settings-card">
          <div class="setting-item">
            <div class="setting-info">
              <h4>Payment Method</h4>
              <p>{{ payoutMethod || 'Not configured' }}</p>
            </div>
            <button @click="editPayoutMethod" class="edit-btn">Edit</button>
          </div>
          <div class="setting-item">
            <div class="setting-info">
              <h4>Payout Schedule</h4>
              <p>{{ payoutSchedule || 'Monthly' }}</p>
            </div>
            <button @click="editPayoutSchedule" class="edit-btn">Edit</button>
          </div>
          <div class="setting-item">
            <div class="setting-info">
              <h4>Minimum Payout</h4>
              <p>${{ minimumPayout || 50 }}</p>
            </div>
            <button @click="editMinimumPayout" class="edit-btn">Edit</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useApiData } from '@/composables/useApiData'
// Removed unused import
import { useErrorHandler } from '@/composables/useErrorHandler'
import AnalyticsChart from '@/components/analytics/AnalyticsChart.vue'

const { handleApiError } = useErrorHandler()

// Reactive state
const chartPeriod = ref('6months')
const statusFilter = ref('')
const monthFilter = ref('')

// API data
const { 
  // data: earningsData, // Unused
  loading, 
  error, 
  refresh 
} = useApiData('/teacher/earnings/', {
  immediate: true,
  transform: (data) => {
    // Transform the response to ensure consistent data structure
    return {
      totalEarnings: data.total_earnings || 0,
      monthlyEarnings: data.monthly_earnings || 0,
      pendingPayments: data.pending_payments || 0,
      pendingCount: data.pending_count || 0,
      averagePerCourse: data.average_per_course || 0,
      totalCourses: data.total_courses || 0,
      payments: (data.payments || []).map((payment: any) => ({
        id: payment.id,
        date: payment.created_at || payment.date,
        course_title: payment.course?.title || payment.course_title,
        student_name: payment.student?.full_name || payment.student_name,
        amount: payment.amount,
        status: payment.status
      })),
      courseRevenue: (data.course_revenue || []).map((course: any) => ({
        id: course.id,
        title: course.title,
        thumbnail: course.thumbnail,
        enrollments: course.enrollments || 0,
        revenue: course.revenue || 0,
        averageRevenue: course.average_revenue || 0,
        growth: course.growth || 0
      }))
    }
  },
  retryAttempts: 3,
  onError: (error) => {
    console.error('Failed to load earnings:', error)
  }
})

// Mock data (replace with real API data)
const totalEarnings = ref(12450)
const monthlyEarnings = ref(2340)
const pendingPayments = ref(450)
const pendingCount = ref(3)
const averagePerCourse = ref(890)
const totalCourses = ref(14)

const payoutMethod = ref('PayPal - john@example.com')
const payoutSchedule = ref('Monthly')
const minimumPayout = ref(50)

const payments = ref([
  {
    id: 1,
    date: '2024-01-15',
    course_title: 'JavaScript Fundamentals',
    student_name: 'John Doe',
    amount: 99,
    status: 'completed'
  },
  {
    id: 2,
    date: '2024-01-14',
    course_title: 'React Advanced',
    student_name: 'Jane Smith',
    amount: 149,
    status: 'pending'
  },
  {
    id: 3,
    date: '2024-01-13',
    course_title: 'Node.js Backend',
    student_name: 'Bob Johnson',
    amount: 199,
    status: 'completed'
  }
])

const courseRevenue = ref([
  {
    id: 1,
    title: 'JavaScript Fundamentals',
    thumbnail: null,
    enrollments: 45,
    revenue: 4455,
    averageRevenue: 99,
    growth: 12
  },
  {
    id: 2,
    title: 'React Advanced',
    thumbnail: null,
    enrollments: 32,
    revenue: 4768,
    averageRevenue: 149,
    growth: 8
  }
])

// Computed properties
const filteredPayments = computed(() => {
  let filtered = payments.value

  if (statusFilter.value) {
    filtered = filtered.filter(p => p.status === statusFilter.value)
  }

  if (monthFilter.value) {
    const [year, month] = monthFilter.value.split('-')
    filtered = filtered.filter(p => {
      const paymentDate = new Date(p.date)
      return paymentDate.getFullYear() === parseInt(year) && 
             paymentDate.getMonth() === parseInt(month) - 1
    })
  }

  return filtered
})

const earningsChartData = computed(() => ({
  labels: ['Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
  datasets: [{
    label: 'Monthly Earnings',
    data: [1200, 1800, 1500, 2100, 1900, 2340],
    borderColor: '#f59e0b',
    backgroundColor: 'rgba(245, 158, 11, 0.1)',
    fill: true
  }]
}))

// Methods
const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const formatStatus = (status: string) => {
  return status.charAt(0).toUpperCase() + status.slice(1)
}

const updateChart = () => {
  // Update chart data based on selected period
  console.log('Update chart for period:', chartPeriod.value)
}

const filterPayments = () => {
  // Filtering is handled by computed property
}

const viewPaymentDetails = (payment: any) => {
  console.log('View payment details:', payment)
}

const editPayoutMethod = () => {
  console.log('Edit payout method')
}

const editPayoutSchedule = () => {
  console.log('Edit payout schedule')
}

const editMinimumPayout = () => {
  console.log('Edit minimum payout')
}

const handleRetry = async () => {
  try {
    await refresh()
  } catch (err) {
    handleApiError(err as any, { context: { action: 'retry_earnings_load' } })
  }
}

onMounted(() => {
  // Set default month filter to current month
  const now = new Date()
  monthFilter.value = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`
})
</script><style 
scoped>
.earnings-view {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
  min-height: 100vh;
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

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(254, 243, 226, 0.3));
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.1);
  text-align: center;
  transition: all 0.3s ease;
}

.stat-card.primary {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
}

.stat-card.primary .stat-number {
  color: white;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(245, 158, 11, 0.15);
}

.stat-icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.stat-card h3 {
  font-size: 0.875rem;
  font-weight: 500;
  color: #6b7280;
  margin-bottom: 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.stat-card.primary h3 {
  color: rgba(255, 255, 255, 0.9);
}

.stat-number {
  font-size: 2rem;
  font-weight: 700;
  color: #f59e0b;
  margin: 0 0 0.25rem 0;
}

.stat-change {
  font-size: 0.75rem;
  font-weight: 500;
}

.stat-change.positive {
  color: #10b981;
}

.stat-change.neutral {
  color: #6b7280;
}

.stat-card.primary .stat-change {
  color: rgba(255, 255, 255, 0.8);
}

.earnings-chart, .payment-history, .course-revenue, .payout-settings {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.1);
  margin-bottom: 2rem;
}

.chart-header, .section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.chart-header h2, .section-header h2, .course-revenue h2, .payout-settings h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.chart-filters, .history-filters {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.chart-filters select, .history-filters select, .month-filter {
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
  background: white;
}

.payments-table {
  overflow-x: auto;
}

.payments-table table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

.payments-table th {
  background: #f9fafb;
  padding: 0.75rem;
  text-align: left;
  font-weight: 600;
  color: #374151;
  border-bottom: 1px solid #e5e7eb;
}

.payments-table td {
  padding: 0.75rem;
  border-bottom: 1px solid #f3f4f6;
  font-size: 0.875rem;
}

.amount {
  font-weight: 600;
  color: #10b981;
}

.status-badge {
  padding: 0.25rem 0.5rem;
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
  background: #fef2f2;
  color: #dc2626;
}

.view-btn {
  background: #3b82f6;
  color: white;
  padding: 0.25rem 0.75rem;
  border: none;
  border-radius: 4px;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.view-btn:hover {
  background: #2563eb;
}

.course-revenue-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.course-revenue-card {
  background: #f9fafb;
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.course-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.course-thumbnail {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  object-fit: cover;
}

.course-details h4 {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.25rem;
}

.course-details p {
  font-size: 0.875rem;
  color: #6b7280;
}

.revenue-info {
  text-align: right;
}

.revenue-amount {
  font-size: 1.25rem;
  font-weight: 700;
  color: #10b981;
  margin-bottom: 0.25rem;
}

.revenue-stats {
  display: flex;
  gap: 1rem;
  font-size: 0.75rem;
  color: #6b7280;
}

.settings-card {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.setting-info h4 {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.25rem;
}

.setting-info p {
  font-size: 0.875rem;
  color: #6b7280;
}

.edit-btn {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.edit-btn:hover {
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
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
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

/* Responsive */
@media (max-width: 768px) {
  .earnings-view {
    padding: 1rem;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .chart-header, .section-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .chart-filters, .history-filters {
    flex-direction: column;
    align-items: stretch;
  }
  
  .course-revenue-card {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .revenue-info {
    text-align: left;
  }
  
  .revenue-stats {
    justify-content: flex-start;
  }
  
  .setting-item {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
}
</style>