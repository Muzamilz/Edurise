import { api } from './api'
import type { 
  RecommendationResponse,
  SimilarCoursesResponse,
  TrendingCoursesResponse,
  RecommendationInteraction,
  RecommendationAnalytics
} from '../types/api'

export class RecommendationService {
  // Get personalized recommendations
  static async getRecommendations(options?: {
    limit?: number
    algorithm?: 'collaborative' | 'content_based' | 'popularity' | 'hybrid'
    context?: string
  }): Promise<RecommendationResponse> {
    const params = {
      limit: options?.limit || 10,
      algorithm: options?.algorithm || 'hybrid',
      context: options?.context || 'general'
    }
    
    const response = await api.get('/courses/recommendations/', { params })
    return response.data.data
  }

  // Get similar courses to a specific course
  static async getSimilarCourses(courseId: string, limit = 5): Promise<SimilarCoursesResponse> {
    const response = await api.get('/courses/recommendations/similar_courses/', {
      params: { course_id: courseId, limit }
    })
    return response.data.data
  }

  // Get trending courses
  static async getTrendingCourses(options?: {
    limit?: number
    days?: number
  }): Promise<TrendingCoursesResponse> {
    const params = {
      limit: options?.limit || 10,
      days: options?.days || 7
    }
    
    const response = await api.get('/courses/recommendations/trending/', { params })
    return response.data.data
  }

  // Track user interaction with recommendations
  static async trackInteraction(interaction: RecommendationInteraction): Promise<{ interaction_id: string }> {
    const response = await api.post('/courses/recommendations/track_interaction/', interaction)
    return response.data.data
  }

  // Get recommendation analytics (admin only)
  static async getAnalytics(days = 30): Promise<RecommendationAnalytics> {
    const response = await api.get('/courses/recommendations/analytics/', {
      params: { days }
    })
    return response.data.data
  }

  // Helper method to track multiple interactions at once
  static async trackMultipleInteractions(interactions: RecommendationInteraction[]): Promise<void> {
    const promises = interactions.map(interaction => this.trackInteraction(interaction))
    await Promise.all(promises)
  }

  // Track recommendation view (convenience method)
  static async trackView(courseId: string, metadata?: {
    algorithm?: string
    score?: number
    context?: string
    position?: number
  }): Promise<void> {
    await this.trackInteraction({
      course_id: courseId,
      interaction_type: 'view',
      algorithm_used: metadata?.algorithm,
      recommendation_score: metadata?.score,
      context: metadata?.context,
      position_in_list: metadata?.position
    })
  }

  // Track recommendation click (convenience method)
  static async trackClick(courseId: string, metadata?: {
    algorithm?: string
    score?: number
    context?: string
    position?: number
  }): Promise<void> {
    await this.trackInteraction({
      course_id: courseId,
      interaction_type: 'click',
      algorithm_used: metadata?.algorithm,
      recommendation_score: metadata?.score,
      context: metadata?.context,
      position_in_list: metadata?.position
    })
  }

  // Track wishlist addition (convenience method)
  static async trackWishlistAdd(courseId: string, metadata?: {
    algorithm?: string
    score?: number
    context?: string
    position?: number
  }): Promise<void> {
    await this.trackInteraction({
      course_id: courseId,
      interaction_type: 'wishlist',
      algorithm_used: metadata?.algorithm,
      recommendation_score: metadata?.score,
      context: metadata?.context,
      position_in_list: metadata?.position
    })
  }

  // Track enrollment (convenience method)
  static async trackEnrollment(courseId: string, metadata?: {
    algorithm?: string
    score?: number
    context?: string
    position?: number
  }): Promise<void> {
    await this.trackInteraction({
      course_id: courseId,
      interaction_type: 'enroll',
      algorithm_used: metadata?.algorithm,
      recommendation_score: metadata?.score,
      context: metadata?.context,
      position_in_list: metadata?.position
    })
  }

  // Track dismissal (convenience method)
  static async trackDismiss(courseId: string, metadata?: {
    algorithm?: string
    score?: number
    context?: string
    position?: number
  }): Promise<void> {
    await this.trackInteraction({
      course_id: courseId,
      interaction_type: 'dismiss',
      algorithm_used: metadata?.algorithm,
      recommendation_score: metadata?.score,
      context: metadata?.context,
      position_in_list: metadata?.position
    })
  }
}