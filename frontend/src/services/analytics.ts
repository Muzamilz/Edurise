import { api } from './api'
import type { AnalyticsFilters } from '@/composables/useAnalytics'
import type {
  Report,
  ReportParams,
  ReportStatus,
  ScheduledReport,
  ScheduledReportConfig,
  PlatformAnalytics,
  TeacherAnalytics,
  StudentAnalytics,
  CourseAnalytics
} from '../types/analytics'
import type { PaginatedResponse } from '../types/api'

export interface ChartDataPoint {
  label: string
  value: number
  date?: string
  metadata?: Record<string, string | number | boolean>
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
 * Enrollment trend data item
 */
export interface EnrollmentTrendItem {
  period: string
  date: string
  total_enrollments: number
  active_enrollments: number
  completed_enrollments: number
  dropped_enrollments: number
  completion_rate: number
  dropout_rate: number
}

/**
 * Enrollment trends with summary
 */
export interface EnrollmentTrends {
  summary: {
    total_enrollments: number
    growth_rate: number
    completion_rate: number
  }
  trends: EnrollmentTrendItem[]
}

/**
 * User engagement data structure
 */
export interface UserEngagementData {
  engagement_overview: {
    total_active_users: number
    engagement_rate: number
    active_users: number
    new_users: number
  }
  daily_active_users: Array<{
    date: string
    active_users: number
  }>
  engagement_metrics: Record<string, number>
  course_engagement: {
    total_interactions: number
    courses_completed: number
    engagement_rate: number
  }
  live_class_engagement: {
    total_attendances: number
  }
}

/**
 * Financial data structure
 */
export interface FinancialData {
  revenue_overview: {
    currency: string
    total_revenue: number
    success_rate: number
  }
  revenue_trend: Array<{
    period: string
    date: string
    revenue: number
    transaction_count: number
    unique_customers: number
    avg_transaction: number
  }>
  payment_methods: Array<{
    method: string
    revenue: number
    transaction_count: number
    percentage: number
  }>
  top_courses_by_revenue: Array<{
    course_title: string
    revenue: number
    enrollment_count: number
    avg_revenue_per_enrollment: number
  }>
}

/**
 * Course performance data structure
 */
export interface CoursePerformanceData {
  summary: {
    avg_completion_rate: number
    total_courses: number
    avg_rating: number
  }
  course_performance: Array<{
    course_title: string
    completion_rate: number
    enrollments: number
    rating: number
    metrics: {
      completion_rate: number
      total_enrollments: number
      completed_enrollments: number
      avg_rating: number
      engagement_score: number
      revenue: number
    }
    performance_indicators: {
      is_high_performing: boolean
      needs_attention: boolean
      trending_up: boolean
    }
  }>
}

/**
 * Analytics service for centralized API data processing and visualization
 */
export class AnalyticsService {
  
  // ===== Export Functionality =====
  
  /**
   * Export analytics data in specified format
   * @param format - Export format (csv or xlsx)
   * @param filters - Optional filters to apply to the export
   * @returns Blob containing the exported data
   */
  static async exportData(format: 'csv' | 'xlsx', filters?: Record<string, string | number | boolean>): Promise<Blob> {
    try {
      const params = new URLSearchParams({ format, ...filters as Record<string, string> })
      const response = await api.get(`/analytics/export/?${params}`, {
        responseType: 'blob'
      })
      return response.data as unknown as Blob
    } catch (error) {
      console.error('Failed to export analytics data:', error)
      throw error
    }
  }
  
  // ===== Report Generation =====
  
  /**
   * Generate a custom report
   * @param params - Report parameters including type, timeframe, and format
   * @returns Generated report
   */
  static async generateReport(params: ReportParams): Promise<Report> {
    try {
      const response = await api.post<Report>('/reports/generate/', params)
      return response.data.data
    } catch (error) {
      console.error('Failed to generate report:', error)
      throw error
    }
  }
  
  /**
   * Get the status of a report generation
   * @param reportId - ID of the report
   * @returns Report status with progress information
   */
  static async getReportStatus(reportId: string): Promise<ReportStatus> {
    try {
      const response = await api.get<ReportStatus>(`/reports/${reportId}/status/`)
      return response.data.data
    } catch (error) {
      console.error(`Failed to get report status for ${reportId}:`, error)
      throw error
    }
  }
  
  /**
   * Download a completed report
   * @param reportId - ID of the report to download
   * @returns Blob containing the report file
   */
  static async downloadReport(reportId: string): Promise<Blob> {
    try {
      const response = await api.get(`/reports/download/${reportId}/`, {
        responseType: 'blob'
      })
      return response.data as unknown as Blob
    } catch (error) {
      console.error(`Failed to download report ${reportId}:`, error)
      throw error
    }
  }
  
  // ===== Scheduled Reports =====
  
  /**
   * Create a scheduled report
   * @param config - Scheduled report configuration
   * @returns Created scheduled report
   */
  static async createScheduledReport(config: ScheduledReportConfig): Promise<ScheduledReport> {
    try {
      const response = await api.post<ScheduledReport>('/scheduled-reports/', config)
      return response.data.data
    } catch (error) {
      console.error('Failed to create scheduled report:', error)
      throw error
    }
  }
  
  /**
   * Get all scheduled reports
   * @returns Paginated list of scheduled reports
   */
  static async getScheduledReports(): Promise<PaginatedResponse<ScheduledReport>> {
    try {
      const response = await api.get<PaginatedResponse<ScheduledReport>>('/scheduled-reports/')
      return response.data.data
    } catch (error) {
      console.error('Failed to fetch scheduled reports:', error)
      throw error
    }
  }
  
  /**
   * Update a scheduled report
   * @param id - Scheduled report ID
   * @param config - Updated configuration
   * @returns Updated scheduled report
   */
  static async updateScheduledReport(id: string, config: Partial<ScheduledReportConfig>): Promise<ScheduledReport> {
    try {
      const response = await api.patch<ScheduledReport>(`/scheduled-reports/${id}/`, config)
      return response.data.data
    } catch (error) {
      console.error(`Failed to update scheduled report ${id}:`, error)
      throw error
    }
  }
  
  /**
   * Delete a scheduled report
   * @param id - Scheduled report ID to delete
   */
  static async deleteScheduledReport(id: string): Promise<void> {
    try {
      await api.delete(`/scheduled-reports/${id}/`)
    } catch (error) {
      console.error(`Failed to delete scheduled report ${id}:`, error)
      throw error
    }
  }
  
  // ===== Analytics Overview Methods =====
  
  /**
   * Get platform-wide analytics
   * @param timeframe - Optional timeframe filter
   * @returns Platform analytics data
   */
  static async getPlatformAnalytics(timeframe?: string): Promise<PlatformAnalytics> {
    try {
      const params = timeframe ? { timeframe } : {}
      const response = await api.get<PlatformAnalytics>('/analytics/platform-overview/', { params })
      return response.data.data
    } catch (error) {
      console.error('Failed to fetch platform analytics:', error)
      throw error
    }
  }
  
  /**
   * Get teacher-specific analytics
   * @param teacherId - Optional teacher ID (defaults to current user if teacher)
   * @returns Teacher analytics data
   */
  static async getTeacherAnalytics(teacherId?: string): Promise<TeacherAnalytics> {
    try {
      const endpoint = teacherId 
        ? `/analytics/teacher/${teacherId}/` 
        : '/analytics/teacher/'
      const response = await api.get<TeacherAnalytics>(endpoint)
      return response.data.data
    } catch (error) {
      console.error('Failed to fetch teacher analytics:', error)
      throw error
    }
  }
  
  /**
   * Get student-specific analytics
   * @param studentId - Optional student ID (defaults to current user if student)
   * @returns Student analytics data
   */
  static async getStudentAnalytics(studentId?: string): Promise<StudentAnalytics> {
    try {
      const endpoint = studentId 
        ? `/analytics/student/${studentId}/` 
        : '/analytics/student/'
      const response = await api.get<StudentAnalytics>(endpoint)
      return response.data.data
    } catch (error) {
      console.error('Failed to fetch student analytics:', error)
      throw error
    }
  }
  
  /**
   * Get course-specific analytics
   * @param courseId - Course ID
   * @returns Course analytics data
   */
  static async getCourseAnalytics(courseId: string): Promise<CourseAnalytics> {
    try {
      const response = await api.get<CourseAnalytics>(`/analytics/course/${courseId}/`)
      return response.data.data
    } catch (error) {
      console.error(`Failed to fetch course analytics for ${courseId}:`, error)
      throw error
    }
  }
  
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
   * Get details of a specific scheduled report
   * @param reportId - Scheduled report ID
   * @returns Scheduled report details
   */
  static async getScheduledReport(reportId: string): Promise<ScheduledReport> {
    try {
      const response = await api.get<ScheduledReport>(`/scheduled-reports/${reportId}/`)
      return response.data.data
    } catch (error) {
      console.error(`Failed to fetch scheduled report ${reportId}:`, error)
      throw error
    }
  }
  
  /**
   * Download a completed report and trigger browser download
   * @param reportId - ID of the report to download
   * @param filename - Optional custom filename
   */
  static async downloadReportFile(reportId: string, filename?: string) {
    try {
      const blob = await this.downloadReport(reportId)
      
      // Create download link
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = filename || `report_${reportId}.csv`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error(`Failed to download report file ${reportId}:`, error)
      throw error
    }
  }
  
  /**
   * Transform enrollment trend data for chart visualization
   * @param data - Array of enrollment trend items
   * @returns Chart data and configuration
   */
  static transformEnrollmentTrendData(data: EnrollmentTrendItem[]): {
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
   * @param data - User engagement data
   * @returns Chart data and configuration for daily active users and engagement metrics
   */
  static transformUserEngagementData(data: UserEngagementData): {
    dailyActiveUsers: { chartData: ChartDataPoint[], config: ChartConfig }
    engagementMetrics: { chartData: ChartDataPoint[], config: ChartConfig }
  } {
    // Daily active users chart
    const dailyActiveUsers = {
      chartData: data.daily_active_users.map(item => ({
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
   * @param data - Financial data
   * @returns Chart data and configuration for revenue trends, payment methods, and top courses
   */
  static transformFinancialData(data: FinancialData): {
    revenueTrend: { chartData: ChartDataPoint[], config: ChartConfig }
    paymentMethods: { chartData: ChartDataPoint[], config: ChartConfig }
    topCourses: { chartData: ChartDataPoint[], config: ChartConfig }
  } {
    // Revenue trend chart
    const revenueTrend = {
      chartData: data.revenue_trend.map(item => ({
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
      chartData: data.payment_methods.map(item => ({
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
      chartData: data.top_courses_by_revenue.slice(0, 10).map(item => ({
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
   * @param data - Course performance data
   * @returns Chart data and configuration for completion rates, enrollment vs rating, and performance indicators
   */
  static transformCoursePerformanceData(data: CoursePerformanceData): {
    completionRates: { chartData: ChartDataPoint[], config: ChartConfig }
    enrollmentVsRating: { chartData: ChartDataPoint[], config: ChartConfig }
    performanceIndicators: { chartData: ChartDataPoint[], config: ChartConfig }
  } {
    // Completion rates chart
    const completionRates = {
      chartData: data.course_performance.slice(0, 15).map(item => ({
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
      chartData: data.course_performance.slice(0, 10).map(item => ({
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
    const highPerforming = data.course_performance.filter(item => 
      item.performance_indicators.is_high_performing
    ).length
    
    const needsAttention = data.course_performance.filter(item => 
      item.performance_indicators.needs_attention
    ).length
    
    const trending = data.course_performance.filter(item => 
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
   * @param data - Analytics data from various sources
   * @returns Array of KPI objects
   */
  static calculateKPIs(data: {
    enrollmentTrends?: EnrollmentTrends
    userEngagement?: UserEngagementData
    financialAnalytics?: FinancialData
    coursePerformance?: CoursePerformanceData
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
   * @param data - Array of data objects to export
   * @param filename - Name of the CSV file
   */
  static exportToCSV(data: Record<string, unknown>[], filename: string) {
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