<template>
  <div class="admin-dashboard">
    <div class="dashboard-header">
      <div class="admin-badge">🏢 ORG ADMIN</div>
      <h1>Organization Dashboard</h1>
      <p>Manage your organization users, courses, and settings</p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>Loading admin dashboard...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-state">
      <div class="error-icon">⚠️</div>
      <h3>Unable to load dashboard</h3>
      <p>{{ error.message }}</p>
      <button @click="handleRetry" class="retry-btn">
        Try Again
      </button>
    </div>

    <div v-else class="dashboard-content">
      <!-- Admin Stats -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon">👥</div>
          <h3>Total Users</h3>
          <p class="stat-number">{{ totalUsers }}</p>
          <span class="stat-change">{{ totalStudents }} students, {{ totalTeachers }} teachers</span>
        </div>
        <div class="stat-card">
          <div class="stat-icon">👨‍🏫</div>
          <h3>Teacher Approvals</h3>
          <p class="stat-number">{{ pendingTeachersCount }}</p>
          <span class="stat-change">Pending review</span>
        </div>
        <div class="stat-card">
          <div class="stat-icon">📚</div>
          <h3>Course Management</h3>
          <p class="stat-number">{{ totalCourses }}</p>
          <span class="stat-change">{{ publishedCourses }} published, {{ draftCourses }} drafts</span>
        </div>
        <div class="stat-card">
          <div class="stat-icon">🎥</div>
          <h3>Live Classes</h3>
          <p class="stat-number">{{ liveClassesActive }}</p>
          <span class="stat-change">Currently active</span>
        </div>
        <div class="stat-card">
          <div class="stat-icon">📊</div>
          <h3>Enrollments</h3>
          <p class="stat-number">{{ activeEnrollments }}</p>
          <span class="stat-change">{{ completedEnrollments }} completed</span>
        </div>
        <div class="stat-card">
          <div class="stat-icon">💰</div>
          <h3>Platform Revenue</h3>
          <p class="stat-number">${{ totalRevenue }}</p>
          <span class="stat-change">${{ monthlyRevenue }} this month</span>
        </div>
        <div class="stat-card">
          <div class="stat-icon">🛡️</div>
          <h3>Content Moderation</h3>
          <p class="stat-number">{{ contentModerationQueue }}</p>
          <span class="stat-change">Items pending review</span>
        </div>
        <div class="stat-card">
          <div class="stat-icon">📈</div>
          <h3>Growth Rate</h3>
          <p class="stat-number">{{ enrollmentGrowth }}%</p>
          <span class="stat-change">Monthly growth</span>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="quick-actions">
        <h2>Quick Actions</h2>
        <div class="action-buttons">
          <router-link to="/admin/users" class="action-btn primary">
            <span class="btn-icon">👥</span>
            User Management
          </router-link>
          <router-link to="/admin/teachers/pending" class="action-btn secondary">
            <span class="btn-icon">👨‍🏫</span>
            Teacher Approvals
          </router-link>
          <router-link to="/admin/courses" class="action-btn secondary">
            <span class="btn-icon">📚</span>
            Course Management
          </router-link>
          <router-link to="/admin/content-moderation" class="action-btn secondary">
            <span class="btn-icon">🛡️</span>
            Content Moderation
          </router-link>
          <router-link to="/admin/analytics" class="action-btn secondary">
            <span class="btn-icon">📊</span>
            Platform Analytics
          </router-link>
          <router-link to="/admin/financial" class="action-btn secondary">
            <span class="btn-icon">💰</span>
            Financial Reports
          </router-link>
          <router-link to="/admin/organization" class="action-btn secondary">
            <span class="btn-icon">🏢</span>
            Organization Settings
          </router-link>
          <router-link to="/admin/system" class="action-btn secondary">
            <span class="btn-icon">⚙️</span>
            System Settings
          </router-link>
          <router-link to="/admin/categories" class="action-btn secondary">
            <span class="btn-icon">📂</span>
            Category Management
          </router-link>
          <router-link to="/admin/subscription-plans" class="action-btn secondary">
            <span class="btn-icon">💳</span>
            Subscription Plans
          </router-link>
        </div>
      </div>

      <!-- Pending Approvals -->
      <div class="pending-approvals">
        <div class="section-header">
          <h2>Pending Teacher Approvals</h2>
          <router-link to="/admin/teachers" class="view-all-link">View All</router-link>
        </div>
        
        <div v-if="pendingTeachers.length > 0" class="approvals-list">
          <div v-for="teacher in pendingTeachers" :key="teacher.id" class="approval-card">
            <div class="teacher-info">
              <div class="teacher-avatar">
                <img :src="teacher.avatar || '/default-avatar.jpg'" :alt="teacher.name" />
              </div>
              <div class="teacher-details">
                <h3>{{ teacher.name }}</h3>
                <p class="teacher-email">{{ teacher.email }}</p>
                <p class="application-date">Applied {{ formatDate(teacher.appliedAt) }}</p>
              </div>
            </div>
            <div class="teacher-qualifications">
              <p><strong>Experience:</strong> {{ teacher.experience }}</p>
              <p><strong>Expertise:</strong> {{ teacher.expertise }}</p>
            </div>
            <div class="approval-actions">
              <button @click="approveTeacher(teacher.id)" class="approve-btn">
                Approve
              </button>
              <button @click="rejectTeacher(teacher.id)" class="reject-btn">
                Reject
              </button>
              <router-link :to="`/admin/teachers/${teacher.id}`" class="review-btn">
                Review
              </router-link>
            </div>
          </div>
        </div>
        
        <div v-else class="empty-state">
          <div class="empty-icon">✅</div>
          <h3>No pending approvals</h3>
          <p>All teacher applications have been reviewed</p>
        </div>
      </div>

      <!-- Recent Activity -->
      <div class="recent-activity">
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
            <div class="activity-status" :class="activity.status">
              {{ activity.status }}
            </div>
          </div>
        </div>
      </div>

      <!-- System Health -->
      <div class="system-health">
        <h2>System Health</h2>
        <div class="health-grid">
          <div class="health-card">
            <div class="health-header">
              <h3>Server Status</h3>
              <div class="health-status" :class="systemHealth.serverStatus === 'healthy' ? 'online' : 'warning'">
                {{ systemHealth.serverStatus || 'Unknown' }}
              </div>
            </div>
            <div class="health-metrics">
              <div class="metric">
                <span class="metric-label">Response Time</span>
                <span class="metric-value">{{ systemHealth.apiResponseTime || 0 }}ms</span>
              </div>
            </div>
          </div>
          
          <div class="health-card">
            <div class="health-header">
              <h3>Database</h3>
              <div class="health-status" :class="systemHealth.databaseStatus === 'healthy' ? 'online' : 'warning'">
                {{ systemHealth.databaseStatus || 'Unknown' }}
              </div>
            </div>
            <div class="health-metrics">
              <div class="metric">
                <span class="metric-label">Status</span>
                <span class="metric-value">{{ systemHealth.databaseStatus || 'Unknown' }}</span>
              </div>
            </div>
          </div>
          
          <div class="health-card">
            <div class="health-header">
              <h3>Cache</h3>
              <div class="health-status" :class="systemHealth.cacheStatus === 'healthy' ? 'online' : 'warning'">
                {{ systemHealth.cacheStatus || 'Unknown' }}
              </div>
            </div>
            <div class="health-metrics">
              <div class="metric">
                <span class="metric-label">Status</span>
                <span class="metric-value">{{ systemHealth.cacheStatus || 'Unknown' }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Platform Analytics -->
      <div class="platform-analytics">
        <h2>Platform Analytics</h2>
        <div class="analytics-grid">
          <div class="analytics-card">
            <h3>User Growth</h3>
            <div class="analytics-chart">
              <div class="chart-placeholder">
                📈 User growth chart would go here
              </div>
            </div>
          </div>
          
          <div class="analytics-card">
            <h3>Course Popularity</h3>
            <div class="popularity-list">
              <div v-for="course in popularCourses" :key="course.id" class="popularity-item">
                <span class="course-name">{{ course.title }}</span>
                <span class="enrollment-count">{{ course.enrollments }} enrollments</span>
              </div>
            </div>
          </div>
          
          <div class="analytics-card">
            <h3>Revenue Trends</h3>
            <div class="revenue-metrics">
              <div class="revenue-item">
                <span class="revenue-label">This Month</span>
                <span class="revenue-value">${{ monthlyRevenue }}</span>
                <span class="revenue-change positive">+12%</span>
              </div>
              <div class="revenue-item">
                <span class="revenue-label">Last Month</span>
                <span class="revenue-value">${{ lastMonthRevenue }}</span>
                <span class="revenue-change positive">+8%</span>
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
import { useDashboardData } from '@/composables/useDashboardData'
import { useErrorHandler } from '@/composables/useErrorHandler'
import { useApiMutation } from '@/composables/useApiData'
import { api } from '@/services/api'

const { adminData } = useDashboardData()
const { handleApiError } = useErrorHandler()

// Real data from API
const dashboardData = computed(() => adminData.data.value)
const loading = computed(() => adminData.loading.value)
const error = computed(() => adminData.error.value)

// Computed properties for admin stats
const totalUsers = computed(() => 
  dashboardData.value?.userStats?.totalUsers || 0
)

const totalStudents = computed(() => 
  dashboardData.value?.userStats?.studentCount || 0
)

const totalTeachers = computed(() => 
  dashboardData.value?.userStats?.teacherCount || 0
)

const pendingTeachersCount = computed(() => {
  // This would need to be added to the admin dashboard API
  return 0 // Placeholder - would come from backend
})

const totalCourses = computed(() => 
  dashboardData.value?.courseStats?.totalCourses || 0
)

const publishedCourses = computed(() => 
  dashboardData.value?.courseStats?.publishedCourses || 0
)

const draftCourses = computed(() => 
  totalCourses.value - publishedCourses.value
)

const totalRevenue = computed(() => 
  Math.round(dashboardData.value?.revenueStats?.totalRevenue || 0)
)

const monthlyRevenue = computed(() => 
  Math.round(dashboardData.value?.revenueStats?.monthlyRevenue || 0)
)

const lastMonthRevenue = computed(() => {
  const currentRevenue = monthlyRevenue.value
  const growth = dashboardData.value?.revenueStats?.revenueGrowth || 0
  return Math.round(currentRevenue / (1 + growth / 100))
})

const activeEnrollments = computed(() => 
  dashboardData.value?.courseStats?.totalEnrollments || 0
)

const completedEnrollments = computed(() => {
  const total = activeEnrollments.value
  const completionRate = dashboardData.value?.courseStats?.completionRate || 0
  return Math.round(total * (completionRate / 100))
})

const enrollmentGrowth = computed(() => 
  Math.round(dashboardData.value?.revenueStats?.revenueGrowth || 0)
)

const liveClassesActive = computed(() => {
  // This would need to be added to admin dashboard API
  return 0 // Placeholder
})

const contentModerationQueue = computed(() => {
  // This would need to be added to admin dashboard API
  return 0 // Placeholder
})

// System health data
const systemHealth = computed(() => 
  dashboardData.value?.systemHealth || {
    serverStatus: 'healthy',
    databaseStatus: 'healthy',
    cacheStatus: 'healthy',
    apiResponseTime: 0
  }
)

// Recent activity
const recentActivity = computed(() => {
  const activities: any[] = []
  
  // Add recent enrollments as activities
  const recentEnrollments = (dashboardData.value?.recentActivity as any)?.recent_enrollments || []
  recentEnrollments.forEach((enrollment: any) => {
    activities.push({
      id: `enrollment_${enrollment.student_name}`,
      type: 'enrollment',
      text: `${enrollment.student_name} enrolled in "${enrollment.course_title}"`,
      timestamp: new Date(enrollment.enrolled_at),
      status: 'completed'
    })
  })
  
  // Add recent courses as activities
  const recentCourses = (dashboardData.value?.recentActivity as any)?.recent_courses || []
  recentCourses.forEach((course: any) => {
    activities.push({
      id: `course_${course.id}`,
      type: 'course',
      text: `New course "${course.title}" created by ${course.instructor_name}`,
      timestamp: new Date(course.created_at),
      status: course.is_public ? 'completed' : 'pending'
    })
  })
  
  // Sort by timestamp (most recent first)
  return activities.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime()).slice(0, 5)
})

// Top performing courses
const popularCourses = computed(() => 
  dashboardData.value?.topPerformingCourses?.slice(0, 4).map(course => ({
    id: course.id,
    title: course.title,
    enrollments: course.enrollmentCount
  })) || []
)

// Mock pending teachers (this would come from a separate API endpoint)
interface PendingTeacher {
  id: string
  name: string
  email: string
  avatar?: string
  appliedAt: string
  experience: string
  expertise: string
}

const pendingTeachers = computed((): PendingTeacher[] => [
  // This would be fetched from /api/v1/teacher-approvals/ endpoint
])

// Teacher approval mutations
const { mutate: approveTeacherMutation } = useApiMutation(
  (teacherId: string) => api.patch(`/teacher-approvals/${teacherId}/`, { status: 'approved' }),
  {
    onSuccess: () => {
      console.log('Teacher approved successfully')
      // Refresh dashboard data
      adminData.refresh()
    },
    onError: (error) => {
      handleApiError(error, { context: { action: 'approve_teacher' } })
    }
  }
)

const { mutate: rejectTeacherMutation } = useApiMutation(
  (teacherId: string) => api.patch(`/teacher-approvals/${teacherId}/`, { status: 'rejected' }),
  {
    onSuccess: () => {
      console.log('Teacher rejected successfully')
      // Refresh dashboard data
      adminData.refresh()
    },
    onError: (error) => {
      handleApiError(error, { context: { action: 'reject_teacher' } })
    }
  }
)

const approveTeacher = async (teacherId: string) => {
  try {
    await approveTeacherMutation(teacherId)
  } catch (error) {
    // Error handling is done in the mutation
  }
}

const rejectTeacher = async (teacherId: string) => {
  try {
    await rejectTeacherMutation(teacherId)
  } catch (error) {
    // Error handling is done in the mutation
  }
}

// Utility functions
const formatDate = (date: Date | string) => {
  const dateObj = typeof date === 'string' ? new Date(date) : date
  const now = new Date()
  const diff = now.getTime() - dateObj.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (days === 0) return 'today'
  if (days === 1) return 'yesterday'
  return `${days} days ago`
}

const getActivityIcon = (type: string) => {
  const icons = {
    user: '👤',
    course: '📚',
    payment: '💳',
    system: '⚙️',
    enrollment: '📝',
    completion: '✅'
  }
  return icons[type as keyof typeof icons] || '📝'
}

const formatTime = (timestamp: Date | string) => {
  const dateObj = typeof timestamp === 'string' ? new Date(timestamp) : timestamp
  const now = new Date()
  const diff = now.getTime() - dateObj.getTime()
  const hours = Math.floor(diff / (1000 * 60 * 60))
  
  if (hours < 1) return 'Just now'
  if (hours === 1) return '1 hour ago'
  return `${hours} hours ago`
}

const handleRetry = async () => {
  try {
    await adminData.refresh()
  } catch (err) {
    handleApiError(err as any, { 
      context: { action: 'retry_admin_dashboard_load' } 
    })
  }
}
</script>

<style scoped>
.admin-dashboard {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  min-height: 100vh;
}

.dashboard-header {
  margin-bottom: 2rem;
  position: relative;
}

.admin-badge {
  display: inline-block;
  background: linear-gradient(135deg, #ea580c, #c2410c);
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 1rem;
  box-shadow: 0 4px 15px rgba(234, 88, 12, 0.3);
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

.quick-actions, .pending-approvals, .recent-activity, .system-health, .platform-analytics {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(254, 243, 226, 0.3));
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.1);
  margin-bottom: 2rem;
}

.quick-actions h2, .pending-approvals h2, .recent-activity h2, .system-health h2, .platform-analytics h2 {
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

.approvals-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.approval-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  border: 1px solid rgba(245, 158, 11, 0.1);
  display: grid;
  grid-template-columns: 1fr 1fr auto;
  gap: 1.5rem;
  align-items: center;
}

.teacher-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.teacher-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
}

.teacher-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.teacher-details h3 {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.25rem;
}

.teacher-email {
  font-size: 0.875rem;
  color: #6b7280;
  margin-bottom: 0.25rem;
}

.application-date {
  font-size: 0.75rem;
  color: #f59e0b;
  font-weight: 500;
}

.teacher-qualifications p {
  font-size: 0.875rem;
  color: #374151;
  margin-bottom: 0.5rem;
}

.approval-actions {
  display: flex;
  gap: 0.5rem;
}

.approve-btn, .reject-btn, .review-btn {
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  border: none;
  cursor: pointer;
  text-decoration: none;
  transition: all 0.3s ease;
}

.approve-btn {
  background: #10b981;
  color: white;
}

.approve-btn:hover {
  background: #059669;
}

.reject-btn {
  background: #ef4444;
  color: white;
}

.reject-btn:hover {
  background: #dc2626;
}

.review-btn {
  background: linear-gradient(135deg, #fef3e2, #fed7aa);
  color: #92400e;
  border: 1px solid rgba(245, 158, 11, 0.3);
  display: inline-block;
}

.review-btn:hover {
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
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.activity-item {
  display: flex;
  align-items: center;
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
  background: rgba(245, 158, 11, 0.1);
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

.activity-status {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
}

.activity-status.completed {
  background: #dcfce7;
  color: #166534;
}

.activity-status.pending {
  background: #fef3c7;
  color: #92400e;
}

.health-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.health-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  border: 1px solid rgba(245, 158, 11, 0.1);
}

.health-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.health-header h3 {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.health-status {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
}

.health-status.online {
  background: #dcfce7;
  color: #166534;
}

.health-status.warning {
  background: #fef3c7;
  color: #92400e;
}

.health-metrics {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.metric {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.metric-label {
  font-size: 0.875rem;
  color: #6b7280;
}

.metric-value {
  font-size: 0.875rem;
  font-weight: 600;
  color: #1f2937;
}

.analytics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.analytics-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  border: 1px solid rgba(245, 158, 11, 0.1);
}

.analytics-card h3 {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 1rem;
}

.chart-placeholder {
  height: 150px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f9fafb;
  border-radius: 6px;
  color: #6b7280;
  font-size: 0.875rem;
}

.popularity-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.popularity-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: #f9fafb;
  border-radius: 6px;
}

.course-name {
  font-size: 0.875rem;
  color: #1f2937;
  font-weight: 500;
}

.enrollment-count {
  font-size: 0.875rem;
  color: #f59e0b;
  font-weight: 600;
}

.revenue-metrics {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.revenue-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: #f9fafb;
  border-radius: 6px;
}

.revenue-label {
  font-size: 0.875rem;
  color: #6b7280;
}

.revenue-value {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
}

.revenue-change {
  font-size: 0.75rem;
  font-weight: 500;
}

.revenue-change.positive {
  color: #10b981;
}

/* Loading and Error States */
.loading-state, .error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(254, 243, 226, 0.3));
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.1);
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

.error-state .error-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.error-state h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #dc2626;
  margin-bottom: 0.5rem;
}

.error-state p {
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
  .admin-dashboard {
    padding: 1rem;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .action-buttons {
    grid-template-columns: 1fr;
  }
  
  .approval-card {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .approval-actions {
    justify-content: center;
  }
  
  .health-grid, .analytics-grid {
    grid-template-columns: 1fr;
  }
  
  .section-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
}
</style>