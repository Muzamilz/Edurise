import { api } from './api'
import type { AnalyticsFilters } from '@/composables/useAnalytics'

export interface ChartDataPoint {
  label: string
  value: number
  date?: string
  metadata?: Record<string, any>
}

export interface ChartConfig {
  type: 'line' | 'bar' | 'pie' | 'doughnut' | 'area'
  title: string
  subtitle?: string
  xAxisLabel?: string
  yAxisLabel?: string
  colors?: string[]
  showLegend?: boolean
  showTooltips?: boolean
}

/**
 * Analytics service for centralized API data processing and visualization
 */
export class AnalyticsService {
  
  /**
   * Fetch enrollment trends data
   */
  static async getEnrollmentTrends(filters: AnalyticsFilters = {}) {
    const params = new URLSearchParams()
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString())
      }
    })
    
    const response = await api.get(`/analytics/enrollment_trends/?${params}`)
    return response.data
  }
  
  /**
   * Fetch user engagement data
   */
  static async getUserEngagement(filters: AnalyticsFilters = {}) {
    const params = new URLSearchParams()
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString())
      }
    })
    
    const response = await api.get(`/analytics/user_engagement/?${params}`)
    return response.data
  }
  
  /**
   * Fetch financial analytics data
   */
  static async getFinancialAnalytics(filters: AnalyticsFilters = {}) {
    const params = new URLSearchParams()
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString())
      }
    })
    
    const response = await api.get(`/analytics/financial_analytics/?${params}`)
    return response.data
  }
  
  /**
   * Fetch course performance data
   */
  static async getCoursePerformance(filters: AnalyticsFilters = {}) {
    const params = new URLSearchParams()
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString())
      }
    })
    
    const response = await api.get(`/analytics/course_performance/?${params}`)
    return response.data
  }
  
  /**
   * Generate comprehensive report
   */
  static async generateReport(
    type: 'overview' | 'enrollment' | 'financial' | 'course',
    filters: AnalyticsFilters = {},
    format: 'json' | 'csv' | 'pdf' = 'json'
  ) {
    const params = new URLSearchParams({
      type,
      format,
      ...Object.fromEntries(
        Object.entries(filters).filter(([_, value]) => 
          value !== undefined && value !== null && value !== ''
        ).map(([key, value]) => [key, value.toString()])
      )
    })
    
    const response = await api.get(`/reports/generate/?${params}`)
    return response.data
  }
  
  /**
   * Schedule a report for background generation
   */
  static async scheduleReport(
    type: 'overview' | 'enrollment' | 'financial' | 'course',
    email: string,
    filters: AnalyticsFilters = {},
    format: 'json' | 'csv' | 'pdf' = 'pdf'
  ) {
    const response = await api.post('/scheduled-reports/', {
      report_type: type,
      email,
      filters,
      format
    })
    return response.data
  }
  
  /**
   * Get list of scheduled reports
   */
  static async getScheduledReports() {
    const response = await api.get('/scheduled-reports/')
    return response.data
  }
  
  /**
   * Get details of a specific scheduled report
   */
  static async getScheduledReport(reportId: string) {
    const response = await api.get(`/scheduled-reports/${reportId}/`)
    return response.data
  }
  
  /**
   * Download a completed report
   */
  static async downloadReport(reportId: string) {
    const response = await api.get(`/reports/download/${reportId}/`, {
      responseType: 'blob'
    })
    
    // Create download link
    const blob = new Blob([response.data.data || response.data], { type: 'application/pdf' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    
    // Extract filename from response headers or use default
    const contentDisposition = response.headers['content-disposition']
    let filename = `report_${reportId}.csv`
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename="(.+)"/)
      if (filenameMatch) {
        filename = filenameMatch[1]
      }
    }
    
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  }
  
  /**
   * Transform enrollment trend data for chart visualization
   */
  static transformEnrollmentTrendData(data: any[]): {
    chartData: ChartDataPoint[]
    config: ChartConfig
  } {
    const chartData = data.map(item => ({
      label: item.period,
      value: item.total_enrollments,
      date: item.date,
      metadata: {
        active: item.active_enrollments,
        completed: item.completed_enrollments,
        dropped: item.dropped_enrollments,
        completion_rate: item.completion_rate,
        dropout_rate: item.dropout_rate
      }
    }))
    
    const config: ChartConfig = {
      type: 'line',
      title: 'Enrollment Trends',
      xAxisLabel: 'Period',
      yAxisLabel: 'Number of Enrollments',
      colors: ['#3B82F6', '#10B981', '#F59E0B', '#EF4444'],
      showLegend: true,
      showTooltips: true
    }
    
    return { chartData, config }
  }
  
  /**
   * Transform user engagement data for chart visualization
   */
  static transformUserEngagementData(data: any): {
    dailyActiveUsers: { chartData: ChartDataPoint[], config: ChartConfig }
    engagementMetrics: { chartData: ChartDataPoint[], config: ChartConfig }
  } {
    // Daily active users chart
    const dailyActiveUsers = {
      chartData: data.daily_active_users.map((item: any) => ({
        label: new Date(item.date).toLocaleDateString(),
        value: item.active_users,
        date: item.date
      })),
      config: {
        type: 'area' as const,
        title: 'Daily Active Users',
        xAxisLabel: 'Date',
        yAxisLabel: 'Active Users',
        colors: ['#3B82F6'],
        showLegend: false,
        showTooltips: true
      }
    }
    
    // Engagement metrics pie chart
    const engagementMetrics = {
      chartData: [
        {
          label: 'Course Interactions',
          value: data.course_engagement.total_interactions
        },
        {
          label: 'Live Class Attendances',
          value: data.live_class_engagement.total_attendances
        },
        {
          label: 'Completed Courses',
          value: data.course_engagement.courses_completed
        }
      ],
      config: {
        type: 'doughnut' as const,
        title: 'Engagement Breakdown',
        colors: ['#3B82F6', '#10B981', '#F59E0B'],
        showLegend: true,
        showTooltips: true
      }
    }
    
    return { dailyActiveUsers, engagementMetrics }
  }
  
  /**
   * Transform financial data for chart visualization
   */
  static transformFinancialData(data: any): {
    revenueTrend: { chartData: ChartDataPoint[], config: ChartConfig }
    paymentMethods: { chartData: ChartDataPoint[], config: ChartConfig }
    topCourses: { chartData: ChartDataPoint[], config: ChartConfig }
  } {
    // Revenue trend chart
    const revenueTrend = {
      chartData: data.revenue_trend.map((item: any) => ({
        label: item.period,
        value: item.revenue,
        date: item.date,
        metadata: {
          transactions: item.transaction_count,
          customers: item.unique_customers,
          avg_transaction: item.avg_transaction
        }
      })),
      config: {
        type: 'line' as const,
        title: 'Revenue Trend',
        xAxisLabel: 'Period',
        yAxisLabel: `Revenue (${data.revenue_overview.currency})`,
        colors: ['#10B981'],
        showLegend: false,
        showTooltips: true
      }
    }
    
    // Payment methods pie chart
    const paymentMethods = {
      chartData: data.payment_methods.map((item: any) => ({
        label: item.method,
        value: item.revenue,
        metadata: {
          transactions: item.transaction_count,
          percentage: item.percentage
        }
      })),
      config: {
        type: 'pie' as const,
        title: 'Revenue by Payment Method',
        colors: ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'],
        showLegend: true,
        showTooltips: true
      }
    }
    
    // Top courses by revenue
    const topCourses = {
      chartData: data.top_courses_by_revenue.slice(0, 10).map((item: any) => ({
        label: item.course_title.length > 30 
          ? item.course_title.substring(0, 30) + '...' 
          : item.course_title,
        value: item.revenue,
        metadata: {
          enrollments: item.enrollment_count,
          avg_per_enrollment: item.avg_revenue_per_enrollment
        }
      })),
      config: {
        type: 'bar' as const,
        title: 'Top Courses by Revenue',
        xAxisLabel: 'Course',
        yAxisLabel: `Revenue (${data.revenue_overview.currency})`,
        colors: ['#3B82F6'],
        showLegend: false,
        showTooltips: true
      }
    }
    
    return { revenueTrend, paymentMethods, topCourses }
  }
  
  /**
   * Transform course performance data for chart visualization
   */
  static transformCoursePerformanceData(data: any): {
    completionRates: { chartData: ChartDataPoint[], config: ChartConfig }
    enrollmentVsRating: { chartData: ChartDataPoint[], config: ChartConfig }
    performanceIndicators: { chartData: ChartDataPoint[], config: ChartConfig }
  } {
    // Completion rates chart
    const completionRates = {
      chartData: data.course_performance.slice(0, 15).map((item: any) => ({
        label: item.course_title.length > 25 
          ? item.course_title.substring(0, 25) + '...' 
          : item.course_title,
        value: item.metrics.completion_rate,
        metadata: {
          total_enrollments: item.metrics.total_enrollments,
          completed: item.metrics.completed_enrollments,
          avg_rating: item.metrics.avg_rating
        }
      })),
      config: {
        type: 'bar' as const,
        title: 'Course Completion Rates',
        xAxisLabel: 'Course',
        yAxisLabel: 'Completion Rate (%)',
        colors: ['#10B981'],
        showLegend: false,
        showTooltips: true
      }
    }
    
    // Enrollment vs Rating scatter plot (represented as bar chart)
    const enrollmentVsRating = {
      chartData: data.course_performance.slice(0, 10).map((item: any) => ({
        label: item.course_title.length > 20 
          ? item.course_title.substring(0, 20) + '...' 
          : item.course_title,
        value: item.metrics.total_enrollments,
        metadata: {
          rating: item.metrics.avg_rating,
          engagement_score: item.metrics.engagement_score,
          revenue: item.metrics.revenue
        }
      })),
      config: {
        type: 'bar' as const,
        title: 'Enrollment vs Course Rating',
        xAxisLabel: 'Course',
        yAxisLabel: 'Total Enrollments',
        colors: ['#3B82F6'],
        showLegend: false,
        showTooltips: true
      }
    }
    
    // Performance indicators
    const highPerforming = data.course_performance.filter((item: any) => 
      item.performance_indicators.is_high_performing
    ).length
    
    const needsAttention = data.course_performance.filter((item: any) => 
      item.performance_indicators.needs_attention
    ).length
    
    const trending = data.course_performance.filter((item: any) => 
      item.performance_indicators.trending_up
    ).length
    
    const normal = data.course_performance.length - highPerforming - needsAttention
    
    const performanceIndicators = {
      chartData: [
        { label: 'High Performing', value: highPerforming },
        { label: 'Needs Attention', value: needsAttention },
        { label: 'Trending Up', value: trending },
        { label: 'Normal', value: normal }
      ],
      config: {
        type: 'doughnut' as const,
        title: 'Course Performance Distribution',
        colors: ['#10B981', '#EF4444', '#F59E0B', '#6B7280'],
        showLegend: true,
        showTooltips: true
      }
    }
    
    return { completionRates, enrollmentVsRating, performanceIndicators }
  }
  
  /**
   * Calculate key performance indicators
   */
  static calculateKPIs(data: {
    enrollmentTrends?: any
    userEngagement?: any
    financialAnalytics?: any
    coursePerformance?: any
  }) {
    const kpis = []
    
    // Enrollment KPIs
    if (data.enrollmentTrends?.summary) {
      const summary = data.enrollmentTrends.summary
      kpis.push(
        {
          title: 'Total Enrollments',
          value: summary.total_enrollments.toLocaleString(),
          change: '+12%', // This would be calculated from trend data
          trend: 'up',
          icon: '📚'
        },
        {
          title: 'Completion Rate',
          value: `${summary.completion_rate.toFixed(1)}%`,
          change: '+2.3%',
          trend: 'up',
          icon: '✅'
        }
      )
    }
    
    // User engagement KPIs
    if (data.userEngagement?.engagement_overview) {
      const engagement = data.userEngagement.engagement_overview
      kpis.push(
        {
          title: 'Active Users',
          value: engagement.active_users.toLocaleString(),
          change: `+${engagement.new_users}`,
          trend: 'up',
          icon: '👥'
        },
        {
          title: 'Engagement Rate',
          value: `${data.userEngagement.course_engagement.engagement_rate.toFixed(1)}%`,
          change: '+5.2%',
          trend: 'up',
          icon: '📈'
        }
      )
    }
    
    // Financial KPIs
    if (data.financialAnalytics?.revenue_overview) {
      const revenue = data.financialAnalytics.revenue_overview
      kpis.push(
        {
          title: 'Total Revenue',
          value: `${revenue.currency} ${revenue.total_revenue.toLocaleString()}`,
          change: '+18.5%',
          trend: 'up',
          icon: '💰'
        },
        {
          title: 'Success Rate',
          value: `${revenue.success_rate.toFixed(1)}%`,
          change: '+1.2%',
          trend: 'up',
          icon: '✨'
        }
      )
    }
    
    // Course performance KPIs
    if (data.coursePerformance?.summary) {
      const summary = data.coursePerformance.summary
      kpis.push(
        {
          title: 'Avg Course Rating',
          value: `${summary.avg_rating.toFixed(1)}/5`,
          change: '+0.2',
          trend: 'up',
          icon: '⭐'
        },
        {
          title: 'Total Courses',
          value: summary.total_courses.toLocaleString(),
          change: '+3',
          trend: 'up',
          icon: '📖'
        }
      )
    }
    
    return kpis
  }
  
  /**
   * Export data to CSV format
   */
  static exportToCSV(data: any[], filename: string) {
    if (!data.length) return
    
    const headers = Object.keys(data[0])
    const csvContent = [
      headers.join(','),
      ...data.map(row => 
        headers.map(header => {
          const value = row[header]
          return typeof value === 'string' && value.includes(',') 
            ? `"${value}"` 
            : value
        }).join(',')
      )
    ].join('\n')
    
    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${filename}.csv`
    link.click()
    window.URL.revokeObjectURL(url)
  }
  
  /**
   * Format currency values
   */
  static formatCurrency(amount: number, currency: string = 'USD'): string {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency
    }).format(amount)
  }
  
  /**
   * Format percentage values
   */
  static formatPercentage(value: number, decimals: number = 1): string {
    return `${value.toFixed(decimals)}%`
  }
  
  /**
   * Format large numbers with abbreviations
   */
  static formatNumber(num: number): string {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M'
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K'
    }
    return num.toString()
  }
}