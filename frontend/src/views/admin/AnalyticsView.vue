<template>
  <div class="admin-analytics-view">
    <div class="page-header">
      <h1>Platform Analytics</h1>
      <p>Monitor your organization's performance and growth metrics</p>
    </div>

    <!-- Date Range Selector -->
    <div class="date-range-selector">
      <div class="date-controls">
        <select v-model="selectedPeriod" @change="updateDateRange" class="period-select">
          <option value="7d">Last 7 days</option>
          <option value="30d">Last 30 days</option>
          <option value="90d">Last 90 days</option>
          <option value="1y">Last year</option>
          <option value="custom">Custom range</option>
        </select>
        <div v-if="selectedPeriod === 'custom'" class="custom-date-inputs">
          <input v-model="startDate" type="date" class="date-input" />
          <span>to</span>
          <input v-model="endDate" type="date" class="date-input" />
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>Loading analytics data...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-state">
      <div class="error-icon">⚠️</div>
      <h3>Failed to load analytics</h3>
      <p>{{ error.message }}</p>
      <button @click="handleRetry" class="retry-btn">Try Again</button>
    </div>

    <!-- Analytics Content -->
    <div v-else class="analytics-content">
      <!-- Key Metrics Cards -->
      <div class="metrics-grid">
        <div class="metric-card">
          <div class="metric-header">
            <h3>Total Users</h3>
            <div class="metric-icon">👥</div>
          </div>
          <div class="metric-value">{{ formatNumber(typedAnalyticsData?.totalUsers || 0) }}</div>
          <div class="metric-change" :class="getChangeClass(analyticsData?.userGrowth)">
            {{ formatChange(analyticsData?.userGrowth) }}
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-header">
            <h3>Active Courses</h3>
            <div class="metric-icon">📚</div>
          </div>
          <div class="metric-value">{{ formatNumber(analyticsData?.activeCourses || 0) }}</div>
          <div class="metric-change" :class="getChangeClass(analyticsData?.courseGrowth)">
            {{ formatChange(analyticsData?.courseGrowth) }}
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-header">
            <h3>Total Enrollments</h3>
            <div class="metric-icon">🎓</div>
          </div>
          <div class="metric-value">{{ formatNumber(analyticsData?.totalEnrollments || 0) }}</div>
          <div class="metric-change" :class="getChangeClass(analyticsData?.enrollmentGrowth)">
            {{ formatChange(analyticsData?.enrollmentGrowth) }}
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-header">
            <h3>Revenue</h3>
            <div class="metric-icon">💰</div>
          </div>
          <div class="metric-value">${{ formatNumber(analyticsData?.totalRevenue || 0) }}</div>
          <div class="metric-change" :class="getChangeClass(analyticsData?.revenueGrowth)">
            {{ formatChange(analyticsData?.revenueGrowth) }}
          </div>
        </div>
      </div>

      <!-- Charts Section -->
      <div class="charts-section">
        <div class="chart-container">
          <div class="chart-header">
            <h3>User Growth Trend</h3>
            <div class="chart-controls">
              <select v-model="userChartType" class="chart-type-select">
                <option value="total">Total Users</option>
                <option value="new">New Users</option>
                <option value="active">Active Users</option>
              </select>
            </div>
          </div>
          <div class="chart-content">
            <AnalyticsChart
              :data="userGrowthData"
              :type="'line'"
              :height="300"
              :color="'#f59e0b'"
            />
          </div>
        </div>

        <div class="chart-container">
          <div class="chart-header">
            <h3>Enrollment Analytics</h3>
            <div class="chart-controls">
              <select v-model="enrollmentChartType" class="chart-type-select">
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
                <option value="monthly">Monthly</option>
              </select>
            </div>
          </div>
          <div class="chart-content">
            <AnalyticsChart
              :data="enrollmentData"
              :type="'bar'"
              :height="300"
              :color="'#10b981'"
            />
          </div>
        </div>
      </div>

      <!-- Detailed Analytics -->
      <div class="detailed-analytics">
        <div class="analytics-section">
          <h3>Course Performance</h3>
          <div class="course-performance-table">
            <table>
              <thead>
                <tr>
                  <th>Course</th>
                  <th>Enrollments</th>
                  <th>Completion Rate</th>
                  <th>Avg. Rating</th>
                  <th>Revenue</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="course in topCourses" :key="course.id" class="course-row">
                  <td class="course-info">
                    <div class="course-title">{{ course.title }}</div>
                    <div class="course-instructor">{{ course.instructor }}</div>
                  </td>
                  <td>{{ formatNumber(course.enrollments) }}</td>
                  <td>
                    <div class="completion-rate">
                      <div class="completion-bar">
                        <div 
                          class="completion-fill" 
                          :style="{ width: course.completionRate + '%' }"
                        ></div>
                      </div>
                      <span>{{ course.completionRate }}%</span>
                    </div>
                  </td>
                  <td>
                    <div class="rating">
                      <span class="stars">★★★★★</span>
                      <span class="rating-value">{{ course.rating.toFixed(1) }}</span>
                    </div>
                  </td>
                  <td class="revenue">${{ formatNumber(course.revenue) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="analytics-section">
          <h3>User Engagement</h3>
          <div class="engagement-metrics">
            <div class="engagement-card">
              <h4>Average Session Duration</h4>
              <div class="engagement-value">{{ analyticsData?.avgSessionDuration || '0m' }}</div>
            </div>
            <div class="engagement-card">
              <h4>Daily Active Users</h4>
              <div class="engagement-value">{{ formatNumber(analyticsData?.dailyActiveUsers || 0) }}</div>
            </div>
            <div class="engagement-card">
              <h4>Course Completion Rate</h4>
              <div class="engagement-value">{{ analyticsData?.overallCompletionRate || 0 }}%</div>
            </div>
            <div class="engagement-card">
              <h4>User Retention (30d)</h4>
              <div class="engagement-value">{{ analyticsData?.userRetention || 0 }}%</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Export Options -->
      <div class="export-section">
        <h3>Export Data</h3>
        <div class="export-buttons">
          <button @click="exportData('csv')" class="export-btn">
            <span class="btn-icon">📊</span>
            Export CSV
          </button>
          <button @click="exportData('pdf')" class="export-btn">
            <span class="btn-icon">📄</span>
            Export PDF
          </button>
          <button @click="generateReport" class="export-btn primary">
            <span class="btn-icon">📈</span>
            Generate Report
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useApiData } from '@/composables/useApiData'
import type { APIError } from '@/services/api'
import { useErrorHandler } from '@/composables/useErrorHandler'
import AnalyticsChart from '@/components/analytics/AnalyticsChart.vue'

const { handleApiError } = useErrorHandler()

// Date range state
const selectedPeriod = ref('30d')
const startDate = ref('')
const endDate = ref('')

// Chart type state
const userChartType = ref('total')
const enrollmentChartType = ref('daily')

// Data fetching
const { data: analyticsData, loading, error, refresh } = useApiData<any>(() => {
  const params = new URLSearchParams({
    period: selectedPeriod.value,
    start_date: startDate.value || '',
    end_date: endDate.value || ''
  })
  return `/analytics/?${params.toString()}`
})

// Computed properties
const typedAnalyticsData = computed(() => analyticsData.value as any)

const userGrowthData = computed(() => {
  if (!(analyticsData.value as any)?.userGrowthTrend) return []
  
  return (analyticsData.value as any).userGrowthTrend.map((item: any) => ({
    label: item.date,
    value: item[userChartType.value] || 0
  }))
})

const enrollmentData = computed(() => {
  if (!(analyticsData.value as any)?.enrollmentTrend) return []
  
  return (analyticsData.value as any).enrollmentTrend.map((item: any) => ({
    label: item.period,
    value: item.enrollments || 0
  }))
})

const topCourses = computed(() => {
  return analyticsData.value?.topCourses || []
})

// Methods
const updateDateRange = () => {
  if (selectedPeriod.value !== 'custom') {
    startDate.value = ''
    endDate.value = ''
  }
  refresh()
}

const formatNumber = (num: number) => {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M'
  } else if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  return num.toString()
}

const formatChange = (change: number) => {
  if (!change) return '0%'
  const sign = change > 0 ? '+' : ''
  return `${sign}${change.toFixed(1)}%`
}

const getChangeClass = (change: number) => {
  if (!change) return 'neutral'
  return change > 0 ? 'positive' : 'negative'
}

const exportData = async (format: string) => {
  try {
    const response = await fetch(`/api/v1/analytics/export/?format=${format}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    })
    
    if (response.ok) {
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `analytics-${new Date().toISOString().split('T')[0]}.${format}`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    }
  } catch (error) {
    handleApiError(error as APIError, { context: { action: 'export_analytics' } })
  }
}

const generateReport = async () => {
  try {
    const response = await fetch('/reports/generate/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      },
      body: JSON.stringify({
        type: 'analytics',
        period: selectedPeriod.value,
        start_date: startDate.value,
        end_date: endDate.value
      })
    })
    
    if (response.ok) {
      await response.json() // Parse response but don't store unused data
      // Handle report generation success
      alert('Report generation started. You will receive an email when it\'s ready.')
    }
  } catch (error) {
    handleApiError(error as APIError, { context: { action: 'generate_report' } })
  }
}

const handleRetry = async () => {
  try {
    await refresh()
  } catch (err) {
    handleApiError(err as APIError, { context: { action: 'retry_analytics_load' } })
  }
}

// Watch for chart type changes
watch([userChartType, enrollmentChartType], () => {
  // Charts will automatically update due to computed properties
})

onMounted(() => {
  refresh()
})
</script>

<style scoped>
.admin-analytics-view {
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

.date-range-selector {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
}

.date-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.period-select, .date-input {
  padding: 0.75rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 1rem;
}

.custom-date-inputs {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.metric-card {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
}

.metric-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.metric-header h3 {
  font-size: 0.875rem;
  font-weight: 500;
  color: #6b7280;
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.metric-icon {
  font-size: 1.5rem;
}

.metric-value {
  font-size: 2rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.metric-change {
  font-size: 0.875rem;
  font-weight: 500;
}

.metric-change.positive {
  color: #10b981;
}

.metric-change.negative {
  color: #ef4444;
}

.metric-change.neutral {
  color: #6b7280;
}

.charts-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
  gap: 2rem;
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

.chart-type-select {
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
}

.chart-content {
  height: 300px;
}

.detailed-analytics {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  margin-bottom: 2rem;
}

.analytics-section {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
}

.analytics-section h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 1.5rem;
}

.course-performance-table {
  overflow-x: auto;
}

.course-performance-table table {
  width: 100%;
  border-collapse: collapse;
}

.course-performance-table th {
  background: #f9fafb;
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: #374151;
  border-bottom: 1px solid #e5e7eb;
}

.course-performance-table td {
  padding: 1rem;
  border-bottom: 1px solid #f3f4f6;
}

.course-row:hover {
  background: #f9fafb;
}

.course-info .course-title {
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.25rem;
}

.course-info .course-instructor {
  font-size: 0.875rem;
  color: #6b7280;
}

.completion-rate {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.completion-bar {
  width: 60px;
  height: 6px;
  background: #f3f4f6;
  border-radius: 3px;
  overflow: hidden;
}

.completion-fill {
  height: 100%;
  background: linear-gradient(135deg, #10b981, #059669);
  transition: width 0.3s ease;
}

.rating {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.stars {
  color: #fbbf24;
  font-size: 0.875rem;
}

.rating-value {
  font-weight: 600;
  color: #1f2937;
}

.revenue {
  font-weight: 600;
  color: #10b981;
}

.engagement-metrics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

.engagement-card {
  background: #f9fafb;
  padding: 1.5rem;
  border-radius: 8px;
  text-align: center;
}

.engagement-card h4 {
  font-size: 0.875rem;
  font-weight: 500;
  color: #6b7280;
  margin-bottom: 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.engagement-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1f2937;
}

.export-section {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
}

.export-section h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 1.5rem;
}

.export-buttons {
  display: flex;
  gap: 1rem;
}

.export-btn {
  padding: 0.75rem 1.5rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  background: white;
  color: #374151;
  cursor: pointer;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.3s ease;
}

.export-btn:hover {
  background: #f9fafb;
  border-color: #f59e0b;
}

.export-btn.primary {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  border-color: transparent;
}

.export-btn.primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(245, 158, 11, 0.4);
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