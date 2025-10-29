<template>
  <div class="course-learning-view">
    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>Loading course content...</p>
    </div>

    <!-- Course Learning Interface -->
    <div v-else class="learning-interface">
      <!-- Course Header -->
      <div class="course-header">
        <div class="course-info">
          <h1>{{ course?.title }}</h1>
          <p>{{ course?.instructor_name }}</p>
        </div>
        <div class="progress-info">
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: courseProgress + '%' }"></div>
          </div>
          <span class="progress-text">{{ courseProgress }}% Complete</span>
        </div>
      </div>

      <div class="learning-content">
        <!-- Sidebar -->
        <div class="sidebar">
          <div class="course-navigation">
            <h3>Course Content</h3>
            <div class="modules-list">
              <div v-for="module in modules" :key="module.id" class="module-item">
                <div class="module-header" @click="toggleModule(module.id)">
                  <span class="module-title">{{ module.title }}</span>
                  <span class="module-toggle">{{ expandedModules.includes(module.id) ? '−' : '+' }}</span>
                </div>
                <div v-if="expandedModules.includes(module.id)" class="lessons-list">
                  <div 
                    v-for="lesson in module.lessons" 
                    :key="lesson.id"
                    @click="selectLesson(lesson)"
                    class="lesson-item"
                    :class="{ 
                      active: currentLesson?.id === lesson.id,
                      completed: lesson.completed 
                    }"
                  >
                    <span class="lesson-icon">
                      {{ lesson.completed ? '✓' : (lesson.type === 'video' ? '▶️' : '📄') }}
                    </span>
                    <span class="lesson-title">{{ lesson.title }}</span>
                    <span class="lesson-duration">{{ lesson.duration }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Main Content -->
        <div class="main-content">
          <div v-if="currentLesson" class="lesson-content">
            <!-- Video Lesson -->
            <div v-if="currentLesson.type === 'video'" class="video-lesson">
              <div class="video-container">
                <video 
                  ref="videoPlayer"
                  :src="currentLesson.video_url" 
                  controls
                  @timeupdate="updateVideoProgress"
                  @ended="markLessonComplete"
                >
                  Your browser does not support the video tag.
                </video>
              </div>
            </div>

            <!-- Text Lesson -->
            <div v-else-if="currentLesson.type === 'text'" class="text-lesson">
              <div class="text-content" v-html="currentLesson.content"></div>
            </div>

            <!-- Quiz Lesson -->
            <div v-else-if="currentLesson.type === 'quiz'" class="quiz-lesson">
              <div class="quiz-container">
                <h3>{{ currentLesson.title }}</h3>
                <div v-if="!quizCompleted" class="quiz-questions">
                  <div v-for="(question, index) in currentLesson.questions" :key="index" class="question-item">
                    <h4>{{ question.question }}</h4>
                    <div class="answer-options">
                      <label v-for="(option, optionIndex) in question.options" :key="optionIndex" class="option-label">
                        <input 
                          type="radio" 
                          :name="`question-${index}`" 
                          :value="optionIndex"
                          v-model="quizAnswers[index]"
                        >
                        {{ option }}
                      </label>
                    </div>
                  </div>
                  <button @click="submitQuiz" class="submit-quiz-btn">Submit Quiz</button>
                </div>
                <div v-else class="quiz-results">
                  <h4>Quiz Results</h4>
                  <p>Score: {{ quizScore }}%</p>
                  <button @click="retakeQuiz" class="retake-btn">Retake Quiz</button>
                </div>
              </div>
            </div>

            <!-- Lesson Info -->
            <div class="lesson-info">
              <h2>{{ currentLesson.title }}</h2>
              <p v-if="currentLesson.description">{{ currentLesson.description }}</p>
              
              <!-- Lesson Actions -->
              <div class="lesson-actions">
                <button 
                  @click="markLessonComplete" 
                  v-if="!currentLesson.completed"
                  class="complete-btn"
                >
                  Mark as Complete
                </button>
                <button @click="previousLesson" :disabled="!hasPreviousLesson" class="nav-btn">
                  ← Previous
                </button>
                <button @click="nextLesson" :disabled="!hasNextLesson" class="nav-btn">
                  Next →
                </button>
              </div>
            </div>
          </div>

          <!-- No Lesson Selected -->
          <div v-else class="no-lesson">
            <div class="welcome-message">
              <h2>Welcome to {{ course?.title }}</h2>
              <p>Select a lesson from the sidebar to begin learning.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useApiData } from '@/composables/useApiData'
import type { APIError } from '@/services/api'
import { useErrorHandler } from '@/composables/useErrorHandler'
import { api } from '@/services/api'

const route = useRoute()
const { handleApiError } = useErrorHandler()

// Reactive state
const expandedModules = ref([])
const currentLesson = ref(null)
const videoPlayer = ref(null)
const quizAnswers = ref({})
const quizCompleted = ref(false)
const quizScore = ref(0)

// API data
const courseId = route.params.id
const { 
  data: courseData, 
  loading, 
  // error, // Unused
  refresh 
} = useApiData(`/courses/${courseId}/`, {
  immediate: true
})

const { data: modulesData } = useApiData(`/course-modules/?course=${courseId}`, {
  immediate: true
})

const { data: progressData } = useApiData(`/enrollments/`, {
  immediate: true,
  params: { course: courseId }
})

// Computed properties
const course = computed(() => {
  if (!courseData.value) return {}
  // Handle different response structures
  return (courseData.value as any)?.data || courseData.value || {}
})
const modules = computed(() => {
  if (!modulesData.value) return []
  return (modulesData.value as any)?.results || 
         (modulesData.value as any)?.data || 
         (Array.isArray(modulesData.value) ? modulesData.value : [])
})
const courseProgress = computed(() => {
  const enrollment = (progressData.value as any)?.results?.[0] || 
                     (progressData.value as any)?.data?.[0] ||
                     (Array.isArray(progressData.value) ? progressData.value[0] : null)
  return enrollment?.progress_percentage || 0
})

const allLessons = computed(() => {
  return modules.value.flatMap((module: any) => module.lessons || [])
})

const currentLessonIndex = computed(() => {
  return allLessons.value.findIndex((lesson: any) => lesson.id === currentLesson.value?.id)
})

const hasPreviousLesson = computed(() => currentLessonIndex.value > 0)
const hasNextLesson = computed(() => currentLessonIndex.value < allLessons.value.length - 1)

// Methods
const toggleModule = (moduleId: string) => {
  const index = expandedModules.value.indexOf(moduleId)
  if (index > -1) {
    expandedModules.value.splice(index, 1)
  } else {
    expandedModules.value.push(moduleId)
  }
}

const selectLesson = (lesson: any) => {
  currentLesson.value = lesson
  resetQuiz()
}

const previousLesson = () => {
  if (hasPreviousLesson.value) {
    const prevLesson = allLessons.value[currentLessonIndex.value - 1]
    selectLesson(prevLesson)
  }
}

const nextLesson = () => {
  if (hasNextLesson.value) {
    const nextLesson = allLessons.value[currentLessonIndex.value + 1]
    selectLesson(nextLesson)
  }
}

const markLessonComplete = async () => {
  if (!currentLesson.value) return

  try {
    await api.patch(`/course-modules/${currentLesson.value.id}/complete/`)
    currentLesson.value.completed = true
    await refresh()
  } catch (error) {
    handleApiError(error as APIError, { context: { action: 'mark_lesson_complete' } })
  }
}

const updateVideoProgress = (event: Event) => {
  const video = event.target as HTMLVideoElement
  const progress = (video.currentTime / video.duration) * 100
  
  // Auto-mark as complete when 90% watched
  if (progress >= 90 && !currentLesson.value?.completed) {
    markLessonComplete()
  }
}

const submitQuiz = () => {
  if (!currentLesson.value?.questions) return

  let correct = 0
  currentLesson.value.questions.forEach((question, index) => {
    if (quizAnswers.value[index] === question.correct_answer) {
      correct++
    }
  })

  quizScore.value = Math.round((correct / currentLesson.value.questions.length) * 100)
  quizCompleted.value = true

  // Mark as complete if score is above 70%
  if (quizScore.value >= 70) {
    markLessonComplete()
  }
}

const retakeQuiz = () => {
  resetQuiz()
}

const resetQuiz = () => {
  quizAnswers.value = {}
  quizCompleted.value = false
  quizScore.value = 0
}

onMounted(() => {
  // Expand first module by default
  if (modules.value.length > 0) {
    expandedModules.value.push(modules.value[0].id)
    
    // Select first lesson
    if (modules.value[0].lessons?.length > 0) {
      selectLesson(modules.value[0].lessons[0])
    }
  }
})
</script><style
 scoped>
.course-learning-view {
  min-height: 100vh;
  background: #f9fafb;
}

.course-header {
  background: white;
  padding: 1rem 2rem;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.course-info h1 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.25rem;
}

.course-info p {
  color: #6b7280;
  font-size: 0.875rem;
}

.progress-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.progress-bar {
  width: 200px;
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(135deg, #f59e0b, #d97706);
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  white-space: nowrap;
}

.learning-content {
  display: flex;
  height: calc(100vh - 80px);
}

.sidebar {
  width: 350px;
  background: white;
  border-right: 1px solid #e5e7eb;
  overflow-y: auto;
}

.course-navigation {
  padding: 1.5rem;
}

.course-navigation h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 1rem;
}

.modules-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.module-item {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
}

.module-header {
  padding: 1rem;
  background: #f9fafb;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: background-color 0.3s ease;
}

.module-header:hover {
  background: #f3f4f6;
}

.module-title {
  font-weight: 500;
  color: #374151;
}

.module-toggle {
  font-weight: bold;
  color: #6b7280;
}

.lessons-list {
  background: white;
}

.lesson-item {
  padding: 0.75rem 1rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
  transition: all 0.3s ease;
  border-bottom: 1px solid #f3f4f6;
}

.lesson-item:hover {
  background: #f9fafb;
}

.lesson-item.active {
  background: #fef3e2;
  border-left: 3px solid #f59e0b;
}

.lesson-item.completed {
  background: #f0fdf4;
}

.lesson-item.completed .lesson-icon {
  color: #10b981;
}

.lesson-icon {
  font-size: 1rem;
  width: 20px;
  text-align: center;
}

.lesson-title {
  flex: 1;
  font-size: 0.875rem;
  color: #374151;
}

.lesson-duration {
  font-size: 0.75rem;
  color: #6b7280;
}

.main-content {
  flex: 1;
  overflow-y: auto;
  background: white;
}

.lesson-content {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.video-lesson, .text-lesson, .quiz-lesson {
  flex: 1;
  padding: 2rem;
}

.video-container {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
  background: #000;
  border-radius: 8px;
  overflow: hidden;
}

.video-container video {
  width: 100%;
  height: auto;
  display: block;
}

.text-content {
  max-width: 800px;
  margin: 0 auto;
  line-height: 1.6;
  color: #374151;
}

.quiz-container {
  max-width: 600px;
  margin: 0 auto;
}

.quiz-container h3 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 2rem;
}

.question-item {
  background: #f9fafb;
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  border: 1px solid #e5e7eb;
}

.question-item h4 {
  font-size: 1.125rem;
  font-weight: 500;
  color: #1f2937;
  margin-bottom: 1rem;
}

.answer-options {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.option-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 4px;
  transition: background-color 0.3s ease;
}

.option-label:hover {
  background: #f3f4f6;
}

.option-label input[type="radio"] {
  margin: 0;
}

.submit-quiz-btn, .retake-btn {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.submit-quiz-btn:hover, .retake-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(245, 158, 11, 0.4);
}

.quiz-results {
  text-align: center;
  padding: 2rem;
  background: #f0fdf4;
  border-radius: 8px;
  border: 1px solid #bbf7d0;
}

.quiz-results h4 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #166534;
  margin-bottom: 1rem;
}

.quiz-results p {
  font-size: 1.125rem;
  color: #166534;
  margin-bottom: 1.5rem;
}

.lesson-info {
  background: #f9fafb;
  padding: 2rem;
  border-top: 1px solid #e5e7eb;
}

.lesson-info h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.lesson-info p {
  color: #6b7280;
  margin-bottom: 1.5rem;
}

.lesson-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.complete-btn, .nav-btn {
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
}

.complete-btn {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
}

.complete-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(16, 185, 129, 0.4);
}

.nav-btn {
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
}

.nav-btn:hover:not(:disabled) {
  background: #e5e7eb;
}

.nav-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.no-lesson {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 2rem;
}

.welcome-message {
  text-align: center;
  max-width: 400px;
}

.welcome-message h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 1rem;
}

.welcome-message p {
  color: #6b7280;
}

/* Loading State */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  background: white;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f4f6;
  border-top: 4px solid #f59e0b;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Responsive */
@media (max-width: 768px) {
  .course-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .progress-info {
    justify-content: center;
  }
  
  .learning-content {
    flex-direction: column;
    height: auto;
  }
  
  .sidebar {
    width: 100%;
    max-height: 300px;
  }
  
  .main-content {
    min-height: 500px;
  }
  
  .video-lesson, .text-lesson, .quiz-lesson, .lesson-info {
    padding: 1rem;
  }
  
  .lesson-actions {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>