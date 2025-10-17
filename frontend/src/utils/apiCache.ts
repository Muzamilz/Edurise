// Advanced API caching utility with TTL, invalidation, and persistence

export interface CacheEntry<T = any> {
  data: T
  timestamp: number
  ttl: number
  key: string
  tags?: string[]
}

export interface CacheOptions {
  ttl?: number // Time to live in milliseconds
  tags?: string[] // Tags for group invalidation
  persist?: boolean // Whether to persist to localStorage
  transform?: (data: any) => any // Transform data before caching
}

export class ApiCache {
  private cache = new Map<string, CacheEntry>()
  private readonly defaultTTL = 300000 // 5 minutes
  private readonly maxSize = 1000 // Maximum cache entries
  private readonly storageKey = 'edurise_api_cache'

  constructor() {
    this.loadFromStorage()
    this.startCleanupInterval()
  }

  /**
   * Set data in cache with options
   */
  set<T>(key: string, data: T, options: CacheOptions = {}): void {
    const {
      ttl = this.defaultTTL,
      tags = [],
      persist = false,
      transform
    } = options

    // Transform data if transformer provided
    const processedData = transform ? transform(data) : data

    const entry: CacheEntry<T> = {
      data: processedData,
      timestamp: Date.now(),
      ttl,
      key,
      tags
    }

    // Check cache size and evict oldest entries if needed
    if (this.cache.size >= this.maxSize) {
      this.evictOldest()
    }

    this.cache.set(key, entry)

    // Persist to localStorage if requested
    if (persist) {
      this.persistEntry(key, entry)
    }

    console.log(`📦 Cached data for key: ${key} (TTL: ${ttl}ms, Tags: ${tags.join(', ')})`)
  }

  /**
   * Get data from cache
   */
  get<T>(key: string): T | null {
    const entry = this.cache.get(key)
    
    if (!entry) {
      return null
    }

    // Check if entry has expired
    if (this.isExpired(entry)) {
      this.delete(key)
      return null
    }

    console.log(`🎯 Cache hit for key: ${key}`)
    return entry.data as T
  }

  /**
   * Check if key exists and is not expired
   */
  has(key: string): boolean {
    const entry = this.cache.get(key)
    return entry ? !this.isExpired(entry) : false
  }

  /**
   * Delete specific cache entry
   */
  delete(key: string): boolean {
    const deleted = this.cache.delete(key)
    this.removeFromStorage(key)
    
    if (deleted) {
      console.log(`🗑️ Deleted cache entry: ${key}`)
    }
    
    return deleted
  }

  /**
   * Clear all cache entries
   */
  clear(): void {
    this.cache.clear()
    this.clearStorage()
    console.log('🧹 Cleared all cache entries')
  }

  /**
   * Invalidate cache entries by pattern
   */
  invalidatePattern(pattern: string): number {
    let count = 0
    const regex = new RegExp(pattern)
    
    for (const key of this.cache.keys()) {
      if (regex.test(key)) {
        this.delete(key)
        count++
      }
    }
    
    console.log(`🔄 Invalidated ${count} entries matching pattern: ${pattern}`)
    return count
  }

  /**
   * Invalidate cache entries by tags
   */
  invalidateByTags(tags: string[]): number {
    let count = 0
    
    for (const [key, entry] of this.cache.entries()) {
      if (entry.tags && entry.tags.some(tag => tags.includes(tag))) {
        this.delete(key)
        count++
      }
    }
    
    console.log(`🏷️ Invalidated ${count} entries with tags: ${tags.join(', ')}`)
    return count
  }

  /**
   * Get cache statistics
   */
  getStats(): {
    size: number
    hitRate: number
    entries: Array<{ key: string; age: number; ttl: number; tags: string[] }>
  } {
    const entries = Array.from(this.cache.entries()).map(([key, entry]) => ({
      key,
      age: Date.now() - entry.timestamp,
      ttl: entry.ttl,
      tags: entry.tags || []
    }))

    return {
      size: this.cache.size,
      hitRate: 0, // Would need to track hits/misses for accurate calculation
      entries
    }
  }

  /**
   * Prune expired entries
   */
  prune(): number {
    let count = 0
    
    for (const [key, entry] of this.cache.entries()) {
      if (this.isExpired(entry)) {
        this.delete(key)
        count++
      }
    }
    
    if (count > 0) {
      console.log(`🧽 Pruned ${count} expired cache entries`)
    }
    
    return count
  }

  /**
   * Generate cache key from URL and parameters
   */
  static generateKey(url: string, params?: Record<string, any>): string {
    const baseKey = url.replace(/^\/+|\/+$/g, '').replace(/\//g, ':')
    
    if (!params || Object.keys(params).length === 0) {
      return baseKey
    }
    
    const sortedParams = Object.keys(params)
      .sort()
      .map(key => `${key}=${JSON.stringify(params[key])}`)
      .join('&')
    
    return `${baseKey}?${sortedParams}`
  }

  /**
   * Create cache key for user-specific data
   */
  static generateUserKey(userId: string, endpoint: string, params?: Record<string, any>): string {
    const baseKey = this.generateKey(endpoint, params)
    return `user:${userId}:${baseKey}`
  }

  /**
   * Create cache key for tenant-specific data
   */
  static generateTenantKey(tenantId: string, endpoint: string, params?: Record<string, any>): string {
    const baseKey = this.generateKey(endpoint, params)
    return `tenant:${tenantId}:${baseKey}`
  }

  // Private methods

  private isExpired(entry: CacheEntry): boolean {
    return Date.now() - entry.timestamp > entry.ttl
  }

  private evictOldest(): void {
    let oldestKey = ''
    let oldestTimestamp = Date.now()
    
    for (const [key, entry] of this.cache.entries()) {
      if (entry.timestamp < oldestTimestamp) {
        oldestTimestamp = entry.timestamp
        oldestKey = key
      }
    }
    
    if (oldestKey) {
      this.delete(oldestKey)
    }
  }

  private startCleanupInterval(): void {
    // Clean up expired entries every 5 minutes
    setInterval(() => {
      this.prune()
    }, 300000)
  }

  private loadFromStorage(): void {
    try {
      const stored = localStorage.getItem(this.storageKey)
      if (stored) {
        const entries: Array<[string, CacheEntry]> = JSON.parse(stored)
        
        for (const [key, entry] of entries) {
          if (!this.isExpired(entry)) {
            this.cache.set(key, entry)
          }
        }
        
        console.log(`📥 Loaded ${this.cache.size} cache entries from storage`)
      }
    } catch (error) {
      console.warn('Failed to load cache from storage:', error)
    }
  }

  private persistEntry(key: string, entry: CacheEntry): void {
    try {
      const stored = localStorage.getItem(this.storageKey)
      const entries: Array<[string, CacheEntry]> = stored ? JSON.parse(stored) : []
      
      // Remove existing entry for this key
      const filteredEntries = entries.filter(([k]) => k !== key)
      
      // Add new entry
      filteredEntries.push([key, entry])
      
      // Keep only last 100 entries to avoid localStorage bloat
      const limitedEntries = filteredEntries.slice(-100)
      
      localStorage.setItem(this.storageKey, JSON.stringify(limitedEntries))
    } catch (error) {
      console.warn('Failed to persist cache entry:', error)
    }
  }

  private removeFromStorage(key: string): void {
    try {
      const stored = localStorage.getItem(this.storageKey)
      if (stored) {
        const entries: Array<[string, CacheEntry]> = JSON.parse(stored)
        const filteredEntries = entries.filter(([k]) => k !== key)
        localStorage.setItem(this.storageKey, JSON.stringify(filteredEntries))
      }
    } catch (error) {
      console.warn('Failed to remove cache entry from storage:', error)
    }
  }

  private clearStorage(): void {
    try {
      localStorage.removeItem(this.storageKey)
    } catch (error) {
      console.warn('Failed to clear cache storage:', error)
    }
  }
}

// Create singleton instance
export const apiCache = new ApiCache()

// Cache invalidation helpers for centralized API
export const CacheInvalidation = {
  // Invalidate all user-related data
  invalidateUser: (userId: string) => {
    return apiCache.invalidatePattern(`^user:${userId}:`)
  },

  // Invalidate all tenant-related data
  invalidateTenant: (tenantId: string) => {
    return apiCache.invalidatePattern(`^tenant:${tenantId}:`)
  },

  // Invalidate dashboard data
  invalidateDashboards: () => {
    return apiCache.invalidateByTags(['dashboard'])
  },

  // Invalidate course-related data
  invalidateCourses: () => {
    return apiCache.invalidateByTags(['courses'])
  },

  // Invalidate enrollment data
  invalidateEnrollments: () => {
    return apiCache.invalidateByTags(['enrollments'])
  },

  // Invalidate payment data
  invalidatePayments: () => {
    return apiCache.invalidateByTags(['payments'])
  },

  // Invalidate live class data
  invalidateLiveClasses: () => {
    return apiCache.invalidateByTags(['live-classes'])
  },

  // Invalidate notification data
  invalidateNotifications: () => {
    return apiCache.invalidateByTags(['notifications'])
  },

  // Invalidate user profile data
  invalidateUserProfiles: () => {
    return apiCache.invalidateByTags(['user-profiles'])
  },

  // Invalidate organization data
  invalidateOrganizations: () => {
    return apiCache.invalidateByTags(['organizations'])
  },

  // Invalidate all data for a specific centralized API endpoint
  invalidateEndpoint: (endpoint: string) => {
    const pattern = endpoint.replace(/^\/+|\/+$/g, '').replace(/\//g, ':')
    return apiCache.invalidatePattern(pattern)
  },

  // Invalidate all centralized API data
  invalidateAll: () => {
    apiCache.clear()
  },

  // Invalidate data after mutations
  invalidateAfterMutation: (_mutationType: 'create' | 'update' | 'delete', resource: string) => {
    switch (resource) {
      case 'course':
        CacheInvalidation.invalidateCourses()
        CacheInvalidation.invalidateDashboards()
        break
      case 'enrollment':
        CacheInvalidation.invalidateEnrollments()
        CacheInvalidation.invalidateCourses()
        CacheInvalidation.invalidateDashboards()
        break
      case 'payment':
        CacheInvalidation.invalidatePayments()
        CacheInvalidation.invalidateDashboards()
        break
      case 'user':
        CacheInvalidation.invalidateUserProfiles()
        CacheInvalidation.invalidateDashboards()
        break
      case 'live-class':
        CacheInvalidation.invalidateLiveClasses()
        CacheInvalidation.invalidateDashboards()
        break
      case 'notification':
        CacheInvalidation.invalidateNotifications()
        break
      default:
        console.warn(`Unknown resource type for cache invalidation: ${resource}`)
    }
  }
}

// Cache configuration presets for centralized API
export const CachePresets = {
  // Short-lived data (1 minute)
  shortLived: { ttl: 60000, tags: ['short-lived'] },
  
  // Medium-lived data (5 minutes) - default
  mediumLived: { ttl: 300000, tags: ['medium-lived'] },
  
  // Long-lived data (30 minutes)
  longLived: { ttl: 1800000, tags: ['long-lived'] },
  
  // Dashboard data (3 minutes, persisted) - frequent updates
  dashboard: { ttl: 180000, tags: ['dashboard'], persist: true },
  
  // User profile data (15 minutes, persisted)
  userProfile: { ttl: 900000, tags: ['user-profiles'], persist: true },
  
  // Course catalog (10 minutes)
  courseCatalog: { ttl: 600000, tags: ['courses', 'catalog'] },
  
  // Enrollment data (5 minutes)
  enrollmentData: { ttl: 300000, tags: ['enrollments'] },
  
  // Payment data (2 minutes) - sensitive data
  paymentData: { ttl: 120000, tags: ['payments'] },
  
  // Live class data (1 minute) - real-time updates
  liveClassData: { ttl: 60000, tags: ['live-classes'] },
  
  // Notification data (30 seconds) - real-time
  notificationData: { ttl: 30000, tags: ['notifications'] },
  
  // Organization data (1 hour) - rarely changes
  organizationData: { ttl: 3600000, tags: ['organizations'], persist: true },
  
  // Static content (1 hour)
  staticContent: { ttl: 3600000, tags: ['static'], persist: true },
  
  // Analytics data (10 minutes)
  analyticsData: { ttl: 600000, tags: ['analytics'] }
}

export default apiCache