import uuid
from decimal import Decimal
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.common.models import TenantAwareModel

User = get_user_model()


class Payment(TenantAwareModel):
    """Payment transactions for courses and subscriptions"""
    
    PAYMENT_METHOD_CHOICES = [
        ('stripe', 'Stripe'),
        ('paypal', 'PayPal'),
        ('bank_transfer', 'Bank Transfer'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_TYPE_CHOICES = [
        ('course', 'Course Payment'),
        ('subscription', 'Subscription Payment'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    
    # Payment can be for course or subscription
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES, default='course')
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    subscription = models.ForeignKey('Subscription', on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # External payment IDs
    stripe_payment_intent_id = models.CharField(max_length=100, blank=True)
    stripe_subscription_id = models.CharField(max_length=100, blank=True)
    paypal_order_id = models.CharField(max_length=100, blank=True)
    
    # Bank transfer details
    bank_transfer_reference = models.CharField(max_length=100, blank=True)
    bank_transfer_approved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='approved_bank_transfers'
    )
    
    # Additional metadata
    description = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'status']),
            models.Index(fields=['user', 'payment_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.amount} {self.currency} ({self.status})"
    
    def mark_completed(self):
        """Mark payment as completed"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()
    
    def mark_failed(self, reason=None):
        """Mark payment as failed"""
        self.status = 'failed'
        self.failed_at = timezone.now()
        if reason:
            self.metadata['failure_reason'] = reason
        self.save()


class SubscriptionPlan(models.Model):
    """Subscription plan definitions with feature limits"""
    
    PLAN_CHOICES = [
        ('basic', 'Basic'),
        ('pro', 'Pro'),
        ('enterprise', 'Enterprise'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=20, choices=PLAN_CHOICES, unique=True)
    display_name = models.CharField(max_length=100)
    description = models.TextField()
    
    # Pricing
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2)
    price_yearly = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Feature limits
    max_users = models.IntegerField(default=10)
    max_courses = models.IntegerField(default=5)
    max_storage_gb = models.IntegerField(default=10)
    ai_quota_monthly = models.IntegerField(default=100)  # AI requests per month
    
    # Features
    has_analytics = models.BooleanField(default=False)
    has_api_access = models.BooleanField(default=False)
    has_white_labeling = models.BooleanField(default=False)
    has_priority_support = models.BooleanField(default=False)
    has_custom_integrations = models.BooleanField(default=False)
    
    # File access features
    max_file_size_mb = models.IntegerField(default=10)  # Max file size in MB
    monthly_download_limit = models.IntegerField(null=True, blank=True)  # Null = unlimited
    recording_access = models.BooleanField(default=False)  # Access to class recordings
    premium_content_access = models.BooleanField(default=False)  # Access to premium content
    
    # Additional file features stored as JSON
    features = models.JSONField(default=dict, blank=True)  # Additional features as key-value pairs
    
    # Metadata
    is_popular = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'subscription_plans'
        ordering = ['sort_order', 'price_monthly']
    
    def __str__(self):
        return f"{self.display_name} - ${self.price_monthly}/month"
    
    def get_price(self, billing_cycle='monthly'):
        """Get price for billing cycle"""
        return self.price_yearly if billing_cycle == 'yearly' else self.price_monthly


class Subscription(TenantAwareModel):
    """Institutional subscription plans"""
    
    PLAN_CHOICES = [
        ('basic', 'Basic'),
        ('pro', 'Pro'),
        ('enterprise', 'Enterprise'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('cancelled', 'Cancelled'),
        ('past_due', 'Past Due'),
        ('unpaid', 'Unpaid'),
        ('trialing', 'Trialing'),
    ]
    
    BILLING_CYCLE_CHOICES = [
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.OneToOneField(
        'accounts.Organization', 
        on_delete=models.CASCADE, 
        related_name='subscription'
    )
    
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES)
    billing_cycle = models.CharField(max_length=20, choices=BILLING_CYCLE_CHOICES, default='monthly')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Pricing
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    
    # Stripe subscription details
    stripe_subscription_id = models.CharField(max_length=100, blank=True)
    stripe_customer_id = models.CharField(max_length=100, blank=True)
    
    # Billing dates
    current_period_start = models.DateTimeField()
    current_period_end = models.DateTimeField()
    trial_end = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'subscriptions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.organization.name} - {self.plan} ({self.status})"
    
    def is_active(self):
        """Check if subscription is currently active"""
        return self.status == 'active' and self.current_period_end > timezone.now()
    
    def cancel(self):
        """Cancel subscription"""
        self.status = 'cancelled'
        self.cancelled_at = timezone.now()
        self.save()
    
    def get_plan_details(self):
        """Get subscription plan details with feature limits"""
        try:
            return SubscriptionPlan.objects.get(name=self.plan)
        except SubscriptionPlan.DoesNotExist:
            return None
    
    def can_add_user(self):
        """Check if organization can add more users"""
        plan_details = self.get_plan_details()
        if not plan_details:
            return False
        
        current_users = self.organization.users.count()
        return current_users < plan_details.max_users
    
    def can_create_course(self):
        """Check if organization can create more courses"""
        plan_details = self.get_plan_details()
        if not plan_details:
            return False
        
        from apps.courses.models import Course
        current_courses = Course.objects.filter(tenant=self.organization).count()
        return current_courses < plan_details.max_courses
    
    def get_remaining_ai_quota(self):
        """Get remaining AI quota for current month"""
        plan_details = self.get_plan_details()
        if not plan_details:
            return 0
        
        from django.utils import timezone
        from datetime import datetime
        from apps.ai.models import AIUsage
        
        # Get current month usage
        now = timezone.now()
        month_start = datetime(now.year, now.month, 1, tzinfo=now.tzinfo)
        
        used_quota = AIUsage.objects.filter(
            tenant=self.organization,
            created_at__gte=month_start
        ).count()
        
        return max(0, plan_details.ai_quota_monthly - used_quota)
    
    def has_feature(self, feature_name):
        """Check if subscription has specific feature"""
        plan_details = self.get_plan_details()
        if not plan_details:
            return False
        
        return getattr(plan_details, f'has_{feature_name}', False)
    
    def days_until_renewal(self):
        """Get days until next billing cycle"""
        from django.utils import timezone
        
        if self.status != 'active':
            return None
        
        delta = self.current_period_end - timezone.now()
        return delta.days if delta.days > 0 else 0


class Invoice(TenantAwareModel):
    """Invoice generation and tracking for payments and subscriptions"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
        ('void', 'Void'),
    ]
    
    INVOICE_TYPE_CHOICES = [
        ('payment', 'Payment Invoice'),
        ('subscription', 'Subscription Invoice'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice_number = models.CharField(max_length=50, unique=True)
    
    # Invoice can be for user or organization
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invoices', null=True, blank=True)
    organization = models.ForeignKey(
        'accounts.Organization', 
        on_delete=models.CASCADE, 
        related_name='invoices',
        null=True, 
        blank=True
    )
    
    invoice_type = models.CharField(max_length=20, choices=INVOICE_TYPE_CHOICES, default='payment')
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='invoice', null=True, blank=True)
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='invoices', null=True, blank=True)
    
    # Amounts
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=4, default=Decimal('0.0000'))  # e.g., 0.0825 for 8.25%
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Dates
    issue_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    
    # Invoice details
    description = models.TextField()
    notes = models.TextField(blank=True)
    
    # Billing address
    billing_name = models.CharField(max_length=200)
    billing_email = models.EmailField()
    billing_address_line1 = models.CharField(max_length=200, blank=True)
    billing_address_line2 = models.CharField(max_length=200, blank=True)
    billing_city = models.CharField(max_length=100, blank=True)
    billing_state = models.CharField(max_length=100, blank=True)
    billing_postal_code = models.CharField(max_length=20, blank=True)
    billing_country = models.CharField(max_length=100, blank=True)
    
    # File storage
    pdf_file = models.FileField(upload_to='invoices/', blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'invoices'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'status']),
            models.Index(fields=['invoice_number']),
            models.Index(fields=['due_date']),
        ]
    
    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.billing_email}"
    
    def save(self, *args, **kwargs):
        """Auto-generate invoice number if not set"""
        if not self.invoice_number:
            self.invoice_number = self.generate_invoice_number()
        
        # Calculate total amount
        self.total_amount = self.subtotal + self.tax_amount - self.discount_amount
        
        super().save(*args, **kwargs)
    
    def generate_invoice_number(self):
        """Generate unique invoice number"""
        from datetime import datetime
        year = datetime.now().year
        month = datetime.now().month
        
        # Get last invoice number for this tenant and month
        last_invoice = Invoice.objects.filter(
            tenant=self.tenant,
            created_at__year=year,
            created_at__month=month
        ).order_by('-created_at').first()
        
        if last_invoice and last_invoice.invoice_number:
            try:
                last_number = int(last_invoice.invoice_number.split('-')[-1])
                next_number = last_number + 1
            except (ValueError, IndexError):
                next_number = 1
        else:
            next_number = 1
        
        return f"INV-{year}{month:02d}-{next_number:04d}"
    
    def calculate_tax(self):
        """Calculate tax based on billing location and organization settings"""
        # Default tax rates by country/state (simplified)
        tax_rates = {
            'US': {
                'CA': Decimal('0.0875'),  # California
                'NY': Decimal('0.08'),    # New York
                'TX': Decimal('0.0625'),  # Texas
                'FL': Decimal('0.06'),    # Florida
                'default': Decimal('0.0')
            },
            'CA': Decimal('0.13'),  # Canada GST+PST average
            'GB': Decimal('0.20'),  # UK VAT
            'DE': Decimal('0.19'),  # Germany VAT
            'FR': Decimal('0.20'),  # France VAT
            'default': Decimal('0.0')
        }
        
        # Get tax rate based on billing country and state
        country_rates = tax_rates.get(self.billing_country, tax_rates['default'])
        
        if isinstance(country_rates, dict):
            # US state-specific rates
            tax_rate = country_rates.get(self.billing_state, country_rates['default'])
        else:
            # Country-level rate
            tax_rate = country_rates
        
        self.tax_rate = tax_rate
        self.tax_amount = self.subtotal * tax_rate
        self.save()
        
        return self.tax_amount
    
    def mark_paid(self):
        """Mark invoice as paid"""
        self.status = 'paid'
        self.paid_at = timezone.now()
        self.save()
    
    def mark_overdue(self):
        """Mark invoice as overdue"""
        if self.status in ['sent'] and self.due_date < timezone.now().date():
            self.status = 'overdue'
            self.save()


class InvoiceLineItem(models.Model):
    """Individual line items for invoices"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='line_items')
    
    description = models.CharField(max_length=500)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('1.00'))
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Optional course reference
    course = models.ForeignKey('courses.Course', on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'invoice_line_items'
        ordering = ['id']
    
    def save(self, *args, **kwargs):
        """Calculate total price"""
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.description} - {self.total_price}"