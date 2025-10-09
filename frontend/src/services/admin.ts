import { api } from './api'
import type { 
  User, 
  Organization, 
  AuditLog, 
  DashboardStats,
  PaginatedResponse,
  UserFilters 
} from '../types/api'

export class AdminService {
  // Dashboard statistics
  static async getDashboardStats(): Promise<DashboardStats> {
    const response = await api.get<DashboardStats>('/admin/dashboard/stats/')
    return response.data
  }

  // User management
  static async getUsers(filters?: UserFilters): Promise<PaginatedResponse<User>> {
    const response = await api.get<PaginatedResponse<User>>('/accounts/users/', {
      params: filters
    })
    return response.data
  }

  static async getUser(id: string): Promise<User> {
    const response = await api.get<User>(`/accounts/users/${id}/`)
    return response.data
  }

  static async updateUser(id: string, userData: Partial<User>): Promise<User> {
    const response = await api.patch<User>(`/accounts/users/${id}/`, userData)
    return response.data
  }

  static async deleteUser(id: string): Promise<void> {
    await api.delete(`/accounts/users/${id}/`)
  }

  static async activateUser(id: string): Promise<User> {
    const response = await api.post<User>(`/accounts/users/${id}/activate/`)
    return response.data
  }

  static async deactivateUser(id: string): Promise<User> {
    const response = await api.post<User>(`/accounts/users/${id}/deactivate/`)
    return response.data
  }

  // Teacher approval management
  static async getTeacherApprovals(): Promise<PaginatedResponse<any>> {
    const response = await api.get<PaginatedResponse<any>>('/accounts/teacher-approvals/')
    return response.data
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
    return response.data
  }

  static async getOrganization(id: string): Promise<Organization> {
    const response = await api.get<Organization>(`/accounts/organizations/${id}/`)
    return response.data
  }

  static async updateOrganization(id: string, orgData: Partial<Organization>): Promise<Organization> {
    const response = await api.patch<Organization>(`/accounts/organizations/${id}/`, orgData)
    return response.data
  }

  static async createOrganization(orgData: Partial<Organization>): Promise<Organization> {
    const response = await api.post<Organization>('/accounts/organizations/', orgData)
    return response.data
  }

  static async deleteOrganization(id: string): Promise<void> {
    await api.delete(`/accounts/organizations/${id}/`)
  }

  // Audit logs
  static async getAuditLogs(filters?: any): Promise<PaginatedResponse<AuditLog>> {
    const response = await api.get<PaginatedResponse<AuditLog>>('/admin/audit-logs/', {
      params: filters
    })
    return response.data
  }

  // Analytics and reporting
  static async getUserAnalytics(timeframe: 'day' | 'week' | 'month' | 'year' = 'month'): Promise<any> {
    const response = await api.get('/admin/analytics/users/', {
      params: { timeframe }
    })
    return response.data
  }

  static async getCourseAnalytics(timeframe: 'day' | 'week' | 'month' | 'year' = 'month'): Promise<any> {
    const response = await api.get('/admin/analytics/courses/', {
      params: { timeframe }
    })
    return response.data
  }

  static async getRevenueAnalytics(timeframe: 'day' | 'week' | 'month' | 'year' = 'month'): Promise<any> {
    const response = await api.get('/admin/analytics/revenue/', {
      params: { timeframe }
    })
    return response.data
  }

  // System settings
  static async getSystemSettings(): Promise<any> {
    const response = await api.get('/admin/settings/')
    return response.data
  }

  static async updateSystemSettings(settings: any): Promise<any> {
    const response = await api.patch('/admin/settings/', settings)
    return response.data
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
    return response.data
  }

  static async exportCourses(format: 'csv' | 'xlsx' = 'csv'): Promise<Blob> {
    const response = await api.get('/courses/courses/export/', {
      params: { format },
      responseType: 'blob'
    })
    return response.data
  }

  static async exportEnrollments(format: 'csv' | 'xlsx' = 'csv'): Promise<Blob> {
    const response = await api.get('/courses/enrollments/export/', {
      params: { format },
      responseType: 'blob'
    })
    return response.data
  }

  // User role management
  static async promoteToTeacher(userId: string): Promise<User> {
    const response = await api.post<User>(`/accounts/users/${userId}/promote_teacher/`)
    return response.data
  }

  static async promoteToAdmin(userId: string): Promise<User> {
    const response = await api.post<User>(`/accounts/users/${userId}/promote_admin/`)
    return response.data
  }

  static async demoteUser(userId: string): Promise<User> {
    const response = await api.post<User>(`/accounts/users/${userId}/demote/`)
    return response.data
  }

  // Organization statistics
  static async getOrganizationStats(orgId: string): Promise<any> {
    const response = await api.get(`/accounts/organizations/${orgId}/stats/`)
    return response.data
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
}