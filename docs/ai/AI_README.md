# AI Services Module

This module provides AI-powered learning features for the Edurise LMS platform using Google's Gemini API.

## Features

### 1. AI Tutor Chat
- Contextual chat assistance with conversation history
- Course-aware responses based on learning context
- Real-time conversation management

### 2. Content Summarization
- AI-generated summaries of recorded sessions
- Key points extraction from course content
- Support for multiple content types (live_class, course_module, video, text)

### 3. Quiz Generation
- Automatic quiz creation from course content
- Multiple difficulty levels (easy, medium, hard)
- Configurable number of questions (1-20)
- Structured multiple-choice format with explanations

### 4. Usage Quota Management
- Monthly usage limits based on subscription plans
- Token-based cost tracking
- Separate quotas for chat, summaries, and quizzes

### 5. Rate Limiting
- Per-minute, per-hour, and per-day request limits
- Automatic rate limit enforcement
- Configurable limits per user

## API Endpoints

### Conversations
- `GET /api/v1/ai/conversations/` - List user's conversations
- `POST /api/v1/ai/conversations/` - Create new conversation
- `POST /api/v1/ai/conversations/{id}/send_message/` - Send message to AI tutor
- `GET /api/v1/ai/conversations/{id}/messages/` - Get conversation messages

### Content Summaries
- `GET /api/v1/ai/summaries/` - List user's summaries
- `POST /api/v1/ai/summaries/generate/` - Generate content summary

### Quizzes
- `GET /api/v1/ai/quizzes/` - List user's quizzes
- `POST /api/v1/ai/quizzes/generate/` - Generate quiz from content

### Usage Statistics
- `GET /api/v1/ai/usage/` - List usage quotas
- `GET /api/v1/ai/usage/current_stats/` - Get current month statistics

## Models

### AIConversation
Stores AI chat conversations with context and metadata.

### AIMessage
Individual messages within conversations with token usage tracking.

### AIContentSummary
AI-generated summaries with key points extraction.

### AIQuiz
AI-generated quizzes with structured question format.

### AIUsageQuota
Monthly usage tracking and quota enforcement.

### AIRateLimit
Rate limiting configuration and tracking per user.

## Services

### AIService
Main service class that orchestrates all AI functionality:
- `chat_with_tutor()` - Handle AI chat interactions
- `generate_content_summary()` - Create content summaries
- `generate_quiz()` - Generate quizzes from content
- `get_usage_stats()` - Retrieve usage statistics

### GeminiProvider
Gemini API integration with:
- Response generation for chat
- Content summarization
- Quiz question generation
- Token estimation and cost calculation

## Configuration

### Environment Variables
```bash
GEMINI_API_KEY=your-gemini-api-key-here
```

### Subscription Plan Limits
- **Basic**: 50 chat messages, 10 summaries, 5 quizzes per month
- **Pro**: 200 chat messages, 50 summaries, 25 quizzes per month
- **Enterprise**: 1000 chat messages, 200 summaries, 100 quizzes per month

## Usage Examples

### Chat with AI Tutor
```python
from apps.ai.services import AIServiceFactory

# Create AI service for user
ai_service = AIServiceFactory.create_service(user, tenant)

# Send message to AI tutor
response, metadata = ai_service.chat_with_tutor(
    conversation_id='uuid-here',
    message='Explain machine learning basics',
    context={'course_id': 'course-uuid'}
)
```

### Generate Content Summary
```python
summary, key_points, metadata = ai_service.generate_content_summary(
    content='Your content here...',
    content_type='live_class',
    content_id='content-uuid',
    content_title='Introduction to Python',
    course_id='course-uuid'
)
```

### Generate Quiz
```python
questions, metadata = ai_service.generate_quiz(
    content='Course content here...',
    course_id='course-uuid',
    title='Python Basics Quiz',
    num_questions=5,
    difficulty='medium'
)
```

## Testing

Run the AI services tests:
```bash
python manage.py test apps.ai.tests
```

Test AI services functionality:
```bash
python manage.py test_ai_services --test-all
```

## Celery Tasks

### Background Processing
- `generate_content_summary_async` - Async summary generation
- `generate_quiz_async` - Async quiz generation

### Maintenance Tasks
- `cleanup_old_conversations` - Remove inactive conversations (daily)
- `reset_monthly_quotas` - Reset usage quotas (monthly)
- `cleanup_rate_limits` - Reset expired rate limits (hourly)
- `generate_usage_reports` - Generate usage reports (monthly)

## Error Handling

### Custom Exceptions
- `AIServiceError` - General AI service errors
- `QuotaExceededError` - Usage quota exceeded
- `RateLimitExceededError` - Rate limit exceeded

### API Error Responses
```json
{
  "error": "Error message",
  "error_type": "quota_exceeded|rate_limit_exceeded|ai_service_error|internal_error"
}
```

## Security Considerations

- All AI requests are authenticated and tenant-aware
- Usage quotas prevent API abuse
- Rate limiting protects against excessive requests
- Cost tracking prevents unexpected charges
- Input validation and sanitization

## Performance Optimization

- Response caching for summaries
- Async processing for heavy operations
- Database query optimization
- Token usage estimation for cost control

## Monitoring

- Usage statistics tracking
- Cost monitoring and alerts
- Performance metrics collection
- Error logging and reporting