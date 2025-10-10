<template>
  <div class="ai-dashboard min-h-screen bg-gray-50 p-6">
    <!-- Header -->
    <div class="mb-8">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold text-gray-900 flex items-center">
            <div class="w-10 h-10 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-full flex items-center justify-center mr-3">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            AI Learning Assistant
          </h1>
          <p class="text-gray-600 mt-1">
            Enhance your learning with AI-powered tools for chat, summaries, and quizzes
          </p>
        </div>
        
        <!-- Tab Navigation -->
        <div class="flex space-x-1 bg-gray-200 rounded-lg p-1">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click="activeTab = tab.id as 'chat' | 'summary' | 'quiz' | 'usage'"
            class="px-4 py-2 rounded-md text-sm font-medium transition-colors"
            :class="activeTab === tab.id 
              ? 'bg-white text-gray-900 shadow-sm' 
              : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'"
          >
            <div class="flex items-center space-x-2">
              <component :is="tab.icon" class="w-4 h-4" />
              <span>{{ tab.name }}</span>
            </div>
          </button>
        </div>
      </div>
    </div>

    <!-- Usage Quota Banner -->
    <div v-if="isQuotaExceeded" class="mb-6">
      <div class="bg-red-50 border border-red-200 rounded-lg p-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-3">
            <svg class="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <h3 class="font-medium text-red-800">AI Usage Quota Exceeded</h3>
              <p class="text-sm text-red-700">
                You've reached your monthly AI usage limit. Some features may be restricted.
              </p>
            </div>
          </div>
          <button 
            @click="activeTab = 'usage'"
            class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            View Usage
          </button>
        </div>
      </div>
    </div>

    <!-- Tab Content -->
    <div class="tab-content">
      <!-- AI Tutor Chat Tab -->
      <div v-if="activeTab === 'chat'" class="tab-panel">
        <div class="grid grid-cols-1 lg:grid-cols-4 gap-6 h-[calc(100vh-200px)]">
          <!-- Chat Interface -->
          <div class="lg:col-span-3">
            <AITutorChat 
              :course-id="selectedCourseId"
              :context="chatContext"
              class="h-full"
            />
          </div>
          
          <!-- Usage Sidebar -->
          <div class="lg:col-span-1">
            <AIUsageQuota class="h-fit" />
          </div>
        </div>
      </div>

      <!-- Content Summary Tab -->
      <div v-if="activeTab === 'summary'" class="tab-panel">
        <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
          <!-- Summary Interface -->
          <div class="lg:col-span-3">
            <AIContentSummary 
              :course-id="selectedCourseId"
              :initial-content="summaryContent"
              :initial-title="summaryTitle"
              :content-type="summaryContentType"
            />
          </div>
          
          <!-- Usage Sidebar -->
          <div class="lg:col-span-1">
            <AIUsageQuota class="h-fit" />
          </div>
        </div>
      </div>

      <!-- Quiz Generator Tab -->
      <div v-if="activeTab === 'quiz'" class="tab-panel">
        <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
          <!-- Quiz Interface -->
          <div class="lg:col-span-3">
            <AIQuizGenerator 
              :course-id="selectedCourseId"
              :initial-content="quizContent"
              :initial-title="quizTitle"
            />
          </div>
          
          <!-- Usage Sidebar -->
          <div class="lg:col-span-1">
            <AIUsageQuota class="h-fit" />
          </div>
        </div>
      </div>

      <!-- Usage & Analytics Tab -->
      <div v-if="activeTab === 'usage'" class="tab-panel">
        <div class="grid grid-cols-1 xl:grid-cols-3 gap-6">
          <!-- Main Usage Display -->
          <div class="xl:col-span-2">
            <AIUsageQuota />
          </div>
          
          <!-- Quick Actions -->
          <div class="xl:col-span-1">
            <div class="bg-white rounded-lg shadow-lg p-6">
              <h3 class="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
              
              <div class="space-y-3">
                <button
                  @click="activeTab = 'chat'"
                  :disabled="!canUseFeature('chat')"
                  class="w-full flex items-center justify-between p-3 bg-blue-50 border border-blue-200 rounded-lg hover:bg-blue-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  <div class="flex items-center space-x-3">
                    <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                    </svg>
                    <span class="font-medium text-blue-800">Start AI Chat</span>
                  </div>
                  <svg class="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                  </svg>
                </button>
                
                <button
                  @click="activeTab = 'summary'"
                  :disabled="!canUseFeature('summary')"
                  class="w-full flex items-center justify-between p-3 bg-green-50 border border-green-200 rounded-lg hover:bg-green-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  <div class="flex items-center space-x-3">
                    <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <span class="font-medium text-green-800">Generate Summary</span>
                  </div>
                  <svg class="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                  </svg>
                </button>
                
                <button
                  @click="activeTab = 'quiz'"
                  :disabled="!canUseFeature('quiz')"
                  class="w-full flex items-center justify-between p-3 bg-purple-50 border border-purple-200 rounded-lg hover:bg-purple-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  <div class="flex items-center space-x-3">
                    <svg class="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span class="font-medium text-purple-800">Create Quiz</span>
                  </div>
                  <svg class="w-4 h-4 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                  </svg>
                </button>
              </div>
              
              <!-- Feature Status -->
              <div class="mt-6 pt-4 border-t border-gray-200">
                <h4 class="text-sm font-medium text-gray-700 mb-3">Feature Status</h4>
                <div class="space-y-2">
                  <div class="flex items-center justify-between text-sm">
                    <span class="text-gray-600">AI Chat</span>
                    <span 
                      class="px-2 py-1 rounded-full text-xs font-medium"
                      :class="canUseFeature('chat') 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'"
                    >
                      {{ canUseFeature('chat') ? 'Available' : 'Quota Exceeded' }}
                    </span>
                  </div>
                  
                  <div class="flex items-center justify-between text-sm">
                    <span class="text-gray-600">Summaries</span>
                    <span 
                      class="px-2 py-1 rounded-full text-xs font-medium"
                      :class="canUseFeature('summary') 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'"
                    >
                      {{ canUseFeature('summary') ? 'Available' : 'Quota Exceeded' }}
                    </span>
                  </div>
                  
                  <div class="flex items-center justify-between text-sm">
                    <span class="text-gray-600">Quizzes</span>
                    <span 
                      class="px-2 py-1 rounded-full text-xs font-medium"
                      :class="canUseFeature('quiz') 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'"
                    >
                      {{ canUseFeature('quiz') ? 'Available' : 'Quota Exceeded' }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick, watch, h } from 'vue'
import { useAI } from '@/composables/useAI'
import { useAnimations } from '@/composables/useAnimations'
import AITutorChat from './AITutorChat.vue'
import AIContentSummary from './AIContentSummary.vue'
import AIQuizGenerator from './AIQuizGenerator.vue'
import AIUsageQuota from './AIUsageQuota.vue'

// Props
interface Props {
  courseId?: string
  initialTab?: 'chat' | 'summary' | 'quiz' | 'usage'
  // Content pre-population props
  summaryContent?: string
  summaryTitle?: string
  summaryContentType?: 'text' | 'video' | 'live_class' | 'course_module'
  quizContent?: string
  quizTitle?: string
  chatContext?: Record<string, any>
}

const props = withDefaults(defineProps<Props>(), {
  initialTab: 'chat',
  summaryContentType: 'text',
  chatContext: () => ({})
})

// Composables
const {
  isQuotaExceeded,
  canUseFeature,
  loadUsageStats
} = useAI()

const { fadeIn } = useAnimations()

// Local state
const activeTab = ref(props.initialTab)
const selectedCourseId = ref(props.courseId)

// Watch for tab changes and animate content
watch(activeTab, async () => {
  await nextTick()
  const tabContent = document.querySelector('.tab-panel')
  if (tabContent) {
    fadeIn(tabContent, { duration: 300 })
  }
})

// Tab configuration
const tabs = computed(() => [
  {
    id: 'chat',
    name: 'AI Tutor',
    icon: () => h('svg', {
      class: 'w-4 h-4',
      fill: 'none',
      stroke: 'currentColor',
      viewBox: '0 0 24 24'
    }, [
      h('path', {
        'stroke-linecap': 'round',
        'stroke-linejoin': 'round',
        'stroke-width': '2',
        d: 'M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z'
      })
    ])
  },
  {
    id: 'summary',
    name: 'Summaries',
    icon: () => h('svg', {
      class: 'w-4 h-4',
      fill: 'none',
      stroke: 'currentColor',
      viewBox: '0 0 24 24'
    }, [
      h('path', {
        'stroke-linecap': 'round',
        'stroke-linejoin': 'round',
        'stroke-width': '2',
        d: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z'
      })
    ])
  },
  {
    id: 'quiz',
    name: 'Quizzes',
    icon: () => h('svg', {
      class: 'w-4 h-4',
      fill: 'none',
      stroke: 'currentColor',
      viewBox: '0 0 24 24'
    }, [
      h('path', {
        'stroke-linecap': 'round',
        'stroke-linejoin': 'round',
        'stroke-width': '2',
        d: 'M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z'
      })
    ])
  },
  {
    id: 'usage',
    name: 'Usage',
    icon: () => h('svg', {
      class: 'w-4 h-4',
      fill: 'none',
      stroke: 'currentColor',
      viewBox: '0 0 24 24'
    }, [
      h('path', {
        'stroke-linecap': 'round',
        'stroke-linejoin': 'round',
        'stroke-width': '2',
        d: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z'
      })
    ])
  }
])

// Initialize
onMounted(async () => {
  try {
    await loadUsageStats()
  } catch (err) {
    console.error('Failed to initialize AI dashboard:', err)
  }
})
</script>

<style scoped>
/* Tab transition animations */
.tab-panel {
  animation: fadeInUp 0.3s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Tab button hover effects */
.tab-content {
  min-height: 600px;
}

/* Responsive adjustments */
@media (max-width: 1024px) {
  .grid.lg\\:grid-cols-4 {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .lg\\:col-span-3,
  .lg\\:col-span-1 {
    grid-column: span 1;
  }
}

/* Custom scrollbar for dashboard */
.ai-dashboard::-webkit-scrollbar {
  width: 8px;
}

.ai-dashboard::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 4px;
}

.ai-dashboard::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
}

.ai-dashboard::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>