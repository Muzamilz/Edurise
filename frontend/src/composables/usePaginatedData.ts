import { ref, computed, watch } from 'vue'
import { useApiData } from './useApiData'
// Removed unused import

export interface PaginationMeta {
  current_page: number
  total_pages: number
  page_size: number
  total_count: number
  has_next: boolean
  has_previous: boolean
  next_page?: number
  previous_page?: number
}

export interface PaginatedResponse<T> {
  results: T[]
  meta: {
    pagination: PaginationMeta
  }
}

export interface UsePaginatedDataOptions {
  pageSize?: number
  immediate?: boolean
  cacheKey?: string
  cacheTTL?: number
}

export const usePaginatedData = <T>(
  endpoint: string | (() => string),
  options: UsePaginatedDataOptions = {}
) => {
  const {
    pageSize = 20,
    immediate = true,
    cacheKey,
    // cacheTTL = 300000 // 5 minutes - removed unused parameter
  } = options

  const currentPage = ref(1)
  const searchQuery = ref('')
  const filters = ref<Record<string, any>>({})
  const ordering = ref<string>('')

  // Build query parameters
  const queryParams = computed(() => {
    const params: Record<string, any> = {
      page: currentPage.value,
      page_size: pageSize
    }

    if (searchQuery.value) {
      params.search = searchQuery.value
    }

    if (ordering.value) {
      params.ordering = ordering.value
    }

    // Add filters
    Object.entries(filters.value).forEach(([key, value]) => {
      if (value !== null && value !== undefined && value !== '') {
        params[key] = value
      }
    })

    return params
  })

  // Build full endpoint with query parameters
  const fullEndpoint = computed(() => {
    const baseEndpoint = typeof endpoint === 'function' ? endpoint() : endpoint
    const params = new URLSearchParams()
    
    Object.entries(queryParams.value).forEach(([key, value]) => {
      if (Array.isArray(value)) {
        value.forEach(v => params.append(key, v.toString()))
      } else {
        params.append(key, value.toString())
      }
    })

    return `${baseEndpoint}?${params.toString()}`
  })

  // Use the base useApiData composable
  const {
    data: rawData,
    loading,
    error,
    refresh: refreshData
  } = useApiData<PaginatedResponse<T>>(() => fullEndpoint.value, {
    immediate,
    cacheKey: cacheKey ? `${cacheKey}_${JSON.stringify(queryParams.value)}` : undefined
  })

  // Extract data and pagination info
  const data = computed(() => rawData.value?.results || [])
  const pagination = computed(() => rawData.value?.meta?.pagination || null)

  // Pagination helpers
  const hasNextPage = computed(() => pagination.value?.has_next || false)
  const hasPreviousPage = computed(() => pagination.value?.has_previous || false)
  const totalPages = computed(() => pagination.value?.total_pages || 0)
  const totalCount = computed(() => pagination.value?.total_count || 0)

  // Navigation methods
  const goToPage = async (page: number) => {
    if (page >= 1 && page <= totalPages.value) {
      currentPage.value = page
      await refreshData()
    }
  }

  const nextPage = async () => {
    if (hasNextPage.value) {
      await goToPage(currentPage.value + 1)
    }
  }

  const previousPage = async () => {
    if (hasPreviousPage.value) {
      await goToPage(currentPage.value - 1)
    }
  }

  const firstPage = async () => {
    await goToPage(1)
  }

  const lastPage = async () => {
    await goToPage(totalPages.value)
  }

  // Search and filter methods
  const search = async (query: string) => {
    searchQuery.value = query
    currentPage.value = 1 // Reset to first page
    await refreshData()
  }

  const setFilter = async (key: string, value: any) => {
    filters.value[key] = value
    currentPage.value = 1 // Reset to first page
    await refreshData()
  }

  const removeFilter = async (key: string) => {
    delete filters.value[key]
    currentPage.value = 1 // Reset to first page
    await refreshData()
  }

  const clearFilters = async () => {
    filters.value = {}
    searchQuery.value = ''
    currentPage.value = 1
    await refreshData()
  }

  const setOrdering = async (field: string, direction: 'asc' | 'desc' = 'asc') => {
    ordering.value = direction === 'desc' ? `-${field}` : field
    currentPage.value = 1 // Reset to first page
    await refreshData()
  }

  const clearOrdering = async () => {
    ordering.value = ''
    currentPage.value = 1
    await refreshData()
  }

  // Refresh method
  const refresh = async () => {
    await refreshData()
  }

  // Reset all state
  const reset = () => {
    currentPage.value = 1
    searchQuery.value = ''
    filters.value = {}
    ordering.value = ''
  }

  // Watch for changes in dependencies and refresh
  watch([searchQuery, filters, ordering], async () => {
    if (immediate) {
      await refreshData()
    }
  }, { deep: true })

  return {
    // Data
    data,
    loading,
    error,
    
    // Pagination info
    pagination,
    currentPage: computed(() => currentPage.value),
    totalPages,
    totalCount,
    hasNextPage,
    hasPreviousPage,
    
    // Navigation
    goToPage,
    nextPage,
    previousPage,
    firstPage,
    lastPage,
    
    // Search and filtering
    searchQuery: computed({
      get: () => searchQuery.value,
      set: (value: string) => { searchQuery.value = value }
    }),
    search,
    setFilter,
    removeFilter,
    clearFilters,
    filters: computed(() => filters.value),
    
    // Ordering
    ordering: computed({
      get: () => ordering.value,
      set: (value: string) => { ordering.value = value }
    }),
    setOrdering,
    clearOrdering,
    
    // Actions
    refresh,
    reset
  }
}

// Specialized composables for common use cases
export const useCourses = (options?: UsePaginatedDataOptions) => {
  return usePaginatedData('/courses/', {
    cacheKey: 'courses',
    ...options
  })
}

export const useEnrollments = (options?: UsePaginatedDataOptions) => {
  return usePaginatedData('/enrollments/', {
    cacheKey: 'enrollments',
    ...options
  })
}

export const useUsers = (options?: UsePaginatedDataOptions) => {
  return usePaginatedData('/users/', {
    cacheKey: 'users',
    ...options
  })
}

export const useNotifications = (options?: UsePaginatedDataOptions) => {
  return usePaginatedData('/api/v1/notifications/', {
    cacheKey: 'notifications',
    ...options
  })
}

export const usePayments = (options?: UsePaginatedDataOptions) => {
  return usePaginatedData('/payments/', {
    cacheKey: 'payments',
    ...options
  })
}

export const useLiveClasses = (options?: UsePaginatedDataOptions) => {
  return usePaginatedData('/live-classes/', {
    cacheKey: 'live-classes',
    ...options
  })
}