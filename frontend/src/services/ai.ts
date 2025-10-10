import { api } from './api'
import type { 
  AIConversation, 
  AIMessage, 
  AIContentSummary, 
  AIQuiz, 
  AIUsageQuota,
  ChatMessageResponse,
  SummaryRequest,
  SummaryResponse,
  QuizRequest,
  QuizResponse,
  UsageStatsResponse
} from '../types/ai'

export class AIService {
  // AI Tutor Chat Methods
  static async getConversations(): Promise<AIConversation[]> {
    const response = await api.get<AIConversation[]>('/ai/conversations/')
    return response.data
  }

  static async createConversation(data: {
    title?: string
    conversation_type?: string
    context?: Record<string, any>
    course?: string
  }): Promise<AIConversation> {
    const response = await api.post<AIConversation>('/ai/conversations/', data)
    return response.data
  }

  static async getConversation(id: string): Promise<AIConversation> {
    const response = await api.get<AIConversation>(`/ai/conversations/${id}/`)
    return response.data
  }

  static async getConversationMessages(id: string): Promise<AIMessage[]> {
    const response = await api.get<AIMessage[]>(`/ai/conversations/${id}/messages/`)
    return response.data
  }

  static async sendMessage(
    conversationId: string, 
    message: string, 
    context?: Record<string, any>
  ): Promise<ChatMessageResponse> {
    const response = await api.post<ChatMessageResponse>(
      `/ai/conversations/${conversationId}/send_message/`,
      { message, context }
    )
    return response.data
  }

  // Content Summarization Methods
  static async getSummaries(): Promise<AIContentSummary[]> {
    const response = await api.get<AIContentSummary[]>('/ai/summaries/')
    return response.data
  }

  static async generateSummary(data: SummaryRequest): Promise<SummaryResponse> {
    const response = await api.post<SummaryResponse>('/ai/summaries/generate/', data)
    return response.data
  }

  static async getSummary(id: string): Promise<AIContentSummary> {
    const response = await api.get<AIContentSummary>(`/ai/summaries/${id}/`)
    return response.data
  }

  // Quiz Generation Methods
  static async getQuizzes(): Promise<AIQuiz[]> {
    const response = await api.get<AIQuiz[]>('/ai/quizzes/')
    return response.data
  }

  static async generateQuiz(data: QuizRequest): Promise<QuizResponse> {
    const response = await api.post<QuizResponse>('/ai/quizzes/generate/', data)
    return response.data
  }

  static async getQuiz(id: string): Promise<AIQuiz> {
    const response = await api.get<AIQuiz>(`/ai/quizzes/${id}/`)
    return response.data
  }

  // Usage and Quota Methods
  static async getUsageStats(): Promise<UsageStatsResponse> {
    const response = await api.get<UsageStatsResponse>('/ai/usage/current_stats/')
    return response.data
  }

  static async getUsageHistory(): Promise<AIUsageQuota[]> {
    const response = await api.get<AIUsageQuota[]>('/ai/usage/')
    return response.data
  }

  // Error handling helper
  static handleAIError(error: any): string {
    if (error.response?.data?.error_type) {
      switch (error.response.data.error_type) {
        case 'quota_exceeded':
          return 'AI usage quota exceeded for this month. Please upgrade your plan or wait for next month.'
        case 'rate_limit_exceeded':
          return 'Too many requests. Please wait a moment before trying again.'
        case 'ai_service_error':
          return 'AI service is temporarily unavailable. Please try again later.'
        default:
          return error.response.data.error || 'An unexpected error occurred'
      }
    }
    return error.message || 'An unexpected error occurred'
  }
}