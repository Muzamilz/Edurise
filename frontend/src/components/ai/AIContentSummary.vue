<template>
  <div class="ai-content-summary bg-white rounded-lg shadow-lg">
    <!-- Header -->
    <div class="p-6 border-b border-gray-200">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <div class="w-10 h-10 bg-gradient-to-r from-green-500 to-teal-600 rounded-full flex items-center justify-center">
            <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <div>
            <h3 class="text-lg font-semibold text-gray-900">AI Content Summary</h3>
            <p class="text-sm text-gray-500">Generate intelligent summaries from your content</p>
          </div>
        </div>
        
        <button
          @click="showSummaryHistory = !showSummaryHistory"
          class="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 transition-colors"
          title="Summary History"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Summary History Sidebar -->
    <div 
      v-if="showSummaryHistory"
      class="absolute top-20 right-6 w-80 bg-white border border-gray-200 rounded-lg shadow-lg z-10 max-h-96 overflow-y-auto"
    >
      <div class="p-3 border-b border-gray-200">
        <h4 class="font-medium text-gray-900">Recent Summaries</h4>
      </div>
      <div class="p-2">
        <div
          v-for="summary in summaries"
          :key="summary.id"
          @click="viewSummary(summary)"
          class="p-3 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
        >
          <div class="font-medium text-sm text-gray-900 truncate">
            {{ summary.content_title }}
          </div>
          <div class="text-xs text-gray-500 mt-1">
            {{ formatDate(summary.created_at) }} • {{ summary.content_type }}
          </div>
        </div>
        
        <div v-if="summaries.length === 0" class="p-3 text-center text-gray-500 text-sm">
          No summaries yet
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="p-6">
      <!-- Generate Summary Form -->
      <div v-if="!currentSummary" class="space-y-6">
        <div>
          <label for="content-title" class="block text-sm font-medium text-gray-700 mb-2">
            Content Title
          </label>
          <input
            id="content-title"
            v-model="summaryForm.title"
            type="text"
            placeholder="Enter a title for your content..."
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
          />
        </div>

        <div>
          <label for="content-type" class="block text-sm font-medium text-gray-700 mb-2">
            Content Type
          </label>
          <select
            id="content-type"
            v-model="summaryForm.contentType"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
          >
            <option value="text">Text Content</option>
            <option value="video">Video Content</option>
            <option value="live_class">Live Class Recording</option>
            <option value="course_module">Course Module</option>
          </select>
        </div>

        <div>
          <label for="content-input" class="block text-sm font-medium text-gray-700 mb-2">
            Content to Summarize
          </label>
          <textarea
            id="content-input"
            v-model="summaryForm.content"
            rows="8"
            placeholder="Paste your content here (text, transcript, notes, etc.)..."
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent resize-none"
          ></textarea>
          <div class="mt-1 text-sm text-gray-500">
            {{ summaryForm.content.length }} characters
          </div>
        </div>

        <!-- Error Display -->
        <div v-if="error" class="p-4 bg-red-50 border border-red-200 rounded-lg">
          <div class="flex items-center space-x-2">
            <svg class="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span class="text-red-700 text-sm">{{ error.message }}</span>
            <button @click="clearError" class="text-red-500 hover:text-red-700">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <!-- Generate Button -->
        <div class="flex justify-between items-center">
          <div class="text-sm text-gray-500">
            <span v-if="!canUseFeature('summary')" class="text-red-600">
              Summary quota exceeded
            </span>
            <span v-else>
              AI will generate a concise summary with key points
            </span>
          </div>
          
          <button
            @click="handleGenerateSummary"
            :disabled="!canGenerateSummary || loading.summary"
            class="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
          >
            <svg v-if="loading.summary" class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <span>{{ loading.summary ? 'Generating...' : 'Generate Summary' }}</span>
          </button>
        </div>
      </div>

      <!-- Summary Display -->
      <div v-else class="space-y-6">
        <!-- Summary Header -->
        <div class="flex items-center justify-between">
          <div>
            <h4 class="text-xl font-semibold text-gray-900">{{ currentSummary.content_title }}</h4>
            <div class="flex items-center space-x-4 mt-1 text-sm text-gray-500">
              <span class="capitalize">{{ currentSummary.content_type.replace('_', ' ') }}</span>
              <span>•</span>
              <span>{{ formatDate(currentSummary.created_at) }}</span>
              <span>•</span>
              <span>{{ currentSummary.generation_time_ms }}ms generation time</span>
            </div>
          </div>
          
          <button
            @click="clearCurrentSummary"
            class="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 transition-colors"
            title="Create New Summary"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
          </button>
        </div>

        <!-- Summary Content -->
        <div class="bg-gradient-to-r from-green-50 to-teal-50 rounded-lg p-6 border border-green-200">
          <h5 class="text-lg font-semibold text-gray-900 mb-3 flex items-center">
            <svg class="w-5 h-5 text-green-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Summary
          </h5>
          <div class="text-gray-700 leading-relaxed whitespace-pre-wrap">
            {{ currentSummary.summary }}
          </div>
        </div>

        <!-- Key Points -->
        <div v-if="currentSummary.key_points && currentSummary.key_points.length > 0">
          <h5 class="text-lg font-semibold text-gray-900 mb-3 flex items-center">
            <svg class="w-5 h-5 text-blue-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
            </svg>
            Key Points
          </h5>
          <div class="space-y-2">
            <div
              v-for="(point, index) in currentSummary.key_points"
              :key="index"
              class="flex items-start space-x-3 p-3 bg-blue-50 rounded-lg border border-blue-200"
            >
              <div class="w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-semibold flex-shrink-0 mt-0.5">
                {{ index + 1 }}
              </div>
              <div class="text-gray-700 leading-relaxed">{{ point }}</div>
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex justify-between items-center pt-4 border-t border-gray-200">
          <div class="text-sm text-gray-500">
            Tokens used: {{ currentSummary.tokens_used }}
          </div>
          
          <div class="flex space-x-3">
            <button
              @click="copySummary"
              class="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors flex items-center space-x-2"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
              <span>Copy</span>
            </button>
            
            <button
              @click="exportSummary"
              class="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors flex items-center space-x-2"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <span>Export</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { useAI } from '@/composables/useAI'
import { useAnimations } from '@/composables/useAnimations'
import type { AIContentSummary } from '@/types/ai'

// Props
interface Props {
  courseId?: string
  initialContent?: string
  initialTitle?: string
  contentType?: 'text' | 'video' | 'live_class' | 'course_module'
}

const props = withDefaults(defineProps<Props>(), {
  contentType: 'text'
})

// Composables
const {
  summaries,
  loading,
  error,
  loadSummaries,
  generateSummary,
  clearError,
  canUseFeature
} = useAI()

const { slideIn, scaleIn } = useAnimations()

// Local state
const showSummaryHistory = ref(false)
const currentSummary = ref<AIContentSummary | null>(null)

const summaryForm = ref({
  title: props.initialTitle || '',
  content: props.initialContent || '',
  contentType: props.contentType
})

// Computed
const canGenerateSummary = computed(() => {
  return summaryForm.value.title.trim() && 
         summaryForm.value.content.trim() && 
         canUseFeature('summary')
})

// Methods
const handleGenerateSummary = async () => {
  if (!canGenerateSummary.value) return

  try {
    await generateSummary({
      content: summaryForm.value.content,
      content_type: summaryForm.value.contentType as any,
      content_title: summaryForm.value.title,
      course_id: props.courseId
    })

    // Find the newly created summary
    await loadSummaries()
    const newSummary = summaries.value.find(s => s.content_title === summaryForm.value.title)
    if (newSummary) {
      currentSummary.value = newSummary
      
      // Animate the summary display
      await nextTick()
      const summaryElement = document.querySelector('.bg-gradient-to-r')
      if (summaryElement) {
        scaleIn(summaryElement, { duration: 800, easing: 'easeOutBack' })
      }
    }
  } catch (err) {
    console.error('Failed to generate summary:', err)
  }
}

const viewSummary = (summary: AIContentSummary) => {
  currentSummary.value = summary
  showSummaryHistory.value = false
  
  // Animate the summary display
  nextTick(() => {
    const summaryElement = document.querySelector('.bg-gradient-to-r')
    if (summaryElement) {
      slideIn(summaryElement, 'right', { duration: 600, easing: 'easeOutExpo' })
    }
  })
}

const clearCurrentSummary = () => {
  currentSummary.value = null
  summaryForm.value = {
    title: '',
    content: '',
    contentType: 'text'
  }
}

const copySummary = async () => {
  if (!currentSummary.value) return

  const text = `${currentSummary.value.content_title}\n\n${currentSummary.value.summary}\n\nKey Points:\n${currentSummary.value.key_points.map((point, index) => `${index + 1}. ${point}`).join('\n')}`
  
  try {
    await navigator.clipboard.writeText(text)
    // Show success feedback (you could add a toast notification here)
  } catch (err) {
    console.error('Failed to copy summary:', err)
  }
}

const exportSummary = () => {
  if (!currentSummary.value) return

  const text = `${currentSummary.value.content_title}\n\n${currentSummary.value.summary}\n\nKey Points:\n${currentSummary.value.key_points.map((point, index) => `${index + 1}. ${point}`).join('\n')}`
  
  const blob = new Blob([text], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${currentSummary.value.content_title} - Summary.txt`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString([], { 
    year: 'numeric', 
    month: 'short', 
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Initialize
onMounted(async () => {
  try {
    await loadSummaries()
  } catch (err) {
    console.error('Failed to load summaries:', err)
  }
})
</script>

<style scoped>
/* Custom animations for summary display */
.summary-enter-active {
  transition: all 0.5s ease-out;
}

.summary-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.summary-enter-to {
  opacity: 1;
  transform: translateY(0);
}

/* Scrollbar styling */
.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>