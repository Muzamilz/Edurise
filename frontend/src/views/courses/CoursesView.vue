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
          <input
            v-model="searchQuery"
            @keydown.enter="performSearch"
            type="text"
            placeholder="What do you want to learn?"
            class="search-input"
          />
          <button @click="performSearch" class="search-btn">
            Search
          </button>
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

    <!-- All Courses -->
    <section class="courses-section">
      <div class="container">
        <div class="section-header">
          <h2 class="section-title">All Courses</h2>
          <div class="view-toggle">
            <button
              @click="viewMode = 'grid'"
              class="toggle-btn"
              :class="{ active: viewMode === 'grid' }"
            >
              Grid
            </button>
            <button
              @click="viewMode = 'list'"
              class="toggle-btn"
              :class="{ active: viewMode === 'list' }"
            >
              List
            </button>
          </div>
        </div>

        <CourseList
          :use-marketplace="true"
          :show-enroll-button="true"
          @course-click="goToCourse"
          @enroll="handleEnroll"
          @continue="handleContinue"
        />
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
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import CourseCard from '../../components/courses/CourseCard.vue'
import CourseList from '../../components/courses/CourseList.vue'
import PaymentModal from '../../components/payments/PaymentModal.vue'
import { useApiData } from '../../composables/useApiData'
import { useErrorHandler } from '../../composables/useErrorHandler'
import { useAuth } from '../../composables/useAuth'
import { useEnrollment } from '../../composables/useEnrollment'
import { CachePresets } from '../../utils/apiCache'
import type { Course } from '../../types/api'

const router = useRouter()
const { isAuthenticated } = useAuth()
const { handleApiError } = useErrorHandler()
const { enrollInCourse, isEnrolledInCourse } = useEnrollment()

// Local state
const searchQuery = ref('')
const viewMode = ref<'grid' | 'list'>('grid')
const showPaymentModal = ref(false)
const selectedCourse = ref<Course | null>(null)

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

// Computed - enrollment status is handled by useEnrollment composable

// Methods
const performSearch = () => {
  if (searchQuery.value.trim()) {
    router.push({
      name: 'courses',
      query: { search: searchQuery.value.trim() }
    })
  }
}

const filterByCategory = (category: string) => {
  router.push({
    name: 'courses',
    query: { category }
  })
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
  }
}

const handleContinue = (course: Course) => {
  router.push(`/courses/${course.id}/learn`)
}

const formatCategory = (category: string) => {
  return category.charAt(0).toUpperCase() + category.slice(1).replace('_', ' ')
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

// Error handling for featured courses and categories
const handleRetryFeatured = async () => {
  try {
    await refreshFeatured()
  } catch (error) {
    handleApiError(error as any, { context: { action: 'retry_featured_courses' } })
  }
}

// Lifecycle - data is loaded automatically by composables
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
  display: flex;
  max-width: 500px;
  margin: 0 auto;
  gap: 12px;
}

.search-input {
  flex: 1;
  padding: 16px 20px;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  outline: none;
}

.search-input::placeholder {
  color: #9CA3AF;
}

.search-btn {
  padding: 16px 32px;
  background: linear-gradient(135deg, #fed7aa, #fdba74);
  color: #92400e;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(254, 215, 170, 0.4);
}

.search-btn:hover {
  background: linear-gradient(135deg, #fdba74, #fb923c);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(254, 215, 170, 0.6);
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
  margin-bottom: 40px;
}

.section-header .section-title {
  margin: 0;
  text-align: left;
}

.view-toggle {
  display: flex;
  background: rgba(254, 243, 226, 0.5);
  border-radius: 8px;
  padding: 4px;
  border: 1px solid rgba(245, 158, 11, 0.2);
}

.toggle-btn {
  padding: 8px 16px;
  background: none;
  border: none;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  color: #6B7280;
  cursor: pointer;
  transition: all 0.2s ease;
}

.toggle-btn.active {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  box-shadow: 0 2px 8px rgba(245, 158, 11, 0.3);
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
  
  .hero-search {
    flex-direction: column;
    max-width: 100%;
  }
  
  .search-btn {
    padding: 16px;
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
  
  .view-toggle {
    align-self: center;
  }
}

@media (max-width: 480px) {
  .hero-section {
    padding: 60px 20px;
  }
  
  .categories-grid {
    grid-template-columns: 1fr 1fr;
  }
}
</style>