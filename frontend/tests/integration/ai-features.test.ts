/**
 * Integration tests for AI features frontend functionality
 * Tests AI tutor chat, content summarization, quiz generation, and quota display
 * Requirements: 6.1, 6.2, 6.3, 6.5
 */

import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import axios from 'axios'
import { AIService } from '@/services/ai'
import { useAI } from '@/composables/useAI'

// Mock axios
vi.mock('axios')
const mockedAxios = vi.mocked(axios)

// Mock API responses
const mockAIResponses = {
  chatResponse: {
    success: true,
    ai_response: 'This is a helpful AI tutor response about machine learning concepts.',
    metadata: {
      conversation_id: 'test-conversation-id',
      tokens_used: 150,
      response_time_ms: 800,
      remaining_quota: 45
    }
  },
  summaryResponse: {
    success: true,
    summary: 'This is a concise summary of the machine learning content covering key concepts.',
    key_points: [
      'Machine learning is a subset of AI',
      'Three main types: supervised, unsupervised, reinforcement',
      'Applications include classification and regression'
    ],
    metadata: {
      summary_id: 'test-summary-id',
      tokens_used: 200,
      generation_time_ms: 1200,
      remaining_quota: 18
    }
  },
  quizResponse: {
    success: true,
    questions: [
      {
        question: 'What is machine learning?',
        type: 'multiple_choice',
        options: [
          'A type of computer hardware',
          'A subset of artificial intelligence',
          'A programming language',
          'A database system'
        ],
        correct_answer: 1,
        explanation: 'Machine learning is indeed a subset of artificial intelligence.'
      }
    ],
    metadata: {
      quiz_id: 'test-quiz-id',
      tokens_used: 300,
      generation_time_ms: 1500,
      remaining_quota: 4
    }
  },
  usageStats: {
    success: true,
    stats: {
      chat: {
        messages_used: 5,
        messages_limit: 50,
        percentage_used: 10.0
      },
      summaries: {
        summaries_used: 2,
        summaries_limit: 20,
        percentage_used: 10.0
      },
      quizzes: {
        quizzes_used: 1,
        quizzes_limit: 5,
        percentage_used: 20.0
      }
    }
  }
}

describe('AI Features Integration Tests', () => {
  let pinia: any

  beforeEach(() => {
    pinia = createPinia()
    vi.clearAllMocks()
    
    // Setup default axios mock
    mockedAxios.create = vi.fn(() => mockedAxios)
    mockedAxios.interceptors = {
      request: { use: vi.fn() },
      response: { use: vi.fn() }
    }
    
    // Default successful response
    mockedAxios.get = vi.fn().mockResolvedValue({ data: mockAIResponses.chatResponse })
    mockedAxios.post = vi.fn().mockResolvedValue({ data: mockAIResponses.chatResponse })
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('AI Tutor Chat - Context Retention and Conversation Flow (Requirement 6.1)', () => {
    it('should maintain conversation context across multiple messages', async () => {
      // Mock conversation creation
      mockedAxios.post
        .mockResolvedValueOnce({
          data: {
            id: 'test-conversation-id',
            title: 'AI Learning Session',
            conversation_type: 'tutor',
            created_at: new Date().toISOString()
          }
        })
        .mockResolvedValueOnce({
          data: mockAIResponses.chatResponse
        })
      
      mockedAxios.get.mockResolvedValueOnce({
        data: [
          {
            id: 'msg-1',
            role: 'user',
            content: 'What is machine learning?',
            created_at: new Date().toISOString()
          },
          {
            id: 'msg-2',
            role: 'assistant',
            content: mockAIResponses.chatResponse.ai_response,
            created_at: new Date().toISOString()
          }
        ]
      })

      // Test conversation creation
      const conversation = await AIService.createConversation({
        title: 'AI Learning Session',
        conversation_type: 'tutor',
        context: {
          course_id: 'test-course-id',
          topic: 'machine learning basics'
        }
      })

      expect(conversation.id).toBe('test-conversation-id')
      expect(conversation.title).toBe('AI Learning Session')

      // Test sending message with context
      const response = await AIService.sendMessage(
        'test-conversation-id',
        'What is machine learning?',
        { topic: 'machine learning basics' }
      )

      expect(response.success).toBe(true)
      expect(response.ai_response).toContain('helpful AI tutor response')
      expect(response.metadata.conversation_id).toBe('test-conversation-id')
      expect(response.metadata.tokens_used).toBe(150)

      // Test retrieving conversation history
      const messages = await AIService.getConversationMessages('test-conversation-id')
      expect(messages).toHaveLength(2)
      expect(messages[0].role).toBe('user')
      expect(messages[1].role).toBe('assistant')

      // Verify API calls were made with correct parameters
      expect(mockedAxios.post).toHaveBeenCalledTimes(2)
      expect(mockedAxios.get).toHaveBeenCalledTimes(1)
      
      // Check conversation creation call
      expect(mockedAxios.post).toHaveBeenNthCalledWith(1, 
        '/ai/conversations/',
        expect.objectContaining({
          title: 'AI Learning Session',
          conversation_type: 'tutor'
        })
      )

      // Check message sending call
      expect(mockedAxios.post).toHaveBeenNthCalledWith(2,
        '/ai/conversations/test-conversation-id/send_message/',
        expect.objectContaining({
          message: 'What is machine learning?'
        })
      )
    })

    it('should handle AI service errors gracefully', async () => {
      // Mock API error
      mockedAxios.post.mockRejectedValueOnce(new Error('AI service unavailable'))

      try {
        await AIService.sendMessage('test-id', 'test message')
      } catch (error) {
        const errorMessage = AIService.handleAIError(error)
        expect(errorMessage).toContain('An unexpected error occurred')
      }
    })
  })

  describe('Content Summarization - Generation and Display (Requirement 6.2)', () => {
    it('should generate and display content summaries accurately', async () => {
      // Mock summary generation
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockAIResponses.summaryResponse)
      })

      const testContent = `
        Machine learning is a subset of artificial intelligence that focuses on algorithms
        that can learn and make decisions from data. There are three main types of machine
        learning: supervised learning, unsupervised learning, and reinforcement learning.
      `

      const response = await AIService.generateSummary({
        content: testContent,
        content_type: 'course_module',
        content_id: 'test-content-id',
        content_title: 'Introduction to Machine Learning Types',
        course_id: 'test-course-id'
      })

      expect(response.success).toBe(true)
      expect(response.summary).toContain('concise summary')
      expect(response.key_points).toHaveLength(3)
      expect(response.key_points[0]).toContain('Machine learning is a subset of AI')
      expect(response.metadata.summary_id).toBe('test-summary-id')
      expect(response.metadata.tokens_used).toBe(200)
      expect(response.metadata.generation_time_ms).toBe(1200)

      // Verify API call
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/ai/summaries/generate/'),
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json'
          }),
          body: expect.stringContaining('Introduction to Machine Learning Types')
        })
      )
    })

    it('should retrieve summaries list', async () => {
      // Mock summaries list
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve([
          {
            id: 'test-summary-id',
            content_title: 'Machine Learning Basics',
            summary: mockAIResponses.summaryResponse.summary,
            key_points: mockAIResponses.summaryResponse.key_points,
            created_at: new Date().toISOString()
          }
        ])
      })

      const summaries = await AIService.getSummaries()
      expect(summaries).toHaveLength(1)
      expect(summaries[0].content_title).toBe('Machine Learning Basics')
      expect(summaries[0].key_points).toHaveLength(3)
    })
  })

  describe('Quiz Generation and Submission Process (Requirement 6.3)', () => {
    it('should generate quiz questions from content', async () => {
      // Mock quiz generation
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockAIResponses.quizResponse)
      })

      const quizContent = `
        Artificial Intelligence is the simulation of human intelligence in machines.
        Machine learning enables computers to learn without explicit programming.
      `

      const response = await AIService.generateQuiz({
        content: quizContent,
        course_id: 'test-course-id',
        title: 'AI Fundamentals Quiz',
        num_questions: 1,
        difficulty: 'medium'
      })

      expect(response.success).toBe(true)
      expect(response.questions).toHaveLength(1)
      
      const question = response.questions[0]
      expect(question.question).toBe('What is machine learning?')
      expect(question.type).toBe('multiple_choice')
      expect(question.options).toHaveLength(4)
      expect(question.correct_answer).toBe(1)
      expect(question.explanation).toContain('subset of artificial intelligence')

      expect(response.metadata.quiz_id).toBe('test-quiz-id')
      expect(response.metadata.tokens_used).toBe(300)

      // Verify API call
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/ai/quizzes/generate/'),
        expect.objectContaining({
          method: 'POST',
          body: expect.stringContaining('AI Fundamentals Quiz')
        })
      )
    })

    it('should validate quiz generation parameters', async () => {
      // Test missing content
      try {
        await AIService.generateQuiz({
          content: '',
          course_id: 'test-course-id',
          title: 'Test Quiz',
          num_questions: 1,
          difficulty: 'medium'
        })
      } catch (error) {
        expect(error.message).toContain('content')
      }

      // Test invalid number of questions
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: () => Promise.resolve({
          error: 'Number of questions must be between 1 and 20'
        })
      })

      try {
        await AIService.generateQuiz({
          content: 'test content',
          course_id: 'test-course-id',
          title: 'Test Quiz',
          num_questions: 25, // Too many
          difficulty: 'medium'
        })
      } catch (error) {
        expect(error.message).toContain('between 1 and 20')
      }
    })
  })

  describe('Quota Enforcement and Rate Limiting Display (Requirement 6.5)', () => {
    it('should display usage statistics accurately', async () => {
      // Mock usage stats
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockAIResponses.usageStats)
      })

      const stats = await AIService.getUsageStats()
      
      expect(stats.success).toBe(true)
      expect(stats.stats.chat.messages_used).toBe(5)
      expect(stats.stats.chat.messages_limit).toBe(50)
      expect(stats.stats.chat.percentage_used).toBe(10.0)

      expect(stats.stats.summaries.summaries_used).toBe(2)
      expect(stats.stats.summaries.summaries_limit).toBe(20)
      expect(stats.stats.summaries.percentage_used).toBe(10.0)

      expect(stats.stats.quizzes.quizzes_used).toBe(1)
      expect(stats.stats.quizzes.quizzes_limit).toBe(5)
      expect(stats.stats.quizzes.percentage_used).toBe(20.0)

      // Verify API call
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/ai/usage/current_stats/'),
        expect.objectContaining({
          method: 'GET'
        })
      )
    })

    it('should handle quota exceeded errors', async () => {
      // Mock quota exceeded response
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 429,
        json: () => Promise.resolve({
          error: 'Chat message quota exceeded for this month',
          error_type: 'quota_exceeded'
        })
      })

      try {
        await AIService.sendMessage('test-id', 'test message')
      } catch (error) {
        const errorMessage = AIService.handleAIError(error)
        expect(errorMessage).toContain('quota exceeded')
        expect(errorMessage).toContain('upgrade your plan')
      }
    })

    it('should handle rate limit exceeded errors', async () => {
      // Mock rate limit exceeded response
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 429,
        json: () => Promise.resolve({
          error: 'Rate limit exceeded. Please try again later.',
          error_type: 'rate_limit_exceeded'
        })
      })

      try {
        await AIService.generateSummary({
          content: 'test content',
          content_type: 'text',
          content_id: 'test-id',
          content_title: 'Test',
          course_id: 'test-course-id'
        })
      } catch (error) {
        const errorMessage = AIService.handleAIError(error)
        expect(errorMessage).toContain('Too many requests')
        expect(errorMessage).toContain('try again later')
      }
    })

    it('should handle AI service errors', async () => {
      // Mock AI service error
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 503,
        json: () => Promise.resolve({
          error: 'AI service temporarily unavailable',
          error_type: 'ai_service_error'
        })
      })

      try {
        await AIService.generateQuiz({
          content: 'test content',
          course_id: 'test-course-id',
          title: 'Test Quiz',
          num_questions: 1,
          difficulty: 'medium'
        })
      } catch (error) {
        const errorMessage = AIService.handleAIError(error)
        expect(errorMessage).toContain('temporarily unavailable')
        expect(errorMessage).toContain('try again later')
      }
    })
  })

  describe('AI Composable Integration', () => {
    it('should provide reactive AI state management', () => {
      const { 
        conversations, 
        summaries, 
        quizzes, 
        usageStats, 
        isLoading, 
        error 
      } = useAI()

      // Test initial state
      expect(conversations.value).toEqual([])
      expect(summaries.value).toEqual([])
      expect(quizzes.value).toEqual([])
      expect(usageStats.value).toBeNull()
      expect(isLoading.value).toBe(false)
      expect(error.value).toBeNull()
    })
  })
})