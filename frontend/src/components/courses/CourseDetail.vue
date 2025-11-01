<template>
  <div class="course-detail" v-if="course">
    <!-- Course Header -->
    <div class="course-header">
      <div class="course-header-content">
        <div class="course-info">
          <div class="course-breadcrumb">
            <router-link to="/courses" class="breadcrumb-link">Courses</router-link>
            <span class="breadcrumb-separator">›</span>
            <span class="breadcrumb-current">{{ course.title }}</span>
          </div>
          
          <h1 class="course-title">{{ course.title }}</h1>
          
          <p class="course-description">{{ course.description }}</p>
          
          <div class="course-meta">
            <div class="meta-item">
              <span class="meta-label">Instructor:</span>
              <span class="meta-value">
                {{ course.instructor.first_name }} {{ course.instructor.last_name }}
              </span>
            </div>
            
            <div class="meta-item">
              <span class="meta-label">Category:</span>
              <span class="meta-value">{{ formatCategory(course.category) }}</span>
            </div>
            
            <div class="meta-item">
              <span class="meta-label">Level:</span>
              <span class="meta-value">{{ formatDifficulty(course.difficulty_level) }}</span>
            </div>
            
            <div class="meta-item">
              <span class="meta-label">Duration:</span>
              <span class="meta-value">{{ course.duration_weeks }} weeks</span>
            </div>
          </div>
          
          <div class="course-stats">
            <div class="stat-item" v-if="course.average_rating > 0">
              <div class="rating">
                <div class="stars">
                  <span 
                    v-for="star in 5" 
                    :key="star"
                    class="star"
                    :class="{ filled: star <= Math.round(course.average_rating) }"
                  >
                    ★
                  </span>
                </div>
                <span class="rating-text">{{ course.average_rating.toFixed(1) }}</span>
              </div>
            </div>
            
            <div class="stat-item">
              <span class="stat-number">{{ course.total_enrollments }}</span>
              <span class="stat-label">students enrolled</span>
            </div>
          </div>
          
          <div class="course-tags" v-if="course.tags && course.tags.length > 0">
            <span v-for="tag in course.tags" :key="tag" class="tag">
              {{ tag }}
            </span>
          </div>
        </div>
        
        <div class="course-sidebar">
          <div class="course-image">
            <img 
              :src="course.thumbnail || '/placeholder-course.jpg'" 
              :alt="course.title"
              class="course-thumbnail"
            />
          </div>
          
          <div class="course-pricing">
            <div class="price" v-if="course.price">
              <span class="price-amount">${{ course.price }}</span>
            </div>
            <div class="price free" v-else>
              <span class="price-amount">Free</span>
            </div>
            
            <div class="enrollment-actions">
              <button 
                v-if="!isEnrolled && !isOwner"
                @click="enrollInCourse"
                class="btn btn-primary btn-large"
                :disabled="enrolling"
              >
                {{ enrolling ? 'Enrolling...' : 'Enroll Now' }}
              </button>
              
              <button 
                v-else-if="isEnrolled"
                @click="continueLearning"
                class="btn btn-secondary btn-large"
              >
                Continue Learning
              </button>
              
              <button 
                v-if="isOwner"
                @click="editCourse"
                class="btn btn-outline btn-large"
              >
                Edit Course
              </button>
            </div>
            
            <div class="course-features">
              <div class="feature">
                <i class="icon-clock"></i>
                <span>{{ course.duration_weeks }} weeks duration</span>
              </div>
              <div class="feature" v-if="course.max_students">
                <i class="icon-users"></i>
                <span>Max {{ course.max_students }} students</span>
              </div>
              <div class="feature">
                <i class="icon-certificate"></i>
                <span>Certificate of completion</span>
              </div>
              <div class="feature">
                <i class="icon-mobile"></i>
                <span>Access on mobile and desktop</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Course Content Tabs -->
    <div class="course-content">
      <div class="tabs">
        <button 
          v-for="tab in tabs" 
          :key="tab.id"
          @click="activeTab = tab.id"
          class="tab"
          :class="{ active: activeTab === tab.id }"
        >
          {{ tab.label }}
        </button>
      </div>
      
      <!-- Overview Tab -->
      <div v-if="activeTab === 'overview'" class="tab-content">
        <div class="overview-content">
          <section class="content-section">
            <h3>About This Course</h3>
            <p>{{ course.description }}</p>
          </section>
          
          <section class="content-section" v-if="modules && modules.length > 0">
            <h3>Course Curriculum</h3>
            <div class="modules-list">
              <div 
                v-for="(module, index) in modules" 
                :key="module.id"
                class="module-item"
                :class="{ published: module.is_published }"
              >
                <div class="module-header">
                  <span class="module-number">{{ index + 1 }}</span>
                  <h4 class="module-title">{{ module.title }}</h4>
                  <span v-if="!module.is_published" class="draft-badge">Draft</span>
                </div>
                <p class="module-description">{{ module.description }}</p>
              </div>
            </div>
          </section>
          
          <section class="content-section" v-if="liveClasses && liveClasses.length > 0">
            <h3>Live Classes</h3>
            <div class="live-classes-list">
              <div 
                v-for="liveClass in liveClasses" 
                :key="liveClass.id"
                class="live-class-item"
              >
                <div class="class-info">
                  <h4>{{ liveClass.title }}</h4>
                  <p>{{ liveClass.description }}</p>
                  <div class="class-meta">
                    <span class="class-date">
                      {{ formatDate(liveClass.scheduled_at) }}
                    </span>
                    <span class="class-duration">
                      {{ liveClass.duration_minutes }} minutes
                    </span>
                    <span class="class-status" :class="liveClass.status">
                      {{ formatStatus(liveClass.status) }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </section>
        </div>
      </div>
      
      <!-- Reviews Tab -->
      <div v-if="activeTab === 'reviews'" class="tab-content">
        <div class="reviews-content">
          <div class="reviews-header">
            <h3>Student Reviews</h3>
            <button 
              v-if="isEnrolled && !hasUserReview"
              @click="showReviewForm = true"
              class="btn btn-primary"
            >
              Write a Review
            </button>
          </div>
          
          <!-- Review Form -->
          <div v-if="showReviewForm" class="review-form">
            <h4>Write Your Review</h4>
            <div class="rating-input">
              <label>Rating:</label>
              <div class="stars-input">
                <button
                  v-for="star in 5"
                  :key="star"
                  @click="newReview.rating = star"
                  class="star-btn"
                  :class="{ active: star <= newReview.rating }"
                >
                  ★
                </button>
              </div>
            </div>
            <div class="comment-input">
              <label>Comment:</label>
              <textarea
                v-model="newReview.comment"
                placeholder="Share your experience with this course..."
                rows="4"
              ></textarea>
            </div>
            <div class="form-actions">
              <button @click="submitReview" class="btn btn-primary" :disabled="submittingReview">
                {{ submittingReview ? 'Submitting...' : 'Submit Review' }}
              </button>
              <button @click="cancelReview" class="btn btn-outline">
                Cancel
              </button>
            </div>
          </div>
          
          <!-- Reviews List -->
          <div class="reviews-list">
            <div 
              v-for="review in reviews" 
              :key="review.id"
              class="review-item"
              v-show="review.is_approved"
            >
              <div class="review-header">
                <div class="reviewer-info">
                  <span class="reviewer-name">
                    {{ review.student.first_name }} {{ review.student.last_name }}
                  </span>
                  <div class="review-rating">
                    <span 
                      v-for="star in 5" 
                      :key="star"
                      class="star"
                      :class="{ filled: star <= review.rating }"
                    >
                      ★
                    </span>
                  </div>
                </div>
                <span class="review-date">
                  {{ formatDate(review.created_at) }}
                </span>
              </div>
              <p class="review-comment">{{ review.comment }}</p>
            </div>
            
            <div v-if="!reviews || reviews.length === 0" class="no-reviews">
              <p>No reviews yet. Be the first to review this course!</p>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Instructor Tab -->
      <div v-if="activeTab === 'instructor'" class="tab-content">
        <div class="instructor-content">
          <div class="instructor-info">
            <h3>About the Instructor</h3>
            <div class="instructor-details">
              <h4>{{ course.instructor.first_name }} {{ course.instructor.last_name }}</h4>
              <p v-if="(course.instructor as any)?.bio">{{ (course.instructor as any).bio }}</p>
              <p v-else>Experienced instructor with expertise in {{ formatCategory(course.category) }}.</p>
              <div class="instructor-stats" v-if="instructorStats">
                <div class="stat-item">
                  <span class="stat-number">{{ instructorStats.total_courses }}</span>
                  <span class="stat-label">Courses</span>
                </div>
                <div class="stat-item">
                  <span class="stat-number">{{ instructorStats.total_students }}</span>
                  <span class="stat-label">Students</span>
                </div>
                <div class="stat-item" v-if="instructorStats.avg_rating > 0">
                  <span class="stat-number">{{ instructorStats.avg_rating.toFixed(1) }}</span>
                  <span class="stat-label">Rating</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  
  <div v-else-if="loading" class="loading-state">
    <div class="loading-spinner"></div>
    <p>Loading course details...</p>
  </div>
  
  <div v-else-if="courseError" class="error-state">
    <div class="error-icon">⚠️</div>
    <h3>Unable to load course</h3>
    <p>{{ courseError.message }}</p>
    <div class="error-actions">
      <button @click="handleRetry" class="btn btn-primary">
        Try Again
      </button>
      <router-link to="/courses" class="btn btn-outline">
        Browse Courses
      </router-link>
    </div>
  </div>
  
  <div v-else class="error-state">
    <div class="error-icon">📚</div>
    <h3>Course not found</h3>
    <p>The course you're looking for doesn't exist or has been removed.</p>
    <router-link to="/courses" class="btn btn-primary">
      Browse Courses
    </router-link>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useApiData, useApiMutation } from '../../composables/useApiData'
import { useErrorHandler } from '../../composables/useErrorHandler'
import { useAuth } from '../../composables/useAuth'
import { api } from '../../services/api'
import { CachePresets, CacheInvalidation } from '../../utils/apiCache'
import type { Course, CourseModule, CourseReview, LiveClass } from '../../types/api'

const route = useRoute()
const router = useRouter()
const { user, isAuthenticated } = useAuth()
const { handleApiError } = useErrorHandler()

// Local state
const activeTab = ref('overview')
const showReviewForm = ref(false)
const courseId = computed(() => route.params.id as string)

const newReview = ref({
  rating: 5,
  comment: ''
})

const tabs = [
  { id: 'overview', label: 'Overview' },
  { id: 'reviews', label: 'Reviews' },
  { id: 'instructor', label: 'Instructor' }
]

// Course data from centralized API
const { 
  data: course, 
  loading, 
  error: courseError,
  refresh: refreshCourse
} = useApiData<Course>(() => `/courses/${courseId.value}/`, {
  immediate: true,
  transform: (data) => data.data || data,
  ...CachePresets.courseCatalog
})

// Course modules from centralized API
const { 
  data: modules 
} = useApiData<CourseModule[]>(() => `/course-modules/?course=${courseId.value}`, {
  immediate: true,
  transform: (data) => {
    const moduleData = data.data || data
    return moduleData.results || moduleData || []
  },
  ...CachePresets.courseCatalog
})

// Course reviews from centralized API
const { 
  data: reviews,
  refresh: refreshReviews
} = useApiData<CourseReview[]>(() => `/course-reviews/?course=${courseId.value}`, {
  immediate: true,
  transform: (data) => {
    const reviewData = data.data || data
    return reviewData.results || reviewData || []
  },
  ...CachePresets.courseCatalog
})

// Live classes from centralized API
const { 
  data: liveClasses 
} = useApiData<LiveClass[]>(() => `/live-classes/?course=${courseId.value}`, {
  immediate: !!courseId.value,
  transform: (data) => {
    const classData = data.data || data
    return classData.results || classData || []
  },
  ...CachePresets.courseCatalog
})

// User enrollments for checking enrollment status
const { 
  data: enrollments, 
  refresh: refreshEnrollments 
} = useApiData<any[]>('/enrollments/', {
  immediate: isAuthenticated.value,
  transform: (data) => {
    const enrollmentData = data.data || data
    return enrollmentData.results || enrollmentData || []
  },
  ...CachePresets.userProfile
})

// Instructor statistics
const { 
  data: instructorStats 
} = useApiData<any>(() => `/users/${course.value?.instructor.id}/instructor_stats/`, {
  immediate: !!course.value?.instructor,
  transform: (data) => data.data || data,
  ...CachePresets.courseCatalog
})

// Enrollment and review mutations using centralized API
const { mutate: enrollMutation, loading: enrolling } = useApiMutation(
  (courseId: string) => api.post(`/courses/${courseId}/enroll/`),
  {
    onSuccess: () => {
      refreshEnrollments()
      CacheInvalidation.invalidateCourses()
    },
    onError: (error) => {
      handleApiError(error, { context: { action: 'enroll_in_course' } })
    }
  }
)

const { mutate: reviewMutation, loading: submittingReview } = useApiMutation(
  (reviewData: any) => api.post('/course-reviews/', reviewData),
  {
    onSuccess: () => {
      refreshReviews()
      refreshCourse() // Refresh to update average rating
      newReview.value = { rating: 5, comment: '' }
      showReviewForm.value = false
    },
    onError: (error) => {
      handleApiError(error, { context: { action: 'submit_review' } })
    }
  }
)

// Computed
const enrolledCourseIds = computed(() => 
  enrollments.value?.map(enrollment => enrollment.course?.id || enrollment.course) || []
)

const isEnrolled = computed(() => {
  if (!course.value) return false
  return enrolledCourseIds.value.includes(course.value.id)
})

const isOwner = computed(() => {
  if (!course.value || !user.value) return false
  return course.value.instructor.id === user.value.id
})

const hasUserReview = computed(() => {
  if (!user.value || !reviews.value) return false
  return reviews.value.some(review => review.student.id === user.value!.id)
})

// Methods
const enrollInCourse = async () => {
  if (!course.value) return
  
  if (!isAuthenticated.value) {
    router.push('/auth/login')
    return
  }
  
  try {
    await enrollMutation(course.value.id)
  } catch (error) {
    // Error handling is done in the mutation
  }
}

const continueLearning = () => {
  if (!course.value) return
  router.push(`/courses/${course.value.id}/learn`)
}

const editCourse = () => {
  if (!course.value) return
  router.push(`/teacher/courses/${course.value.id}/edit`)
}

const submitReview = async () => {
  if (!course.value || !newReview.value.rating) return
  
  try {
    await reviewMutation({
      course: course.value.id,
      rating: newReview.value.rating,
      comment: newReview.value.comment
    })
  } catch (error) {
    // Error handling is done in the mutation
  }
}

const cancelReview = () => {
  newReview.value = { rating: 5, comment: '' }
  showReviewForm.value = false
}

const handleRetry = async () => {
  try {
    await refreshCourse()
  } catch (error) {
    handleApiError(error as any, { context: { action: 'retry_course_load' } })
  }
}

// Utility functions
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

const formatDifficulty = (difficulty: any) => {
  if (!difficulty || typeof difficulty !== 'string') return 'Beginner'
  return difficulty.charAt(0).toUpperCase() + difficulty.slice(1)
}

const formatStatus = (status: any) => {
  if (!status || typeof status !== 'string') return 'Unknown'
  return status.charAt(0).toUpperCase() + status.slice(1)
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

// Lifecycle - data is loaded automatically by composables

// Watch for route changes - courseId computed property will trigger refresh
</script>

<style scoped>
.course-detail {
  max-width: 1200px;
  margin: 0 auto;
}

.course-header {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 50%, #92400e 100%);
  color: white;
  padding: 60px 20px;
  position: relative;
}

.course-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(254, 243, 226, 0.1) 0%, transparent 50%);
  pointer-events: none;
}

.course-header-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 40px;
  max-width: 1200px;
  margin: 0 auto;
}

.course-breadcrumb {
  margin-bottom: 16px;
  font-size: 0.875rem;
}

.breadcrumb-link {
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
}

.breadcrumb-link:hover {
  color: white;
}

.breadcrumb-separator {
  margin: 0 8px;
  color: rgba(255, 255, 255, 0.6);
}

.breadcrumb-current {
  color: white;
}

.course-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 16px;
  line-height: 1.2;
}

.course-description {
  font-size: 1.125rem;
  line-height: 1.6;
  margin-bottom: 24px;
  color: rgba(255, 255, 255, 0.9);
}

.course-meta {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.meta-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.meta-label {
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.7);
  font-weight: 500;
}

.meta-value {
  font-size: 1rem;
  font-weight: 600;
}

.course-stats {
  display: flex;
  gap: 32px;
  margin-bottom: 24px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.rating {
  display: flex;
  align-items: center;
  gap: 8px;
}

.stars {
  display: flex;
  gap: 2px;
}

.star {
  color: rgba(255, 255, 255, 0.3);
  font-size: 1.25rem;
}

.star.filled {
  color: #F59E0B;
}

.rating-text {
  font-size: 1rem;
  font-weight: 600;
}

.stat-number {
  font-size: 1.5rem;
  font-weight: 700;
}

.stat-label {
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.7);
}

.course-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.tag {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 500;
}

.course-sidebar {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(254, 243, 226, 0.3));
  border-radius: 12px;
  padding: 24px;
  height: fit-content;
  box-shadow: 0 8px 30px rgba(245, 158, 11, 0.15);
  border: 1px solid rgba(245, 158, 11, 0.2);
  backdrop-filter: blur(10px);
}

.course-image {
  margin-bottom: 24px;
}

.course-thumbnail {
  width: 100%;
  height: 200px;
  object-fit: cover;
  border-radius: 8px;
}

.course-pricing {
  text-align: center;
}

.price {
  margin-bottom: 24px;
}

.price-amount {
  font-size: 2rem;
  font-weight: 700;
  color: #111827;
}

.price.free .price-amount {
  color: #10B981;
}

.enrollment-actions {
  margin-bottom: 24px;
}

.btn {
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
  display: inline-block;
  text-align: center;
}

.btn-large {
  width: 100%;
  padding: 16px 24px;
  font-size: 1.125rem;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  box-shadow: 0 4px 15px rgba(245, 158, 11, 0.3);
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(245, 158, 11, 0.4);
}

.btn-secondary {
  background: linear-gradient(135deg, #fef3e2, #fed7aa);
  color: #92400e;
  border: 1px solid rgba(245, 158, 11, 0.3);
}

.btn-secondary:hover {
  background: linear-gradient(135deg, #fed7aa, #fdba74);
  border-color: #f59e0b;
}

.btn-outline {
  background: transparent;
  color: #6B7280;
  border: 1px solid rgba(245, 158, 11, 0.4);
}

.btn-outline:hover {
  background: linear-gradient(135deg, #fef3e2, #fed7aa);
  border-color: #f59e0b;
  color: #374151;
}

.course-features {
  text-align: left;
}

.feature {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 0;
  color: #6B7280;
  font-size: 0.875rem;
}

.course-content {
  padding: 40px 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.tabs {
  display: flex;
  border-bottom: 1px solid #E5E7EB;
  margin-bottom: 32px;
}

.tab {
  padding: 16px 24px;
  background: none;
  border: none;
  font-size: 1rem;
  font-weight: 500;
  color: #6B7280;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.2s ease;
}

.tab:hover {
  color: #374151;
}

.tab.active {
  color: #f59e0b;
  border-bottom-color: #f59e0b;
}

.tab-content {
  min-height: 400px;
}

.content-section {
  margin-bottom: 40px;
}

.content-section h3 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #111827;
  margin-bottom: 16px;
}

.modules-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.module-item {
  background: linear-gradient(135deg, #fef3e2, rgba(254, 243, 226, 0.5));
  border-radius: 8px;
  padding: 20px;
  border-left: 4px solid rgba(245, 158, 11, 0.3);
  border: 1px solid rgba(245, 158, 11, 0.1);
}

.module-item.published {
  border-left-color: #f59e0b;
  background: linear-gradient(135deg, #fed7aa, rgba(254, 215, 170, 0.5));
}

.module-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.module-number {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.875rem;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(245, 158, 11, 0.3);
}

.module-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #111827;
  flex: 1;
}

.draft-badge {
  background: #F59E0B;
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
}

.module-description {
  color: #6B7280;
  line-height: 1.5;
}

.live-classes-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.live-class-item {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(254, 243, 226, 0.3));
  border: 1px solid rgba(245, 158, 11, 0.2);
  border-radius: 8px;
  padding: 20px;
  transition: all 0.3s ease;
}

.live-class-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(245, 158, 11, 0.1);
}

.class-info h4 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #111827;
  margin-bottom: 8px;
}

.class-info p {
  color: #6B7280;
  margin-bottom: 12px;
}

.class-meta {
  display: flex;
  gap: 16px;
  font-size: 0.875rem;
}

.class-date {
  color: #374151;
  font-weight: 500;
}

.class-duration {
  color: #6B7280;
}

.class-status {
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 500;
  text-transform: capitalize;
}

.class-status.scheduled {
  background: #DBEAFE;
  color: #1D4ED8;
}

.class-status.live {
  background: #DCFCE7;
  color: #166534;
}

.class-status.completed {
  background: #F3F4F6;
  color: #374151;
}

.reviews-content {
  max-width: 800px;
}

.reviews-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.reviews-header h3 {
  margin: 0;
}

.review-form {
  background: linear-gradient(135deg, #fef3e2, rgba(254, 243, 226, 0.7));
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 32px;
  border: 1px solid rgba(245, 158, 11, 0.2);
}

.review-form h4 {
  margin-bottom: 20px;
  color: #111827;
}

.rating-input {
  margin-bottom: 16px;
}

.rating-input label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #374151;
}

.stars-input {
  display: flex;
  gap: 4px;
}

.star-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #D1D5DB;
  cursor: pointer;
  transition: color 0.2s ease;
}

.star-btn:hover,
.star-btn.active {
  color: #F59E0B;
}

.comment-input {
  margin-bottom: 20px;
}

.comment-input label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #374151;
}

.comment-input textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #D1D5DB;
  border-radius: 6px;
  font-size: 1rem;
  resize: vertical;
}

.comment-input textarea:focus {
  outline: none;
  border-color: #f59e0b;
  box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.1);
}

.form-actions {
  display: flex;
  gap: 12px;
}

.reviews-list {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.review-item {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(254, 243, 226, 0.2));
  border: 1px solid rgba(245, 158, 11, 0.1);
  border-radius: 8px;
  padding: 20px;
  transition: all 0.3s ease;
}

.review-item:hover {
  box-shadow: 0 4px 20px rgba(245, 158, 11, 0.1);
}

.review-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.reviewer-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.reviewer-name {
  font-weight: 600;
  color: #111827;
}

.review-rating .star {
  color: #D1D5DB;
  font-size: 1rem;
}

.review-rating .star.filled {
  color: #F59E0B;
}

.review-date {
  color: #6B7280;
  font-size: 0.875rem;
}

.review-comment {
  color: #374151;
  line-height: 1.6;
}

.no-reviews {
  text-align: center;
  padding: 40px;
  color: #6B7280;
}

.instructor-content {
  max-width: 600px;
}

.instructor-details h4 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
  margin-bottom: 8px;
}

.instructor-details p {
  color: #6B7280;
  line-height: 1.6;
  margin-bottom: 16px;
}

.instructor-stats {
  display: flex;
  gap: 24px;
  margin-top: 16px;
}

.instructor-stats .stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.instructor-stats .stat-number {
  font-size: 1.5rem;
  font-weight: 700;
  color: #f59e0b;
  margin-bottom: 4px;
}

.instructor-stats .stat-label {
  font-size: 0.875rem;
  color: #6B7280;
  font-weight: 500;
}

.loading-state, .error-state {
  text-align: center;
  padding: 60px 20px;
  max-width: 600px;
  margin: 0 auto;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(245, 158, 11, 0.2);
  border-top: 4px solid #f59e0b;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-state .error-icon {
  font-size: 3rem;
  margin-bottom: 16px;
}

.error-state h3 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #111827;
  margin-bottom: 8px;
}

.error-state p {
  color: #6B7280;
  margin-bottom: 24px;
}

.error-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
}

/* Responsive */
@media (max-width: 768px) {
  .course-header-content {
    grid-template-columns: 1fr;
    gap: 32px;
  }
  
  .course-title {
    font-size: 2rem;
  }
  
  .course-meta {
    grid-template-columns: 1fr;
  }
  
  .course-stats {
    flex-direction: column;
    gap: 16px;
  }
  
  .tabs {
    overflow-x: auto;
  }
  
  .tab {
    white-space: nowrap;
  }
  
  .reviews-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .form-actions {
    flex-direction: column;
  }
}
</style>