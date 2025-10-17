# Data migration to populate subscription plans

from django.db import migrations
from decimal import Decimal


def create_subscription_plans(apps, schema_editor):
    SubscriptionPlan = apps.get_model('payments', 'SubscriptionPlan')
    
    plans = [
        {
            'name': 'basic',
            'display_name': 'Basic Plan',
            'description': 'Perfect for small teams getting started with online learning',
            'price_monthly': Decimal('29.00'),
            'price_yearly': Decimal('290.00'),
            'max_users': 10,
            'max_courses': 5,
            'max_storage_gb': 10,
            'ai_quota_monthly': 100,
            'has_analytics': False,
            'has_api_access': False,
            'has_white_labeling': False,
            'has_priority_support': False,
            'has_custom_integrations': False,
            'is_popular': False,
            'sort_order': 1,
        },
        {
            'name': 'pro',
            'display_name': 'Pro Plan',
            'description': 'Ideal for growing organizations with advanced learning needs',
            'price_monthly': Decimal('99.00'),
            'price_yearly': Decimal('990.00'),
            'max_users': 100,
            'max_courses': 50,
            'max_storage_gb': 100,
            'ai_quota_monthly': 1000,
            'has_analytics': True,
            'has_api_access': True,
            'has_white_labeling': False,
            'has_priority_support': True,
            'has_custom_integrations': False,
            'is_popular': True,
            'sort_order': 2,
        },
        {
            'name': 'enterprise',
            'display_name': 'Enterprise Plan',
            'description': 'Complete solution for large organizations with custom requirements',
            'price_monthly': Decimal('299.00'),
            'price_yearly': Decimal('2990.00'),
            'max_users': 1000,
            'max_courses': 500,
            'max_storage_gb': 1000,
            'ai_quota_monthly': 10000,
            'has_analytics': True,
            'has_api_access': True,
            'has_white_labeling': True,
            'has_priority_support': True,
            'has_custom_integrations': True,
            'is_popular': False,
            'sort_order': 3,
        },
    ]
    
    for plan_data in plans:
        SubscriptionPlan.objects.get_or_create(
            name=plan_data['name'],
            defaults=plan_data
        )


def reverse_create_subscription_plans(apps, schema_editor):
    SubscriptionPlan = apps.get_model('payments', 'SubscriptionPlan')
    SubscriptionPlan.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0002_add_subscription_plans'),
    ]

    operations = [
        migrations.RunPython(
            create_subscription_plans,
            reverse_create_subscription_plans
        ),
    ]