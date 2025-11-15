from django.urls import path
from apps.payments.billing.views import (
    InvoiceView,
    InvoiceByNumberView,
    OverdueInvoicesView
)

app_name = 'billing'

urlpatterns = [
    path('', InvoiceView.as_view(), name='invoices'),
    path('<str:invoice_id>/', InvoiceView.as_view(), name='invoice-detail'),
    path('number/<str:invoice_number>/', InvoiceByNumberView.as_view(), name='invoice-by-number'),
    path('overdue/', OverdueInvoicesView.as_view(), name='overdue-invoices'),
]
