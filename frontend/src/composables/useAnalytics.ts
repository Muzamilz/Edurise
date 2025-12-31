import { ref, computed, onMounted, readonly } from 'vue'
import { useApiData } from './useApiData'
import { useAuth } from './useAuth'
import { useErrorHandler } from './useErrorHandler'
import { AnalyticsService } from '@/services/analytics'
import type { Ref } from 'vue'

// Analytics types
export interface EnrollmentTrendData {
  period: string
  date: string
  total_enrollments: number
  active_enrollments: number
  completed_enrollments: number
  dropped_enrollments: number
  unique_students: number
  unique_courses: number
  avg_progress: number
  completion_rate: number
  dropout_rate: number
}

export interface UserEngagementData {
  engagement_overview: {
    total_users: number
    active_users: number
    new_users: number
    returning_users: number
  }
  daily_active_users: Array<{
    date: string
    active_users: number
  }>
  course_engagement: {
    total_interactions: number
    avg_progress_gain: number
    courses_completed: number
    engagement_rate: number
  }
  live_class_engagement: {
    total_attendances: number
    unique_attendees: number
    avg_attendance_duration: number
    attendance_rate: number
  }
}

export interface FinancialAnalyticsData {
  revenue_overview: {
    total_revenue: number
    pending_revenue: number
    failed_revenue: number
    refunded_revenue: number
    net_revenue: number
    avg_transaction_value: number
    success_rate: number
    currency: string
  }
  revenue_trend: Array<{
    period: string
    date: string
    revenue: number
    transaction_count: number
    unique_customers: number
    avg_transaction: number
  }>
  subscription_analytics: {
    total_subscriptions: number
    active_subscriptions: number
    churn_rate: number
    mrr: number
    arr: number
    retention_rate: number
  }
  top_courses_by_revenue: Array<{
    course_id: string
    course_title: string
    revenue: number
    enrollment_count: number
    avg_revenue_per_enrollment: number
  }>
  payment_methods: Array<{
    method: string
    transaction_count: number
    revenue: number
    percentage: number
  }>
}

export interface CoursePerformanceData {
  course_performance: Array<{
    course_id: string
    course_title: string
    instructor_name: string
    category: string
    price: number
    is_public: boolean
    metrics: {
      total_enrollments: number
      active_enrollments: number
      completed_enrollments: number
      completion_rate: number
      avg_progress: number
      avg_rating: number
      total_reviews: number
      engagement_score: number
      revenue: number
      recent_enrollments: number
    }
    performance_indicators: {
      is_high_performing: boolean
      needs_attention: boolean
      trending_up: boolean
    }
  }>
  summary: {
    total_courses: number
    avg_completion_rate: number
    avg_rating: number
    total_revenue: number
  }
}

export interface AnalyticsFilters {
  start_date?: string
  end_date?: string
  period?: 'day' | 'week' | 'month'
  course_id?: string
  instructor_id?: string
  category?: string
  user_type?: 'all' | 'student' | 'teacher'
  currency?: string
  limit?: number
}

/**
 * Composable for enrollment trend analytics
 */
export const useEnrollmentTrends = (filters: Ref<AnalyticsFilters> = ref({})) => {
  const { user } = useAuth()
  // const { handleApiError } = useErrorHandler() // Unused for now
  
  const queryParams = computed(() => {
    const params = new URLSearchParams()
    Object.entries(filters.value).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString())
      }
    })
    return params.toString()
  })
  
  const endpoint = computed(() => 
    `/api/v1/analytics/enrollment_trends/?${queryParams.value}`
  )
  
  const {
    data,
    loading,
    error,
    refresh
  } = useApiData<{
    trend_data: EnrollmentTrendData[]
    summary: {
      total_enrollments: number
      total_students: number
      total_courses: number
      avg_progress: number
      completion_rate: number
      period: string
      date_range: {
        start: string
        end: string
      }
    }
  }>(endpoint.value, {
    immediate: !!user.value
  })
  
  return {
    enrollmentTrends: data,
    loading,
    error,
    refresh,
    filters
  }
}

/**
 * Composable for user engagement analytics
 */
export const useUserEngagement = (filters: Ref<AnalyticsFilters> = ref({})) => {
  const { user } = useAuth()
  // const { handleApiError } = useErrorHandler() // Unused for now
  
  const queryParams = computed(() => {
    const params = new URLSearchParams()
    Object.entries(filters.value).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString())
      }
    })
    return params.toString()
  })
  
  const endpoint = computed(() => 
    `/api/v1/analytics/user_engagement/?${queryParams.value}`
  )
  
  const {
    data,
    loading,
    error,
    refresh
  } = useApiData<UserEngagementData>(endpoint.value, {
    immediate: !!user.value
  })
  
  return {
    userEngagement: data,
    loading,
    error,
    refresh,
    filters
  }
}

/**
 * Composable for financial analytics
 */
export const useFinancialAnalytics = (filters: Ref<AnalyticsFilters> = ref({})) => {
  const { user } = useAuth()
  // const { handleApiError } = useErrorHandler() // Unused for now
  
  const queryParams = computed(() => {
    const params = new URLSearchParams()
    Object.entries(filters.value).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString())
      }
    })
    return params.toString()
  })
  
  const endpoint = computed(() => 
    `/api/v1/analytics/financial_analytics/?${queryParams.value}`
  )
  
  const {
    data,
    loading,
    error,
    refresh
  } = useApiData<FinancialAnalyticsData>(endpoint.value, {
    immediate: !!user.value && (user.value.is_staff || user.value.is_superuser)
  })
  
  return {
    financialAnalytics: data,
    loading,
    error,
    refresh,
    filters
  }
}

/**
 * Composable for course performance analytics
 */
export const useCoursePerformance = (filters: Ref<AnalyticsFilters> = ref({})) => {
  const { user } = useAuth()
  // const { handleApiError } = useErrorHandler() // Unused for now
  
  const queryParams = computed(() => {
    const params = new URLSearchParams()
    Object.entries(filters.value).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString())
      }
    })
    return params.toString()
  })
  
  const endpoint = computed(() => 
    `/api/v1/analytics/course_performance/?${queryParams.value}`
  )
  
  const {
    data,
    loading,
    error,
    refresh
  } = useApiData<CoursePerformanceData>(endpoint.value, {
    immediate: !!user.value
  })
  
  return {
    coursePerformance: data,
    loading,
    error,
    refresh,
    filters
  }
}

/**
 * Composable for generating reports
 */
export const useReportGeneration = () => {
  const { user } = useAuth()
  const { handleApiError } = useErrorHandler()
  
  const loading = ref(false)
  const error = ref<string | null>(null)
  const scheduledReports = ref<any[]>([])
  
  const generateReport = async (
    type: 'overview' | 'enrollment' | 'financial' | 'course',
    filters: AnalyticsFilters = {},
    format: 'json' | 'csv' | 'pdf' = 'json'
  ) => {
    if (!user.value) {
      throw new Error('User must be authenticated to generate reports')
    }
    
    loading.value = true
    error.value = null
    
    try {
      const data = await AnalyticsService.generateReport({
        type: type as any,
        timeframe: 'custom',
        format: format as any,
        filters
      })
      return data
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to generate report'
      error.value = errorMessage
      handleApiError(err as any)
      throw err
    } finally {
      loading.value = false
    }
  }
  
  const scheduleReport = async (
    type: 'overview' | 'enrollment' | 'financial' | 'course',
    email: string,
    filters: AnalyticsFilters = {},
    format: 'json' | 'csv' | 'pdf' = 'pdf'
  ) => {
    if (!user.value) {
      throw new Error('User must be authenticated to schedule reports')
    }
    
    loading.value = true
    error.value = null
    
    try {
      const data = await AnalyticsService.createScheduledReport({
        name: `${type} Report`,
        report_type: type,
        schedule: '0 0 * * *', // Daily at midnight
        recipients: [email],
        format: format as any,
        filters
      })
      
      // Refresh scheduled reports list
      await fetchScheduledReports()
      
      return data
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to schedule report'
      error.value = errorMessage
      handleApiError(err as any)
      throw err
    } finally {
      loading.value = false
    }
  }
  
  const fetchScheduledReports = async () => {
    if (!user.value) return
    
    try {
      const data = await AnalyticsService.getScheduledReports()
      scheduledReports.value = data.results || []
    } catch (err) {
      handleApiError(err as any)
    }
  }
  
  const downloadReport = async (reportId: string) => {
    if (!user.value) {
      throw new Error('User must be authenticated to download reports')
    }
    
    try {
      const blob = await AnalyticsService.downloadReport(reportId)
      
      // Handle file download
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      
      // Use default filename
      const filename = `report_${reportId}.csv`
        }
      }
      
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to download report'
      error.value = errorMessage
      handleApiError(err as any)
      throw err
    }
  }
  
  // Auto-fetch scheduled reports on mount
  onMounted(() => {
    if (user.value) {
      fetchScheduledReports()
    }
  })
  
  return {
    generateReport,
    scheduleReport,
    downloadReport,
    fetchScheduledReports,
    scheduledReports: readonly(scheduledReports),
    loading,
    error
  }
}

/**
 * Combined analytics composable for dashboard use
 */
export const useAnalyticsDashboard = (initialFilters: AnalyticsFilters = {}) => {
  const filters = ref<AnalyticsFilters>({
    period: 'month',
    ...initialFilters
  })
  
  const enrollmentTrends = useEnrollmentTrends(filters)
  const userEngagement = useUserEngagement(filters)
  const financialAnalytics = useFinancialAnalytics(filters)
  const coursePerformance = useCoursePerformance(filters)
  const reportGeneration = useReportGeneration()
  
  // Combined loading state
  const isLoading = computed(() => 
    enrollmentTrends.loading.value ||
    userEngagement.loading.value ||
    financialAnalytics.loading.value ||
    coursePerformance.loading.value
  )
  
  // Combined error state
  const hasError = computed(() => 
    enrollmentTrends.error.value ||
    userEngagement.error.value ||
    financialAnalytics.error.value ||
    coursePerformance.error.value
  )
  
  // Refresh all analytics
  const refreshAll = async () => {
    await Promise.all([
      enrollmentTrends.refresh(),
      userEngagement.refresh(),
      financialAnalytics.refresh(),
      coursePerformance.refresh()
    ])
  }
  
  // Update filters for all analytics
  const updateFilters = (newFilters: Partial<AnalyticsFilters>) => {
    filters.value = { ...filters.value, ...newFilters }
  }
  
  // Set date range
  const setDateRange = (startDate: string, endDate: string) => {
    updateFilters({ start_date: startDate, end_date: endDate })
  }
  
  // Set period
  const setPeriod = (period: 'day' | 'week' | 'month') => {
    updateFilters({ period })
  }
  
  return {
    // Data
    enrollmentTrends: enrollmentTrends.enrollmentTrends,
    userEngagement: userEngagement.userEngagement,
    financialAnalytics: financialAnalytics.financialAnalytics,
    coursePerformance: coursePerformance.coursePerformance,
    
    // State
    isLoading,
    hasError,
    filters,
    
    // Actions
    refreshAll,
    updateFilters,
    setDateRange,
    setPeriod,
    
    // Report generation
    generateReport: reportGeneration.generateReport,
    scheduleReport: reportGeneration.scheduleReport,
    downloadReport: reportGeneration.downloadReport,
    scheduledReports: reportGeneration.scheduledReports,
    fetchScheduledReports: reportGeneration.fetchScheduledReports,
    
    // Individual refresh functions
    refreshEnrollmentTrends: enrollmentTrends.refresh,
    refreshUserEngagement: userEngagement.refresh,
    refreshFinancialAnalytics: financialAnalytics.refresh,
    refreshCoursePerformance: coursePerformance.refresh
  }
}