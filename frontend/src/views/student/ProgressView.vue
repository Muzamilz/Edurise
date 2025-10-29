<template>
  <div class="progress-view">
    <div class="page-header">
      <h1>Learning Progress</h1>
      <p>Track your learning journey and achievements</p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>Loading your progress...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-state">
      <div class="error-icon">⚠️</div>
      <h3>Failed to load progress</h3>
      <p>{{ error.message }}</p>
      <button @click="handleRetry" class="retry-btn">Try Again</button>
    </div>

    <!-- Progress Content -->
    <div v-else class="progress-content">
      <!-- Overall Progress Stats -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon">📚</div>
          <h3>Courses Enrolled</h3>
          <p class="stat-number">{{ progressData?.totalEnrollments || 0 }}</p>
        </div>
        <div class="stat-card">
          <div class="stat-icon">✅</div>
          <h3>Courses Completed</h3>
          <p class="stat-number">{{ progressData?.completedCourses || 0 }}</p>
        </div>
        <div class="stat-card">
          <div class="stat-icon">⏱️</div>
          <h3>Hours Learned</h3>
          <p class="stat-number">{{ progressData?.totalHours || 0 }}</p>
        </div>
        <div class="stat-card">
          <div class="stat-icon">🎯</div>
          <h3>Average Progress</h3>
          <p class="stat-number">{{ progressData?.averageProgress || 0 }}%</p>
        </div>
      </div>

      <!-- Course Progress -->
      <div class="course-progress-section">
        <h2>Course Progress</h2>
        <div v-if="courseProgress?.length > 0" class="course-progress-list">
          <div v-for="course in courseProgress" :key="course.id" class="course-progress-card">
            <div class="course-info">
              <img :src="course.thumbnail || '/placeholder-course.jpg'" :alt="course.title" class="course-thumbnail" />
              <div class="course-details">
                <h3>{{ course.title }}</h3>
                <p class="instructor">{{ course.instructor }}</p>
                <p class="enrollment-date">Enrolled {{ formatDate(course.enrolledAt) }}</p>
              </div>
            </div>
            <div class="progress-info">
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: course.progress + '%' }"></div>
              </div>
              <div class="progress-details">
                <span class="progress-percentage">{{ course.progress }}%</span>
                <span class="progress-status" :class="course.status">{{ formatStatus(course.status) }}</span>
              </div>
            </div>
            <div class="course-actions">
              <router-link :to="`/courses/${course.id}/learn`" class="continue-btn">
                Continue Learning
              </router-link>
            </div>
          </div>
        </div>
        <div v-else class="empty-state">
          <div class="empty-icon">📚</div>
          <h3>No courses yet</h3>
          <p>Start your learning journey by enrolling in a course</p>
          <router-link to="/courses" class="browse-btn">Browse Courses</router-link>
        </div>
      </div>

      <!-- Learning Goals -->
      <div class="goals-section">
        <h2>Learning Goals</h2>
        <div class="goals-grid">
          <div class="goal-card">
            <div class="goal-header">
              <h3>Weekly Goal</h3>
              <span class="goal-progress">{{ weeklyProgress }}/{{ weeklyGoal }}h</span>
            </div>
            <div class="goal-bar">
              <div class="goal-fill" :style="{ width: (weeklyProgress / weeklyGoal * 100) + '%' }"></div>
            </div>
            <p class="goal-description">Study {{ weeklyGoal }} hours this week</p>
          </div>
          
          <div class="goal-card">
            <div class="goal-header">
              <h3>Monthly Goal</h3>
              <span class="goal-progress">{{ monthlyProgress }}/{{ monthlyGoal }}</span>
            </div>
            <div class="goal-bar">
              <div class="goal-fill" :style="{ width: (monthlyProgress / monthlyGoal * 100) + '%' }"></div>
            </div>
            <p class="goal-description">Complete {{ monthlyGoal }} courses this month</p>
          </div>
        </div>
      </div>

      <!-- Achievements -->
      <div class="achievements-section">
        <h2>Achievements</h2>
        <div class="achievements-grid">
          <div v-for="achievement in achievements" :key="achievement.id" class="achievement-card" :class="{ earned: achievement.earned }">
            <div class="achievement-icon">{{ achievement.icon }}</div>
            <h3>{{ achievement.title }}</h3>
            <p>{{ achievement.description }}</p>
            <div v-if="achievement.earned" class="earned-badge">Earned!</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useApiData } from '@/composables/useApiData'
import type { APIError } from '@/services/api'
import { useErrorHandler } from '@/composables/useErrorHandler'

const { handleApiError } = useErrorHandler()

// Data fetching
const { data: progressData, loading, error, refresh } = useApiData('/course-progress/', {
  immediate: true,
  transform: (data) => {
    // Transform the response to ensure consistent data structure
    return {
      totalEnrollments: data.total_enrollments || 0,
      completedCourses: data.completed_courses || 0,
      totalHours: data.total_hours || 0,
      averageProgress: data.average_progress || 0,
      courseProgress: (data.course_progress || []).map((progress: any) => ({
        id: progress.id,
        title: progress.course?.title || progress.course_title,
        instructor: progress.course?.instructor?.full_name || progress.instructor_name,
        thumbnail: progress.course?.thumbnail,
        progress: progress.progress_percentage || 0,
        enrolledAt: progress.enrolled_at,
        status: progress.status || (progress.progress_percentage >= 100 ? 'completed' : 
                 progress.progress_percentage > 0 ? 'active' : 'not_started')
      }))
    }
  },
  retryAttempts: 3,
  onError: (error) => {
    console.error('Failed to load progress data:', error)
  }
})

// Mock data for goals and achievements
const weeklyGoal = ref(10)
const weeklyProgress = ref(7)
const monthlyGoal = ref(3)
const monthlyProgress = ref(1)

const achievements = ref([
  {
    id: 1,
    title: 'First Steps',
    description: 'Complete your first course',
    icon: '🎯',
    earned: true
  },
  {
    id: 2,
    title: 'Dedicated Learner',
    description: 'Study for 7 consecutive days',
    icon: '🔥',
    earned: false
  },
  {
    id: 3,
    title: 'Course Master',
    description: 'Complete 5 courses',
    icon: '🏆',
    earned: false
  }
])

// Computed properties
const courseProgress = computed(() => progressData.value?.courseProgress || [])

// Methods
const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString()
}

const formatStatus = (status: string) => {
  return status.charAt(0).toUpperCase() + status.slice(1)
}

const handleRetry = async () => {
  try {
    await refresh()
  } catch (err) {
    handleApiError(err as APIError, { context: { action: 'retry_progress_load' } })
  }
}

onMounted(() => {
  refresh()
})
</script>

<style scoped>
.progress-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
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

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
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
  font-size: 2rem;
  font-weight: 700;
  color: #f59e0b;
  margin: 0;
}

.course-progress-section, .goals-section, .achievements-section {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(254, 243, 226, 0.3));
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.1);
  margin-bottom: 2rem;
}

.course-progress-section h2, .goals-section h2, .achievements-section h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 1.5rem;
}

.course-progress-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.course-progress-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  border: 1px solid rgba(245, 158, 11, 0.1);
  display: grid;
  grid-template-columns: 1fr auto auto;
  gap: 1.5rem;
  align-items: center;
}

.course-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.course-thumbnail {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  object-fit: cover;
}

.course-details h3 {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.25rem;
}

.instructor {
  font-size: 0.875rem;
  color: #6b7280;
  margin-bottom: 0.25rem;
}

.enrollment-date {
  font-size: 0.75rem;
  color: #f59e0b;
  font-weight: 500;
}

.progress-info {
  min-width: 200px;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: #f3f4f6;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(135deg, #f59e0b, #d97706);
  transition: width 0.3s ease;
}

.progress-details {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.progress-percentage {
  font-weight: 600;
  color: #f59e0b;
}

.progress-status {
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
}

.progress-status.active {
  background: #dbeafe;
  color: #1e40af;
}

.progress-status.completed {
  background: #dcfce7;
  color: #166534;
}

.continue-btn {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.3s ease;
}

.continue-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
}

.goals-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.goal-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  border: 1px solid rgba(245, 158, 11, 0.1);
}

.goal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.goal-header h3 {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.goal-progress {
  font-size: 0.875rem;
  font-weight: 600;
  color: #f59e0b;
}

.goal-bar {
  width: 100%;
  height: 8px;
  background: #f3f4f6;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.goal-fill {
  height: 100%;
  background: linear-gradient(135deg, #f59e0b, #d97706);
  transition: width 0.3s ease;
}

.goal-description {
  font-size: 0.875rem;
  color: #6b7280;
  margin: 0;
}

.achievements-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.achievement-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  border: 1px solid rgba(245, 158, 11, 0.1);
  text-align: center;
  position: relative;
  transition: all 0.3s ease;
}

.achievement-card.earned {
  background: linear-gradient(135deg, #fef3e2, #fed7aa);
  border-color: #f59e0b;
}

.achievement-icon {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.achievement-card h3 {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.achievement-card p {
  font-size: 0.875rem;
  color: #6b7280;
  margin: 0;
}

.earned-badge {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  background: #10b981;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
}

.empty-state {
  text-align: center;
  padding: 3rem 1rem;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.empty-state h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.empty-state p {
  color: #6b7280;
  margin-bottom: 1.5rem;
}

.browse-btn {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s ease;
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
  .progress-view {
    padding: 1rem;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .course-progress-card {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .goals-grid, .achievements-grid {
    grid-template-columns: 1fr;
  }
}
</style>