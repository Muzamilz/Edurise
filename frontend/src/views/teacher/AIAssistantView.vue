<template>
  <div class="min-h-screen bg-gradient-to-br from-orange-50 via-white to-amber-50">
    <!-- Header -->
    <div class="bg-gradient-to-r from-orange-500 to-amber-600 shadow-lg">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="py-6">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-4">
              <router-link 
                to="/dashboard" 
                class="p-2 text-white/80 hover:text-white rounded-lg hover:bg-white/10 transition-colors"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                </svg>
              </router-link>
              <div>
                <h1 class="text-3xl font-bold text-white flex items-center">
                  <span class="text-4xl mr-3">🤖</span>
                  AI Teaching Assistant
                </h1>
                <p class="text-orange-100 mt-1">Powerful AI tools to enhance your teaching</p>
              </div>
            </div>
            <div class="flex items-center space-x-3">
              <router-link 
                to="/teacher/courses" 
                class="px-4 py-2 text-sm font-medium text-orange-600 bg-white rounded-lg hover:bg-orange-50 transition-colors shadow-sm"
              >
                My Courses
              </router-link>
              <router-link 
                to="/dashboard" 
                class="px-4 py-2 text-sm font-medium text-white bg-orange-700 rounded-lg hover:bg-orange-800 transition-colors shadow-sm"
              >
                Dashboard
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Content -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <AIDashboard :initial-tab="initialTab" :course-id="courseId" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import AIDashboard from '@/components/ai/AIDashboard.vue'

const route = useRoute()
const initialTab = ref<'chat' | 'summary' | 'quiz' | 'usage'>((route.query.tab as any) || 'summary')
const courseId = ref<string | undefined>(route.query.courseId as string | undefined)

onMounted(() => {
  document.title = 'AI Assistant - Edurise'
})
</script>


