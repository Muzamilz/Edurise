<template>
  <div class="analytics-view">
    <div class="page-header">
      <h1>Teaching Analytics</h1>
      <p>Track your teaching performance and student engagement</p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>Loading analytics...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-state">
      <div class="error-icon">⚠️</div>
      <h3>Failed to load analytics</h3>
      <p>{{ error.message }}</p>
      <button @click="handleRetry" class="retry-btn">Try Again</button>
    </div>

    <!-- Analytics Content -->
    <div v-else class="analytics-content">
      <!-- Key Metrics -->
      <div class="metrics-grid">
        <div class="metric-card">
          <div class="metric-icon">👥</div>
          <h3>Total Students</h3>
          <p class="metric-number">{{ analyticsData?.totalStudents || 0 }}</p>
          <span class="metric-change positive">+12% this month</span>
        </div>
        <div class="metric-card">
          <div class="metric-icon">📚</div>
          <h3>Course Completion Rate</h3>
          <p class="metric-number">{{ analyticsData?.completionRate || 0 }}%</p>
          <span class="metric-change positive">+5% from last month</span>
        </div>
        <div class="metric-card">
          <div class="metric-icon">⭐</div>
          <h3>Average Rating</h3>
          <p class="metric-number">{{ analyticsData?.averageRating || 0 }}</p>
          <span class="metric-change neutral">{{ analyticsData?.totalReviews || 0 }} reviews</span>
        </div>
        <div class="metric-card">
          <div class="metric-icon">💰</div>
          <h3>Total Earnings</h3>
          <p class="metric-number">${{ analyticsData?.totalEarnings || 0 }}</p>
          <span class="metric-change positive">+8% this month</span>
        </div>
      </div>

      <!-- Charts Section -->
      <div class="charts-section">
        <div class="chart-container">
          <h3>Student Enrollment Trends</h3>
          <AnalyticsChart 
            :data="enrollmentData" 
            type="line"
            :height="300"
          />
        </div>
        
        <div class="chart-container">
          <h3>Course Performance</h3>
          <AnalyticsChart 
            :data="performanceData" 
            type="bar"
            :height="300"
          />
        </div>
      </div>

      <!-- Detailed Analytics -->
      <div class="detailed-analytics">
        <h2>Course Performance Details</h2>
        <div class="course-analytics-list">
          <div v-for="course in courseAnalytics" :key="course.id" class="course-analytics-card">
            <div class="course-info">
              <h4>{{ course.title }}</h4>
              <p>{{ course.enrollments }} students enrolled</p>
            </div>
            <div class="course-metrics">
              <div class="metric">
                <span class="metric-label">Completion Rate</span>
                <span class="metric-value">{{ course.completionRate }}%</span>
              </div>
              <div class="metric">
                <span class="metric-label">Avg. Progress</span>
                <span class="metric-value">{{ course.averageProgress }}%</span>
              </div>
              <div class="metric">
                <span class="metric-label">Rating</span>
                <span class="metric-value">{{ course.rating }}/5</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useApiData } from '@/composables/useApiData'
// Removed unused import
import { useErrorHandler } from '@/composables/useErrorHandler'
import AnalyticsChart from '@/components/analytics/AnalyticsChart.vue'

const { handleApiError } = useErrorHandler()

// API data
const { 
  data: analyticsData, 
  loading, 
  error, 
  refresh 
} = useApiData('/analytics/teacher/', {
  immediate: true,
  transform: (data) => {
    // Transform the response to ensure consistent data structure
    return {
      totalStudents: data.total_students || 0,
      completionRate: data.completion_rate || 0,
      averageRating: data.average_rating || 0,
      totalReviews: data.total_reviews || 0,
      totalEarnings: data.total_earnings || 0,
      courseAnalytics: (data.course_analytics || []).map((course: any) => ({
        id: course.id,
        title: course.title,
        enrollments: course.enrollments || 0,
        completionRate: course.completion_rate || 0,
        averageProgress: course.average_progress || 0,
        rating: course.average_rating || 0
      }))
    }
  },
  retryAttempts: 3,
  onError: (error) => {
    console.error('Failed to load analytics:', error)
  }
})

// Mock data for charts
const enrollmentData = computed(() => ({
  labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
  datasets: [{
    label: 'New Enrollments',
    data: [12, 19, 8, 15, 22, 18],
    borderColor: '#f59e0b',
    backgroundColor: 'rgba(245, 158, 11, 0.1)'
  }]
}))

const performanceData = computed(() => ({
  labels: ['Course A', 'Course B', 'Course C'],
  datasets: [{
    label: 'Completion Rate %',
    data: [85, 92, 78],
    backgroundColor: ['#10b981', '#3b82f6', '#8b5cf6']
  }]
}))

const courseAnalytics = computed(() => analyticsData.value?.courseAnalytics || [])

const handleRetry = async () => {
  try {
    await refresh()
  } catch (err) {
    handleApiError(err as any, { context: { action: 'retry_analytics_load' } })
  }
}
</script><style s
coped>
.analytics-view {
  max-width: 1400px;
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

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.metric-card {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(254, 243, 226, 0.3));
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.1);
  text-align: center;
  transition: all 0.3s ease;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(245, 158, 11, 0.15);
}

.metric-icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.metric-card h3 {
  font-size: 0.875rem;
  font-weight: 500;
  color: #6b7280;
  margin-bottom: 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.metric-number {
  font-size: 2rem;
  font-weight: 700;
  color: #f59e0b;
  margin: 0 0 0.25rem 0;
}

.metric-change {
  font-size: 0.75rem;
  font-weight: 500;
}

.metric-change.positive {
  color: #10b981;
}

.metric-change.negative {
  color: #ef4444;
}

.metric-change.neutral {
  color: #6b7280;
}

.charts-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 2rem;
  margin-bottom: 2rem;
}

.chart-container {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.1);
}

.chart-container h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 1rem;
}

.detailed-analytics {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.1);
}

.detailed-analytics h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 1.5rem;
}

.course-analytics-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.course-analytics-card {
  background: #f9fafb;
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.course-info h4 {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.25rem;
}

.course-info p {
  font-size: 0.875rem;
  color: #6b7280;
}

.course-metrics {
  display: flex;
  gap: 2rem;
}

.metric {
  text-align: center;
}

.metric-label {
  display: block;
  font-size: 0.75rem;
  color: #6b7280;
  margin-bottom: 0.25rem;
}

.metric-value {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
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
  .analytics-view {
    padding: 1rem;
  }
  
  .metrics-grid {
    grid-template-columns: 1fr;
  }
  
  .charts-section {
    grid-template-columns: 1fr;
  }
  
  .course-analytics-card {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .course-metrics {
    justify-content: space-around;
  }
}
</style>