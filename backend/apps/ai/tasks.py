import logging
from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from .services import AIServiceFactory, AIServiceError
from .models import AIUsageQuota, AIRateLimit

User = get_user_model()
logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def generate_content_summary_async(
    self, 
    user_id: str, 
    tenant_id: str, 
    content: str, 
    content_type: str,
    content_id: str,
    content_title: str,
    course_id: str = None
):
    """
    Asynchronous task for generating content summaries
    Useful for large content that might take time to process
    """
    try:
        # Get user
        user = User.objects.get(id=user_id)
        
        # Get tenant (you'll need to implement tenant retrieval)
        tenant = None
        if tenant_id:
            from apps.common.models import Tenant  # Adjust import as needed
            tenant = Tenant.objects.get(id=tenant_id)
        
        # Create AI service
        ai_service = AIServiceFactory.create_service(user, tenant)
        
        # Generate summary
        summary, key_points, metadata = ai_service.generate_content_summary(
            content, content_type, content_id, content_title, course_id
        )
        
        logger.info(f"Successfully generated summary for user {user_id}, content {content_id}")
        
        return {
            'success': True,
            'summary': summary,
            'key_points': key_points,
            'metadata': metadata
        }
        
    except Exception as e:
        logger.error(f"Failed to generate summary for user {user_id}: {str(e)}")
        
        # Retry with exponential backoff
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60 * (2 ** self.request.retries))
        
        return {
            'success': False,
            'error': str(e)
        }


@shared_task(bind=True, max_retries=3)
def generate_quiz_async(
    self,
    user_id: str,
    tenant_id: str,
    content: str,
    course_id: str,
    title: str,
    num_questions: int = 5,
    difficulty: str = 'medium'
):
    """
    Asynchronous task for generating quizzes
    Useful for complex content that requires more processing time
    """
    try:
        # Get user
        user = User.objects.get(id=user_id)
        
        # Get tenant
        tenant = None
        if tenant_id:
            from apps.common.models import Tenant  # Adjust import as needed
            tenant = Tenant.objects.get(id=tenant_id)
        
        # Create AI service
        ai_service = AIServiceFactory.create_service(user, tenant)
        
        # Generate quiz
        questions, metadata = ai_service.generate_quiz(
            content, course_id, title, num_questions, difficulty
        )
        
        logger.info(f"Successfully generated quiz for user {user_id}, course {course_id}")
        
        return {
            'success': True,
            'questions': questions,
            'metadata': metadata
        }
        
    except Exception as e:
        logger.error(f"Failed to generate quiz for user {user_id}: {str(e)}")
        
        # Retry with exponential backoff
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60 * (2 ** self.request.retries))
        
        return {
            'success': False,
            'error': str(e)
        }


@shared_task
def cleanup_old_conversations():
    """
    Cleanup old inactive AI conversations
    Run this task daily to maintain database performance
    """
    try:
        # Delete conversations older than 90 days with no activity
        cutoff_date = timezone.now() - timedelta(days=90)
        
        from .models import AIConversation
        old_conversations = AIConversation.objects.filter(
            last_activity__lt=cutoff_date,
            is_active=False
        )
        
        count = old_conversations.count()
        old_conversations.delete()
        
        logger.info(f"Cleaned up {count} old AI conversations")
        
        return {
            'success': True,
            'cleaned_conversations': count
        }
        
    except Exception as e:
        logger.error(f"Failed to cleanup old conversations: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


@shared_task
def reset_monthly_quotas():
    """
    Reset monthly AI usage quotas
    Run this task on the first day of each month
    """
    try:
        current_month = timezone.now().date().replace(day=1)
        
        # Create new quota records for all users who had quotas last month
        last_month = (current_month - timedelta(days=1)).replace(day=1)
        
        last_month_quotas = AIUsageQuota.objects.filter(month=last_month)
        
        new_quotas_created = 0
        for quota in last_month_quotas:
            # Check if quota for current month already exists
            if not AIUsageQuota.objects.filter(
                user=quota.user,
                tenant=quota.tenant,
                month=current_month
            ).exists():
                # Create new quota with same limits but reset usage
                AIUsageQuota.objects.create(
                    user=quota.user,
                    tenant=quota.tenant,
                    month=current_month,
                    chat_messages_limit=quota.chat_messages_limit,
                    chat_tokens_limit=quota.chat_tokens_limit,
                    summaries_limit=quota.summaries_limit,
                    summary_tokens_limit=quota.summary_tokens_limit,
                    quizzes_limit=quota.quizzes_limit,
                    quiz_tokens_limit=quota.quiz_tokens_limit,
                    cost_limit_usd=quota.cost_limit_usd
                )
                new_quotas_created += 1
        
        logger.info(f"Reset monthly quotas: created {new_quotas_created} new quota records")
        
        return {
            'success': True,
            'new_quotas_created': new_quotas_created
        }
        
    except Exception as e:
        logger.error(f"Failed to reset monthly quotas: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


@shared_task
def cleanup_rate_limits():
    """
    Cleanup and reset rate limit counters
    Run this task every hour to reset expired windows
    """
    try:
        now = timezone.now()
        
        # Reset rate limits that have expired windows
        rate_limits = AIRateLimit.objects.all()
        
        updated_count = 0
        for rate_limit in rate_limits:
            updated = False
            
            # Reset minute window if expired
            if (now - rate_limit.minute_window_start).total_seconds() >= 60:
                rate_limit.minute_window_start = now
                rate_limit.minute_requests = 0
                updated = True
            
            # Reset hour window if expired
            if (now - rate_limit.hour_window_start).total_seconds() >= 3600:
                rate_limit.hour_window_start = now
                rate_limit.hour_requests = 0
                updated = True
            
            # Reset day window if expired
            if (now - rate_limit.day_window_start).total_seconds() >= 86400:
                rate_limit.day_window_start = now
                rate_limit.day_requests = 0
                updated = True
            
            if updated:
                rate_limit.save()
                updated_count += 1
        
        logger.info(f"Cleaned up {updated_count} rate limit records")
        
        return {
            'success': True,
            'updated_rate_limits': updated_count
        }
        
    except Exception as e:
        logger.error(f"Failed to cleanup rate limits: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


@shared_task
def generate_usage_reports():
    """
    Generate monthly usage reports for administrators
    Run this task at the end of each month
    """
    try:
        current_month = timezone.now().date().replace(day=1)
        last_month = (current_month - timedelta(days=1)).replace(day=1)
        
        # Get usage statistics for last month
        last_month_quotas = AIUsageQuota.objects.filter(month=last_month)
        
        total_users = last_month_quotas.count()
        total_chat_messages = sum(q.chat_messages_used for q in last_month_quotas)
        total_summaries = sum(q.summaries_generated for q in last_month_quotas)
        total_quizzes = sum(q.quizzes_generated for q in last_month_quotas)
        total_cost = sum(q.total_cost_usd for q in last_month_quotas)
        
        # Calculate averages
        avg_chat_messages = total_chat_messages / total_users if total_users > 0 else 0
        avg_summaries = total_summaries / total_users if total_users > 0 else 0
        avg_quizzes = total_quizzes / total_users if total_users > 0 else 0
        avg_cost = total_cost / total_users if total_users > 0 else 0
        
        report = {
            'month': last_month.strftime('%Y-%m'),
            'total_users': total_users,
            'total_chat_messages': total_chat_messages,
            'total_summaries': total_summaries,
            'total_quizzes': total_quizzes,
            'total_cost_usd': float(total_cost),
            'averages': {
                'chat_messages_per_user': avg_chat_messages,
                'summaries_per_user': avg_summaries,
                'quizzes_per_user': avg_quizzes,
                'cost_per_user_usd': float(avg_cost)
            }
        }
        
        logger.info(f"Generated usage report for {last_month.strftime('%Y-%m')}: {report}")
        
        # Here you could save the report to database or send via email
        # For now, just log it
        
        return {
            'success': True,
            'report': report
        }
        
    except Exception as e:
        logger.error(f"Failed to generate usage reports: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }