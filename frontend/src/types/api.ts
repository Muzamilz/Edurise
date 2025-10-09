// User and Authentication Types
export interface User {
  id: string
  email: string
  first_name: string
  last_name: string
  is_teacher: boolean
  is_approved_teacher: boolean
  is_staff: boolean
  is_superuser: boolean
  date_joined: string
  last_login: string
}

export interface UserProfile {
  id: string
  user: User
  tenant: Organization
  avatar?: string
  bio?: string
  phone_number?: string
  date_of_birth?: string
  timezone: string
  language: string
  created_at: string
  updated_at: string
}

export interface Organization {
  id: string
  name: string
  subdomain: string
  logo?: string
  primary_color: string
  secondary_color: string
  subscription_plan: 'basic' | 'pro' | 'enterprise'
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  password: string
  password_confirm: string
  first_name: string
  last_name: string
  is_teacher?: boolean
}

export interface AuthResponse {
  user: User
  tokens: {
    access: string
    refresh: string
  }
}

// Course Types
export interface Course {
  id: string
  title: string
  description: string
  instructor: User
  category: string
  tags: string[]
  thumbnail?: string
  price?: number
  is_public: boolean
  max_students?: number
  duration_weeks: number
  difficulty_level: 'beginner' | 'intermediate' | 'advanced'
  average_rating: number
  total_enrollments: number
  created_at: string
  updated_at: string
}

export interface CourseModule {
  id: string
  course: string
  title: string
  description: string
  content: string
  order: number
  is_published: boolean
  video_url?: string
  materials: string[]
  created_at: string
  updated_at: string
}

export interface LiveClass {
  id: string
  course: string
  title: string
  description: string
  scheduled_at: string
  duration_minutes: number
  status: 'scheduled' | 'live' | 'completed' | 'cancelled'
  zoom_meeting_id?: string
  join_url?: string
  start_url?: string
  password?: string
  recording_url?: string
  recording_password?: string
  created_at: string
  updated_at: string
}

export interface ClassAttendance {
  id: string
  live_class: string
  student: User
  status: 'present' | 'absent' | 'partial' | 'late'
  join_time?: string
  leave_time?: string
  duration_minutes: number
  participation_score: number
  questions_asked: number
  created_at: string
  updated_at: string
}

export interface EngagementMetrics {
  total_students: number
  attendance_rate: number
  average_duration: number
  engagement_score: number
  status_breakdown: {
    present: number
    absent: number
    partial: number
    late: number
  }
  duration_stats: {
    min_duration: number
    max_duration: number
    median_duration: number
    duration_retention_rate: number
  }
  participation_stats: {
    average_participation: number
    total_questions: number
    active_participants: number
    participation_rate: number
  }
}

export interface ClassAnalyticsReport {
  total_students: number
  attendance_rate: number
  average_duration: number
  engagement_score: number
  status_breakdown: {
    present: number
    absent: number
    partial: number
    late: number
  }
  duration_stats: {
    min_duration: number
    max_duration: number
    median_duration: number
    duration_retention_rate: number
  }
  participation_stats: {
    average_participation: number
    total_questions: number
    active_participants: number
    participation_rate: number
  }
  class_info: {
    title: string
    scheduled_at: string
    duration_minutes: number
    status: string
    zoom_meeting_id?: string
  }
  timing_analysis: {
    on_time_students: number
    late_students: number
    peak_join_time?: string
    peak_join_count: number
  }
  recommendations: Array<{
    type: string
    message: string
    priority: 'low' | 'medium' | 'high'
  }>
}

export interface ZoomMeetingInfo {
  id: string
  topic: string
  start_time: string
  duration: number
  join_url: string
  start_url: string
  password?: string
  status: string
}

export interface Enrollment {
  id: string
  student: User
  course: Course
  status: 'active' | 'completed' | 'dropped' | 'suspended'
  progress_percentage: number
  enrolled_at: string
  completed_at?: string
  last_accessed: string
}

export interface CourseReview {
  id: string
  course: string
  student: User
  rating: number
  comment: string
  is_approved: boolean
  created_at: string
  updated_at: string
}

// Payment Types
export interface Payment {
  id: string
  user: User
  course?: Course
  amount: number
  currency: string
  status: 'pending' | 'completed' | 'failed' | 'refunded'
  payment_method: 'stripe' | 'paypal'
  transaction_id?: string
  created_at: string
  updated_at: string
}

// Admin Types
export interface AuditLog {
  id: string
  user: User
  action: string
  model_name: string
  object_id: string
  changes: Record<string, any>
  timestamp: string
  ip_address: string
}

export interface DashboardStats {
  total_users: number
  total_courses: number
  total_enrollments: number
  total_revenue: number
  active_users_today: number
  new_enrollments_today: number
  completion_rate: number
}

// Notification Types
export interface Notification {
  id: string
  user: User
  title: string
  message: string
  type: 'info' | 'success' | 'warning' | 'error'
  is_read: boolean
  created_at: string
}

// AI Types
export interface AIConversation {
  id: string
  user: User
  title: string
  messages: AIMessage[]
  created_at: string
  updated_at: string
}

export interface AIMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
}

// API Request/Response Types
export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface ApiError {
  message: string
  errors?: Record<string, string[]>
  status: number
}

// Filter and Search Types
export interface CourseFilters {
  category?: string
  difficulty_level?: string
  is_public?: boolean
  instructor?: string
  price_min?: number
  price_max?: number
  search?: string
  ordering?: string
}

export interface UserFilters {
  is_teacher?: boolean
  is_approved_teacher?: boolean
  is_staff?: boolean
  search?: string
  ordering?: string
}

export interface EnrollmentFilters {
  status?: string
  course?: string
  student?: string
  search?: string
  ordering?: string
}