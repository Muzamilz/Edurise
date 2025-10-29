<template>
  <div class="wishlist-analytics">
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>Loading analytics...</p>
    </div>

    <div v-else-if="error" class="error-state">
      <p>Failed to load analytics</p>
      <button @click="loadAnalytics" class="retry-btn">Retry</button>
    </div>

    <div v-else-if="analytics" class="analytics-content">
      <!-- Summary Stats -->
      <div class="summary-stats">
        <div class="stat-item">
          <div class="stat-icon">📚</div>
          <div class="stat-info">
            <span class="stat-value">{{ analytics.total_items }}</span>
            <span class="stat-label">Total Courses</span>
          </div>
        </div>
        <div class="stat-item">
          <div class="stat-icon">💰</div>
          <div class="stat-info">
            <span class="stat-value">${{ analytics.total_value.toFixed(2) }}</span>
            <span class="stat-label">Total Value</span>
          </div>
        </div>
        <div class="stat-item">
          <div class="stat-icon">📊</div>
          <div class="stat-info">
            <span class="stat-value">${{ analytics.average_price.toFixed(2) }}</span>
            <span class="stat-label">Avg Price</span>
          </div>
        </div>
      </div>

      <!-- Category Distribution -->
      <div v-if="analytics.categories.length > 0" class="analytics-section">
        <h3>Categories</h3>
        <div class="category-chart">
          <div 
            v-for="category in analytics.categories" 
            :key="category.name"
            class="category-bar"
          >
            <div class="category-info">
              <span class="category-name">{{ formatCategoryName(category.name) }}</span>
              <span class="category-stats">{{ category.count }} courses • ${{ category.total_value.toFixed(2) }}</span>
            </div>
            <div class="category-progress">
              <div 
                class="category-fill"
                :style="{ width: `${(category.count / analytics.total_items) * 100}%` }"
              ></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Price Distribution -->
      <div class="analytics-section">
        <h3>Price Distribution</h3>
        <div class="price-distribution">
          <div 
            v-for="(count, range) in analytics.price_ranges" 
            :key="range"
            class="price-range-item"
            :class="{ 'has-courses': count > 0 }"
          >
            <div class="price-range-label">{{ formatPriceRange(range) }}</div>
            <div class="price-range-bar">
              <div 
                class="price-range-fill"
                :style="{ width: `${(count / analytics.total_items) * 100}%` }"
              ></div>
            </div>
            <div class="price-range-count">{{ count }}</div>
          </div>
        </div>
      </div>

      <!-- Availability Status -->
      <div class="analytics-section">
        <h3>Course Status</h3>
        <div class="status-grid">
          <div class="status-card available">
            <div class="status-icon">✅</div>
            <div class="status-info">
              <span class="status-count">{{ analytics.availability_status.available }}</span>
              <span class="status-label">Available</span>
            </div>
          </div>
          <div class="status-card enrolled">
            <div class="status-icon">🎓</div>
            <div class="status-info">
              <span class="status-count">{{ analytics.availability_status.enrolled }}</span>
              <span class="status-label">Enrolled</span>
            </div>
          </div>
          <div class="status-card unavailable">
            <div class="status-icon">❌</div>
            <div class="status-info">
              <span class="status-count">{{ analytics.availability_status.unavailable }}</span>
              <span class="status-label">Unavailable</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Recommendations -->
      <div v-if="analytics.recommendations && analytics.recommendations.length > 0" class="analytics-section">
        <h3>Recommended for You</h3>
        <div class="recommendations-list">
          <div 
            v-for="rec in analytics.recommendations.slice(0, showAllRecommendations ? undefined : 3)" 
            :key="rec.course_id"
            class="recommendation-item"
          >
            <div class="rec-main">
              <h4 class="rec-title">{{ rec.title }}</h4>
              <p class="rec-instructor">by {{ rec.instructor }}</p>
              <p class="rec-reason">{{ rec.reason }}</p>
            </div>
            <div class="rec-meta">
              <div class="rec-price">${{ rec.price }}</div>
              <div class="rec-rating">⭐ {{ rec.average_rating.toFixed(1) }}</div>
              <div class="rec-students">{{ rec.enrollment_count }} students</div>
            </div>
            <div class="rec-actions">
              <button @click="$emit('add-to-wishlist', rec.course_id)" class="add-wishlist-btn">
                Add to Wishlist
              </button>
              <router-link :to="`/courses/${rec.course_id}`" class="view-course-btn">
                View Course
              </router-link>
            </div>
          </div>
        </div>
        
        <button 
          v-if="analytics.recommendations.length > 3"
          @click="showAllRecommendations = !showAllRecommendations"
          class="toggle-recommendations-btn"
        >
          {{ showAllRecommendations ? 'Show Less' : `Show All ${analytics.recommendations.length} Recommendations` }}
        </button>
      </div>
    </div>

    <div v-else class="empty-state">
      <p>No analytics data available</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useWishlist } from '@/composables/useWishlist'
// import type { WishlistAnalytics } from '@/types/api'

interface Emits {
  (e: 'add-to-wishlist', courseId: string): void
}

defineEmits<Emits>() // Used via $emit in template

const { analytics, loadAnalytics } = useWishlist()
const loading = ref(false)
const error = ref<Error | null>(null)
const showAllRecommendations = ref(false)

const formatCategoryName = (category: string) => {
  return category.charAt(0).toUpperCase() + category.slice(1).replace('_', ' ')
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

const loadData = async () => {
  loading.value = true
  error.value = null
  
  try {
    await loadAnalytics()
  } catch (err) {
    error.value = err as Error
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.wishlist-analytics {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.loading-state, .error-state, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  text-align: center;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #f3f4f6;
  border-top: 3px solid #f59e0b;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.retry-btn {
  background: #f59e0b;
  color: white;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
}

.retry-btn:hover {
  background: #d97706;
  transform: translateY(-1px);
}

.analytics-content {
  padding: 1.5rem;
}

.summary-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.stat-icon {
  font-size: 1.5rem;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1f2937;
}

.stat-label {
  font-size: 0.75rem;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.analytics-section {
  margin-bottom: 2rem;
}

.analytics-section:last-child {
  margin-bottom: 0;
}

.analytics-section h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 1rem;
}

.category-chart {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.category-bar {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.category-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.category-name {
  font-weight: 500;
  color: #374151;
}

.category-stats {
  font-size: 0.875rem;
  color: #6b7280;
}

.category-progress {
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
}

.category-fill {
  height: 100%;
  background: linear-gradient(90deg, #f59e0b, #d97706);
  transition: width 0.3s ease;
}

.price-distribution {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.price-range-item {
  display: grid;
  grid-template-columns: 1fr 2fr auto;
  gap: 1rem;
  align-items: center;
  padding: 0.5rem;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.price-range-item.has-courses {
  background: #f9fafb;
}

.price-range-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
}

.price-range-bar {
  height: 6px;
  background: #e5e7eb;
  border-radius: 3px;
  overflow: hidden;
}

.price-range-fill {
  height: 100%;
  background: linear-gradient(90deg, #10b981, #059669);
  transition: width 0.3s ease;
}

.price-range-count {
  font-size: 0.875rem;
  font-weight: 600;
  color: #6b7280;
  min-width: 20px;
  text-align: right;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 1rem;
}

.status-card {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  border-radius: 8px;
  border: 2px solid;
  transition: all 0.3s ease;
}

.status-card.available {
  border-color: #10b981;
  background: #ecfdf5;
}

.status-card.enrolled {
  border-color: #3b82f6;
  background: #eff6ff;
}

.status-card.unavailable {
  border-color: #ef4444;
  background: #fef2f2;
}

.status-icon {
  font-size: 1.25rem;
}

.status-info {
  display: flex;
  flex-direction: column;
}

.status-count {
  font-size: 1.125rem;
  font-weight: 700;
  color: #1f2937;
}

.status-label {
  font-size: 0.75rem;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.recommendations-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.recommendation-item {
  display: grid;
  grid-template-columns: 1fr auto auto;
  gap: 1rem;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  transition: all 0.3s ease;
}

.recommendation-item:hover {
  background: #f3f4f6;
  border-color: #d1d5db;
}

.rec-main {
  min-width: 0;
}

.rec-title {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.25rem;
}

.rec-instructor {
  font-size: 0.875rem;
  color: #f59e0b;
  margin-bottom: 0.25rem;
}

.rec-reason {
  font-size: 0.75rem;
  color: #6b7280;
  line-height: 1.4;
}

.rec-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.25rem;
  font-size: 0.875rem;
}

.rec-price {
  font-weight: 600;
  color: #10b981;
}

.rec-rating, .rec-students {
  color: #6b7280;
}

.rec-actions {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.add-wishlist-btn, .view-course-btn {
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 500;
  text-decoration: none;
  text-align: center;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.add-wishlist-btn {
  background: #f59e0b;
  color: white;
  border: none;
  cursor: pointer;
}

.add-wishlist-btn:hover {
  background: #d97706;
  transform: translateY(-1px);
}

.view-course-btn {
  background: white;
  color: #374151;
  border: 1px solid #d1d5db;
}

.view-course-btn:hover {
  background: #f9fafb;
  border-color: #9ca3af;
}

.toggle-recommendations-btn {
  width: 100%;
  padding: 0.75rem;
  margin-top: 1rem;
  background: white;
  color: #f59e0b;
  border: 2px solid #f59e0b;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.toggle-recommendations-btn:hover {
  background: #f59e0b;
  color: white;
}

/* Responsive */
@media (max-width: 768px) {
  .summary-stats {
    grid-template-columns: 1fr;
  }
  
  .status-grid {
    grid-template-columns: 1fr;
  }
  
  .recommendation-item {
    grid-template-columns: 1fr;
    gap: 0.75rem;
  }
  
  .rec-meta {
    align-items: flex-start;
    flex-direction: row;
    justify-content: space-between;
  }
  
  .rec-actions {
    flex-direction: row;
  }
}
</style>