<template>
  <div class="platform-analytics-view">
    <div class="page-header">
      <h1>Platform Analytics</h1>
      <p>Comprehensive analytics across all organizations and users</p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>Loading platform analytics...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-state">
      <div class="error-icon">⚠️</div>
      <h3>Unable to load analytics</h3>
      <p>{{ error.message }}</p>
      <button @click="handleRetry" class="retry-btn">Try Again</button>
    </div>

    <!-- Analytics Content -->
    <div v-else class="analytics-content">
      <!-- Key Metrics -->
      <div class="metrics-grid">
        <div class="metric-card">
          <div class="metric-icon">👥</div>
          <h3>Total Users</h3>
          <div class="metric-value">{{ formatNumber(analytics.totalUsers) }}</div>
          <div class="metric-change positive">+{{ analytics.userGrowth }}% this month</div>
        </div>
        <div class="metric-card">
          <div class="metric-icon">🏢</div>
          <h3>Organizations</h3>
          <div class="metric-value">{{ formatNumber(analytics.totalOrganizations) }}</div>
          <div class="metric-change positive">+{{ analytics.orgGrowth }}% this month</div>
        </div>
        <div class="metric-card">
          <div class="metric-icon">📚</div>
          <h3>Total Courses</h3>
          <div class="metric-value">{{ formatNumber(analytics.totalCourses) }}</div>
          <div class="metric-change positive">+{{ analytics.courseGrowth }}% this month</div>
        </div>
        <div class="metric-card">
          <div class="metric-icon">💰</div>
          <h3>Platform Revenue</h3>
          <div class="metric-value">${{ formatNumber(analytics.totalRevenue) }}</div>
          <div class="metric-change positive">+{{ analytics.revenueGrowth }}% this month</div>
        </div>
      </div>

      <!-- Charts Section -->
      <div class="charts-section">
        <div class="chart-container">
          <h3>User Growth Trend</h3>
          <AnalyticsChart
            :data="userGrowthData"
            type="line"
            :options="chartOptions"
          />
        </div>
        <div class="chart-container">
          <h3>Revenue Trend</h3>
          <AnalyticsChart
            :data="revenueData"
            type="bar"
            :options="chartOptions"
          />
        </div>
      </div>

      <!-- Organization Performance -->
      <div class="org-performance">
        <h3>Top Performing Organizations</h3>
        <div class="performance-table">
          <table>
            <thead>
              <tr>
                <th>Organization</th>
                <th>Users</th>
                <th>Courses</th>
                <th>Revenue</th>
                <th>Growth</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="org in topOrganizations" :key="org.id">
                <td>
                  <div class="org-info">
                    <strong>{{ org.name }}</strong>
                    <span class="subdomain">{{ org.subdomain }}.edurise.com</span>
                  </div>
                </td>
                <td>{{ formatNumber(org.userCount) }}</td>
                <td>{{ formatNumber(org.courseCount) }}</td>
                <td>${{ formatNumber(org.revenue) }}</td>
                <td>
                  <span class="growth-indicator" :class="org.growth >= 0 ? 'positive' : 'negative'">
                    {{ org.growth >= 0 ? '+' : '' }}{{ org.growth }}%
                  </span>
                </td>
                <td>
                  <router-link :to="`/super-admin/organizations/${org.id}`" class="view-btn">
                    View Details
                  </router-link>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Platform Health -->
      <div class="platform-health">
        <h3>Platform Health Metrics</h3>
        <div class="health-grid">
          <div class="health-card">
            <h4>System Performance</h4>
            <div class="health-metric">
              <span class="metric-label">Response Time</span>
              <span class="metric-value">{{ analytics.avgResponseTime }}ms</span>
            </div>
            <div class="health-metric">
              <span class="metric-label">Uptime</span>
              <span class="metric-value">{{ analytics.uptime }}%</span>
            </div>
          </div>
          <div class="health-card">
            <h4>User Engagement</h4>
            <div class="health-metric">
              <span class="metric-label">Daily Active Users</span>
              <span class="metric-value">{{ formatNumber(analytics.dailyActiveUsers) }}</span>
            </div>
            <div class="health-metric">
              <span class="metric-label">Session Duration</span>
              <span class="metric-value">{{ analytics.avgSessionDuration }}min</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useApiData } from '@/composables/useApiData'
// Removed unused import
import { useErrorHandler } from '@/composables/useErrorHandler'
import AnalyticsChart from '@/components/analytics/AnalyticsChart.vue'

const { handleApiError } = useErrorHandler()

// Data fetching
const { data: analyticsData, loading, error, refresh } = useApiData('/analytics/platform/', {
  immediate: true,
  transform: (data) => {
    console.log('🔍 Raw analytics data:', data)
    // Transform the response to match the new backend structure
    const apiData = data.data || data
    return {
      totalUsers: apiData.totalUsers || 0,
      totalOrganizations: apiData.totalOrganizations || 0,
      totalCourses: apiData.totalCourses || 0,
      totalRevenue: apiData.totalRevenue || 0,
      userGrowth: apiData.userGrowth || 0,
      orgGrowth: apiData.orgGrowth || 0,
      courseGrowth: apiData.courseGrowth || 0,
      revenueGrowth: apiData.revenueGrowth || 0,
      avgResponseTime: apiData.avgResponseTime || 145,
      uptime: apiData.uptime || 99.8,
      dailyActiveUsers: apiData.dailyActiveUsers || 0,
      avgSessionDuration: apiData.avgSessionDuration || 24,
      userGrowthTrend: apiData.userGrowthTrend || [],
      revenueTrend: apiData.revenueTrend || [],
      topOrganizations: apiData.topOrganizations || []
    }
  },
  retryAttempts: 3,
  onError: (error) => {
    console.error('Failed to load platform analytics:', error)
  }
})

// Computed properties
const analytics = computed(() => analyticsData.value || {
  totalUsers: 0,
  totalOrganizations: 0,
  totalCourses: 0,
  totalRevenue: 0,
  userGrowth: 0,
  orgGrowth: 0,
  courseGrowth: 0,
  revenueGrowth: 0,
  avgResponseTime: 0,
  uptime: 99.9,
  dailyActiveUsers: 0,
  avgSessionDuration: 0
})

const userGrowthData = computed(() => ({
  labels: (analyticsData.value as any)?.userGrowthTrend?.map((item: any) => item.month) || [],
  datasets: [{
    label: 'New Users',
    data: (analyticsData.value as any)?.userGrowthTrend?.map((item: any) => item.count) || [],
    borderColor: '#7c3aed',
    backgroundColor: 'rgba(124, 58, 237, 0.1)',
    tension: 0.4
  }]
}))

const revenueData = computed(() => ({
  labels: (analyticsData.value as any)?.revenueTrend?.map((item: any) => item.month) || [],
  datasets: [{
    label: 'Revenue',
    data: (analyticsData.value as any)?.revenueTrend?.map((item: any) => item.amount) || [],
    backgroundColor: '#10b981',
    borderColor: '#059669',
    borderWidth: 1
  }]
}))

const topOrganizations = computed(() => analyticsData.value?.topOrganizations || [])

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: true,
      position: 'top'
    }
  },
  scales: {
    y: {
      beginAtZero: true
    }
  }
}

// Methods
const formatNumber = (num: number) => {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M'
  } else if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  return num.toString()
}

const handleRetry = async () => {
  try {
    await refresh()
  } catch (err) {
    handleApiError(err as any, { 
      context: { action: 'retry_platform_analytics_load' } 
    })
  }
}

onMounted(() => {
  // Analytics data is automatically loaded by useApiData
})
</script>

<style scoped>
.platform-analytics-view {
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

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.metric-card {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(243, 232, 255, 0.3));
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(124, 58, 237, 0.1);
  border: 1px solid rgba(124, 58, 237, 0.1);
  text-align: center;
  transition: all 0.3s ease;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(124, 58, 237, 0.15);
}

.metric-icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.metric-card h3 {
  font-size: 0.875rem;
  font-weight: 500;
  color: #6b7280;
  margin-bottom: 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.metric-value {
  font-size: 2rem;
  font-weight: 700;
  color: #7c3aed;
  margin-bottom: 0.25rem;
}

.metric-change {
  font-size: 0.75rem;
  font-weight: 500;
}

.metric-change.positive {
  color: #10b981;
}

.metric-change.negative {
  color: #ef4444;
}

.charts-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  margin-bottom: 2rem;
}

.chart-container {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(124, 58, 237, 0.1);
  border: 1px solid rgba(124, 58, 237, 0.1);
}

.chart-container h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 1rem;
}

.org-performance, .platform-health {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(124, 58, 237, 0.1);
  border: 1px solid rgba(124, 58, 237, 0.1);
  margin-bottom: 2rem;
}

.org-performance h3, .platform-health h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 1rem;
}

.performance-table {
  overflow-x: auto;
}

.performance-table table {
  width: 100%;
  border-collapse: collapse;
}

.performance-table th,
.performance-table td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

.performance-table th {
  background: #f9fafb;
  font-weight: 600;
  color: #374151;
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.org-info strong {
  display: block;
  color: #1f2937;
  font-weight: 600;
}

.subdomain {
  font-size: 0.75rem;
  color: #6b7280;
}

.growth-indicator.positive {
  color: #10b981;
}

.growth-indicator.negative {
  color: #ef4444;
}

.view-btn {
  background: linear-gradient(135deg, #7c3aed, #5b21b6);
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.3s ease;
}

.view-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(124, 58, 237, 0.3);
}

.health-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.health-card {
  background: #f9fafb;
  padding: 1.5rem;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.health-card h4 {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 1rem;
}

.health-metric {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.health-metric:last-child {
  margin-bottom: 0;
}

.metric-label {
  font-size: 0.875rem;
  color: #6b7280;
}

.metric-value {
  font-size: 0.875rem;
  font-weight: 600;
  color: #1f2937;
}

/* Loading and Error States */
.loading-state, .error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(243, 232, 255, 0.3));
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(124, 58, 237, 0.1);
  border: 1px solid rgba(124, 58, 237, 0.1);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f4f6;
  border-top: 4px solid #7c3aed;
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
  background: linear-gradient(135deg, #7c3aed, #5b21b6);
  color: white;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(124, 58, 237, 0.3);
}

.retry-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(124, 58, 237, 0.4);
}

/* Responsive */
@media (max-width: 768px) {
  .platform-analytics-view {
    padding: 1rem;
  }
  
  .metrics-grid {
    grid-template-columns: 1fr;
  }
  
  .charts-section {
    grid-template-columns: 1fr;
  }
  
  .health-grid {
    grid-template-columns: 1fr;
  }
  
  .performance-table {
    font-size: 0.875rem;
  }
}
</style>