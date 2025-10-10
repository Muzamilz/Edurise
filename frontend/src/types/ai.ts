// AI Types for Frontend

export interface AIConversation {
  id: string
  title: string
  conversation_type: 'tutor' | 'general' | 'course_help'
  context: Record<string, any>
  course?: string
  is_active: boolean
  last_activity: string
  created_at: string
  updated_at: string
  messages?: AIMessage[]
  message_count: number
}

export interface AIMessage {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  tokens_used: number
  response_time_ms?: number
  created_at: string
}

export interface AIContentSummary {
  id: string
  content_type: 'live_class' | 'course_module' | 'video' | 'text'
  content_id: string
  content_title: string
  course?: string
  course_title?: string
  summary: string
  key_points: string[]
  tokens_used: number
  generation_time_ms: number
  created_at: string
}

export interface AIQuiz {
  id: string
  title: string
  description: string
  difficulty_level: 'easy' | 'medium' | 'hard'
  course: string
  course_title?: string
  questions: QuizQuestion[]
  question_count: number
  tokens_used: number
  generation_time_ms: number
  created_at: string
}

export interface QuizQuestion {
  id: string
  question: string
  type: 'multiple_choice' | 'true_false' | 'short_answer'
  options?: string[]
  correct_answer: string | number
  explanation?: string
  points: number
}

export interface AIUsageQuota {
  id: string
  month: string
  // Chat usage
  chat_messages_used: number
  chat_messages_limit: number
  chat_usage_percentage: number
  chat_tokens_used: number
  chat_tokens_limit: number
  // Summary usage
  summaries_generated: number
  summaries_limit: number
  summary_usage_percentage: number
  summary_tokens_used: number
  summary_tokens_limit: number
  // Quiz usage
  quizzes_generated: number
  quizzes_limit: number
  quiz_usage_percentage: number
  quiz_tokens_used: number
  quiz_tokens_limit: number
  // Cost tracking
  total_cost_usd: number
  cost_limit_usd: number
  cost_usage_percentage: number
  created_at: string
  updated_at: string
}

// Request/Response types
export interface ChatMessageRequest {
  message: string
  context?: Record<string, any>
}

export interface ChatMessageResponse {
  success: boolean
  ai_response: string
  metadata: {
    conversation_id: string
    user_message_id: string
    ai_message_id: string
    tokens_used: number
    response_time_ms: number
    remaining_quota: number
  }
}

export interface SummaryRequest {
  content: string
  content_type: 'live_class' | 'course_module' | 'video' | 'text'
  content_id?: string
  content_title: string
  course_id?: string
}

export interface SummaryResponse {
  success: boolean
  summary: string
  key_points: string[]
  metadata: {
    summary_id: string
    tokens_used: number
    generation_time_ms: number
    remaining_quota: number
  }
}

export interface QuizRequest {
  content: string
  course_id: string
  title: string
  num_questions: number
  difficulty: 'easy' | 'medium' | 'hard'
}

export interface QuizResponse {
  success: boolean
  questions: QuizQuestion[]
  metadata: {
    quiz_id: string
    tokens_used: number
    generation_time_ms: number
    remaining_quota: number
    difficulty: string
    num_questions: number
  }
}

export interface UsageStatsResponse {
  success: boolean
  stats: {
    chat: {
      messages_used: number
      messages_limit: number
      tokens_used: number
      tokens_limit: number
      percentage_used: number
    }
    summaries: {
      summaries_used: number
      summaries_limit: number
      tokens_used: number
      tokens_limit: number
      percentage_used: number
    }
    quizzes: {
      quizzes_used: number
      quizzes_limit: number
      tokens_used: number
      tokens_limit: number
      percentage_used: number
    }
    cost: {
      total_cost_usd: number
      cost_limit_usd: number
      percentage_used: number
    }
    month: string
  }
}

// UI State types
export interface AIError {
  type: 'quota_exceeded' | 'rate_limit_exceeded' | 'ai_service_error' | 'internal_error'
  message: string
}

export interface AILoadingState {
  chat: boolean
  summary: boolean
  quiz: boolean
  usage: boolean
}