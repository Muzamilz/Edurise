<template>
  <div class="wishlist-view">
    <div class="page-header">
      <h1>My Wishlist</h1>
      <p>Courses you've saved for later</p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>Loading your wishlist...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-state">
      <div class="error-icon">⚠️</div>
      <h3>Failed to load wishlist</h3>
      <p>{{ error.message }}</p>
      <button @click="handleRetry" class="retry-btn">Try Again</button>
    </div>

    <!-- Wishlist Content -->
    <div v-else class="wishlist-content">
      <!-- Wishlist Stats -->
      <div class="wishlist-stats">
        <div class="stat-card">
          <div class="stat-icon">❤️</div>
          <h3>Saved Courses</h3>
          <p class="stat-number">{{ totalItems }}</p>
        </div>
        <div class="stat-card">
          <div class="stat-icon">💰</div>
          <h3>Total Value</h3>
          <p class="stat-number">${{ totalValue.toFixed(2) }}</p>
        </div>
        <div class="stat-card">
          <div class="stat-icon">⏰</div>
          <h3>Available Courses</h3>
          <p class="stat-number">{{ availableCourses.length }}</p>
        </div>
      </div>

      <!-- Bulk Actions -->
      <div v-if="wishlistItems.length > 0" class="bulk-actions">
        <div class="selection-info">
          <label class="select-all">
            <input 
              type="checkbox" 
              :checked="selectedCourses.length === availableCourses.length && availableCourses.length > 0"
              @change="toggleSelectAll"
            />
            Select All Available ({{ availableCourses.length }})
          </label>
          <span v-if="selectedCourses.length > 0" class="selected-count">
            {{ selectedCourses.length }} selected
          </span>
        </div>
        <div class="bulk-buttons">
          <button 
            v-if="selectedAvailableCourses.length > 0"
            @click="handleBulkEnroll" 
            :disabled="enrolling"
            class="bulk-enroll-btn"
          >
            <span v-if="enrolling">Enrolling...</span>
            <span v-else>Enroll in {{ selectedAvailableCourses.length }} Course{{ selectedAvailableCourses.length > 1 ? 's' : '' }}</span>
          </button>
          <button 
            v-if="selectedCourses.length > 0"
            @click="clearSelection" 
            class="clear-selection-btn"
          >
            Clear Selection
          </button>
        </div>
      </div>

      <!-- Wishlist Courses -->
      <div v-if="wishlistItems.length > 0" class="courses-grid">
        <div v-for="item in wishlistItems" :key="item.id" class="course-card">
          <!-- Selection Checkbox -->
          <div class="course-selection">
            <input 
              type="checkbox" 
              :value="item.course"
              v-model="selectedCourses"
              :disabled="!item.is_course_available || item.is_enrolled"
              class="course-checkbox"
            />
          </div>

          <!-- Course Image -->
          <div class="course-image">
            <img :src="item.course_thumbnail || '/placeholder-course.jpg'" :alt="item.course_title" />
            <button @click="handleRemoveFromWishlist(item.course)" class="remove-btn">
              <span class="remove-icon">❌</span>
            </button>
            
            <!-- Priority Badge -->
            <div class="priority-badge" :style="{ backgroundColor: getPriorityColor(item.priority) }">
              {{ getPriorityLabel(item.priority) }}
            </div>

            <!-- Status Badges -->
            <div class="status-badges">
              <span v-if="item.is_enrolled" class="status-badge enrolled">Enrolled</span>
              <span v-else-if="!item.is_course_available" class="status-badge unavailable">Unavailable</span>
            </div>
          </div>
          
          <div class="course-info">
            <div class="course-category">{{ item.course_category }}</div>
            <h3>{{ item.course_title }}</h3>
            <p class="instructor">{{ item.course_instructor }}</p>
            
            <div class="course-meta">
              <div class="rating">
                <span class="stars">⭐</span>
                <span>{{ item.course_average_rating?.toFixed(1) || 'New' }}</span>
                <span class="enrollments">({{ item.course_total_enrollments }} students)</span>
              </div>
              <div class="difficulty">{{ item.course_difficulty }}</div>
            </div>

            <div class="price-section">
              <span v-if="item.course_price" class="price">${{ item.course_price }}</span>
              <span v-else class="price free">Free</span>
            </div>

            <!-- Personal Notes -->
            <div v-if="item.notes" class="notes">
              <strong>Notes:</strong> {{ item.notes }}
            </div>
            
            <div class="course-actions">
              <router-link :to="`/courses/${item.course}`" class="view-btn">
                View Course
              </router-link>
              <button 
                v-if="!item.is_enrolled && item.is_course_available"
                @click="handleEnrollInCourse(item.course)" 
                :disabled="enrolling"
                class="enroll-btn"
              >
                <span v-if="enrolling">Enrolling...</span>
                <span v-else>{{ item.course_price ? 'Buy Now' : 'Enroll Free' }}</span>
              </button>
              <button 
                v-else-if="item.is_enrolled"
                @click="$router.push(`/student/courses/${item.course}`)"
                class="continue-btn"
              >
                Continue Learning
              </button>
            </div>

            <div class="added-info">
              Added {{ formatDate(item.added_at) }}
            </div>
          </div>
        </div>
      </div>

      <!-- Empty Wishlist -->
      <div v-else class="empty-wishlist">
        <div class="empty-icon">💔</div>
        <h3>Your wishlist is empty</h3>
        <p>Browse courses and add them to your wishlist to save them for later</p>
        <router-link to="/courses" class="browse-btn">
          Browse Courses
        </router-link>
      </div>

      <!-- Analytics Section -->
      <div v-if="analytics && wishlistItems.length > 0" class="analytics-section">
        <h2>Wishlist Insights</h2>
        
        <div class="analytics-grid">
          <!-- Category Distribution -->
          <div class="analytics-card">
            <h3>Categories</h3>
            <div class="category-list">
              <div v-for="category in analytics.categories" :key="category.name" class="category-item">
                <span class="category-name">{{ category.name }}</span>
                <span class="category-count">{{ category.count }} courses</span>
                <span class="category-value">${{ category.total_value.toFixed(2) }}</span>
              </div>
            </div>
          </div>

          <!-- Price Ranges -->
          <div class="analytics-card">
            <h3>Price Distribution</h3>
            <div class="price-ranges">
              <div v-for="(count, range) in analytics.price_ranges" :key="range" class="price-range">
                <span class="range-label">{{ formatPriceRange(range) }}</span>
                <span class="range-count">{{ count }} courses</span>
              </div>
            </div>
          </div>

          <!-- Availability Status -->
          <div class="analytics-card">
            <h3>Course Status</h3>
            <div class="status-breakdown">
              <div class="status-item available">
                <span class="status-label">Available</span>
                <span class="status-count">{{ analytics.availability_status.available }}</span>
              </div>
              <div class="status-item enrolled">
                <span class="status-label">Already Enrolled</span>
                <span class="status-count">{{ analytics.availability_status.enrolled }}</span>
              </div>
              <div class="status-item unavailable">
                <span class="status-label">Unavailable</span>
                <span class="status-count">{{ analytics.availability_status.unavailable }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Recommendations -->
        <div v-if="analytics.recommendations?.length > 0" class="recommendations">
          <h3>Recommended for You</h3>
          <div class="recommendations-grid">
            <div v-for="rec in analytics.recommendations.slice(0, 3)" :key="rec.course_id" class="recommendation-card">
              <h4>{{ rec.title }}</h4>
              <p class="rec-instructor">{{ rec.instructor }}</p>
              <p class="rec-reason">{{ rec.reason }}</p>
              <div class="rec-meta">
                <span class="rec-price">${{ rec.price }}</span>
                <span class="rec-rating">⭐ {{ rec.average_rating.toFixed(1) }}</span>
              </div>
              <button @click="addRecommendationToWishlist(rec.course_id)" class="add-rec-btn">
                Add to Wishlist
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useWishlist } from '@/composables/useWishlist'
import { useErrorHandler } from '@/composables/useErrorHandler'
import { CourseService } from '@/services/courses'

const { handleApiError } = useErrorHandler()

// Wishlist composable
const {
  wishlistItems,
  analytics,
  loading,
  error,
  totalValue,
  totalItems,
  availableCourses,
  enrolledCourses,
  loadWishlistItems,
  loadAnalytics,
  removeFromWishlist,
  bulkEnroll,
  addToWishlist,
  refresh
} = useWishlist()

// Local state
const selectedCourses = ref<string[]>([])
const enrolling = ref(false)

// Computed properties
const hasSelectedCourses = computed(() => selectedCourses.value.length > 0)

const selectedAvailableCourses = computed(() => {
  return selectedCourses.value.filter(courseId => {
    const item = wishlistItems.value.find(w => w.course === courseId)
    return item && item.is_course_available && !item.is_enrolled
  })
})

// Methods
const handleRemoveFromWishlist = async (courseId: string) => {
  try {
    await removeFromWishlist(courseId)
    // Remove from selected courses if it was selected
    selectedCourses.value = selectedCourses.value.filter(id => id !== courseId)
  } catch (error) {
    console.error('Failed to remove from wishlist:', error)
  }
}

const handleEnrollInCourse = async (courseId: string) => {
  try {
    enrolling.value = true
    await CourseService.enrollInCourse(courseId)
    // Remove from wishlist after successful enrollment
    await handleRemoveFromWishlist(courseId)
  } catch (error) {
    handleApiError(error, { context: { action: 'enroll_in_course' } })
  } finally {
    enrolling.value = false
  }
}

const handleBulkEnroll = async () => {
  if (selectedAvailableCourses.value.length === 0) return
  
  try {
    enrolling.value = true
    await bulkEnroll(selectedAvailableCourses.value)
    selectedCourses.value = []
  } catch (error) {
    console.error('Bulk enrollment failed:', error)
  } finally {
    enrolling.value = false
  }
}

const toggleSelectAll = () => {
  if (selectedCourses.value.length === availableCourses.value.length) {
    selectedCourses.value = []
  } else {
    selectedCourses.value = availableCourses.value.map(item => item.course)
  }
}

const clearSelection = () => {
  selectedCourses.value = []
}

const addRecommendationToWishlist = async (courseId: string) => {
  try {
    await addToWishlist(courseId)
    await loadAnalytics() // Refresh analytics after adding
  } catch (error) {
    console.error('Failed to add recommendation to wishlist:', error)
  }
}

const handleRetry = async () => {
  try {
    await refresh()
  } catch (err) {
    handleApiError(err as any, { context: { action: 'retry_wishlist_load' } })
  }
}

const getPriorityLabel = (priority: number) => {
  switch (priority) {
    case 3: return 'High'
    case 2: return 'Medium'
    case 1: return 'Low'
    default: return 'Medium'
  }
}

const getPriorityColor = (priority: number) => {
  switch (priority) {
    case 3: return '#ef4444' // red
    case 2: return '#f59e0b' // amber
    case 1: return '#10b981' // emerald
    default: return '#f59e0b'
  }
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffTime = Math.abs(now.getTime() - date.getTime())
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  
  if (diffDays === 1) return 'yesterday'
  if (diffDays < 7) return `${diffDays} days ago`
  if (diffDays < 30) return `${Math.ceil(diffDays / 7)} weeks ago`
  return `${Math.ceil(diffDays / 30)} months ago`
}

const formatPriceRange = (range: string) => {
  switch (range) {
    case 'free': return 'Free'
    case 'under_50': return 'Under $50'
    case 'under_100': return '$50 - $100'
    case 'under_200': return '$100 - $200'
    case 'over_200': return 'Over $200'
    default: return range
  }
}

// Lifecycle
onMounted(async () => {
  try {
    await loadWishlistItems()
    if (wishlistItems.value.length > 0) {
      await loadAnalytics()
    }
  } catch (error) {
    console.error('Failed to load wishlist data:', error)
  }
})
</script>

<style scoped>
.wishlist-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  min-height: 100vh;
}

.page-header {
  margin-bottom: 2rem;
}

.page-header h1 {
  font-size: 2rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.page-header p {
  color: #6b7280;
  font-size: 1.125rem;
}

.wishlist-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(254, 243, 226, 0.3));
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.1);
  text-align: center;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(245, 158, 11, 0.15);
}

.stat-icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.stat-card h3 {
  font-size: 0.875rem;
  font-weight: 500;
  color: #6b7280;
  margin-bottom: 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.stat-number {
  font-size: 1.5rem;
  font-weight: 700;
  color: #f59e0b;
  margin: 0;
}

.bulk-actions {
  background: white;
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.selection-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.select-all {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.selected-count {
  color: #f59e0b;
  font-weight: 500;
}

.bulk-buttons {
  display: flex;
  gap: 0.5rem;
}

.bulk-enroll-btn, .clear-selection-btn {
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.bulk-enroll-btn {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  border: none;
}

.bulk-enroll-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
}

.bulk-enroll-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.clear-selection-btn {
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
}

.clear-selection-btn:hover {
  background: #e5e7eb;
}

.courses-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2rem;
  margin-bottom: 2rem;
}

.course-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.1);
  transition: all 0.3s ease;
  position: relative;
}

.course-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 30px rgba(245, 158, 11, 0.15);
}

.course-selection {
  position: absolute;
  top: 0.5rem;
  left: 0.5rem;
  z-index: 10;
}

.course-checkbox {
  width: 20px;
  height: 20px;
  cursor: pointer;
}

.course-image {
  position: relative;
  height: 200px;
  overflow: hidden;
}

.course-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.remove-btn {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  border: none;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.remove-btn:hover {
  background: rgba(239, 68, 68, 0.9);
  transform: scale(1.1);
}

.priority-badge {
  position: absolute;
  bottom: 0.5rem;
  left: 0.5rem;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-badges {
  position: absolute;
  bottom: 0.5rem;
  right: 0.5rem;
  display: flex;
  gap: 0.25rem;
}

.status-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-badge.enrolled {
  background: #10b981;
  color: white;
}

.status-badge.unavailable {
  background: #ef4444;
  color: white;
}

.course-info {
  padding: 1.5rem;
}

.course-category {
  font-size: 0.75rem;
  color: #f59e0b;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.5rem;
}

.course-info h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.instructor {
  font-size: 0.875rem;
  color: #f59e0b;
  font-weight: 500;
  margin-bottom: 0.75rem;
}

.course-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  font-size: 0.875rem;
}

.rating {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.enrollments {
  color: #6b7280;
  font-size: 0.75rem;
}

.difficulty {
  color: #6b7280;
  text-transform: capitalize;
}

.price-section {
  margin-bottom: 1rem;
}

.price {
  font-weight: 700;
  color: #10b981;
  font-size: 1rem;
}

.price.free {
  color: #10b981;
}

.notes {
  background: #f9fafb;
  padding: 0.75rem;
  border-radius: 6px;
  margin-bottom: 1rem;
  font-size: 0.875rem;
  color: #374151;
}

.course-actions {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.view-btn, .enroll-btn, .continue-btn {
  flex: 1;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  font-weight: 600;
  text-decoration: none;
  text-align: center;
  transition: all 0.3s ease;
  border: none;
  cursor: pointer;
}

.view-btn {
  background: linear-gradient(135deg, #fef3e2, #fed7aa);
  color: #92400e;
  border: 1px solid rgba(245, 158, 11, 0.3);
}

.view-btn:hover {
  background: linear-gradient(135deg, #fed7aa, #fdba74);
  border-color: #f59e0b;
}

.enroll-btn {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
}

.enroll-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(245, 158, 11, 0.4);
}

.enroll-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.continue-btn {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
}

.continue-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(16, 185, 129, 0.4);
}

.added-info {
  font-size: 0.75rem;
  color: #9ca3af;
  text-align: center;
}

.analytics-section {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
}

.analytics-section h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 1.5rem;
}

.analytics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.analytics-card {
  background: #f9fafb;
  padding: 1.5rem;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.analytics-card h3 {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 1rem;
}

.category-list, .price-ranges, .status-breakdown {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.category-item, .price-range, .status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem;
  background: white;
  border-radius: 4px;
  font-size: 0.875rem;
}

.category-name, .range-label, .status-label {
  font-weight: 500;
  color: #374151;
}

.category-count, .range-count, .status-count {
  color: #6b7280;
}

.category-value {
  color: #f59e0b;
  font-weight: 600;
}

.status-item.available {
  border-left: 4px solid #10b981;
}

.status-item.enrolled {
  border-left: 4px solid #3b82f6;
}

.status-item.unavailable {
  border-left: 4px solid #ef4444;
}

.recommendations {
  margin-top: 2rem;
}

.recommendations h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 1rem;
}

.recommendations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.recommendation-card {
  background: white;
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  transition: all 0.3s ease;
}

.recommendation-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.recommendation-card h4 {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.rec-instructor {
  font-size: 0.875rem;
  color: #f59e0b;
  margin-bottom: 0.5rem;
}

.rec-reason {
  font-size: 0.75rem;
  color: #6b7280;
  margin-bottom: 0.75rem;
}

.rec-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
  font-size: 0.875rem;
}

.rec-price {
  font-weight: 600;
  color: #10b981;
}

.rec-rating {
  color: #6b7280;
}

.add-rec-btn {
  width: 100%;
  padding: 0.5rem;
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.add-rec-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
}

.empty-wishlist {
  text-align: center;
  padding: 4rem 2rem;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(254, 243, 226, 0.3));
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.1);
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.empty-wishlist h3 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.empty-wishlist p {
  color: #6b7280;
  margin-bottom: 2rem;
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
}

.browse-btn {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  padding: 0.75rem 2rem;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s ease;
  display: inline-block;
}

.browse-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(245, 158, 11, 0.4);
}

/* Loading and Error States */
.loading-state, .error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
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

.retry-btn {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.retry-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(245, 158, 11, 0.4);
}

/* Responsive */
@media (max-width: 768px) {
  .wishlist-view {
    padding: 1rem;
  }
  
  .wishlist-stats {
    grid-template-columns: 1fr;
  }
  
  .courses-grid {
    grid-template-columns: 1fr;
  }
  
  .bulk-actions {
    flex-direction: column;
    align-items: stretch;
  }
  
  .bulk-buttons {
    justify-content: stretch;
  }
  
  .bulk-enroll-btn, .clear-selection-btn {
    flex: 1;
  }
  
  .analytics-grid {
    grid-template-columns: 1fr;
  }
  
  .recommendations-grid {
    grid-template-columns: 1fr;
  }
}
</style>