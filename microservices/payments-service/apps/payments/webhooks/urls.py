"""
apps/payments/webhooks/urls.py
"""
from django.urls import path
from apps.payments.webhooks.views import (
    StripeWebhookView,
    PayPalWebhookView
)

app_name = 'webhooks'

urlpatterns = [
    path('stripe/', StripeWebhookView.as_view(), name='stripe-webhook'),
    path('paypal/', PayPalWebhookView.as_view(), name='paypal-webhook'),
]
