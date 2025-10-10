/**
 * Simplified Integration tests for AI features frontend functionality
 * Tests AI tutor chat, content summarization, quiz generation, and quota display
 * Requirements: 6.1, 6.2, 6.3, 6.5
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import axios from 'axios'

// Mock axios
vi.mock('axios')
const mockedAxios = vi.mocked(axios)

// Mock API responses
const mockResponses = {
    conversation: {
        id: 'test-conversation-id',
        title: 'AI Learning Session',
        conversation_type: 'tutor',
        created_at: new Date().toISOString()
    },
    chatMessage: {
        success: true,
        ai_response: 'This is a helpful AI tutor response about machine learning concepts.',
        metadata: {
            conversation_id: 'test-conversation-id',
            tokens_used: 150,
            response_time_ms: 800,
            remaining_quota: 45
        }
    },
    summary: {
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
    quiz: {
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
    beforeEach(() => {
        vi.clearAllMocks()

        // Setup axios mock
        mockedAxios.create = vi.fn(() => mockedAxios)
        mockedAxios.interceptors = {
            request: { use: vi.fn() },
            response: { use: vi.fn() }
        }
    })

    describe('AI Tutor Chat - Context Retention and Conversation Flow (Requirement 6.1)', () => {
        it('should create conversation and send messages', async () => {
            // Mock axios responses
            mockedAxios.post
                .mockResolvedValueOnce({ data: mockResponses.conversation })
                .mockResolvedValueOnce({ data: mockResponses.chatMessage })

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
                        content: mockResponses.chatMessage.ai_response,
                        created_at: new Date().toISOString()
                    }
                ]
            })

            // Import AIService after mocking
            const { AIService } = await import('@/services/ai')

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

            // Test sending message
            const response = await AIService.sendMessage(
                'test-conversation-id',
                'What is machine learning?',
                { topic: 'machine learning basics' }
            )

            expect(response.success).toBe(true)
            expect(response.ai_response).toContain('helpful AI tutor response')
            expect(response.metadata.tokens_used).toBe(150)

            // Test retrieving messages
            const messages = await AIService.getConversationMessages('test-conversation-id')
            expect(messages).toHaveLength(2)
            expect(messages[0].role).toBe('user')
            expect(messages[1].role).toBe('assistant')

            // Verify API calls
            expect(mockedAxios.post).toHaveBeenCalledTimes(2)
            expect(mockedAxios.get).toHaveBeenCalledTimes(1)
        })

        it('should handle errors gracefully', async () => {
            // Mock error response
            mockedAxios.post.mockRejectedValueOnce(new Error('Network error'))

            const { AIService } = await import('@/services/ai')

            try {
                await AIService.sendMessage('test-id', 'test message')
            } catch (error) {
                const errorMessage = AIService.handleAIError(error)
                expect(errorMessage).toContain('Network error')
            }
        })
    })

    describe('Content Summarization - Generation and Display (Requirement 6.2)', () => {
        it('should generate content summaries', async () => {
            // Mock summary response
            mockedAxios.post.mockResolvedValueOnce({ data: mockResponses.summary })

            const { AIService } = await import('@/services/ai')

            const response = await AIService.generateSummary({
                content: 'Machine learning is a subset of artificial intelligence...',
                content_type: 'course_module',
                content_id: 'test-content-id',
                content_title: 'Introduction to Machine Learning Types',
                course_id: 'test-course-id'
            })

            expect(response.success).toBe(true)
            expect(response.summary).toContain('concise summary')
            expect(response.key_points).toHaveLength(3)
            expect(response.key_points[0]).toContain('Machine learning is a subset of AI')
            expect(response.metadata.tokens_used).toBe(200)

            // Verify API call
            expect(mockedAxios.post).toHaveBeenCalledWith(
                '/ai/summaries/generate/',
                expect.objectContaining({
                    content_title: 'Introduction to Machine Learning Types'
                }),
                undefined
            )
        })

        it('should retrieve summaries list', async () => {
            // Mock summaries list
            mockedAxios.get.mockResolvedValueOnce({
                data: [
                    {
                        id: 'test-summary-id',
                        content_title: 'Machine Learning Basics',
                        summary: mockResponses.summary.summary,
                        key_points: mockResponses.summary.key_points,
                        created_at: new Date().toISOString()
                    }
                ]
            })

            const { AIService } = await import('@/services/ai')

            const summaries = await AIService.getSummaries()
            expect(summaries).toHaveLength(1)
            expect(summaries[0].content_title).toBe('Machine Learning Basics')
            expect(summaries[0].key_points).toHaveLength(3)
        })
    })

    describe('Quiz Generation and Submission Process (Requirement 6.3)', () => {
        it('should generate quiz questions from content', async () => {
            // Mock quiz response
            mockedAxios.post.mockResolvedValueOnce({ data: mockResponses.quiz })

            const { AIService } = await import('@/services/ai')

            const response = await AIService.generateQuiz({
                content: 'Artificial Intelligence is the simulation of human intelligence...',
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

            expect(response.metadata.tokens_used).toBe(300)

            // Verify API call
            expect(mockedAxios.post).toHaveBeenCalledWith(
                '/ai/quizzes/generate/',
                expect.objectContaining({
                    title: 'AI Fundamentals Quiz'
                }),
                undefined
            )
        })

        it('should handle validation errors', async () => {
            // Mock validation error
            mockedAxios.post.mockRejectedValueOnce({
                response: {
                    status: 400,
                    data: {
                        error: 'Number of questions must be between 1 and 20'
                    }
                }
            })

            const { AIService } = await import('@/services/ai')

            try {
                await AIService.generateQuiz({
                    content: 'test content',
                    course_id: 'test-course-id',
                    title: 'Test Quiz',
                    num_questions: 25, // Too many
                    difficulty: 'medium'
                })
            } catch (error) {
                const errorMessage = AIService.handleAIError(error)
                expect(errorMessage).toContain('An unexpected error occurred')
            }
        })
    })

    describe('Quota Enforcement and Rate Limiting Display (Requirement 6.5)', () => {
        it('should display usage statistics accurately', async () => {
            // Mock usage stats
            mockedAxios.get.mockResolvedValueOnce({ data: mockResponses.usageStats })

            const { AIService } = await import('@/services/ai')

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
            expect(mockedAxios.get).toHaveBeenCalledWith('/ai/usage/current_stats/', undefined)
        })

        it('should handle quota exceeded errors', async () => {
            // Mock quota exceeded response
            mockedAxios.post.mockRejectedValueOnce({
                response: {
                    status: 429,
                    data: {
                        error: 'Chat message quota exceeded for this month',
                        error_type: 'quota_exceeded'
                    }
                }
            })

            const { AIService } = await import('@/services/ai')

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
            mockedAxios.post.mockRejectedValueOnce({
                response: {
                    status: 429,
                    data: {
                        error: 'Rate limit exceeded. Please try again later.',
                        error_type: 'rate_limit_exceeded'
                    }
                }
            })

            const { AIService } = await import('@/services/ai')

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
                expect(errorMessage).toContain('trying again')
            }
        })

        it('should handle AI service errors', async () => {
            // Mock AI service error
            mockedAxios.post.mockRejectedValueOnce({
                response: {
                    status: 503,
                    data: {
                        error: 'AI service temporarily unavailable',
                        error_type: 'ai_service_error'
                    }
                }
            })

            const { AIService } = await import('@/services/ai')

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
})