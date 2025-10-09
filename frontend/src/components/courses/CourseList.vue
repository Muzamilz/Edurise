<template>
  <div class="course-list">
    <!-- Search and Filters -->
    <div class="course-filters">
      <div class="search-bar">
        <input
          v-model="searchQuery"
          @input="onSearch"
          type="text"
          placeholder="Search courses..."
          class="search-input"
        />
        <button @click="onSearch" class="search-btn">
          <i class="icon-search"></i>
        </button>
      </div>
      
      <div class="filters">
        <select v-model="selectedCategory" @change="onFilterChange" class="filter-select">
          <option value="">All Categories</option>
          <option value="technology">Technology</option>
          <option value="business">Business</option>
          <option value="design">Design</option>
          <option value="marketing">Marketing</option>
          <option value="language">Language</option>
          <option value="science">Science</option>
          <option value="other">Other</option>
        </select>
        
        <select v-model="selectedDifficulty" @change="onFilterChange" class="filter-select">
          <option value="">All Levels</option>
          <option value="beginner">Beginner</option>
          <option value="intermediate">Intermediate</option>
          <option value="advanced">Advanced</option>
        </select>
        
        <select v-model="sortBy" @change="onFilterChange" class="filter-select">
          <option value="-created_at">Newest First</option>
          <option value="created_at">Oldest First</option>
          <option value="title">Title A-Z</option>
          <option value="-title">Title Z-A</option>
          <option value="price">Price Low to High</option>
          <option value="-price">Price High to Low</option>
          <option value="-average_rating">Highest Rated</option>
          <option value="-total_enrollments">Most Popular</option>
        </select>
        
        <button @click="clearFilters" class="clear-filters-btn">
          Clear Filters
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading && courses.length === 0" class="loading-state">
      <div class="loading-spinner"></div>
      <p>Loading courses...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="!loading && courses.length === 0" class="empty-state">
      <div class="empty-icon">📚</div>
      <h3>No courses found</h3>
      <p>Try adjusting your search criteria or filters.</p>
    </div>

    <!-- Course Grid -->
    <div v-else class="course-grid">
      <CourseCard
        v-for="course in courses"
        :key="course.id"
        :course="course"
        :is-enrolled="isEnrolledInCourse(course.id)"
        :show-enroll-button="showEnrollButton"
        :show-edit-button="showEditButton"
        :show-delete-button="showDeleteButton"
        :loading="enrollingCourseId === course.id"
        @click="onCourseClick"
        @enroll="onEnroll"
        @continue="onContinue"
        @edit="onEdit"
        @delete="onDelete"
      />
    </div>

    <!-- Load More Button -->
    <div v-if="hasNextPage && !loading" class="load-more">
      <button @click="loadMore" class="load-more-btn">
        Load More Courses
      </button>
    </div>

    <!-- Loading More -->
    <div v-if="loading && courses.length > 0" class="loading-more">
      <div class="loading-spinner small"></div>
      <span>Loading more courses...</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import CourseCard from './CourseCard.vue'
import { useCourse } from '../../composables/useCourse'
import { useCourseStore } from '../../stores/courses'
import type { Course } from '../../types/api'

interface Props {
  showEnrollButton?: boolean
  showEditButton?: boolean
  showDeleteButton?: boolean
  useMarketplace?: boolean
}

interface Emits {
  (e: 'courseClick', course: Course): void
  (e: 'enroll', course: Course): void
  (e: 'continue', course: Course): void
  (e: 'edit', course: Course): void
  (e: 'delete', course: Course): void
}

const props = withDefaults(defineProps<Props>(), {
  showEnrollButton: true,
  showEditButton: false,
  showDeleteButton: false,
  useMarketplace: false
})

const emit = defineEmits<Emits>()

const router = useRouter()
const courseStore = useCourseStore()
const { 
  courses, 
  loading, 
  hasNextPage,
  fetchCourses,
  fetchMarketplaceCourses,
  nextPage,
  updateFilters,
  clearFilters: clearCourseFilters
} = useCourse()

// Local state
const searchQuery = ref('')
const selectedCategory = ref('')
const selectedDifficulty = ref('')
const sortBy = ref('-created_at')
const enrollingCourseId = ref<string | null>(null)

// Computed
const isEnrolledInCourse = computed(() => courseStore.isEnrolledInCourse)

// Methods
const loadCourses = async () => {
  const filters = {
    category: selectedCategory.value || undefined,
    difficulty_level: selectedDifficulty.value || undefined,
    ordering: sortBy.value,
    search: searchQuery.value || undefined
  }

  updateFilters(filters)
  
  if (props.useMarketplace) {
    await fetchMarketplaceCourses()
  } else {
    await fetchCourses()
  }
}

const onSearch = async () => {
  await loadCourses()
}

const onFilterChange = async () => {
  await loadCourses()
}

const clearFilters = async () => {
  searchQuery.value = ''
  selectedCategory.value = ''
  selectedDifficulty.value = ''
  sortBy.value = '-created_at'
  
  clearCourseFilters()
  await loadCourses()
}

const loadMore = async () => {
  await nextPage()
}

// Event handlers
const onCourseClick = (course: Course) => {
  emit('courseClick', course)
  router.push(`/courses/${course.id}`)
}

const onEnroll = async (course: Course) => {
  try {
    enrollingCourseId.value = course.id
    await courseStore.enrollInCourse(course.id)
    emit('enroll', course)
  } catch (error) {
    console.error('Failed to enroll in course:', error)
  } finally {
    enrollingCourseId.value = null
  }
}

const onContinue = (course: Course) => {
  emit('continue', course)
  router.push(`/courses/${course.id}/learn`)
}

const onEdit = (course: Course) => {
  emit('edit', course)
  router.push(`/teacher/courses/${course.id}/edit`)
}

const onDelete = (course: Course) => {
  emit('delete', course)
}

// Lifecycle
onMounted(async () => {
  await loadCourses()
  
  // Load enrolled courses for enrollment status
  if (props.showEnrollButton) {
    await courseStore.fetchEnrollments()
  }
})

// Watch for external changes
watch(() => props.useMarketplace, async () => {
  await loadCourses()
})
</script>

<style scoped>
.course-list {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.course-filters {
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 32px;
}

.search-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.search-input {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid #D1D5DB;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.2s ease;
}

.search-input:focus {
  outline: none;
  border-color: #3B82F6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.search-btn {
  padding: 12px 20px;
  background: #3B82F6;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.search-btn:hover {
  background: #2563EB;
}

.filters {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  align-items: center;
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

.clear-filters-btn {
  padding: 8px 16px;
  background: transparent;
  color: #6B7280;
  border: 1px solid #D1D5DB;
  border-radius: 6px;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.clear-filters-btn:hover {
  background: #F9FAFB;
  border-color: #9CA3AF;
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

.loading-spinner.small {
  width: 20px;
  height: 20px;
  border-width: 2px;
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
  font-size: 1rem;
}

.course-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.load-more {
  text-align: center;
  margin-top: 32px;
}

.load-more-btn {
  padding: 12px 32px;
  background: #3B82F6;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.load-more-btn:hover {
  background: #2563EB;
}

.loading-more {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 20px;
  color: #6B7280;
  font-size: 0.875rem;
}

/* Responsive */
@media (max-width: 768px) {
  .course-list {
    padding: 16px;
  }
  
  .course-filters {
    padding: 20px;
  }
  
  .filters {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-select {
    width: 100%;
  }
  
  .course-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
}

@media (max-width: 480px) {
  .search-bar {
    flex-direction: column;
  }
  
  .search-btn {
    align-self: stretch;
  }
}
</style>