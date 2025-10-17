from rest_framework import serializers
from .models import Payment, Invoice, Subscription, InvoiceLineItem, SubscriptionPlan


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for Payment model"""
    
    user_email = serializers.CharField(source='user.email', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)
    subscription_plan = serializers.CharField(source='subscription.plan', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'user', 'user_email', 'course', 'course_title', 
            'subscription', 'subscription_plan', 'payment_type',
            'amount', 'currency', 'payment_method', 'status',
            'stripe_payment_intent_id', 'stripe_subscription_id',
            'paypal_order_id', 'bank_transfer_reference',
            'description', 'created_at', 'completed_at', 'failed_at'
        ]
        read_only_fields = [
            'id', 'user', 'stripe_payment_intent_id', 'stripe_subscription_id',
            'paypal_order_id', 'bank_transfer_reference', 'created_at',
            'completed_at', 'failed_at'
        ]


class InvoiceLineItemSerializer(serializers.ModelSerializer):
    """Serializer for InvoiceLineItem model"""
    
    course_title = serializers.CharField(source='course.title', read_only=True)
    
    class Meta:
        model = InvoiceLineItem
        fields = [
            'id', 'description', 'quantity', 'unit_price', 
            'total_price', 'course', 'course_title'
        ]
        read_only_fields = ['id', 'total_price']


class InvoiceSerializer(serializers.ModelSerializer):
    """Serializer for Invoice model"""
    
    line_items = InvoiceLineItemSerializer(many=True, read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    payment_id = serializers.CharField(source='payment.id', read_only=True)
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'user', 'user_email', 
            'organization', 'organization_name', 'invoice_type',
            'payment', 'payment_id', 'subscription',
            'subtotal', 'tax_rate', 'tax_amount', 'discount_amount',
            'total_amount', 'currency', 'status',
            'issue_date', 'due_date', 'description', 'notes',
            'billing_name', 'billing_email', 'billing_address_line1',
            'billing_address_line2', 'billing_city', 'billing_state',
            'billing_postal_code', 'billing_country',
            'pdf_file', 'line_items',
            'created_at', 'updated_at', 'sent_at', 'paid_at'
        ]
        read_only_fields = [
            'id', 'invoice_number', 'total_amount', 'created_at',
            'updated_at', 'sent_at', 'paid_at'
        ]


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    """Serializer for SubscriptionPlan model"""
    
    class Meta:
        model = SubscriptionPlan
        fields = [
            'id', 'name', 'display_name', 'description',
            'price_monthly', 'price_yearly',
            'max_users', 'max_courses', 'max_storage_gb', 'ai_quota_monthly',
            'has_analytics', 'has_api_access', 'has_white_labeling',
            'has_priority_support', 'has_custom_integrations',
            'is_popular', 'is_active', 'sort_order'
        ]
        read_only_fields = ['id']


class SubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for Subscription model"""
    
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    is_active_status = serializers.BooleanField(source='is_active', read_only=True)
    plan_details = SubscriptionPlanSerializer(source='get_plan_details', read_only=True)
    days_until_renewal = serializers.IntegerField(read_only=True)
    remaining_ai_quota = serializers.IntegerField(source='get_remaining_ai_quota', read_only=True)
    can_add_user = serializers.BooleanField(read_only=True)
    can_create_course = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Subscription
        fields = [
            'id', 'organization', 'organization_name', 'plan',
            'billing_cycle', 'status', 'is_active_status',
            'amount', 'currency', 'stripe_subscription_id',
            'stripe_customer_id', 'current_period_start',
            'current_period_end', 'trial_end',
            'plan_details', 'days_until_renewal', 'remaining_ai_quota',
            'can_add_user', 'can_create_course',
            'created_at', 'updated_at', 'cancelled_at'
        ]
        read_only_fields = [
            'id', 'stripe_subscription_id', 'stripe_customer_id',
            'created_at', 'updated_at', 'cancelled_at'
        ]


class PaymentCreateSerializer(serializers.Serializer):
    """Serializer for creating payments"""
    
    course_id = serializers.UUIDField(required=False)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    payment_method = serializers.ChoiceField(choices=Payment.PAYMENT_METHOD_CHOICES)
    
    def validate(self, data):
        """Validate payment creation data"""
        if not data.get('course_id'):
            raise serializers.ValidationError("course_id is required for course payments")
        
        return data


class SubscriptionCreateSerializer(serializers.Serializer):
    """Serializer for creating subscriptions"""
    
    plan = serializers.ChoiceField(choices=Subscription.PLAN_CHOICES)
    billing_cycle = serializers.ChoiceField(
        choices=Subscription.BILLING_CYCLE_CHOICES,
        default='monthly'
    )
    payment_method = serializers.ChoiceField(
        choices=Payment.PAYMENT_METHOD_CHOICES,
        default='stripe'
    )


class BankTransferApprovalSerializer(serializers.Serializer):
    """Serializer for bank transfer approval/rejection"""
    
    reason = serializers.CharField(required=False, allow_blank=True)