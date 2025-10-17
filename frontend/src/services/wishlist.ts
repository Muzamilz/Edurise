import { api } from './api'
import type { 
  Wishlist, 
  WishlistAnalytics, 
  WishlistFilters,
  PaginatedResponse 
} from '../types/api'

export class WishlistService {
  // Basic CRUD operations
  static async getWishlistItems(filters?: WishlistFilters): Promise<PaginatedResponse<Wishlist>> {
    const response = await api.get('/courses/wishlist/', { params: filters })
    return response.data.data
  }

  static async getWishlistItem(id: string): Promise<Wishlist> {
    const response = await api.get(`/courses/wishlist/${id}/`)
    return response.data.data
  }

  static async createWishlistItem(wishlistData: Partial<Wishlist>): Promise<Wishlist> {
    const response = await api.post('/courses/wishlist/', wishlistData)
    return response.data.data
  }

  static async updateWishlistItem(id: string, wishlistData: Partial<Wishlist>): Promise<Wishlist> {
    const response = await api.patch(`/courses/wishlist/${id}/`, wishlistData)
    return response.data.data
  }

  static async deleteWishlistItem(id: string): Promise<void> {
    await api.delete(`/courses/wishlist/${id}/`)
  }

  // Convenient methods for adding/removing courses
  static async addCourseToWishlist(courseId: string, options?: {
    priority?: 1 | 2 | 3
    notes?: string
    notify_price_change?: boolean
    notify_course_updates?: boolean
    notify_enrollment_opening?: boolean
  }): Promise<Wishlist> {
    const response = await api.post('/courses/wishlist/add_course/', {
      course_id: courseId,
      priority: options?.priority || 2,
      notes: options?.notes || '',
      notify_price_change: options?.notify_price_change ?? true,
      notify_course_updates: options?.notify_course_updates ?? true,
      notify_enrollment_opening: options?.notify_enrollment_opening ?? true
    })
    return response.data.data
  }

  static async removeCourseFromWishlist(courseId: string): Promise<void> {
    await api.delete('/courses/wishlist/remove_course/', {
      data: { course_id: courseId }
    })
  }

  // Analytics and insights
  static async getWishlistAnalytics(): Promise<WishlistAnalytics> {
    const response = await api.get('/courses/wishlist/analytics/')
    return response.data.data
  }

  // Bulk operations
  static async bulkEnrollFromWishlist(courseIds: string[]): Promise<{
    enrolled_courses: Array<{
      course_id: string
      course_title: string
      enrollment_id: string
    }>
    failed_enrollments: Array<{
      course_id: string
      course_title: string
      reason: string
    }>
    total_enrolled: number
    total_failed: number
  }> {
    const response = await api.post('/courses/wishlist/bulk_enroll/', {
      course_ids: courseIds
    })
    return response.data.data
  }

  // Notification preferences
  static async updateNotificationPreferences(preferences: {
    notify_price_change?: boolean
    notify_course_updates?: boolean
    notify_enrollment_opening?: boolean
  }): Promise<{ updated_count: number }> {
    const response = await api.post('/courses/wishlist/update_notifications/', preferences)
    return response.data.data
  }

  // Helper methods
  static async isInWishlist(courseId: string): Promise<boolean> {
    try {
      const wishlistItems = await this.getWishlistItems()
      return wishlistItems.results.some(item => item.course === courseId)
    } catch (error) {
      console.error('Error checking wishlist status:', error)
      return false
    }
  }

  static async toggleWishlist(courseId: string): Promise<{ added: boolean; item?: Wishlist }> {
    const isInWishlist = await this.isInWishlist(courseId)
    
    if (isInWishlist) {
      await this.removeCourseFromWishlist(courseId)
      return { added: false }
    } else {
      const item = await this.addCourseToWishlist(courseId)
      return { added: true, item }
    }
  }
}