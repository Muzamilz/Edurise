import { ref, computed, onMounted, watch, type Ref } from 'vue'
import { api, type APIError } from '@/services/api'
import { apiCache, type CacheOptions, ApiCache } from '@/utils/apiCache'
import { getFallbackData, hasFallbackData } from '@/services/fallbackData'
import { useToast } from '@/composables/useToast'

// Generic data fetching composable with loading, error, and data states
export interface UseApiDataOptions<T> extends CacheOptions {
  immediate?: boolean
  transform?: (data: any) => T
  dependencies?: Ref[]
  cacheKey?: string
  retryAttempts?: number
  retryDelay?: number
  enableOptimisticUpdates?: boolean
  onError?: (error: APIError) => void
  onSuccess?: (data: T) => void
}

export interface UseApiDataReturn<T> {
  data: Readonly<Ref<T | null>>
  loading: Readonly<Ref<boolean>>
  error: Readonly<Ref<APIError | null>>
  fetch: () => Promise<void>
  refresh: () => Promise<void>
  reset: () => void
}

export const useApiData = <T>(
  endpoint: string | (() => string),
  options: UseApiDataOptions<T> = {}
): UseApiDataReturn<T> => {
  const {
    immediate = true,
    transform,
    dependencies = [],
    cacheKey,
    ttl,
    tags,
    persist,
    retryAttempts = 3,
    retryDelay = 1000,
    // enableOptimisticUpdates = false, // Unused
    onError,
    onSuccess
  } = options

  const data = ref<T | null>(null)
  const loading = ref(false)
  const error = ref<APIError | null>(null)
  const retryCount = ref(0)
  
  const { showToast } = useToast()

  const getEndpoint = () => {
    return typeof endpoint === 'function' ? endpoint() : endpoint
  }

  const getCacheKey = () => {
    if (cacheKey) return cacheKey
    return ApiCache.generateKey(getEndpoint())
  }

  const getCachedData = (): T | null => {
    return apiCache.get<T>(getCacheKey())
  }

  const setCachedData = (value: T) => {
    apiCache.set(getCacheKey(), value, {
      ttl,
      tags,
      persist,
      transform: options.transform
    })
  }

  const fetch = async (skipCache = false) => {
    // Check cache first unless explicitly skipped
    if (!skipCache) {
      const cachedData = getCachedData()
      if (cachedData) {
        data.value = cachedData
        onSuccess?.(cachedData)
        return
      }
    }

    loading.value = true
    error.value = null

    const attemptFetch = async (attempt: number): Promise<void> => {
      try {
        const response = await api.get(getEndpoint())
        const responseData = response.data.data || response.data

        const transformedData = transform ? transform(responseData) : responseData
        data.value = transformedData

        // Cache the data
        setCachedData(transformedData)

        // Reset retry count on success
        retryCount.value = 0

        // Call success callback
        onSuccess?.(transformedData)

      } catch (err) {
        const apiError = err as APIError

        // Retry logic for network errors and 5xx errors
        if (attempt < retryAttempts && shouldRetry(apiError)) {
          retryCount.value = attempt
          console.log(`🔄 Retrying API call (${attempt}/${retryAttempts}) for ${getEndpoint()}`)

          // Exponential backoff delay
          const delay = retryDelay * Math.pow(2, attempt - 1)
          await new Promise(resolve => setTimeout(resolve, delay))

          return attemptFetch(attempt + 1)
        }

        // If it's a 404 and we have fallback data, use that instead of showing error
        if (apiError.status === 404 && hasFallbackData(getEndpoint())) {
          const fallbackData = getFallbackData(getEndpoint())
          const transformedData = transform ? transform(fallbackData) : fallbackData
          data.value = transformedData

          // Cache the fallback data
          setCachedData(transformedData)

          console.log(`📋 Using fallback data for ${getEndpoint()}`)
          showToast('Using offline data - some features may be limited', 'warning')

          onSuccess?.(transformedData)
        } else {
          error.value = apiError
          console.error(`API Error for ${getEndpoint()}:`, err)

          // Call error callback
          onError?.(apiError)

          // Show user-friendly error message
          if (apiError.status === 0) {
            showToast('Network connection error. Please check your internet connection.', 'error')
          } else if (apiError.status && apiError.status >= 500) {
            showToast('Server error. Please try again later.', 'error')
          } else if (apiError.status === 401) {
            showToast('Authentication required. Please log in again.', 'error')
          } else if (apiError.status === 403) {
            showToast('Access denied. You don\'t have permission to view this content.', 'error')
          } else if (apiError.status === 404) {
            showToast('Content not found.', 'error')
          } else {
            showToast(apiError.message || 'An unexpected error occurred.', 'error')
          }
        }
      }
    }

    try {
      await attemptFetch(1)
    } finally {
      loading.value = false
    }
  }

  // Helper function to determine if we should retry
  const shouldRetry = (error: APIError): boolean => {
    // Retry on network errors (status 0) or server errors (5xx)
    return error.status === 0 || (error.status && error.status >= 500 && error.status < 600) || false
  }

  const refresh = async () => {
    // Clear cache before refreshing
    apiCache.delete(getCacheKey())
    await fetch(true) // Skip cache check
  }

  const reset = () => {
    data.value = null
    loading.value = false
    error.value = null
    apiCache.delete(getCacheKey())
  }

  // Auto-fetch on mount if immediate is true
  if (immediate) {
    onMounted(fetch)
  }

  // Re-fetch when dependencies change
  if (dependencies.length > 0) {
    watch(dependencies, () => fetch(), { deep: true })
  }

  return {
    data: computed(() => data.value),
    loading: computed(() => loading.value),
    error: computed(() => error.value),
    fetch,
    refresh,
    reset
  }
}

// Specialized composable for paginated data
export interface UsePaginatedDataOptions<T> extends UseApiDataOptions<T> {
  pageSize?: number
  initialPage?: number
}

export interface UsePaginatedDataReturn<T> extends UseApiDataReturn<T[]> {
  currentPage: Ref<number>
  totalPages: Readonly<Ref<number>>
  totalCount: Readonly<Ref<number>>
  hasNextPage: Readonly<Ref<boolean>>
  hasPreviousPage: Readonly<Ref<boolean>>
  nextPage: () => Promise<void>
  previousPage: () => Promise<void>
  goToPage: (page: number) => Promise<void>
}

export const usePaginatedData = <T>(
  baseEndpoint: string,
  options: UsePaginatedDataOptions<T> = {}
): UsePaginatedDataReturn<T> => {
  const {
    pageSize = 20,
    initialPage = 1,
    ...apiOptions
  } = options

  const currentPage = ref(initialPage)
  const totalPages = ref(0)
  const totalCount = ref(0)

  const endpoint = computed(() => {
    const params = new URLSearchParams({
      page: currentPage.value.toString(),
      page_size: pageSize.toString()
    })
    return `${baseEndpoint}?${params.toString()}`
  })

  const transform = (data: any) => {
    if (data.results) {
      // Standard DRF pagination format
      totalCount.value = data.count || 0
      totalPages.value = Math.ceil(totalCount.value / pageSize)
      return options.transform ? options.transform(data.results) : data.results
    }
    return options.transform ? options.transform(data) : data
  }

  const apiData = useApiData<T[]>(() => endpoint.value, {
    ...apiOptions,
    transform,
    dependencies: [currentPage, ...(apiOptions.dependencies || [])],
    onSuccess: apiOptions.onSuccess as ((data: T[]) => void) | undefined
  })

  const hasNextPage = computed(() => currentPage.value < totalPages.value)
  const hasPreviousPage = computed(() => currentPage.value > 1)

  const nextPage = async () => {
    if (hasNextPage.value) {
      currentPage.value++
    }
  }

  const previousPage = async () => {
    if (hasPreviousPage.value) {
      currentPage.value--
    }
  }

  const goToPage = async (page: number) => {
    if (page >= 1 && page <= totalPages.value) {
      currentPage.value = page
    }
  }

  return {
    ...apiData,
    currentPage,
    totalPages: computed(() => totalPages.value),
    totalCount: computed(() => totalCount.value),
    hasNextPage,
    hasPreviousPage,
    nextPage,
    previousPage,
    goToPage
  }
}

// Composable for API mutations (POST, PUT, PATCH, DELETE)
export interface UseApiMutationOptions<TData, TVariables> {
  onSuccess?: (data: TData, variables: TVariables) => void
  onError?: (error: APIError, variables: TVariables) => void
  onMutate?: (variables: TVariables) => void | Promise<void>
  invalidateCache?: string[]
  optimisticUpdate?: (variables: TVariables) => TData
  rollbackOnError?: boolean
}

export interface UseApiMutationReturn<TData, TVariables> {
  mutate: (variables: TVariables) => Promise<TData>
  loading: Readonly<Ref<boolean>>
  error: Readonly<Ref<APIError | null>>
  data: Readonly<Ref<TData | null>>
  reset: () => void
}

export const useApiMutation = <TData = any, TVariables = any>(
  mutationFn: (variables: TVariables) => Promise<any> | { method: string; url: string; data?: any },
  options: UseApiMutationOptions<TData, TVariables> = {}
): UseApiMutationReturn<TData, TVariables> => {
  const loading = ref(false)
  const error = ref<APIError | null>(null)
  const data = ref<TData | null>(null)
  let previousData: TData | null = null
  
  const { showToast } = useToast()

  const mutate = async (variables: TVariables): Promise<TData> => {
    loading.value = true
    error.value = null

    // Store previous data for potential rollback
    previousData = data.value

    try {
      // Call onMutate callback (for optimistic updates)
      await options.onMutate?.(variables)

      // Apply optimistic update if provided
      if (options.optimisticUpdate) {
        data.value = options.optimisticUpdate(variables)
      }

      const mutationResult = mutationFn(variables)
      let response: any

      // Handle both Promise and config object returns
      if (mutationResult && typeof mutationResult === 'object' && 'method' in mutationResult) {
        // It's a config object, execute the API call
        const config = mutationResult as { method: string; url: string; data?: any }
        if (config.method === 'GET') {
          response = await api.get(config.url)
        } else if (config.method === 'POST') {
          response = await api.post(config.url, config.data)
        } else if (config.method === 'PUT') {
          response = await api.put(config.url, config.data)
        } else if (config.method === 'PATCH') {
          response = await api.patch(config.url, config.data)
        } else if (config.method === 'DELETE') {
          response = await api.delete(config.url)
        }
      } else {
        // It's a Promise
        response = await mutationResult
      }

      const responseData = response.data?.data || response.data
      data.value = responseData

      options.onSuccess?.(responseData, variables)

      // Invalidate cache if specified
      if (options.invalidateCache) {
        options.invalidateCache.forEach(cacheKey => {
          apiCache.delete(cacheKey)
        })
        console.log('Invalidated cache for:', options.invalidateCache)
      }

      // Show success message
      showToast('Operation completed successfully', 'success')

      return responseData
    } catch (err) {
      const apiError = err as APIError
      error.value = apiError

      // Rollback optimistic update if enabled
      if (options.rollbackOnError && previousData !== null) {
        data.value = previousData
      }

      options.onError?.(apiError, variables)

      // Show user-friendly error message
      if (apiError.status === 0) {
        showToast('Network error. Please check your connection and try again.', 'error')
      } else if (apiError.status && apiError.status >= 500) {
        showToast('Server error. Please try again later.', 'error')
      } else if (apiError.status === 401) {
        showToast('Authentication required. Please log in again.', 'error')
      } else if (apiError.status === 403) {
        showToast('Access denied. You don\'t have permission to perform this action.', 'error')
      } else if (apiError.status === 422) {
        showToast('Invalid data. Please check your input and try again.', 'error')
      } else {
        showToast(apiError.message || 'Operation failed. Please try again.', 'error')
      }

      throw apiError
    } finally {
      loading.value = false
    }
  }

  const reset = () => {
    loading.value = false
    error.value = null
    data.value = null
    previousData = null
  }

  return {
    mutate,
    loading: computed(() => loading.value),
    error: computed(() => error.value),
    data: computed(() => data.value),
    reset
  }
}