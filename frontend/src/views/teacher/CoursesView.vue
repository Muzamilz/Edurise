<template>
  <div class="teacher-courses-view">
    <!-- Header -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">My Courses</h1>
        <p class="page-subtitle">Manage your courses and track student progress</p>
      </div>
      <div class="header-actions">
        <router-link to="/teacher/courses/create" class="btn btn-primary">
          <i class="icon-plus"></i>
          Create Course
        </router-link>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="stats-section" v-if="analytics">
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon">📚</div>
          <div class="stat-content">
            <div class="stat-number">{{ analytics.total_courses }}</div>
            <div class="stat-label">Total Courses</div>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon">👥</div>
          <div class="stat-content">
            <div class="stat-number">{{ analytics.total_students }}</div>
            <div class="stat-label">Total Students</div>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon">⭐</div>
          <div class="stat-content">
            <div class="stat-number">{{ analytics.average_rating.toFixed(1) }}</div>
            <div class="stat-label">Average Rating</div>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon">💰</div>
          <div class="stat-content">
            <div class="stat-number">${{ analytics.total_revenue.toFixed(2) }}</div>
            <div class="stat-label">Total Revenue</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Courses Section -->
    <div class="courses-section">
      <div class="section-header">
        <h2 class="section-title">Your Courses</h2>
        <div class="section-actions">
          <div class="search-bar">
            <input
              v-model="searchQuery"
              @input="handleSearch"
              type="text"
              placeholder="Search your courses..."
              class="search-input"
            />
          </div>
          <select v-model="statusFilter" @change="handleFilter" class="filter-select">
            <option value="">All Courses</option>
            <option value="published">Published</option>
            <option value="draft">Draft</option>
          </select>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading && courses.length === 0" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Loading your courses...</p>
      </div>

      <!-- Empty State -->
      <div v-else-if="!loading && courses.length === 0" class="empty-state">
        <div class="empty-icon">📚</div>
        <h3>No courses yet</h3>
        <p>Create your first course to start teaching and earning.</p>
        <router-link to="/teacher/courses/create" class="btn btn-primary">
          Create Your First Course
        </router-link>
      </div>

      <!-- Courses Grid -->
      <div v-else class="courses-grid">
        <div
          v-for="course in filteredCourses"
          :key="course.id"
          class="course-card"
        >
          <div class="course-image">
            <img 
              :src="course.thumbnail || '/placeholder-course.jpg'" 
              :alt="course.title"
              class="course-thumbnail"
            />
            <div class="course-status" :class="course.is_public ? 'published' : 'draft'">
              {{ course.is_public ? 'Published' : 'Draft' }}
            </div>
          </div>
          
          <div class="course-content">
            <h3 class="course-title">{{ course.title }}</h3>
            <p class="course-description">
              {{ truncateText(course.description, 100) }}
            </p>
            
            <div class="course-meta">
              <div class="meta-item">
                <span class="meta-label">Students:</span>
                <span class="meta-value">{{ course.total_enrollments }}</span>
              </div>
              <div class="meta-item" v-if="course.average_rating > 0">
                <span class="meta-label">Rating:</span>
                <span class="meta-value">{{ course.average_rating.toFixed(1) }}★</span>
              </div>
              <div class="meta-item">
                <span class="meta-label">Price:</span>
                <span class="meta-value">
                  {{ course.price ? `$${course.price}` : 'Free' }}
                </span>
              </div>
            </div>
            
            <div class="course-tags" v-if="course.tags && course.tags.length > 0">
              <span 
                v-for="tag in course.tags.slice(0, 3)" 
                :key="tag"
                class="tag"
              >
                {{ tag }}
              </span>
            </div>
          </div>
          
          <div class="course-actions">
            <button
              @click="viewCourse(course)"
              class="btn btn-outline btn-small"
            >
              View
            </button>
            <button
              @click="editCourse(course)"
              class="btn btn-primary btn-small"
            >
              Edit
            </button>
            <button
              @click="duplicateCourse(course)"
              class="btn btn-secondary btn-small"
              :disabled="duplicating === course.id"
            >
              {{ duplicating === course.id ? 'Duplicating...' : 'Duplicate' }}
            </button>
            <button
              @click="showDeleteConfirm(course)"
              class="btn btn-danger btn-small"
            >
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="courseToDelete" class="modal-overlay" @click="cancelDelete">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>Delete Course</h3>
        </div>
        <div class="modal-body">
          <p>Are you sure you want to delete "{{ courseToDelete.title }}"?</p>
          <p class="warning-text">This action cannot be undone.</p>
        </div>
        <div class="modal-actions">
          <button @click="cancelDelete" class="btn btn-outline">
            Cancel
          </button>
          <button 
            @click="confirmDelete" 
            class="btn btn-danger"
            :disabled="deleting"
          >
            {{ deleting ? 'Deleting...' : 'Delete Course' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCourseStore } from '../../stores/courses'
import type { Course } from '../../types/api'

const router = useRouter()
const courseStore = useCourseStore()

// Local state
const searchQuery = ref('')
const statusFilter = ref('')
const courseToDelete = ref<Course | null>(null)
const duplicating = ref<string | null>(null)
const deleting = ref(false)

// Computed
const courses = computed(() => courseStore.myCourses)
const analytics = computed(() => courseStore.instructorAnalytics)
const loading = computed(() => courseStore.loading)

const filteredCourses = computed(() => {
  let filtered = courses.value

  // Filter by search query
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(course =>
      course.title.toLowerCase().includes(query) ||
      course.description.toLowerCase().includes(query) ||
      course.tags.some(tag => tag.toLowerCase().includes(query))
    )
  }

  // Filter by status
  if (statusFilter.value) {
    if (statusFilter.value === 'published') {
      filtered = filtered.filter(course => course.is_public)
    } else if (statusFilter.value === 'draft') {
      filtered = filtered.filter(course => !course.is_public)
    }
  }

  return filtered
})

// Methods
const handleSearch = () => {
  // Search is reactive through computed property
}

const handleFilter = () => {
  // Filter is reactive through computed property
}

const viewCourse = (course: Course) => {
  router.push(`/courses/${course.id}`)
}

const editCourse = (course: Course) => {
  router.push(`/teacher/courses/${course.id}/edit`)
}

const duplicateCourse = async (course: Course) => {
  try {
    duplicating.value = course.id
    await courseStore.duplicateCourse(course.id)
    // Show success message
  } catch (error) {
    console.error('Failed to duplicate course:', error)
    // Show error message
  } finally {
    duplicating.value = null
  }
}

const showDeleteConfirm = (course: Course) => {
  courseToDelete.value = course
}

const cancelDelete = () => {
  courseToDelete.value = null
}

const confirmDelete = async () => {
  if (!courseToDelete.value) return

  try {
    deleting.value = true
    await courseStore.deleteCourse(courseToDelete.value.id)
    courseToDelete.value = null
    // Show success message
  } catch (error) {
    console.error('Failed to delete course:', error)
    // Show error message
  } finally {
    deleting.value = false
  }
}

const truncateText = (text: string, maxLength: number) => {
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

// Lifecycle
onMounted(async () => {
  await Promise.all([
    courseStore.fetchMyCourses(),
    courseStore.fetchInstructorAnalytics()
  ])
})
</script>

<style scoped>
.teacher-courses-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 40px;
  padding-bottom: 20px;
  border-bottom: 1px solid #E5E7EB;
}

.header-content h1 {
  font-size: 2rem;
  font-weight: 700;
  color: #111827;
  margin-bottom: 8px;
}

.page-subtitle {
  color: #6B7280;
  font-size: 1rem;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.btn {
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-small {
  padding: 6px 12px;
  font-size: 0.75rem;
}

.btn-primary {
  background: #3B82F6;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2563EB;
}

.btn-secondary {
  background: #10B981;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: #059669;
}

.btn-outline {
  background: transparent;
  color: #6B7280;
  border: 1px solid #D1D5DB;
}

.btn-outline:hover:not(:disabled) {
  background: #F9FAFB;
  border-color: #9CA3AF;
}

.btn-danger {
  background: #EF4444;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background: #DC2626;
}

.stats-section {
  margin-bottom: 40px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  font-size: 2rem;
  width: 60px;
  height: 60px;
  background: #F3F4F6;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-content {
  flex: 1;
}

.stat-number {
  font-size: 1.75rem;
  font-weight: 700;
  color: #111827;
  line-height: 1;
  margin-bottom: 4px;
}

.stat-label {
  color: #6B7280;
  font-size: 0.875rem;
  font-weight: 500;
}

.courses-section {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.section-header {
  padding: 24px;
  border-bottom: 1px solid #E5E7EB;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
  margin: 0;
}

.section-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.search-bar {
  position: relative;
}

.search-input {
  padding: 8px 12px;
  border: 1px solid #D1D5DB;
  border-radius: 6px;
  font-size: 0.875rem;
  width: 200px;
}

.search-input:focus {
  outline: none;
  border-color: #3B82F6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.filter-select {
  padding: 8px 12px;
  border: 1px solid #D1D5DB;
  border-radius: 6px;
  font-size: 0.875rem;
  background: white;
  cursor: pointer;
}

.filter-select:focus {
  outline: none;
  border-color: #3B82F6;
}

.loading-state, .empty-state {
  text-align: center;
  padding: 60px 20px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #F3F4F6;
  border-top: 4px solid #3B82F6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.empty-state .empty-icon {
  font-size: 4rem;
  margin-bottom: 16px;
}

.empty-state h3 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #111827;
  margin-bottom: 8px;
}

.empty-state p {
  color: #6B7280;
  margin-bottom: 24px;
}

.courses-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
  padding: 24px;
}

.course-card {
  border: 1px solid #E5E7EB;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.course-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.course-image {
  position: relative;
  height: 180px;
  overflow: hidden;
}

.course-thumbnail {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.course-status {
  position: absolute;
  top: 12px;
  right: 12px;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
}

.course-status.published {
  background: rgba(16, 185, 129, 0.9);
  color: white;
}

.course-status.draft {
  background: rgba(245, 158, 11, 0.9);
  color: white;
}

.course-content {
  padding: 20px;
}

.course-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #111827;
  margin-bottom: 8px;
  line-height: 1.4;
}

.course-description {
  color: #6B7280;
  font-size: 0.875rem;
  line-height: 1.5;
  margin-bottom: 16px;
}

.course-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 16px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.75rem;
}

.meta-label {
  color: #6B7280;
  font-weight: 500;
}

.meta-value {
  color: #374151;
  font-weight: 600;
}

.course-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.tag {
  background: #F3F4F6;
  color: #6B7280;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 500;
}

.course-actions {
  padding: 16px 20px;
  border-top: 1px solid #F3F4F6;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

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
  max-width: 400px;
  width: 90%;
  max-height: 90vh;
  overflow: auto;
}

.modal-header {
  padding: 20px 24px 0;
}

.modal-header h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
  margin: 0;
}

.modal-body {
  padding: 20px 24px;
}

.modal-body p {
  color: #374151;
  margin-bottom: 8px;
}

.warning-text {
  color: #EF4444;
  font-size: 0.875rem;
  font-weight: 500;
}

.modal-actions {
  padding: 0 24px 24px;
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

/* Responsive */
@media (max-width: 768px) {
  .teacher-courses-view {
    padding: 16px;
  }
  
  .page-header {
    flex-direction: column;
    gap: 20px;
    align-items: stretch;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .section-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .section-actions {
    flex-direction: column;
    gap: 12px;
  }
  
  .search-input {
    width: 100%;
  }
  
  .courses-grid {
    grid-template-columns: 1fr;
    gap: 16px;
    padding: 16px;
  }
  
  .course-actions {
    flex-direction: column;
  }
}
</style>