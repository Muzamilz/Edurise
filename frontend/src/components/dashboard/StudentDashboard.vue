<template>
  <div class="student-dashboard">
    <div class="dashboard-header">
      <div class="student-badge">👨‍🎓 STUDENT</div>
      <h1>Welcome back, {{ fullName }}!</h1>
      <p>Continue your learning journey and discover new skills</p>
    </div>

    <div class="dashboard-content">
      <!-- Student Stats -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon">📚</div>
          <h3>Enrolled Courses</h3>
          <p class="stat-number">{{ enrolledCoursesCount }}</p>
          <span class="stat-change">+2 this month</span>
        </div>
        <div class="stat-card">
          <div class="stat-icon">✅</div>
          <h3>Completed Courses</h3>
          <p class="stat-number">{{ completedCoursesCount }}</p>
          <span class="stat-change">{{ completionRate }}% completion rate</span>
        </div>
        <div class="stat-card">
          <div class="stat-icon">⏱️</div>
          <h3>Hours Learned</h3>
          <p class="stat-number">{{ hoursLearned }}</p>
          <span class="stat-change">This week: {{ weeklyHours }}h</span>
        </div>
        <div class="stat-card">
          <div class="stat-icon">🏆</div>
          <h3>Certificates</h3>
          <p class="stat-number">{{ certificatesCount }}</p>
          <span class="stat-change">{{ certificatesCount > 0 ? 'Great job!' : 'Complete courses to earn' }}</span>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="quick-actions">
        <h2>Quick Actions</h2>
        <div class="action-buttons">
          <router-link to="/courses" class="action-btn primary">
            <span class="btn-icon">🔍</span>
            Browse Courses
          </router-link>
          <router-link to="/student/my-courses" class="action-btn secondary">
            <span class="btn-icon">📖</span>
            My Courses
          </router-link>
          <router-link to="/student/live-classes" class="action-btn secondary">
            <span class="btn-icon">🎥</span>
            Live Classes
          </router-link>
          <router-link to="/student/certificates" class="action-btn secondary">
            <span class="btn-icon">🎓</span>
            Certificates
          </router-link>
          <router-link to="/student/progress" class="action-btn secondary">
            <span class="btn-icon">📊</span>
            Progress
          </router-link>
          <router-link to="/student/wishlist" class="action-btn secondary">
            <span class="btn-icon">❤️</span>
            Wishlist
          </router-link>
        </div>
      </div>

      <!-- Current Courses -->
      <div class="current-courses">
        <div class="section-header">
          <h2>Continue Learning</h2>
          <router-link to="/dashboard/my-courses" class="view-all-link">View All</router-link>
        </div>
        
        <div v-if="currentCourses.length > 0" class="courses-grid">
          <div v-for="course in currentCourses" :key="course.id" class="course-progress-card">
            <div class="course-thumbnail">
              <img :src="course.thumbnail || '/placeholder-course.jpg'" :alt="course.title" />
              <div class="progress-overlay">
                <div class="progress-circle">
                  <span>{{ course.progress }}%</span>
                </div>
              </div>
            </div>
            <div class="course-info">
              <h3>{{ course.title }}</h3>
              <p class="instructor">{{ course.instructor.first_name }} {{ course.instructor.last_name }}</p>
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: course.progress + '%' }"></div>
              </div>
              <div class="course-actions">
                <router-link :to="`/courses/${course.id}/learn`" class="continue-btn">
                  Continue Learning
                </router-link>
              </div>
            </div>
          </div>
        </div>
        
        <div v-else class="empty-state">
          <div class="empty-icon">📚</div>
          <h3>No courses yet</h3>
          <p>Start your learning journey by enrolling in a course</p>
          <router-link to="/courses" class="action-btn primary">Browse Courses</router-link>
        </div>
      </div>

      <!-- Learning Goals -->
      <div class="learning-goals">
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

      <!-- Recommendations -->
      <div class="recommendations">
        <h2>Recommended for You</h2>
        <div class="recommendations-grid">
          <div v-for="course in recommendedCourses" :key="course.id" class="recommendation-card">
            <img :src="course.thumbnail || '/placeholder-course.jpg'" :alt="course.title" />
            <div class="recommendation-info">
              <h3>{{ course.title }}</h3>
              <p class="category">{{ formatCategory(course.category) }}</p>
              <div class="rating">
                <span class="stars">★★★★★</span>
                <span class="rating-text">{{ course.average_rating?.toFixed(1) || 'New' }}</span>
              </div>
              <router-link :to="`/courses/${course.id}`" class="view-course-btn">
                View Course
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAuth } from '@/composables/useAuth'

const { fullName } = useAuth()

// Mock data - replace with real data from API
const enrolledCoursesCount = ref(3)
const completedCoursesCount = ref(1)
const hoursLearned = ref(24)
const weeklyHours = ref(8)
const certificatesCount = ref(1)
const completionRate = computed(() => 
  enrolledCoursesCount.value > 0 ? Math.round((completedCoursesCount.value / enrolledCoursesCount.value) * 100) : 0
)

// Learning goals
const weeklyGoal = ref(10)
const weeklyProgress = ref(8)
const monthlyGoal = ref(3)
const monthlyProgress = ref(1)

// Mock current courses
const currentCourses = ref([
  {
    id: '1',
    title: 'Introduction to Web Development',
    instructor: { first_name: 'John', last_name: 'Doe' },
    thumbnail: '/placeholder-course.jpg',
    progress: 65
  },
  {
    id: '2',
    title: 'Advanced JavaScript Concepts',
    instructor: { first_name: 'Jane', last_name: 'Smith' },
    thumbnail: '/placeholder-course.jpg',
    progress: 30
  }
])

// Mock recommended courses
const recommendedCourses = ref([
  {
    id: '3',
    title: 'React for Beginners',
    category: 'technology',
    thumbnail: '/placeholder-course.jpg',
    average_rating: 4.8
  },
  {
    id: '4',
    title: 'UI/UX Design Fundamentals',
    category: 'design',
    thumbnail: '/placeholder-course.jpg',
    average_rating: 4.6
  }
])

const formatCategory = (category: string) => {
  return category.charAt(0).toUpperCase() + category.slice(1).replace('_', ' ')
}

onMounted(() => {
  // Load student dashboard data
  // useCourseStore().fetchEnrolledCourses()
  // useCourseStore().fetchRecommendedCourses()
})
</script>

<style scoped>
.student-dashboard {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  min-height: 100vh;
}

.dashboard-header {
  margin-bottom: 2rem;
}

.student-badge {
  display: inline-block;
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 1rem;
  box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3);
}

.dashboard-header h1 {
  font-size: 2rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.dashboard-header p {
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
  margin: 0 0 0.25rem 0;
}

.stat-change {
  font-size: 0.75rem;
  color: #10b981;
  font-weight: 500;
}

.quick-actions {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(254, 243, 226, 0.3));
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.1);
  margin-bottom: 2rem;
}

.quick-actions h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 1rem;
}

.action-buttons {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.action-btn {
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  transition: all 0.3s ease;
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  justify-content: center;
}

.action-btn.primary {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  box-shadow: 0 4px 15px rgba(245, 158, 11, 0.3);
}

.action-btn.primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(245, 158, 11, 0.4);
}

.action-btn.secondary {
  background: linear-gradient(135deg, #fef3e2, #fed7aa);
  color: #92400e;
  border: 1px solid rgba(245, 158, 11, 0.3);
}

.action-btn.secondary:hover {
  background: linear-gradient(135deg, #fed7aa, #fdba74);
  border-color: #f59e0b;
}

.btn-icon {
  font-size: 1.1rem;
}

.current-courses, .learning-goals, .recommendations {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(254, 243, 226, 0.3));
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.1);
  margin-bottom: 2rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.section-header h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.view-all-link {
  color: #f59e0b;
  text-decoration: none;
  font-weight: 500;
  font-size: 0.875rem;
}

.view-all-link:hover {
  color: #d97706;
}

.courses-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.course-progress-card {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.1);
  transition: all 0.3s ease;
}

.course-progress-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(245, 158, 11, 0.15);
}

.course-thumbnail {
  position: relative;
  height: 150px;
  overflow: hidden;
}

.course-thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.progress-overlay {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
}

.progress-circle {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: rgba(245, 158, 11, 0.9);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.75rem;
}

.course-info {
  padding: 1rem;
}

.course-info h3 {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.25rem;
}

.instructor {
  font-size: 0.875rem;
  color: #6b7280;
  margin-bottom: 0.75rem;
}

.progress-bar {
  width: 100%;
  height: 6px;
  background: #f3f4f6;
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 1rem;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(135deg, #f59e0b, #d97706);
  transition: width 0.3s ease;
}

.continue-btn {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 500;
  display: inline-block;
  transition: all 0.3s ease;
}

.continue-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
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

.goals-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
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

.recommendations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.recommendation-card {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.1);
  transition: all 0.3s ease;
}

.recommendation-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(245, 158, 11, 0.15);
}

.recommendation-card img {
  width: 100%;
  height: 120px;
  object-fit: cover;
}

.recommendation-info {
  padding: 1rem;
}

.recommendation-info h3 {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.25rem;
}

.category {
  font-size: 0.75rem;
  color: #f59e0b;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.5rem;
}

.rating {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.stars {
  color: #fbbf24;
  font-size: 0.875rem;
}

.rating-text {
  font-size: 0.875rem;
  color: #6b7280;
  font-weight: 500;
}

.view-course-btn {
  background: linear-gradient(135deg, #fef3e2, #fed7aa);
  color: #92400e;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 500;
  display: inline-block;
  border: 1px solid rgba(245, 158, 11, 0.3);
  transition: all 0.3s ease;
}

.view-course-btn:hover {
  background: linear-gradient(135deg, #fed7aa, #fdba74);
  border-color: #f59e0b;
}

/* Responsive */
@media (max-width: 768px) {
  .student-dashboard {
    padding: 1rem;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .action-buttons {
    grid-template-columns: 1fr;
  }
  
  .courses-grid, .goals-grid, .recommendations-grid {
    grid-template-columns: 1fr;
  }
  
  .section-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
}
</style>