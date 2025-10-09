from celery import shared_task
from .providers import GeminiProvider
from .models import AIUsageQuota
from apps.courses.models import CourseModule
from django.contrib.auth import get_user_model

User = get_user_model()


@shared_task
def generate_content_summary(module_id, user_id):
    """Generate summary for course module content"""
    try:
        module = CourseModule.objects.get(id=module_id)
        user = User.objects.get(id=user_id)
        
        # Check usage quota
        quota = AIUsageQuota.objects.get_or_create(
            user=user,
            month=timezone.now().date().replace(day=1),
            tenant=module.course.tenant
        )[0]
        
        if quota.summaries_generated >= quota.summaries_limit:
            return {'error': 'Summary generation quota exceeded'}
        
        # Generate summary
        provider = GeminiProvider()
        summary = provider.generate_summary(module.content)
        
        # Update usage
        quota.summaries_generated += 1
        quota.save()
        
        # Save summary to module (you might want a separate Summary model)
        module.ai_summary = summary
        module.save()
        
        return {'success': True, 'summary': summary}
        
    except Exception as e:
        return {'error': str(e)}


@shared_task
def generate_quiz_questions(module_id, user_id, num_questions=5):
    """Generate quiz questions for course module"""
    try:
        module = CourseModule.objects.get(id=module_id)
        user = User.objects.get(id=user_id)
        
        # Check usage quota
        quota = AIUsageQuota.objects.get_or_create(
            user=user,
            month=timezone.now().date().replace(day=1),
            tenant=module.course.tenant
        )[0]
        
        if quota.quizzes_generated >= quota.quizzes_limit:
            return {'error': 'Quiz generation quota exceeded'}
        
        # Generate quiz
        provider = GeminiProvider()
        quiz_data = provider.generate_quiz(module.content, num_questions)
        
        # Update usage
        quota.quizzes_generated += 1
        quota.save()
        
        return {'success': True, 'quiz': quiz_data}
        
    except Exception as e:
        return {'error': str(e)}