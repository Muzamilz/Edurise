import { ref, computed, reactive } from 'vue'
import { AIService } from '@/services/ai'
import type { 
  AIConversation, 
  AIMessage, 
  AIContentSummary, 
  AIQuiz, 
  AIUsageQuota,
  AIError,
  AILoadingState,
  SummaryRequest,
  QuizRequest,
  UsageStatsResponse
} from '@/types/ai'

export const useAI = () => {
  // State
  const conversations = ref<AIConversation[]>([])
  const currentConversation = ref<AIConversation | null>(null)
  const messages = ref<AIMessage[]>([])
  const summaries = ref<AIContentSummary[]>([])
  const quizzes = ref<AIQuiz[]>([])
  const usageStats = ref<UsageStatsResponse['stats'] | null>(null)
  const usageHistory = ref<AIUsageQuota[]>([])
  
  const loading = reactive<AILoadingState>({
    chat: false,
    summary: false,
    quiz: false,
    usage: false
  })
  
  const error = ref<AIError | null>(null)

  // Computed
  const hasActiveConversation = computed(() => !!currentConversation.value)
  const isQuotaExceeded = computed(() => {
    if (!usageStats.value) return false
    return usageStats.value.chat.percentage_used >= 100 ||
           usageStats.value.summaries.percentage_used >= 100 ||
           usageStats.value.quizzes.percentage_used >= 100
  })

  // Chat Methods
  const loadConversations = async () => {
    try {
      loading.chat = true
      error.value = null
      conversations.value = await AIService.getConversations()
    } catch (err: any) {
      error.value = {
        type: err.response?.data?.error_type || 'internal_error',
        message: AIService.handleAIError(err)
      }
      throw err
    } finally {
      loading.chat = false
    }
  }

  const createConversation = async (data: {
    title?: string
    conversation_type?: string
    context?: Record<string, any>
    course?: string
  }) => {
    try {
      loading.chat = true
      error.value = null
      const conversation = await AIService.createConversation(data)
      conversations.value.unshift(conversation)
      currentConversation.value = conversation
      messages.value = []
      return conversation
    } catch (err: any) {
      error.value = {
        type: err.response?.data?.error_type || 'internal_error',
        message: AIService.handleAIError(err)
      }
      throw err
    } finally {
      loading.chat = false
    }
  }

  const selectConversation = async (conversationId: string) => {
    try {
      loading.chat = true
      error.value = null
      
      const conversation = await AIService.getConversation(conversationId)
      const conversationMessages = await AIService.getConversationMessages(conversationId)
      
      currentConversation.value = conversation
      messages.value = conversationMessages
    } catch (err: any) {
      error.value = {
        type: err.response?.data?.error_type || 'internal_error',
        message: AIService.handleAIError(err)
      }
      throw err
    } finally {
      loading.chat = false
    }
  }

  const sendMessage = async (message: string, context?: Record<string, any>) => {
    if (!currentConversation.value) {
      throw new Error('No active conversation')
    }

    try {
      loading.chat = true
      error.value = null

      // Add user message to UI immediately with smooth animation
      const userMessage: AIMessage = {
        id: `temp-${Date.now()}`,
        role: 'user',
        content: message,
        tokens_used: 0,
        created_at: new Date().toISOString()
      }
      messages.value.push(userMessage)

      // Send to AI service
      const response = await AIService.sendMessage(
        currentConversation.value.id,
        message,
        context
      )

      // Remove temporary message and add real messages
      messages.value = messages.value.filter(m => m.id !== userMessage.id)
      
      // Reload messages to get the actual conversation
      const updatedMessages = await AIService.getConversationMessages(currentConversation.value.id)
      messages.value = updatedMessages

      // Update usage stats in background
      loadUsageStats().catch(console.error)

      return response
    } catch (err: any) {
      // Remove temporary message on error
      messages.value = messages.value.filter(m => m.role !== 'user' || m.id.startsWith('temp-'))
      
      error.value = {
        type: err.response?.data?.error_type || 'internal_error',
        message: AIService.handleAIError(err)
      }
      throw err
    } finally {
      loading.chat = false
    }
  }

  // Summary Methods
  const loadSummaries = async () => {
    try {
      loading.summary = true
      error.value = null
      summaries.value = await AIService.getSummaries()
    } catch (err: any) {
      error.value = {
        type: err.response?.data?.error_type || 'internal_error',
        message: AIService.handleAIError(err)
      }
      throw err
    } finally {
      loading.summary = false
    }
  }

  const generateSummary = async (data: SummaryRequest) => {
    try {
      loading.summary = true
      error.value = null
      
      const response = await AIService.generateSummary(data)
      
      // Reload summaries to include the new one
      await loadSummaries()
      
      // Update usage stats
      await loadUsageStats()
      
      return response
    } catch (err: any) {
      error.value = {
        type: err.response?.data?.error_type || 'internal_error',
        message: AIService.handleAIError(err)
      }
      throw err
    } finally {
      loading.summary = false
    }
  }

  // Quiz Methods
  const loadQuizzes = async () => {
    try {
      loading.quiz = true
      error.value = null
      quizzes.value = await AIService.getQuizzes()
    } catch (err: any) {
      error.value = {
        type: err.response?.data?.error_type || 'internal_error',
        message: AIService.handleAIError(err)
      }
      throw err
    } finally {
      loading.quiz = false
    }
  }

  const generateQuiz = async (data: QuizRequest) => {
    try {
      loading.quiz = true
      error.value = null
      
      const response = await AIService.generateQuiz(data)
      
      // Reload quizzes to include the new one
      await loadQuizzes()
      
      // Update usage stats
      await loadUsageStats()
      
      return response
    } catch (err: any) {
      error.value = {
        type: err.response?.data?.error_type || 'internal_error',
        message: AIService.handleAIError(err)
      }
      throw err
    } finally {
      loading.quiz = false
    }
  }

  // Usage Methods
  const loadUsageStats = async () => {
    try {
      loading.usage = true
      error.value = null
      const response = await AIService.getUsageStats()
      usageStats.value = response.stats
    } catch (err: any) {
      error.value = {
        type: err.response?.data?.error_type || 'internal_error',
        message: AIService.handleAIError(err)
      }
      throw err
    } finally {
      loading.usage = false
    }
  }

  const loadUsageHistory = async () => {
    try {
      loading.usage = true
      error.value = null
      usageHistory.value = await AIService.getUsageHistory()
    } catch (err: any) {
      error.value = {
        type: err.response?.data?.error_type || 'internal_error',
        message: AIService.handleAIError(err)
      }
      throw err
    } finally {
      loading.usage = false
    }
  }

  // Utility Methods
  const clearError = () => {
    error.value = null
  }

  const clearCurrentConversation = () => {
    currentConversation.value = null
    messages.value = []
  }

  const formatUsagePercentage = (used: number, limit: number): number => {
    if (limit === 0) return 0
    return Math.round((used / limit) * 100)
  }

  const getUsageColor = (percentage: number): string => {
    if (percentage >= 90) return 'text-red-600'
    if (percentage >= 75) return 'text-yellow-600'
    return 'text-green-600'
  }

  const canUseFeature = (feature: 'chat' | 'summary' | 'quiz'): boolean => {
    if (!usageStats.value) return true
    
    switch (feature) {
      case 'chat':
        return usageStats.value.chat.percentage_used < 100
      case 'summary':
        return usageStats.value.summaries.percentage_used < 100
      case 'quiz':
        return usageStats.value.quizzes.percentage_used < 100
      default:
        return true
    }
  }

  return {
    // State
    conversations,
    currentConversation,
    messages,
    summaries,
    quizzes,
    usageStats,
    usageHistory,
    loading,
    error,

    // Computed
    hasActiveConversation,
    isQuotaExceeded,

    // Chat Methods
    loadConversations,
    createConversation,
    selectConversation,
    sendMessage,

    // Summary Methods
    loadSummaries,
    generateSummary,

    // Quiz Methods
    loadQuizzes,
    generateQuiz,

    // Usage Methods
    loadUsageStats,
    loadUsageHistory,

    // Utility Methods
    clearError,
    clearCurrentConversation,
    formatUsagePercentage,
    getUsageColor,
    canUseFeature
  }
}