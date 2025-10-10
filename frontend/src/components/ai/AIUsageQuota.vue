<template>
  <div class="ai-usage-quota bg-white rounded-lg shadow-lg p-6">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center space-x-3">
        <div class="w-10 h-10 bg-gradient-to-r from-indigo-500 to-blue-600 rounded-full flex items-center justify-center">
          <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
        </div>
        <div>
          <h3 class="text-lg font-semibold text-gray-900">AI Usage & Quota</h3>
          <p class="text-sm text-gray-500">
            {{ usageStats?.month ? `Usage for ${formatMonth(usageStats.month)}` : 'Current month usage' }}
          </p>
        </div>
      </div>
      
      <button
        @click="refreshUsageStats"
        :disabled="loading.usage"
        class="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 transition-colors"
        title="Refresh Usage Stats"
      >
        <svg 
          class="w-5 h-5" 
          :class="{ 'animate-spin': loading.usage }"
          fill="none" 
          stroke="currentColor" 
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading.usage && !usageStats" class="flex items-center justify-center py-12">
      <div class="text-center">
        <svg class="w-8 h-8 animate-spin text-indigo-600 mx-auto mb-4" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <p class="text-gray-500">Loading usage statistics...</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="p-4 bg-red-50 border border-red-200 rounded-lg">
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

    <!-- Usage Statistics -->
    <div v-else-if="usageStats" class="space-y-6">
      <!-- Overall Status -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-4 border border-blue-200">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-blue-800">Chat Messages</p>
              <p class="text-2xl font-bold text-blue-900">
                {{ usageStats.chat.messages_used }}
              </p>
              <p class="text-xs text-blue-600">
                of {{ usageStats.chat.messages_limit }} limit
              </p>
            </div>
            <div class="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
            </div>
          </div>
        </div>

        <div class="bg-gradient-to-r from-green-50 to-teal-50 rounded-lg p-4 border border-green-200">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-green-800">Summaries</p>
              <p class="text-2xl font-bold text-green-900">
                {{ usageStats.summaries.summaries_used }}
              </p>
              <p class="text-xs text-green-600">
                of {{ usageStats.summaries.summaries_limit }} limit
              </p>
            </div>
            <div class="w-12 h-12 bg-green-600 rounded-full flex items-center justify-center">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
          </div>
        </div>

        <div class="bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg p-4 border border-purple-200">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-purple-800">Quizzes</p>
              <p class="text-2xl font-bold text-purple-900">
                {{ usageStats.quizzes.quizzes_used }}
              </p>
              <p class="text-xs text-purple-600">
                of {{ usageStats.quizzes.quizzes_limit }} limit
              </p>
            </div>
            <div class="w-12 h-12 bg-purple-600 rounded-full flex items-center justify-center">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
        </div>

        <div class="bg-gradient-to-r from-yellow-50 to-orange-50 rounded-lg p-4 border border-yellow-200">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-yellow-800">Cost</p>
              <p class="text-2xl font-bold text-yellow-900">
                ${{ usageStats.cost.total_cost_usd.toFixed(2) }}
              </p>
              <p class="text-xs text-yellow-600">
                of ${{ usageStats.cost.cost_limit_usd.toFixed(2) }} limit
              </p>
            </div>
            <div class="w-12 h-12 bg-yellow-600 rounded-full flex items-center justify-center">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      <!-- Detailed Usage Bars -->
      <div class="space-y-6">
        <!-- Chat Usage -->
        <div class="usage-section">
          <div class="flex items-center justify-between mb-3">
            <h4 class="text-lg font-semibold text-gray-900 flex items-center">
              <svg class="w-5 h-5 text-blue-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
              AI Chat Usage
            </h4>
            <span 
              class="text-sm font-medium"
              :class="getUsageColor(usageStats.chat.percentage_used)"
            >
              {{ Math.round(usageStats.chat.percentage_used) }}%
            </span>
          </div>
          
          <div class="space-y-3">
            <!-- Messages Progress -->
            <div>
              <div class="flex justify-between text-sm text-gray-600 mb-1">
                <span>Messages</span>
                <span>{{ usageStats.chat.messages_used }} / {{ usageStats.chat.messages_limit }}</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div 
                  class="h-2 rounded-full transition-all duration-500"
                  :class="getProgressBarColor(usageStats.chat.percentage_used)"
                  :style="{ width: `${Math.min(usageStats.chat.percentage_used, 100)}%` }"
                ></div>
              </div>
            </div>
            
            <!-- Tokens Progress -->
            <div>
              <div class="flex justify-between text-sm text-gray-600 mb-1">
                <span>Tokens</span>
                <span>{{ formatNumber(usageStats.chat.tokens_used) }} / {{ formatNumber(usageStats.chat.tokens_limit) }}</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div 
                  class="h-2 rounded-full transition-all duration-500"
                  :class="getProgressBarColor((usageStats.chat.tokens_used / usageStats.chat.tokens_limit) * 100)"
                  :style="{ width: `${Math.min((usageStats.chat.tokens_used / usageStats.chat.tokens_limit) * 100, 100)}%` }"
                ></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Summary Usage -->
        <div class="usage-section">
          <div class="flex items-center justify-between mb-3">
            <h4 class="text-lg font-semibold text-gray-900 flex items-center">
              <svg class="w-5 h-5 text-green-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Content Summaries
            </h4>
            <span 
              class="text-sm font-medium"
              :class="getUsageColor(usageStats.summaries.percentage_used)"
            >
              {{ Math.round(usageStats.summaries.percentage_used) }}%
            </span>
          </div>
          
          <div class="space-y-3">
            <!-- Summaries Progress -->
            <div>
              <div class="flex justify-between text-sm text-gray-600 mb-1">
                <span>Summaries</span>
                <span>{{ usageStats.summaries.summaries_used }} / {{ usageStats.summaries.summaries_limit }}</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div 
                  class="h-2 rounded-full transition-all duration-500"
                  :class="getProgressBarColor(usageStats.summaries.percentage_used)"
                  :style="{ width: `${Math.min(usageStats.summaries.percentage_used, 100)}%` }"
                ></div>
              </div>
            </div>
            
            <!-- Tokens Progress -->
            <div>
              <div class="flex justify-between text-sm text-gray-600 mb-1">
                <span>Tokens</span>
                <span>{{ formatNumber(usageStats.summaries.tokens_used) }} / {{ formatNumber(usageStats.summaries.tokens_limit) }}</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div 
                  class="h-2 rounded-full transition-all duration-500"
                  :class="getProgressBarColor((usageStats.summaries.tokens_used / usageStats.summaries.tokens_limit) * 100)"
                  :style="{ width: `${Math.min((usageStats.summaries.tokens_used / usageStats.summaries.tokens_limit) * 100, 100)}%` }"
                ></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Quiz Usage -->
        <div class="usage-section">
          <div class="flex items-center justify-between mb-3">
            <h4 class="text-lg font-semibold text-gray-900 flex items-center">
              <svg class="w-5 h-5 text-purple-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Quiz Generation
            </h4>
            <span 
              class="text-sm font-medium"
              :class="getUsageColor(usageStats.quizzes.percentage_used)"
            >
              {{ Math.round(usageStats.quizzes.percentage_used) }}%
            </span>
          </div>
          
          <div class="space-y-3">
            <!-- Quizzes Progress -->
            <div>
              <div class="flex justify-between text-sm text-gray-600 mb-1">
                <span>Quizzes</span>
                <span>{{ usageStats.quizzes.quizzes_used }} / {{ usageStats.quizzes.quizzes_limit }}</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div 
                  class="h-2 rounded-full transition-all duration-500"
                  :class="getProgressBarColor(usageStats.quizzes.percentage_used)"
                  :style="{ width: `${Math.min(usageStats.quizzes.percentage_used, 100)}%` }"
                ></div>
              </div>
            </div>
            
            <!-- Tokens Progress -->
            <div>
              <div class="flex justify-between text-sm text-gray-600 mb-1">
                <span>Tokens</span>
                <span>{{ formatNumber(usageStats.quizzes.tokens_used) }} / {{ formatNumber(usageStats.quizzes.tokens_limit) }}</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div 
                  class="h-2 rounded-full transition-all duration-500"
                  :class="getProgressBarColor((usageStats.quizzes.tokens_used / usageStats.quizzes.tokens_limit) * 100)"
                  :style="{ width: `${Math.min((usageStats.quizzes.tokens_used / usageStats.quizzes.tokens_limit) * 100, 100)}%` }"
                ></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Cost Usage -->
        <div class="usage-section">
          <div class="flex items-center justify-between mb-3">
            <h4 class="text-lg font-semibold text-gray-900 flex items-center">
              <svg class="w-5 h-5 text-yellow-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
              </svg>
              Cost Tracking
            </h4>
            <span 
              class="text-sm font-medium"
              :class="getUsageColor(usageStats.cost.percentage_used)"
            >
              {{ Math.round(usageStats.cost.percentage_used) }}%
            </span>
          </div>
          
          <div>
            <div class="flex justify-between text-sm text-gray-600 mb-1">
              <span>Monthly Cost</span>
              <span>${{ usageStats.cost.total_cost_usd.toFixed(2) }} / ${{ usageStats.cost.cost_limit_usd.toFixed(2) }}</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div 
                class="h-2 rounded-full transition-all duration-500"
                :class="getProgressBarColor(usageStats.cost.percentage_used)"
                :style="{ width: `${Math.min(usageStats.cost.percentage_used, 100)}%` }"
              ></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Quota Warnings -->
      <div v-if="hasQuotaWarnings" class="space-y-3">
        <div 
          v-if="usageStats.chat.percentage_used >= 90"
          class="p-3 bg-yellow-50 border border-yellow-200 rounded-lg flex items-center space-x-2"
        >
          <svg class="w-5 h-5 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
          <span class="text-yellow-800 text-sm">
            Chat quota is {{ Math.round(usageStats.chat.percentage_used) }}% used. Consider upgrading your plan.
          </span>
        </div>
        
        <div 
          v-if="usageStats.summaries.percentage_used >= 90"
          class="p-3 bg-yellow-50 border border-yellow-200 rounded-lg flex items-center space-x-2"
        >
          <svg class="w-5 h-5 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
          <span class="text-yellow-800 text-sm">
            Summary quota is {{ Math.round(usageStats.summaries.percentage_used) }}% used. Consider upgrading your plan.
          </span>
        </div>
        
        <div 
          v-if="usageStats.quizzes.percentage_used >= 90"
          class="p-3 bg-yellow-50 border border-yellow-200 rounded-lg flex items-center space-x-2"
        >
          <svg class="w-5 h-5 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
          <span class="text-yellow-800 text-sm">
            Quiz quota is {{ Math.round(usageStats.quizzes.percentage_used) }}% used. Consider upgrading your plan.
          </span>
        </div>
      </div>

      <!-- Upgrade CTA -->
      <div v-if="isQuotaExceeded" class="p-4 bg-red-50 border border-red-200 rounded-lg">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-3">
            <svg class="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <h5 class="font-medium text-red-800">Quota Exceeded</h5>
              <p class="text-sm text-red-700">You've reached your monthly AI usage limit.</p>
            </div>
          </div>
          <button class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors">
            Upgrade Plan
          </button>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="text-center py-12">
      <svg class="w-16 h-16 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
      </svg>
      <h3 class="text-lg font-medium text-gray-900 mb-2">No Usage Data</h3>
      <p class="text-gray-500">Start using AI features to see your usage statistics.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, nextTick } from 'vue'
import { useAI } from '@/composables/useAI'
import { useAnimations } from '@/composables/useAnimations'

// Composables
const {
  usageStats,
  loading,
  error,
  isQuotaExceeded,
  loadUsageStats,
  clearError,
  getUsageColor
} = useAI()

const { staggerIn } = useAnimations()

// Computed
const hasQuotaWarnings = computed(() => {
  if (!usageStats.value) return false
  return usageStats.value.chat.percentage_used >= 90 ||
         usageStats.value.summaries.percentage_used >= 90 ||
         usageStats.value.quizzes.percentage_used >= 90
})

// Methods
const refreshUsageStats = async () => {
  try {
    await loadUsageStats()
  } catch (err) {
    console.error('Failed to refresh usage stats:', err)
  }
}

const formatNumber = (num: number): string => {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M'
  } else if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  return num.toString()
}

const formatMonth = (monthString: string): string => {
  const [year, month] = monthString.split('-')
  const date = new Date(parseInt(year), parseInt(month) - 1)
  return date.toLocaleDateString([], { year: 'numeric', month: 'long' })
}

const getProgressBarColor = (percentage: number): string => {
  if (percentage >= 100) return 'bg-red-600'
  if (percentage >= 90) return 'bg-red-500'
  if (percentage >= 75) return 'bg-yellow-500'
  return 'bg-green-500'
}

// Initialize
onMounted(async () => {
  try {
    await loadUsageStats()
    
    // Animate progress bars after data loads
    await nextTick()
    const progressBars = document.querySelectorAll('.bg-green-500, .bg-yellow-500, .bg-red-500, .bg-red-600')
    if (progressBars.length > 0) {
      staggerIn(progressBars, { delay: 200 })
    }
  } catch (err) {
    console.error('Failed to load usage stats:', err)
  }
})
</script>

<style scoped>
/* Progress bar animations */
.transition-all {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 500ms;
}

/* Usage section spacing */
.usage-section {
  padding: 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  background-color: #fafafa;
}

/* Hover effects for interactive elements */
.usage-section:hover {
  background-color: #f3f4f6;
  transition: background-color 0.2s ease-in-out;
}

/* Custom scrollbar for overflow areas */
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