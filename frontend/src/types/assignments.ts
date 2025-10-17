// Assignment and Certification Types

export interface Assignment {
  id: string
  course: string
  title: string
  description: string
  instructions: string
  assignment_type: 'essay' | 'project' | 'quiz' | 'presentation' | 'code' | 'other'
  max_score: number
  passing_score: number
  allow_file_upload: boolean
  max_file_size_mb: number
  allowed_file_types: string[]
  due_date: string
  late_submission_allowed: boolean
  late_penalty_percent: number
  status: 'draft' | 'published' | 'closed' | 'archived'
  is_required: boolean
  weight_percentage: number
  created_at: string
  updated_at: string
  published_at?: string
  is_overdue: boolean
  days_until_due: number
  submission_count: number
  graded_submission_count: number
}

export interface Submission {
  id: string
  assignment: string
  student: {
    id: string
    email: string
    first_name: string
    last_name: string
  }
  text_content: string
  file_upload?: string
  score?: number
  feedback: string
  is_graded: boolean
  graded_by?: {
    id: string
    email: string
    first_name: string
    last_name: string
  }
  status: 'draft' | 'submitted' | 'late' | 'graded' | 'returned'
  is_late: boolean
  late_penalty_applied: number
  created_at: string
  submitted_at?: string
  graded_at?: string
  updated_at: string
  final_score?: number
  grade_percentage?: number
  is_passing: boolean
}

export interface Certificate {
  id: string
  student: {
    id: string
    email: string
    first_name: string
    last_name: string
    full_name: string
  }
  course: {
    id: string
    title: string
    description: string
    category: string
    duration_weeks: number
  }
  instructor: {
    id: string
    email: string
    first_name: string
    last_name: string
    full_name: string
  }
  certificate_type: 'completion' | 'achievement' | 'participation' | 'excellence'
  certificate_number: string
  final_grade?: number
  completion_date: string
  qr_code?: string
  qr_code_url?: string
  verification_url: string
  status: 'pending' | 'issued' | 'revoked'
  pdf_file?: string
  certificate_file_url?: string
  created_at: string
  issued_at?: string
  updated_at: string
  is_valid: boolean
}

export interface CourseProgress {
  id: string
  student: string
  course: string
  modules_completed: string[]
  assignments_completed: string[]
  live_classes_attended: string[]
  overall_progress_percentage: number
  assignment_average_score?: number
  attendance_percentage: number
  is_completed: boolean
  completion_requirements_met: boolean
  created_at: string
  updated_at: string
  completed_at?: string
}

// Request/Response Types
export interface CreateAssignmentRequest {
  course: string
  title: string
  description: string
  instructions?: string
  assignment_type: Assignment['assignment_type']
  max_score?: number
  passing_score?: number
  allow_file_upload?: boolean
  max_file_size_mb?: number
  allowed_file_types?: string[]
  due_date: string
  late_submission_allowed?: boolean
  late_penalty_percent?: number
  is_required?: boolean
  weight_percentage?: number
}

export interface UpdateAssignmentRequest extends Partial<CreateAssignmentRequest> {
  status?: Assignment['status']
}

export interface CreateSubmissionRequest {
  assignment: string
  text_content?: string
  file_upload?: File
}

export interface UpdateSubmissionRequest {
  text_content?: string
  file_upload?: File
}

export interface GradeSubmissionRequest {
  score: number
  feedback?: string
}

export interface CertificateVerificationRequest {
  certificate_number: string
}

export interface CertificateVerificationResponse {
  valid: boolean
  certificate?: Certificate
  message: string
  student_name?: string
  student_email?: string
  course_title?: string
  course_category?: string
  instructor_name?: string
  completion_date?: string
  final_grade?: number
  certificate_type?: string
  verification_url?: string
  qr_code_url?: string
  certificate_file_url?: string
  issued_at?: string
}

// Filter Types
export interface AssignmentFilters {
  course?: string
  status?: Assignment['status']
  assignment_type?: Assignment['assignment_type']
  is_required?: boolean
  is_overdue?: boolean
  search?: string
  ordering?: string
}

export interface SubmissionFilters {
  assignment?: string
  student?: string
  status?: Submission['status']
  is_graded?: boolean
  is_late?: boolean
  search?: string
  ordering?: string
}

export interface CertificateFilters {
  student?: string
  course?: string
  certificate_type?: Certificate['certificate_type']
  status?: Certificate['status']
  search?: string
  ordering?: string
}

// Progress Visualization Types
export interface ProgressVisualizationData {
  overall_progress: number
  modules_progress: number
  assignments_progress: number
  attendance_progress: number
  assignment_scores: Array<{
    assignment_title: string
    score: number
    max_score: number
    percentage: number
  }>
  timeline: Array<{
    date: string
    event_type: 'module' | 'assignment' | 'class'
    title: string
    completed: boolean
  }>
}

// Animation Types for Deadline Reminders
export interface DeadlineReminder {
  assignment_id: string
  assignment_title: string
  due_date: string
  days_remaining: number
  urgency_level: 'low' | 'medium' | 'high' | 'critical'
  animation_type: 'pulse' | 'shake' | 'glow' | 'bounce'
}