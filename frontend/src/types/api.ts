// User and Authentication Types
export interface User {
  readonly id: string
  readonly email: string
  readonly first_name: string
  readonly last_name: string
  readonly is_staff: boolean
  readonly is_superuser: boolean
  readonly is_teacher: boolean
  readonly is_approved_teacher: boolean
  readonly date_joined: string
  readonly last_login: string
  readonly current_profile?: UserProfile
  readonly full_name?: string
  readonly avatar?: string
  readonly role?: 'student' | 'teacher' | 'admin'
  readonly organization_name?: string
  readonly profiles_count?: number
  readonly is_active?: boolean
  readonly last_seen?: string
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
  role: 'student' | 'teacher' | 'admin'
  is_approved_teacher: boolean
  teacher_approval_status: 'not_applied' | 'pending' | 'approved' | 'rejected'
  teacher_approved_at?: string
  teacher_approved_by?: User
  notification_preferences: Record<string, any>
  is_online: boolean
  last_seen?: string
  created_at: string
  updated_at: string
}

export interface Organization {
  id: string
  name: string
  subdomain: string
  logo?: string
  description?: string
  primary_color: string
  secondary_color: string
  is_active: boolean
  created_at: string
  updated_at: string
  // Additional properties for enhanced courses view
  course_count?: number
  total_students?: number
  avg_rating?: number
  user_count?: number
  // Legacy subscription plan field (still used in some views)
  subscription_plan?: 'basic' | 'pro' | 'enterprise'
  // Subscription is now a separate relationship
  subscription?: Subscription
}

export interface SubscriptionPlan {
  id: string
  name: 'basic' | 'pro' | 'enterprise'
  display_name: string
  description: string
  price_monthly: number
  price_yearly: number
  max_users: number
  max_courses: number
  max_storage_gb: number
  ai_quota_monthly: number
  has_analytics: boolean
  has_api_access: boolean
  has_white_labeling: boolean
  has_priority_support: boolean
  has_custom_integrations: boolean
  max_file_size_mb: number
  monthly_download_limit: number | null
  recording_access: boolean
  premium_content_access: boolean
  features: Record<string, any>
  is_popular: boolean
  is_active: boolean
  sort_order: number
  created_at: string
  updated_at: string
}

export interface Subscription {
  id: string
  organization: string
  plan: SubscriptionPlan
  billing_cycle: 'monthly' | 'yearly'
  status: 'active' | 'cancelled' | 'past_due' | 'unpaid' | 'trialing'
  amount: number
  currency: string
  current_period_start: string
  current_period_end: string
  trial_end: string | null
  created_at: string
  updated_at: string
  cancelled_at: string | null
}

export interface CourseCategory {
  id: string
  name: string
  slug: string
  description: string
  icon: string
  color: string
  parent: string | null
  sort_order: number
  is_active: boolean
  tenant: string | null
  created_at: string
  updated_at: string
  // Computed properties
  full_path?: string
  subcategories?: CourseCategory[]
  course_count?: number
  usage_count?: number
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

/**
 * Teacher Approval entity
 */
export interface TeacherApproval {
  id: string
  user: User
  status: 'pending' | 'approved' | 'rejected'
  application_date: string
  reviewed_date?: string
  reviewed_by?: User
  notes?: string
  qualifications?: string
  experience?: string
  teaching_subjects?: string[]
  created_at: string
  updated_at: string
}

/**
 * Audit Log Filters
 */
export interface AuditLogFilters {
  user_id?: string
  action?: string
  resource_type?: string
  date_from?: string
  date_to?: string
  page?: number
  page_size?: number
}

/**
 * Security Event Filters
 */
export interface SecurityEventFilters {
  type?: string
  severity?: 'low' | 'medium' | 'high' | 'critical'
  user_id?: string
  date_from?: string
  date_to?: string
  page?: number
  page_size?: number
}

/**
 * User Analytics Data
 */
export interface UserAnalytics {
  total_users: number
  active_users: number
  new_users: number
  user_growth_rate: number
  users_by_role: {
    students: number
    teachers: number
    admins: number
  }
  users_by_status: {
    active: number
    inactive: number
    suspended: number
  }
  registration_trend: Array<{
    date: string
    count: number
  }>
  engagement_metrics: {
    avg_session_duration: number
    avg_courses_per_user: number
    daily_active_users: number
    weekly_active_users: number
    monthly_active_users: number
  }
}

/**
 * Course Analytics Data
 */
export interface CourseAnalyticsData {
  total_courses: number
  published_courses: number
  draft_courses: number
  course_growth_rate: number
  courses_by_category: Array<{
    category: string
    count: number
  }>
  courses_by_status: {
    published: number
    draft: number
    archived: number
  }
  enrollment_trend: Array<{
    date: string
    count: number
  }>
  completion_metrics: {
    avg_completion_rate: number
    total_completions: number
    in_progress: number
  }
}

/**
 * Revenue Analytics Data
 */
export interface RevenueAnalytics {
  total_revenue: number
  revenue_growth_rate: number
  revenue_by_period: Array<{
    period: string
    revenue: number
  }>
  revenue_by_course: Array<{
    course_id: string
    course_title: string
    revenue: number
  }>
  revenue_by_payment_method: Array<{
    method: string
    revenue: number
    count: number
  }>
  average_transaction_value: number
  total_transactions: number
}

/**
 * Enrollment Filters
 */
export interface EnrollmentFilters {
  course_id?: string
  student_id?: string
  status?: 'active' | 'completed' | 'dropped' | 'paused'
  date_from?: string
  date_to?: string
  page?: number
  page_size?: number
}

/**
 * Course Statistics
 */
export interface CourseStatistics {
  total_enrollments: number
  active_enrollments: number
  completed_enrollments: number
  average_progress: number
  completion_rate: number
  average_rating: number
  total_reviews: number
  total_revenue: number
  enrollment_trend: Array<{
    date: string
    count: number
  }>
  student_demographics: {
    by_country: Record<string, number>
    by_age_group: Record<string, number>
  }
}

// Course Types
export interface Course {
  id: string
  title: string
  description: string
  instructor: User
  category: string // Category ID
  category_details?: CourseCategory
  category_name?: string
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

export interface PaymentCapture {
  payment_id: string
  status: 'completed' | 'failed'
  transaction_id: string
  amount: number
  currency: string
  payer_email?: string
  payer_name?: string
  captured_at: string
  message?: string
}

export interface PayPalOrder {
  order_id: string
  approval_url: string
  status: 'created' | 'approved' | 'completed'
  amount: number
  currency: string
  created_at: string
}

/**
 * Report Generation Response
 */
export interface ReportGenerationResponse {
  report_id: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  message: string
  estimated_completion?: string
  download_url?: string
}

/**
 * Export Data Response
 */
export interface ExportDataResponse {
  export_id: string
  format: 'csv' | 'xlsx' | 'json' | 'pdf'
  status: 'pending' | 'processing' | 'completed' | 'failed'
  file_url?: string
  file_size?: number
  record_count?: number
  created_at: string
  expires_at?: string
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

export interface FinancialData {
  total_revenue: number
  current_month_revenue: number
  last_month_revenue: number
  growth_rate: number
  total_transactions: number
  average_transaction: number
  total_commission: number
  total_payouts: number
  revenue_trend: Array<{
    date: string
    revenue: number
  }>
  revenue_by_organization: Array<{
    organization_id: string
    organization_name: string
    revenue: number
  }>
}

export interface Transaction {
  id: string
  user: {
    name: string
    email: string
  }
  course: {
    title: string
  }
  amount: number
  status: string
  payment_method: string
  created_at: string
  organization?: {
    name: string
  }
  student?: {
    first_name: string
    last_name: string
  }
  commission?: number
}

export interface OrganizationPayout {
  id: string
  name: string
  pending_payout: number
}

// Notification Types
export interface Notification {
  id: string
  user: string
  user_name: string
  user_email: string
  title: string
  message: string
  notification_type: 'course_enrollment' | 'class_reminder' | 'assignment_due' | 'payment_success' | 'payment_failed' | 'payment_overdue' | 'subscription_renewed' | 'subscription_cancelled' | 'invoice_sent' | 'teacher_approval' | 'system'
  is_read: boolean
  sent_email: boolean
  sent_push: boolean
  related_object_id?: string
  related_object_type?: string
  created_at: string
  read_at?: string
  time_since_created: string
}

export interface NotificationPreferences {
  email_notifications: boolean
  push_notifications: boolean
  course_enrollment_notifications: boolean
  class_reminder_notifications: boolean
  assignment_due_notifications: boolean
  payment_notifications: boolean
  system_notifications: boolean
}

export interface NotificationStats {
  total_notifications: number
  unread_notifications: number
  read_notifications: number
  notifications_by_type: Record<string, number>
  recent_notifications: Notification[]
}

export interface EmailDeliveryLog {
  id: string
  notification: string
  notification_title: string
  recipient_email: string
  status: 'sent' | 'failed' | 'bounced' | 'delivered' | 'opened' | 'clicked'
  details: string
  sent_at: string
  delivered_at?: string
  opened_at?: string
  clicked_at?: string
  subject: string
  template_used: string
}

export interface NotificationTemplate {
  id: string
  name: string
  notification_type: string
  subject_template: string
  html_template: string
  text_template: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface EmailTemplate {
  template_name: string
  display_name: string
  notification_type: string
  is_available: boolean
}

export interface ChatMessage {
  id: string
  room_name: string
  user: string
  user_name: string
  user_email: string
  content: string
  is_edited: boolean
  edited_at?: string
  is_deleted: boolean
  deleted_at?: string
  created_at: string
  updated_at: string
  time_since_created: string
}

export interface WebSocketConnection {
  id: string
  user: string
  user_name: string
  user_email: string
  connection_type: 'notifications' | 'chat' | 'live_class'
  channel_name: string
  room_name: string
  ip_address?: string
  user_agent: string
  is_active: boolean
  connected_at: string
  disconnected_at?: string
  last_activity: string
  connection_duration: number
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

/**
 * Standard API response wrapper
 * All API endpoints return data wrapped in this structure
 */
export interface APIResponse<T> {
  success: boolean
  data: T
  message?: string
  timestamp: string
}

/**
 * Paginated API response
 * Used for list endpoints that support pagination
 */
export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

/**
 * API Error response
 * Standardized error structure returned by the API
 */
export interface ApiError {
  message: string
  code?: string
  errors?: Record<string, string[]>
  status: number
  timestamp?: string
  detail?: string
}

/**
 * Error response from API
 * Used when API returns an error status
 */
export interface ErrorResponse {
  error: ApiError
  success: false
  timestamp: string
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
  course_id?: string
  student_id?: string
  status?: 'active' | 'completed' | 'dropped' | 'paused'
  date_from?: string
  date_to?: string
  page?: number
  page_size?: number
}

// Wishlist Types
export interface Wishlist {
  id: string
  user: string
  course: string
  course_title: string
  course_price: number | null
  course_instructor: string
  course_category: string
  course_difficulty: string
  course_thumbnail?: string
  course_average_rating: number
  course_total_enrollments: number
  priority: 1 | 2 | 3 // Low, Medium, High
  notes: string
  notify_price_change: boolean
  notify_course_updates: boolean
  notify_enrollment_opening: boolean
  is_course_available: boolean
  is_enrolled: boolean
  price_change_percentage: number
  added_at: string
  updated_at: string
}

export interface WishlistAnalytics {
  total_items: number
  total_value: number
  average_price: number
  categories: Array<{
    name: string
    count: number
    total_value: number
  }>
  price_ranges: {
    free: number
    under_50: number
    under_100: number
    under_200: number
    over_200: number
  }
  availability_status: {
    available: number
    enrolled: number
    unavailable: number
  }
  recommendations: Array<{
    course_id: string
    title: string
    instructor: string
    category: string
    price: number
    average_rating: number
    enrollment_count: number
    reason: string
  }>
}

export interface WishlistFilters {
  priority?: 1 | 2 | 3
  category?: string
  search?: string
  ordering?: string
  page?: number
  page_size?: number
}

// Recommendation Types
export interface Recommendation {
  course: Course
  recommendation_score: number
  recommendation_reason: string
  recommendation_algorithm: string
  recommendation_metadata: Record<string, any>
  position_in_list: number
}

export interface RecommendationResponse {
  recommendations: Recommendation[]
  user_context: {
    total_enrollments: number
    completed_courses: number
    wishlist_items: number
    preferred_categories: Record<string, number>
    skill_level: 'beginner' | 'intermediate' | 'advanced'
    is_new_user: boolean
  }
  algorithm_used: string
  context: string
  total_count: number
  generated_at: string
}

export interface SimilarCoursesResponse {
  similar_courses: Array<Course & {
    similarity_reason: string
    similarity_score: number
  }>
  reference_course: Course
  total_count: number
}

export interface TrendingCoursesResponse {
  trending_courses: Array<Course & {
    trending_score: number
    recent_enrollments: number
    recent_views: number
    trending_reason: string
  }>
  period_days: number
  total_count: number
}

export interface RecommendationInteraction {
  course_id: string
  interaction_type: 'view' | 'click' | 'wishlist' | 'enroll' | 'dismiss'
  algorithm_used?: string
  recommendation_score?: number
  context?: string
  position_in_list?: number
}

export interface RecommendationAnalytics {
  total_interactions: number
  interactions_by_type: Record<string, number>
  click_through_rate: number
  conversion_rate: number
  top_recommended_courses: Array<{
    course_id: string
    course_title: string
    interaction_count: number
  }>
  algorithm_performance: Record<string, {
    views: number
    clicks: number
    enrollments: number
    ctr: number
    conversion_rate: number
  }>
}