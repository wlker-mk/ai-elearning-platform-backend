from django.urls import path
from apps.payments.payments.views import (
    PaymentView,
    ConfirmPaymentView,
    RefundPaymentView,
    PaymentStatisticsView
)

app_name = 'payments'

urlpatterns = [
    path('', PaymentView.as_view(), name='payments'),
    path('<str:payment_id>/', PaymentView.as_view(), name='payment-detail'),
    path('<str:payment_id>/confirm/', ConfirmPaymentView.as_view(), name='confirm-payment'),
    path('<str:payment_id>/refund/', RefundPaymentView.as_view(), name='refund-payment'),
    path('statistics/', PaymentStatisticsView.as_view(), name='payment-statistics'),
]