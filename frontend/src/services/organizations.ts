import { api } from './api'
import type { Organization, User, Course, PaginatedResponse } from '../types/api'

/**
 * Organization management service
 * Handles all organization-related API operations for super-admin features
 */
export class OrganizationService {
  /**
   * Get a single organization by ID
   * @param id - Organization ID
   * @returns Organization details
   */
  static async getOrganization(id: string): Promise<Organization> {
    try {
      const response = await api.get<Organization>(`/organizations/${id}/`)
      return (response.data as any).data || response.data
    } catch (error) {
      console.error('Error fetching organization:', error)
      throw error
    }
  }

  /**
   * Get all organizations with optional filters
   * @param filters - Optional filter parameters
   * @returns Paginated list of organizations
   */
  static async getOrganizations(filters?: {
    page?: number
    page_size?: number
    is_active?: boolean
    search?: string
  }): Promise<PaginatedResponse<Organization>> {
    try {
      const response = await api.get<PaginatedResponse<Organization>>('/organizations/', {
        params: filters
      })
      return (response.data as any).data || response.data
    } catch (error) {
      console.error('Error fetching organizations:', error)
      throw error
    }
  }

  /**
   * Create a new organization
   * @param organizationData - Organization data
   * @returns Created organization
   */
  static async createOrganization(organizationData: Partial<Organization>): Promise<Organization> {
    try {
      const response = await api.post<Organization>('/organizations/', organizationData)
      return (response.data as any).data || response.data
    } catch (error) {
      console.error('Error creating organization:', error)
      throw error
    }
  }

  /**
   * Update an existing organization
   * @param id - Organization ID
   * @param organizationData - Updated organization data
   * @returns Updated organization
   */
  static async updateOrganization(id: string, organizationData: Partial<Organization>): Promise<Organization> {
    try {
      const response = await api.patch<Organization>(`/organizations/${id}/`, organizationData)
      return (response.data as any).data || response.data
    } catch (error) {
      console.error('Error updating organization:', error)
      throw error
    }
  }

  /**
   * Delete an organization
   * @param id - Organization ID
   */
  static async deleteOrganization(id: string): Promise<void> {
    try {
      await api.delete(`/organizations/${id}/`)
    } catch (error) {
      console.error('Error deleting organization:', error)
      throw error
    }
  }

  /**
   * Get users belonging to an organization
   * @param id - Organization ID
   * @returns List of users in the organization
   */
  static async getOrganizationUsers(id: string): Promise<User[]> {
    try {
      const response = await api.get<User[]>(`/organizations/${id}/users/`)
      return (response.data as any).data || response.data
    } catch (error) {
      console.error('Error fetching organization users:', error)
      throw error
    }
  }

  /**
   * Get courses belonging to an organization
   * @param id - Organization ID
   * @returns List of courses in the organization
   */
  static async getOrganizationCourses(id: string): Promise<Course[]> {
    try {
      const response = await api.get<Course[]>(`/organizations/${id}/courses/`)
      return (response.data as any).data || response.data
    } catch (error) {
      console.error('Error fetching organization courses:', error)
      throw error
    }
  }

  /**
   * Get organization statistics
   * @param id - Organization ID
   * @returns Organization statistics
   */
  static async getOrganizationStats(id: string): Promise<{
    total_users: number
    active_users: number
    total_courses: number
    total_enrollments: number
    total_revenue: number
    [key: string]: any
  }> {
    try {
      const response = await api.get(`/organizations/${id}/stats/`)
      return (response.data as any).data || response.data
    } catch (error) {
      console.error('Error fetching organization stats:', error)
      throw error
    }
  }

  /**
   * Switch current user's tenant/organization context
   * @param tenantId - Tenant/Organization ID to switch to
   * @returns Switch result with new token or context
   */
  static async switchTenant(tenantId: string): Promise<{
    success: boolean
    message: string
    token?: string
    organization?: Organization
  }> {
    try {
      const response = await api.post('/users/switch_tenant/', { tenant_id: tenantId })
      return (response.data as any).data || response.data
    } catch (error) {
      console.error('Error switching tenant:', error)
      throw error
    }
  }

  /**
   * Activate an organization
   * @param id - Organization ID
   * @returns Updated organization
   */
  static async activateOrganization(id: string): Promise<Organization> {
    return this.updateOrganization(id, { is_active: true })
  }

  /**
   * Deactivate an organization
   * @param id - Organization ID
   * @returns Updated organization
   */
  static async deactivateOrganization(id: string): Promise<Organization> {
    return this.updateOrganization(id, { is_active: false })
  }
}
