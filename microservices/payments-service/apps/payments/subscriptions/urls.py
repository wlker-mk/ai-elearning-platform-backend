from django.urls import path
from apps.payments.subscriptions.views import (
    SubscriptionView,
    CancelSubscriptionView,
    DiscountView,
    ValidateDiscountView
)

app_name = 'subscriptions'

urlpatterns = [
    path('', SubscriptionView.as_view(), name='subscriptions'),
    path('<str:subscription_id>/', SubscriptionView.as_view(), name='subscription-detail'),
    path('<str:subscription_id>/cancel/', CancelSubscriptionView.as_view(), name='cancel-subscription'),
    path('discounts/', DiscountView.as_view(), name='discounts'),
    path('discounts/validate/', ValidateDiscountView.as_view(), name='validate-discount'),
]
