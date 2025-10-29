<template>
  <div class="analytics-dashboard">
    <!-- Dashboard Header -->
    <div class="dashboard-header">
      <div class="header-content">
        <h1 class="dashboard-title">Analytics Dashboard</h1>
        <p class="dashboard-subtitle">
          Comprehensive insights into your platform performance
        </p>
      </div>
      
      <div class="header-actions">
        <div class="filter-controls">
          <!-- Date Range Picker -->
          <div class="date-range-picker">
            <label class="filter-label">Date Range:</label>
            <select 
              v-model="selectedDateRange" 
              @change="updateDateRange"
              class="filter-select"
            >
              <option value="7d">Last 7 days</option>
              <option value="30d">Last 30 days</option>
              <option value="90d">Last 90 days</option>
              <option value="1y">Last year</option>
              <option value="custom">Custom range</option>
            </select>
          </div>
          
          <!-- Period Selector -->
          <div class="period-selector">
            <label class="filter-label">Period:</label>
            <select 
              v-model="selectedPeriod" 
              @change="updatePeriod"
              class="filter-select"
            >
              <option value="day">Daily</option>
              <option value="week">Weekly</option>
              <option value="month">Monthly</option>
            </select>
          </div>
        </div>
        
        <div class="report-controls">
          <button 
            @click="generateReport"
            :disabled="reportLoading"
            class="generate-report-btn"
          >
            <svg v-if="!reportLoading" class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 3l-4-4-4 4m5-10V7a2 2 0 00-2-2H7a2 2 0 00-2-2 2 2 0 00-2 2v2" />
            </svg>
            <svg v-else class="w-4 h-4 mr-2 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            {{ reportLoading ? 'Generating...' : 'Generate Report' }}
          </button>
          
          <button 
            @click="scheduleReport"
            :disabled="reportLoading"
            class="schedule-report-btn"
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Schedule Report
          </button>
          
          <button 
            @click="showScheduledReports = !showScheduledReports"
            class="view-reports-btn"
            :class="{ 'active': showScheduledReports }"
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            View Reports ({{ analytics.scheduledReports.value.length }})
          </button>
        </div>
      </div>
    </div>
    
    <!-- KPI Cards -->
    <div class="kpi-grid">
      <div 
        v-for="kpi in kpis" 
        :key="kpi.title"
        class="kpi-card"
      >
        <div class="kpi-icon">{{ kpi.icon }}</div>
        <div class="kpi-content">
          <h3 class="kpi-title">{{ kpi.title }}</h3>
          <p class="kpi-value">{{ kpi.value }}</p>
          <div class="kpi-change" :class="kpi.trend">
            <svg v-if="kpi.trend === 'up'" class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M3.293 9.707a1 1 0 010-1.414l6-6a1 1 0 011.414 0l6 6a1 1 0 01-1.414 1.414L11 5.414V17a1 1 0 11-2 0V5.414L4.707 9.707a1 1 0 01-1.414 0z" clip-rule="evenodd" />
            </svg>
            <svg v-else class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M16.707 10.293a1 1 0 010 1.414l-6 6a1 1 0 01-1.414 0l-6-6a1 1 0 111.414-1.414L9 14.586V3a1 1 0 012 0v11.586l4.293-4.293a1 1 0 011.414 0z" clip-rule="evenodd" />
            </svg>
            <span>{{ kpi.change }}</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Charts Grid -->
    <div class="charts-grid">
      <!-- Enrollment Trends -->
      <div class="chart-section">
        <AnalyticsChart
          :data="transformedEnrollmentData"
          :type="enrollmentChartConfig.type === 'area' ? 'line' : enrollmentChartConfig.type"
          :options="enrollmentChartOptions"
        />
      </div>
      
      <!-- User Engagement -->
      <div class="chart-section">
        <AnalyticsChart
          :data="transformedEngagementData"
          :type="engagementChartConfig.type === 'area' ? 'line' : engagementChartConfig.type"
          :options="engagementChartOptions"
        />
      </div>
      
      <!-- Financial Analytics (Admin/SuperAdmin only) -->
      <div v-if="canViewFinancials" class="chart-section">
        <AnalyticsChart
          :data="transformedRevenueData"
          :type="revenueChartConfig.type === 'area' ? 'line' : revenueChartConfig.type"
          :options="revenueChartOptions"
        />
      </div>
      
      <!-- Course Performance -->
      <div class="chart-section">
        <AnalyticsChart
          :data="transformedCoursePerformanceData"
          :type="coursePerformanceChartConfig.type === 'area' ? 'line' : coursePerformanceChartConfig.type"
          :options="coursePerformanceChartOptions"
        />
      </div>
      
      <!-- Additional Charts for Financial Data -->
      <div v-if="canViewFinancials && transformedPaymentMethodsData.datasets[0]?.data?.length" class="chart-section">
        <AnalyticsChart
          :data="transformedPaymentMethodsData"
          :type="paymentMethodsChartConfig.type === 'area' ? 'pie' : paymentMethodsChartConfig.type"
          :options="paymentMethodsChartOptions"
        />
      </div>
      
      <!-- Top Courses by Revenue -->
      <div v-if="canViewFinancials && transformedTopCoursesData.datasets[0]?.data?.length" class="chart-section">
        <AnalyticsChart
          :data="transformedTopCoursesData"
          :type="topCoursesChartConfig.type === 'area' ? 'bar' : topCoursesChartConfig.type"
          :options="topCoursesChartOptions"
        />
      </div>
    </div>
    
    <!-- Scheduled Reports Section -->
    <div v-if="showScheduledReports" class="scheduled-reports-section">
      <div class="section-header">
        <h2 class="section-title">Scheduled Reports</h2>
        <button 
          @click="analytics.fetchScheduledReports()"
          class="refresh-reports-btn"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Refresh
        </button>
      </div>
      
      <div class="reports-grid">
        <div 
          v-for="report in analytics.scheduledReports.value" 
          :key="report.id"
          class="report-card"
        >
          <div class="report-header">
            <h4 class="report-title">{{ report.report_type }} Report</h4>
            <span 
              class="report-status"
              :class="report.status"
            >
              {{ report.status }}
            </span>
          </div>
          
          <div class="report-details">
            <p class="report-date">
              Created: {{ new Date(report.created_at).toLocaleDateString() }}
            </p>
            <p v-if="report.completed_at" class="report-date">
              Completed: {{ new Date(report.completed_at).toLocaleDateString() }}
            </p>
            <p v-if="report.estimated_completion" class="report-date">
              ETA: {{ new Date(report.estimated_completion).toLocaleDateString() }}
            </p>
          </div>
          
          <div class="report-actions">
            <button 
              v-if="report.status === 'completed' && report.download_url"
              @click="downloadReport(report.id)"
              class="download-btn"
            >
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Download
            </button>
            <span v-else-if="report.status === 'processing'" class="processing-indicator">
              <svg class="w-4 h-4 animate-spin mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Processing...
            </span>
            <span v-else-if="report.status === 'failed'" class="error-indicator">
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Failed
            </span>
          </div>
        </div>
        
        <div v-if="!analytics.scheduledReports.value.length" class="no-reports">
          <svg class="w-12 h-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p class="text-gray-500">No scheduled reports found</p>
        </div>
      </div>
    </div>

    <!-- Data Tables -->
    <div class="data-tables">
      <div class="table-section">
        <h3 class="table-title">Recent Enrollment Trends</h3>
        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>Period</th>
                <th>Total Enrollments</th>
                <th>Completion Rate</th>
                <th>Avg Progress</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in recentEnrollmentData" :key="item.period">
                <td>{{ item.period }}</td>
                <td>{{ item.total_enrollments.toLocaleString() }}</td>
                <td>{{ item.completion_rate.toFixed(1) }}%</td>
                <td>{{ item.avg_progress.toFixed(1) }}%</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      
      <div v-if="canViewFinancials" class="table-section">
        <h3 class="table-title">Revenue Breakdown</h3>
        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>Period</th>
                <th>Revenue</th>
                <th>Transactions</th>
                <th>Avg Transaction</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in recentRevenueData" :key="item.period">
                <td>{{ item.period }}</td>
                <td>${{ item.revenue.toLocaleString() }}</td>
                <td>{{ item.transaction_count.toLocaleString() }}</td>
                <td>${{ item.avg_transaction.toFixed(2) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAnalyticsDashboard } from '@/composables/useAnalytics'
import { useAuth } from '@/composables/useAuth'
import { useToast } from '@/composables/useToast'
import { AnalyticsService } from '@/services/analytics'
import AnalyticsChart from './AnalyticsChart.vue'

const { user } = useAuth()
const { success, error: showError } = useToast()

// Date range and period controls
const selectedDateRange = ref('30d')
const selectedPeriod = ref('month')
const reportLoading = ref(false)
const showScheduledReports = ref(false)

// Initialize analytics dashboard
const analytics = useAnalyticsDashboard({
  period: selectedPeriod.value as 'month' | 'week' | 'day'
})

// Computed properties for permissions
const canViewFinancials = computed(() => 
  user.value?.is_staff || user.value?.is_superuser
)

// Chart data transformations
const enrollmentTransformed = computed(() => {
  if (!analytics.enrollmentTrends.value?.trend_data) {
    return AnalyticsService.transformEnrollmentTrendData([])
  }
  return AnalyticsService.transformEnrollmentTrendData(
    analytics.enrollmentTrends.value.trend_data
  )
})

const transformedEnrollmentData = computed(() => ({
  labels: enrollmentTransformed.value.chartData.map(item => item.label),
  datasets: [{
    label: 'Enrollments',
    data: enrollmentTransformed.value.chartData.map(item => item.value),
    backgroundColor: '#3B82F6',
    borderColor: '#3B82F6',
    borderWidth: 2,
    tension: 0.4
  }]
}))

const enrollmentChartConfig = computed(() => enrollmentTransformed.value.config)

const enrollmentChartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: enrollmentChartConfig.value.showLegend ?? true,
      position: 'top'
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      title: {
        display: true,
        text: enrollmentChartConfig.value.yAxisLabel
      }
    },
    x: {
      title: {
        display: true,
        text: enrollmentChartConfig.value.xAxisLabel
      }
    }
  }
}))

const engagementTransformed = computed(() => {
  if (!analytics.userEngagement.value?.daily_active_users) {
    return AnalyticsService.transformUserEngagementData({
      daily_active_users: [],
      course_engagement: {},
      live_class_engagement: {}
    })
  }
  return AnalyticsService.transformUserEngagementData(
    analytics.userEngagement.value
  )
})

const transformedEngagementData = computed(() => ({
  labels: engagementTransformed.value.dailyActiveUsers.chartData.map(item => item.label),
  datasets: [{
    label: 'Daily Active Users',
    data: engagementTransformed.value.dailyActiveUsers.chartData.map(item => item.value),
    backgroundColor: '#10B981',
    borderColor: '#10B981',
    borderWidth: 2,
    tension: 0.4
  }]
}))

const engagementChartConfig = computed(() => engagementTransformed.value.dailyActiveUsers.config)

const engagementChartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: engagementChartConfig.value.showLegend ?? true,
      position: 'top'
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      title: {
        display: true,
        text: engagementChartConfig.value.yAxisLabel
      }
    },
    x: {
      title: {
        display: true,
        text: engagementChartConfig.value.xAxisLabel
      }
    }
  }
}))

const revenueTransformed = computed(() => {
  if (!analytics.financialAnalytics.value?.revenue_trend) {
    return AnalyticsService.transformFinancialData({
      revenue_trend: [],
      revenue_overview: { currency: 'USD' },
      payment_methods: [],
      top_courses_by_revenue: []
    })
  }
  return AnalyticsService.transformFinancialData(
    analytics.financialAnalytics.value
  )
})

const transformedRevenueData = computed(() => ({
  labels: revenueTransformed.value.revenueTrend.chartData.map(item => item.label),
  datasets: [{
    label: 'Revenue',
    data: revenueTransformed.value.revenueTrend.chartData.map(item => item.value),
    backgroundColor: '#F59E0B',
    borderColor: '#F59E0B',
    borderWidth: 2,
    tension: 0.4
  }]
}))

const revenueChartConfig = computed(() => revenueTransformed.value.revenueTrend.config)

const revenueChartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: revenueChartConfig.value.showLegend ?? true,
      position: 'top'
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      title: {
        display: true,
        text: revenueChartConfig.value.yAxisLabel
      }
    },
    x: {
      title: {
        display: true,
        text: revenueChartConfig.value.xAxisLabel
      }
    }
  }
}))

const transformedPaymentMethodsData = computed(() => ({
  labels: revenueTransformed.value.paymentMethods.chartData.map(item => item.label),
  datasets: [{
    label: 'Payment Methods',
    data: revenueTransformed.value.paymentMethods.chartData.map(item => item.value),
    backgroundColor: ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'],
    borderWidth: 1
  }]
}))

const paymentMethodsChartConfig = computed(() => revenueTransformed.value.paymentMethods.config)

const paymentMethodsChartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: paymentMethodsChartConfig.value.showLegend ?? true,
      position: 'right'
    }
  }
}))

const transformedTopCoursesData = computed(() => ({
  labels: revenueTransformed.value.topCourses.chartData.map(item => item.label),
  datasets: [{
    label: 'Revenue',
    data: revenueTransformed.value.topCourses.chartData.map(item => item.value),
    backgroundColor: '#3B82F6',
    borderColor: '#3B82F6',
    borderWidth: 1
  }]
}))

const topCoursesChartConfig = computed(() => revenueTransformed.value.topCourses.config)

const topCoursesChartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: topCoursesChartConfig.value.showLegend ?? true,
      position: 'top'
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      title: {
        display: true,
        text: topCoursesChartConfig.value.yAxisLabel
      }
    },
    x: {
      title: {
        display: true,
        text: topCoursesChartConfig.value.xAxisLabel
      }
    }
  }
}))

const coursePerformanceTransformed = computed(() => {
  if (!analytics.coursePerformance.value?.course_performance) {
    return AnalyticsService.transformCoursePerformanceData({
      course_performance: [],
      summary: {}
    })
  }
  return AnalyticsService.transformCoursePerformanceData(
    analytics.coursePerformance.value
  )
})

const transformedCoursePerformanceData = computed(() => ({
  labels: coursePerformanceTransformed.value.completionRates.chartData.map(item => item.label),
  datasets: [{
    label: 'Completion Rate',
    data: coursePerformanceTransformed.value.completionRates.chartData.map(item => item.value),
    backgroundColor: '#10B981',
    borderColor: '#10B981',
    borderWidth: 2
  }]
}))

const coursePerformanceChartConfig = computed(() => coursePerformanceTransformed.value.completionRates.config)

const coursePerformanceChartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: coursePerformanceChartConfig.value.showLegend ?? true,
      position: 'top'
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      title: {
        display: true,
        text: coursePerformanceChartConfig.value.yAxisLabel
      }
    },
    x: {
      title: {
        display: true,
        text: coursePerformanceChartConfig.value.xAxisLabel
      }
    }
  }
}))

// KPIs calculation
const kpis = computed(() => {
  return AnalyticsService.calculateKPIs({
    enrollmentTrends: analytics.enrollmentTrends.value,
    userEngagement: analytics.userEngagement.value,
    financialAnalytics: analytics.financialAnalytics.value,
    coursePerformance: analytics.coursePerformance.value
  })
})

// Table data
const recentEnrollmentData = computed(() => {
  return analytics.enrollmentTrends.value?.trend_data?.slice(-5) || []
})

const recentRevenueData = computed(() => {
  return analytics.financialAnalytics.value?.revenue_trend?.slice(-5) || []
})

// Methods
const updateDateRange = () => {
  const now = new Date()
  let startDate: Date
  
  switch (selectedDateRange.value) {
    case '7d':
      startDate = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
      break
    case '30d':
      startDate = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000)
      break
    case '90d':
      startDate = new Date(now.getTime() - 90 * 24 * 60 * 60 * 1000)
      break
    case '1y':
      startDate = new Date(now.getTime() - 365 * 24 * 60 * 60 * 1000)
      break
    default:
      return // Custom range - would need date picker implementation
  }
  
  analytics.setDateRange(
    startDate.toISOString(),
    now.toISOString()
  )
}

const updatePeriod = () => {
  analytics.setPeriod(selectedPeriod.value as 'day' | 'week' | 'month')
}

const generateReport = async () => {
  reportLoading.value = true
  
  try {
    const report = await analytics.generateReport('overview', analytics.filters.value, 'json')
    
    // Create and download report
    const blob = new Blob([JSON.stringify(report, null, 2)], { 
      type: 'application/json' 
    })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `analytics_report_${new Date().toISOString().split('T')[0]}.json`
    link.click()
    URL.revokeObjectURL(url)
    
    success('Report generated successfully')
  } catch (error) {
    showError('Failed to generate report')
  } finally {
    reportLoading.value = false
  }
}

const scheduleReport = async () => {
  if (!user.value?.email) {
    showError('User email not available')
    return
  }
  
  reportLoading.value = true
  
  try {
    await analytics.scheduleReport(
      'overview',
      user.value.email,
      analytics.filters.value,
      'pdf'
    )
    
    success('Report scheduled successfully. You will receive an email when ready.')
    showScheduledReports.value = true
  } catch (error) {
    showError('Failed to schedule report')
  } finally {
    reportLoading.value = false
  }
}

const downloadReport = async (reportId: string) => {
  try {
    await analytics.downloadReport(reportId)
    success('Report downloaded successfully')
  } catch (error) {
    showError('Failed to download report')
  }
}

// Export methods (commented out as they're not currently used)
// const exportEnrollmentData = (data: any[]) => {
//   AnalyticsService.exportToCSV(data, 'enrollment_trends')
// }

// const exportEngagementData = (data: any[]) => {
//   AnalyticsService.exportToCSV(data, 'user_engagement')
// }

// const exportFinancialData = (data: any[]) => {
//   AnalyticsService.exportToCSV(data, 'financial_analytics')
// }

// const exportCourseData = (data: any[]) => {
//   AnalyticsService.exportToCSV(data, 'course_performance')
// }

// const exportPaymentMethodsData = (data: any[]) => {
//   AnalyticsService.exportToCSV(data, 'payment_methods')
// }

// const exportTopCoursesData = (data: any[]) => {
//   AnalyticsService.exportToCSV(data, 'top_courses_revenue')
// }

// Initialize
onMounted(() => {
  updateDateRange()
})
</script>

<style scoped>
.analytics-dashboard {
  @apply space-y-8;
}

.dashboard-header {
  @apply flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0;
}

.header-content {
  @apply flex-1;
}

.dashboard-title {
  @apply text-3xl font-bold text-gray-900;
}

.dashboard-subtitle {
  @apply text-gray-600 mt-2;
}

.header-actions {
  @apply flex flex-col sm:flex-row items-start sm:items-center space-y-4 sm:space-y-0 sm:space-x-4;
}

.filter-controls {
  @apply flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-4;
}

.date-range-picker,
.period-selector {
  @apply flex items-center space-x-2;
}

.filter-label {
  @apply text-sm font-medium text-gray-700 whitespace-nowrap;
}

.filter-select {
  @apply border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500;
}

.report-controls {
  @apply flex flex-wrap gap-2;
}

.generate-report-btn {
  @apply inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed;
}

.schedule-report-btn {
  @apply inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed;
}

.view-reports-btn {
  @apply inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500;
}

.view-reports-btn.active {
  @apply bg-blue-50 border-blue-300 text-blue-700;
}

.scheduled-reports-section {
  @apply bg-white rounded-lg shadow-sm border border-gray-200 p-6;
}

.section-header {
  @apply flex justify-between items-center mb-6;
}

.section-title {
  @apply text-xl font-semibold text-gray-900;
}

.refresh-reports-btn {
  @apply inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500;
}

.reports-grid {
  @apply grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4;
}

.report-card {
  @apply border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow;
}

.report-header {
  @apply flex justify-between items-start mb-3;
}

.report-title {
  @apply font-medium text-gray-900 capitalize;
}

.report-status {
  @apply px-2 py-1 text-xs font-medium rounded-full;
}

.report-status.completed {
  @apply bg-green-100 text-green-800;
}

.report-status.processing {
  @apply bg-yellow-100 text-yellow-800;
}

.report-status.failed {
  @apply bg-red-100 text-red-800;
}

.report-status.scheduled {
  @apply bg-blue-100 text-blue-800;
}

.report-details {
  @apply space-y-1 mb-4;
}

.report-date {
  @apply text-sm text-gray-600;
}

.report-actions {
  @apply flex justify-end;
}

.download-btn {
  @apply inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500;
}

.processing-indicator,
.error-indicator {
  @apply inline-flex items-center text-sm;
}

.processing-indicator {
  @apply text-yellow-600;
}

.error-indicator {
  @apply text-red-600;
}

.no-reports {
  @apply col-span-full flex flex-col items-center justify-center py-12 text-center;
}

.kpi-grid {
  @apply grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6;
}

.kpi-card {
  @apply bg-white rounded-lg shadow-sm border border-gray-200 p-6 flex items-center space-x-4;
}

.kpi-icon {
  @apply text-3xl;
}

.kpi-content {
  @apply flex-1;
}

.kpi-title {
  @apply text-sm font-medium text-gray-500 uppercase tracking-wide;
}

.kpi-value {
  @apply text-2xl font-bold text-gray-900 mt-1;
}

.kpi-change {
  @apply flex items-center mt-2 text-sm;
}

.kpi-change.up {
  @apply text-green-600;
}

.kpi-change.down {
  @apply text-red-600;
}

.charts-grid {
  @apply grid grid-cols-1 lg:grid-cols-2 gap-8;
}

.chart-section {
  @apply col-span-1;
}

.data-tables {
  @apply grid grid-cols-1 lg:grid-cols-2 gap-8;
}

.table-section {
  @apply bg-white rounded-lg shadow-sm border border-gray-200 p-6;
}

.table-title {
  @apply text-lg font-semibold text-gray-900 mb-4;
}

.table-container {
  @apply overflow-x-auto;
}

.data-table {
  @apply min-w-full divide-y divide-gray-200;
}

.data-table th {
  @apply px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider;
}

.data-table td {
  @apply px-6 py-4 whitespace-nowrap text-sm text-gray-900;
}

.data-table tbody tr:nth-child(even) {
  @apply bg-gray-50;
}
</style>