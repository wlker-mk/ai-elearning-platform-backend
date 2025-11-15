from django.urls import path, include

app_name = 'payments'

urlpatterns = [
    path('payments/', include('apps.payments.payments.urls')),
    path('invoices/', include('apps.payments.billing.urls')),
    path('subscriptions/', include('apps.payments.subscriptions.urls')),
]
