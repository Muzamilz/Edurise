import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings

from apps.ai.services import AIServiceFactory, QuotaExceededError, RateLimitExceededError, AIServiceError
from apps.courses.models import Course

User = get_user_model()


class Command(BaseCommand):
    help = 'Test AI services functionality'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-email',
            type=str,
            help='Email of user to test with',
            default='test@example.com'
        )
        parser.add_argument(
            '--test-chat',
            action='store_true',
            help='Test AI chat functionality'
        )
        parser.add_argument(
            '--test-summary',
            action='store_true',
            help='Test content summarization'
        )
        parser.add_argument(
            '--test-quiz',
            action='store_true',
            help='Test quiz generation'
        )
        parser.add_argument(
            '--test-all',
            action='store_true',
            help='Test all AI services'
        )

    def handle(self, *args, **options):
        # Check if Gemini API key is configured
        if not settings.GEMINI_API_KEY:
            self.stdout.write(
                self.style.ERROR('GEMINI_API_KEY not configured in settings')
            )
            return

        # Get or create test user
        user_email = options['user_email']
        try:
            user = User.objects.get(email=user_email)
            self.stdout.write(f'Using existing user: {user_email}')
        except User.DoesNotExist:
            user = User.objects.create_user(
                email=user_email,
                password='testpassword123',
                first_name='Test',
                last_name='User'
            )
            self.stdout.write(f'Created test user: {user_email}')

        # Create AI service
        ai_service = AIServiceFactory.create_service(user, tenant=None)

        # Run tests based on options
        if options['test_all'] or options['test_chat']:
            self.test_chat_functionality(ai_service)

        if options['test_all'] or options['test_summary']:
            self.test_summary_functionality(ai_service)

        if options['test_all'] or options['test_quiz']:
            self.test_quiz_functionality(ai_service)

        # Show usage stats
        self.show_usage_stats(ai_service)

    def test_chat_functionality(self, ai_service):
        """Test AI chat functionality"""
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('Testing AI Chat Functionality'))
        self.stdout.write('='*50)

        try:
            # Test basic chat
            conversation_id = 'test-conversation-123'
            message = "Hello! Can you help me understand machine learning basics?"
            
            self.stdout.write(f'Sending message: "{message}"')
            
            ai_response, metadata = ai_service.chat_with_tutor(
                conversation_id, message
            )
            
            self.stdout.write(self.style.SUCCESS('✓ Chat response received'))
            self.stdout.write(f'Response: {ai_response[:200]}...')
            self.stdout.write(f'Tokens used: {metadata["tokens_used"]}')
            self.stdout.write(f'Response time: {metadata["response_time_ms"]}ms')
            
            # Test follow-up message
            follow_up = "Can you give me a simple example?"
            self.stdout.write(f'\nSending follow-up: "{follow_up}"')
            
            ai_response2, metadata2 = ai_service.chat_with_tutor(
                conversation_id, follow_up
            )
            
            self.stdout.write(self.style.SUCCESS('✓ Follow-up response received'))
            self.stdout.write(f'Response: {ai_response2[:200]}...')
            
        except QuotaExceededError as e:
            self.stdout.write(self.style.WARNING(f'⚠ Quota exceeded: {e}'))
        except RateLimitExceededError as e:
            self.stdout.write(self.style.WARNING(f'⚠ Rate limit exceeded: {e}'))
        except AIServiceError as e:
            self.stdout.write(self.style.ERROR(f'✗ AI service error: {e}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Unexpected error: {e}'))

    def test_summary_functionality(self, ai_service):
        """Test content summarization"""
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('Testing Content Summarization'))
        self.stdout.write('='*50)

        try:
            # Sample content to summarize
            content = """
            Machine learning is a subset of artificial intelligence that focuses on the development 
            of algorithms and statistical models that enable computers to improve their performance 
            on a specific task through experience. The core idea is that machines can learn from 
            data without being explicitly programmed for every scenario.
            
            There are three main types of machine learning: supervised learning, unsupervised learning, 
            and reinforcement learning. Supervised learning uses labeled data to train models, 
            unsupervised learning finds patterns in unlabeled data, and reinforcement learning 
            learns through interaction with an environment.
            
            Common applications include image recognition, natural language processing, recommendation 
            systems, and predictive analytics. Popular algorithms include linear regression, 
            decision trees, neural networks, and support vector machines.
            """
            
            self.stdout.write('Generating summary for sample content...')
            
            summary, key_points, metadata = ai_service.generate_content_summary(
                content=content,
                content_type='text',
                content_id='test-content-123',
                content_title='Introduction to Machine Learning'
            )
            
            self.stdout.write(self.style.SUCCESS('✓ Summary generated'))
            self.stdout.write(f'Summary: {summary}')
            self.stdout.write(f'Key Points: {", ".join(key_points)}')
            self.stdout.write(f'Tokens used: {metadata["tokens_used"]}')
            self.stdout.write(f'Generation time: {metadata["generation_time_ms"]}ms')
            
        except QuotaExceededError as e:
            self.stdout.write(self.style.WARNING(f'⚠ Quota exceeded: {e}'))
        except RateLimitExceededError as e:
            self.stdout.write(self.style.WARNING(f'⚠ Rate limit exceeded: {e}'))
        except AIServiceError as e:
            self.stdout.write(self.style.ERROR(f'✗ AI service error: {e}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Unexpected error: {e}'))

    def test_quiz_functionality(self, ai_service):
        """Test quiz generation"""
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('Testing Quiz Generation'))
        self.stdout.write('='*50)

        try:
            # Get or create a test course
            course = self.get_or_create_test_course()
            
            # Sample content for quiz generation
            content = """
            Python is a high-level, interpreted programming language known for its simplicity 
            and readability. It was created by Guido van Rossum and first released in 1991.
            
            Key features of Python include:
            - Dynamic typing: Variables don't need explicit type declarations
            - Interpreted execution: Code is executed line by line
            - Object-oriented programming: Supports classes and objects
            - Extensive standard library: Includes modules for many common tasks
            - Cross-platform compatibility: Runs on Windows, macOS, and Linux
            
            Python is widely used in web development, data science, artificial intelligence, 
            automation, and scientific computing. Popular frameworks include Django for web 
            development and pandas for data analysis.
            """
            
            self.stdout.write('Generating quiz from sample content...')
            
            questions, metadata = ai_service.generate_quiz(
                content=content,
                course_id=str(course.id),
                title='Python Basics Quiz',
                num_questions=3,
                difficulty='medium'
            )
            
            self.stdout.write(self.style.SUCCESS('✓ Quiz generated'))
            self.stdout.write(f'Number of questions: {len(questions)}')
            self.stdout.write(f'Tokens used: {metadata["tokens_used"]}')
            self.stdout.write(f'Generation time: {metadata["generation_time_ms"]}ms')
            
            # Display questions
            for i, question in enumerate(questions, 1):
                self.stdout.write(f'\nQuestion {i}: {question["question"]}')
                for j, option in enumerate(question["options"]):
                    marker = "✓" if j == question["correct_answer"] else " "
                    self.stdout.write(f'  {marker} {chr(65+j)}. {option}')
                self.stdout.write(f'  Explanation: {question["explanation"]}')
            
        except QuotaExceededError as e:
            self.stdout.write(self.style.WARNING(f'⚠ Quota exceeded: {e}'))
        except RateLimitExceededError as e:
            self.stdout.write(self.style.WARNING(f'⚠ Rate limit exceeded: {e}'))
        except AIServiceError as e:
            self.stdout.write(self.style.ERROR(f'✗ AI service error: {e}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Unexpected error: {e}'))

    def get_or_create_test_course(self):
        """Get or create a test course"""
        try:
            course = Course.objects.get(title='Test Course for AI')
        except Course.DoesNotExist:
            # Get a user to be the instructor
            instructor = User.objects.first()
            if not instructor:
                instructor = User.objects.create_user(
                    email='instructor@example.com',
                    password='testpassword123',
                    first_name='Test',
                    last_name='Instructor'
                )
            
            course = Course.objects.create(
                title='Test Course for AI',
                description='A test course for AI functionality testing',
                instructor=instructor,
                is_public=True,
                price=0.00
            )
        
        return course

    def show_usage_stats(self, ai_service):
        """Show current usage statistics"""
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('Current Usage Statistics'))
        self.stdout.write('='*50)

        try:
            stats = ai_service.get_usage_stats()
            
            self.stdout.write(f'Month: {stats["month"]}')
            self.stdout.write('\nChat Usage:')
            self.stdout.write(f'  Messages: {stats["chat"]["messages_used"]}/{stats["chat"]["messages_limit"]} ({stats["chat"]["percentage_used"]:.1f}%)')
            self.stdout.write(f'  Tokens: {stats["chat"]["tokens_used"]}/{stats["chat"]["tokens_limit"]}')
            
            self.stdout.write('\nSummary Usage:')
            self.stdout.write(f'  Summaries: {stats["summaries"]["summaries_used"]}/{stats["summaries"]["summaries_limit"]} ({stats["summaries"]["percentage_used"]:.1f}%)')
            self.stdout.write(f'  Tokens: {stats["summaries"]["tokens_used"]}/{stats["summaries"]["tokens_limit"]}')
            
            self.stdout.write('\nQuiz Usage:')
            self.stdout.write(f'  Quizzes: {stats["quizzes"]["quizzes_used"]}/{stats["quizzes"]["quizzes_limit"]} ({stats["quizzes"]["percentage_used"]:.1f}%)')
            self.stdout.write(f'  Tokens: {stats["quizzes"]["tokens_used"]}/{stats["quizzes"]["tokens_limit"]}')
            
            self.stdout.write('\nCost:')
            self.stdout.write(f'  Total: ${stats["cost"]["total_cost_usd"]:.4f}/${stats["cost"]["cost_limit_usd"]:.2f} ({stats["cost"]["percentage_used"]:.1f}%)')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Error getting usage stats: {e}'))