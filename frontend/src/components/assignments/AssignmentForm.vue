<template>
  <div class="assignment-form">
    <form @submit.prevent="handleSubmit" class="space-y-6">
      <!-- Basic Information -->
      <div class="bg-white rounded-lg shadow-sm border p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Basic Information</h3>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label for="title" class="block text-sm font-medium text-gray-700 mb-2">
              Assignment Title *
            </label>
            <input
              id="title"
              v-model="form.title"
              type="text"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Enter assignment title"
            />
          </div>
          
          <div>
            <label for="assignment_type" class="block text-sm font-medium text-gray-700 mb-2">
              Assignment Type *
            </label>
            <select
              id="assignment_type"
              v-model="form.assignment_type"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="essay">Essay</option>
              <option value="project">Project</option>
              <option value="quiz">Quiz</option>
              <option value="presentation">Presentation</option>
              <option value="code">Code Assignment</option>
              <option value="other">Other</option>
            </select>
          </div>
        </div>
        
        <div class="mt-6">
          <label for="description" class="block text-sm font-medium text-gray-700 mb-2">
            Description *
          </label>
          <textarea
            id="description"
            v-model="form.description"
            required
            rows="4"
            class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="Describe the assignment objectives and requirements"
          ></textarea>
        </div>
        
        <div class="mt-6">
          <label for="instructions" class="block text-sm font-medium text-gray-700 mb-2">
            Detailed Instructions
          </label>
          <textarea
            id="instructions"
            v-model="form.instructions"
            rows="6"
            class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="Provide detailed instructions for students"
          ></textarea>
        </div>
      </div>

      <!-- Grading Settings -->
      <div class="bg-white rounded-lg shadow-sm border p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Grading Settings</h3>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <label for="max_score" class="block text-sm font-medium text-gray-700 mb-2">
              Maximum Score *
            </label>
            <input
              id="max_score"
              v-model.number="form.max_score"
              type="number"
              min="1"
              max="1000"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          
          <div>
            <label for="passing_score" class="block text-sm font-medium text-gray-700 mb-2">
              Passing Score *
            </label>
            <input
              id="passing_score"
              v-model.number="form.passing_score"
              type="number"
              :min="1"
              :max="form.max_score"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          
          <div>
            <label for="weight_percentage" class="block text-sm font-medium text-gray-700 mb-2">
              Weight in Final Grade (%)
            </label>
            <input
              id="weight_percentage"
              v-model.number="form.weight_percentage"
              type="number"
              min="0"
              max="100"
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>
      </div>

      <!-- File Upload Settings -->
      <div class="bg-white rounded-lg shadow-sm border p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">File Upload Settings</h3>
        
        <div class="space-y-4">
          <div class="flex items-center">
            <input
              id="allow_file_upload"
              v-model="form.allow_file_upload"
              type="checkbox"
              class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label for="allow_file_upload" class="ml-2 block text-sm text-gray-900">
              Allow file uploads
            </label>
          </div>
          
          <div v-if="form.allow_file_upload" class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label for="max_file_size_mb" class="block text-sm font-medium text-gray-700 mb-2">
                Maximum File Size (MB)
              </label>
              <input
                id="max_file_size_mb"
                v-model.number="form.max_file_size_mb"
                type="number"
                min="1"
                max="100"
                class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            
            <div>
              <label for="allowed_file_types" class="block text-sm font-medium text-gray-700 mb-2">
                Allowed File Types
              </label>
              <input
                id="allowed_file_types"
                v-model="allowedFileTypesString"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="pdf, doc, docx, txt (comma separated)"
              />
              <p class="mt-1 text-xs text-gray-500">
                Leave empty to allow all file types
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Due Date and Late Submission -->
      <div class="bg-white rounded-lg shadow-sm border p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Due Date and Late Submission</h3>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label for="due_date" class="block text-sm font-medium text-gray-700 mb-2">
              Due Date *
            </label>
            <input
              id="due_date"
              v-model="form.due_date"
              type="datetime-local"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          
          <div>
            <label for="late_penalty_percent" class="block text-sm font-medium text-gray-700 mb-2">
              Late Penalty (% per day)
            </label>
            <input
              id="late_penalty_percent"
              v-model.number="form.late_penalty_percent"
              type="number"
              min="0"
              max="100"
              :disabled="!form.late_submission_allowed"
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100"
            />
          </div>
        </div>
        
        <div class="mt-4 space-y-4">
          <div class="flex items-center">
            <input
              id="late_submission_allowed"
              v-model="form.late_submission_allowed"
              type="checkbox"
              class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label for="late_submission_allowed" class="ml-2 block text-sm text-gray-900">
              Allow late submissions
            </label>
          </div>
          
          <div class="flex items-center">
            <input
              id="is_required"
              v-model="form.is_required"
              type="checkbox"
              class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label for="is_required" class="ml-2 block text-sm text-gray-900">
              Required for course completion
            </label>
          </div>
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
          v-if="!isEditing"
          type="button"
          @click="handleSaveDraft"
          :disabled="submitting"
          class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
        >
          Save as Draft
        </button>
        
        <button
          type="submit"
          :disabled="submitting"
          class="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
        >
          {{ submitting ? 'Saving...' : (isEditing ? 'Update Assignment' : 'Create Assignment') }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useAssignments } from '../../composables/useAssignments'
import type { Assignment, CreateAssignmentRequest, UpdateAssignmentRequest } from '../../types/assignments'

interface Props {
  courseId: string
  assignment?: Assignment
}

interface Emits {
  (e: 'submit', assignment: Assignment): void
  (e: 'cancel'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const { createAssignment, updateAssignment, submitting } = useAssignments()

const isEditing = computed(() => !!props.assignment)

// Form data
const form = ref<CreateAssignmentRequest>({
  course: props.courseId,
  title: '',
  description: '',
  instructions: '',
  assignment_type: 'essay',
  max_score: 100,
  passing_score: 60,
  allow_file_upload: true,
  max_file_size_mb: 10,
  allowed_file_types: [],
  due_date: '',
  late_submission_allowed: true,
  late_penalty_percent: 10,
  is_required: true,
  weight_percentage: 10
})

// Helper for file types input
const allowedFileTypesString = ref('')

// Watch for changes in file types string
watch(allowedFileTypesString, (newValue) => {
  form.value.allowed_file_types = newValue
    .split(',')
    .map(type => type.trim())
    .filter(type => type.length > 0)
})

// Initialize form with existing assignment data
onMounted(() => {
  if (props.assignment) {
    form.value = {
      course: props.assignment.course,
      title: props.assignment.title,
      description: props.assignment.description,
      instructions: props.assignment.instructions,
      assignment_type: props.assignment.assignment_type,
      max_score: props.assignment.max_score,
      passing_score: props.assignment.passing_score,
      allow_file_upload: props.assignment.allow_file_upload,
      max_file_size_mb: props.assignment.max_file_size_mb,
      allowed_file_types: props.assignment.allowed_file_types,
      due_date: props.assignment.due_date.slice(0, 16), // Format for datetime-local
      late_submission_allowed: props.assignment.late_submission_allowed,
      late_penalty_percent: props.assignment.late_penalty_percent,
      is_required: props.assignment.is_required,
      weight_percentage: props.assignment.weight_percentage
    }
    
    allowedFileTypesString.value = props.assignment.allowed_file_types.join(', ')
  } else {
    // Set default due date to 1 week from now
    const nextWeek = new Date()
    nextWeek.setDate(nextWeek.getDate() + 7)
    form.value.due_date = nextWeek.toISOString().slice(0, 16)
  }
})

const handleSubmit = async () => {
  try {
    let assignment: Assignment
    
    if (isEditing.value && props.assignment) {
      assignment = await updateAssignment(props.assignment.id, form.value as UpdateAssignmentRequest)
    } else {
      assignment = await createAssignment(form.value)
    }
    
    emit('submit', assignment)
  } catch (error) {
    // Error is handled by the composable
  }
}

const handleSaveDraft = async () => {
  try {
    const draftData = { ...form.value, status: 'draft' as const }
    const assignment = await createAssignment(draftData)
    emit('submit', assignment)
  } catch (error) {
    // Error is handled by the composable
  }
}
</script>

<style scoped>
.assignment-form {
  max-width: 4xl;
}

/* Custom styles for form elements */
input:focus,
textarea:focus,
select:focus {
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* Animation for form sections */
.assignment-form > form > div {
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