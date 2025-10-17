<template>
  <div class="assignment-list">
    <!-- Header with filters and actions -->
    <div class="bg-white rounded-lg shadow-sm border p-6 mb-6">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-4">
        <h2 class="text-xl font-semibold text-gray-900">Assignments</h2>
        
        <div class="mt-4 sm:mt-0 flex space-x-3">
          <button
            v-if="canCreateAssignment"
            @click="$emit('create-assignment')"
            class="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            Create Assignment
          </button>
        </div>
      </div>
      
      <!-- Filters -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label for="status-filter" class="block text-sm font-medium text-gray-700 mb-1">
            Status
          </label>
          <select
            id="status-filter"
            v-model="assignmentFilters.status"
            class="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">All Statuses</option>
            <option value="draft">Draft</option>
            <option value="published">Published</option>
            <option value="closed">Closed</option>
            <option value="archived">Archived</option>
          </select>
        </div>
        
        <div>
          <label for="type-filter" class="block text-sm font-medium text-gray-700 mb-1">
            Type
          </label>
          <select
            id="type-filter"
            v-model="assignmentFilters.assignment_type"
            class="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">All Types</option>
            <option value="essay">Essay</option>
            <option value="project">Project</option>
            <option value="quiz">Quiz</option>
            <option value="presentation">Presentation</option>
            <option value="code">Code Assignment</option>
            <option value="other">Other</option>
          </select>
        </div>
        
        <div>
          <label for="required-filter" class="block text-sm font-medium text-gray-700 mb-1">
            Required
          </label>
          <select
            id="required-filter"
            v-model="assignmentFilters.is_required"
            class="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">All</option>
            <option :value="true">Required</option>
            <option :value="false">Optional</option>
          </select>
        </div>
        
        <div>
          <label for="search" class="block text-sm font-medium text-gray-700 mb-1">
            Search
          </label>
          <input
            id="search"
            v-model="assignmentFilters.search"
            type="text"
            placeholder="Search assignments..."
            class="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
      </div>
    </div>

    <!-- Loading state -->
    <div v-if="loading" class="flex justify-center py-8">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
    </div>

    <!-- Assignment cards -->
    <div v-else-if="assignments.length > 0" class="space-y-4">
      <div
        v-for="assignment in assignments"
        :key="assignment.id"
        :id="`assignment-${assignment.id}`"
        class="bg-white rounded-lg shadow-sm border hover:shadow-md transition-shadow duration-200"
      >
        <div class="p-6">
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <div class="flex items-center space-x-3 mb-2">
                <h3 class="text-lg font-semibold text-gray-900">
                  {{ assignment.title }}
                </h3>
                
                <!-- Status badge -->
                <span
                  :class="getStatusBadgeClass(assignment.status)"
                  class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                >
                  {{ assignment.status.charAt(0).toUpperCase() + assignment.status.slice(1) }}
                </span>
                
                <!-- Overdue badge -->
                <span
                  v-if="assignment.is_overdue && assignment.status === 'published'"
                  class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800"
                >
                  Overdue
                </span>
                
                <!-- Required badge -->
                <span
                  v-if="assignment.is_required"
                  class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                >
                  Required
                </span>
              </div>
              
              <p class="text-gray-600 mb-3 line-clamp-2">
                {{ assignment.description }}
              </p>
              
              <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-500">
                <div>
                  <span class="font-medium">Type:</span>
                  {{ formatAssignmentType(assignment.assignment_type) }}
                </div>
                <div>
                  <span class="font-medium">Due:</span>
                  {{ formatDueDate(assignment.due_date) }}
                </div>
                <div>
                  <span class="font-medium">Max Score:</span>
                  {{ assignment.max_score }}
                </div>
                <div>
                  <span class="font-medium">Weight:</span>
                  {{ assignment.weight_percentage }}%
                </div>
              </div>
              
              <!-- Progress bar for instructors -->
              <div v-if="showProgress" class="mt-4">
                <div class="flex items-center justify-between text-sm text-gray-600 mb-1">
                  <span>Submissions</span>
                  <span>{{ assignment.graded_submission_count }}/{{ assignment.submission_count }}</span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-2">
                  <div
                    class="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    :style="{ width: `${getProgressPercentage(assignment)}%` }"
                  ></div>
                </div>
              </div>
              
              <!-- Time remaining for students -->
              <div v-if="!showProgress && assignment.status === 'published'" class="mt-3">
                <div
                  :class="getTimeRemainingClass(assignment)"
                  class="text-sm font-medium"
                >
                  {{ formatTimeRemaining(assignment.due_date) }}
                </div>
              </div>
            </div>
            
            <!-- Actions dropdown -->
            <div class="relative ml-4">
              <button
                @click="toggleDropdown(assignment.id)"
                class="p-2 text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded-md"
              >
                <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z" />
                </svg>
              </button>
              
              <div
                v-if="activeDropdown === assignment.id"
                class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg z-10 border"
              >
                <div class="py-1">
                  <button
                    @click="$emit('view-assignment', assignment)"
                    class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    View Details
                  </button>
                  
                  <button
                    v-if="canEditAssignment(assignment)"
                    @click="$emit('edit-assignment', assignment)"
                    class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    Edit
                  </button>
                  
                  <button
                    v-if="canPublishAssignment(assignment)"
                    @click="handlePublishAssignment(assignment)"
                    class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    Publish
                  </button>
                  
                  <button
                    v-if="canCloseAssignment(assignment)"
                    @click="handleCloseAssignment(assignment)"
                    class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    Close
                  </button>
                  
                  <button
                    v-if="showProgress"
                    @click="$emit('view-submissions', assignment)"
                    class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    View Submissions ({{ assignment.submission_count }})
                  </button>
                  
                  <button
                    v-if="!showProgress && assignment.status === 'published'"
                    @click="$emit('start-submission', assignment)"
                    class="block w-full text-left px-4 py-2 text-sm text-blue-600 hover:bg-blue-50"
                  >
                    Start Submission
                  </button>
                  
                  <div class="border-t border-gray-100"></div>
                  
                  <button
                    v-if="canDeleteAssignment(assignment)"
                    @click="handleDeleteAssignment(assignment)"
                    class="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty state -->
    <div v-else class="text-center py-12">
      <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
      <h3 class="mt-2 text-sm font-medium text-gray-900">No assignments</h3>
      <p class="mt-1 text-sm text-gray-500">
        {{ canCreateAssignment ? 'Get started by creating a new assignment.' : 'No assignments have been created yet.' }}
      </p>
      <div v-if="canCreateAssignment" class="mt-6">
        <button
          @click="$emit('create-assignment')"
          class="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Create Assignment
        </button>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="mt-6 flex items-center justify-between">
      <div class="text-sm text-gray-700">
        Showing {{ ((currentPage - 1) * 20) + 1 }} to {{ Math.min(currentPage * 20, totalCount) }} of {{ totalCount }} results
      </div>
      
      <div class="flex space-x-2">
        <button
          @click="goToPage(currentPage - 1)"
          :disabled="!hasPrevious"
          class="px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Previous
        </button>
        
        <button
          @click="goToPage(currentPage + 1)"
          :disabled="!hasNext"
          class="px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Next
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useAssignments } from '../../composables/useAssignments'
import { useAuth } from '../../composables/useAuth'
import type { Assignment } from '../../types/assignments'

interface Props {
  courseId?: string
  showProgress?: boolean // Show progress for instructors
}

interface Emits {
  (e: 'create-assignment'): void
  (e: 'edit-assignment', assignment: Assignment): void
  (e: 'view-assignment', assignment: Assignment): void
  (e: 'view-submissions', assignment: Assignment): void
  (e: 'start-submission', assignment: Assignment): void
}

const props = withDefaults(defineProps<Props>(), {
  showProgress: false
})

defineEmits<Emits>()

const { user } = useAuth()
const {
  assignments,
  loading,
  assignmentFilters,
  currentPage,
  totalPages,
  totalCount,
  hasNext,
  hasPrevious,

  fetchAssignments,
  publishAssignment,
  closeAssignment,
  deleteAssignment,
  formatTimeRemaining,
  startDeadlineReminderAnimations
} = useAssignments()

const activeDropdown = ref<string | null>(null)

// Computed properties
const canCreateAssignment = computed(() => {
  return user.value?.is_teacher || user.value?.is_staff
})

// Initialize filters
onMounted(() => {
  if (props.courseId) {
    assignmentFilters.value.course = props.courseId
  }
  fetchAssignments(assignmentFilters.value)
  
  // Start deadline reminder animations after a delay
  setTimeout(() => {
    startDeadlineReminderAnimations()
  }, 2000)
})

// Close dropdown when clicking outside
const handleClickOutside = (event: Event) => {
  const target = event.target as HTMLElement
  if (!target.closest('.relative')) {
    activeDropdown.value = null
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

// Methods
const toggleDropdown = (assignmentId: string) => {
  activeDropdown.value = activeDropdown.value === assignmentId ? null : assignmentId
}

const canEditAssignment = (assignment: Assignment) => {
  return (user.value?.is_teacher || user.value?.is_staff) && assignment.status !== 'archived'
}

const canPublishAssignment = (assignment: Assignment) => {
  return (user.value?.is_teacher || user.value?.is_staff) && assignment.status === 'draft'
}

const canCloseAssignment = (assignment: Assignment) => {
  return (user.value?.is_teacher || user.value?.is_staff) && assignment.status === 'published'
}

const canDeleteAssignment = (assignment: Assignment) => {
  return (user.value?.is_teacher || user.value?.is_staff) && assignment.status === 'draft'
}

const handlePublishAssignment = async (assignment: Assignment) => {
  try {
    await publishAssignment(assignment.id)
    activeDropdown.value = null
  } catch (error) {
    // Error handled by composable
  }
}

const handleCloseAssignment = async (assignment: Assignment) => {
  if (confirm('Are you sure you want to close this assignment? Students will no longer be able to submit.')) {
    try {
      await closeAssignment(assignment.id)
      activeDropdown.value = null
    } catch (error) {
      // Error handled by composable
    }
  }
}

const handleDeleteAssignment = async (assignment: Assignment) => {
  if (confirm('Are you sure you want to delete this assignment? This action cannot be undone.')) {
    try {
      await deleteAssignment(assignment.id)
      activeDropdown.value = null
    } catch (error) {
      // Error handled by composable
    }
  }
}

const getStatusBadgeClass = (status: string) => {
  const classes = {
    draft: 'bg-gray-100 text-gray-800',
    published: 'bg-green-100 text-green-800',
    closed: 'bg-orange-100 text-orange-800',
    archived: 'bg-gray-100 text-gray-800'
  }
  return classes[status as keyof typeof classes] || 'bg-gray-100 text-gray-800'
}

const getTimeRemainingClass = (assignment: Assignment) => {
  if (assignment.is_overdue) return 'text-red-600'
  if (assignment.days_until_due <= 1) return 'text-red-600'
  if (assignment.days_until_due <= 3) return 'text-orange-600'
  if (assignment.days_until_due <= 7) return 'text-yellow-600'
  return 'text-green-600'
}

const formatAssignmentType = (type: string) => {
  const types = {
    essay: 'Essay',
    project: 'Project',
    quiz: 'Quiz',
    presentation: 'Presentation',
    code: 'Code Assignment',
    other: 'Other'
  }
  return types[type as keyof typeof types] || type
}

const formatDueDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const getProgressPercentage = (assignment: Assignment) => {
  if (assignment.submission_count === 0) return 0
  return Math.round((assignment.graded_submission_count / assignment.submission_count) * 100)
}

const goToPage = (page: number) => {
  currentPage.value = page
  fetchAssignments(assignmentFilters.value)
}
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Animation for assignment cards */
.assignment-list > div:not(.text-center) > div {
  animation: slideInUp 0.3s ease-out;
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>