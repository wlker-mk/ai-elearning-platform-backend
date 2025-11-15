"""
config/celery.py
Configuration Celery pour le service de paiements
"""
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

app = Celery('payments_service')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Configuration des taches périodiques
app.conf.beat_schedule = {
    'check-expired-subscriptions': {
        'task': 'payments.check_expired_subscriptions',
        'schedule': crontab(hour=2, minute=0),
    },
    'process-subscription-renewals': {
        'task': 'payments.process_subscription_renewals',
        'schedule': crontab(hour=3, minute=0),
    },
    'send-overdue-invoice-reminders': {
        'task': 'payments.send_overdue_invoice_reminders',
        'schedule': crontab(hour=9, minute=0),
    },
    'generate-payment-reports': {
        'task': 'payments.generate_payment_reports',
        'schedule': crontab(hour=6, minute=0, day_of_month=1),
    },
}

app.conf.task_routes = {
    'payments.*': {'queue': 'payments'},
}

app.conf.task_time_limit = 600
app.conf.task_soft_time_limit = 540

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
