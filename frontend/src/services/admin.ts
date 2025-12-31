import { api } from './api'
import type { 
  User, 
  Organization, 
  AuditLog, 
  DashboardStats,
  PaginatedResponse,
  UserFilters,
  TeacherApproval,
  AuditLogFilters,
  UserAnalytics,
  CourseAnalyticsData,
  RevenueAnalytics
} from '../types/api'

export class AdminService {
  // Dashboard statistics
  static async getDashboardStats(): Promise<DashboardStats> {
    const response = await api.get<DashboardStats>('/admin/dashboard/stats/')
    return response.data.data
  }

  // User management
  static async getUsers(filters?: UserFilters): Promise<PaginatedResponse<User>> {
    const response = await api.get<PaginatedResponse<User>>('/accounts/users/', {
      params: filters
    })
    return response.data.data
  }

  static async getUser(id: string): Promise<User> {
    const response = await api.get<User>(`/accounts/users/${id}/`)
    return response.data.data
  }

  static async updateUser(id: string, userData: Partial<User>): Promise<User> {
    const response = await api.patch<User>(`/accounts/users/${id}/`, userData)
    return response.data.data
  }

  static async deleteUser(id: string): Promise<void> {
    await api.delete(`/accounts/users/${id}/`)
  }

  static async activateUser(id: string): Promise<User> {
    const response = await api.post<User>(`/accounts/users/${id}/activate/`)
    return response.data.data
  }

  static async deactivateUser(id: string): Promise<User> {
    const response = await api.post<User>(`/accounts/users/${id}/deactivate/`)
    return response.data.data
  }

  // Teacher approval management
  /**
   * Get teacher approval requests
   * @returns Paginated list of teacher approval requests
   */
  static async getTeacherApprovals(): Promise<PaginatedResponse<TeacherApproval>> {
    const response = await api.get<PaginatedResponse<TeacherApproval>>('/accounts/teacher-approvals/')
    return response.data.data
  }

  static async approveTeacher(id: string): Promise<void> {
    await api.post(`/accounts/teacher-approvals/${id}/approve/`)
  }

  static async rejectTeacher(id: string, notes?: string): Promise<void> {
    await api.post(`/accounts/teacher-approvals/${id}/reject/`, { notes })
  }

  // Organization management
  static async getOrganizations(): Promise<PaginatedResponse<Organization>> {
    const response = await api.get<PaginatedResponse<Organization>>('/accounts/organizations/')
    return response.data.data
  }

  static async getOrganization(id: string): Promise<Organization> {
    const response = await api.get<Organization>(`/accounts/organizations/${id}/`)
    return response.data.data
  }

  static async updateOrganization(id: string, orgData: Partial<Organization>): Promise<Organization> {
    const response = await api.patch<Organization>(`/accounts/organizations/${id}/`, orgData)
    return response.data.data
  }

  static async createOrganization(orgData: Partial<Organization>): Promise<Organization> {
    const response = await api.post<Organization>('/accounts/organizations/', orgData)
    return response.data.data
  }

  static async deleteOrganization(id: string): Promise<void> {
    await api.delete(`/accounts/organizations/${id}/`)
  }

  // Audit logs
  /**
   * Get audit logs with optional filtering
   * @param filters - Optional filters for audit logs
   * @returns Paginated list of audit logs
   */
  static async getAuditLogs(filters?: AuditLogFilters): Promise<PaginatedResponse<AuditLog>> {
    const response = await api.get<PaginatedResponse<AuditLog>>('/admin/audit-logs/', {
      params: filters
    })
    return response.data.data
  }

  // Analytics and reporting
  /**
   * Get user analytics for specified timeframe
   * @param timeframe - Time period for analytics
   * @returns User analytics data
   */
  static async getUserAnalytics(timeframe: 'day' | 'week' | 'month' | 'year' = 'month'): Promise<UserAnalytics> {
    const response = await api.get<UserAnalytics>('/admin/analytics/users/', {
      params: { timeframe }
    })
    return response.data.data
  }

  /**
   * Get course analytics for specified timeframe
   * @param timeframe - Time period for analytics
   * @returns Course analytics data
   */
  static async getCourseAnalytics(timeframe: 'day' | 'week' | 'month' | 'year' = 'month'): Promise<CourseAnalyticsData> {
    const response = await api.get<CourseAnalyticsData>('/admin/analytics/courses/', {
      params: { timeframe }
    })
    return response.data.data
  }

  /**
   * Get revenue analytics for specified timeframe
   * @param timeframe - Time period for analytics
   * @returns Revenue analytics data
   */
  static async getRevenueAnalytics(timeframe: 'day' | 'week' | 'month' | 'year' = 'month'): Promise<RevenueAnalytics> {
    const response = await api.get<RevenueAnalytics>('/admin/analytics/revenue/', {
      params: { timeframe }
    })
    return response.data.data
  }

  // System settings
  /**
   * Get system settings
   * @returns System settings configuration
   */
  static async getSystemSettings(): Promise<Record<string, unknown>> {
    const response = await api.get<Record<string, unknown>>('/admin/settings/')
    return response.data.data
  }

  /**
   * Update system settings
   * @param settings - Settings to update
   * @returns Updated system settings
   */
  static async updateSystemSettings(settings: Record<string, unknown>): Promise<Record<string, unknown>> {
    const response = await api.patch<Record<string, unknown>>('/admin/settings/', settings)
    return response.data.data
  }

  // Bulk operations
  static async bulkUpdateUsers(userIds: string[], updates: Partial<User>): Promise<void> {
    await api.post('/accounts/users/bulk_update/', {
      user_ids: userIds,
      updates
    })
  }

  static async bulkDeleteUsers(userIds: string[]): Promise<void> {
    await api.post('/accounts/users/bulk_delete/', {
      user_ids: userIds
    })
  }

  // Export functionality
  static async exportUsers(format: 'csv' | 'xlsx' = 'csv'): Promise<Blob> {
    const response = await api.get('/accounts/users/export/', {
      params: { format },
      responseType: 'blob'
    })
    return response.data.data
  }

  static async exportCourses(format: 'csv' | 'xlsx' = 'csv'): Promise<Blob> {
    const response = await api.get('/courses/export/', {
      params: { format },
      responseType: 'blob'
    })
    return response.data.data
  }

  static async exportEnrollments(format: 'csv' | 'xlsx' = 'csv'): Promise<Blob> {
    const response = await api.get('/enrollments/export/', {
      params: { format },
      responseType: 'blob'
    })
    return response.data.data
  }

  // User role management
  static async promoteToTeacher(userId: string): Promise<User> {
    const response = await api.post<User>(`/accounts/users/${userId}/promote_teacher/`)
    return response.data.data
  }

  static async promoteToAdmin(userId: string): Promise<User> {
    const response = await api.post<User>(`/accounts/users/${userId}/promote_admin/`)
    return response.data.data
  }

  static async demoteUser(userId: string): Promise<User> {
    const response = await api.post<User>(`/accounts/users/${userId}/demote/`)
    return response.data.data
  }

  // Organization statistics
  /**
   * Get organization statistics
   * @param orgId - Organization ID
   * @returns Organization statistics
   */
  static async getOrganizationStats(orgId: string): Promise<Record<string, unknown>> {
    const response = await api.get<Record<string, unknown>>(`/accounts/organizations/${orgId}/stats/`)
    return response.data.data
  }

  // Search and filtering utilities
  static buildUserFilters(params: {
    search?: string
    role?: 'student' | 'teacher' | 'admin'
    isActive?: boolean
    dateJoined?: [Date, Date]
  }): UserFilters {
    const filters: UserFilters = {}
    
    if (params.search) filters.search = params.search
    if (params.role === 'teacher') filters.is_teacher = true
    if (params.role === 'admin') filters.is_staff = true
    
    return filters
  }

  // Notification management for admins
  static async sendBulkNotification(userIds: string[], notification: {
    title: string
    message: string
    type: 'info' | 'success' | 'warning' | 'error'
  }): Promise<void> {
    await api.post('/admin/notifications/bulk_send/', {
      user_ids: userIds,
      ...notification
    })
  }

  static async sendSystemAnnouncement(announcement: {
    title: string
    message: string
    type: 'info' | 'success' | 'warning' | 'error'
    target_roles?: string[]
  }): Promise<void> {
    await api.post('/admin/announcements/', announcement)
  }

  // User profile management
  /**
   * Upload user avatar
   * @param file - Avatar image file
   * @returns URL of uploaded avatar
   */
  static async uploadAvatar(file: File): Promise<string> {
    try {
      const formData = new FormData()
      formData.append('avatar', file)
      
      const response = await api.post('/user-profiles/upload_avatar/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      return (response.data as any).data?.avatar_url || (response.data as any).avatar_url
    } catch (error) {
      console.error('Error uploading avatar:', error)
      throw error
    }
  }

  /**
   * Get current user's profile
   * @returns Current user profile
   */
  static async getCurrentUserProfile(): Promise<any> {
    try {
      const response = await api.get('/user-profiles/me/')
      return (response.data as any).data || response.data
    } catch (error) {
      console.error('Error fetching current user profile:', error)
      throw error
    }
  }

  /**
   * Update current user's profile
   * @param profileData - Profile data to update
   * @returns Updated profile
   */
  static async updateCurrentUserProfile(profileData: any): Promise<any> {
    try {
      const response = await api.patch('/user-profiles/me/', profileData)
      return (response.data as any).data || response.data
    } catch (error) {
      console.error('Error updating current user profile:', error)
      throw error
    }
  }
}