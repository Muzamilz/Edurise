<template>
  <div class="courses-view">
    <!-- Hero Section -->
    <div class="hero-section">
      <div class="hero-content">
        <h1 class="hero-title">Discover Amazing Courses</h1>
        <p class="hero-subtitle">
          Learn new skills from expert instructors and advance your career
        </p>
        <div class="hero-search">
          <div class="search-container">
            <input
              v-model="searchQuery"
              @keydown.enter="performSearch"
              @input="handleSearchInput"
              type="text"
              placeholder="Search courses, instructors, or topics..."
              class="search-input"
            />
            <button @click="performSearch" class="search-btn" :disabled="!searchQuery.trim()">
              <span v-if="!searchLoading">🔍</span>
              <span v-else class="search-spinner">⏳</span>
              Search
            </button>
          </div>
          <div class="search-suggestions" v-if="searchSuggestions.length > 0">
            <div 
              v-for="suggestion in searchSuggestions" 
              :key="suggestion"
              @click="selectSuggestion(suggestion)"
              class="suggestion-item"
            >
              {{ suggestion }}
            </div>
          </div>
        </div>
        
        <!-- Quick Stats -->
        <div class="hero-stats">
          <div class="stat-item">
            <span class="stat-number">{{ totalCourses }}+</span>
            <span class="stat-label">Courses</span>
          </div>
          <div class="stat-item">
            <span class="stat-number">{{ totalInstructors }}+</span>
            <span class="stat-label">Instructors</span>
          </div>
          <div class="stat-item">
            <span class="stat-number">{{ totalStudents }}+</span>
            <span class="stat-label">Students</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Featured Courses -->
    <section class="featured-section">
      <div class="container">
        <h2 class="section-title">Featured Courses</h2>
        
        <!-- Loading State -->
        <div v-if="featuredLoading" class="loading-state">
          <div class="loading-spinner"></div>
          <p>Loading featured courses...</p>
        </div>
        
        <!-- Error State -->
        <div v-else-if="featuredError" class="error-state">
          <div class="error-icon">⚠️</div>
          <h3>Unable to load featured courses</h3>
          <p>{{ featuredError.message }}</p>
          <button @click="handleRetryFeatured" class="retry-btn">
            Try Again
          </button>
        </div>
        
        <!-- Featured Courses Grid -->
        <div v-else-if="featuredCourses && featuredCourses.length > 0" class="featured-grid">
          <CourseCard
            v-for="course in featuredCourses"
            :key="course.id"
            :course="course"
            :is-enrolled="isEnrolledInCourse(course.id)"
            @click="goToCourse"
            @enroll="handleEnroll"
            @continue="handleContinue"
          />
        </div>
        
        <!-- Empty State -->
        <div v-else class="empty-state">
          <div class="empty-icon">📚</div>
          <h3>No featured courses available</h3>
          <p>Check back later for featured content</p>
        </div>
      </div>
    </section>

    <!-- Categories -->
    <section class="categories-section">
      <div class="container">
        <h2 class="section-title">Browse by Category</h2>
        
        <!-- Loading State -->
        <div v-if="categoriesLoading" class="loading-state">
          <div class="loading-spinner"></div>
          <p>Loading categories...</p>
        </div>
        
        <!-- Error State -->
        <div v-else-if="categoriesError" class="error-state">
          <div class="error-icon">⚠️</div>
          <h3>Unable to load categories</h3>
          <p>{{ categoriesError.message }}</p>
        </div>
        
        <!-- Categories Grid -->
        <div v-else-if="categories && categories.length > 0" class="categories-grid">
          <div
            v-for="category in categories"
            :key="category.category"
            @click="filterByCategory(category.category)"
            class="category-card"
          >
            <div class="category-icon">
              {{ getCategoryIcon(category.category) }}
            </div>
            <h3 class="category-name">{{ formatCategory(category.category) }}</h3>
            <p class="category-stats">
              {{ category.count }} courses
              <span v-if="category.avg_rating > 0">
                • {{ category.avg_rating.toFixed(1) }}★
              </span>
            </p>
          </div>
        </div>
        
        <!-- Empty State -->
        <div v-else class="empty-state">
          <div class="empty-icon">📂</div>
          <h3>No categories available</h3>
          <p>Categories will appear as courses are added</p>
        </div>
      </div>
    </section>

    <!-- Filters and All Courses -->
    <section class="courses-section">
      <div class="container">
        <div class="section-header">
          <h2 class="section-title">
            All Courses
            <span v-if="filteredCoursesCount > 0" class="course-count">({{ filteredCoursesCount }})</span>
          </h2>
          <div class="header-controls">
            <div class="view-toggle">
              <button
                @click="viewMode = 'grid'"
                class="toggle-btn"
                :class="{ active: viewMode === 'grid' }"
                title="Grid View"
              >
                📊
              </button>
              <button
                @click="viewMode = 'list'"
                class="toggle-btn"
                :class="{ active: viewMode === 'list' }"
                title="List View"
              >
                📋
              </button>
            </div>
          </div>
        </div>

        <!-- Advanced Filters -->
        <div class="filters-section">
          <div class="filters-row">
            <div class="filter-group">
              <label>Category</label>
              <select v-model="selectedCategory" @change="applyFilters" class="filter-select">
                <option value="">All Categories</option>
                <option v-for="category in categories" :key="category.category" :value="category.category">
                  {{ formatCategory(category.category) }} ({{ category.count }})
                </option>
              </select>
            </div>
            
            <div class="filter-group">
              <label>Price</label>
              <select v-model="selectedPriceRange" @change="applyFilters" class="filter-select">
                <option value="">Any Price</option>
                <option value="free">Free</option>
                <option value="0-50">$0 - $50</option>
                <option value="50-100">$50 - $100</option>
                <option value="100-200">$100 - $200</option>
                <option value="200+">$200+</option>
              </select>
            </div>
            
            <div class="filter-group">
              <label>Difficulty</label>
              <select v-model="selectedDifficulty" @change="applyFilters" class="filter-select">
                <option value="">Any Level</option>
                <option value="beginner">Beginner</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
              </select>
            </div>
            
            <div class="filter-group">
              <label>Duration</label>
              <select v-model="selectedDuration" @change="applyFilters" class="filter-select">
                <option value="">Any Duration</option>
                <option value="1-4">1-4 weeks</option>
                <option value="5-8">5-8 weeks</option>
                <option value="9-12">9-12 weeks</option>
                <option value="12+">12+ weeks</option>
              </select>
            </div>
            
            <div class="filter-group">
              <label>Sort By</label>
              <select v-model="sortBy" @change="applyFilters" class="filter-select">
                <option value="newest">Newest First</option>
                <option value="oldest">Oldest First</option>
                <option value="price-low">Price: Low to High</option>
                <option value="price-high">Price: High to Low</option>
                <option value="rating">Highest Rated</option>
                <option value="popular">Most Popular</option>
              </select>
            </div>
            
            <button @click="clearFilters" class="clear-filters-btn" v-if="hasActiveFilters">
              Clear Filters
            </button>
          </div>
        </div>

        <!-- Course Grid/List -->
        <div class="courses-container">
          <!-- Loading State -->
          <div v-if="coursesLoading" class="loading-state">
            <div class="loading-spinner"></div>
            <p>Loading courses...</p>
          </div>
          
          <!-- Error State -->
          <div v-else-if="coursesError" class="error-state">
            <div class="error-icon">⚠️</div>
            <h3>Unable to load courses</h3>
            <p>{{ coursesError.message }}</p>
            <button @click="handleRetryCourses" class="retry-btn">Try Again</button>
          </div>
          
          <!-- Courses Grid -->
          <div v-else-if="filteredCourses && filteredCourses.length > 0" 
               class="courses-grid" 
               :class="{ 'list-view': viewMode === 'list' }">
            <CourseCard
              v-for="course in paginatedCourses"
              :key="course.id"
              :course="course"
              :is-enrolled="isEnrolledInCourse(course.id)"
              :show-enroll-button="true"
              :loading="enrollingCourseId === course.id"
              @click="goToCourse"
              @enroll="handleEnroll"
              @continue="handleContinue"
              class="course-item"
            />
          </div>
          
          <!-- Empty State -->
          <div v-else class="empty-state">
            <div class="empty-icon">🔍</div>
            <h3>No courses found</h3>
            <p v-if="hasActiveFilters">Try adjusting your filters or search terms</p>
            <p v-else>No courses are currently available</p>
            <button v-if="hasActiveFilters" @click="clearFilters" class="clear-filters-btn">
              Clear All Filters
            </button>
          </div>
          
          <!-- Pagination -->
          <div v-if="totalPages > 1" class="pagination">
            <button 
              @click="currentPage--" 
              :disabled="currentPage === 1"
              class="pagination-btn"
            >
              ← Previous
            </button>
            
            <div class="pagination-numbers">
              <button
                v-for="page in visiblePages"
                :key="page"
                @click="currentPage = typeof page === 'number' ? page : parseInt(page.toString())"
                class="pagination-number"
                :class="{ active: page === currentPage }"
              >
                {{ page }}
              </button>
            </div>
            
            <button 
              @click="currentPage++" 
              :disabled="currentPage === totalPages"
              class="pagination-btn"
            >
              Next →
            </button>
          </div>
        </div>
      </div>
    </section>
    
    <!-- Payment Modal -->
    <PaymentModal
      v-if="selectedCourse && selectedCourse.price !== undefined"
      :show="showPaymentModal"
      :course="{
        id: selectedCourse.id,
        title: selectedCourse.title,
        price: selectedCourse.price || 0,
        thumbnail: selectedCourse.thumbnail,
        instructor: {
          first_name: selectedCourse.instructor.first_name,
          last_name: selectedCourse.instructor.last_name
        }
      }"
      @close="handlePaymentClose"
      @success="handlePaymentSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import CourseCard from '../../components/courses/CourseCard.vue'
import PaymentModal from '../../components/payments/PaymentModal.vue'
import { useApiData } from '../../composables/useApiData'
import { useErrorHandler } from '../../composables/useErrorHandler'
import { useAuth } from '../../composables/useAuth'
import { useEnrollment } from '../../composables/useEnrollment'
import { CachePresets } from '../../utils/apiCache'
import type { Course } from '../../types/api'

const router = useRouter()
const route = useRoute()
const { isAuthenticated } = useAuth()
const { handleApiError } = useErrorHandler()
const { enrollInCourse, isEnrolledInCourse } = useEnrollment()

// Local state
const searchQuery = ref('')
const searchLoading = ref(false)
const searchSuggestions = ref<string[]>([])
const viewMode = ref<'grid' | 'list'>('grid')
const showPaymentModal = ref(false)
const selectedCourse = ref<Course | null>(null)
const enrollingCourseId = ref<string | null>(null)

// Filter state
const selectedCategory = ref('')
const selectedPriceRange = ref('')
const selectedDifficulty = ref('')
const selectedDuration = ref('')
const sortBy = ref('newest')

// Pagination state
const currentPage = ref(1)
const itemsPerPage = ref(12)

// All courses from centralized API
const { 
  data: allCourses, 
  loading: coursesLoading, 
  error: coursesError,
  refresh: refreshCourses
} = useApiData<Course[]>('/courses/', {
  ...CachePresets.courseCatalog,
  transform: (data) => {
    // Handle both direct array and response with data property
    const courses = data.results || data.data || data
    return Array.isArray(courses) ? courses : []
  }
})

// Featured courses from centralized API
const { 
  data: featuredCourses, 
  loading: featuredLoading, 
  error: featuredError,
  refresh: refreshFeatured
} = useApiData<Course[]>('/courses/featured/', {
  ...CachePresets.courseCatalog,
  transform: (data) => {
    // Handle both direct array and response with data property
    const courses = data.data || data
    return Array.isArray(courses) ? courses.slice(0, 6) : []
  }
})

// Course categories from centralized API
const { 
  data: categories, 
  loading: categoriesLoading, 
  error: categoriesError 
} = useApiData<Array<{ category: string; count: number; avg_rating: number }>>('/courses/categories/', {
  ...CachePresets.courseCatalog,
  transform: (data) => {
    // Handle both direct array and response with data property
    const categoryData = data.data || data
    return Array.isArray(categoryData) ? categoryData : []
  }
})

// Platform stats
const { data: platformStats } = useApiData('/courses/stats/', {
  ...CachePresets.courseCatalog,
  transform: (data) => data.data || data
})

// Computed properties
const totalCourses = computed(() => platformStats.value?.total_courses || allCourses.value?.length || 0)
const totalInstructors = computed(() => platformStats.value?.total_instructors || 0)
const totalStudents = computed(() => platformStats.value?.total_students || 0)

const filteredCourses = computed(() => {
  if (!allCourses.value) return []
  
  let filtered = [...allCourses.value]
  
  // Apply search filter
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(course => 
      course.title.toLowerCase().includes(query) ||
      course.description.toLowerCase().includes(query) ||
      (course.instructor?.first_name + ' ' + course.instructor?.last_name).toLowerCase().includes(query) ||
      course.category?.toLowerCase().includes(query) ||
      course.tags?.some(tag => tag.toLowerCase().includes(query))
    )
  }
  
  // Apply category filter
  if (selectedCategory.value) {
    filtered = filtered.filter(course => course.category === selectedCategory.value)
  }
  
  // Apply price filter
  if (selectedPriceRange.value) {
    filtered = filtered.filter(course => {
      const price = course.price || 0
      switch (selectedPriceRange.value) {
        case 'free': return price === 0
        case '0-50': return price > 0 && price <= 50
        case '50-100': return price > 50 && price <= 100
        case '100-200': return price > 100 && price <= 200
        case '200+': return price > 200
        default: return true
      }
    })
  }
  
  // Apply difficulty filter
  if (selectedDifficulty.value) {
    filtered = filtered.filter(course => course.difficulty_level === selectedDifficulty.value)
  }
  
  // Apply duration filter
  if (selectedDuration.value) {
    filtered = filtered.filter(course => {
      const weeks = course.duration_weeks || 0
      switch (selectedDuration.value) {
        case '1-4': return weeks >= 1 && weeks <= 4
        case '5-8': return weeks >= 5 && weeks <= 8
        case '9-12': return weeks >= 9 && weeks <= 12
        case '12+': return weeks > 12
        default: return true
      }
    })
  }
  
  // Apply sorting
  switch (sortBy.value) {
    case 'newest':
      filtered.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
      break
    case 'oldest':
      filtered.sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime())
      break
    case 'price-low':
      filtered.sort((a, b) => (a.price || 0) - (b.price || 0))
      break
    case 'price-high':
      filtered.sort((a, b) => (b.price || 0) - (a.price || 0))
      break
    case 'rating':
      filtered.sort((a, b) => (b.average_rating || 0) - (a.average_rating || 0))
      break
    case 'popular':
      filtered.sort((a, b) => (b.total_enrollments || 0) - (a.total_enrollments || 0))
      break
  }
  
  return filtered
})

const filteredCoursesCount = computed(() => filteredCourses.value.length)

const totalPages = computed(() => Math.ceil(filteredCoursesCount.value / itemsPerPage.value))

const paginatedCourses = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value
  const end = start + itemsPerPage.value
  return filteredCourses.value.slice(start, end)
})

const visiblePages = computed(() => {
  const pages = []
  const total = totalPages.value
  const current = currentPage.value
  
  if (total <= 7) {
    for (let i = 1; i <= total; i++) {
      pages.push(i)
    }
  } else {
    if (current <= 4) {
      for (let i = 1; i <= 5; i++) pages.push(i)
      pages.push('...', total)
    } else if (current >= total - 3) {
      pages.push(1, '...')
      for (let i = total - 4; i <= total; i++) pages.push(i)
    } else {
      pages.push(1, '...')
      for (let i = current - 1; i <= current + 1; i++) pages.push(i)
      pages.push('...', total)
    }
  }
  
  return pages
})

const hasActiveFilters = computed(() => 
  selectedCategory.value || 
  selectedPriceRange.value || 
  selectedDifficulty.value || 
  selectedDuration.value ||
  searchQuery.value.trim()
)

// Methods
const performSearch = () => {
  applyFilters()
  updateURL()
}

const handleSearchInput = () => {
  // Generate search suggestions (mock implementation)
  if (searchQuery.value.length > 2) {
    const suggestions = [
      'Web Development',
      'JavaScript',
      'Python',
      'Data Science',
      'Machine Learning',
      'UI/UX Design'
    ].filter(s => s.toLowerCase().includes(searchQuery.value.toLowerCase()))
    searchSuggestions.value = suggestions.slice(0, 5)
  } else {
    searchSuggestions.value = []
  }
}

const selectSuggestion = (suggestion: string) => {
  searchQuery.value = suggestion
  searchSuggestions.value = []
  performSearch()
}

const filterByCategory = (category: string) => {
  selectedCategory.value = category
  applyFilters()
  updateURL()
}

const applyFilters = () => {
  currentPage.value = 1 // Reset to first page when filters change
}

const clearFilters = () => {
  searchQuery.value = ''
  selectedCategory.value = ''
  selectedPriceRange.value = ''
  selectedDifficulty.value = ''
  selectedDuration.value = ''
  sortBy.value = 'newest'
  currentPage.value = 1
  searchSuggestions.value = []
  updateURL()
}

const updateURL = () => {
  const query: any = {}
  if (searchQuery.value.trim()) query.search = searchQuery.value.trim()
  if (selectedCategory.value) query.category = selectedCategory.value
  if (selectedPriceRange.value) query.price = selectedPriceRange.value
  if (selectedDifficulty.value) query.difficulty = selectedDifficulty.value
  if (selectedDuration.value) query.duration = selectedDuration.value
  if (sortBy.value !== 'newest') query.sort = sortBy.value
  if (currentPage.value > 1) query.page = currentPage.value
  
  router.replace({ query })
}

const loadFromURL = () => {
  const query = route.query
  searchQuery.value = (query.search as string) || ''
  selectedCategory.value = (query.category as string) || ''
  selectedPriceRange.value = (query.price as string) || ''
  selectedDifficulty.value = (query.difficulty as string) || ''
  selectedDuration.value = (query.duration as string) || ''
  sortBy.value = (query.sort as string) || 'newest'
  currentPage.value = parseInt((query.page as string) || '1')
}

const goToCourse = (course: Course) => {
  router.push(`/courses/${course.id}`)
}

const handleEnroll = async (course: Course) => {
  if (!isAuthenticated.value) {
    router.push('/auth/login')
    return
  }

  try {
    enrollingCourseId.value = course.id
    
    // If course is free, enroll directly
    if (!course.price || course.price === 0) {
      await enrollInCourse(course.id, course)
      router.push(`/courses/${course.id}`)
    } else {
      // For paid courses, show payment modal
      selectedCourse.value = course
      showPaymentModal.value = true
    }
  } catch (error) {
    handleApiError(error as any, {
      context: { action: 'enroll_in_course', courseId: course.id }
    })
  } finally {
    enrollingCourseId.value = null
  }
}

const handleContinue = (course: Course) => {
  router.push(`/courses/${course.id}/learn`)
}

const formatCategory = (category: any) => {
  if (!category) return 'General'
  
  // If category is an object with a name property
  if (typeof category === 'object' && category.name) {
    return category.name.charAt(0).toUpperCase() + category.name.slice(1).replace('_', ' ')
  }
  
  // If category is a string
  if (typeof category === 'string') {
    return category.charAt(0).toUpperCase() + category.slice(1).replace('_', ' ')
  }
  
  // Fallback
  return 'General'
}

const getCategoryIcon = (category: string) => {
  const icons: Record<string, string> = {
    technology: '💻',
    business: '💼',
    design: '🎨',
    marketing: '📈',
    language: '🗣️',
    science: '🔬',
    other: '📚'
  }
  return icons[category] || '📚'
}

// Payment modal handlers
const handlePaymentSuccess = () => {
  showPaymentModal.value = false
  if (selectedCourse.value) {
    router.push(`/courses/${selectedCourse.value.id}`)
  }
  selectedCourse.value = null
}

const handlePaymentClose = () => {
  showPaymentModal.value = false
  selectedCourse.value = null
}

// Error handling
const handleRetryFeatured = async () => {
  try {
    await refreshFeatured()
  } catch (error) {
    handleApiError(error as any, { context: { action: 'retry_featured_courses' } })
  }
}

const handleRetryCourses = async () => {
  try {
    await refreshCourses()
  } catch (error) {
    handleApiError(error as any, { context: { action: 'retry_courses' } })
  }
}

// Watchers
watch(() => route.query, () => {
  loadFromURL()
}, { immediate: true })

watch([selectedCategory, selectedPriceRange, selectedDifficulty, selectedDuration, sortBy], () => {
  updateURL()
})

watch(currentPage, () => {
  updateURL()
  // Scroll to top when page changes
  window.scrollTo({ top: 0, behavior: 'smooth' })
})

// Lifecycle
onMounted(() => {
  loadFromURL()
})
</script>

<style scoped>
.courses-view {
  min-height: 100vh;
}

.hero-section {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 50%, #92400e 100%);
  color: white;
  padding: 80px 20px;
  text-align: center;
  position: relative;
}

.hero-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(254, 243, 226, 0.1) 0%, transparent 50%);
  pointer-events: none;
}

.hero-content {
  max-width: 800px;
  margin: 0 auto;
}

.hero-title {
  font-size: 3rem;
  font-weight: 700;
  margin-bottom: 16px;
  line-height: 1.2;
}

.hero-subtitle {
  font-size: 1.25rem;
  margin-bottom: 40px;
  color: rgba(255, 255, 255, 0.9);
  line-height: 1.5;
}

.hero-search {
  max-width: 600px;
  margin: 0 auto 40px auto;
  position: relative;
}

.search-container {
  display: flex;
  gap: 12px;
  position: relative;
}

.search-input {
  flex: 1;
  padding: 16px 20px;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  outline: none;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.search-input:focus {
  box-shadow: 0 8px 30px rgba(245, 158, 11, 0.3);
  transform: translateY(-2px);
}

.search-input::placeholder {
  color: #9CA3AF;
}

.search-btn {
  padding: 16px 32px;
  background: linear-gradient(135deg, #fed7aa, #fdba74);
  color: #92400e;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(254, 215, 170, 0.4);
  display: flex;
  align-items: center;
  gap: 8px;
}

.search-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #fdba74, #fb923c);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(254, 215, 170, 0.6);
}

.search-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.search-spinner {
  animation: spin 1s linear infinite;
}

.search-suggestions {
  position: absolute;
  top: 100%;
  left: 0;
  right: 80px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
  z-index: 10;
  margin-top: 4px;
}

.suggestion-item {
  padding: 12px 16px;
  cursor: pointer;
  border-bottom: 1px solid #f3f4f6;
  transition: background-color 0.2s ease;
}

.suggestion-item:hover {
  background: #fef3e2;
}

.suggestion-item:last-child {
  border-bottom: none;
}

.hero-stats {
  display: flex;
  justify-content: center;
  gap: 40px;
  margin-top: 40px;
}

.stat-item {
  text-align: center;
}

.stat-number {
  display: block;
  font-size: 2rem;
  font-weight: 700;
  color: white;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.8);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.featured-section,
.categories-section,
.courses-section {
  padding: 60px 0;
}

.categories-section {
  background: linear-gradient(135deg, #fef3e2 0%, #ffffff 50%, #f0f9ff 100%);
}

.section-title {
  font-size: 2rem;
  font-weight: 700;
  color: #111827;
  margin-bottom: 40px;
  text-align: center;
}

.featured-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 24px;
}

.categories-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.category-card {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(254, 243, 226, 0.3));
  border-radius: 12px;
  padding: 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 20px rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.1);
}

.category-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 12px 35px rgba(245, 158, 11, 0.2);
  background: linear-gradient(135deg, rgba(254, 243, 226, 0.8), rgba(254, 215, 170, 0.4));
}

.category-icon {
  font-size: 3rem;
  margin-bottom: 16px;
}

.category-name {
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
  margin-bottom: 8px;
}

.category-stats {
  color: #6B7280;
  font-size: 0.875rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.section-header .section-title {
  margin: 0;
  text-align: left;
  display: flex;
  align-items: center;
  gap: 12px;
}

.course-count {
  font-size: 1rem;
  font-weight: 400;
  color: #6b7280;
}

.header-controls {
  display: flex;
  align-items: center;
  gap: 16px;
}

.view-toggle {
  display: flex;
  background: rgba(254, 243, 226, 0.5);
  border-radius: 8px;
  padding: 4px;
  border: 1px solid rgba(245, 158, 11, 0.2);
}

.toggle-btn {
  padding: 8px 12px;
  background: none;
  border: none;
  border-radius: 6px;
  font-size: 1.2rem;
  color: #6B7280;
  cursor: pointer;
  transition: all 0.2s ease;
}

.toggle-btn.active {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  box-shadow: 0 2px 8px rgba(245, 158, 11, 0.3);
}

.filters-section {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(254, 243, 226, 0.3));
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 32px;
  box-shadow: 0 4px 20px rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.1);
}

.filters-row {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  align-items: end;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 150px;
}

.filter-group label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
}

.filter-select {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 0.875rem;
  background: white;
  cursor: pointer;
  transition: all 0.2s ease;
}

.filter-select:focus {
  outline: none;
  border-color: #f59e0b;
  box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.1);
}

.clear-filters-btn {
  padding: 8px 16px;
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px rgba(239, 68, 68, 0.3);
}

.clear-filters-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 15px rgba(239, 68, 68, 0.4);
}

.courses-container {
  min-height: 400px;
}

.courses-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
  margin-bottom: 40px;
}

.courses-grid.list-view {
  grid-template-columns: 1fr;
  gap: 16px;
}

.courses-grid.list-view .course-item {
  max-width: none;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  margin-top: 40px;
}

.pagination-btn {
  padding: 8px 16px;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  color: #374151;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.875rem;
}

.pagination-btn:hover:not(:disabled) {
  background: #f9fafb;
  border-color: #f59e0b;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-numbers {
  display: flex;
  gap: 4px;
}

.pagination-number {
  padding: 8px 12px;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  color: #374151;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.875rem;
  min-width: 40px;
  text-align: center;
}

.pagination-number:hover {
  background: #f9fafb;
  border-color: #f59e0b;
}

.pagination-number.active {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  border-color: #f59e0b;
}

/* Loading and Error States */
.loading-state, .error-state, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 2rem;
  text-align: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f4f6;
  border-top: 4px solid #f59e0b;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-state p {
  color: #6b7280;
  font-size: 1rem;
  margin: 0;
}

.error-state .error-icon, .empty-state .empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.error-state h3, .empty-state h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.error-state p, .empty-state p {
  color: #6b7280;
  margin-bottom: 1.5rem;
  max-width: 400px;
}

.retry-btn {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(245, 158, 11, 0.3);
}

.retry-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(245, 158, 11, 0.4);
}

.retry-btn:active {
  transform: translateY(0);
}

/* Responsive */
@media (max-width: 768px) {
  .hero-title {
    font-size: 2rem;
  }
  
  .hero-subtitle {
    font-size: 1rem;
  }
  
  .search-container {
    flex-direction: column;
    gap: 12px;
  }
  
  .search-btn {
    padding: 16px;
  }
  
  .hero-stats {
    gap: 20px;
  }
  
  .stat-number {
    font-size: 1.5rem;
  }
  
  .featured-section,
  .categories-section,
  .courses-section {
    padding: 40px 0;
  }
  
  .section-title {
    font-size: 1.5rem;
    margin-bottom: 24px;
  }
  
  .featured-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .categories-grid {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 16px;
  }
  
  .category-card {
    padding: 20px;
  }
  
  .category-icon {
    font-size: 2rem;
    margin-bottom: 12px;
  }
  
  .section-header {
    flex-direction: column;
    gap: 20px;
    align-items: stretch;
  }
  
  .section-header .section-title {
    text-align: center;
  }
  
  .header-controls {
    justify-content: center;
  }
  
  .filters-section {
    padding: 16px;
  }
  
  .filters-row {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-group {
    min-width: auto;
  }
  
  .courses-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .pagination {
    flex-wrap: wrap;
    gap: 4px;
  }
  
  .pagination-numbers {
    order: -1;
    width: 100%;
    justify-content: center;
    margin-bottom: 12px;
  }
}

@media (max-width: 480px) {
  .hero-section {
    padding: 60px 20px;
  }
  
  .hero-stats {
    flex-direction: column;
    gap: 16px;
  }
  
  .categories-grid {
    grid-template-columns: 1fr 1fr;
  }
  
  .filters-row {
    gap: 12px;
  }
  
  .pagination-numbers {
    gap: 2px;
  }
  
  .pagination-number {
    padding: 6px 8px;
    min-width: 32px;
    font-size: 0.75rem;
  }
}
</style>