<template>
  <div class="admin-courses-view">
    <div class="page-header">
      <h1>Course Management</h1>
      <p>Manage and moderate courses in your organization</p>
    </div>

    <!-- Filters and Actions -->
    <div class="filters-section">
      <div class="search-bar">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search courses..."
          class="search-input"
        />
      </div>
      <div class="filter-controls">
        <select v-model="statusFilter" class="filter-select">
          <option value="">All Status</option>
          <option value="published">Published</option>
          <option value="draft">Draft</option>
          <option value="pending">Pending Review</option>
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
            :class="['view-btn', { active: viewMode === 'grid' }]"
          >
            Grid
          </button>
          <button 
            @click="viewMode = 'list'" 
            :class="['view-btn', { active: viewMode === 'list' }]"
          >
            List
          </button>
        </div>
      </div>

      <div v-if="filteredCourses.length === 0" class="empty-state">
        <div class="empty-icon">📚</div>
        <h3>No courses found</h3>
        <p>No courses match your current filters</p>
      </div>

      <div v-else :class="['courses-grid', viewMode]">
        <div v-for="course in paginatedCourses" :key="course.id" class="course-card">
          <div class="course-thumbnail">
            <img :src="course.thumbnail || '/placeholder-course.jpg'" :alt="course.title" />
            <div class="course-status" :class="course.status">
              {{ formatStatus(course.status) }}
            </div>
          </div>
          
          <div class="course-content">
            <div class="course-header">
              <h3>{{ course.title }}</h3>
              <div class="course-price">${{ course.price || 0 }}</div>
            </div>
            
            <p class="course-description">{{ truncateText(course.description, 100) }}</p>
            
            <div class="course-meta">
              <div class="meta-item">
                <span class="meta-label">Instructor:</span>
                <span class="meta-value">{{ course.instructor_name }}</span>
              </div>
              <div class="meta-item">
                <span class="meta-label">Category:</span>
                <span class="meta-value">{{ course.category || 'Uncategorized' }}</span>
              </div>
              <div class="meta-item">
                <span class="meta-label">Enrollments:</span>
                <span class="meta-value">{{ course.enrollment_count || 0 }}</span>
              </div>
              <div class="meta-item">
                <span class="meta-label">Rating:</span>
                <div class="rating">
                  <span class="stars">★★★★★</span>
                  <span class="rating-value">{{ (course.average_rating || 0).toFixed(1) }}</span>
                </div>
              </div>
            </div>
            
            <div class="course-actions">
              <button @click="viewCourse(course)" class="action-btn view">
                View
              </button>
              <button @click="editCourse(course)" class="action-btn edit">
                Edit
              </button>
              <button 
                v-if="course.status === 'pending'"
                @click="approveCourse(course)" 
                class="action-btn approve"
              >
                Approve
              </button>
              <button 
                @click="toggleCourseStatus(course)" 
                :class="['action-btn', course.is_public ? 'unpublish' : 'publish']"
              >
                {{ course.is_public ? 'Unpublish' : 'Publish' }}
              </button>
              <button @click="deleteCourse(course)" class="action-btn delete">
                Delete
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="pagination">
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
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useApiData, useApiMutation } from '@/composables/useApiData'
import { useErrorHandler } from '@/composables/useErrorHandler'

const router = useRouter()
const { handleApiError } = useErrorHandler()

// Data fetching
const { data: courses, loading, error, refresh } = useApiData('/courses/')

// Filters and search
const searchQuery = ref('')
const statusFilter = ref('')
const categoryFilter = ref('')
const viewMode = ref('grid')
const currentPage = ref(1)
const itemsPerPage = 12

// Mutations
const { mutate: updateCourse } = useApiMutation(
  ({ id, ...data }) => ({ method: 'PATCH', url: `/api/v1/courses/${id}/`, data }),
  {
    onSuccess: () => refresh(),
    onError: (error) => handleApiError(error, { context: { action: 'update_course' } })
  }
)

const { mutate: deleteCourseApi } = useApiMutation(
  (courseId) => ({ method: 'DELETE', url: `/api/v1/courses/${courseId}/` }),
  {
    onSuccess: () => refresh(),
    onError: (error) => handleApiError(error, { context: { action: 'delete_course' } })
  }
)

// Computed properties
const filteredCourses = computed(() => {
  if (!courses.value) return []
  
  return courses.value.filter(course => {
    const matchesSearch = !searchQuery.value || 
      course.title.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      course.description.toLowerCase().includes(searchQuery.value.toLowerCase())
    
    const matchesStatus = !statusFilter.value || 
      (statusFilter.value === 'published' && course.is_public) ||
      (statusFilter.value === 'draft' && !course.is_public) ||
      (statusFilter.value === 'pending' && course.status === 'pending')
    
    const matchesCategory = !categoryFilter.value || course.category === categoryFilter.value
    
    return matchesSearch && matchesStatus && matchesCategory
  })
})

const totalPages = computed(() => Math.ceil(filteredCourses.value.length / itemsPerPage))

const paginatedCourses = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return filteredCourses.value.slice(start, end)
})

// Methods
const formatStatus = (status) => {
  if (status === 'published') return 'Published'
  if (status === 'draft') return 'Draft'
  if (status === 'pending') return 'Pending'
  return status
}

const truncateText = (text, length) => {
  if (!text) return ''
  return text.length > length ? text.substring(0, length) + '...' : text
}

const viewCourse = (course) => {
  router.push(`/courses/${course.id}`)
}

const editCourse = (course) => {
  router.push(`/teacher/courses/${course.id}/edit`)
}

const approveCourse = async (course) => {
  if (confirm(`Approve "${course.title}" for publication?`)) {
    await updateCourse({ id: course.id, status: 'approved', is_public: true })
  }
}

const toggleCourseStatus = async (course) => {
  const action = course.is_public ? 'unpublish' : 'publish'
  if (confirm(`${action.charAt(0).toUpperCase() + action.slice(1)} "${course.title}"?`)) {
    await updateCourse({ id: course.id, is_public: !course.is_public })
  }
}

const deleteCourse = async (course) => {
  if (confirm(`Are you sure you want to delete "${course.title}"? This action cannot be undone.`)) {
    await deleteCourseApi(course.id)
  }
}

const handleRetry = async () => {
  try {
    await refresh()
  } catch (err) {
    handleApiError(err, { context: { action: 'retry_courses_load' } })
  }
}

onMounted(() => {
  refresh()
})
</script>

<style scoped>
.admin-courses-view {
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
  display: flex;
  gap: 1rem;
  align-items: center;
}

.search-bar {
  flex: 1;
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
  padding: 1.5rem;
}

.courses-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
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
  font-size: 0.875rem;
  transition: all 0.3s ease;
}

.view-btn.active {
  background: #f59e0b;
  color: white;
  border-color: #f59e0b;
}

.courses-grid.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.courses-grid.list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.courses-grid.list .course-card {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
}

.courses-grid.list .course-thumbnail {
  width: 200px;
  height: 120px;
  flex-shrink: 0;
}

.courses-grid.list .course-content {
  flex: 1;
}

.course-card {
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.course-card:hover {
  border-color: #f59e0b;
  box-shadow: 0 4px 15px rgba(245, 158, 11, 0.1);
}

.course-thumbnail {
  position: relative;
  height: 200px;
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
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
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

.course-status.pending {
  background: #fee2e2;
  color: #dc2626;
}

.course-content {
  padding: 1.5rem;
}

.course-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.course-header h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
  flex: 1;
}

.course-price {
  font-size: 1.25rem;
  font-weight: 700;
  color: #10b981;
  margin-left: 1rem;
}

.course-description {
  color: #6b7280;
  font-size: 0.875rem;
  line-height: 1.5;
  margin-bottom: 1rem;
}

.course-meta {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
}

.meta-label {
  color: #6b7280;
  font-weight: 500;
}

.meta-value {
  color: #1f2937;
  font-weight: 600;
}

.rating {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.stars {
  color: #fbbf24;
  font-size: 0.75rem;
}

.rating-value {
  font-weight: 600;
  color: #1f2937;
}

.course-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.action-btn {
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

.action-btn.edit {
  background: #fef3c7;
  color: #92400e;
}

.action-btn.edit:hover {
  background: #fde68a;
}

.action-btn.approve {
  background: #dcfce7;
  color: #166534;
}

.action-btn.approve:hover {
  background: #bbf7d0;
}

.action-btn.publish {
  background: #dcfce7;
  color: #166534;
}

.action-btn.publish:hover {
  background: #bbf7d0;
}

.action-btn.unpublish {
  background: #fef3c7;
  color: #92400e;
}

.action-btn.unpublish:hover {
  background: #fde68a;
}

.action-btn.delete {
  background: #fee2e2;
  color: #dc2626;
}

.action-btn.delete:hover {
  background: #fecaca;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 2rem;
  padding-top: 1.5rem;
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

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
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