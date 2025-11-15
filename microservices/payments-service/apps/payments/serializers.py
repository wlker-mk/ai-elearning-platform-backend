from rest_framework import serializers
from datetime import datetime


# ============ Payment Serializers ============

class PaymentSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    student_id = serializers.UUIDField(source='studentId')
    amount = serializers.FloatField()
    currency = serializers.CharField(default='USD')
    method = serializers.ChoiceField(choices=[
        'CREDIT_CARD', 'DEBIT_CARD', 'PAYPAL', 'STRIPE',
        'BANK_TRANSFER', 'MOBILE_MONEY', 'CRYPTO',
        'APPLE_PAY', 'GOOGLE_PAY'
    ])
    status = serializers.CharField(read_only=True)
    transaction_id = serializers.CharField(source='transactionId', read_only=True, allow_null=True)
    external_reference = serializers.CharField(source='externalReference', read_only=True, allow_null=True)
    course_id = serializers.UUIDField(source='courseId', required=False, allow_null=True)
    subscription_id = serializers.UUIDField(source='subscriptionId', required=False, allow_null=True)
    items = serializers.JSONField(required=False, allow_null=True)
    description = serializers.CharField(required=False, allow_null=True)
    processing_fee = serializers.FloatField(source='processingFee', read_only=True)
    platform_fee = serializers.FloatField(source='platformFee', read_only=True)
    net_amount = serializers.FloatField(source='netAmount', read_only=True)
    is_refunded = serializers.BooleanField(source='isRefunded', read_only=True)
    refunded_amount = serializers.FloatField(source='refundedAmount', read_only=True, allow_null=True)
    paid_at = serializers.DateTimeField(source='paidAt', read_only=True, allow_null=True)
    created_at = serializers.DateTimeField(source='createdAt', read_only=True)
    updated_at = serializers.DateTimeField(source='updatedAt', read_only=True)


class CreatePaymentSerializer(serializers.Serializer):
    student_id = serializers.UUIDField()
    amount = serializers.FloatField(min_value=0.01)
    currency = serializers.CharField(default='USD', max_length=3)
    method = serializers.ChoiceField(choices=[
        'CREDIT_CARD', 'DEBIT_CARD', 'PAYPAL', 'STRIPE',
        'BANK_TRANSFER', 'MOBILE_MONEY', 'CRYPTO',
        'APPLE_PAY', 'GOOGLE_PAY'
    ])
    course_id = serializers.UUIDField(required=False, allow_null=True)
    subscription_id = serializers.UUIDField(required=False, allow_null=True)
    items = serializers.JSONField(required=False, allow_null=True)
    description = serializers.CharField(required=False, allow_null=True)
    gateway = serializers.ChoiceField(choices=['STRIPE', 'PAYPAL'], default='STRIPE')


class RefundPaymentSerializer(serializers.Serializer):
    amount = serializers.FloatField(required=False, allow_null=True, min_value=0.01)
    reason = serializers.CharField(required=False, allow_null=True)


# ============ Invoice Serializers ============

class InvoiceSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    invoice_number = serializers.CharField(source='invoiceNumber', read_only=True)
    student_id = serializers.UUIDField(source='studentId')
    payment_id = serializers.UUIDField(source='paymentId', read_only=True, allow_null=True)
    subtotal = serializers.FloatField()
    tax = serializers.FloatField()
    discount = serializers.FloatField()
    total = serializers.FloatField()
    amount_paid = serializers.FloatField(source='amountPaid', read_only=True)
    amount_due = serializers.FloatField(source='amountDue', read_only=True)
    currency = serializers.CharField(default='USD')
    status = serializers.CharField(read_only=True)
    items = serializers.JSONField()
    issue_date = serializers.DateTimeField(source='issueDate', read_only=True)
    due_date = serializers.DateTimeField(source='dueDate')
    paid_at = serializers.DateTimeField(source='paidAt', read_only=True, allow_null=True)
    pdf_url = serializers.URLField(source='pdfUrl', read_only=True, allow_null=True)
    created_at = serializers.DateTimeField(source='createdAt', read_only=True)
    updated_at = serializers.DateTimeField(source='updatedAt', read_only=True)


class CreateInvoiceSerializer(serializers.Serializer):
    student_id = serializers.UUIDField()
    items = serializers.ListField(
        child=serializers.DictField()
    )
    currency = serializers.CharField(default='USD', max_length=3)
    tax_country = serializers.CharField(required=False, allow_null=True)
    discount_amount = serializers.FloatField(default=0, min_value=0)
    due_days = serializers.IntegerField(default=30, min_value=1)


# ============ Subscription Serializers ============

class SubscriptionSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    student_id = serializers.UUIDField(source='studentId')
    type = serializers.ChoiceField(choices=[
        'FREE', 'MONTHLY', 'QUARTERLY', 'SEMI_ANNUAL',
        'ANNUAL', 'LIFETIME', 'ENTERPRISE', 'STUDENT', 'TEAM'
    ])
    start_date = serializers.DateTimeField(source='startDate', read_only=True)
    end_date = serializers.DateTimeField(source='endDate', read_only=True)
    trial_end_date = serializers.DateTimeField(source='trialEndDate', read_only=True, allow_null=True)
    is_active = serializers.BooleanField(source='isActive', read_only=True)
    is_cancelled = serializers.BooleanField(source='isCancelled', read_only=True)
    cancelled_at = serializers.DateTimeField(source='cancelledAt', read_only=True, allow_null=True)
    price = serializers.FloatField()
    currency = serializers.CharField(default='USD')
    auto_renew = serializers.BooleanField(source='autoRenew')
    next_billing_date = serializers.DateTimeField(source='nextBillingDate', read_only=True, allow_null=True)
    payment_method = serializers.CharField(source='paymentMethod')
    last_payment_id = serializers.UUIDField(source='lastPaymentId', read_only=True, allow_null=True)
    created_at = serializers.DateTimeField(source='createdAt', read_only=True)
    updated_at = serializers.DateTimeField(source='updatedAt', read_only=True)


class CreateSubscriptionSerializer(serializers.Serializer):
    student_id = serializers.UUIDField()
    type = serializers.ChoiceField(choices=[
        'FREE', 'MONTHLY', 'QUARTERLY', 'SEMI_ANNUAL',
        'ANNUAL', 'LIFETIME', 'ENTERPRISE', 'STUDENT', 'TEAM'
    ])
    payment_method = serializers.ChoiceField(choices=[
        'CREDIT_CARD', 'DEBIT_CARD', 'PAYPAL', 'STRIPE',
        'BANK_TRANSFER', 'MOBILE_MONEY', 'CRYPTO',
        'APPLE_PAY', 'GOOGLE_PAY'
    ])
    payment_id = serializers.UUIDField(required=False, allow_null=True)
    trial_days = serializers.IntegerField(default=0, min_value=0)


class CancelSubscriptionSerializer(serializers.Serializer):
    immediate = serializers.BooleanField(default=False)


# ============ Discount Serializers ============

class DiscountSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    code = serializers.CharField()
    type = serializers.ChoiceField(choices=[
        'PERCENTAGE', 'FIXED_AMOUNT', 'BUNDLE',
        'EARLY_BIRD', 'FLASH_SALE'
    ])
    value = serializers.FloatField()
    start_date = serializers.DateTimeField(source='startDate')
    end_date = serializers.DateTimeField(source='endDate')
    max_uses = serializers.IntegerField(source='maxUses', required=False, allow_null=True)
    uses_count = serializers.IntegerField(source='usesCount', read_only=True)
    max_uses_per_user = serializers.IntegerField(source='maxUsesPerUser', default=1)
    created_at = serializers.DateTimeField(source='createdAt', read_only=True)
    updated_at = serializers.DateTimeField(source='updatedAt', read_only=True)


class CreateDiscountSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=50)
    type = serializers.ChoiceField(choices=[
        'PERCENTAGE', 'FIXED_AMOUNT', 'BUNDLE',
        'EARLY_BIRD', 'FLASH_SALE'
    ])
    value = serializers.FloatField(min_value=0)
    start_date = serializers.DateTimeField()
    end_date = serializers.DateTimeField()
    max_uses = serializers.IntegerField(required=False, allow_null=True, min_value=1)
    max_uses_per_user = serializers.IntegerField(default=1, min_value=1)


class ValidateDiscountSerializer(serializers.Serializer):
    code = serializers.CharField()
    user_id = serializers.UUIDField()


# ============ Transaction Serializers ============

class TransactionSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    payment_id = serializers.UUIDField(source='paymentId', allow_null=True)
    type = serializers.CharField()
    amount = serializers.FloatField()
    currency = serializers.CharField(default='USD')
    status = serializers.CharField()
    from_account = serializers.CharField(source='fromAccount', allow_null=True)
    to_account = serializers.CharField(source='toAccount', allow_null=True)
    gateway_id = serializers.CharField(source='gatewayId', allow_null=True)
    gateway_response = serializers.JSONField(source='gatewayResponse', allow_null=True)
    created_at = serializers.DateTimeField(source='createdAt', read_only=True)