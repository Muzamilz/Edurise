<template>
  <div class="recommendations-section">
    <!-- Section Header -->
    <div class="section-header">
      <div class="header-content">
        <h2>{{ title }}</h2>
        <p v-if="subtitle" class="subtitle">{{ subtitle }}</p>
      </div>
      <div class="header-actions">
        <select 
          v-if="showAlgorithmSelector"
          v-model="selectedAlgorithm" 
          @change="handleAlgorithmChange"
          class="algorithm-selector"
        >
          <option value="hybrid">Smart Recommendations</option>
          <option value="collaborative">Similar Users</option>
          <option value="content_based">Based on Your Interests</option>
          <option value="popularity">Popular Courses</option>
        </select>
        <button 
          @click="() => refreshRecommendations()" 
          :disabled="loading"
          class="refresh-btn"
        >
          <span v-if="loading" class="loading-spinner"></span>
          <span v-else>🔄</span>
          Refresh
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading && !hasRecommendations" class="loading-state">
      <div class="loading-grid">
        <div v-for="i in 3" :key="i" class="loading-card">
          <div class="loading-image"></div>
          <div class="loading-content">
            <div class="loading-line long"></div>
            <div class="loading-line medium"></div>
            <div class="loading-line short"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-state">
      <div class="error-icon">⚠️</div>
      <h3>Failed to load recommendations</h3>
      <p>{{ error.message }}</p>
      <button @click="handleRetry" class="retry-btn">Try Again</button>
    </div>

    <!-- Recommendations Grid -->
    <div v-else-if="hasRecommendations" class="recommendations-content">
      <!-- User Context Info -->
      <div v-if="showUserContext && userContext" class="user-context">
        <div class="context-item">
          <span class="context-label">Skill Level:</span>
          <span class="context-value skill-level" :class="userContext.skill_level">
            {{ formatSkillLevel(userContext.skill_level) }}
          </span>
        </div>
        <div v-if="topCategories.length > 0" class="context-item">
          <span class="context-label">Interests:</span>
          <div class="interests-tags">
            <span 
              v-for="{ category } in topCategories" 
              :key="category"
              class="interest-tag"
            >
              {{ formatCategory(category) }}
            </span>
          </div>
        </div>
      </div>

      <!-- Recommendations Grid -->
      <div class="recommendations-grid">
        <div 
          v-for="recommendation in displayedRecommendations" 
          :key="recommendation.course.id"
          class="recommendation-card"
          @click="handleCourseClick(recommendation)"
        >
          <!-- Recommendation Badge -->
          <div class="recommendation-badge">
            <span class="badge-icon">✨</span>
            <span class="confidence-score">{{ Math.round(recommendation.recommendation_score * 100) }}%</span>
          </div>

          <!-- Dismiss Button -->
          <button 
            @click.stop="handleDismiss(recommendation)"
            class="dismiss-btn"
            title="Don't show this recommendation"
          >
            ✕
          </button>

          <!-- Course Image -->
          <div class="course-image">
            <img 
              :src="recommendation.course.thumbnail || '/placeholder-course.jpg'" 
              :alt="recommendation.course.title"
              loading="lazy"
            />
            <div class="image-overlay">
              <div class="course-category">{{ formatCategory(recommendation.course.category) }}</div>
              <div class="course-difficulty">{{ recommendation.course.difficulty_level }}</div>
            </div>
          </div>

          <!-- Course Info -->
          <div class="course-info">
            <h3 class="course-title">{{ recommendation.course.title }}</h3>
            <p class="course-instructor">{{ recommendation.course.instructor ? `${recommendation.course.instructor.first_name} ${recommendation.course.instructor.last_name}` : 'Unknown Instructor' }}</p>
            
            <!-- Recommendation Reason -->
            <div class="recommendation-reason">
              <span class="reason-icon">💡</span>
              <span class="reason-text">{{ recommendation.recommendation_reason }}</span>
            </div>

            <!-- Course Meta -->
            <div class="course-meta">
              <div class="meta-item">
                <span class="meta-icon">⭐</span>
                <span>{{ recommendation.course.average_rating?.toFixed(1) || 'New' }}</span>
              </div>
              <div class="meta-item">
                <span class="meta-icon">👥</span>
                <span>{{ recommendation.course.total_enrollments || 0 }} students</span>
              </div>
              <div class="meta-item">
                <span class="meta-icon">⏱️</span>
                <span>{{ recommendation.course.duration_weeks || 4 }} weeks</span>
              </div>
            </div>

            <!-- Price -->
            <div class="course-price">
              <span v-if="recommendation.course.price" class="price">
                ${{ recommendation.course.price }}
              </span>
              <span v-else class="price free">Free</span>
            </div>

            <!-- Actions -->
            <div class="course-actions">
              <WishlistButton 
                :course-id="recommendation.course.id" 
                compact
                @toggle="handleWishlistToggle(recommendation, $event)"
              />
              <router-link 
                :to="`/courses/${recommendation.course.id}`"
                class="view-course-btn"
                @click="handleCourseClick(recommendation)"
              >
                View Course
              </router-link>
              <button 
                @click.stop="handleEnroll(recommendation)"
                class="enroll-btn"
              >
                {{ recommendation.course.price ? 'Buy Now' : 'Enroll Free' }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Load More Button -->
      <div v-if="canLoadMore" class="load-more-section">
        <button 
          @click="loadMoreRecommendations"
          :disabled="loading"
          class="load-more-btn"
        >
          <span v-if="loading">Loading...</span>
          <span v-else>Load More Recommendations</span>
        </button>
      </div>

      <!-- Algorithm Info -->
      <div v-if="showAlgorithmInfo" class="algorithm-info">
        <details class="algorithm-details">
          <summary>How we chose these recommendations</summary>
          <div class="algorithm-explanation">
            <p>{{ getAlgorithmExplanation(algorithmUsed) }}</p>
            <div v-if="userContext" class="user-stats">
              <div class="stat">
                <strong>{{ userContext.total_enrollments }}</strong> courses enrolled
              </div>
              <div class="stat">
                <strong>{{ userContext.completed_courses }}</strong> courses completed
              </div>
              <div class="stat">
                <strong>{{ userContext.wishlist_items }}</strong> courses in wishlist
              </div>
            </div>
          </div>
        </details>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="empty-state">
      <div class="empty-icon">🎯</div>
      <h3>No recommendations available</h3>
      <p>{{ getEmptyStateMessage() }}</p>
      <button @click="handleRetry" class="retry-btn">Try Again</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
// import { useRouter } from 'vue-router'
import { useRecommendations } from '@/composables/useRecommendations'
import { CourseService } from '@/services/courses'
import WishlistButton from './WishlistButton.vue'
import type { Recommendation } from '@/types/api'

interface Props {
  title?: string
  subtitle?: string
  limit?: number
  algorithm?: 'collaborative' | 'content_based' | 'popularity' | 'hybrid'
  context?: string
  showAlgorithmSelector?: boolean
  showUserContext?: boolean
  showAlgorithmInfo?: boolean
  autoLoad?: boolean
}

interface Emits {
  (e: 'course-click', recommendation: Recommendation): void
  (e: 'course-enroll', recommendation: Recommendation): void
  (e: 'wishlist-toggle', recommendation: Recommendation, added: boolean): void
  (e: 'recommendation-dismiss', recommendation: Recommendation): void
}

const props = withDefaults(defineProps<Props>(), {
  title: 'Recommended for You',
  subtitle: '',
  limit: 6,
  algorithm: 'hybrid',
  context: 'general',
  showAlgorithmSelector: true,
  showUserContext: true,
  showAlgorithmInfo: true,
  autoLoad: true
})

const emit = defineEmits<Emits>()

// const router = useRouter()

// Composables
const {
  recommendations,
  userContext,
  loading,
  error,
  algorithmUsed,
  hasRecommendations,
  topCategories,
  loadRecommendations,
  trackClick,
  trackWishlistAdd,
  trackEnrollment,
  trackDismiss,
  refreshRecommendations,
  clearError
} = useRecommendations()

// Local state
const selectedAlgorithm = ref(props.algorithm)
const displayLimit = ref(props.limit)

// Computed
const displayedRecommendations = computed(() => {
  return recommendations.value.slice(0, displayLimit.value)
})

const canLoadMore = computed(() => {
  return recommendations.value.length > displayLimit.value
})

// Methods
const handleAlgorithmChange = async () => {
  await loadRecommendations({
    limit: props.limit,
    algorithm: selectedAlgorithm.value,
    context: props.context
  })
}

const handleCourseClick = async (recommendation: Recommendation) => {
  await trackClick(recommendation)
  emit('course-click', recommendation)
}

const handleEnroll = async (recommendation: Recommendation) => {
  try {
    await CourseService.enrollInCourse(recommendation.course.id)
    await trackEnrollment(recommendation)
    emit('course-enroll', recommendation)
  } catch (error) {
    console.error('Enrollment failed:', error)
  }
}

const handleWishlistToggle = async (recommendation: Recommendation, added: boolean) => {
  if (added) {
    await trackWishlistAdd(recommendation)
  }
  emit('wishlist-toggle', recommendation, added)
}

const handleDismiss = async (recommendation: Recommendation) => {
  await trackDismiss(recommendation)
  emit('recommendation-dismiss', recommendation)
}

const loadMoreRecommendations = () => {
  displayLimit.value += props.limit
}

const handleRetry = async () => {
  clearError()
  await loadRecommendations({
    limit: props.limit,
    algorithm: selectedAlgorithm.value,
    context: props.context
  })
}

const formatCategory = (category: string) => {
  return category.charAt(0).toUpperCase() + category.slice(1).replace('_', ' ')
}

const formatSkillLevel = (level: string) => {
  return level.charAt(0).toUpperCase() + level.slice(1)
}

const getAlgorithmExplanation = (algorithm: string) => {
  switch (algorithm) {
    case 'collaborative':
      return 'These recommendations are based on courses that students with similar interests have enrolled in.'
    case 'content_based':
      return 'These recommendations match your learning preferences and course history.'
    case 'popularity':
      return 'These are the most popular and highly-rated courses on the platform.'
    case 'hybrid':
      return 'These recommendations combine multiple factors including your interests, similar students, and course popularity.'
    default:
      return 'These courses are personalized for your learning journey.'
  }
}

const getEmptyStateMessage = () => {
  if (userContext.value?.is_new_user) {
    return 'Start by enrolling in a few courses to get personalized recommendations!'
  }
  return 'We\'re working on finding the perfect courses for you. Check back soon!'
}

// Watchers
watch(() => props.algorithm, (newAlgorithm) => {
  selectedAlgorithm.value = newAlgorithm
})

// Lifecycle
onMounted(async () => {
  if (props.autoLoad) {
    await loadRecommendations({
      limit: props.limit,
      algorithm: props.algorithm,
      context: props.context
    })
  }
})
</script>

<style scoped>
.recommendations-section {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 2rem 2rem 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.header-content h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.25rem;
}

.subtitle {
  color: #6b7280;
  font-size: 0.875rem;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.algorithm-selector {
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: white;
  font-size: 0.875rem;
  cursor: pointer;
}

.refresh-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: #f59e0b;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.refresh-btn:hover:not(:disabled) {
  background: #d97706;
  transform: translateY(-1px);
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.loading-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-state {
  padding: 2rem;
}

.loading-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.loading-card {
  background: #f9fafb;
  border-radius: 8px;
  overflow: hidden;
  animation: pulse 2s infinite;
}

.loading-image {
  height: 180px;
  background: #e5e7eb;
}

.loading-content {
  padding: 1rem;
}

.loading-line {
  height: 12px;
  background: #e5e7eb;
  border-radius: 6px;
  margin-bottom: 0.5rem;
}

.loading-line.long { width: 100%; }
.loading-line.medium { width: 70%; }
.loading-line.short { width: 40%; }

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.error-state, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
}

.error-icon, .empty-icon {
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
}

.retry-btn {
  background: #f59e0b;
  color: white;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.retry-btn:hover {
  background: #d97706;
  transform: translateY(-2px);
}

.recommendations-content {
  padding: 1.5rem 2rem 2rem;
}

.user-context {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.context-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.context-label {
  font-size: 0.875rem;
  color: #6b7280;
  font-weight: 500;
}

.context-value {
  font-size: 0.875rem;
  font-weight: 600;
}

.skill-level.beginner { color: #10b981; }
.skill-level.intermediate { color: #f59e0b; }
.skill-level.advanced { color: #ef4444; }

.interests-tags {
  display: flex;
  gap: 0.5rem;
}

.interest-tag {
  padding: 0.25rem 0.5rem;
  background: #e0e7ff;
  color: #3730a3;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
}

.recommendations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.recommendation-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
  cursor: pointer;
  position: relative;
}

.recommendation-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
  border-color: #f59e0b;
}

.recommendation-badge {
  position: absolute;
  top: 0.75rem;
  left: 0.75rem;
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  z-index: 10;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.dismiss-btn {
  position: absolute;
  top: 0.75rem;
  right: 0.75rem;
  width: 28px;
  height: 28px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  font-size: 0.875rem;
  z-index: 10;
  transition: all 0.3s ease;
}

.dismiss-btn:hover {
  background: #ef4444;
  transform: scale(1.1);
}

.course-image {
  position: relative;
  height: 180px;
  overflow: hidden;
}

.course-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-overlay {
  position: absolute;
  bottom: 0.75rem;
  right: 0.75rem;
  display: flex;
  gap: 0.5rem;
}

.course-category, .course-difficulty {
  padding: 0.25rem 0.5rem;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
}

.course-info {
  padding: 1.5rem;
}

.course-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.5rem;
  line-height: 1.4;
}

.course-instructor {
  color: #f59e0b;
  font-size: 0.875rem;
  font-weight: 500;
  margin-bottom: 0.75rem;
}

.recommendation-reason {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  padding: 0.75rem;
  background: #fef3e2;
  border-radius: 6px;
  margin-bottom: 1rem;
}

.reason-icon {
  font-size: 1rem;
  flex-shrink: 0;
}

.reason-text {
  font-size: 0.875rem;
  color: #92400e;
  line-height: 1.4;
}

.course-meta {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1rem;
  font-size: 0.875rem;
  color: #6b7280;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.course-price {
  margin-bottom: 1rem;
}

.price {
  font-size: 1.125rem;
  font-weight: 700;
  color: #10b981;
}

.price.free {
  color: #10b981;
}

.course-actions {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.view-course-btn, .enroll-btn {
  flex: 1;
  padding: 0.75rem;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  text-decoration: none;
  text-align: center;
  transition: all 0.3s ease;
  cursor: pointer;
}

.view-course-btn {
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
}

.view-course-btn:hover {
  background: #e5e7eb;
  border-color: #9ca3af;
}

.enroll-btn {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  border: none;
}

.enroll-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
}

.load-more-section {
  text-align: center;
  margin-bottom: 1rem;
}

.load-more-btn {
  background: white;
  color: #f59e0b;
  border: 2px solid #f59e0b;
  padding: 0.75rem 2rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.load-more-btn:hover:not(:disabled) {
  background: #f59e0b;
  color: white;
}

.load-more-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.algorithm-info {
  border-top: 1px solid #e5e7eb;
  padding-top: 1rem;
}

.algorithm-details summary {
  cursor: pointer;
  font-weight: 500;
  color: #374151;
  padding: 0.5rem 0;
}

.algorithm-explanation {
  padding: 1rem 0;
  color: #6b7280;
  font-size: 0.875rem;
  line-height: 1.6;
}

.user-stats {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
}

.stat {
  font-size: 0.875rem;
  color: #374151;
}

.stat strong {
  color: #f59e0b;
}

/* Responsive */
@media (max-width: 768px) {
  .section-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }

  .header-actions {
    justify-content: space-between;
  }

  .recommendations-grid {
    grid-template-columns: 1fr;
  }

  .user-context {
    flex-direction: column;
    gap: 0.5rem;
  }

  .course-meta {
    flex-direction: column;
    gap: 0.5rem;
  }

  .course-actions {
    flex-direction: column;
  }

  .user-stats {
    flex-direction: column;
    gap: 0.5rem;
  }
}
</style>