<template>
  <div class="ai-quiz-generator bg-white rounded-lg shadow-lg">
    <!-- Header -->
    <div class="p-6 border-b border-gray-200">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <div class="w-10 h-10 bg-gradient-to-r from-purple-500 to-pink-600 rounded-full flex items-center justify-center">
            <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div>
            <h3 class="text-lg font-semibold text-gray-900">AI Quiz Generator</h3>
            <p class="text-sm text-gray-500">Create intelligent quizzes from your content</p>
          </div>
        </div>
        
        <button
          @click="showQuizHistory = !showQuizHistory"
          class="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 transition-colors"
          title="Quiz History"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Quiz History Sidebar -->
    <div 
      v-if="showQuizHistory"
      class="absolute top-20 right-6 w-80 bg-white border border-gray-200 rounded-lg shadow-lg z-10 max-h-96 overflow-y-auto"
    >
      <div class="p-3 border-b border-gray-200">
        <h4 class="font-medium text-gray-900">Recent Quizzes</h4>
      </div>
      <div class="p-2">
        <div
          v-for="quiz in quizzes"
          :key="quiz.id"
          @click="viewQuiz(quiz)"
          class="p-3 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
        >
          <div class="font-medium text-sm text-gray-900 truncate">
            {{ quiz.title }}
          </div>
          <div class="text-xs text-gray-500 mt-1">
            {{ formatDate(quiz.created_at) }} • {{ quiz.question_count }} questions • {{ quiz.difficulty_level }}
          </div>
        </div>
        
        <div v-if="quizzes.length === 0" class="p-3 text-center text-gray-500 text-sm">
          No quizzes yet
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="p-6">
      <!-- Generate Quiz Form -->
      <div v-if="!currentQuiz" class="space-y-6">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label for="quiz-title" class="block text-sm font-medium text-gray-700 mb-2">
              Quiz Title
            </label>
            <input
              id="quiz-title"
              v-model="quizForm.title"
              type="text"
              placeholder="Enter quiz title..."
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            />
          </div>

          <div>
            <label for="course-select" class="block text-sm font-medium text-gray-700 mb-2">
              Course <span class="text-red-500">*</span>
            </label>
            <select
              id="course-select"
              v-model="quizForm.courseId"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              required
            >
              <option value="">Select a course...</option>
              <option v-for="course in availableCourses" :key="course.id" :value="course.id">
                {{ course.title }}
              </option>
            </select>
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label for="num-questions" class="block text-sm font-medium text-gray-700 mb-2">
              Number of Questions
            </label>
            <select
              id="num-questions"
              v-model="quizForm.numQuestions"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              <option :value="3">3 questions</option>
              <option :value="5">5 questions</option>
              <option :value="10">10 questions</option>
              <option :value="15">15 questions</option>
              <option :value="20">20 questions</option>
            </select>
          </div>

          <div>
            <label for="difficulty" class="block text-sm font-medium text-gray-700 mb-2">
              Difficulty Level
            </label>
            <select
              id="difficulty"
              v-model="quizForm.difficulty"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              <option value="easy">Easy</option>
              <option value="medium">Medium</option>
              <option value="hard">Hard</option>
            </select>
          </div>
        </div>

        <div>
          <label for="content-input" class="block text-sm font-medium text-gray-700 mb-2">
            Content for Quiz Generation
          </label>
          <textarea
            id="content-input"
            v-model="quizForm.content"
            rows="8"
            placeholder="Paste your content here (lecture notes, textbook chapters, etc.)..."
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
          ></textarea>
          <div class="mt-1 text-sm text-gray-500">
            {{ quizForm.content.length }} characters
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
            <span v-if="!canUseFeature('quiz')" class="text-red-600">
              Quiz generation quota exceeded
            </span>
            <span v-else>
              AI will generate {{ quizForm.numQuestions }} {{ quizForm.difficulty }} questions
            </span>
          </div>
          
          <button
            @click="handleGenerateQuiz"
            :disabled="!canGenerateQuiz || loading.quiz"
            class="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
          >
            <svg v-if="loading.quiz" class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>{{ loading.quiz ? 'Generating...' : 'Generate Quiz' }}</span>
          </button>
        </div>
      </div>

      <!-- Quiz Display -->
      <div v-else class="space-y-6">
        <!-- Quiz Header -->
        <div class="flex items-center justify-between">
          <div>
            <h4 class="text-xl font-semibold text-gray-900">{{ currentQuiz.title }}</h4>
            <div class="flex items-center space-x-4 mt-1 text-sm text-gray-500">
              <span class="capitalize">{{ currentQuiz.difficulty_level }} difficulty</span>
              <span>•</span>
              <span>{{ currentQuiz.question_count }} questions</span>
              <span>•</span>
              <span>{{ formatDate(currentQuiz.created_at) }}</span>
            </div>
          </div>
          
          <div class="flex space-x-2">
            <button
              @click="startQuizMode"
              class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center space-x-2"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1.01M15 10h1.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>Take Quiz</span>
            </button>
            
            <button
              @click="clearCurrentQuiz"
              class="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 transition-colors"
              title="Create New Quiz"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
            </button>
          </div>
        </div>

        <!-- Quiz Mode -->
        <div v-if="isQuizMode" class="quiz-mode">
          <div class="bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg p-6 border border-purple-200">
            <!-- Progress Bar -->
            <div class="mb-6">
              <div class="flex justify-between text-sm text-gray-600 mb-2">
                <span>Question {{ currentQuestionIndex + 1 }} of {{ currentQuiz.questions.length }}</span>
                <span>{{ Math.round(((currentQuestionIndex + 1) / currentQuiz.questions.length) * 100) }}% Complete</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div 
                  class="bg-purple-600 h-2 rounded-full transition-all duration-300"
                  :style="{ width: `${((currentQuestionIndex + 1) / currentQuiz.questions.length) * 100}%` }"
                ></div>
              </div>
            </div>

            <!-- Current Question -->
            <div v-if="currentQuestion" class="space-y-4">
              <h5 class="text-lg font-semibold text-gray-900">
                {{ currentQuestion.question }}
              </h5>

              <!-- Multiple Choice Options -->
              <div v-if="currentQuestion.type === 'multiple_choice'" class="space-y-3">
                <div
                  v-for="(option, index) in currentQuestion.options"
                  :key="index"
                  @click="selectAnswer(index)"
                  class="p-3 border border-gray-300 rounded-lg cursor-pointer transition-colors hover:bg-purple-50"
                  :class="{
                    'bg-purple-100 border-purple-500': selectedAnswers[currentQuestionIndex] === index,
                    'bg-green-100 border-green-500': showAnswers && index === currentQuestion.correct_answer,
                    'bg-red-100 border-red-500': showAnswers && selectedAnswers[currentQuestionIndex] === index && index !== currentQuestion.correct_answer
                  }"
                >
                  <div class="flex items-center space-x-3">
                    <div class="w-6 h-6 border-2 border-gray-400 rounded-full flex items-center justify-center">
                      <div 
                        v-if="selectedAnswers[currentQuestionIndex] === index"
                        class="w-3 h-3 bg-purple-600 rounded-full"
                      ></div>
                    </div>
                    <span>{{ option }}</span>
                  </div>
                </div>
              </div>

              <!-- True/False Options -->
              <div v-else-if="currentQuestion.type === 'true_false'" class="space-y-3">
                <div
                  @click="selectAnswer(true)"
                  class="p-3 border border-gray-300 rounded-lg cursor-pointer transition-colors hover:bg-purple-50"
                  :class="{
                    'bg-purple-100 border-purple-500': selectedAnswers[currentQuestionIndex] === true,
                    'bg-green-100 border-green-500': showAnswers && currentQuestion.correct_answer === 'true',
                    'bg-red-100 border-red-500': showAnswers && selectedAnswers[currentQuestionIndex] === true && currentQuestion.correct_answer !== 'true'
                  }"
                >
                  <div class="flex items-center space-x-3">
                    <div class="w-6 h-6 border-2 border-gray-400 rounded-full flex items-center justify-center">
                      <div 
                        v-if="selectedAnswers[currentQuestionIndex] === true"
                        class="w-3 h-3 bg-purple-600 rounded-full"
                      ></div>
                    </div>
                    <span>True</span>
                  </div>
                </div>
                
                <div
                  @click="selectAnswer(false)"
                  class="p-3 border border-gray-300 rounded-lg cursor-pointer transition-colors hover:bg-purple-50"
                  :class="{
                    'bg-purple-100 border-purple-500': selectedAnswers[currentQuestionIndex] === false,
                    'bg-green-100 border-green-500': showAnswers && currentQuestion.correct_answer === 'false',
                    'bg-red-100 border-red-500': showAnswers && selectedAnswers[currentQuestionIndex] === false && currentQuestion.correct_answer !== 'false'
                  }"
                >
                  <div class="flex items-center space-x-3">
                    <div class="w-6 h-6 border-2 border-gray-400 rounded-full flex items-center justify-center">
                      <div 
                        v-if="selectedAnswers[currentQuestionIndex] === false"
                        class="w-3 h-3 bg-purple-600 rounded-full"
                      ></div>
                    </div>
                    <span>False</span>
                  </div>
                </div>
              </div>

              <!-- Short Answer -->
              <div v-else-if="currentQuestion.type === 'short_answer'" class="space-y-3">
                <textarea
                  v-model="selectedAnswers[currentQuestionIndex]"
                  rows="3"
                  placeholder="Enter your answer..."
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  :disabled="showAnswers"
                ></textarea>
                
                <div v-if="showAnswers" class="p-3 bg-green-50 border border-green-200 rounded-lg">
                  <div class="font-medium text-green-800 mb-1">Correct Answer:</div>
                  <div class="text-green-700">{{ currentQuestion.correct_answer }}</div>
                </div>
              </div>

              <!-- Explanation -->
              <div v-if="showAnswers && currentQuestion.explanation" class="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                <div class="font-medium text-blue-800 mb-1">Explanation:</div>
                <div class="text-blue-700">{{ currentQuestion.explanation }}</div>
              </div>
            </div>

            <!-- Navigation -->
            <div class="flex justify-between items-center mt-6 pt-4 border-t border-gray-200">
              <button
                @click="previousQuestion"
                :disabled="currentQuestionIndex === 0"
                class="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Previous
              </button>

              <div class="flex space-x-3">
                <button
                  v-if="!showAnswers"
                  @click="showAnswers = true"
                  :disabled="selectedAnswers[currentQuestionIndex] === undefined"
                  class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  Show Answer
                </button>

                <button
                  @click="nextQuestion"
                  :disabled="currentQuestionIndex === currentQuiz.questions.length - 1"
                  class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {{ currentQuestionIndex === currentQuiz.questions.length - 1 ? 'Finish' : 'Next' }}
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Quiz Preview Mode -->
        <div v-else class="space-y-4">
          <div
            v-for="(question, index) in currentQuiz.questions"
            :key="index"
            class="p-4 border border-gray-200 rounded-lg hover:border-gray-300 transition-colors"
          >
            <div class="flex items-start space-x-3">
              <div class="w-8 h-8 bg-purple-600 text-white rounded-full flex items-center justify-center text-sm font-semibold flex-shrink-0">
                {{ index + 1 }}
              </div>
              <div class="flex-1">
                <h6 class="font-medium text-gray-900 mb-2">{{ question.question }}</h6>
                
                <div v-if="question.type === 'multiple_choice'" class="space-y-1 text-sm text-gray-600">
                  <div v-for="(option, optionIndex) in question.options" :key="optionIndex">
                    {{ String.fromCharCode(65 + optionIndex) }}. {{ option }}
                  </div>
                </div>
                
                <div v-else-if="question.type === 'true_false'" class="text-sm text-gray-600">
                  True / False
                </div>
                
                <div v-else class="text-sm text-gray-600">
                  Short answer question
                </div>
                
                <div class="mt-2 text-xs text-gray-500">
                  {{ question.points }} points • {{ question.type.replace('_', ' ') }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex justify-between items-center pt-4 border-t border-gray-200">
          <div class="text-sm text-gray-500">
            Tokens used: {{ currentQuiz.tokens_used }} • Generation time: {{ currentQuiz.generation_time_ms }}ms
          </div>
          
          <div class="flex space-x-3">
            <button
              @click="exportQuiz"
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
import { useCourse } from '@/composables/useCourse'
import type { AIQuiz } from '@/types/ai'

// Props
interface Props {
  courseId?: string
  initialContent?: string
  initialTitle?: string
}

const props = defineProps<Props>()

// Composables
const {
  quizzes,
  loading,
  error,
  loadQuizzes,
  generateQuiz,
  clearError,
  canUseFeature
} = useAI()

const { courses: availableCourses, fetchCourses } = useCourse()
const { slideIn, staggerIn } = useAnimations()

// Local state
const showQuizHistory = ref(false)
const currentQuiz = ref<AIQuiz | null>(null)
const isQuizMode = ref(false)
const currentQuestionIndex = ref(0)
const selectedAnswers = ref<Record<number, any>>({})
const showAnswers = ref(false)

const quizForm = ref({
  title: props.initialTitle || '',
  content: props.initialContent || '',
  courseId: props.courseId || '',
  numQuestions: 5,
  difficulty: 'medium' as 'easy' | 'medium' | 'hard'
})

// Computed
const canGenerateQuiz = computed(() => {
  return quizForm.value.title.trim() && 
         quizForm.value.content.trim() && 
         quizForm.value.courseId &&
         canUseFeature('quiz')
})

const currentQuestion = computed(() => {
  if (!currentQuiz.value || !currentQuiz.value.questions) return null
  return currentQuiz.value.questions[currentQuestionIndex.value]
})

// Methods
const handleGenerateQuiz = async () => {
  if (!canGenerateQuiz.value) return

  try {
    await generateQuiz({
      content: quizForm.value.content,
      course_id: quizForm.value.courseId,
      title: quizForm.value.title,
      num_questions: quizForm.value.numQuestions,
      difficulty: quizForm.value.difficulty
    })

    // Find the newly created quiz
    await loadQuizzes()
    const newQuiz = quizzes.value.find(q => q.title === quizForm.value.title)
    if (newQuiz) {
      currentQuiz.value = newQuiz
      
      // Animate the quiz display
      await nextTick()
      const quizElement = document.querySelector('.space-y-4')
      if (quizElement) {
        staggerIn(quizElement, { delay: 100 })
      }
    }
  } catch (err) {
    console.error('Failed to generate quiz:', err)
  }
}

const viewQuiz = (quiz: AIQuiz) => {
  currentQuiz.value = quiz
  showQuizHistory.value = false
  isQuizMode.value = false
  
  // Animate the quiz display
  nextTick(() => {
    const quizElement = document.querySelector('.space-y-4')
    if (quizElement) {
      slideIn(quizElement, 'right', { duration: 600, easing: 'easeOutExpo' })
    }
  })
}

const clearCurrentQuiz = () => {
  currentQuiz.value = null
  isQuizMode.value = false
  currentQuestionIndex.value = 0
  selectedAnswers.value = {}
  showAnswers.value = false
  quizForm.value = {
    title: '',
    content: '',
    courseId: props.courseId || '',
    numQuestions: 5,
    difficulty: 'medium'
  }
}

const startQuizMode = () => {
  isQuizMode.value = true
  currentQuestionIndex.value = 0
  selectedAnswers.value = {}
  showAnswers.value = false
}

const selectAnswer = (answer: any) => {
  if (showAnswers.value) return
  selectedAnswers.value[currentQuestionIndex.value] = answer
}

const nextQuestion = () => {
  if (currentQuestionIndex.value < (currentQuiz.value?.questions.length || 0) - 1) {
    currentQuestionIndex.value++
    showAnswers.value = false
  }
}

const previousQuestion = () => {
  if (currentQuestionIndex.value > 0) {
    currentQuestionIndex.value--
    showAnswers.value = false
  }
}

const exportQuiz = () => {
  if (!currentQuiz.value) return

  let text = `${currentQuiz.value.title}\n`
  text += `Difficulty: ${currentQuiz.value.difficulty_level}\n`
  text += `Questions: ${currentQuiz.value.question_count}\n\n`

  currentQuiz.value.questions.forEach((question, index) => {
    text += `${index + 1}. ${question.question}\n`
    
    if (question.type === 'multiple_choice' && question.options) {
      question.options.forEach((option, optionIndex) => {
        text += `   ${String.fromCharCode(65 + optionIndex)}. ${option}\n`
      })
      text += `   Correct Answer: ${String.fromCharCode(65 + (question.correct_answer as number))}\n`
    } else if (question.type === 'true_false') {
      text += `   True / False\n`
      text += `   Correct Answer: ${question.correct_answer}\n`
    } else {
      text += `   Correct Answer: ${question.correct_answer}\n`
    }
    
    if (question.explanation) {
      text += `   Explanation: ${question.explanation}\n`
    }
    
    text += `   Points: ${question.points}\n\n`
  })

  const blob = new Blob([text], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${currentQuiz.value.title} - Quiz.txt`
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
    await Promise.all([
      loadQuizzes(),
      fetchCourses()
    ])
  } catch (err) {
    console.error('Failed to initialize quiz generator:', err)
  }
})
</script>

<style scoped>
/* Quiz mode animations */
.quiz-mode {
  animation: slideInUp 0.5s ease-out;
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

/* Progress bar animation */
.bg-purple-600 {
  transition: width 0.3s ease-in-out;
}

/* Question transition */
.space-y-4 > div {
  transition: all 0.3s ease-in-out;
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