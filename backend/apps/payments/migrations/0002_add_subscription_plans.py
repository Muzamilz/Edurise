# Generated migration for SubscriptionPlan model

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubscriptionPlan',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(choices=[('basic', 'Basic'), ('pro', 'Pro'), ('enterprise', 'Enterprise')], max_length=20, unique=True)),
                ('display_name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('price_monthly', models.DecimalField(decimal_places=2, max_digits=10)),
                ('price_yearly', models.DecimalField(decimal_places=2, max_digits=10)),
                ('max_users', models.IntegerField(default=10)),
                ('max_courses', models.IntegerField(default=5)),
                ('max_storage_gb', models.IntegerField(default=10)),
                ('ai_quota_monthly', models.IntegerField(default=100)),
                ('has_analytics', models.BooleanField(default=False)),
                ('has_api_access', models.BooleanField(default=False)),
                ('has_white_labeling', models.BooleanField(default=False)),
                ('has_priority_support', models.BooleanField(default=False)),
                ('has_custom_integrations', models.BooleanField(default=False)),
                ('is_popular', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('sort_order', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'subscription_plans',
                'ordering': ['sort_order', 'price_monthly'],
            },
        ),
    ]