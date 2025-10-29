<template>
  <div class="global-courses-view">
    <div class="page-header">
      <h1>Global Course Management</h1>
      <p>Manage all courses across all organizations on the platform</p>
    </div>

    <!-- Filters and Search -->
    <div class="filters-section">
      <div class="search-bar">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search courses by title, instructor, or organization..."
          class="search-input"
        />
      </div>
      <div class="filter-controls">
        <select v-model="organizationFilter" class="filter-select">
          <option value="">All Organizations</option>
          <option v-for="org in organizations" :key="org.id" :value="org.id">
            {{ org.name }}
          </option>
        </select>
        <select v-model="statusFilter" class="filter-select">
          <option value="">All Status</option>
          <option value="published">Published</option>
          <option value="draft">Draft</option>
          <option value="under_review">Under Review</option>
          <option value="suspended">Suspended</option>
        </select>
        <select v-model="categoryFilter" class="filter-select">
          <option value="">All Categories</option>
          <option value="technology">Technology</option>
          <option value="business">Business</option>
          <option value="design">Design</option>
          <option value="marketing">Marketing</option>
        </select>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>Loading courses...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-state">
      <div class="error-icon">⚠️</div>
      <h3>Failed to load courses</h3>
      <p>{{ error.message }}</p>
      <button @click="handleRetry" class="retry-btn">Try Again</button>
    </div>

    <!-- Courses Grid -->
    <div v-else class="courses-container">
      <div class="courses-header">
        <h2>Courses ({{ filteredCourses.length }})</h2>
        <div class="view-controls">
          <button 
            @click="viewMode = 'grid'" 
            :class="{ active: viewMode === 'grid' }"
            class="view-btn"
          >
            Grid
          </button>
          <button 
            @click="viewMode = 'list'" 
            :class="{ active: viewMode === 'list' }"
            class="view-btn"
          >
            List
          </button>
        </div>
      </div>

      <!-- Grid View -->
      <div v-if="viewMode === 'grid'" class="courses-grid">
        <div v-for="course in paginatedCourses" :key="course.id" class="course-card">
          <div class="course-image">
            <img :src="course.thumbnail || '/default-course.jpg'" :alt="course.title" />
            <div class="course-status" :class="course.status">
              {{ formatStatus(course.status) }}
            </div>
          </div>
          <div class="course-content">
            <div class="course-meta">
              <span class="organization">{{ course.organization?.name }}</span>
              <span class="category">{{ course.category }}</span>
            </div>
            <h3>{{ course.title }}</h3>
            <p class="course-description">{{ course.description }}</p>
            <div class="course-stats">
              <div class="stat">
                <span class="stat-label">Students:</span>
                <span class="stat-value">{{ course.enrollment_count || 0 }}</span>
              </div>
              <div class="stat">
                <span class="stat-label">Rating:</span>
                <span class="stat-value">{{ course.average_rating || 'N/A' }}</span>
              </div>
              <div class="stat">
                <span class="stat-label">Price:</span>
                <span class="stat-value">${{ course.price || 'Free' }}</span>
              </div>
            </div>
            <div class="course-instructor">
              <img :src="course.instructor?.avatar || '/default-avatar.jpg'" :alt="course.instructor?.name" />
              <span>{{ course.instructor?.first_name }} {{ course.instructor?.last_name }}</span>
            </div>
          </div>
          <div class="course-actions">
            <button @click="viewCourse(course)" class="action-btn view">
              View Details
            </button>
            <button @click="moderateCourse(course)" class="action-btn moderate">
              Moderate
            </button>
            <button 
              @click="toggleCourseStatus(course)" 
              :class="course.status === 'published' ? 'suspend' : 'publish'"
              class="action-btn"
            >
              {{ course.status === 'published' ? 'Suspend' : 'Publish' }}
            </button>
          </div>
        </div>
      </div>

      <!-- List View -->
      <div v-else class="courses-table">
        <table>
          <thead>
            <tr>
              <th>Course</th>
              <th>Organization</th>
              <th>Instructor</th>
              <th>Students</th>
              <th>Revenue</th>
              <th>Status</th>
              <th>Created</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="course in paginatedCourses" :key="course.id" class="course-row">
              <td class="course-info">
                <div class="course-thumbnail">
                  <img :src="course.thumbnail || '/default-course.jpg'" :alt="course.title" />
                </div>
                <div class="course-details">
                  <h4>{{ course.title }}</h4>
                  <p>{{ course.category }}</p>
                </div>
              </td>
              <td>{{ course.organization?.name }}</td>
              <td>{{ course.instructor?.first_name }} {{ course.instructor?.last_name }}</td>
              <td>{{ course.enrollment_count || 0 }}</td>
              <td>${{ calculateRevenue(course) }}</td>
              <td>
                <span class="status-badge" :class="course.status">
                  {{ formatStatus(course.status) }}
                </span>
              </td>
              <td>{{ formatDate(course.created_at) }}</td>
              <td class="actions">
                <button @click="viewCourse(course)" class="action-btn view">
                  View
                </button>
                <button @click="moderateCourse(course)" class="action-btn moderate">
                  Moderate
                </button>
                <button 
                  @click="toggleCourseStatus(course)" 
                  :class="course.status === 'published' ? 'suspend' : 'publish'"
                  class="action-btn"
                >
                  {{ course.status === 'published' ? 'Suspend' : 'Publish' }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div class="pagination">
        <button 
          @click="currentPage--" 
          :disabled="currentPage === 1"
          class="pagination-btn"
        >
          Previous
        </button>
        <span class="pagination-info">
          Page {{ currentPage }} of {{ totalPages }}
        </span>
        <button 
          @click="currentPage++" 
          :disabled="currentPage === totalPages"
          class="pagination-btn"
        >
          Next
        </button>
      </div>
    </div>

    <!-- Course Moderation Modal -->
    <div v-if="moderatingCourse" class="modal-overlay" @click="closeModerationModal">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>Moderate Course: {{ moderatingCourse.title }}</h3>
          <button @click="closeModerationModal" class="close-btn">×</button>
        </div>
        <div class="modal-body">
          <div class="moderation-form">
            <div class="form-group">
              <label>Action</label>
              <select v-model="moderationAction">
                <option value="approve">Approve Course</option>
                <option value="request_changes">Request Changes</option>
                <option value="suspend">Suspend Course</option>
                <option value="delete">Delete Course</option>
              </select>
            </div>
            <div class="form-group">
              <label>Reason/Comments</label>
              <textarea 
                v-model="moderationReason" 
                placeholder="Provide reason for this action..."
                rows="4"
              ></textarea>
            </div>
            <div class="form-actions">
              <button @click="closeModerationModal" class="cancel-btn">Cancel</button>
              <button @click="submitModeration" class="submit-btn">
                Submit Action
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useApiData, useApiMutation } from '@/composables/useApiData'
import type { APIError } from '@/services/api'
import { useErrorHandler } from '@/composables/useErrorHandler'

const { handleApiError } = useErrorHandler()

// Data fetching
const { data: courses, loading, error, refresh } = useApiData<any[]>('/courses/', {
  immediate: true,
  transform: (data) => {
    console.log('🔍 Raw courses data:', data)
    
    // Handle both paginated and direct array responses
    const results = data.results || data.data || data || []
    
    return results.map((course: any) => ({
      id: course.id,
      title: course.title || 'Untitled Course',
      instructor_name: course.instructor_name || 'Unknown Instructor',
      organization_name: course.organization_name || 'Unknown Organization',
      price: course.price || 0,
      is_public: course.is_public !== false,
      created_at: course.created_at,
      enrollment_count: course.enrollment_count || 0,
      average_rating: course.average_rating || 0,
      status: course.is_public ? 'published' : 'draft'
    }))
  }
})

const { data: organizations } = useApiData<any[]>('/organizations/', {
  immediate: true,
  transform: (data) => {
    console.log('🔍 Raw organizations data:', data)
    
    const results = data.results || data.data || data || []
    
    return results.map((org: any) => ({
      id: org.id,
      name: org.name || 'Unknown Organization'
    }))
  }
})

// Filters and search
const searchQuery = ref('')
const organizationFilter = ref('')
const statusFilter = ref('')
const categoryFilter = ref('')
const viewMode = ref('grid')
const currentPage = ref(1)
const itemsPerPage = 12

// Moderation state
const moderatingCourse = ref<any>(null)
const moderationAction = ref('approve')
const moderationReason = ref('')

// Course mutations
const { mutate: updateCourseStatus } = useApiMutation(
  ({ id, status, reason }) => ({ 
    method: 'PATCH', 
    url: `/courses/${id}/`, 
    data: { status, moderation_reason: reason } 
  }),
  {
    onSuccess: () => refresh(),
    onError: (error) => handleApiError(error, { context: { action: 'update_course_status' } })
  }
)

const { mutate: moderateCourseAction } = useApiMutation(
  ({ id, action, reason }) => ({ 
    method: 'POST', 
    url: `/courses/${id}/moderate/`, 
    data: { action, reason } 
  }),
  {
    onSuccess: () => {
      closeModerationModal()
      refresh()
    },
    onError: (error) => handleApiError(error, { context: { action: 'moderate_course' } })
  }
)

// Computed properties
const filteredCourses = computed(() => {
  if (!courses.value) return []
  
  return courses.value.filter((course: any) => {
    const matchesSearch = !searchQuery.value || 
      course.title.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      course.description.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      course.instructor?.first_name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      course.instructor?.last_name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      course.organization?.name.toLowerCase().includes(searchQuery.value.toLowerCase())
    
    const matchesOrg = !organizationFilter.value || course.organization?.id === organizationFilter.value
    const matchesStatus = !statusFilter.value || course.status === statusFilter.value
    const matchesCategory = !categoryFilter.value || course.category === categoryFilter.value
    
    return matchesSearch && matchesOrg && matchesStatus && matchesCategory
  })
})

const totalPages = computed(() => Math.ceil(filteredCourses.value.length / itemsPerPage))

const paginatedCourses = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return filteredCourses.value.slice(start, end)
})

// Methods
const formatStatus = (status: string) => {
  return status.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const formatDate = (date: string) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleDateString()
}

const calculateRevenue = (course: any) => {
  return ((course.enrollment_count || 0) * (course.price || 0)).toFixed(2)
}

const viewCourse = (course: any) => {
  window.open(`/courses/${course.id}`, '_blank')
}

const moderateCourse = (course: any) => {
  moderatingCourse.value = course
  moderationAction.value = 'approve'
  moderationReason.value = ''
}

const closeModerationModal = () => {
  moderatingCourse.value = null
  moderationAction.value = 'approve'
  moderationReason.value = ''
}

const submitModeration = async () => {
  if (!moderatingCourse.value) return
  
  await moderateCourseAction({
    id: moderatingCourse.value.id,
    action: moderationAction.value,
    reason: moderationReason.value
  })
}

const toggleCourseStatus = async (course: any) => {
  const newStatus = course.status === 'published' ? 'suspended' : 'published'
  const reason = `Status changed to ${newStatus} by super admin`
  
  await updateCourseStatus({
    id: course.id,
    status: newStatus,
    reason
  })
}

const handleRetry = async () => {
  try {
    await refresh()
  } catch (err) {
    handleApiError(err as APIError, { context: { action: 'retry_courses_load' } })
  }
}

onMounted(() => {
  refresh()
})
</script>

<style scoped>
.global-courses-view {
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

.filters-section {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
}

.search-bar {
  margin-bottom: 1rem;
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

.filter-controls {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.filter-select {
  padding: 0.75rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 1rem;
  min-width: 150px;
}

.courses-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.courses-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.courses-header h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.view-controls {
  display: flex;
  gap: 0.5rem;
}

.view-btn {
  padding: 0.5rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: white;
  color: #374151;
  cursor: pointer;
  transition: all 0.3s ease;
}

.view-btn.active {
  background: #f59e0b;
  color: white;
  border-color: #f59e0b;
}

.courses-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
  padding: 1.5rem;
}

.course-card {
  border: 1px solid #e5e7eb;
  border-radius: 12px;
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

.course-status {
  position: absolute;
  top: 0.75rem;
  right: 0.75rem;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
}

.course-status.published {
  background: #dcfce7;
  color: #166534;
}

.course-status.draft {
  background: #fef3c7;
  color: #92400e;
}

.course-status.under_review {
  background: #dbeafe;
  color: #1e40af;
}

.course-status.suspended {
  background: #fee2e2;
  color: #dc2626;
}

.course-content {
  padding: 1rem;
}

.course-meta {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
  color: #6b7280;
}

.course-content h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.5rem;
  line-height: 1.4;
}

.course-description {
  color: #6b7280;
  font-size: 0.875rem;
  margin-bottom: 1rem;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.course-stats {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1rem;
  font-size: 0.875rem;
}

.stat {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-label {
  color: #6b7280;
  margin-bottom: 0.25rem;
}

.stat-value {
  font-weight: 600;
  color: #1f2937;
}

.course-instructor {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: #6b7280;
}

.course-instructor img {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  object-fit: cover;
}

.course-actions {
  display: flex;
  gap: 0.5rem;
  padding: 1rem;
  border-top: 1px solid #f3f4f6;
}

.action-btn {
  flex: 1;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-btn.view {
  background: #dbeafe;
  color: #1e40af;
}

.action-btn.view:hover {
  background: #bfdbfe;
}

.action-btn.moderate {
  background: #fef3c7;
  color: #92400e;
}

.action-btn.moderate:hover {
  background: #fde68a;
}

.action-btn.publish {
  background: #dcfce7;
  color: #166534;
}

.action-btn.publish:hover {
  background: #bbf7d0;
}

.action-btn.suspend {
  background: #fee2e2;
  color: #dc2626;
}

.action-btn.suspend:hover {
  background: #fecaca;
}

.courses-table {
  overflow-x: auto;
}

.courses-table table {
  width: 100%;
  border-collapse: collapse;
}

.courses-table th {
  background: #f9fafb;
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: #374151;
  border-bottom: 1px solid #e5e7eb;
}

.courses-table td {
  padding: 1rem;
  border-bottom: 1px solid #f3f4f6;
}

.course-row:hover {
  background: #f9fafb;
}

.course-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.course-thumbnail {
  width: 60px;
  height: 40px;
  border-radius: 6px;
  overflow: hidden;
  flex-shrink: 0;
}

.course-thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.course-details h4 {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 0.25rem 0;
}

.course-details p {
  font-size: 0.875rem;
  color: #6b7280;
  margin: 0;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
}

.status-badge.published {
  background: #dcfce7;
  color: #166534;
}

.status-badge.draft {
  background: #fef3c7;
  color: #92400e;
}

.status-badge.under_review {
  background: #dbeafe;
  color: #1e40af;
}

.status-badge.suspended {
  background: #fee2e2;
  color: #dc2626;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  border-top: 1px solid #e5e7eb;
}

.pagination-btn {
  padding: 0.5rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: white;
  color: #374151;
  cursor: pointer;
  transition: all 0.3s ease;
}

.pagination-btn:hover:not(:disabled) {
  background: #f9fafb;
  border-color: #f59e0b;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-info {
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

.form-group select,
.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 1rem;
}

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

.submit-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  cursor: pointer;
  font-weight: 600;
}

.submit-btn:hover {
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