<template>
  <div class="submission-form">
    <!-- Assignment Details -->
    <div class="bg-white rounded-lg shadow-sm border p-6 mb-6">
      <div class="flex items-start justify-between mb-4">
        <div>
          <h2 class="text-xl font-semibold text-gray-900">{{ assignment.title }}</h2>
          <p class="text-sm text-gray-600 mt-1">{{ assignment.assignment_type.charAt(0).toUpperCase() + assignment.assignment_type.slice(1) }}</p>
        </div>
        
        <div class="text-right">
          <div class="text-sm text-gray-600">Due Date</div>
          <div :class="getTimeRemainingClass()" class="font-semibold">
            {{ formatDueDate(assignment.due_date) }}
          </div>
          <div :class="getTimeRemainingClass()" class="text-sm">
            {{ formatTimeRemaining(assignment.due_date) }}
          </div>
        </div>
      </div>
      
      <div class="prose max-w-none">
        <div class="mb-4">
          <h4 class="text-sm font-medium text-gray-900 mb-2">Description</h4>
          <p class="text-gray-700">{{ assignment.description }}</p>
        </div>
        
        <div v-if="assignment.instructions" class="mb-4">
          <h4 class="text-sm font-medium text-gray-900 mb-2">Instructions</h4>
          <div class="text-gray-700 whitespace-pre-wrap">{{ assignment.instructions }}</div>
        </div>
        
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <span class="font-medium text-gray-900">Max Score:</span>
            <span class="text-gray-700 ml-1">{{ assignment.max_score }}</span>
          </div>
          <div>
            <span class="font-medium text-gray-900">Passing Score:</span>
            <span class="text-gray-700 ml-1">{{ assignment.passing_score }}</span>
          </div>
          <div>
            <span class="font-medium text-gray-900">Weight:</span>
            <span class="text-gray-700 ml-1">{{ assignment.weight_percentage }}%</span>
          </div>
          <div>
            <span class="font-medium text-gray-900">Late Penalty:</span>
            <span class="text-gray-700 ml-1">{{ assignment.late_penalty_percent }}% per day</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Existing Submission Status -->
    <div v-if="existingSubmission" class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
      <div class="flex items-center">
        <svg class="w-5 h-5 text-blue-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
        </svg>
        <div>
          <h4 class="text-sm font-medium text-blue-900">
            {{ getSubmissionStatusText() }}
          </h4>
          <p class="text-sm text-blue-700 mt-1">
            {{ getSubmissionStatusDescription() }}
          </p>
        </div>
      </div>
    </div>

    <!-- Submission Form -->
    <form @submit.prevent="handleSubmit" class="space-y-6">
      <!-- Text Content -->
      <div class="bg-white rounded-lg shadow-sm border p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Your Submission</h3>
        
        <div>
          <label for="text_content" class="block text-sm font-medium text-gray-700 mb-2">
            Written Response
          </label>
          <textarea
            id="text_content"
            v-model="form.text_content"
            rows="10"
            :disabled="!canEdit"
            class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
            placeholder="Enter your response here..."
          ></textarea>
        </div>
      </div>

      <!-- File Upload -->
      <div v-if="assignment.allow_file_upload" class="bg-white rounded-lg shadow-sm border p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">File Upload</h3>
        
        <!-- Current file display -->
        <div v-if="existingSubmission?.file_upload" class="mb-4 p-3 bg-gray-50 rounded-md">
          <div class="flex items-center justify-between">
            <div class="flex items-center">
              <svg class="w-5 h-5 text-gray-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
              <span class="text-sm text-gray-700">Current file: {{ getFileName(existingSubmission.file_upload) }}</span>
            </div>
            <a
              :href="existingSubmission.file_upload"
              target="_blank"
              class="text-sm text-blue-600 hover:text-blue-800"
            >
              Download
            </a>
          </div>
        </div>
        
        <!-- File upload input -->
        <div class="space-y-4">
          <div>
            <label for="file_upload" class="block text-sm font-medium text-gray-700 mb-2">
              {{ existingSubmission?.file_upload ? 'Replace File' : 'Upload File' }}
            </label>
            <input
              id="file_upload"
              ref="fileInput"
              type="file"
              :disabled="!canEdit"
              :accept="getAcceptedFileTypes()"
              @change="handleFileChange"
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
            />
          </div>
          
          <!-- File upload info -->
          <div class="text-xs text-gray-500 space-y-1">
            <div>Maximum file size: {{ assignment.max_file_size_mb }}MB</div>
            <div v-if="assignment.allowed_file_types.length > 0">
              Allowed file types: {{ assignment.allowed_file_types.join(', ') }}
            </div>
          </div>
          
          <!-- Selected file preview -->
          <div v-if="selectedFile" class="p-3 bg-blue-50 rounded-md">
            <div class="flex items-center justify-between">
              <div class="flex items-center">
                <svg class="w-5 h-5 text-blue-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
                <span class="text-sm text-blue-700">{{ selectedFile.name }} ({{ formatFileSize(selectedFile.size) }})</span>
              </div>
              <button
                type="button"
                @click="clearSelectedFile"
                class="text-sm text-red-600 hover:text-red-800"
              >
                Remove
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Grading Information (if graded) -->
      <div v-if="existingSubmission?.is_graded" class="bg-white rounded-lg shadow-sm border p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Grading</h3>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div class="text-center p-4 bg-gray-50 rounded-lg">
            <div class="text-2xl font-bold" :class="getScoreColor()">
              {{ existingSubmission.final_score }}/{{ assignment.max_score }}
            </div>
            <div class="text-sm text-gray-600">Final Score</div>
          </div>
          
          <div class="text-center p-4 bg-gray-50 rounded-lg">
            <div class="text-2xl font-bold" :class="getScoreColor()">
              {{ Math.round(existingSubmission.grade_percentage || 0) }}%
            </div>
            <div class="text-sm text-gray-600">Percentage</div>
          </div>
          
          <div class="text-center p-4 rounded-lg" :class="getPassingStatusClass()">
            <div class="text-2xl font-bold">
              {{ existingSubmission.is_passing ? 'PASS' : 'FAIL' }}
            </div>
            <div class="text-sm">Status</div>
          </div>
        </div>
        
        <div v-if="existingSubmission.feedback" class="mt-6">
          <h4 class="text-sm font-medium text-gray-900 mb-2">Instructor Feedback</h4>
          <div class="p-3 bg-gray-50 rounded-md">
            <p class="text-gray-700 whitespace-pre-wrap">{{ existingSubmission.feedback }}</p>
          </div>
        </div>
        
        <div class="mt-4 text-sm text-gray-500">
          <div>Graded by: {{ existingSubmission.graded_by?.first_name }} {{ existingSubmission.graded_by?.last_name }}</div>
          <div>Graded on: {{ formatDate(existingSubmission.graded_at!) }}</div>
        </div>
      </div>

      <!-- Form Actions -->
      <div class="flex justify-end space-x-4">
        <button
          type="button"
          @click="$emit('cancel')"
          class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          Cancel
        </button>
        
        <button
          v-if="canEdit && !isSubmitted"
          type="button"
          @click="handleSaveDraft"
          :disabled="submitting"
          class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
        >
          Save Draft
        </button>
        
        <button
          v-if="canEdit"
          type="submit"
          :disabled="submitting || (!form.text_content?.trim() && !selectedFile && !existingSubmission?.file_upload)"
          class="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
        >
          {{ submitting ? 'Submitting...' : (isSubmitted ? 'Update Submission' : 'Submit Assignment') }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAssignments } from '../../composables/useAssignments'
import type { Assignment, Submission, CreateSubmissionRequest, UpdateSubmissionRequest } from '../../types/assignments'

interface Props {
  assignment: Assignment
  existingSubmission?: Submission | null
}

interface Emits {
  (e: 'submit', submission: Submission): void
  (e: 'cancel'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const { createSubmission, updateSubmission, submitAssignment, submitting, formatTimeRemaining } = useAssignments()

const fileInput = ref<HTMLInputElement>()
const selectedFile = ref<File | null>(null)

// Form data
const form = ref<CreateSubmissionRequest | UpdateSubmissionRequest>({
  assignment: props.assignment.id,
  text_content: props.existingSubmission?.text_content || '',
  file_upload: undefined
})

// Computed properties
const canEdit = computed(() => {
  if (!props.assignment) return false
  if (props.assignment.status !== 'published') return false
  if (props.existingSubmission?.status === 'graded') return false
  
  // Allow editing if not submitted or if late submissions are allowed
  return !isSubmitted.value || props.assignment.late_submission_allowed
})

const isSubmitted = computed(() => {
  return props.existingSubmission?.status === 'submitted' || 
         props.existingSubmission?.status === 'late' ||
         props.existingSubmission?.status === 'graded'
})

const getTimeRemainingClass = () => {
  if (props.assignment.is_overdue) return 'text-red-600'
  if (props.assignment.days_until_due <= 1) return 'text-red-600'
  if (props.assignment.days_until_due <= 3) return 'text-orange-600'
  if (props.assignment.days_until_due <= 7) return 'text-yellow-600'
  return 'text-green-600'
}

// Methods
const handleFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  
  if (file) {
    // Validate file size
    if (file.size > props.assignment.max_file_size_mb * 1024 * 1024) {
      alert(`File size exceeds the maximum allowed size of ${props.assignment.max_file_size_mb}MB`)
      target.value = ''
      return
    }
    
    // Validate file type
    if (props.assignment.allowed_file_types.length > 0) {
      const fileExtension = file.name.split('.').pop()?.toLowerCase()
      if (!fileExtension || !props.assignment.allowed_file_types.includes(fileExtension)) {
        alert(`File type not allowed. Allowed types: ${props.assignment.allowed_file_types.join(', ')}`)
        target.value = ''
        return
      }
    }
    
    selectedFile.value = file
    form.value.file_upload = file
  }
}

const clearSelectedFile = () => {
  selectedFile.value = null
  form.value.file_upload = undefined
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const handleSubmit = async () => {
  try {
    let submission: Submission
    
    if (props.existingSubmission) {
      // Update existing submission
      submission = await updateSubmission(props.existingSubmission.id, form.value as UpdateSubmissionRequest)
      
      // Submit if not already submitted
      if (!isSubmitted.value) {
        submission = await submitAssignment(submission.id)
      }
    } else {
      // Create new submission
      submission = await createSubmission(form.value as CreateSubmissionRequest)
      // Submit immediately
      submission = await submitAssignment(submission.id)
    }
    
    emit('submit', submission)
  } catch (error) {
    // Error is handled by the composable
  }
}

const handleSaveDraft = async () => {
  try {
    let submission: Submission
    
    if (props.existingSubmission) {
      submission = await updateSubmission(props.existingSubmission.id, form.value as UpdateSubmissionRequest)
    } else {
      submission = await createSubmission(form.value as CreateSubmissionRequest)
    }
    
    emit('submit', submission)
  } catch (error) {
    // Error is handled by the composable
  }
}

const getSubmissionStatusText = () => {
  if (!props.existingSubmission) return ''
  
  switch (props.existingSubmission.status) {
    case 'draft': return 'Draft Saved'
    case 'submitted': return 'Submitted'
    case 'late': return 'Late Submission'
    case 'graded': return 'Graded'
    case 'returned': return 'Returned for Revision'
    default: return props.existingSubmission.status
  }
}

const getSubmissionStatusDescription = () => {
  if (!props.existingSubmission) return ''
  
  switch (props.existingSubmission.status) {
    case 'draft': return 'Your work has been saved as a draft. Remember to submit before the deadline.'
    case 'submitted': return 'Your assignment has been submitted successfully and is awaiting grading.'
    case 'late': return 'Your assignment was submitted after the deadline. Late penalties may apply.'
    case 'graded': return 'Your assignment has been graded. See the grading section below for details.'
    case 'returned': return 'Your assignment has been returned for revision. Please make the requested changes and resubmit.'
    default: return ''
  }
}

const getAcceptedFileTypes = () => {
  if (props.assignment.allowed_file_types.length === 0) return '*'
  return props.assignment.allowed_file_types.map(type => `.${type}`).join(',')
}

const getFileName = (url: string) => {
  return url.split('/').pop() || 'file'
}

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatDueDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString() + ' at ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString() + ' at ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const getScoreColor = () => {
  if (!props.existingSubmission?.grade_percentage) return 'text-gray-600'
  
  const percentage = props.existingSubmission.grade_percentage
  if (percentage >= 90) return 'text-green-600'
  if (percentage >= 80) return 'text-blue-600'
  if (percentage >= 70) return 'text-yellow-600'
  if (percentage >= 60) return 'text-orange-600'
  return 'text-red-600'
}

const getPassingStatusClass = () => {
  if (!props.existingSubmission) return 'bg-gray-50'
  return props.existingSubmission.is_passing ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'
}
</script>

<style scoped>
.prose {
  max-width: none;
}

.prose h4 {
  margin-top: 0;
  margin-bottom: 0.5rem;
}

.prose p {
  margin-top: 0;
  margin-bottom: 1rem;
}

/* Animation for form sections */
.submission-form > form > div {
  animation: fadeInUp 0.3s ease-out;
}

@keyframes fadeInUp {
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