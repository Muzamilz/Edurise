<template>
  <div class="student-live-classes-view">
    <div class="page-header">
      <h1>My Live Classes</h1>
      <p>Join live classes and view recordings</p>
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
          <h3>Enrolled Classes</h3>
          <p class="stat-number">{{ totalClasses }}</p>
        </div>
        <div class="stat-card">
          <div class="stat-icon">📅</div>
          <h3>Upcoming</h3>
          <p class="stat-number">{{ upcomingClasses }}</p>
        </div>
        <div class="stat-card">
          <div class="stat-icon">✅</div>
          <h3>Attended</h3>
          <p class="stat-number">{{ attendedClasses }}</p>
        </div>
        <div class="stat-card">
          <div class="stat-icon">📹</div>
          <h3>Recordings</h3>
          <p class="stat-number">{{ availableRecordings }}</p>
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
      </div>

      <!-- Classes List -->
      <div v-if="filteredClasses.length > 0" class="classes-list">
        <div v-for="liveClass in filteredClasses" :key="liveClass.id" class="class-card">
          <div class="class-header">
            <div class="class-info">
              <h3>{{ liveClass.title }}</h3>
              <p class="course-name">{{ liveClass.course_title }}</p>
              <p class="instructor-name">Instructor: {{ liveClass.instructor_name }}</p>
            </div>
            <div class="class-status">
              <span class="status-badge" :class="liveClass.status">
                {{ formatStatus(liveClass.status) }}
              </span>
            </div>
          </div>

          <div class="class-details">
            <div class="class-meta">
              <div class="meta-item">
                <span class="meta-icon">📅</span>
                <span>{{ formatDate(liveClass.scheduled_at) }}</span>
              </div>
              <div class="meta-item">
                <span class="meta-icon">⏰</span>
                <span>{{ formatTime(liveClass.scheduled_at) }}</span>
              </div>
              <div class="meta-item">
                <span class="meta-icon">⏱️</span>
                <span>{{ liveClass.duration_minutes }} min</span>
              </div>
            </div>
            
            <p v-if="liveClass.description" class="class-description">
              {{ liveClass.description }}
            </p>
          </div>

          <div class="class-actions">
            <!-- Upcoming Class Actions -->
            <template v-if="liveClass.status === 'scheduled'">
              <button @click="joinClass(liveClass)" v-if="canJoinClass(liveClass)" class="join-btn">
                <span class="btn-icon">🎥</span>
                Join Class
              </button>
              <button @click="addToCalendar(liveClass)" class="calendar-btn">
                <span class="btn-icon">📅</span>
                Add to Calendar
              </button>
              <button @click="setReminder(liveClass)" class="reminder-btn">
                <span class="btn-icon">🔔</span>
                Set Reminder
              </button>
            </template>

            <!-- Live Class Actions -->
            <template v-else-if="liveClass.status === 'live'">
              <button @click="joinClass(liveClass)" class="join-btn live">
                <span class="btn-icon">🔴</span>
                Join Live Class
              </button>
            </template>

            <!-- Completed Class Actions -->
            <template v-else-if="liveClass.status === 'completed'">
              <button @click="viewRecording(liveClass)" v-if="liveClass.recording_url" class="recording-btn">
                <span class="btn-icon">📹</span>
                View Recording
              </button>
              <button @click="downloadMaterials(liveClass)" v-if="liveClass.has_materials" class="materials-btn">
                <span class="btn-icon">📄</span>
                Download Materials
              </button>
              <button @click="viewNotes(liveClass)" class="notes-btn">
                <span class="btn-icon">📝</span>
                My Notes
              </button>
            </template>
          </div>

          <!-- Attendance Status -->
          <div v-if="liveClass.status === 'completed'" class="attendance-status">
            <div class="attendance-info">
              <span class="attendance-icon">
                {{ liveClass.attended ? '✅' : '❌' }}
              </span>
              <span class="attendance-text">
                {{ liveClass.attended ? 'Attended' : 'Missed' }}
              </span>
              <span v-if="liveClass.attended && liveClass.attendance_duration" class="attendance-duration">
                ({{ liveClass.attendance_duration }} min)
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="empty-state">
        <div class="empty-icon">🎥</div>
        <h3>No live classes found</h3>
        <p>{{ getEmptyStateMessage() }}</p>
        <router-link to="/courses" class="browse-courses-btn">
          Browse Courses with Live Classes
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useApiData } from '@/composables/useApiData'
import { useErrorHandler } from '@/composables/useErrorHandler'
import { api } from '@/services/api'

const { handleApiError } = useErrorHandler()

// Reactive state
const activeFilter = ref('all')

// API data
const { 
  data: liveClassesData, 
  loading, 
  error, 
  refresh 
} = useApiData('/api/v1/live-classes/', {
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
          course_title: liveClass.course?.title || liveClass.course_title,
          instructor_name: liveClass.instructor?.full_name || liveClass.instructor_name,
          scheduled_at: liveClass.scheduled_at,
          duration_minutes: liveClass.duration_minutes || 60,
          status: liveClass.status || 'scheduled',
          join_url: liveClass.join_url,
          recording_url: liveClass.recording_url,
          has_materials: liveClass.has_materials || false,
          attended: liveClass.attended || false,
          attendance_duration: liveClass.attendance_duration
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

// Filter tabs
const filterTabs = [
  { label: 'All Classes', value: 'all' },
  { label: 'Upcoming', value: 'scheduled' },
  { label: 'Live Now', value: 'live' },
  { label: 'Completed', value: 'completed' }
]

// Computed properties
const liveClasses = computed(() => liveClassesData.value?.results || [])

const totalClasses = computed(() => liveClasses.value.length)
const upcomingClasses = computed(() => 
  liveClasses.value.filter(cls => cls.status === 'scheduled').length
)
const attendedClasses = computed(() => 
  liveClasses.value.filter(cls => cls.attended).length
)
const availableRecordings = computed(() => 
  liveClasses.value.filter(cls => cls.recording_url).length
)

const filteredClasses = computed(() => {
  let classes = liveClasses.value

  if (activeFilter.value !== 'all') {
    classes = classes.filter(cls => cls.status === activeFilter.value)
  }

  return classes.sort((a, b) => new Date(b.scheduled_at).getTime() - new Date(a.scheduled_at).getTime())
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
    scheduled: 'Upcoming',
    live: 'Live Now',
    completed: 'Completed',
    cancelled: 'Cancelled'
  }
  return statusMap[status as keyof typeof statusMap] || status
}

const canJoinClass = (liveClass: any) => {
  const now = new Date()
  const classTime = new Date(liveClass.scheduled_at)
  const timeDiff = classTime.getTime() - now.getTime()
  // Allow joining 15 minutes before and during class
  return timeDiff <= 15 * 60 * 1000 && timeDiff >= -liveClass.duration_minutes * 60 * 1000
}

const getEmptyStateMessage = () => {
  if (activeFilter.value === 'scheduled') {
    return 'No upcoming live classes. Check back later or browse courses with live sessions.'
  } else if (activeFilter.value === 'completed') {
    return 'No completed classes yet. Attended classes will appear here.'
  } else if (activeFilter.value === 'live') {
    return 'No live classes at the moment.'
  }
  return 'You haven\'t enrolled in any courses with live classes yet.'
}

const joinClass = (liveClass: any) => {
  if (liveClass.join_url) {
    window.open(liveClass.join_url, '_blank')
  }
}

const addToCalendar = (liveClass: any) => {
  const startDate = new Date(liveClass.scheduled_at)
  const endDate = new Date(startDate.getTime() + liveClass.duration_minutes * 60000)
  
  const calendarUrl = `https://calendar.google.com/calendar/render?action=TEMPLATE&text=${encodeURIComponent(liveClass.title)}&dates=${startDate.toISOString().replace(/[-:]/g, '').split('.')[0]}Z/${endDate.toISOString().replace(/[-:]/g, '').split('.')[0]}Z&details=${encodeURIComponent(liveClass.description || '')}`
  
  window.open(calendarUrl, '_blank')
}

const setReminder = async (liveClass: any) => {
  try {
    await api.post('/api/v1/notifications/', {
      type: 'class_reminder',
      class_id: liveClass.id,
      scheduled_for: new Date(new Date(liveClass.scheduled_at).getTime() - 15 * 60000) // 15 min before
    })
    alert('Reminder set successfully!')
  } catch (error) {
    handleApiError(error, { context: { action: 'set_class_reminder' } })
  }
}

const viewRecording = (liveClass: any) => {
  if (liveClass.recording_url) {
    window.open(liveClass.recording_url, '_blank')
  }
}

const downloadMaterials = async (liveClass: any) => {
  try {
    const response = await api.get(`/api/v1/live-classes/${liveClass.id}/materials/`, {
      responseType: 'blob'
    })
    
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `${liveClass.title}-materials.zip`)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  } catch (error) {
    handleApiError(error, { context: { action: 'download_class_materials' } })
  }
}

const viewNotes = (liveClass: any) => {
  // Navigate to notes view or open notes modal
  console.log('View notes for:', liveClass.title)
}

const handleRetry = async () => {
  try {
    await refresh()
  } catch (err) {
    handleApiError(err as any, { context: { action: 'retry_live_classes_load' } })
  }
}
</script>

<style scoped>
.student-live-classes-view {
  max-width: 1400px;
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
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 1rem;
}

.stat-icon {
  font-size: 2.5rem;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  background: linear-gradient(135deg, #f59e0b, #d97706);
}

.stat-card h3 {
  font-size: 0.875rem;
  font-weight: 500;
  color: #6b7280;
  margin: 0 0 0.5rem 0;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.stat-number {
  font-size: 1.875rem;
  font-weight: 700;
  color: #1f2937;
  margin: 0;
}

.class-filters {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
}

.filter-tabs {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.filter-tab {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  background: #f3f4f6;
  color: #6b7280;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.filter-tab.active {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
}

.filter-tab:hover:not(.active) {
  background: #e5e7eb;
  color: #374151;
}

.classes-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.class-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.class-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
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
  margin: 0 0 0.5rem 0;
}

.course-name {
  color: #f59e0b;
  font-weight: 500;
  margin: 0 0 0.25rem 0;
}

.instructor-name {
  color: #6b7280;
  font-size: 0.875rem;
  margin: 0;
}

.status-badge {
  padding: 0.5rem 1rem;
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
  background: #fee2e2;
  color: #dc2626;
  animation: pulse 2s infinite;
}

.status-badge.completed {
  background: #dcfce7;
  color: #166534;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.class-details {
  margin-bottom: 1.5rem;
}

.class-meta {
  display: flex;
  gap: 2rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: #6b7280;
}

.meta-icon {
  font-size: 1rem;
}

.class-description {
  color: #6b7280;
  line-height: 1.6;
  margin: 0;
}

.class-actions {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.join-btn,
.calendar-btn,
.reminder-btn,
.recording-btn,
.materials-btn,
.notes-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.3s ease;
}

.join-btn {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
}

.join-btn.live {
  background: linear-gradient(135deg, #dc2626, #b91c1c);
  animation: pulse 2s infinite;
}

.join-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(245, 158, 11, 0.4);
}

.calendar-btn {
  background: #dbeafe;
  color: #1e40af;
}

.calendar-btn:hover {
  background: #bfdbfe;
}

.reminder-btn {
  background: #f3e8ff;
  color: #5b21b6;
}

.reminder-btn:hover {
  background: #e9d5ff;
}

.recording-btn {
  background: #dcfce7;
  color: #166534;
}

.recording-btn:hover {
  background: #bbf7d0;
}

.materials-btn {
  background: #fef3c7;
  color: #92400e;
}

.materials-btn:hover {
  background: #fde68a;
}

.notes-btn {
  background: #f3f4f6;
  color: #374151;
}

.notes-btn:hover {
  background: #e5e7eb;
}

.attendance-status {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
}

.attendance-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
}

.attendance-icon {
  font-size: 1rem;
}

.attendance-text {
  font-weight: 500;
  color: #374151;
}

.attendance-duration {
  color: #6b7280;
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.empty-state h3 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.empty-state p {
  color: #6b7280;
  margin-bottom: 2rem;
  max-width: 400px;
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
  display: inline-block;
  transition: all 0.3s ease;
}

.browse-courses-btn:hover {
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