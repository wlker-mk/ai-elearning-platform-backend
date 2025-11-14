from django.apps import AppConfig

class GatewaysConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.payments.gateways'
    
    def ready(self):
        import apps.payments.gateways.signals
