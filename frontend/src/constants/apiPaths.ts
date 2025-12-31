/**
 * API Path Constants
 * 
 * Centralized definition of all API endpoint paths.
 * All paths are relative to the API base URL (/api/v1/).
 * 
 * Usage:
 *   import { API_PATHS } from '@/constants/apiPaths'
 *   api.get(API_PATHS.COURSES.LIST)
 *   api.get(API_PATHS.COURSES.DETAIL('123'))
 */

export const API_PATHS = {
  // ===== Authentication & Accounts =====
  AUTH: {
    LOGIN: '/accounts/auth/login/',
    LOGOUT: '/accounts/auth/logout/',
    REGISTER: '/accounts/auth/register/',
    REFRESH: '/accounts/auth/token/refresh/',
    PASSWORD_RESET: '/accounts/auth/password/reset/',
    PASSWORD_CHANGE: '/accounts/auth/password/change/',
  },

  // ===== Users =====
  USERS: {
    LIST: '/users/',
    DETAIL: (id: string) => `/users/${id}/`,
    ACTIVATE: (id: string) => `/users/${id}/activate/`,
    DEACTIVATE: (id: string) => `/users/${id}/deactivate/`,
    PROMOTE_TEACHER: (id: string) => `/users/${id}/promote_teacher/`,
    PROMOTE_ADMIN: (id: string) => `/users/${id}/promote_admin/`,
    DEMOTE: (id: string) => `/users/${id}/demote/`,
    BULK_UPDATE: '/users/bulk_update/',
    BULK_DELETE: '/users/bulk_delete/',
    EXPORT: '/users/export/',
  },

  // ===== User Profiles =====
  USER_PROFILES: {
    ME: '/user-profiles/me/',
    UPLOAD_AVATAR: '/user-profiles/upload_avatar/',
  },

  // ===== Teacher Approvals =====
  TEACHER_APPROVALS: {
    LIST: '/teacher-approvals/',
    APPROVE: (id: string) => `/teacher-approvals/${id}/approve/`,
    REJECT: (id: string) => `/teacher-approvals/${id}/reject/`,
  },

  // ===== Organizations =====
  ORGANIZATIONS: {
    LIST: '/organizations/',
    DETAIL: (id: string) => `/organizations/${id}/`,
    STATS: (id: string) => `/organizations/${id}/stats/`,
    USERS: (id: string) => `/organizations/${id}/users/`,
    COURSES: (id: string) => `/organizations/${id}/courses/`,
  },

  // ===== Courses =====
  COURSES: {
    LIST: '/courses/',
    DETAIL: (id: string) => `/courses/${id}/`,
    MARKETPLACE: '/courses/marketplace/',
    FEATURED: '/courses/featured/',
    MY_COURSES: '/courses/my_courses/',
    ENROLLED_COURSES: '/courses/enrolled_courses/',
    CATEGORIES: '/courses/categories/',
    DUPLICATE: (id: string) => `/courses/${id}/duplicate/`,
    STATISTICS: (id: string) => `/courses/${id}/statistics/`,
    STUDENTS: (id: string) => `/courses/${id}/students/`,
    ENROLL: (id: string) => `/courses/${id}/enroll/`,
    INSTRUCTOR_ANALYTICS: '/courses/instructor_analytics/',
    EXPORT: '/courses/export/',
  },

  // ===== Course Categories =====
  COURSE_CATEGORIES: {
    LIST: '/course-categories/',
    DETAIL: (id: string) => `/course-categories/${id}/`,
  },

  // ===== Course Modules =====
  COURSE_MODULES: {
    LIST: '/course-modules/',
    DETAIL: (id: string) => `/course-modules/${id}/`,
    COMPLETE: (id: string) => `/course-modules/${id}/complete/`,
  },

  // ===== Course Reviews =====
  COURSE_REVIEWS: {
    LIST: '/course-reviews/',
    DETAIL: (id: string) => `/course-reviews/${id}/`,
  },

  // ===== Enrollments =====
  ENROLLMENTS: {
    LIST: '/enrollments/',
    DETAIL: (id: string) => `/enrollments/${id}/`,
    UPDATE_PROGRESS: (id: string) => `/enrollments/${id}/update_progress/`,
    DROP: (id: string) => `/enrollments/${id}/drop/`,
    ANALYTICS: '/enrollments/analytics/',
    DASHBOARD: '/enrollments/dashboard/',
    PROGRESS_DETAIL: (id: string) => `/enrollments/${id}/progress_detail/`,
    EXPORT: '/enrollments/export/',
  },

  // ===== Live Classes =====
  LIVE_CLASSES: {
    LIST: '/live-classes/',
    DETAIL: (id: string) => `/live-classes/${id}/`,
    START: (id: string) => `/live-classes/${id}/start_class/`,
    END: (id: string) => `/live-classes/${id}/end_class/`,
    MATERIALS: (id: string) => `/live-classes/${id}/materials/`,
  },

  // ===== Recommendations =====
  RECOMMENDATIONS: {
    LIST: '/recommendations/',
  },

  // ===== Wishlist =====
  WISHLIST: {
    LIST: '/wishlist/',
    ADD_COURSE: '/wishlist/add_course/',
    REMOVE_COURSE: '/wishlist/remove_course/',
    ANALYTICS: '/wishlist/analytics/',
  },

  // ===== Assignments =====
  ASSIGNMENTS: {
    LIST: '/assignments/',
    DETAIL: (id: string) => `/assignments/${id}/`,
    PUBLISH: (id: string) => `/assignments/${id}/publish/`,
    CLOSE: (id: string) => `/assignments/${id}/close/`,
    MY_SUBMISSION: (id: string) => `/assignments/${id}/my-submission/`,
    ANALYTICS: (id: string) => `/assignments/${id}/analytics/`,
    EXPORT_GRADES: (id: string) => `/assignments/${id}/export-grades/`,
    IMPORT_GRADES: (id: string) => `/assignments/${id}/import-grades/`,
  },

  // ===== Submissions =====
  SUBMISSIONS: {
    LIST: '/submissions/',
    DETAIL: (id: string) => `/submissions/${id}/`,
    SUBMIT: (id: string) => `/submissions/${id}/submit/`,
    GRADE: (id: string) => `/submissions/${id}/grade/`,
    BULK_GRADE: '/submissions/bulk-grade/',
  },

  // ===== Certificates =====
  CERTIFICATES: {
    LIST: '/certificates/',
    DETAIL: (id: string) => `/certificates/${id}/`,
    ISSUE: (id: string) => `/certificates/${id}/issue/`,
    REVOKE: (id: string) => `/certificates/${id}/revoke/`,
    DOWNLOAD: (id: string) => `/certificates/${id}/download/`,
    VERIFY: '/certificates/verify/',
    VERIFY_BY_QR: '/certificates/verify_by_qr/',
    GENERATE_PDF: (id: string) => `/certificates/${id}/generate_pdf/`,
    SEND_EMAIL: (id: string) => `/certificates/${id}/send_email/`,
    GENERATE_QR_CODE: (id: string) => `/certificates/${id}/generate_qr_code/`,
    MY_CERTIFICATES: '/certificates/my_certificates/',
  },

  // ===== Payments =====
  PAYMENTS: {
    LIST: '/payments/',
    DETAIL: (id: string) => `/payments/${id}/`,
    CREATE_COURSE_PAYMENT: '/payments/create_course_payment/',
    CONFIRM: (id: string) => `/payments/${id}/confirm_payment/`,
    APPROVE_BANK_TRANSFER: (id: string) => `/payments/${id}/approve_bank_transfer/`,
    REJECT_BANK_TRANSFER: (id: string) => `/payments/${id}/reject_bank_transfer/`,
    ANALYTICS: '/payments/payment_analytics/',
    PAYPAL: {
      CREATE_ORDER: '/payments/paypal/create-order/',
      CAPTURE_ORDER: '/payments/paypal/capture-order/',
    },
  },

  // ===== Subscriptions =====
  SUBSCRIPTIONS: {
    LIST: '/subscriptions/',
    DETAIL: (id: string) => `/subscriptions/${id}/`,
    CREATE: '/subscriptions/create_subscription/',
    CANCEL: (id: string) => `/subscriptions/${id}/cancel_subscription/`,
    RENEW: (id: string) => `/subscriptions/${id}/renew_subscription/`,
    BILLING_AUTOMATION: '/subscriptions/billing_automation/',
  },

  // ===== Subscription Plans =====
  SUBSCRIPTION_PLANS: {
    LIST: '/subscription-plans/',
    COMPARE: '/subscription-plans/compare/',
  },

  // ===== Invoices =====
  INVOICES: {
    LIST: '/invoices/',
    DETAIL: (id: string) => `/invoices/${id}/`,
    SEND: (id: string) => `/invoices/${id}/send_invoice/`,
    MARK_PAID: (id: string) => `/invoices/${id}/mark_paid/`,
    OVERDUE: '/invoices/overdue_invoices/',
    DOWNLOAD: (id: string) => `/invoices/${id}/download/`,
    ANALYTICS: '/invoices/invoice_analytics/',
  },

  // ===== Notifications =====
  NOTIFICATIONS: {
    LIST: '/notifications/',
    DETAIL: (id: string) => `/notifications/${id}/`,
    MARK_READ: (id: string) => `/notifications/${id}/mark_read/`,
    MARK_ALL_READ: '/notifications/mark_all_read/',
  },

  // ===== AI Services =====
  AI: {
    CONVERSATIONS: {
      LIST: '/ai-conversations/',
      DETAIL: (id: string) => `/ai-conversations/${id}/`,
      MESSAGES: (id: string) => `/ai-conversations/${id}/messages/`,
      SEND_MESSAGE: (id: string) => `/ai-conversations/${id}/send_message/`,
    },
    SUMMARIES: {
      LIST: '/ai-content-summaries/',
      DETAIL: (id: string) => `/ai-content-summaries/${id}/`,
      GENERATE: '/ai-content-summaries/generate/',
    },
    QUIZZES: {
      LIST: '/ai-quizzes/',
      DETAIL: (id: string) => `/ai-quizzes/${id}/`,
      GENERATE: '/ai-quizzes/generate/',
    },
    USAGE: {
      LIST: '/ai-usage/',
      CURRENT_STATS: '/ai-usage/current_stats/',
    },
  },

  // ===== Analytics =====
  ANALYTICS: {
    EXPORT: '/analytics/export/',
    PLATFORM_OVERVIEW: '/analytics/platform-overview/',
    TEACHER: '/analytics/teacher/',
    STUDENT: '/analytics/student/',
    COURSE: (id: string) => `/analytics/course/${id}/`,
  },

  // ===== Reports =====
  REPORTS: {
    GENERATE: '/reports/generate/',
    DOWNLOAD: (id: string) => `/reports/download/${id}/`,
    STATUS: (id: string) => `/reports/${id}/status/`,
  },

  // ===== Scheduled Reports =====
  SCHEDULED_REPORTS: {
    LIST: '/scheduled-reports/',
    DETAIL: (id: string) => `/scheduled-reports/${id}/`,
  },

  // ===== Security =====
  SECURITY: {
    OVERVIEW: '/security/',
    ALERTS: '/security/alerts/',
    EVENTS: '/security/events/',
    POLICIES: '/security/policies/',
    SETTINGS: '/security/settings/',
  },

  // ===== Admin =====
  ADMIN: {
    DASHBOARD_STATS: '/admin/dashboard/stats/',
    AUDIT_LOGS: '/admin/audit-logs/',
    ANALYTICS: {
      USERS: '/admin/analytics/users/',
      COURSES: '/admin/analytics/courses/',
      REVENUE: '/admin/analytics/revenue/',
    },
    SETTINGS: '/admin/settings/',
    NOTIFICATIONS: {
      BULK_SEND: '/admin/notifications/bulk_send/',
    },
    ANNOUNCEMENTS: '/admin/announcements/',
  },

  // ===== Content Management =====
  CONTENT: {
    TESTIMONIALS: {
      LIST: '/testimonials/',
      DETAIL: (id: number) => `/testimonials/${id}/`,
      FEATURED: '/testimonials/featured/',
      APPROVE: (id: number) => `/testimonials/${id}/approve/`,
      REJECT: (id: number) => `/testimonials/${id}/reject/`,
    },
    TEAM_MEMBERS: {
      LIST: '/team-members/',
      DETAIL: (id: number) => `/team-members/${id}/`,
      BY_DEPARTMENT: '/team-members/by_department/',
    },
    ANNOUNCEMENTS: {
      LIST: '/announcements/',
      DETAIL: (id: number) => `/announcements/${id}/`,
      FEATURED: '/announcements/featured/',
      HOMEPAGE: '/announcements/homepage/',
    },
    FAQS: {
      LIST: '/faqs/',
      DETAIL: (id: number) => `/faqs/${id}/`,
      FEATURED: '/faqs/featured/',
      BY_CATEGORY: '/faqs/by_category/',
      FEEDBACK: (id: number) => `/faqs/${id}/feedback/`,
    },
    CONTACT_INFO: {
      LIST: '/contact-info/',
      DETAIL: (id: number) => `/contact-info/${id}/`,
      ACTIVE: '/contact-info/active/',
    },
  },
} as const

/**
 * Build URL with query parameters
 * @param path - Base path
 * @param params - Query parameters object
 * @returns URL with query string
 */
export function buildUrl(path: string, params?: Record<string, any>): string {
  if (!params) return path
  
  const searchParams = new URLSearchParams()
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      searchParams.append(key, String(value))
    }
  })
  
  const queryString = searchParams.toString()
  return queryString ? `${path}?${queryString}` : path
}

/**
 * Build URL with path parameters
 * @param template - Path template with {param} placeholders
 * @param params - Path parameters object
 * @returns URL with parameters replaced
 * 
 * @example
 * buildPathUrl('/users/{id}/posts/{postId}/', { id: '123', postId: '456' })
 * // Returns: '/users/123/posts/456/'
 */
export function buildPathUrl(template: string, params: Record<string, string | number>): string {
  let url = template
  Object.entries(params).forEach(([key, value]) => {
    url = url.replace(`{${key}}`, String(value))
  })
  return url
}

/**
 * Type-safe path builder
 * Ensures all required parameters are provided
 */
export type PathBuilder<T extends string> = T extends `${infer _Start}{${infer Param}}${infer Rest}`
  ? (params: Record<Param, string | number>) => PathBuilder<Rest>
  : string

/**
 * Get all API paths as a flat array (useful for testing/validation)
 */
export function getAllApiPaths(): string[] {
  const paths: string[] = []
  
  function extractPaths(obj: any, prefix = ''): void {
    for (const [key, value] of Object.entries(obj)) {
      if (typeof value === 'string') {
        paths.push(value)
      } else if (typeof value === 'function') {
        // Skip functions (they're path builders)
        continue
      } else if (typeof value === 'object' && value !== null) {
        extractPaths(value, `${prefix}${key}.`)
      }
    }
  }
  
  extractPaths(API_PATHS)
  return paths
}
