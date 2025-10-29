<template>
  <div class="students-view">
    <div class="page-header">
      <h1>My Students</h1>
      <p>Manage and track your students' progress</p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>Loading your students...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-state">
      <div class="error-icon">⚠️</div>
      <h3>Failed to load students</h3>
      <p>{{ error.message }}</p>
      <button @click="handleRetry" class="retry-btn">Try Again</button>
    </div>

    <!-- Students Content -->
    <div v-else class="students-content">
      <!-- Quick Stats -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon">👥</div>
          <h3>Total Students</h3>
          <p class="stat-number">{{ totalStudents }}</p>
        </div>
        <div class="stat-card">
          <div class="stat-icon">📚</div>
          <h3>Active Enrollments</h3>
          <p class="stat-number">{{ activeEnrollments }}</p>
        </div>
        <div class="stat-card">
          <div class="stat-icon">✅</div>
          <h3>Completed Courses</h3>
          <p class="stat-number">{{ completedEnrollments }}</p>
        </div>
        <div class="stat-card">
          <div class="stat-icon">📊</div>
          <h3>Average Progress</h3>
          <p class="stat-number">{{ averageProgress }}%</p>
        </div>
      </div>

      <!-- Filters and Search -->
      <div class="filters-section">
        <div class="search-bar">
          <input 
            type="text" 
            v-model="searchQuery" 
            placeholder="Search students by name or email..."
            class="search-input"
          >
          <span class="search-icon">🔍</span>
        </div>
        
        <div class="filters">
          <select v-model="courseFilter" @change="applyFilters" class="filter-select">
            <option value="">All Courses</option>
            <option v-for="course in teacherCourses" :key="course.id" :value="course.id">
              {{ course.title }}
            </option>
          </select>
          
          <select v-model="statusFilter" @change="applyFilters" class="filter-select">
            <option value="">All Status</option>
            <option value="active">Active</option>
            <option value="completed">Completed</option>
            <option value="dropped">Dropped</option>
          </select>
          
          <select v-model="sortBy" @change="applyFilters" class="filter-select">
            <option value="name">Sort by Name</option>
            <option value="progress">Sort by Progress</option>
            <option value="enrolled_date">Sort by Enrollment Date</option>
            <option value="last_activity">Sort by Last Activity</option>
          </select>
        </div>
      </div>

      <!-- Students List -->
      <div v-if="filteredStudents.length > 0" class="students-list">
        <div v-for="student in filteredStudents" :key="`${student.id}-${student.course_id}`" class="student-card">
          <div class="student-header">
            <div class="student-info">
              <div class="student-avatar">
                <img :src="student.avatar || '/default-avatar.jpg'" :alt="student.name" />
              </div>
              <div class="student-details">
                <h3>{{ student.name }}</h3>
                <p class="student-email">{{ student.email }}</p>
                <p class="course-name">{{ student.course_title }}</p>
              </div>
            </div>
            <div class="student-status">
              <span class="status-badge" :class="student.status">
                {{ formatStatus(student.status) }}
              </span>
            </div>
          </div>

          <div class="student-progress">
            <div class="progress-header">
              <span class="progress-label">Course Progress</span>
              <span class="progress-percentage">{{ student.progress_percentage }}%</span>
            </div>
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: student.progress_percentage + '%' }"></div>
            </div>
          </div>

          <div class="student-stats">
            <div class="stat-item">
              <span class="stat-icon">📅</span>
              <div class="stat-content">
                <span class="stat-label">Enrolled</span>
                <span class="stat-value">{{ formatDate(student.enrolled_at) }}</span>
              </div>
            </div>
            <div class="stat-item">
              <span class="stat-icon">⏰</span>
              <div class="stat-content">
                <span class="stat-label">Last Activity</span>
                <span class="stat-value">{{ formatRelativeTime(student.last_accessed) }}</span>
              </div>
            </div>
            <div class="stat-item">
              <span class="stat-icon">🎯</span>
              <div class="stat-content">
                <span class="stat-label">Completion Rate</span>
                <span class="stat-value">{{ calculateCompletionRate(student) }}%</span>
              </div>
            </div>
            <div class="stat-item" v-if="student.grade">
              <span class="stat-icon">📊</span>
              <div class="stat-content">
                <span class="stat-label">Grade</span>
                <span class="stat-value">{{ student.grade }}%</span>
              </div>
            </div>
          </div>

          <div class="student-actions">
            <button @click="viewStudentDetails(student)" class="view-btn">
              <span class="btn-icon">👁️</span>
              View Details
            </button>
            <button @click="sendMessage(student)" class="message-btn">
              <span class="btn-icon">💬</span>
              Send Message
            </button>
            <button @click="viewProgress(student)" class="progress-btn">
              <span class="btn-icon">📈</span>
              View Progress
            </button>
            <button @click="generateReport(student)" class="report-btn">
              <span class="btn-icon">📄</span>
              Generate Report
            </button>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="empty-state">
        <div class="empty-icon">👥</div>
        <h3>No students found</h3>
        <p>{{ getEmptyStateMessage() }}</p>
        <router-link to="/courses" class="browse-courses-btn">
          View Your Courses
        </router-link>
      </div>
    </div>

    <!-- Student Details Modal -->
    <div v-if="selectedStudent" class="modal-overlay" @click="closeStudentModal">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h2>{{ selectedStudent.name }} - Details</h2>
          <button @click="closeStudentModal" class="close-btn">&times;</button>
        </div>
        
        <div class="modal-content">
          <div class="student-profile">
            <div class="profile-header">
              <img :src="selectedStudent.avatar || '/default-avatar.jpg'" :alt="selectedStudent.name" class="profile-avatar" />
              <div class="profile-info">
                <h3>{{ selectedStudent.name }}</h3>
                <p>{{ selectedStudent.email }}</p>
                <span class="status-badge" :class="selectedStudent.status">
                  {{ formatStatus(selectedStudent.status) }}
                </span>
              </div>
            </div>
            
            <div class="profile-stats">
              <div class="profile-stat">
                <span class="stat-label">Course:</span>
                <span class="stat-value">{{ selectedStudent.course_title }}</span>
              </div>
              <div class="profile-stat">
                <span class="stat-label">Enrolled:</span>
                <span class="stat-value">{{ formatDate(selectedStudent.enrolled_at) }}</span>
              </div>
              <div class="profile-stat">
                <span class="stat-label">Progress:</span>
                <span class="stat-value">{{ selectedStudent.progress_percentage }}%</span>
              </div>
              <div class="profile-stat" v-if="selectedStudent.completed_at">
                <span class="stat-label">Completed:</span>
                <span class="stat-value">{{ formatDate(selectedStudent.completed_at) }}</span>
              </div>
            </div>
          </div>
          
          <div class="activity-timeline">
            <h4>Recent Activity</h4>
            <div class="timeline-items">
              <div v-for="activity in selectedStudent.recent_activity" :key="activity.id" class="timeline-item">
                <div class="timeline-icon">{{ getActivityIcon(activity.type) }}</div>
                <div class="timeline-content">
                  <p>{{ activity.description }}</p>
                  <span class="timeline-time">{{ formatRelativeTime(activity.timestamp) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="modal-actions">
          <button @click="sendMessage(selectedStudent)" class="message-btn">
            Send Message
          </button>
          <button @click="generateReport(selectedStudent)" class="report-btn">
            Generate Report
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useApiData } from '@/composables/useApiData'
// Removed unused import
import { useErrorHandler } from '@/composables/useErrorHandler'
import { api } from '@/services/api'

const { handleApiError } = useErrorHandler()

// Reactive state
const searchQuery = ref('')
const courseFilter = ref('')
const statusFilter = ref('')
const sortBy = ref('name')
const selectedStudent = ref(null)

// API data
const { 
  data: studentsData, 
  loading, 
  error, 
  refresh 
} = useApiData('/enrollments/', {
  immediate: true,
  transform: (data) => {
    // Transform the response to ensure consistent data structure
    if (data.results) {
      return {
        ...data,
        results: data.results.map((enrollment: any) => ({
          id: enrollment.id,
          student_id: enrollment.student?.id || enrollment.student_id,
          name: enrollment.student?.full_name || `${enrollment.student?.first_name} ${enrollment.student?.last_name}`.trim(),
          email: enrollment.student?.email,
          avatar: enrollment.student?.avatar,
          course_id: enrollment.course?.id || enrollment.course_id,
          course_title: enrollment.course?.title || enrollment.course_title,
          enrolled_at: enrollment.enrolled_at || enrollment.created_at,
          last_accessed: enrollment.last_accessed,
          progress_percentage: enrollment.progress_percentage || 0,
          status: enrollment.status || 'active',
          completed_at: enrollment.completed_at,
          grade: enrollment.final_grade
        }))
      }
    }
    return data
  },
  retryAttempts: 3,
  onError: (error) => {
    console.error('Failed to load students:', error)
  }
})

const { data: coursesData } = useApiData('/courses/', {
  immediate: true,
  transform: (data) => {
    if (data.results) {
      return {
        ...data,
        results: data.results.filter((course: any) => course.instructor_id === 'current_user_id') // This would be filtered on backend
      }
    }
    return data
  },
  retryAttempts: 3
})

// Computed properties
const students = computed(() => studentsData.value?.results || [])
const teacherCourses = computed(() => coursesData.value?.results || [])

const totalStudents = computed(() => {
  const uniqueStudents = new Set(students.value.map((s: any) => s.student_id))
  return uniqueStudents.size
})

const activeEnrollments = computed(() => 
  students.value.filter((s: any) => s.status === 'active').length
)

const completedEnrollments = computed(() => 
  students.value.filter((s: any) => s.status === 'completed').length
)

const averageProgress = computed(() => {
  if (students.value.length === 0) return 0
  const totalProgress = students.value.reduce((sum: number, s: any) => sum + (s.progress_percentage || 0), 0)
  return Math.round(totalProgress / students.value.length)
})

const filteredStudents = computed(() => {
  let filtered = students.value

  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter((student: any) => 
      student.name.toLowerCase().includes(query) ||
      student.email.toLowerCase().includes(query)
    )
  }

  // Course filter
  if (courseFilter.value) {
    filtered = filtered.filter((student: any) => student.course_id === courseFilter.value)
  }

  // Status filter
  if (statusFilter.value) {
    filtered = filtered.filter((student: any) => student.status === statusFilter.value)
  }

  // Sort
  filtered.sort((a: any, b: any) => {
    switch (sortBy.value) {
      case 'name':
        return a.name.localeCompare(b.name)
      case 'progress':
        return (b.progress_percentage || 0) - (a.progress_percentage || 0)
      case 'enrolled_date':
        return new Date(b.enrolled_at).getTime() - new Date(a.enrolled_at).getTime()
      case 'last_activity':
        return new Date(b.last_accessed || 0).getTime() - new Date(a.last_accessed || 0).getTime()
      default:
        return 0
    }
  })

  return filtered
})

// Methods
const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const formatRelativeTime = (dateString: string) => {
  if (!dateString) return 'Never'
  
  const now = new Date()
  const date = new Date(dateString)
  const diff = now.getTime() - date.getTime()
  
  const minutes = Math.floor(diff / (1000 * 60))
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)
  
  if (days > 0) return `${days} day${days > 1 ? 's' : ''} ago`
  if (hours > 0) return `${hours} hour${hours > 1 ? 's' : ''} ago`
  if (minutes > 0) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`
  return 'Just now'
}

const formatStatus = (status: string) => {
  const statusMap = {
    active: 'Active',
    completed: 'Completed',
    dropped: 'Dropped',
    paused: 'Paused'
  }
  return statusMap[status as keyof typeof statusMap] || status
}

const calculateCompletionRate = (student: any) => {
  // This would be calculated based on completed modules vs total modules
  // For now, using progress percentage as a proxy
  return student.progress_percentage || 0
}

const getEmptyStateMessage = () => {
  if (searchQuery.value) {
    return `No students found matching "${searchQuery.value}"`
  }
  if (courseFilter.value) {
    const course = teacherCourses.value.find((c: any) => c.id === courseFilter.value)
    return `No students enrolled in "${course?.title || 'selected course'}"`
  }
  if (statusFilter.value) {
    return `No students with ${statusFilter.value} status`
  }
  return 'No students enrolled in your courses yet. Students will appear here once they enroll.'
}

const getActivityIcon = (type: string) => {
  const icons = {
    enrollment: '📚',
    lesson_completed: '✅',
    assignment_submitted: '📝',
    quiz_completed: '🎯',
    certificate_earned: '🏆',
    login: '🔐'
  }
  return icons[type as keyof typeof icons] || '📝'
}

const applyFilters = () => {
  // Filters are applied automatically through computed property
}

const viewStudentDetails = (student: any) => {
  // Add mock recent activity data
  student.recent_activity = [
    {
      id: 1,
      type: 'lesson_completed',
      description: 'Completed lesson: Introduction to JavaScript',
      timestamp: new Date(Date.now() - 1000 * 60 * 30).toISOString()
    },
    {
      id: 2,
      type: 'quiz_completed',
      description: 'Completed quiz with score: 85%',
      timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString()
    },
    {
      id: 3,
      type: 'assignment_submitted',
      description: 'Submitted assignment: Build a Calculator',
      timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString()
    }
  ]
  
  selectedStudent.value = student
}

const closeStudentModal = () => {
  selectedStudent.value = null
}

const sendMessage = async (student: any) => {
  try {
    // This would open a messaging interface or send a notification
    console.log('Send message to:', student.name)
    // For now, just show an alert
    alert(`Message feature would open for ${student.name}`)
  } catch (error) {
    handleApiError(error as any, { context: { action: 'send_message' } })
  }
}

const viewProgress = (student: any) => {
  // Navigate to detailed progress view
  window.open(`/teacher/students/${student.id}/progress`, '_blank')
}

const generateReport = async (student: any) => {
  try {
    const response = await api.get(`/enrollments/${student.id}/report/`, {
      responseType: 'blob'
    })
    
    // Create download link
    const url = window.URL.createObjectURL(new Blob([response.data as any]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `${student.name}-progress-report.pdf`)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  } catch (error) {
    handleApiError(error as any, { context: { action: 'generate_student_report' } })
  }
}

const handleRetry = async () => {
  try {
    await refresh()
  } catch (err) {
    handleApiError(err as any, { context: { action: 'retry_students_load' } })
  }
}

onMounted(() => {
  // Any additional setup if needed
})
</script>

<style scoped>
.students-view {
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

.filters-section {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(254, 243, 226, 0.3));
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.1);
  margin-bottom: 2rem;
}

.search-bar {
  position: relative;
  margin-bottom: 1rem;
}

.search-input {
  width: 100%;
  padding: 0.75rem 2.5rem 0.75rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 0.875rem;
  background: white;
  transition: border-color 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: #f59e0b;
  box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.1);
}

.search-icon {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: #6b7280;
  font-size: 1rem;
}

.filters {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.filter-select {
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
  background: white;
  min-width: 150px;
}

.students-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.student-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 20px rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.1);
  transition: all 0.3s ease;
}

.student-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(245, 158, 11, 0.15);
}

.student-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.student-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.student-avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
}

.student-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.student-details h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.25rem;
}

.student-email {
  font-size: 0.875rem;
  color: #6b7280;
  margin-bottom: 0.25rem;
}

.course-name {
  font-size: 0.875rem;
  color: #f59e0b;
  font-weight: 500;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
}

.status-badge.active {
  background: #dcfce7;
  color: #166534;
}

.status-badge.completed {
  background: #dbeafe;
  color: #1e40af;
}

.status-badge.dropped {
  background: #fef2f2;
  color: #dc2626;
}

.student-progress {
  margin-bottom: 1rem;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.progress-label {
  font-size: 0.875rem;
  color: #6b7280;
}

.progress-percentage {
  font-size: 0.875rem;
  font-weight: 600;
  color: #f59e0b;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: #f3f4f6;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(135deg, #f59e0b, #d97706);
  transition: width 0.3s ease;
}

.student-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.stat-icon {
  font-size: 1.25rem;
  flex-shrink: 0;
}

.stat-content {
  display: flex;
  flex-direction: column;
}

.stat-label {
  font-size: 0.75rem;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.stat-value {
  font-size: 0.875rem;
  font-weight: 500;
  color: #1f2937;
}

.student-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.student-actions button {
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.view-btn {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
}

.message-btn {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
}

.progress-btn {
  background: linear-gradient(135deg, #8b5cf6, #7c3aed);
  color: white;
}

.report-btn {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
}

.student-actions button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.empty-state {
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

.empty-state h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.empty-state p {
  color: #6b7280;
  margin-bottom: 1.5rem;
  max-width: 500px;
  margin-left: auto;
  margin-right: auto;
}

.browse-courses-btn {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s ease;
  display: inline-block;
}

.browse-courses-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(245, 158, 11, 0.4);
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.75);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 2rem;
}

.modal {
  background: white;
  border-radius: 12px;
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #6b7280;
  padding: 0.25rem;
}

.close-btn:hover {
  color: #1f2937;
}

.modal-content {
  padding: 1.5rem;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.profile-avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  object-fit: cover;
}

.profile-info h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.25rem;
}

.profile-info p {
  color: #6b7280;
  margin-bottom: 0.5rem;
}

.profile-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.profile-stat {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
  border-bottom: 1px solid #f3f4f6;
}

.profile-stat:last-child {
  border-bottom: none;
}

.activity-timeline h4 {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 1rem;
}

.timeline-items {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.timeline-item {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
}

.timeline-icon {
  font-size: 1.25rem;
  flex-shrink: 0;
}

.timeline-content p {
  font-size: 0.875rem;
  color: #1f2937;
  margin-bottom: 0.25rem;
}

.timeline-time {
  font-size: 0.75rem;
  color: #6b7280;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  padding: 1.5rem;
  border-top: 1px solid #e5e7eb;
  justify-content: flex-end;
}

.modal-actions button {
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
}

.modal-actions .message-btn {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
}

.modal-actions .report-btn {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
}

.modal-actions button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
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
}

.retry-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(245, 158, 11, 0.4);
}

/* Responsive */
@media (max-width: 768px) {
  .students-view {
    padding: 1rem;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .filters {
    flex-direction: column;
  }
  
  .filter-select {
    min-width: auto;
  }
  
  .student-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .student-stats {
    grid-template-columns: 1fr;
  }
  
  .student-actions {
    justify-content: center;
  }
  
  .profile-header {
    flex-direction: column;
    text-align: center;
  }
  
  .profile-stats {
    grid-template-columns: 1fr;
  }
  
  .modal-actions {
    flex-direction: column;
  }
}
</style>