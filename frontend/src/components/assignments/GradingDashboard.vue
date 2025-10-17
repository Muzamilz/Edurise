<template>
  <div class="grading-dashboard">
    <!-- Header -->
    <div class="bg-white rounded-lg shadow-sm border p-6 mb-6">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 class="text-xl font-semibold text-gray-900">{{ assignment.title }}</h2>
          <p class="text-sm text-gray-600 mt-1">Grading Dashboard</p>
        </div>
        
        <div class="mt-4 sm:mt-0 flex space-x-3">
          <button
            @click="exportGrades"
            class="inline-flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Export Grades
          </button>
          
          <button
            @click="showBulkGrading = !showBulkGrading"
            class="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
            </svg>
            Bulk Grade
          </button>
        </div>
      </div>
      
      <!-- Assignment Stats -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
        <div class="text-center p-4 bg-gray-50 rounded-lg">
          <div class="text-2xl font-bold text-gray-900">{{ assignment.submission_count }}</div>
          <div class="text-sm text-gray-600">Total Submissions</div>
        </div>
        <div class="text-center p-4 bg-blue-50 rounded-lg">
          <div class="text-2xl font-bold text-blue-600">{{ assignment.graded_submission_count }}</div>
          <div class="text-sm text-gray-600">Graded</div>
        </div>
        <div class="text-center p-4 bg-yellow-50 rounded-lg">
          <div class="text-2xl font-bold text-yellow-600">{{ pendingSubmissions.length }}</div>
          <div class="text-sm text-gray-600">Pending</div>
        </div>
        <div class="text-center p-4 bg-red-50 rounded-lg">
          <div class="text-2xl font-bold text-red-600">{{ lateSubmissions.length }}</div>
          <div class="text-sm text-gray-600">Late</div>
        </div>
      </div>
    </div>

    <!-- Bulk Grading Panel -->
    <div v-if="showBulkGrading" class="bg-white rounded-lg shadow-sm border p-6 mb-6">
      <h3 class="text-lg font-semibold text-gray-900 mb-4">Bulk Grading</h3>
      
      <div class="space-y-4">
        <div class="flex items-center space-x-4">
          <div class="flex items-center">
            <input
              id="select-all"
              v-model="selectAll"
              type="checkbox"
              @change="toggleSelectAll"
              class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label for="select-all" class="ml-2 text-sm text-gray-700">
              Select All ({{ selectedSubmissions.length }} selected)
            </label>
          </div>
          
          <div class="flex items-center space-x-2">
            <input
              v-model.number="bulkScore"
              type="number"
              :min="0"
              :max="assignment.max_score"
              placeholder="Score"
              class="w-20 px-2 py-1 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
            <input
              v-model="bulkFeedback"
              type="text"
              placeholder="Feedback (optional)"
              class="flex-1 px-3 py-1 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
            <button
              @click="handleBulkGrade"
              :disabled="selectedSubmissions.length === 0 || !bulkScore || grading"
              class="px-4 py-1 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              {{ grading ? 'Grading...' : 'Grade Selected' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-lg shadow-sm border p-6 mb-6">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label for="status-filter" class="block text-sm font-medium text-gray-700 mb-1">
            Status
          </label>
          <select
            id="status-filter"
            v-model="submissionFilters.status"
            class="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">All Statuses</option>
            <option value="submitted">Submitted</option>
            <option value="late">Late</option>
            <option value="graded">Graded</option>
            <option value="returned">Returned</option>
          </select>
        </div>
        
        <div>
          <label for="graded-filter" class="block text-sm font-medium text-gray-700 mb-1">
            Grading Status
          </label>
          <select
            id="graded-filter"
            v-model="submissionFilters.is_graded"
            class="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">All</option>
            <option :value="false">Ungraded</option>
            <option :value="true">Graded</option>
          </select>
        </div>
        
        <div>
          <label for="late-filter" class="block text-sm font-medium text-gray-700 mb-1">
            Late Status
          </label>
          <select
            id="late-filter"
            v-model="submissionFilters.is_late"
            class="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">All</option>
            <option :value="false">On Time</option>
            <option :value="true">Late</option>
          </select>
        </div>
        
        <div>
          <label for="search" class="block text-sm font-medium text-gray-700 mb-1">
            Search Student
          </label>
          <input
            id="search"
            v-model="submissionFilters.search"
            type="text"
            placeholder="Search by name or email..."
            class="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
      </div>
    </div>

    <!-- Loading state -->
    <div v-if="loading" class="flex justify-center py-8">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
    </div>

    <!-- Submissions List -->
    <div v-else-if="submissions.length > 0" class="space-y-4">
      <div
        v-for="submission in submissions"
        :key="submission.id"
        class="bg-white rounded-lg shadow-sm border hover:shadow-md transition-shadow duration-200"
      >
        <div class="p-6">
          <div class="flex items-start justify-between">
            <div class="flex items-start space-x-4 flex-1">
              <!-- Selection checkbox for bulk grading -->
              <div v-if="showBulkGrading" class="pt-1">
                <input
                  :id="`select-${submission.id}`"
                  v-model="selectedSubmissions"
                  :value="submission.id"
                  type="checkbox"
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
              </div>
              
              <!-- Student Info -->
              <div class="flex-1">
                <div class="flex items-center space-x-3 mb-2">
                  <h3 class="text-lg font-semibold text-gray-900">
                    {{ submission.student.first_name }} {{ submission.student.last_name }}
                  </h3>
                  <span class="text-sm text-gray-600">{{ submission.student.email }}</span>
                  
                  <!-- Status badges -->
                  <span
                    :class="getSubmissionStatusClass(submission)"
                    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                  >
                    {{ submission.status.charAt(0).toUpperCase() + submission.status.slice(1) }}
                  </span>
                  
                  <span
                    v-if="submission.is_late"
                    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800"
                  >
                    Late
                  </span>
                </div>
                
                <!-- Submission details -->
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-600 mb-4">
                  <div>
                    <span class="font-medium">Submitted:</span>
                    {{ submission.submitted_at ? formatDate(submission.submitted_at) : 'Not submitted' }}
                  </div>
                  <div v-if="submission.is_graded">
                    <span class="font-medium">Score:</span>
                    <span :class="getScoreColor(submission)">
                      {{ submission.final_score }}/{{ assignment.max_score }} ({{ Math.round(submission.grade_percentage || 0) }}%)
                    </span>
                  </div>
                  <div v-if="submission.is_graded">
                    <span class="font-medium">Status:</span>
                    <span :class="submission.is_passing ? 'text-green-600' : 'text-red-600'">
                      {{ submission.is_passing ? 'Pass' : 'Fail' }}
                    </span>
                  </div>
                  <div v-if="submission.graded_at">
                    <span class="font-medium">Graded:</span>
                    {{ formatDate(submission.graded_at) }}
                  </div>
                </div>
                
                <!-- Text content preview -->
                <div v-if="submission.text_content" class="mb-4">
                  <h4 class="text-sm font-medium text-gray-900 mb-2">Response Preview</h4>
                  <div class="p-3 bg-gray-50 rounded-md">
                    <p class="text-sm text-gray-700 line-clamp-3">{{ submission.text_content }}</p>
                  </div>
                </div>
                
                <!-- File attachment -->
                <div v-if="submission.file_upload" class="mb-4">
                  <h4 class="text-sm font-medium text-gray-900 mb-2">File Attachment</h4>
                  <div class="flex items-center space-x-2">
                    <svg class="w-4 h-4 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clip-rule="evenodd" />
                    </svg>
                    <a
                      :href="submission.file_upload"
                      target="_blank"
                      class="text-sm text-blue-600 hover:text-blue-800"
                    >
                      {{ getFileName(submission.file_upload) }}
                    </a>
                  </div>
                </div>
                
                <!-- Existing feedback -->
                <div v-if="submission.feedback" class="mb-4">
                  <h4 class="text-sm font-medium text-gray-900 mb-2">Current Feedback</h4>
                  <div class="p-3 bg-blue-50 rounded-md">
                    <p class="text-sm text-gray-700">{{ submission.feedback }}</p>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Grading Form -->
            <div class="ml-6 w-80">
              <div v-if="!submission.is_graded || editingSubmission === submission.id" class="space-y-4">
                <div>
                  <label :for="`score-${submission.id}`" class="block text-sm font-medium text-gray-700 mb-1">
                    Score (out of {{ assignment.max_score }})
                  </label>
                  <input
                    :id="`score-${submission.id}`"
                    v-model.number="gradingForms[submission.id].score"
                    type="number"
                    :min="0"
                    :max="assignment.max_score"
                    class="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                
                <div>
                  <label :for="`feedback-${submission.id}`" class="block text-sm font-medium text-gray-700 mb-1">
                    Feedback
                  </label>
                  <textarea
                    :id="`feedback-${submission.id}`"
                    v-model="gradingForms[submission.id].feedback"
                    rows="3"
                    class="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Provide feedback to the student..."
                  ></textarea>
                </div>
                
                <div class="flex space-x-2">
                  <button
                    @click="handleGradeSubmission(submission)"
                    :disabled="!gradingForms[submission.id].score || grading"
                    class="flex-1 px-3 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
                  >
                    {{ grading ? 'Grading...' : (submission.is_graded ? 'Update Grade' : 'Grade') }}
                  </button>
                  
                  <button
                    v-if="submission.is_graded && editingSubmission === submission.id"
                    @click="cancelEditing(submission.id)"
                    class="px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                  >
                    Cancel
                  </button>
                </div>
              </div>
              
              <!-- Graded state -->
              <div v-else class="text-center">
                <div class="text-2xl font-bold mb-2" :class="getScoreColor(submission)">
                  {{ submission.final_score }}/{{ assignment.max_score }}
                </div>
                <div class="text-sm text-gray-600 mb-4">
                  {{ Math.round(submission.grade_percentage || 0) }}% - {{ submission.is_passing ? 'Pass' : 'Fail' }}
                </div>
                <button
                  @click="startEditing(submission)"
                  class="px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  Edit Grade
                </button>
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
      <h3 class="mt-2 text-sm font-medium text-gray-900">No submissions</h3>
      <p class="mt-1 text-sm text-gray-500">No submissions have been made for this assignment yet.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import { useAssignments } from '../../composables/useAssignments'
import AssignmentService from '../../services/assignments'
import type { Assignment, Submission, GradeSubmissionRequest } from '../../types/assignments'

interface Props {
  assignment: Assignment
}

const props = defineProps<Props>()

const {
  submissions,
  loading,
  grading,
  submissionFilters,
  pendingSubmissions,
  lateSubmissions,
  fetchSubmissions,
  gradeSubmission
} = useAssignments()

// Bulk grading state
const showBulkGrading = ref(false)
const selectAll = ref(false)
const selectedSubmissions = ref<string[]>([])
const bulkScore = ref<number>()
const bulkFeedback = ref('')

// Individual grading state
const editingSubmission = ref<string | null>(null)
const gradingForms = reactive<Record<string, GradeSubmissionRequest>>({})

// Initialize grading forms for each submission
const initializeGradingForms = () => {
  submissions.value.forEach(submission => {
    if (!gradingForms[submission.id]) {
      gradingForms[submission.id] = {
        score: submission.score || 0,
        feedback: submission.feedback || ''
      }
    }
  })
}

// Watch for submissions changes to initialize forms
watch(submissions, initializeGradingForms, { immediate: true })

onMounted(() => {
  submissionFilters.value.assignment = props.assignment.id
  fetchSubmissions(submissionFilters.value)
})

// Methods
const toggleSelectAll = () => {
  if (selectAll.value) {
    selectedSubmissions.value = submissions.value.map(s => s.id)
  } else {
    selectedSubmissions.value = []
  }
}

const handleBulkGrade = async () => {
  if (!bulkScore.value || selectedSubmissions.value.length === 0) return
  
  try {
    const bulkData = selectedSubmissions.value.map(id => ({
      id,
      score: bulkScore.value!,
      feedback: bulkFeedback.value
    }))
    
    await AssignmentService.bulkGradeSubmissions(bulkData)
    
    // Refresh submissions
    await fetchSubmissions(submissionFilters.value)
    
    // Reset bulk grading state
    selectedSubmissions.value = []
    selectAll.value = false
    bulkScore.value = undefined
    bulkFeedback.value = ''
    showBulkGrading.value = false
  } catch (error) {
    // Error handled by service
  }
}

const handleGradeSubmission = async (submission: Submission) => {
  const gradeData = gradingForms[submission.id]
  if (!gradeData.score) return
  
  try {
    await gradeSubmission(submission.id, gradeData)
    editingSubmission.value = null
  } catch (error) {
    // Error handled by composable
  }
}

const startEditing = (submission: Submission) => {
  editingSubmission.value = submission.id
  gradingForms[submission.id] = {
    score: submission.score || 0,
    feedback: submission.feedback || ''
  }
}

const cancelEditing = (submissionId: string) => {
  editingSubmission.value = null
  const submission = submissions.value.find(s => s.id === submissionId)
  if (submission) {
    gradingForms[submissionId] = {
      score: submission.score || 0,
      feedback: submission.feedback || ''
    }
  }
}

const exportGrades = async () => {
  try {
    const blob = await AssignmentService.exportGrades(props.assignment.id, 'csv')
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${props.assignment.title}-grades.csv`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    // Error handled by service
  }
}

const getSubmissionStatusClass = (submission: Submission) => {
  const classes = {
    draft: 'bg-gray-100 text-gray-800',
    submitted: 'bg-blue-100 text-blue-800',
    late: 'bg-orange-100 text-orange-800',
    graded: submission.is_passing ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800',
    returned: 'bg-yellow-100 text-yellow-800'
  }
  return classes[submission.status as keyof typeof classes] || 'bg-gray-100 text-gray-800'
}

const getScoreColor = (submission: Submission) => {
  if (!submission.grade_percentage) return 'text-gray-600'
  
  const percentage = submission.grade_percentage
  if (percentage >= 90) return 'text-green-600'
  if (percentage >= 80) return 'text-blue-600'
  if (percentage >= 70) return 'text-yellow-600'
  if (percentage >= 60) return 'text-orange-600'
  return 'text-red-600'
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString() + ' at ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const getFileName = (url: string) => {
  return url.split('/').pop() || 'file'
}
</script>

<style scoped>
.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Animation for submission cards */
.grading-dashboard > div:last-child > div {
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