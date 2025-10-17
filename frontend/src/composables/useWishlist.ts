import { ref, computed, watch } from 'vue'
import { WishlistService } from '../services/wishlist'
import { useToast } from './useToast'
import { useErrorHandler } from './useErrorHandler'
import type { 
  Wishlist, 
  WishlistAnalytics, 
  WishlistFilters,
  PaginatedResponse 
} from '../types/api'

export function useWishlist() {
  // State
  const wishlistItems = ref<Wishlist[]>([])
  const analytics = ref<WishlistAnalytics | null>(null)
  const loading = ref(false)
  const error = ref<Error | null>(null)
  const totalCount = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(20)

  // Services
  const { showToast } = useToast()
  const { handleApiError } = useErrorHandler()

  // Computed
  const totalValue = computed(() => {
    return wishlistItems.value.reduce((total, item) => {
      return total + (item.course_price || 0)
    }, 0)
  })

  const totalItems = computed(() => wishlistItems.value.length)

  const categoryCounts = computed(() => {
    const counts: Record<string, number> = {}
    wishlistItems.value.forEach(item => {
      counts[item.course_category] = (counts[item.course_category] || 0) + 1
    })
    return counts
  })

  const priorityCounts = computed(() => {
    const counts = { high: 0, medium: 0, low: 0 }
    wishlistItems.value.forEach(item => {
      if (item.priority === 3) counts.high++
      else if (item.priority === 2) counts.medium++
      else counts.low++
    })
    return counts
  })

  const availableCourses = computed(() => {
    return wishlistItems.value.filter(item => item.is_course_available && !item.is_enrolled)
  })

  const enrolledCourses = computed(() => {
    return wishlistItems.value.filter(item => item.is_enrolled)
  })

  // Methods
  const loadWishlistItems = async (filters?: WishlistFilters) => {
    loading.value = true
    error.value = null

    try {
      const response: PaginatedResponse<Wishlist> = await WishlistService.getWishlistItems({
        ...filters,
        page: currentPage.value,
        page_size: pageSize.value
      })

      wishlistItems.value = response.results
      totalCount.value = response.count
      
      return response
    } catch (err) {
      error.value = err as Error
      handleApiError(err, { 
        context: { action: 'load_wishlist_items' },
        showToast: false 
      })
      throw err
    } finally {
      loading.value = false
    }
  }

  const loadAnalytics = async () => {
    try {
      analytics.value = await WishlistService.getWishlistAnalytics()
      return analytics.value
    } catch (err) {
      handleApiError(err, { 
        context: { action: 'load_wishlist_analytics' },
        showToast: false 
      })
      throw err
    }
  }

  const addToWishlist = async (courseId: string, options?: {
    priority?: 1 | 2 | 3
    notes?: string
    notify_price_change?: boolean
    notify_course_updates?: boolean
    notify_enrollment_opening?: boolean
  }) => {
    try {
      const item = await WishlistService.addCourseToWishlist(courseId, options)
      
      // Add to local state
      wishlistItems.value.unshift(item)
      totalCount.value++
      
      showToast({
        type: 'success',
        title: 'Added to Wishlist',
        message: `${item.course_title} has been added to your wishlist`
      })
      
      return item
    } catch (err) {
      handleApiError(err, { 
        context: { action: 'add_to_wishlist', courseId },
        showToast: true 
      })
      throw err
    }
  }

  const removeFromWishlist = async (courseId: string) => {
    try {
      await WishlistService.removeCourseFromWishlist(courseId)
      
      // Remove from local state
      const removedItem = wishlistItems.value.find(item => item.course === courseId)
      wishlistItems.value = wishlistItems.value.filter(item => item.course !== courseId)
      totalCount.value--
      
      showToast({
        type: 'success',
        title: 'Removed from Wishlist',
        message: removedItem ? `${removedItem.course_title} has been removed from your wishlist` : 'Course removed from wishlist'
      })
    } catch (err) {
      handleApiError(err, { 
        context: { action: 'remove_from_wishlist', courseId },
        showToast: true 
      })
      throw err
    }
  }

  const updateWishlistItem = async (id: string, updates: Partial<Wishlist>) => {
    try {
      const updatedItem = await WishlistService.updateWishlistItem(id, updates)
      
      // Update local state
      const index = wishlistItems.value.findIndex(item => item.id === id)
      if (index !== -1) {
        wishlistItems.value[index] = updatedItem
      }
      
      showToast({
        type: 'success',
        title: 'Wishlist Updated',
        message: 'Your wishlist item has been updated'
      })
      
      return updatedItem
    } catch (err) {
      handleApiError(err, { 
        context: { action: 'update_wishlist_item', itemId: id },
        showToast: true 
      })
      throw err
    }
  }

  const toggleWishlist = async (courseId: string) => {
    try {
      const result = await WishlistService.toggleWishlist(courseId)
      
      if (result.added && result.item) {
        // Added to wishlist
        wishlistItems.value.unshift(result.item)
        totalCount.value++
        
        showToast({
          type: 'success',
          title: 'Added to Wishlist',
          message: `${result.item.course_title} has been added to your wishlist`
        })
      } else {
        // Removed from wishlist
        const removedItem = wishlistItems.value.find(item => item.course === courseId)
        wishlistItems.value = wishlistItems.value.filter(item => item.course !== courseId)
        totalCount.value--
        
        showToast({
          type: 'success',
          title: 'Removed from Wishlist',
          message: removedItem ? `${removedItem.course_title} has been removed from your wishlist` : 'Course removed from wishlist'
        })
      }
      
      return result
    } catch (err) {
      handleApiError(err, { 
        context: { action: 'toggle_wishlist', courseId },
        showToast: true 
      })
      throw err
    }
  }

  const bulkEnroll = async (courseIds: string[]) => {
    try {
      const result = await WishlistService.bulkEnrollFromWishlist(courseIds)
      
      // Remove successfully enrolled courses from wishlist
      if (result.enrolled_courses.length > 0) {
        const enrolledCourseIds = result.enrolled_courses.map(course => course.course_id)
        wishlistItems.value = wishlistItems.value.filter(
          item => !enrolledCourseIds.includes(item.course)
        )
        totalCount.value -= result.enrolled_courses.length
      }
      
      // Show results
      if (result.total_enrolled > 0) {
        showToast({
          type: 'success',
          title: 'Enrollment Successful',
          message: `Successfully enrolled in ${result.total_enrolled} course${result.total_enrolled > 1 ? 's' : ''}`
        })
      }
      
      if (result.total_failed > 0) {
        showToast({
          type: 'warning',
          title: 'Some Enrollments Failed',
          message: `${result.total_failed} enrollment${result.total_failed > 1 ? 's' : ''} could not be completed`
        })
      }
      
      return result
    } catch (err) {
      handleApiError(err, { 
        context: { action: 'bulk_enroll', courseIds },
        showToast: true 
      })
      throw err
    }
  }

  const updateNotificationPreferences = async (preferences: {
    notify_price_change?: boolean
    notify_course_updates?: boolean
    notify_enrollment_opening?: boolean
  }) => {
    try {
      const result = await WishlistService.updateNotificationPreferences(preferences)
      
      // Update local state
      wishlistItems.value.forEach(item => {
        if (preferences.notify_price_change !== undefined) {
          item.notify_price_change = preferences.notify_price_change
        }
        if (preferences.notify_course_updates !== undefined) {
          item.notify_course_updates = preferences.notify_course_updates
        }
        if (preferences.notify_enrollment_opening !== undefined) {
          item.notify_enrollment_opening = preferences.notify_enrollment_opening
        }
      })
      
      showToast({
        type: 'success',
        title: 'Preferences Updated',
        message: `Updated notification preferences for ${result.updated_count} item${result.updated_count > 1 ? 's' : ''}`
      })
      
      return result
    } catch (err) {
      handleApiError(err, { 
        context: { action: 'update_notification_preferences' },
        showToast: true 
      })
      throw err
    }
  }

  const isInWishlist = (courseId: string): boolean => {
    return wishlistItems.value.some(item => item.course === courseId)
  }

  const getWishlistItem = (courseId: string): Wishlist | undefined => {
    return wishlistItems.value.find(item => item.course === courseId)
  }

  const refresh = async (filters?: WishlistFilters) => {
    await loadWishlistItems(filters)
  }

  const clearError = () => {
    error.value = null
  }

  // Pagination
  const nextPage = async (filters?: WishlistFilters) => {
    currentPage.value++
    await loadWishlistItems(filters)
  }

  const previousPage = async (filters?: WishlistFilters) => {
    if (currentPage.value > 1) {
      currentPage.value--
      await loadWishlistItems(filters)
    }
  }

  const goToPage = async (page: number, filters?: WishlistFilters) => {
    currentPage.value = page
    await loadWishlistItems(filters)
  }

  return {
    // State
    wishlistItems,
    analytics,
    loading,
    error,
    totalCount,
    currentPage,
    pageSize,

    // Computed
    totalValue,
    totalItems,
    categoryCounts,
    priorityCounts,
    availableCourses,
    enrolledCourses,

    // Methods
    loadWishlistItems,
    loadAnalytics,
    addToWishlist,
    removeFromWishlist,
    updateWishlistItem,
    toggleWishlist,
    bulkEnroll,
    updateNotificationPreferences,
    isInWishlist,
    getWishlistItem,
    refresh,
    clearError,

    // Pagination
    nextPage,
    previousPage,
    goToPage
  }
}

// Global wishlist state for cross-component usage
const globalWishlistState = ref<string[]>([]) // Array of course IDs in wishlist

export function useGlobalWishlist() {
  const { showToast } = useToast()
  const { handleApiError } = useErrorHandler()

  const isInWishlist = (courseId: string): boolean => {
    return globalWishlistState.value.includes(courseId)
  }

  const addToGlobalWishlist = (courseId: string) => {
    if (!globalWishlistState.value.includes(courseId)) {
      globalWishlistState.value.push(courseId)
    }
  }

  const removeFromGlobalWishlist = (courseId: string) => {
    const index = globalWishlistState.value.indexOf(courseId)
    if (index > -1) {
      globalWishlistState.value.splice(index, 1)
    }
  }

  const toggleGlobalWishlist = async (courseId: string) => {
    try {
      const result = await WishlistService.toggleWishlist(courseId)
      
      if (result.added) {
        addToGlobalWishlist(courseId)
        showToast({
          type: 'success',
          title: 'Added to Wishlist',
          message: result.item ? `${result.item.course_title} added to wishlist` : 'Course added to wishlist'
        })
      } else {
        removeFromGlobalWishlist(courseId)
        showToast({
          type: 'success',
          title: 'Removed from Wishlist',
          message: 'Course removed from wishlist'
        })
      }
      
      return result
    } catch (err) {
      handleApiError(err, { 
        context: { action: 'toggle_global_wishlist', courseId },
        showToast: true 
      })
      throw err
    }
  }

  const loadGlobalWishlistState = async () => {
    try {
      const response = await WishlistService.getWishlistItems()
      globalWishlistState.value = response.results.map(item => item.course)
    } catch (err) {
      console.error('Failed to load global wishlist state:', err)
    }
  }

  return {
    wishlistCourseIds: globalWishlistState,
    isInWishlist,
    addToGlobalWishlist,
    removeFromGlobalWishlist,
    toggleGlobalWishlist,
    loadGlobalWishlistState
  }
}