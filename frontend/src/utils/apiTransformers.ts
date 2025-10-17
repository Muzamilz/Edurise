// API Response Transformation Utilities
// Provides consistent data formatting across the application

export interface PaginatedResponse<T> {
  results: T[]
  count: number
  next: string | null
  previous: string | null
  page: number
  total_pages: number
}

export interface StandardApiResponse<T> {
  success: boolean
  data: T
  message?: string
  timestamp?: string
  meta?: {
    pagination?: {
      page: number
      total_pages: number
      count: number
      next: string | null
      previous: string | null
    }
  }
}

// Transform paginated response to consistent format
export const transformPaginatedResponse = <T>(response: any): PaginatedResponse<T> => {
  // Handle Django REST Framework pagination format
  if (response.results !== undefined) {
    return {
      results: response.results,
      count: response.count || 0,
      next: response.next,
      previous: response.previous,
      page: response.page || 1,
      total_pages: response.total_pages || Math.ceil((response.count || 0) / (response.results?.length || 1))
    }
  }

  // Handle array response (convert to paginated format)
  if (Array.isArray(response)) {
    return {
      results: response,
      count: response.length,
      next: null,
      previous: null,
      page: 1,
      total_pages: 1
    }
  }

  // Handle single item response
  return {
    results: [response],
    count: 1,
    next: null,
    previous: null,
    page: 1,
    total_pages: 1
  }
}

// Transform enrollment data for student views
export const transformEnrollmentData = (enrollment: any) => {
  return {
    id: enrollment.id,
    course: {
      id: enrollment.course?.id || enrollment.course_id,
      title: enrollment.course?.title || enrollment.course_title,
      description: enrollment.course?.description,
      thumbnail: enrollment.course?.thumbnail,
      instructor: {
        id: enrollment.course?.instructor?.id,
        first_name: enrollment.course?.instructor?.first_name || enrollment.instructor_name?.split(' ')[0],
        last_name: enrollment.course?.instructor?.last_name || enrollment.instructor_name?.split(' ').slice(1).join(' '),
        full_name: enrollment.course?.instructor?.full_name || enrollment.instructor_name
      },
      difficulty_level: enrollment.course?.difficulty_level || 'Beginner',
      total_lessons: enrollment.course?.total_lessons || 0,
      total_duration: enrollment.course?.total_duration || 0,
      price: enrollment.course?.price || 0
    },
    enrollment_date: enrollment.enrolled_at || enrollment.created_at,
    last_accessed: enrollment.last_accessed,
    progress_percentage: enrollment.progress_percentage || 0,
    completed_at: enrollment.completed_at,
    certificate_earned: enrollment.certificate_earned || false,
    status: enrollment.status || (enrollment.progress_percentage >= 100 ? 'completed' : 
             enrollment.progress_percentage > 0 ? 'in_progress' : 'not_started')
  }
}

// Transform live class data
export const transformLiveClassData = (liveClass: any) => {
  return {
    id: liveClass.id,
    title: liveClass.title,
    description: liveClass.description,
    course_id: liveClass.course?.id || liveClass.course_id,
    course_title: liveClass.course?.title || liveClass.course_title,
    instructor_id: liveClass.instructor?.id || liveClass.instructor_id,
    instructor_name: liveClass.instructor?.full_name || liveClass.instructor_name,
    scheduled_at: liveClass.scheduled_at,
    duration_minutes: liveClass.duration_minutes || 60,
    status: liveClass.status || 'scheduled',
    join_url: liveClass.join_url,
    recording_url: liveClass.recording_url,
    has_materials: liveClass.has_materials || false,
    attended: liveClass.attended || false,
    attendance_duration: liveClass.attendance_duration
  }
}

// Transform course progress data
export const transformCourseProgressData = (progress: any) => {
  return {
    id: progress.id,
    course: {
      id: progress.course?.id || progress.course_id,
      title: progress.course?.title || progress.course_title,
      thumbnail: progress.course?.thumbnail,
      instructor: progress.course?.instructor?.full_name || progress.instructor_name
    },
    progress_percentage: progress.progress_percentage || 0,
    completed_lessons: progress.completed_lessons || 0,
    total_lessons: progress.total_lessons || 0,
    time_spent: progress.time_spent || 0,
    last_accessed: progress.last_accessed,
    enrolled_at: progress.enrolled_at,
    completed_at: progress.completed_at,
    status: progress.status || (progress.progress_percentage >= 100 ? 'completed' : 
             progress.progress_percentage > 0 ? 'active' : 'not_started')
  }
}

// Transform certificate data
export const transformCertificateData = (certificate: any) => {
  return {
    id: certificate.id,
    course_id: certificate.course?.id || certificate.course_id,
    course_title: certificate.course?.title || certificate.course_title,
    instructor_name: certificate.instructor?.full_name || certificate.instructor_name,
    student_name: certificate.student?.full_name || certificate.student_name,
    issued_at: certificate.issued_at,
    verification_code: certificate.verification_code,
    certificate_url: certificate.certificate_url,
    final_score: certificate.final_score,
    type: certificate.type || 'completion'
  }
}

// Transform user data for consistent format
export const transformUserData = (user: any) => {
  return {
    id: user.id,
    email: user.email,
    first_name: user.first_name,
    last_name: user.last_name,
    full_name: user.full_name || `${user.first_name} ${user.last_name}`.trim(),
    role: user.role,
    avatar: user.avatar || user.profile_picture,
    is_active: user.is_active,
    date_joined: user.date_joined,
    last_login: user.last_login,
    profile: {
      bio: user.profile?.bio,
      phone: user.profile?.phone,
      timezone: user.profile?.timezone || 'UTC',
      language: user.profile?.language || 'en'
    }
  }
}

// Transform error response to consistent format
export const transformErrorResponse = (error: any) => {
  if (error.response?.data) {
    const errorData = error.response.data
    return {
      message: errorData.message || errorData.detail || 'An error occurred',
      code: errorData.code || `HTTP_${error.response.status}`,
      status: error.response.status,
      errors: errorData.errors || errorData.non_field_errors,
      timestamp: errorData.timestamp || new Date().toISOString()
    }
  }

  return {
    message: error.message || 'Network error',
    code: 'NETWORK_ERROR',
    status: 0,
    timestamp: new Date().toISOString()
  }
}

// Generic transformer for common API response patterns
export const createTransformer = <T, R>(transformFn: (item: T) => R) => {
  return (data: any): R | R[] => {
    if (Array.isArray(data)) {
      return data.map(transformFn)
    }
    
    if (data.results && Array.isArray(data.results)) {
      return {
        ...data,
        results: data.results.map(transformFn)
      }
    }
    
    return transformFn(data)
  }
}

// Utility to normalize API endpoints
export const normalizeEndpoint = (endpoint: string): string => {
  // Ensure endpoint starts with /api/v1/
  if (!endpoint.startsWith('/api/v1/')) {
    if (endpoint.startsWith('/')) {
      return `/api/v1${endpoint}`
    }
    return `/api/v1/${endpoint}`
  }
  return endpoint
}

// Utility to build query parameters
export const buildQueryParams = (params: Record<string, any>): string => {
  const searchParams = new URLSearchParams()
  
  Object.entries(params).forEach(([key, value]) => {
    if (value !== null && value !== undefined && value !== '') {
      if (Array.isArray(value)) {
        value.forEach(item => searchParams.append(key, String(item)))
      } else {
        searchParams.append(key, String(value))
      }
    }
  })
  
  const queryString = searchParams.toString()
  return queryString ? `?${queryString}` : ''
}

// Export commonly used transformers
export const enrollmentTransformer = createTransformer(transformEnrollmentData)
export const liveClassTransformer = createTransformer(transformLiveClassData)
export const progressTransformer = createTransformer(transformCourseProgressData)
export const certificateTransformer = createTransformer(transformCertificateData)
export const userTransformer = createTransformer(transformUserData)