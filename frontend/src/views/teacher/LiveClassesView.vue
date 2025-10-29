<template>
  <div class="live-classes-view">
    <div class="page-header">
      <h1>Live Classes</h1>
      <p>Schedule and manage your live classes</p>
      <button @click="showCreateModal = true" class="create-btn">
        <span class="btn-icon">➕</span>
        Schedule New Class
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>Loading your live classes...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-state">
      <div class="error-icon">⚠️</div>
      <h3>Failed to load live classes</h3>
      <p>{{ error.message }}</p>
      <button @click="handleRetry" class="retry-btn">Try Again</button>
    </div>

    <!-- Live Classes Content -->
    <div v-else class="live-classes-content">
      <!-- Quick Stats -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon">🎥</div>
          <h3>Total Classes</h3>
          <p class="stat-number">{{ totalClasses }}</p>
        </div>
        <div class="stat-card">
          <div class="stat-icon">📅</div>
          <h3>Upcoming Classes</h3>
          <p class="stat-number">{{ upcomingClasses }}</p>
        </div>
        <div class="stat-card">
          <div class="stat-icon">✅</div>
          <h3>Completed Classes</h3>
          <p class="stat-number">{{ completedClasses }}</p>
        </div>
        <div class="stat-card">
          <div class="stat-icon">👥</div>
          <h3>Total Attendees</h3>
          <p class="stat-number">{{ totalAttendees }}</p>
        </div>
      </div>

      <!-- Class Filters -->
      <div class="class-filters">
        <div class="filter-tabs">
          <button 
            v-for="tab in filterTabs" 
            :key="tab.value"
            @click="activeFilter = tab.value"
            class="filter-tab"
            :class="{ active: activeFilter === tab.value }"
          >
            {{ tab.label }}
          </button>
        </div>
        <div class="filter-controls">
          <select v-model="courseFilter" @change="applyFilters" class="course-select">
            <option value="">All Courses</option>
            <option v-for="course in teacherCourses" :key="course.id" :value="course.id">
              {{ course.title }}
            </option>
          </select>
          <input 
            type="date" 
            v-model="dateFilter" 
            @change="applyFilters"
            class="date-filter"
          >
        </div>
      </div>

      <!-- Classes List -->
      <div v-if="filteredClasses.length > 0" class="classes-list">
        <div v-for="liveClass in filteredClasses" :key="liveClass.id" class="class-card">
          <div class="class-header">
            <div class="class-info">
              <h3>{{ liveClass.title }}</h3>
              <p class="course-name">{{ liveClass.course_title }}</p>
              <div class="class-meta">
                <span class="class-date">
                  <span class="meta-icon">📅</span>
                  {{ formatDate(liveClass.scheduled_at) }}
                </span>
                <span class="class-time">
                  <span class="meta-icon">⏰</span>
                  {{ formatTime(liveClass.scheduled_at) }}
                </span>
                <span class="class-duration">
                  <span class="meta-icon">⏱️</span>
                  {{ liveClass.duration_minutes }} min
                </span>
              </div>
            </div>
            <div class="class-status">
              <span class="status-badge" :class="liveClass.status">
                {{ formatStatus(liveClass.status) }}
              </span>
            </div>
          </div>

          <div class="class-details">
            <p v-if="liveClass.description" class="class-description">
              {{ liveClass.description }}
            </p>
            <div class="class-stats">
              <div class="stat-item">
                <span class="stat-label">Enrolled Students:</span>
                <span class="stat-value">{{ liveClass.enrolled_students }}</span>
              </div>
              <div class="stat-item" v-if="liveClass.status === 'completed'">
                <span class="stat-label">Attendance:</span>
                <span class="stat-value">{{ liveClass.attendance_count }}/{{ liveClass.enrolled_students }}</span>
              </div>
              <div class="stat-item" v-if="liveClass.recording_url">
                <span class="stat-label">Recording:</span>
                <span class="stat-value">Available</span>
              </div>
            </div>
          </div>

          <div class="class-actions">
            <template v-if="liveClass.status === 'scheduled'">
              <button @click="startClass(liveClass)" class="start-btn" v-if="canStartClass(liveClass)">
                <span class="btn-icon">▶️</span>
                Start Class
              </button>
              <button @click="editClass(liveClass)" class="edit-btn">
                <span class="btn-icon">✏️</span>
                Edit
              </button>
              <button @click="cancelClass(liveClass)" class="cancel-btn">
                <span class="btn-icon">❌</span>
                Cancel
              </button>
            </template>
            
            <template v-else-if="liveClass.status === 'live'">
              <button @click="joinClass(liveClass)" class="join-btn">
                <span class="btn-icon">🎥</span>
                Join Class
              </button>
              <button @click="endClass(liveClass)" class="end-btn">
                <span class="btn-icon">⏹️</span>
                End Class
              </button>
            </template>
            
            <template v-else-if="liveClass.status === 'completed'">
              <button @click="viewAttendance(liveClass)" class="attendance-btn">
                <span class="btn-icon">👥</span>
                View Attendance
              </button>
              <button @click="viewRecording(liveClass)" v-if="liveClass.recording_url" class="recording-btn">
                <span class="btn-icon">📹</span>
                View Recording
              </button>
              <button @click="scheduleFollowUp(liveClass)" class="followup-btn">
                <span class="btn-icon">🔄</span>
                Schedule Follow-up
              </button>
            </template>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="empty-state">
        <div class="empty-icon">🎥</div>
        <h3>No live classes found</h3>
        <p>{{ getEmptyStateMessage() }}</p>
        <button @click="showCreateModal = true" class="create-class-btn">
          Schedule Your First Class
        </button>
      </div>
    </div>

    <!-- Create/Edit Class Modal -->
    <div v-if="showCreateModal || editingClass" class="modal-overlay" @click="closeModal">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h2>{{ editingClass ? 'Edit Live Class' : 'Schedule New Live Class' }}</h2>
          <button @click="closeModal" class="close-btn">&times;</button>
        </div>
        
        <form @submit.prevent="saveClass" class="modal-form">
          <div class="form-group">
            <label for="classTitle">Class Title</label>
            <input 
              type="text" 
              id="classTitle"
              v-model="classForm.title" 
              required
              placeholder="Enter class title"
            >
          </div>
          
          <div class="form-group">
            <label for="classCourse">Course</label>
            <select id="classCourse" v-model="classForm.course_id" required>
              <option value="">Select a course</option>
              <option v-for="course in teacherCourses" :key="course.id" :value="course.id">
                {{ course.title }}
              </option>
            </select>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label for="classDate">Date</label>
              <input 
                type="date" 
                id="classDate"
                v-model="classForm.date" 
                required
                :min="today"
              >
            </div>
            <div class="form-group">
              <label for="classTime">Time</label>
              <input 
                type="time" 
                id="classTime"
                v-model="classForm.time" 
                required
              >
            </div>
          </div>
          
          <div class="form-group">
            <label for="classDuration">Duration (minutes)</label>
            <select id="classDuration" v-model="classForm.duration_minutes">
              <option value="30">30 minutes</option>
              <option value="45">45 minutes</option>
              <option value="60">60 minutes</option>
              <option value="90">90 minutes</option>
              <option value="120">120 minutes</option>
            </select>
          </div>
          
          <div class="form-group">
            <label for="classDescription">Description (Optional)</label>
            <textarea 
              id="classDescription"
              v-model="classForm.description" 
              rows="3"
              placeholder="Describe what will be covered in this class"
            ></textarea>
          </div>
          
          <div class="form-actions">
            <button type="button" @click="closeModal" class="cancel-btn">Cancel</button>
            <button type="submit" class="save-btn" :disabled="saving">
              {{ saving ? 'Saving...' : (editingClass ? 'Update Class' : 'Schedule Class') }}
            </button>
          </div>
        </form>
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
const activeFilter = ref('all')
const courseFilter = ref('')
const dateFilter = ref('')
const showCreateModal = ref(false)
const editingClass = ref<any>(null)
const saving = ref(false)

const classForm = ref({
  title: '',
  course_id: '',
  date: '',
  time: '',
  duration_minutes: 60,
  description: ''
})

// API data
const { 
  data: liveClassesData, 
  loading, 
  error, 
  refresh 
} = useApiData<any>('/live-classes/', {
  immediate: true,
  transform: (data) => {
    // Transform the response to ensure consistent data structure
    if (data.results) {
      return {
        ...data,
        results: data.results.map((liveClass: any) => ({
          id: liveClass.id,
          title: liveClass.title,
          description: liveClass.description,
          course_id: liveClass.course?.id || liveClass.course_id,
          course_title: liveClass.course?.title || liveClass.course_title,
          scheduled_at: liveClass.scheduled_at,
          duration_minutes: liveClass.duration_minutes || 60,
          status: liveClass.status || 'scheduled',
          join_url: liveClass.join_url,
          recording_url: liveClass.recording_url,
          enrolled_students: liveClass.enrolled_students || 0,
          attendance_count: liveClass.attendance_count || 0
        }))
      }
    }
    return data
  },
  retryAttempts: 3,
  onError: (error) => {
    console.error('Failed to load live classes:', error)
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

// Filter tabs
const filterTabs = [
  { label: 'All Classes', value: 'all' },
  { label: 'Upcoming', value: 'upcoming' },
  { label: 'Live Now', value: 'live' },
  { label: 'Completed', value: 'completed' },
  { label: 'Cancelled', value: 'cancelled' }
]

// Computed properties
const liveClasses = computed(() => liveClassesData.value?.results || [])
const teacherCourses = computed(() => coursesData.value?.results || [])

const totalClasses = computed(() => liveClasses.value.length)
const upcomingClasses = computed(() => 
  (liveClasses.value as any[]).filter((cls: any) => cls.status === 'scheduled').length
)
const completedClasses = computed(() => 
  (liveClasses.value as any[]).filter((cls: any) => cls.status === 'completed').length
)
const totalAttendees = computed(() => 
  (liveClasses.value as any[]).reduce((total: number, cls: any) => total + (cls.attendance_count || 0), 0)
)

const filteredClasses = computed(() => {
  let classes = liveClasses.value as any[]

  // Filter by status
  if (activeFilter.value !== 'all') {
    classes = classes.filter((cls: any) => cls.status === activeFilter.value)
  }

  // Filter by course
  if (courseFilter.value) {
    classes = classes.filter((cls: any) => cls.course_id === courseFilter.value)
  }

  // Filter by date
  if (dateFilter.value) {
    const filterDate = new Date(dateFilter.value)
    classes = classes.filter((cls: any) => {
      const classDate = new Date(cls.scheduled_at)
      return classDate.toDateString() === filterDate.toDateString()
    })
  }

  return classes.sort((a: any, b: any) => new Date(a.scheduled_at).getTime() - new Date(b.scheduled_at).getTime())
})

const today = computed(() => {
  return new Date().toISOString().split('T')[0]
})

// Methods
const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const formatTime = (dateString: string) => {
  return new Date(dateString).toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatStatus = (status: string) => {
  const statusMap = {
    scheduled: 'Scheduled',
    live: 'Live Now',
    completed: 'Completed',
    cancelled: 'Cancelled'
  }
  return statusMap[status as keyof typeof statusMap] || status
}

const canStartClass = (liveClass: any) => {
  const now = new Date()
  const classTime = new Date(liveClass.scheduled_at)
  const timeDiff = classTime.getTime() - now.getTime()
  // Allow starting 15 minutes before scheduled time
  return timeDiff <= 15 * 60 * 1000 && timeDiff >= -30 * 60 * 1000
}

const getEmptyStateMessage = () => {
  if (activeFilter.value === 'upcoming') {
    return 'No upcoming classes scheduled. Schedule a new class to get started.'
  } else if (activeFilter.value === 'completed') {
    return 'No completed classes yet. Your completed classes will appear here.'
  } else if (activeFilter.value === 'live') {
    return 'No live classes at the moment.'
  }
  return 'You haven\'t scheduled any live classes yet. Create your first class to engage with your students in real-time.'
}

const applyFilters = () => {
  // Filters are applied automatically through computed property
}

const startClass = async (liveClass: any) => {
  try {
    const response = await api.post(`/live-classes/${liveClass.id}/start_class/`)
    // Open Zoom meeting
    if ((response.data as any).join_url) {
      window.open((response.data as any).join_url, '_blank')
    }
    await refresh()
  } catch (error) {
    handleApiError(error as any, { context: { action: 'start_live_class' } })
  }
}

const joinClass = (liveClass: any) => {
  if (liveClass.join_url) {
    window.open(liveClass.join_url, '_blank')
  }
}

const endClass = async (liveClass: any) => {
  try {
    await api.post(`/live-classes/${liveClass.id}/end_class/`)
    await refresh()
  } catch (error) {
    handleApiError(error as any, { context: { action: 'end_live_class' } })
  }
}

const editClass = (liveClass: any) => {
  editingClass.value = liveClass
  const scheduledAt = new Date(liveClass.scheduled_at)
  classForm.value = {
    title: liveClass.title,
    course_id: liveClass.course_id,
    date: scheduledAt.toISOString().split('T')[0],
    time: scheduledAt.toTimeString().slice(0, 5),
    duration_minutes: liveClass.duration_minutes,
    description: liveClass.description || ''
  }
}

const cancelClass = async (liveClass: any) => {
  if (confirm('Are you sure you want to cancel this class?')) {
    try {
      await api.patch(`/live-classes/${liveClass.id}/`, { status: 'cancelled' })
      await refresh()
    } catch (error) {
      handleApiError(error as any, { context: { action: 'cancel_live_class' } })
    }
  }
}

const viewAttendance = (liveClass: any) => {
  // Navigate to attendance view
  window.open(`/live-classes/${liveClass.id}/attendance`, '_blank')
}

const viewRecording = (liveClass: any) => {
  if (liveClass.recording_url) {
    window.open(liveClass.recording_url, '_blank')
  }
}

const scheduleFollowUp = (liveClass: any) => {
  // Pre-fill form with follow-up class details
  showCreateModal.value = true
  classForm.value = {
    title: `${liveClass.title} - Follow-up`,
    course_id: liveClass.course_id,
    date: '',
    time: '',
    duration_minutes: liveClass.duration_minutes,
    description: `Follow-up session for: ${liveClass.title}`
  }
}

const closeModal = () => {
  showCreateModal.value = false
  editingClass.value = null
  classForm.value = {
    title: '',
    course_id: '',
    date: '',
    time: '',
    duration_minutes: 60,
    description: ''
  }
}

const saveClass = async () => {
  saving.value = true
  try {
    const scheduledAt = new Date(`${classForm.value.date}T${classForm.value.time}`)
    
    const classData = {
      title: classForm.value.title,
      course_id: classForm.value.course_id,
      scheduled_at: scheduledAt.toISOString(),
      duration_minutes: classForm.value.duration_minutes,
      description: classForm.value.description
    }

    if (editingClass.value) {
      await api.patch(`/live-classes/${editingClass.value.id}/`, classData)
    } else {
      await api.post('/live-classes/', classData)
    }

    await refresh()
    closeModal()
  } catch (error) {
    handleApiError(error as any, { context: { action: 'save_live_class' } })
  } finally {
    saving.value = false
  }
}

const handleRetry = async () => {
  try {
    await refresh()
  } catch (err) {
    handleApiError(err as any, { context: { action: 'retry_live_classes_load' } })
  }
}

onMounted(() => {
  // Set default date filter to today
  dateFilter.value = new Date().toISOString().split('T')[0]
})
</script>

<style scoped>
.live-classes-view {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
}

.page-header div {
  flex: 1;
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

.create-btn {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}

.create-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(245, 158, 11, 0.4);
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

.class-filters {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(254, 243, 226, 0.3));
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.1);
  margin-bottom: 2rem;
}

.filter-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.filter-tab {
  padding: 0.5rem 1rem;
  border: 1px solid #d1d5db;
  background: white;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.filter-tab:hover {
  background: #f9fafb;
  border-color: #9ca3af;
}

.filter-tab.active {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  border-color: #f59e0b;
}

.filter-controls {
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
}

.course-select, .date-filter {
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
  background: white;
}

.classes-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.class-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 20px rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.1);
  transition: all 0.3s ease;
}

.class-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(245, 158, 11, 0.15);
}

.class-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.class-info h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.25rem;
}

.course-name {
  font-size: 0.875rem;
  color: #f59e0b;
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.class-meta {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.class-meta span {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.875rem;
  color: #6b7280;
}

.meta-icon {
  font-size: 1rem;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
}

.status-badge.scheduled {
  background: #dbeafe;
  color: #1e40af;
}

.status-badge.live {
  background: #dcfce7;
  color: #166534;
  animation: pulse 2s infinite;
}

.status-badge.completed {
  background: #f3f4f6;
  color: #374151;
}

.status-badge.cancelled {
  background: #fef2f2;
  color: #dc2626;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.class-description {
  font-size: 0.875rem;
  color: #6b7280;
  margin-bottom: 1rem;
  line-height: 1.5;
}

.class-stats {
  display: flex;
  gap: 2rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.stat-item {
  display: flex;
  gap: 0.5rem;
}

.stat-label {
  font-size: 0.875rem;
  color: #6b7280;
}

.stat-value {
  font-size: 0.875rem;
  font-weight: 500;
  color: #1f2937;
}

.class-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.class-actions button {
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

.start-btn, .join-btn {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
}

.edit-btn {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
}

.cancel-btn, .end-btn {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: white;
}

.attendance-btn, .recording-btn, .followup-btn {
  background: linear-gradient(135deg, #8b5cf6, #7c3aed);
  color: white;
}

.class-actions button:hover {
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

.create-class-btn {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.create-class-btn:hover {
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

.modal-form {
  padding: 1.5rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-group label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.5rem;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
  transition: border-color 0.3s ease;
}

.form-group input:focus,
.form-group select:focus,
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
  padding-top: 1.5rem;
  border-top: 1px solid #e5e7eb;
}

.form-actions .cancel-btn {
  background: #f3f4f6;
  color: #374151;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.form-actions .cancel-btn:hover {
  background: #e5e7eb;
}

.save-btn {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.save-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
}

.save-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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
  .live-classes-view {
    padding: 1rem;
  }
  
  .page-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .filter-tabs {
    justify-content: center;
  }
  
  .filter-controls {
    flex-direction: column;
    align-items: stretch;
  }
  
  .class-header {
    flex-direction: column;
    gap: 1rem;
  }
  
  .class-meta {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .class-stats {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .class-actions {
    justify-content: center;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .form-actions {
    flex-direction: column;
  }
}
</style>