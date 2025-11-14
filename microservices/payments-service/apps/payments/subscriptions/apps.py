from django.apps import AppConfig

class SubscriptionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.payments.subscriptions'
    
    def ready(self):
        import apps.payments.subscriptions.signals
