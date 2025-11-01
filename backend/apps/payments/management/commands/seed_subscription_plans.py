from decimal import Decimal
from django.core.management.base import BaseCommand
from apps.payments.models import SubscriptionPlan


class Command(BaseCommand):
    help = 'Seed default subscription plans'

    def handle(self, *args, **options):
        """Create default subscription plans"""
        
        plans_data = [
            {
                'name': 'basic',
                'display_name': 'Basic Plan',
                'description': 'Perfect for small teams and individual educators getting started with online learning.',
                'price_monthly': Decimal('29.00'),
                'price_yearly': Decimal('290.00'),  # 2 months free
                'max_users': 25,
                'max_courses': 10,
                'max_storage_gb': 50,
                'ai_quota_monthly': 500,
                'has_analytics': False,
                'has_api_access': False,
                'has_white_labeling': False,
                'has_priority_support': False,
                'has_custom_integrations': False,
                'max_file_size_mb': 100,
                'monthly_download_limit': 1000,
                'recording_access': True,
                'premium_content_access': False,
                'is_popular': False,
                'sort_order': 1,
                'features': {
                    'live_classes': True,
                    'assignments': True,
                    'certificates': True,
                    'basic_reporting': True,
                    'email_support': True,
                    'mobile_app': True,
                }
            },
            {
                'name': 'pro',
                'display_name': 'Pro Plan',
                'description': 'Advanced features for growing organizations and professional educators.',
                'price_monthly': Decimal('79.00'),
                'price_yearly': Decimal('790.00'),  # 2 months free
                'max_users': 100,
                'max_courses': 50,
                'max_storage_gb': 200,
                'ai_quota_monthly': 2000,
                'has_analytics': True,
                'has_api_access': True,
                'has_white_labeling': False,
                'has_priority_support': True,
                'has_custom_integrations': False,
                'max_file_size_mb': 500,
                'monthly_download_limit': 5000,
                'recording_access': True,
                'premium_content_access': True,
                'is_popular': True,  # Most popular plan
                'sort_order': 2,
                'features': {
                    'live_classes': True,
                    'assignments': True,
                    'certificates': True,
                    'advanced_reporting': True,
                    'priority_support': True,
                    'mobile_app': True,
                    'custom_branding': True,
                    'advanced_ai_features': True,
                    'bulk_user_management': True,
                    'course_marketplace': True,
                }
            },
            {
                'name': 'enterprise',
                'display_name': 'Enterprise Plan',
                'description': 'Complete solution for large organizations with advanced security and customization needs.',
                'price_monthly': Decimal('199.00'),
                'price_yearly': Decimal('1990.00'),  # 2 months free
                'max_users': 1000,
                'max_courses': 500,
                'max_storage_gb': 1000,
                'ai_quota_monthly': 10000,
                'has_analytics': True,
                'has_api_access': True,
                'has_white_labeling': True,
                'has_priority_support': True,
                'has_custom_integrations': True,
                'max_file_size_mb': 2000,
                'monthly_download_limit': None,  # Unlimited
                'recording_access': True,
                'premium_content_access': True,
                'is_popular': False,
                'sort_order': 3,
                'features': {
                    'live_classes': True,
                    'assignments': True,
                    'certificates': True,
                    'enterprise_reporting': True,
                    'dedicated_support': True,
                    'mobile_app': True,
                    'full_white_labeling': True,
                    'advanced_ai_features': True,
                    'bulk_user_management': True,
                    'course_marketplace': True,
                    'sso_integration': True,
                    'advanced_security': True,
                    'custom_integrations': True,
                    'dedicated_account_manager': True,
                    'custom_development': True,
                }
            }
        ]

        for plan_data in plans_data:
            plan, created = SubscriptionPlan.objects.get_or_create(
                name=plan_data['name'],
                defaults=plan_data
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created subscription plan: {plan.display_name}')
                )
            else:
                # Update existing plan with new data
                for key, value in plan_data.items():
                    setattr(plan, key, value)
                plan.save()
                self.stdout.write(
                    self.style.WARNING(f'Updated subscription plan: {plan.display_name}')
                )

        self.stdout.write(
            self.style.SUCCESS('Successfully seeded subscription plans!')
        )