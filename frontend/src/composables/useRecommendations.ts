import { ref, computed } from 'vue'
import { RecommendationService } from '../services/recommendations'
import { useToast } from './useToast'
import { useErrorHandler } from './useErrorHandler'
import type { 
  RecommendationResponse,
  SimilarCoursesResponse,
  TrendingCoursesResponse,
  Recommendation,
  RecommendationAnalytics
} from '../types/api'

export function useRecommendations() {
  // State
  const recommendations = ref<Recommendation[]>([])
  const userContext = ref<RecommendationResponse['user_context'] | null>(null)
  const similarCourses = ref<SimilarCoursesResponse['similar_courses']>([])
  const trendingCourses = ref<TrendingCoursesResponse['trending_courses']>([])
  const analytics = ref<RecommendationAnalytics | null>(null)
  const loading = ref(false)
  const error = ref<Error | null>(null)
  const algorithmUsed = ref<string>('')
  const context = ref<string>('')

  // Services
  const { success: showSuccess, info } = useToast()
  const { handleApiError } = useErrorHandler()

  // Computed
  const hasRecommendations = computed(() => recommendations.value.length > 0)
  const hasSimilarCourses = computed(() => similarCourses.value.length > 0)
  const hasTrendingCourses = computed(() => trendingCourses.value.length > 0)

  const recommendationsByAlgorithm = computed(() => {
    const grouped: Record<string, Recommendation[]> = {}
    recommendations.value.forEach(rec => {
      const algorithm = rec.recommendation_algorithm
      if (!grouped[algorithm]) {
        grouped[algorithm] = []
      }
      grouped[algorithm].push(rec)
    })
    return grouped
  })

  const topCategories = computed(() => {
    if (!userContext.value) return []
    return Object.entries(userContext.value.preferred_categories)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 3)
      .map(([category, count]) => ({ category, count }))
  })

  // Methods
  const loadRecommendations = async (options?: {
    limit?: number
    algorithm?: 'collaborative' | 'content_based' | 'popularity' | 'hybrid'
    context?: string
  }) => {
    loading.value = true
    error.value = null

    try {
      const response = await RecommendationService.getRecommendations(options)
      
      recommendations.value = response.recommendations
      userContext.value = response.user_context
      algorithmUsed.value = response.algorithm_used
      context.value = response.context

      // Track views for all recommendations
      const trackingPromises = response.recommendations.map((rec, index) =>
        RecommendationService.trackView(rec.course.id, {
          algorithm: rec.recommendation_algorithm,
          score: rec.recommendation_score,
          context: response.context,
          position: index + 1
        })
      )
      
      // Don't await tracking to avoid blocking UI
      Promise.all(trackingPromises).catch(console.error)

      return response
    } catch (err) {
      error.value = err as Error
      handleApiError(err as any, { 
        context: { action: 'load_recommendations' },
        showToast: false 
      })
      throw err
    } finally {
      loading.value = false
    }
  }

  const loadSimilarCourses = async (courseId: string, limit = 5) => {
    try {
      const response = await RecommendationService.getSimilarCourses(courseId, limit)
      similarCourses.value = response.similar_courses
      return response
    } catch (err) {
      handleApiError(err as any, { 
        context: { action: 'load_similar_courses', courseId },
        showToast: false 
      })
      throw err
    }
  }

  const loadTrendingCourses = async (options?: {
    limit?: number
    days?: number
  }) => {
    try {
      const response = await RecommendationService.getTrendingCourses(options)
      trendingCourses.value = response.trending_courses
      return response
    } catch (err) {
      handleApiError(err as any, { 
        context: { action: 'load_trending_courses' },
        showToast: false 
      })
      throw err
    }
  }

  const loadAnalytics = async (days = 30) => {
    try {
      const response = await RecommendationService.getAnalytics(days)
      analytics.value = response
      return response
    } catch (err) {
      handleApiError(err as any, { 
        context: { action: 'load_recommendation_analytics' },
        showToast: false 
      })
      throw err
    }
  }

  const trackClick = async (recommendation: Recommendation) => {
    try {
      await RecommendationService.trackClick(recommendation.course.id, {
        algorithm: recommendation.recommendation_algorithm,
        score: recommendation.recommendation_score,
        context: context.value,
        position: recommendation.position_in_list
      })
    } catch (err) {
      console.error('Failed to track click:', err)
    }
  }

  const trackWishlistAdd = async (recommendation: Recommendation) => {
    try {
      await RecommendationService.trackWishlistAdd(recommendation.course.id, {
        algorithm: recommendation.recommendation_algorithm,
        score: recommendation.recommendation_score,
        context: context.value,
        position: recommendation.position_in_list
      })
      
      showSuccess(`${recommendation.course.title} has been added to your wishlist`)
    } catch (err) {
      console.error('Failed to track wishlist add:', err)
    }
  }

  const trackEnrollment = async (recommendation: Recommendation) => {
    try {
      await RecommendationService.trackEnrollment(recommendation.course.id, {
        algorithm: recommendation.recommendation_algorithm,
        score: recommendation.recommendation_score,
        context: context.value,
        position: recommendation.position_in_list
      })
      
      showSuccess(`Successfully enrolled in ${recommendation.course.title}`)
    } catch (err) {
      console.error('Failed to track enrollment:', err)
    }
  }

  const trackDismiss = async (recommendation: Recommendation) => {
    try {
      await RecommendationService.trackDismiss(recommendation.course.id, {
        algorithm: recommendation.recommendation_algorithm,
        score: recommendation.recommendation_score,
        context: context.value,
        position: recommendation.position_in_list
      })
      
      // Remove from local state
      recommendations.value = recommendations.value.filter(
        rec => rec.course.id !== recommendation.course.id
      )
      
      info('We\'ll use this feedback to improve your recommendations')
    } catch (err) {
      console.error('Failed to track dismiss:', err)
    }
  }

  const refreshRecommendations = async (options?: {
    algorithm?: 'collaborative' | 'content_based' | 'popularity' | 'hybrid'
    context?: string
  }) => {
    await loadRecommendations({
      limit: recommendations.value.length || 10,
      ...options
    })
  }

  const getRecommendationsByCategory = (category: string) => {
    return recommendations.value.filter(rec => rec.course.category === category)
  }

  const getHighConfidenceRecommendations = (threshold = 0.7) => {
    return recommendations.value.filter(rec => rec.recommendation_score >= threshold)
  }

  const clearError = () => {
    error.value = null
  }

  const clearRecommendations = () => {
    recommendations.value = []
    userContext.value = null
    algorithmUsed.value = ''
    context.value = ''
  }

  return {
    // State
    recommendations,
    userContext,
    similarCourses,
    trendingCourses,
    analytics,
    loading,
    error,
    algorithmUsed,
    context,

    // Computed
    hasRecommendations,
    hasSimilarCourses,
    hasTrendingCourses,
    recommendationsByAlgorithm,
    topCategories,

    // Methods
    loadRecommendations,
    loadSimilarCourses,
    loadTrendingCourses,
    loadAnalytics,
    trackClick,
    trackWishlistAdd,
    trackEnrollment,
    trackDismiss,
    refreshRecommendations,
    getRecommendationsByCategory,
    getHighConfidenceRecommendations,
    clearError,
    clearRecommendations
  }
}

// Global recommendation tracking for cross-component usage
export function useRecommendationTracking() {
  const trackInteraction = async (
    courseId: string,
    interactionType: 'view' | 'click' | 'wishlist' | 'enroll' | 'dismiss',
    metadata?: {
      algorithm?: string
      score?: number
      context?: string
      position?: number
    }
  ) => {
    try {
      await RecommendationService.trackInteraction({
        course_id: courseId,
        interaction_type: interactionType,
        algorithm_used: metadata?.algorithm,
        recommendation_score: metadata?.score,
        context: metadata?.context,
        position_in_list: metadata?.position
      })
    } catch (err) {
      console.error(`Failed to track ${interactionType} interaction:`, err)
    }
  }

  return {
    trackInteraction
  }
}