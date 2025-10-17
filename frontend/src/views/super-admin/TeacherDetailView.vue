<template>
  <div class="teacher-detail-view">
    <div class="page-header">
      <div class="header-content">
        <router-link to="/super-admin/teachers/global" class="back-link">
          ← Back to Teachers
        </router-link>
        <h1>{{ teacher?.first_name }} {{ teacher?.last_name || 'Loading...' }}</h1>
        <div class="teacher-status" :class="teacher?.is_approved_teacher ? 'approved' : 'pending'">
          {{ teacher?.is_approved_teacher ? 'Approved Teacher' : 'Pending Approval' }}
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>Loading teacher details...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-state">
      <div class="error-icon">⚠️</div>
      <h3>Failed to load teacher details</h3>
      <p>{{ error.message }}</p>
      <button @click="handleRetry" class="retry-btn">Try Again</button>
    </div>

    <!-- Teacher Details -->
    <div v-else-if="teacher" class="teacher-details">
      <!-- Teacher Profile Section -->
      <div class="profile-section">
        <div class="profile-card">
          <div class="profile-header">
            <div class="profile-avatar">
              <img :src="teacher.avatar || '/default-avatar.jpg'" :alt="teacher.first_name" />
            </div>
            <div class="profile-info">
              <h2>{{ teacher.first_name }} {{ teacher.last_name }}</h2>
              <p class="email">{{ teacher.email }}</p>
              <p class="organization">{{ teacher.organization?.name }}</p>
              <div class="profile-stats">
                <div class="stat">
                  <span class="stat-value">{{ teacher.courses_count || 0 }}</span>
                  <span class="stat-label">Courses</span>
                </div>
                <div class="stat">
                  <span class="stat-value">{{ teacher.students_count || 0 }}</span>
                  <span class="stat-label">Students</span>
                </div>
                <div class="stat">
                  <span class="stat-value">{{ teacher.rating || 'N/A' }}</span>
                  <span class="stat-label">Rating</span>
                </div>
              </div>
            </div>
          </div>
          
          <div class="profile-actions">
            <button 
              v-if="!teacher.is_approved_teacher"
              @click="approveTeacher"
              class="action-btn approve"
            >
              ✅ Approve Teacher
            </button>
            <button 
              v-else
              @click="suspendTeacher"
              class="action-btn suspend"
            >
              ⏸️ Suspend Teacher
            </button>
            <button @click="sendMessage" class="action-btn message">
              💬 Send Message
            </button>
            <button @click="viewAuditLog" class="action-btn audit">
              📋 View Audit Log
            </button>
          </div>
        </div>

        <!-- Teacher Information -->
        <div class="info-grid">
          <div class="info-card">
            <h3>Personal Information</h3>
            <div class="info-item">
              <span class="label">Full Name:</span>
              <span class="value">{{ teacher.first_name }} {{ teacher.last_name }}</span>
            </div>
            <div class="info-item">
              <span class="label">Email:</span>
              <span class="value">{{ teacher.email }}</span>
            </div>
            <div class="info-item">
              <span class="label">Phone:</span>
              <span class="value">{{ teacher.phone || 'Not provided' }}</span>
            </div>
            <div class="info-item">
              <span class="label">Date Joined:</span>
              <span class="value">{{ formatDate(teacher.date_joined) }}</span>
            </div>
            <div class="info-item">
              <span class="label">Last Login:</span>
              <span class="value">{{ formatDate(teacher.last_login) }}</span>
            </div>
          </div>

          <div class="info-card">
            <h3>Professional Information</h3>
            <div class="info-item">
              <span class="label">Organization:</span>
              <span class="value">{{ teacher.organization?.name || 'Independent' }}</span>
            </div>
            <div class="info-item">
              <span class="label">Specialization:</span>
              <span class="value">{{ teacher.specialization || 'Not specified' }}</span>
            </div>
            <div class="info-item">
              <span class="label">Experience:</span>
              <span class="value">{{ teacher.years_experience || 'Not specified' }} years</span>
            </div>
            <div class="info-item">
              <span class="label">Qualifications:</span>
              <span class="value">{{ teacher.qualifications || 'Not provided' }}</span>
            </div>
            <div class="info-item">
              <span class="label">Bio:</span>
              <span class="value">{{ teacher.bio || 'No bio provided' }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Courses Section -->
      <div class="courses-section">
        <div class="section-header">
          <h2>Courses ({{ teacherCourses.length }})</h2>
          <div class="course-filters">
            <select v-model="courseFilter">
              <option value="">All Courses</option>
              <option value="published">Published</option>
              <option value="draft">Draft</option>
              <option value="under_review">Under Review</option>
            </select>
          </div>
        </div>

        <div v-if="filteredCourses.length > 0" class="courses-grid">
          <div v-for="course in filteredCourses" :key="course.id" class="course-card">
            <div class="course-image">
              <img :src="course.thumbnail || '/default-course.jpg'" :alt="course.title" />
              <div class="course-status" :class="course.status">
                {{ formatStatus(course.status) }}
              </div>
            </div>
            <div class="course-content">
              <h4>{{ course.title }}</h4>
              <p class="course-description">{{ course.description }}</p>
              <div class="course-stats">
                <div class="stat">
                  <span class="stat-icon">👥</span>
                  <span>{{ course.enrollment_count || 0 }} students</span>
                </div>
                <div class="stat">
                  <span class="stat-icon">⭐</span>
                  <span>{{ course.average_rating || 'N/A' }}</span>
                </div>
                <div class="stat">
                  <span class="stat-icon">💰</span>
                  <span>${{ course.price || 'Free' }}</span>
                </div>
              </div>
            </div>
            <div class="course-actions">
              <button @click="viewCourse(course)" class="course-btn view">
                View Course
              </button>
              <button @click="moderateCourse(course)" class="course-btn moderate">
                Moderate
              </button>
            </div>
          </div>
        </div>

        <div v-else class="empty-courses">
          <div class="empty-icon">📚</div>
          <h3>No courses found</h3>
          <p>This teacher hasn't created any courses yet.</p>
        </div>
      </div>

      <!-- Analytics Section -->
      <div class="analytics-section">
        <div class="section-header">
          <h2>Performance Analytics</h2>
          <div class="period-selector">
            <select v-model="analyticsPeriod">
              <option value="7d">Last 7 Days</option>
              <option value="30d">Last 30 Days</option>
              <option value="90d">Last 90 Days</option>
              <option value="1y">Last Year</option>
            </select>
          </div>
        </div>

        <div class="analytics-grid">
          <div class="analytics-card">
            <h3>Revenue</h3>
            <p class="analytics-value">${{ formatCurrency(analytics?.total_revenue || 0) }}</p>
            <span class="analytics-change" :class="{ positive: analytics?.revenue_change > 0 }">
              {{ analytics?.revenue_change > 0 ? '+' : '' }}{{ analytics?.revenue_change || 0 }}%
            </span>
          </div>
          
          <div class="analytics-card">
            <h3>New Students</h3>
            <p class="analytics-value">{{ analytics?.new_students || 0 }}</p>
            <span class="analytics-change" :class="{ positive: analytics?.students_change > 0 }">
              {{ analytics?.students_change > 0 ? '+' : '' }}{{ analytics?.students_change || 0 }}%
            </span>
          </div>
          
          <div class="analytics-card">
            <h3>Course Completions</h3>
            <p class="analytics-value">{{ analytics?.completions || 0 }}</p>
            <span class="analytics-change" :class="{ positive: analytics?.completions_change > 0 }">
              {{ analytics?.completions_change > 0 ? '+' : '' }}{{ analytics?.completions_change || 0 }}%
            </span>
          </div>
          
          <div class="analytics-card">
            <h3>Average Rating</h3>
            <p class="analytics-value">{{ analytics?.average_rating || 'N/A' }}</p>
            <span class="analytics-change">
              {{ analytics?.total_reviews || 0 }} reviews
            </span>
          </div>
        </div>
      </div>

      <!-- Recent Activity -->
      <div class="activity-section">
        <div class="section-header">
          <h2>Recent Activity</h2>
        </div>

        <div class="activity-list">
          <div v-for="activity in recentActivity" :key="activity.id" class="activity-item">
            <div class="activity-icon" :class="activity.type">
              <span v-if="activity.type === 'course_created'">📚</span>
              <span v-else-if="activity.type === 'student_enrolled'">👥</span>
              <span v-else-if="activity.type === 'course_updated'">✏️</span>
              <span v-else-if="activity.type === 'review_received'">⭐</span>
              <span v-else>📋</span>
            </div>
            <div class="activity-content">
              <p class="activity-description">{{ activity.description }}</p>
              <span class="activity-time">{{ formatDateTime(activity.timestamp) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Message Modal -->
    <div v-if="showMessageModal" class="modal-overlay" @click="closeMessageModal">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>Send Message to {{ teacher?.first_name }} {{ teacher?.last_name }}</h3>
          <button @click="closeMessageModal" class="close-btn">×</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="sendMessageToTeacher">
            <div class="form-group">
              <label>Subject</label>
              <input v-model="messageForm.subject" type="text" required />
            </div>
            <div class="form-group">
              <label>Message</label>
              <textarea v-model="messageForm.content" rows="6" required></textarea>
            </div>
            <div class="form-actions">
              <button type="button" @click="closeMessageModal" class="cancel-btn">Cancel</button>
              <button type="submit" class="send-btn">Send Message</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useApiData, useApiMutation } from '@/composables/useApiData'
import { useErrorHandler } from '@/composables/useErrorHandler'

const route = useRoute()
const router = useRouter()
const { handleApiError } = useErrorHandler()

// Reactive state
const courseFilter = ref('')
const analyticsPeriod = ref('30d')
const showMessageModal = ref(false)
const messageForm = ref({
  subject: '',
  content: ''
})

// API data
const teacherId = computed(() => route.params.id as string)

const { 
  data: teacher, 
  loading, 
  error, 
  refresh 
} = useApiData(() => `/users/${teacherId.value}/`, {
  immediate: true
})

const { data: teacherCourses } = useApiData(() => `/courses/?instructor=${teacherId.value}`)
const { data: analytics } = useApiData(() => `/analytics/teacher/?user=${teacherId.value}&period=${analyticsPeriod.value}`)
const { data: recentActivity } = useApiData(() => `/audit-logs/?user=${teacherId.value}&limit=10`)

// Mutations
const { mutate: updateTeacherStatus } = useApiMutation(
  ({ id, status }) => ({ 
    method: 'PATCH', 
    url: `/users/${id}/`, 
    data: { is_approved_teacher: status } 
  }),
  {
    onSuccess: () => refresh(),
    onError: (error) => handleApiError(error, { context: { action: 'update_teacher_status' } })
  }
)

const { mutate: sendMessageMutation } = useApiMutation(
  (messageData) => ({ 
    method: 'POST', 
    url: '/notifications/', 
    data: messageData 
  }),
  {
    onSuccess: () => {
      closeMessageModal()
      // Show success message
    },
    onError: (error) => handleApiError(error, { context: { action: 'send_message' } })
  }
)

// Computed properties
const filteredCourses = computed(() => {
  if (!teacherCourses.value) return []
  
  return teacherCourses.value.filter(course => {
    return !courseFilter.value || course.status === courseFilter.value
  })
})

// Methods
const formatDate = (date: string) => {
  if (!date) return 'Never'
  return new Date(date).toLocaleDateString()
}

const formatDateTime = (date: string) => {
  if (!date) return 'Never'
  return new Date(date).toLocaleString()
}

const formatStatus = (status: string) => {
  return status.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(amount)
}

const approveTeacher = async () => {
  if (confirm('Are you sure you want to approve this teacher?')) {
    await updateTeacherStatus({ id: teacherId.value, status: true })
  }
}

const suspendTeacher = async () => {
  if (confirm('Are you sure you want to suspend this teacher?')) {
    await updateTeacherStatus({ id: teacherId.value, status: false })
  }
}

const sendMessage = () => {
  showMessageModal.value = true
}

const closeMessageModal = () => {
  showMessageModal.value = false
  messageForm.value = { subject: '', content: '' }
}

const sendMessageToTeacher = async () => {
  await sendMessageMutation({
    recipient_id: teacherId.value,
    type: 'admin_message',
    title: messageForm.value.subject,
    message: messageForm.value.content
  })
}

const viewAuditLog = () => {
  // Navigate to audit log filtered by this teacher
  router.push(`/super-admin/audit-logs?user=${teacherId.value}`)
}

const viewCourse = (course: any) => {
  window.open(`/courses/${course.id}`, '_blank')
}

const moderateCourse = (course: any) => {
  // Navigate to course moderation
  router.push(`/super-admin/courses/${course.id}/moderate`)
}

const handleRetry = async () => {
  try {
    await refresh()
  } catch (err) {
    handleApiError(err as any, { context: { action: 'retry_teacher_load' } })
  }
}

onMounted(() => {
  refresh()
})
</script>

<style scoped>
.teacher-detail-view {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
}

.page-header {
  margin-bottom: 2rem;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.back-link {
  color: #f59e0b;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.3s ease;
}

.back-link:hover {
  color: #d97706;
}

.header-content h1 {
  font-size: 2rem;
  font-weight: 700;
  color: #1f2937;
  margin: 0;
  flex: 1;
}

.teacher-status {
  padding: 0.5rem 1rem;
  border-radius: 12px;
  font-size: 0.875rem;
  font-weight: 500;
  text-transform: uppercase;
}

.teacher-status.approved {
  background: #dcfce7;
  color: #166534;
}

.teacher-status.pending {
  background: #fef3c7;
  color: #92400e;
}

.profile-section {
  margin-bottom: 2rem;
}

.profile-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  padding: 2rem;
  margin-bottom: 1.5rem;
}

.profile-header {
  display: flex;
  gap: 2rem;
  margin-bottom: 2rem;
}

.profile-avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
}

.profile-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.profile-info h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 0.5rem 0;
}

.profile-info .email {
  color: #6b7280;
  margin-bottom: 0.25rem;
}

.profile-info .organization {
  color: #f59e0b;
  font-weight: 500;
  margin-bottom: 1rem;
}

.profile-stats {
  display: flex;
  gap: 2rem;
}

.stat {
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 1.5rem;
  font-weight: 700;
  color: #1f2937;
}

.stat-label {
  font-size: 0.875rem;
  color: #6b7280;
}

.profile-actions {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.action-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-btn.approve {
  background: #dcfce7;
  color: #166534;
}

.action-btn.approve:hover {
  background: #bbf7d0;
}

.action-btn.suspend {
  background: #fee2e2;
  color: #dc2626;
}

.action-btn.suspend:hover {
  background: #fecaca;
}

.action-btn.message {
  background: #dbeafe;
  color: #1e40af;
}

.action-btn.message:hover {
  background: #bfdbfe;
}

.action-btn.audit {
  background: #f3f4f6;
  color: #374151;
}

.action-btn.audit:hover {
  background: #e5e7eb;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 1.5rem;
}

.info-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
}

.info-card h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 1rem 0;
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 0.5rem;
}

.info-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.75rem;
}

.info-item .label {
  font-weight: 500;
  color: #6b7280;
}

.info-item .value {
  color: #1f2937;
  text-align: right;
  max-width: 60%;
  word-break: break-word;
}

.courses-section,
.analytics-section,
.activity-section {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
  overflow: hidden;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.section-header h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.course-filters select,
.period-selector select {
  padding: 0.5rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
}

.courses-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
  padding: 1.5rem;
}

.course-card {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.course-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.course-image {
  position: relative;
  height: 150px;
  overflow: hidden;
}

.course-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.course-status {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
  background: white;
  color: #374151;
}

.course-content {
  padding: 1rem;
}

.course-content h4 {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 0.5rem 0;
}

.course-description {
  color: #6b7280;
  font-size: 0.875rem;
  margin-bottom: 1rem;
  line-height: 1.5;
}

.course-stats {
  display: flex;
  justify-content: space-between;
  font-size: 0.875rem;
  color: #6b7280;
  margin-bottom: 1rem;
}

.stat {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.stat-icon {
  font-size: 1rem;
}

.course-actions {
  display: flex;
  gap: 0.5rem;
  padding: 1rem;
  border-top: 1px solid #f3f4f6;
}

.course-btn {
  flex: 1;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.course-btn.view {
  background: #dbeafe;
  color: #1e40af;
}

.course-btn.view:hover {
  background: #bfdbfe;
}

.course-btn.moderate {
  background: #fef3c7;
  color: #92400e;
}

.course-btn.moderate:hover {
  background: #fde68a;
}

.empty-courses {
  text-align: center;
  padding: 3rem;
  color: #6b7280;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.analytics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  padding: 1.5rem;
}

.analytics-card {
  text-align: center;
  padding: 1.5rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.analytics-card h3 {
  font-size: 0.875rem;
  font-weight: 500;
  color: #6b7280;
  margin: 0 0 0.5rem 0;
  text-transform: uppercase;
}

.analytics-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 0.25rem 0;
}

.analytics-change {
  font-size: 0.875rem;
  color: #6b7280;
}

.analytics-change.positive {
  color: #059669;
}

.activity-list {
  padding: 1.5rem;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 0;
  border-bottom: 1px solid #f3f4f6;
}

.activity-item:last-child {
  border-bottom: none;
}

.activity-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  background: #f3f4f6;
}

.activity-content {
  flex: 1;
}

.activity-description {
  color: #1f2937;
  margin: 0 0 0.25rem 0;
}

.activity-time {
  font-size: 0.875rem;
  color: #6b7280;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
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

.modal-header h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #6b7280;
  cursor: pointer;
  padding: 0.25rem;
}

.close-btn:hover {
  color: #374151;
}

.modal-body {
  padding: 1.5rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.5rem;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 1rem;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #f59e0b;
  box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.1);
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1.5rem;
}

.cancel-btn {
  padding: 0.75rem 1.5rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: white;
  color: #374151;
  cursor: pointer;
  font-weight: 500;
}

.cancel-btn:hover {
  background: #f9fafb;
}

.send-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  cursor: pointer;
  font-weight: 600;
}

.send-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
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
</style>