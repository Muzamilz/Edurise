import type { User } from './api'

/**
 * Report Parameters for generating custom reports
 */
export interface ReportParams {
  type: 'user' | 'course' | 'revenue' | 'engagement' | 'custom'
  timeframe: 'day' | 'week' | 'month' | 'quarter' | 'year' | 'custom'
  date_from?: string
  date_to?: string
  format: 'csv' | 'xlsx' | 'pdf' | 'json'
  filters?: Record<string, any>
}

/**
 * Report entity
 */
export interface Report {
  id: string
  name: string
  type: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  created_at: string
  completed_at?: string
  file_url?: string
  file_size?: number
  error_message?: string
  created_by?: User
}

/**
 * Report Status for tracking generation progress
 */
export interface ReportStatus {
  id: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress: number
  message: string
  estimated_completion?: string
}

/**
 * Scheduled Report Configuration
 */
export interface ScheduledReportConfig {
  name: string
  description?: string
  report_type: string
  schedule: string // cron expression
  recipients: string[]
  format: 'csv' | 'xlsx' | 'pdf'
  filters?: Record<string, any>
  enabled?: boolean
}

/**
 * Scheduled Report entity
 */
export interface ScheduledReport {
  id: string
  name: string
  description: string
  report_type: string
  schedule: string // cron expression
  recipients: string[]
  format: 'csv' | 'xlsx' | 'pdf'
  filters: Record<string, any>
  enabled: boolean
  last_run?: string
  next_run: string
  created_at: string
  created_by: User
}

/**
 * Platform-wide Analytics
 */
export interface PlatformAnalytics {
  total_users: number
  active_users: number
  total_courses: number
  total_enrollments: number
  total_revenue: number
  user_growth_rate: number
  course_growth_rate: number
  revenue_growth_rate: number
  engagement_metrics: {
    avg_session_duration: number
    avg_courses_per_user: number
    completion_rate: number
  }
  time_series: Array<{
    date: string
    users: number
    enrollments: number
    revenue: number
  }>
}

/**
 * Teacher-specific Analytics
 */
export interface TeacherAnalytics {
  teacher_id: string
  teacher_name: string
  total_courses: number
  total_students: number
  total_revenue: number
  average_rating: number
  total_reviews: number
  course_completion_rate: number
  student_satisfaction: number
  top_courses: Array<{
    id: string
    title: string
    enrollments: number
    revenue: number
    rating: number
  }>
  revenue_trend: Array<{
    month: string
    revenue: number
  }>
}

/**
 * Student-specific Analytics
 */
export interface StudentAnalytics {
  student_id: string
  student_name: string
  total_enrollments: number
  completed_courses: number
  in_progress_courses: number
  total_learning_hours: number
  certificates_earned: number
  average_progress: number
  learning_streak_days: number
  favorite_categories: string[]
  progress_trend: Array<{
    month: string
    courses_completed: number
    hours_learned: number
  }>
}

/**
 * Course-specific Analytics
 */
export interface CourseAnalytics {
  course_id: string
  course_title: string
  total_enrollments: number
  active_enrollments: number
  completed_enrollments: number
  dropout_rate: number
  average_progress: number
  average_rating: number
  total_reviews: number
  total_revenue: number
  completion_time_avg: number
  engagement_metrics: {
    avg_time_per_module: number
    avg_quiz_score: number
    discussion_participation: number
  }
  enrollment_trend: Array<{
    month: string
    enrollments: number
  }>
  student_demographics: {
    by_country: Record<string, number>
    by_age_group: Record<string, number>
  }
}
