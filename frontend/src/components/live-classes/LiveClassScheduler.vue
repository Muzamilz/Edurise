<template>
  <div class="live-class-scheduler">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-2xl font-bold text-gray-900">Schedule Live Class</h2>
      <button
        @click="resetForm"
        class="px-4 py-2 text-sm text-gray-600 hover:text-gray-800 transition-colors"
      >
        Reset Form
      </button>
    </div>

    <!-- Form -->
    <form @submit.prevent="handleSubmit" class="space-y-6">
      <!-- Course Selection -->
      <div class="form-group">
        <label for="course" class="block text-sm font-medium text-gray-700 mb-2">
          Course *
        </label>
        <select
          id="course"
          v-model="form.course"
          required
          class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          :disabled="isLoading"
        >
          <option value="">Select a course</option>
          <option
            v-for="course in availableCourses"
            :key="course.id"
            :value="course.id"
          >
            {{ course.title }}
          </option>
        </select>
        <p v-if="errors.course" class="mt-1 text-sm text-red-600">
          {{ errors.course }}
        </p>
      </div>

      <!-- Class Title -->
      <div class="form-group">
        <label for="title" class="block text-sm font-medium text-gray-700 mb-2">
          Class Title *
        </label>
        <input
          id="title"
          v-model="form.title"
          type="text"
          required
          placeholder="Enter class title"
          class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          :disabled="isLoading"
        />
        <p v-if="errors.title" class="mt-1 text-sm text-red-600">
          {{ errors.title }}
        </p>
      </div>

      <!-- Description -->
      <div class="form-group">
        <label for="description" class="block text-sm font-medium text-gray-700 mb-2">
          Description
        </label>
        <textarea
          id="description"
          v-model="form.description"
          rows="3"
          placeholder="Enter class description (optional)"
          class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          :disabled="isLoading"
        ></textarea>
      </div>

      <!-- Date and Time -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="form-group">
          <label for="date" class="block text-sm font-medium text-gray-700 mb-2">
            Date *
          </label>
          <input
            id="date"
            v-model="form.date"
            type="date"
            required
            :min="minDate"
            class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            :disabled="isLoading"
          />
          <p v-if="errors.date" class="mt-1 text-sm text-red-600">
            {{ errors.date }}
          </p>
        </div>

        <div class="form-group">
          <label for="time" class="block text-sm font-medium text-gray-700 mb-2">
            Time *
          </label>
          <input
            id="time"
            v-model="form.time"
            type="time"
            required
            class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            :disabled="isLoading"
          />
          <p v-if="errors.time" class="mt-1 text-sm text-red-600">
            {{ errors.time }}
          </p>
        </div>
      </div>

      <!-- Duration -->
      <div class="form-group">
        <label for="duration" class="block text-sm font-medium text-gray-700 mb-2">
          Duration (minutes) *
        </label>
        <select
          id="duration"
          v-model="form.duration_minutes"
          required
          class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          :disabled="isLoading"
        >
          <option value="">Select duration</option>
          <option value="30">30 minutes</option>
          <option value="45">45 minutes</option>
          <option value="60">1 hour</option>
          <option value="90">1.5 hours</option>
          <option value="120">2 hours</option>
          <option value="180">3 hours</option>
        </select>
        <p v-if="errors.duration_minutes" class="mt-1 text-sm text-red-600">
          {{ errors.duration_minutes }}
        </p>
      </div>

      <!-- Zoom Integration Options -->
      <div class="form-group">
        <div class="flex items-center space-x-3">
          <input
            id="create-zoom-meeting"
            v-model="form.createZoomMeeting"
            type="checkbox"
            class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          />
          <label for="create-zoom-meeting" class="text-sm font-medium text-gray-700">
            Create Zoom meeting automatically
          </label>
        </div>
        <p class="mt-1 text-sm text-gray-500">
          If checked, a Zoom meeting will be created automatically when you schedule the class.
        </p>
      </div>

      <!-- Error Display -->
      <div v-if="error" class="bg-red-50 border border-red-200 rounded-md p-4">
        <div class="flex">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="ml-3">
            <h3 class="text-sm font-medium text-red-800">Error</h3>
            <p class="mt-1 text-sm text-red-700">{{ error }}</p>
          </div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="flex items-center justify-end space-x-4 pt-6 border-t border-gray-200">
        <button
          type="button"
          @click="$emit('cancel')"
          class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
          :disabled="isLoading"
        >
          Cancel
        </button>
        <button
          type="submit"
          class="px-6 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          :disabled="isLoading || !isFormValid"
        >
          <span v-if="isLoading" class="flex items-center">
            <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ isEditMode ? 'Updating...' : 'Scheduling...' }}
          </span>
          <span v-else>
            {{ isEditMode ? 'Update Class' : 'Schedule Class' }}
          </span>
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useZoom } from '@/composables/useZoom'
import { useCourse } from '@/composables/useCourse'
import type { LiveClass, Course } from '@/types/api'

interface Props {
  liveClass?: LiveClass
  courseId?: string
}

interface Emits {
  (e: 'success', liveClass: LiveClass): void
  (e: 'cancel'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const { 
  createLiveClass, 
  updateLiveClass, 
  createZoomMeeting,
  isLoading, 
  error,
  clearError 
} = useZoom()

const { courses, fetchCourses } = useCourse()

// Form state
const form = ref({
  course: props.courseId || '',
  title: '',
  description: '',
  date: '',
  time: '',
  duration_minutes: '',
  createZoomMeeting: true
})

const errors = ref<Record<string, string>>({})

// Computed properties
const isEditMode = computed(() => !!props.liveClass)

const minDate = computed(() => {
  const today = new Date()
  return today.toISOString().split('T')[0]
})

const availableCourses = computed(() => {
  return courses.value.filter(course => course.is_public || course.instructor)
})

const isFormValid = computed(() => {
  return form.value.course && 
         form.value.title && 
         form.value.date && 
         form.value.time && 
         form.value.duration_minutes
})

// Initialize form for editing
const initializeForm = () => {
  if (props.liveClass) {
    const scheduledAt = new Date(props.liveClass.scheduled_at)
    form.value = {
      course: props.liveClass.course,
      title: props.liveClass.title,
      description: props.liveClass.description || '',
      date: scheduledAt.toISOString().split('T')[0],
      time: scheduledAt.toTimeString().slice(0, 5),
      duration_minutes: props.liveClass.duration_minutes.toString(),
      createZoomMeeting: !props.liveClass.zoom_meeting_id
    }
  }
}

// Form validation
const validateForm = () => {
  errors.value = {}
  
  if (!form.value.course) {
    errors.value.course = 'Please select a course'
  }
  
  if (!form.value.title.trim()) {
    errors.value.title = 'Class title is required'
  }
  
  if (!form.value.date) {
    errors.value.date = 'Date is required'
  } else {
    const selectedDate = new Date(form.value.date)
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    
    if (selectedDate < today) {
      errors.value.date = 'Date cannot be in the past'
    }
  }
  
  if (!form.value.time) {
    errors.value.time = 'Time is required'
  }
  
  if (!form.value.duration_minutes) {
    errors.value.duration_minutes = 'Duration is required'
  }
  
  // Check if date/time is in the past
  if (form.value.date && form.value.time) {
    const scheduledDateTime = new Date(`${form.value.date}T${form.value.time}`)
    if (scheduledDateTime <= new Date()) {
      errors.value.time = 'Scheduled time must be in the future'
    }
  }
  
  return Object.keys(errors.value).length === 0
}

// Form submission
const handleSubmit = async () => {
  clearError()
  
  if (!validateForm()) {
    return
  }
  
  try {
    const scheduledAt = new Date(`${form.value.date}T${form.value.time}`).toISOString()
    
    const liveClassData = {
      course: form.value.course,
      title: form.value.title.trim(),
      description: form.value.description.trim(),
      scheduled_at: scheduledAt,
      duration_minutes: parseInt(form.value.duration_minutes)
    }
    
    let liveClass: LiveClass
    
    if (isEditMode.value && props.liveClass) {
      liveClass = await updateLiveClass(props.liveClass.id, liveClassData)
    } else {
      liveClass = await createLiveClass(liveClassData)
    }
    
    // Create Zoom meeting if requested
    if (form.value.createZoomMeeting && !liveClass.zoom_meeting_id) {
      try {
        await createZoomMeeting(liveClass.id)
      } catch (zoomError) {
        console.warn('Failed to create Zoom meeting:', zoomError)
        // Continue anyway - user can create meeting later
      }
    }
    
    emit('success', liveClass)
    
    if (!isEditMode.value) {
      resetForm()
    }
  } catch (err) {
    console.error('Error scheduling live class:', err)
  }
}

// Reset form
const resetForm = () => {
  form.value = {
    course: props.courseId || '',
    title: '',
    description: '',
    date: '',
    time: '',
    duration_minutes: '',
    createZoomMeeting: true
  }
  errors.value = {}
  clearError()
}

// Watch for prop changes
watch(() => props.liveClass, initializeForm, { immediate: true })

// Lifecycle
onMounted(async () => {
  await fetchCourses()
  initializeForm()
})
</script>

<style scoped>
.live-class-scheduler {
  @apply max-w-2xl mx-auto bg-white rounded-lg shadow-sm border border-gray-200 p-6;
}

.form-group {
  @apply space-y-1;
}

.form-group label {
  @apply block text-sm font-medium text-gray-700;
}

.form-group input,
.form-group select,
.form-group textarea {
  @apply w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm;
  @apply focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500;
  @apply disabled:bg-gray-50 disabled:text-gray-500;
}

.form-group input:invalid,
.form-group select:invalid,
.form-group textarea:invalid {
  @apply border-red-300 focus:ring-red-500 focus:border-red-500;
}
</style>