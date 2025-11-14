from django.apps import AppConfig

class BillingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.payments.billing'
    
    def ready(self):
        import apps.payments.billing.signals
