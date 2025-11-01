import { api } from './api'
import type { Course, Organization } from '../types/api'

export interface OrganizationCoursesResponse {
  results: Course[]
  count: number
  next: string | null
  previous: string | null
}

export class OrganizationService {
  /**
   * Get all available organizations
   */
  static async getOrganizations(): Promise<Organization[]> {
    try {
      const response = await api.get('/organizations/marketplace_summary/')
      const data = response.data as any
      return data.data || data.results || data || []
    } catch (error) {
      console.error('Failed to fetch organizations:', error)
      // Fallback to basic organizations endpoint
      try {
        const fallbackResponse = await api.get('/organizations/')
        const fallbackData = fallbackResponse.data as any
        return fallbackData.results || fallbackData.data || fallbackData || []
      } catch (fallbackError) {
        console.error('Fallback organizations fetch also failed:', fallbackError)
        return []
      }
    }
  }

  /**
   * Get courses for a specific organization
   */
  static async getOrganizationCourses(
    orgId: string, 
    page: number = 1, 
    pageSize: number = 6
  ): Promise<OrganizationCoursesResponse> {
    try {
      const response = await api.get('/courses/', {
        params: {
          tenant: orgId,
          page,
          page_size: pageSize,
          is_public: true
        }
      })
      
      const data = response.data as any
      return {
        results: data.results || data.data || data || [],
        count: data.count || 0,
        next: data.next || null,
        previous: data.previous || null
      }
    } catch (error) {
      console.error(`Failed to fetch courses for organization ${orgId}:`, error)
      return {
        results: [],
        count: 0,
        next: null,
        previous: null
      }
    }
  }

  /**
   * Get main platform courses (tenant: 'main')
   */
  static async getMainCourses(
    page: number = 1, 
    pageSize: number = 12
  ): Promise<OrganizationCoursesResponse> {
    try {
      const response = await api.get('/courses/', {
        params: {
          tenant: 'main',
          page,
          page_size: pageSize,
          is_public: true
        }
      })
      
      const data = response.data as any
      return {
        results: data.results || data.data || data || [],
        count: data.count || 0,
        next: data.next || null,
        previous: data.previous || null
      }
    } catch (error) {
      console.error('Failed to fetch main platform courses:', error)
      return {
        results: [],
        count: 0,
        next: null,
        previous: null
      }
    }
  }

  /**
   * Get featured courses for main platform
   */
  static async getFeaturedMainCourses(): Promise<Course[]> {
    try {
      const response = await api.get('/courses/featured/', {
        params: {
          tenant: 'main'
        }
      })
      
      const data = response.data as any
      const courses = data.data || data.results || data || []
      return Array.isArray(courses) ? courses.slice(0, 6) : []
    } catch (error) {
      console.error('Failed to fetch featured main courses:', error)
      return []
    }
  }

  /**
   * Search courses across all organizations
   */
  static async searchCourses(
    query: string,
    filters?: {
      category?: string
      difficulty?: string
      minPrice?: number
      maxPrice?: number
      organization?: string
    }
  ): Promise<Course[]> {
    try {
      const params: any = {
        search: query,
        is_public: true
      }

      if (filters) {
        if (filters.category) params.category = filters.category
        if (filters.difficulty) params.difficulty_level = filters.difficulty
        if (filters.minPrice !== undefined) params.min_price = filters.minPrice
        if (filters.maxPrice !== undefined) params.max_price = filters.maxPrice
        if (filters.organization) params.tenant = filters.organization
      }

      const response = await api.get('/courses/', { params })
      const data = response.data as any
      return data.results || data.data || data || []
    } catch (error) {
      console.error('Failed to search courses:', error)
      return []
    }
  }

  /**
   * Get organization statistics
   */
  static async getOrganizationStats(orgId: string): Promise<{
    course_count: number
    student_count: number
    avg_rating: number
    total_revenue: number
  }> {
    try {
      const response = await api.get(`/organizations/${orgId}/stats/`)
      const data = response.data.data || response.data
      return {
        course_count: data?.course_statistics?.total_courses || 0,
        student_count: data?.student_statistics?.total_students || 0,
        avg_rating: data?.performance_metrics?.avg_rating || 0,
        total_revenue: data?.financial_statistics?.total_revenue || 0
      }
    } catch (error) {
      console.error(`Failed to fetch stats for organization ${orgId}:`, error)
      return {
        course_count: 0,
        student_count: 0,
        avg_rating: 0,
        total_revenue: 0
      }
    }
  }

  /**
   * Get organization subscription information (super admin only)
   */
  static async getOrganizationSubscription(orgId: string): Promise<{
    has_subscription: boolean
    current_plan?: any
    available_plans: any[]
    subscription_id?: string
    billing_cycle?: string
    status?: string
    current_period_start?: string
    current_period_end?: string
    amount?: number
  }> {
    try {
      const response = await api.get(`/organizations/${orgId}/subscription-info/`)
      const data = response.data as any
      return data.data || data
    } catch (error) {
      console.error(`Failed to fetch subscription info for organization ${orgId}:`, error)
      throw error
    }
  }

  /**
   * Change organization subscription plan (super admin only)
   */
  static async changeOrganizationSubscriptionPlan(orgId: string, planId: string): Promise<{
    organization_id: string
    organization_name: string
    old_plan?: string
    new_plan: string
    plan_details: any
  }> {
    try {
      const response = await api.post(`/organizations/${orgId}/change-subscription-plan/`, {
        plan_id: planId
      })
      const data = response.data as any
      return data.data || data
    } catch (error) {
      console.error(`Failed to change subscription plan for organization ${orgId}:`, error)
      throw error
    }
  }
}