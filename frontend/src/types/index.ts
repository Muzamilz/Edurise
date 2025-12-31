// Core API Response Types
export interface ApiResponse<T = any> {
  data: T
  status: number
  statusText: string
  headers: any
  config: any
}

// User and Authentication Types
export interface User {
  id: string
  email: string
  first_name: string
  last_name: string
  is_staff: boolean
  is_superuser: boolean
  is_verified?: boolean
  date_joined: string
  last_login: string
  current_profile?: UserProfile
  avatar?: string
  phone?: string
  organization?: Organization
  specialization?: string
  years_experience?: number
  qualifications?: string
  bio?: string
  title?: string
  experience?: string
  expertise?: string
  education?: string[]
  social_links?: {
    website?: string
    linkedin?: string
    twitter?: string
    github?: string
  }
  total_students?: number
  total_courses?: number
  average_rating?: number
  courses_count?: number
  students_count?: number
  rating?: number
}

export interface UserProfile {
  id: string
  role: 'student' | 'teacher' | 'admin'
  is_approved_teacher: boolean
  teacher_approval_status: 'not_applied' | 'pending' | 'approved' | 'rejected'
  is_online: boolean
  last_seen?: string
  avatar?: string
  bio?: string
  phone_number?: string
  timezone: string
  language: string
}

export interface Organization {
  id: string
  name: string
  subdomain: string
  logo?: string
  primary_color?: string
  secondary_color?: string
  subscription?: {
    id: string
    plan_name: string
    plan_display_name: string
    status: string
    billing_cycle: string
    is_active: boolean
  }
}

export interface Tenant {
  id: string
  name: string
  subdomain: string
  logo?: string
  primary_color?: string
  secondary_color?: string
}

// System and Analytics Types
export interface SystemStatus {
  server_status: string
  uptime: string
  database_status: string
  db_connections: number
  storage_used: number
  storage_total: number
  memory_used: number
  memory_total: number
}

export interface SystemLog {
  id: string
  level: string
  message: string
  timestamp: string
  source?: string
}

export interface SystemConfig {
  general: {
    platform_name: string
    platform_url: string
    support_email: string
    default_language: string
    maintenance_mode: boolean
  }
  email: {
    smtp_host: string
    smtp_port: number
    smtp_username: string
    smtp_password: string
    use_tls: boolean
    from_email: string
  }
  storage: {
    provider: string
    max_file_size: number
    allowed_types: string[]
  }
  payment: {
    stripe_public_key: string
    stripe_secret_key: string
    currency: string
  }
}

/**
 * System Health Overview
 */
export interface SystemHealth {
  status: 'healthy' | 'degraded' | 'down'
  uptime_seconds: number
  uptime_formatted: string
  database: DatabaseStatus
  cache: CacheStatus
  storage: StorageStatus
  memory: MemoryStatus
  cpu: CPUStatus
  services: ServiceStatus[]
  last_check: string
  version: string
  environment: 'development' | 'staging' | 'production'
}

/**
 * Database Status
 */
export interface DatabaseStatus {
  status: 'connected' | 'disconnected' | 'error'
  connection_count: number
  max_connections: number
  response_time_ms: number
  size_mb: number
  tables_count: number
  last_backup?: string
  replication_lag_ms?: number
}

/**
 * Cache Status
 */
export interface CacheStatus {
  status: 'connected' | 'disconnected' | 'error'
  hit_rate: number
  miss_rate: number
  memory_used_mb: number
  memory_max_mb: number
  keys_count: number
  evictions: number
  response_time_ms: number
}

/**
 * Storage Status
 */
export interface StorageStatus {
  status: 'healthy' | 'warning' | 'critical'
  total_gb: number
  used_gb: number
  available_gb: number
  usage_percentage: number
  files_count: number
  provider: 'local' | 's3' | 'azure' | 'gcs'
}

/**
 * Memory Status
 */
export interface MemoryStatus {
  total_mb: number
  used_mb: number
  free_mb: number
  usage_percentage: number
  swap_total_mb: number
  swap_used_mb: number
}

/**
 * CPU Status
 */
export interface CPUStatus {
  cores: number
  usage_percentage: number
  load_average: number[]
  processes: number
}

/**
 * Service Status
 */
export interface ServiceStatus {
  name: string
  status: 'running' | 'stopped' | 'error'
  uptime_seconds?: number
  response_time_ms?: number
  last_check: string
  error_message?: string
}

/**
 * System Metrics for monitoring
 */
export interface SystemMetrics {
  timestamp: string
  cpu_usage: number
  memory_usage: number
  disk_usage: number
  network_in_mbps: number
  network_out_mbps: number
  active_connections: number
  request_rate: number
  error_rate: number
  response_time_p50: number
  response_time_p95: number
  response_time_p99: number
}

// Analytics Types
export interface Analytics {
  total_revenue?: number
  revenue_change?: number
  new_students?: number
  students_change?: number
  completions?: number
  completions_change?: number
  average_rating?: number
  total_reviews?: number
}



// Course and Content Types
export interface Course {
  id: string
  title: string
  description?: string
  instructor?: User
  price?: number
  created_at: string
  updated_at: string
  status?: string
  category?: string
  level?: string
  duration?: number
  enrollment_count?: number
  rating?: number
  thumbnail?: string
}

export interface Enrollment {
  id: string
  student: User
  course: Course
  enrolled_at: string
  completed_at?: string
  progress_percentage: number
  status: 'active' | 'completed' | 'dropped'
}

// Notification Types
export interface Notification {
  id: string
  title: string
  message: string
  type: 'info' | 'success' | 'warning' | 'error'
  read: boolean
  created_at: string
  action_url?: string
  metadata?: Record<string, any>
}

// Activity Types
export interface Activity {
  id: string
  type: string
  description: string
  timestamp: string
  user?: User
  metadata?: Record<string, any>
}

// Student Types
export interface Student {
  id: string
  student_id: string
  name: string
  email: string
  avatar?: string
  status: 'active' | 'completed' | 'inactive'
  course_title: string
  course_id: string
  enrolled_at: string
  completed_at?: string
  progress_percentage: number
  recent_activity?: Activity[]
}

// Certificate Types
export interface Certificate {
  id: string
  course: Course
  student: User
  issued_at: string
  certificate_url: string
  verification_code: string
}

// Live Class Types
export interface LiveClass {
  id: string
  title: string
  description?: string
  course: Course
  instructor: User
  scheduled_at: string
  duration: number
  status: 'scheduled' | 'live' | 'completed' | 'cancelled'
  join_url?: string
  recording_url?: string
  attendance_count?: number
  max_participants?: number
}

// Payment Types
export interface Payment {
  id: string
  amount: number
  currency: string
  status: 'pending' | 'completed' | 'failed' | 'refunded'
  created_at: string
  updated_at: string
  user: User
  course?: Course
  payment_method?: string
}

// Error Types
export interface APIError {
  message: string
  code?: string
  status?: number
  errors?: Record<string, string[]>
  timestamp?: string
}

// Form Types
export interface LoginForm {
  email: string
  password: string
}

export interface RegisterForm {
  email: string
  password: string
  first_name: string
  last_name: string
  confirm_password: string
}

// Wishlist Types
export interface WishlistItem {
  id: string
  course: Course
  added_at: string
}

// Testimonial Types
export interface Testimonial {
  id: string
  name: string
  role?: string
  content: string
  rating?: number
  avatar?: string
  course?: Course
  created_at: string
}

// FAQ Types
export interface FAQ {
  id: string
  question: string
  answer: string
  category?: string
  order?: number
  is_featured?: boolean
}

// Team Member Types
export interface TeamMember {
  id: string
  name: string
  role: string
  bio?: string
  avatar?: string
  social_links?: {
    linkedin?: string
    twitter?: string
    github?: string
  }
}

// Announcement Types
export interface Announcement {
  id: string
  title: string
  content: string
  type: 'info' | 'warning' | 'success' | 'error'
  is_active: boolean
  created_at: string
  updated_at: string
  author?: User
}

// Generic List Response
export interface ListResponse<T> {
  results: T[]
  count: number
  next?: string
  previous?: string
}

// Pagination
export interface PaginationMeta {
  page: number
  page_size: number
  total: number
  total_pages: number
}

// Filter and Search
export interface FilterOptions {
  search?: string
  status?: string
  category?: string
  level?: string
  price_min?: number
  price_max?: number
  date_from?: string
  date_to?: string
}

// Chart Data
export interface ChartData {
  labels: string[]
  datasets: {
    label: string
    data: number[]
    backgroundColor?: string | string[]
    borderColor?: string | string[]
    borderWidth?: number
  }[]
}

// Dashboard Stats
export interface DashboardStats {
  total_users?: number
  total_courses?: number
  total_revenue?: number
  active_enrollments?: number
  completion_rate?: number
  user_growth?: number
  revenue_growth?: number
}

// Admin Dashboard Data (from backend API)
export interface AdminDashboardData {
  organization_info: {
    name: string
    subscription_plan: string
    logo?: string
  }
  user_stats: {
    total_users: number
    active_users: number
    newUsersThisMonth: number
    teacherCount: number
    studentCount: number
    total_teachers: number
    approved_teachers: number
    pending_teacher_approvals: number
    user_growth_rate: number
  }
  course_stats: {
    total_courses: number
    published_courses: number
    private_courses: number
    courses_this_month: number
    avg_price: number
    total_modules: number
    average_rating: number
    avg_modules_per_course: number
  }
  enrollment_stats: {
    total_enrollments: number
    active_enrollments: number
    completed_enrollments: number
    dropped_enrollments: number
    enrollments_this_month: number
    avg_progress: number
    completion_rate: number
    dropout_rate: number
  }
  revenue_stats: {
    total_revenue: number
    revenue_this_month: number
    avg_payment: number
    total_payments: number
    revenue_growth_rate: number
  }
  class_stats: {
    total_classes: number
    completed_classes: number
    upcoming_classes: number
    avg_duration: number
    class_completion_rate: number
  }
  popular_courses: Array<{
    id: string
    title: string
    instructor_name: string
    enrollment_count: number
    average_rating: number
  }>
  recent_activity: {
    recent_enrollments: Array<{
      student_name: string
      course_title: string
      enrolled_at: string
    }>
    recent_courses: Array<{
      id: string
      title: string
      instructor_name: string
      created_at: string
      is_public: boolean
    }>
  }
  user_growth_trend: Array<{
    month: string
    new_users: number
  }>
  system_health: {
    database_status: string
    cache_status: string
    storage_status: string
    last_backup: string
  }
}

// Security Types - Re-export from dedicated security types file
export type {
  SecurityOverview,
  SecurityAlert,
  SecurityAlertFilters,
  SecurityEvent,
  SecurityPolicy,
  SecuritySettings,
  ComplianceReport
} from './security'

// Analytics Types - Re-export from dedicated analytics types file
export type {
  Report,
  ReportParams,
  ReportStatus,
  ScheduledReport,
  ScheduledReportConfig,
  PlatformAnalytics,
  TeacherAnalytics,
  StudentAnalytics,
  CourseAnalytics
} from './analytics'

export interface AuditLog {
  id: string
  action: string
  user: User
  resource_type: string
  resource_id: string
  changes: Record<string, any>
  ip_address: string
  user_agent: string
  created_at: string
}