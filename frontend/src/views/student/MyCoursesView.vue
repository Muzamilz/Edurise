<template>
  <div class="my-courses-view">
    <div class="page-header">
      <h1>My Courses</h1>
      <p>Track your learning progress and continue your studies</p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>Loading your courses...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-state">
      <div class="error-icon">⚠️</div>
      <h3>Failed to load courses</h3>
      <p>{{ error.message }}</p>
      <button @click="handleRetry" class="retry-btn">Try Again</button>
    </div>

    <!-- Courses Content -->
    <div v-else class="courses-content">
      <!-- Progress Overview -->
      <div class="progress-overview">
        <div class="overview-card total">
          <div class="card-icon">📚</div>
          <div class="card-content">
            <h3>Total Courses</h3>
            <p class="number">{{ totalCourses }}</p>
          </div>
        </div>
        <div class="overview-card completed">
          <div class="card-icon">✅</div>
          <div class="card-content">
            <h3>Completed</h3>
            <p class="number">{{ completedCourses }}</p>
          </div>
        </div>
        <div class="overview-card in-progress">
          <div class="card-icon">📖</div>
          <div class="card-content">
            <h3>In Progress</h3>
            <p class="number">{{ inProgressCourses }}</p>
          </div>
        </div>
        <div class="overview-card certificates">
          <div class="card-icon">🏆</div>
          <div class="card-content">
            <h3>Certificates</h3>
            <p class="number">{{ earnedCertificates }}</p>
          </div>
        </div>
      </div>

      <!-- Course Filters -->
      <div class="course-filters">
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
        <div class="search-bar">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search your courses..."
            class="search-input"
          />
        </div>
      </div>

      <!-- Courses Grid -->
      <div v-if="filteredCourses.length > 0" class="courses-grid">
        <div v-for="course in filteredCourses" :key="course.id" class="course-card">
          <div class="course-image">
            <img :src="course.thumbnail || '/default-course.jpg'" :alt="course.title" />
            <div class="course-progress-overlay">
              <div class="progress-circle" :style="{ '--progress': course.progress_percentage }">
                <span class="progress-text">{{ Math.round(course.progress_percentage || 0) }}%</span>
              </div>
            </div>
          </div>
          
          <div class="course-content">
            <div class="course-header">
              <h3>{{ course.title }}</h3>
              <div class="course-status" :class="getCourseStatusClass(course)">
                {{ getCourseStatus(course) }}
              </div>
            </div>
            
            <p class="course-instructor">
              by {{ course.instructor?.first_name }} {{ course.instructor?.last_name }}
            </p>
            
            <div class="course-stats">
              <div class="stat">
                <span class="stat-icon">📹</span>
                <span>{{ course.total_lessons || 0 }} lessons</span>
              </div>
              <div class="stat">
                <span class="stat-icon">⏱️</span>
                <span>{{ formatDuration(course.total_duration) }}</span>
              </div>
              <div class="stat">
                <span class="stat-icon">📊</span>
                <span>{{ course.difficulty_level }}</span>
              </div>
            </div>

            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: `${course.progress_percentage || 0}%` }"></div>
            </div>
            
            <div class="course-meta">
              <span class="enrolled-date">
                Enrolled {{ formatDate(course.enrollment_date) }}
              </span>
              <span v-if="course.last_accessed" class="last-accessed">
                Last accessed {{ formatDate(course.last_accessed) }}
              </span>
            </div>
          </div>

          <div class="course-actions">
            <button 
              @click="continueCourse(course)" 
              class="continue-btn"
              :class="{ completed: course.progress_percentage >= 100 }"
            >
              <span class="btn-icon">
                {{ course.progress_percentage >= 100 ? '🏆' : '▶️' }}
              </span>
              {{ course.progress_percentage >= 100 ? 'View Certificate' : 'Continue Learning' }}
            </button>
            
            <div class="action-menu">
              <button @click="toggleActionMenu(course.id)" class="menu-trigger">⋯</button>
              <div v-if="activeMenu === course.id" class="action-dropdown">
                <button @click="viewCourseDetails(course)" class="action-item">
                  <span class="action-icon">👁️</span>
                  View Details
                </button>
                <button @click="downloadMaterials(course)" class="action-item">
                  <span class="action-icon">📄</span>
                  Download Materials
                </button>
                <button @click="viewProgress(course)" class="action-item">
                  <span class="action-icon">📊</span>
                  View Progress
                </button>
                <button @click="leaveFeedback(course)" class="action-item">
                  <span class="action-icon">⭐</span>
                  Leave Review
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="empty-state">
        <div class="empty-icon">📚</div>
        <h3>{{ getEmptyStateTitle() }}</h3>
        <p>{{ getEmptyStateMessage() }}</p>
        <router-link to="/courses" class="browse-courses-btn">
          Browse Available Courses
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useApiData } from '@/composables/useApiData'
// Removed unused import
import { useErrorHandler } from '@/composables/useErrorHandler'

const router = useRouter()
const { handleApiError } = useErrorHandler()

// Reactive state
const activeFilter = ref('all')
const searchQuery = ref('')
const activeMenu = ref<number | null>(null)

// API data
const { 
  data: enrollmentsData, 
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
          course: enrollment.course || {
            id: enrollment.course_id,
            title: enrollment.course_title,
            thumbnail: enrollment.course_thumbnail,
            instructor: {
              first_name: enrollment.instructor_first_name,
              last_name: enrollment.instructor_last_name
            },
            difficulty_level: enrollment.difficulty_level || 'Beginner',
            total_lessons: enrollment.total_lessons || 0,
            total_duration: enrollment.total_duration || 0
          },
          enrollment_date: enrollment.enrolled_at || enrollment.created_at,
          last_accessed: enrollment.last_accessed,
          progress_percentage: enrollment.progress_percentage || 0,
          certificate_earned: enrollment.certificate_earned || false
        }))
      }
    }
    return data
  },
  retryAttempts: 3,
  onError: (error) => {
    console.error('Failed to load enrollments:', error)
  }
})

// Filter tabs
const filterTabs = [
  { label: 'All Courses', value: 'all' },
  { label: 'In Progress', value: 'in_progress' },
  { label: 'Completed', value: 'completed' },
  { label: 'Not Started', value: 'not_started' }
]

// Computed properties
const enrollments = computed(() => enrollmentsData.value?.results || [])

const totalCourses = computed(() => enrollments.value.length)
const completedCourses = computed(() => 
  enrollments.value.filter((e: any) => e.progress_percentage >= 100).length
)
const inProgressCourses = computed(() => 
  enrollments.value.filter((e: any) => e.progress_percentage > 0 && e.progress_percentage < 100).length
)
const earnedCertificates = computed(() => 
  enrollments.value.filter((e: any) => e.certificate_earned).length
)

const filteredCourses = computed(() => {
  let courses = enrollments.value

  // Filter by status
  if (activeFilter.value !== 'all') {
    courses = courses.filter((course: any) => {
      const progress = course.progress_percentage || 0
      switch (activeFilter.value) {
        case 'completed':
          return progress >= 100
        case 'in_progress':
          return progress > 0 && progress < 100
        case 'not_started':
          return progress === 0
        default:
          return true
      }
    })
  }

  // Filter by search query
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    courses = courses.filter((course: any) =>
      course.title?.toLowerCase().includes(query) ||
      course.instructor?.first_name?.toLowerCase().includes(query) ||
      course.instructor?.last_name?.toLowerCase().includes(query)
    )
  }

  return courses.sort((a: any, b: any) => {
    // Sort by last accessed, then by enrollment date
    const aDate = new Date(a.last_accessed || a.enrollment_date)
    const bDate = new Date(b.last_accessed || b.enrollment_date)
    return bDate.getTime() - aDate.getTime()
  })
})

// Methods
const formatDate = (dateString: string) => {
  if (!dateString) return 'Never'
  return new Date(dateString).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  })
}

const formatDuration = (minutes: number) => {
  if (!minutes) return '0 min'
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  if (hours > 0) {
    return `${hours}h ${mins}m`
  }
  return `${mins}m`
}

const getCourseStatus = (course: any) => {
  const progress = course.progress_percentage || 0
  if (progress >= 100) return 'Completed'
  if (progress > 0) return 'In Progress'
  return 'Not Started'
}

const getCourseStatusClass = (course: any) => {
  const progress = course.progress_percentage || 0
  if (progress >= 100) return 'completed'
  if (progress > 0) return 'in-progress'
  return 'not-started'
}

const getEmptyStateTitle = () => {
  if (searchQuery.value) return 'No courses found'
  if (activeFilter.value === 'completed') return 'No completed courses'
  if (activeFilter.value === 'in_progress') return 'No courses in progress'
  if (activeFilter.value === 'not_started') return 'No unstarted courses'
  return 'No enrolled courses'
}

const getEmptyStateMessage = () => {
  if (searchQuery.value) return 'Try adjusting your search terms'
  if (activeFilter.value === 'completed') return 'Complete some courses to see them here'
  if (activeFilter.value === 'in_progress') return 'Start learning to see courses in progress'
  if (activeFilter.value === 'not_started') return 'All your courses have been started'
  return 'Enroll in courses to start your learning journey'
}

const continueCourse = (course: any) => {
  if (course.progress_percentage >= 100) {
    // View certificate
    router.push(`/student/certificates?course=${course.id}`)
  } else {
    // Continue learning
    router.push(`/courses/${course.id}/learn`)
  }
}

const toggleActionMenu = (courseId: number) => {
  activeMenu.value = activeMenu.value === courseId ? null : courseId
}

const viewCourseDetails = (course: any) => {
  router.push(`/courses/${course.id}`)
  activeMenu.value = null
}

const downloadMaterials = async (course: any) => {
  try {
    // Implementation for downloading course materials
    console.log('Download materials for:', course.title)
  } catch (error) {
    handleApiError(error as any, { context: { action: 'download_materials' } })
  }
  activeMenu.value = null
}

const viewProgress = (course: any) => {
  router.push(`/student/progress?course=${course.id}`)
  activeMenu.value = null
}

const leaveFeedback = (course: any) => {
  // Implementation for leaving course feedback
  console.log('Leave feedback for:', course.title)
  activeMenu.value = null
}

const handleRetry = async () => {
  try {
    await refresh()
  } catch (err) {
    handleApiError(err as any, { context: { action: 'retry_courses_load' } })
  }
}

// Close menu when clicking outside
onMounted(() => {
  document.addEventListener('click', (e) => {
    if (!(e.target as Element).closest('.action-menu')) {
      activeMenu.value = null
    }
  })
})
</script>

<style scoped>
.my-courses-view {
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

.progress-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.overview-card {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 1rem;
}

.card-icon {
  font-size: 2.5rem;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  background: linear-gradient(135deg, #f59e0b, #d97706);
}

.card-content h3 {
  font-size: 0.875rem;
  font-weight: 500;
  color: #6b7280;
  margin: 0 0 0.5rem 0;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.card-content .number {
  font-size: 1.875rem;
  font-weight: 700;
  color: #1f2937;
  margin: 0;
}

.course-filters {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.filter-tabs {
  display: flex;
  gap: 0.5rem;
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

.search-bar {
  flex: 1;
  max-width: 300px;
}

.search-input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 1rem;
}

.search-input:focus {
  outline: none;
  border-color: #f59e0b;
  box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.1);
}

.courses-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.course-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: all 0.3s ease;
}

.course-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.15);
}

.course-image {
  position: relative;
  height: 200px;
  overflow: hidden;
}

.course-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.course-progress-overlay {
  position: absolute;
  top: 1rem;
  right: 1rem;
}

.progress-circle {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: conic-gradient(#f59e0b calc(var(--progress) * 1%), #e5e7eb 0);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.progress-circle::before {
  content: '';
  position: absolute;
  width: 45px;
  height: 45px;
  border-radius: 50%;
  background: white;
}

.progress-text {
  position: relative;
  z-index: 1;
  font-size: 0.75rem;
  font-weight: 600;
  color: #1f2937;
}

.course-content {
  padding: 1.5rem;
}

.course-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.5rem;
}

.course-header h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
  line-height: 1.4;
  flex: 1;
}

.course-status {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
  margin-left: 1rem;
}

.course-status.completed {
  background: #dcfce7;
  color: #166534;
}

.course-status.in-progress {
  background: #dbeafe;
  color: #1e40af;
}

.course-status.not-started {
  background: #f3f4f6;
  color: #6b7280;
}

.course-instructor {
  color: #6b7280;
  font-size: 0.875rem;
  margin-bottom: 1rem;
}

.course-stats {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  font-size: 0.875rem;
  color: #6b7280;
}

.stat {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.stat-icon {
  font-size: 1rem;
}

.progress-bar {
  width: 100%;
  height: 6px;
  background: #e5e7eb;
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 1rem;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(135deg, #f59e0b, #d97706);
  transition: width 0.3s ease;
}

.course-meta {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: #9ca3af;
  margin-bottom: 1rem;
}

.course-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-top: 1px solid #f3f4f6;
}

.continue-btn {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.3s ease;
}

.continue-btn.completed {
  background: linear-gradient(135deg, #059669, #047857);
}

.continue-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(245, 158, 11, 0.4);
}

.action-menu {
  position: relative;
}

.menu-trigger {
  background: none;
  border: none;
  font-size: 1.25rem;
  color: #6b7280;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.menu-trigger:hover {
  background: #f3f4f6;
  color: #374151;
}

.action-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
  z-index: 10;
  min-width: 180px;
}

.action-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  width: 100%;
  padding: 0.75rem 1rem;
  border: none;
  background: none;
  color: #374151;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-item:hover {
  background: #f9fafb;
}

.action-item:first-child {
  border-radius: 8px 8px 0 0;
}

.action-item:last-child {
  border-radius: 0 0 8px 8px;
}

.action-icon {
  font-size: 1rem;
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