<template>
  <div class="teacher-dashboard">
    <div class="dashboard-header">
      <div class="teacher-badge">👨‍🏫 TEACHER</div>
      <h1>Welcome back, {{ fullName }}!</h1>
      <p v-if="isApprovedTeacher">Manage your courses and track student progress</p>
      <p v-else class="approval-notice">
        <span class="approval-icon">⏳</span>
        Your teacher application is pending approval. You'll be able to create courses once approved.
      </p>
    </div>

    <!-- Approval Status Banner -->
    <div v-if="!isApprovedTeacher" class="approval-banner">
      <div class="banner-content">
        <div class="banner-icon">📋</div>
        <div class="banner-text">
          <h3>Teacher Application Status: Pending</h3>
          <p>We're reviewing your application. This usually takes 1-2 business days. You'll receive an email once approved.</p>
        </div>
        <router-link to="/teacher/application-status" class="banner-btn">
          View Application
        </router-link>
      </div>
    </div>

    <div class="dashboard-content">
      <!-- Teacher Stats -->
      <div class="stats-grid">
        <!-- Approved Teacher Stats -->
        <template v-if="isApprovedTeacher">
          <div class="stat-card">
            <div class="stat-icon">📚</div>
            <h3>My Courses</h3>
            <p class="stat-number">{{ coursesCount }}</p>
            <span class="stat-change">{{ publishedCoursesCount }} published, {{ draftCoursesCount }} drafts</span>
          </div>
          <div class="stat-card">
            <div class="stat-icon">👥</div>
            <h3>Total Students</h3>
            <p class="stat-number">{{ totalStudents }}</p>
            <span class="stat-change">+{{ newStudentsThisMonth }} this month</span>
          </div>
          <div class="stat-card">
            <div class="stat-icon">🎥</div>
            <h3>Live Classes</h3>
            <p class="stat-number">{{ liveClassesCount }}</p>
            <span class="stat-change">{{ upcomingClassesCount }} upcoming</span>
          </div>
          <div class="stat-card">
            <div class="stat-icon">💰</div>
            <h3>Total Earnings</h3>
            <p class="stat-number">${{ totalEarnings }}</p>
            <span class="stat-change">${{ monthlyEarnings }} this month</span>
          </div>
          <div class="stat-card">
            <div class="stat-icon">⭐</div>
            <h3>Average Rating</h3>
            <p class="stat-number">{{ averageRating }}</p>
            <span class="stat-change">{{ totalReviews }} reviews</span>
          </div>
        </template>
        
        <!-- Unapproved Teacher Stats -->
        <template v-else>
          <div class="stat-card pending">
            <div class="stat-icon">⏳</div>
            <h3>Application Status</h3>
            <p class="stat-number">Pending</p>
            <span class="stat-change">Awaiting approval</span>
          </div>
          <div class="stat-card pending">
            <div class="stat-icon">📋</div>
            <h3>Profile Completion</h3>
            <p class="stat-number">85%</p>
            <span class="stat-change">Almost ready!</span>
          </div>
          <div class="stat-card pending">
            <div class="stat-icon">📚</div>
            <h3>Courses Ready</h3>
            <p class="stat-number">0</p>
            <span class="stat-change">Create after approval</span>
          </div>
          <div class="stat-card pending">
            <div class="stat-icon">🎯</div>
            <h3>Teaching Goals</h3>
            <p class="stat-number">Set</p>
            <span class="stat-change">Ready to teach!</span>
          </div>
        </template>
      </div>

      <!-- Quick Actions -->
      <div class="quick-actions">
        <h2>Quick Actions</h2>
        <div class="action-buttons">
          <!-- Approved Teacher Actions -->
          <template v-if="isApprovedTeacher">
            <router-link to="/teacher/courses/create" class="action-btn primary">
              <span class="btn-icon">➕</span>
              Create New Course
            </router-link>
            <router-link to="/teacher/courses" class="action-btn secondary">
              <span class="btn-icon">📖</span>
              Manage Courses
            </router-link>
            <router-link to="/teacher/live-classes" class="action-btn secondary">
              <span class="btn-icon">🎥</span>
              Live Classes
            </router-link>
            <router-link to="/teacher/students" class="action-btn secondary">
              <span class="btn-icon">👥</span>
              My Students
            </router-link>
            <router-link to="/teacher/analytics" class="action-btn secondary">
              <span class="btn-icon">📊</span>
              Analytics
            </router-link>
            <router-link to="/teacher/earnings" class="action-btn secondary">
              <span class="btn-icon">💳</span>
              Earnings
            </router-link>
          </template>
          
          <!-- Unapproved Teacher Actions -->
          <template v-else>
            <router-link to="/teacher/application-status" class="action-btn primary">
              <span class="btn-icon">📋</span>
              Application Status
            </router-link>
            <router-link to="/teacher/profile" class="action-btn secondary">
              <span class="btn-icon">👤</span>
              Complete Profile
            </router-link>
            <router-link to="/courses" class="action-btn secondary">
              <span class="btn-icon">📚</span>
              Browse Courses
            </router-link>
            <router-link to="/teacher/resources" class="action-btn secondary">
              <span class="btn-icon">📖</span>
              Teaching Resources
            </router-link>
          </template>
        </div>
      </div>

      <!-- Recent Courses -->
      <div class="recent-courses">
        <div class="section-header">
          <h2>My Courses</h2>
          <router-link to="/teacher/courses" class="view-all-link">View All</router-link>
        </div>
        
        <div v-if="recentCourses.length > 0" class="courses-grid">
          <div v-for="course in recentCourses" :key="course.id" class="course-card">
            <div class="course-thumbnail">
              <img :src="course.thumbnail || '/placeholder-course.jpg'" :alt="course.title" />
              <div class="course-status" :class="course.status">
                {{ formatStatus(course.status) }}
              </div>
            </div>
            <div class="course-info">
              <h3>{{ course.title }}</h3>
              <p class="course-category">{{ formatCategory(course.category) }}</p>
              <div class="course-stats">
                <span class="stat">
                  <span class="stat-icon">👥</span>
                  {{ course.enrollments }} students
                </span>
                <span class="stat">
                  <span class="stat-icon">⭐</span>
                  {{ course.rating || 'No ratings' }}
                </span>
              </div>
              <div class="course-actions">
                <router-link :to="`/teacher/courses/${course.id}/edit`" class="edit-btn">
                  Edit
                </router-link>
                <router-link :to="`/courses/${course.id}`" class="view-btn">
                  View
                </router-link>
              </div>
            </div>
          </div>
        </div>
        
        <div v-else class="empty-state">
          <div class="empty-icon">📚</div>
          <h3>No courses yet</h3>
          <p v-if="isApprovedTeacher">Start creating your first course to share your knowledge</p>
          <p v-else>Once approved, you'll be able to create and manage courses</p>
          <router-link 
            v-if="isApprovedTeacher" 
            to="/teacher/courses/create" 
            class="action-btn primary"
          >
            Create Your First Course
          </router-link>
        </div>
      </div>

      <!-- Recent Activity -->
      <div v-if="isApprovedTeacher" class="recent-activity">
        <h2>Recent Activity</h2>
        <div class="activity-list">
          <div v-for="activity in recentActivity" :key="activity.id" class="activity-item">
            <div class="activity-icon" :class="activity.type">
              {{ getActivityIcon(activity.type) }}
            </div>
            <div class="activity-content">
              <p class="activity-text">{{ activity.text }}</p>
              <span class="activity-time">{{ formatTime(activity.timestamp) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Performance Metrics -->
      <div v-if="isApprovedTeacher" class="performance-metrics">
        <h2>This Month's Performance</h2>
        <div class="metrics-grid">
          <div class="metric-card">
            <h3>Course Completion Rate</h3>
            <div class="metric-value">{{ completionRate }}%</div>
            <div class="metric-bar">
              <div class="metric-fill" :style="{ width: completionRate + '%' }"></div>
            </div>
          </div>
          
          <div class="metric-card">
            <h3>Student Satisfaction</h3>
            <div class="metric-value">{{ satisfactionRate }}%</div>
            <div class="metric-bar">
              <div class="metric-fill" :style="{ width: satisfactionRate + '%' }"></div>
            </div>
          </div>
          
          <div class="metric-card">
            <h3>Engagement Rate</h3>
            <div class="metric-value">{{ engagementRate }}%</div>
            <div class="metric-bar">
              <div class="metric-fill" :style="{ width: engagementRate + '%' }"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuth } from '@/composables/useAuth'

const { fullName, isApprovedTeacher } = useAuth()

// Mock data - replace with real data from API
// These should come from the backend Course and Enrollment models
const coursesCount = ref(isApprovedTeacher.value ? 5 : 0)
const publishedCoursesCount = ref(isApprovedTeacher.value ? 3 : 0)
const draftCoursesCount = ref(isApprovedTeacher.value ? 2 : 0)
const totalStudents = ref(isApprovedTeacher.value ? 127 : 0)
const newStudentsThisMonth = ref(isApprovedTeacher.value ? 23 : 0)
const totalEarnings = ref(isApprovedTeacher.value ? 2450 : 0)
const monthlyEarnings = ref(isApprovedTeacher.value ? 680 : 0)
const averageRating = ref(isApprovedTeacher.value ? 4.8 : 0)
const totalReviews = ref(isApprovedTeacher.value ? 45 : 0)
const liveClassesCount = ref(isApprovedTeacher.value ? 8 : 0)
const upcomingClassesCount = ref(isApprovedTeacher.value ? 3 : 0)

// Performance metrics
const completionRate = ref(78)
const satisfactionRate = ref(92)
const engagementRate = ref(85)

// Mock recent courses
const recentCourses = ref([
  {
    id: '1',
    title: 'Advanced JavaScript Concepts',
    category: 'technology',
    thumbnail: '/placeholder-course.jpg',
    status: 'published',
    enrollments: 45,
    rating: 4.8
  },
  {
    id: '2',
    title: 'React Development Masterclass',
    category: 'technology',
    thumbnail: '/placeholder-course.jpg',
    status: 'draft',
    enrollments: 0,
    rating: null
  },
  {
    id: '3',
    title: 'Web Design Fundamentals',
    category: 'design',
    thumbnail: '/placeholder-course.jpg',
    status: 'published',
    enrollments: 32,
    rating: 4.6
  }
])

// Mock recent activity
const recentActivity = ref([
  {
    id: '1',
    type: 'enrollment',
    text: 'New student enrolled in "Advanced JavaScript Concepts"',
    timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000) // 2 hours ago
  },
  {
    id: '2',
    type: 'review',
    text: 'Received a 5-star review for "Web Design Fundamentals"',
    timestamp: new Date(Date.now() - 5 * 60 * 60 * 1000) // 5 hours ago
  },
  {
    id: '3',
    type: 'completion',
    text: 'Student completed "React Development Masterclass"',
    timestamp: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000) // 1 day ago
  }
])

const formatCategory = (category: string) => {
  return category.charAt(0).toUpperCase() + category.slice(1).replace('_', ' ')
}

const formatStatus = (status: string) => {
  return status.charAt(0).toUpperCase() + status.slice(1)
}

const getActivityIcon = (type: string) => {
  const icons = {
    enrollment: '👥',
    review: '⭐',
    completion: '✅',
    purchase: '💰'
  }
  return icons[type as keyof typeof icons] || '📝'
}

const formatTime = (timestamp: Date) => {
  const now = new Date()
  const diff = now.getTime() - timestamp.getTime()
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const days = Math.floor(hours / 24)
  
  if (days > 0) {
    return `${days} day${days > 1 ? 's' : ''} ago`
  } else if (hours > 0) {
    return `${hours} hour${hours > 1 ? 's' : ''} ago`
  } else {
    return 'Just now'
  }
}

onMounted(() => {
  // Load teacher dashboard data
  // teacherStore.fetchTeacherStats()
  // teacherStore.fetchRecentCourses()
  // teacherStore.fetchRecentActivity()
})
</script>

<style scoped>
.teacher-dashboard {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  min-height: 100vh;
}

.dashboard-header {
  margin-bottom: 2rem;
}

.teacher-badge {
  display: inline-block;
  background: linear-gradient(135deg, #059669, #047857);
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 1rem;
  box-shadow: 0 4px 15px rgba(5, 150, 105, 0.3);
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

.approval-notice {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #f59e0b !important;
  font-weight: 500;
}

.approval-icon {
  font-size: 1.2rem;
}

.approval-banner {
  background: linear-gradient(135deg, #fef3e2, #fed7aa);
  border: 1px solid rgba(245, 158, 11, 0.3);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.banner-content {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.banner-icon {
  font-size: 2rem;
  flex-shrink: 0;
}

.banner-text {
  flex: 1;
}

.banner-text h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #92400e;
  margin-bottom: 0.25rem;
}

.banner-text p {
  color: #92400e;
  font-size: 0.875rem;
  margin: 0;
}

.banner-btn {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.banner-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
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

.stat-card.pending {
  background: linear-gradient(135deg, rgba(251, 191, 36, 0.1), rgba(245, 158, 11, 0.1));
  border: 1px solid rgba(251, 191, 36, 0.3);
}

.stat-card.pending .stat-number {
  color: #d97706;
}

.stat-card.pending .stat-change {
  color: #92400e;
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

.quick-actions, .recent-courses, .recent-activity, .performance-metrics {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(254, 243, 226, 0.3));
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.1);
  margin-bottom: 2rem;
}

.quick-actions h2, .recent-courses h2, .recent-activity h2, .performance-metrics h2 {
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

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.section-header h2 {
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

.course-card {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.1);
  transition: all 0.3s ease;
}

.course-card:hover {
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

.course-status {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.course-status.published {
  background: #10b981;
  color: white;
}

.course-status.draft {
  background: #f59e0b;
  color: white;
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

.course-category {
  font-size: 0.75rem;
  color: #f59e0b;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.75rem;
}

.course-stats {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.stat {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.875rem;
  color: #6b7280;
}

.stat-icon {
  font-size: 1rem;
}

.course-actions {
  display: flex;
  gap: 0.5rem;
}

.edit-btn, .view-btn {
  padding: 0.5rem 1rem;
  border-radius: 6px;
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.3s ease;
  flex: 1;
  text-align: center;
}

.edit-btn {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
}

.edit-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
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

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.activity-item {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1rem;
  background: white;
  border-radius: 8px;
  border: 1px solid rgba(245, 158, 11, 0.1);
}

.activity-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  flex-shrink: 0;
}

.activity-icon.enrollment {
  background: rgba(16, 185, 129, 0.1);
}

.activity-icon.review {
  background: rgba(251, 191, 36, 0.1);
}

.activity-icon.completion {
  background: rgba(34, 197, 94, 0.1);
}

.activity-content {
  flex: 1;
}

.activity-text {
  font-size: 0.875rem;
  color: #1f2937;
  margin-bottom: 0.25rem;
}

.activity-time {
  font-size: 0.75rem;
  color: #6b7280;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

.metric-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  border: 1px solid rgba(245, 158, 11, 0.1);
  text-align: center;
}

.metric-card h3 {
  font-size: 0.875rem;
  font-weight: 500;
  color: #6b7280;
  margin-bottom: 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.metric-value {
  font-size: 2rem;
  font-weight: 700;
  color: #f59e0b;
  margin-bottom: 1rem;
}

.metric-bar {
  width: 100%;
  height: 6px;
  background: #f3f4f6;
  border-radius: 3px;
  overflow: hidden;
}

.metric-fill {
  height: 100%;
  background: linear-gradient(135deg, #f59e0b, #d97706);
  transition: width 0.3s ease;
}

/* Responsive */
@media (max-width: 768px) {
  .teacher-dashboard {
    padding: 1rem;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .action-buttons {
    grid-template-columns: 1fr;
  }
  
  .courses-grid, .metrics-grid {
    grid-template-columns: 1fr;
  }
  
  .section-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .banner-content {
    flex-direction: column;
    text-align: center;
  }
  
  .course-actions {
    flex-direction: column;
  }
}
</style>