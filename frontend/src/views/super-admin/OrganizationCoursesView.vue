<template>
  <div class="organization-courses-view">
    <div class="page-header">
      <div class="header-content">
        <router-link :to="`/super-admin/organizations/${organizationId}`" class="back-link">
          ← Back to Organization
        </router-link>
        <h1>{{ organization?.name || 'Loading...' }} - Courses</h1>
        <p class="header-description">
          Manage courses for this organization
        </p>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>Loading courses...</p>
    </div>

    <div v-else-if="error" class="error-state">
      <div class="error-icon">⚠️</div>
      <h3>Failed to load courses</h3>
      <p>{{ error.message }}</p>
      <button @click="loadCourses" class="retry-btn">Try Again</button>
    </div>

    <div v-else class="courses-content">
      <!-- Courses Stats -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon total">
            <i class="fas fa-book"></i>
          </div>
          <div class="stat-content">
            <h3>{{ courses.length }}</h3>
            <p>Total Courses</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon published">
            <i class="fas fa-eye"></i>
          </div>
          <div class="stat-content">
            <h3>{{ publishedCourses.length }}</h3>
            <p>Published</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon draft">
            <i class="fas fa-edit"></i>
          </div>
          <div class="stat-content">
            <h3>{{ draftCourses.length }}</h3>
            <p>Draft</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon enrollments">
            <i class="fas fa-users"></i>
          </div>
          <div class="stat-content">
            <h3>{{ totalEnrollments }}</h3>
            <p>Total Enrollments</p>
          </div>
        </div>
      </div>

      <!-- Filters and Search -->
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
          </select>
          <select v-model="categoryFilter" class="filter-select">
            <option value="">All Categories</option>
            <option
              v-for="category in categories"
              :key="category.id"
              :value="category.id"
            >
              {{ category.name }}
            </option>
          </select>
        </div>
      </div>

      <!-- Courses List -->
      <div class="courses-list">
        <div class="list-header">
          <h3>Courses ({{ filteredCourses.length }})</h3>
        </div>
        
        <div v-if="filteredCourses.length === 0" class="empty-state">
          <i class="fas fa-book-open"></i>
          <h4>No courses found</h4>
          <p>No courses match your current filters.</p>
        </div>

        <div v-else class="courses-grid">
          <div
            v-for="course in paginatedCourses"
            :key="course.id"
            class="course-card"
          >
            <div class="course-image">
              <img
                v-if="course.thumbnail"
                :src="course.thumbnail"
                :alt="course.title"
                class="thumbnail-image"
              />
              <div v-else class="thumbnail-placeholder">
                <i class="fas fa-book"></i>
              </div>
              <div class="course-status" :class="course.is_public ? 'published' : 'draft'">
                {{ course.is_public ? 'Published' : 'Draft' }}
              </div>
            </div>
            
            <div class="course-info">
              <h4>{{ course.title }}</h4>
              <p class="course-description">{{ course.description || 'No description available' }}</p>
              
              <div class="course-meta">
                <div class="meta-item">
                  <i class="fas fa-user"></i>
                  <span>{{ course.instructor_name || 'Unknown' }}</span>
                </div>
                <div class="meta-item">
                  <i class="fas fa-tag"></i>
                  <span>{{ course.category_name || 'Uncategorized' }}</span>
                </div>
                <div class="meta-item">
                  <i class="fas fa-users"></i>
                  <span>{{ course.enrollment_count || 0 }} enrolled</span>
                </div>
                <div class="meta-item">
                  <i class="fas fa-dollar-sign"></i>
                  <span>${{ course.price || 0 }}</span>
                </div>
              </div>

              <div class="course-details">
                <small>Created: {{ formatDate(course.created_at) }}</small>
                <small v-if="course.updated_at !== course.created_at">
                  Updated: {{ formatDate(course.updated_at) }}
                </small>
              </div>
            </div>

            <div class="course-actions">
              <button
                @click="viewCourse(course)"
                class="action-btn view"
                title="View Course"
              >
                <i class="fas fa-eye"></i>
              </button>
              <button
                @click="editCourse(course)"
                class="action-btn edit"
                title="Edit Course"
              >
                <i class="fas fa-edit"></i>
              </button>
              <button
                @click="toggleCourseStatus(course)"
                class="action-btn"
                :class="course.is_public ? 'unpublish' : 'publish'"
                :title="course.is_public ? 'Unpublish' : 'Publish'"
              >
                <i :class="course.is_public ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
              </button>
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
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '@/services/api'
import type { APIError } from '@/services/api'
import { useErrorHandler } from '@/composables/useErrorHandler'

const route = useRoute()
const router = useRouter()
const { handleApiError } = useErrorHandler()

const organizationId = route.params.id as string
const organization = ref(null)
const courses = ref([])
const categories = ref([])
const loading = ref(true)
const error = ref(null)

// Filters
const searchQuery = ref('')
const statusFilter = ref('')
const categoryFilter = ref('')
const currentPage = ref(1)
const itemsPerPage = 12

// Computed properties
const publishedCourses = computed(() => courses.value.filter(course => course.is_public))
const draftCourses = computed(() => courses.value.filter(course => !course.is_public))
const totalEnrollments = computed(() => 
  courses.value.reduce((total, course) => total + (course.enrollment_count || 0), 0)
)

const filteredCourses = computed(() => {
  let filtered = courses.value

  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(course =>
      course.title?.toLowerCase().includes(query) ||
      course.description?.toLowerCase().includes(query) ||
      course.instructor_name?.toLowerCase().includes(query)
    )
  }

  // Status filter
  if (statusFilter.value) {
    const isPublished = statusFilter.value === 'published'
    filtered = filtered.filter(course => course.is_public === isPublished)
  }

  // Category filter
  if (categoryFilter.value) {
    filtered = filtered.filter(course => course.category === categoryFilter.value)
  }

  return filtered
})

const totalPages = computed(() => Math.ceil(filteredCourses.value.length / itemsPerPage))

const paginatedCourses = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return filteredCourses.value.slice(start, end)
})

// Methods
const loadCourses = async () => {
  try {
    loading.value = true
    error.value = null

    // Load organization info
    const orgResponse = await api.get(`/organizations/${organizationId}/`)
    organization.value = orgResponse.data.data || orgResponse.data

    // Load courses for this organization
    const coursesResponse = await api.get(`/organizations/${organizationId}/courses/`)
    courses.value = coursesResponse.data.data || coursesResponse.data || []

    // Load categories
    try {
      const categoriesResponse = await api.get('/categories/')
      categories.value = categoriesResponse.data.data || categoriesResponse.data || []
    } catch (err) {
      console.warn('Failed to load categories:', err)
    }

  } catch (err) {
    error.value = err
    handleApiError(err as APIError, { context: { action: 'load_organization_courses' } })
  } finally {
    loading.value = false
  }
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const viewCourse = (course: any) => {
  // Navigate to course detail page
  window.open(`/courses/${course.id}`, '_blank')
}

const editCourse = (course: any) => {
  // Navigate to course edit page
  console.log('Edit course:', course)
}

const toggleCourseStatus = async (course: any) => {
  try {
    const newStatus = !course.is_public
    await api.patch(`/courses/${course.id}/`, {
      is_public: newStatus
    })
    
    course.is_public = newStatus
  } catch (err) {
    handleApiError(err as APIError, { context: { action: 'toggle_course_status' } })
  }
}

// Lifecycle
onMounted(() => {
  loadCourses()
})
</script>

<style scoped>
.organization-courses-view {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.back-link {
  display: inline-flex;
  align-items: center;
  color: #6b7280;
  text-decoration: none;
  margin-bottom: 1rem;
  font-size: 0.875rem;
  transition: color 0.2s;
}

.back-link:hover {
  color: #374151;
}

.header-content h1 {
  margin: 0 0 0.5rem 0;
  color: #1f2937;
  font-size: 2rem;
  font-weight: 600;
}

.header-description {
  margin: 0;
  color: #6b7280;
  font-size: 1rem;
}

.loading-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f4f6;
  border-top: 4px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.retry-btn {
  padding: 0.75rem 1.5rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  margin-top: 1rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 1.5rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
}

.stat-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  margin-right: 1rem;
  font-size: 1.25rem;
  color: white;
}

.stat-icon.total {
  background: #3b82f6;
}

.stat-icon.published {
  background: #10b981;
}

.stat-icon.draft {
  background: #f59e0b;
}

.stat-icon.enrollments {
  background: #8b5cf6;
}

.stat-content h3 {
  margin: 0 0 0.25rem 0;
  font-size: 1.5rem;
  font-weight: 700;
  color: #1f2937;
}

.stat-content p {
  margin: 0;
  color: #6b7280;
  font-size: 0.875rem;
}

.filters-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  gap: 1rem;
}

.search-bar {
  flex: 1;
  max-width: 400px;
}

.search-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
}

.filter-controls {
  display: flex;
  gap: 0.75rem;
}

.filter-select {
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
  background: white;
}

.courses-list {
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.list-header {
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.list-header h3 {
  margin: 0;
  color: #1f2937;
  font-size: 1.125rem;
  font-weight: 600;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
  color: #6b7280;
}

.empty-state i {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.courses-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 1rem;
  padding: 1.5rem;
}

.course-card {
  display: flex;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.2s;
}

.course-card:hover {
  border-color: #d1d5db;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.course-image {
  position: relative;
  width: 120px;
  height: 120px;
  flex-shrink: 0;
}

.thumbnail-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.thumbnail-placeholder {
  width: 100%;
  height: 100%;
  background: #f3f4f6;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #9ca3af;
  font-size: 2rem;
}

.course-status {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  padding: 0.125rem 0.5rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.course-status.published {
  background: #d1fae5;
  color: #065f46;
}

.course-status.draft {
  background: #fef3c7;
  color: #92400e;
}

.course-info {
  flex: 1;
  padding: 1rem;
  display: flex;
  flex-direction: column;
}

.course-info h4 {
  margin: 0 0 0.5rem 0;
  color: #1f2937;
  font-size: 1rem;
  font-weight: 600;
  line-height: 1.4;
}

.course-description {
  margin: 0 0 0.75rem 0;
  color: #6b7280;
  font-size: 0.875rem;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.course-meta {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
  color: #6b7280;
}

.meta-item i {
  width: 12px;
  color: #9ca3af;
}

.course-details {
  margin-top: auto;
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.course-details small {
  color: #9ca3af;
  font-size: 0.75rem;
}

.course-actions {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  padding: 1rem 0.5rem;
  border-left: 1px solid #e5e7eb;
}

.action-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  color: #6b7280;
  transition: all 0.2s;
}

.action-btn:hover {
  background: #f3f4f6;
  color: #374151;
}

.action-btn.view:hover {
  background: #dbeafe;
  color: #1e40af;
}

.action-btn.edit:hover {
  background: #fef3c7;
  color: #92400e;
}

.action-btn.publish:hover {
  background: #d1fae5;
  color: #065f46;
}

.action-btn.unpublish:hover {
  background: #fee2e2;
  color: #991b1b;
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
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: background 0.2s;
}

.pagination-btn:hover:not(:disabled) {
  background: #2563eb;
}

.pagination-btn:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}

.pagination-info {
  color: #6b7280;
  font-size: 0.875rem;
}
</style>