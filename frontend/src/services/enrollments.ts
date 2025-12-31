import { api } from './api'
import type { Enrollment, PaginatedResponse } from '../types/api'

/**
 * Enrollment management service
 * Handles enrollment-related operations including progress tracking and reporting
 */
export class EnrollmentService {
  /**
   * Get all enrollments with optional filters
   * @param filters - Optional filter parameters
   * @returns Paginated list of enrollments
   */
  static async getEnrollments(filters?: {
    page?: number
    page_size?: number
    course?: string
    student?: string
    status?: string
  }): Promise<PaginatedResponse<Enrollment>> {
    try {
      const response = await api.get<PaginatedResponse<Enrollment>>('/enrollments/', {
        params: filters
      })
      return (response.data as any).data || response.data
    } catch (error) {
      console.error('Error fetching enrollments:', error)
      throw error
    }
  }

  /**
   * Get a single enrollment by ID
   * @param id - Enrollment ID
   * @returns Enrollment details
   */
  static async getEnrollment(id: string): Promise<Enrollment> {
    try {
      const response = await api.get<Enrollment>(`/enrollments/${id}/`)
      return (response.data as any).data || response.data
    } catch (error) {
      console.error('Error fetching enrollment:', error)
      throw error
    }
  }

  /**
   * Update enrollment progress
   * @param enrollmentId - Enrollment ID
   * @param progressPercentage - Progress percentage (0-100)
   * @returns Updated enrollment
   */
  static async updateProgress(enrollmentId: string, progressPercentage: number): Promise<Enrollment> {
    try {
      const response = await api.patch<Enrollment>(`/enrollments/${enrollmentId}/update_progress/`, {
        progress_percentage: progressPercentage
      })
      return (response.data as any).data || response.data
    } catch (error) {
      console.error('Error updating enrollment progress:', error)
      throw error
    }
  }

  /**
   * Update enrollment details
   * @param enrollmentId - Enrollment ID
   * @param data - Enrollment data to update
   * @returns Updated enrollment
   */
  static async updateEnrollment(enrollmentId: string, data: Partial<Enrollment>): Promise<Enrollment> {
    try {
      const response = await api.patch<Enrollment>(`/enrollments/${enrollmentId}/`, data)
      return (response.data as any).data || response.data
    } catch (error) {
      console.error('Error updating enrollment:', error)
      throw error
    }
  }

  /**
   * Drop/unenroll from a course
   * @param enrollmentId - Enrollment ID
   * @returns Updated enrollment with dropped status
   */
  static async dropCourse(enrollmentId: string): Promise<Enrollment> {
    try {
      const response = await api.post<Enrollment>(`/enrollments/${enrollmentId}/drop/`)
      return (response.data as any).data || response.data
    } catch (error) {
      console.error('Error dropping course:', error)
      throw error
    }
  }

  /**
   * Complete a course (set progress to 100%)
   * @param enrollmentId - Enrollment ID
   * @returns Updated enrollment with completed status
   */
  static async completeCourse(enrollmentId: string): Promise<Enrollment> {
    try {
      const response = await api.patch<Enrollment>(`/enrollments/${enrollmentId}/`, {
        progress_percentage: 100,
        status: 'completed',
        completed_at: new Date().toISOString()
      })
      return (response.data as any).data || response.data
    } catch (error) {
      console.error('Error completing course:', error)
      throw error
    }
  }

  /**
   * Resume a paused course
   * @param enrollmentId - Enrollment ID
   * @returns Updated enrollment with active status
   */
  static async resumeCourse(enrollmentId: string): Promise<Enrollment> {
    try {
      const response = await api.patch<Enrollment>(`/enrollments/${enrollmentId}/`, {
        status: 'active'
      })
      return (response.data as any).data || response.data
    } catch (error) {
      console.error('Error resuming course:', error)
      throw error
    }
  }

  /**
   * Pause an active course
   * @param enrollmentId - Enrollment ID
   * @returns Updated enrollment with paused status
   */
  static async pauseCourse(enrollmentId: string): Promise<Enrollment> {
    try {
      const response = await api.patch<Enrollment>(`/enrollments/${enrollmentId}/`, {
        status: 'paused'
      })
      return (response.data as any).data || response.data
    } catch (error) {
      console.error('Error pausing course:', error)
      throw error
    }
  }

  /**
   * Download student report for an enrollment
   * @param enrollmentId - Enrollment ID
   * @returns Blob containing the report file
   */
  static async downloadStudentReport(enrollmentId: string): Promise<Blob> {
    try {
      const response = await api.get(`/enrollments/${enrollmentId}/report/`, {
        responseType: 'blob'
      })
      return response.data as unknown as Blob
    } catch (error) {
      console.error('Error downloading student report:', error)
      throw error
    }
  }

  /**
   * Get enrollment analytics
   * @returns Enrollment analytics data
   */
  static async getEnrollmentAnalytics(): Promise<any> {
    try {
      const response = await api.get('/enrollments/analytics/')
      return (response.data as any).data || response.data
    } catch (error) {
      console.error('Error fetching enrollment analytics:', error)
      throw error
    }
  }

  /**
   * Get student dashboard data
   * @returns Student dashboard data including enrollments and progress
   */
  static async getStudentDashboard(): Promise<any> {
    try {
      const response = await api.get('/enrollments/dashboard/')
      return (response.data as any).data || response.data
    } catch (error) {
      console.error('Error fetching student dashboard:', error)
      throw error
    }
  }

  /**
   * Get detailed progress information for an enrollment
   * @param enrollmentId - Enrollment ID
   * @returns Detailed progress data
   */
  static async getProgressDetail(enrollmentId: string): Promise<any> {
    try {
      const response = await api.get(`/enrollments/${enrollmentId}/progress_detail/`)
      return (response.data as any).data || response.data
    } catch (error) {
      console.error('Error fetching progress detail:', error)
      throw error
    }
  }
}
