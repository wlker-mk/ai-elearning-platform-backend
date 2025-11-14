from django.apps import AppConfig

class GatewayConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.gateway'
    
    def ready(self):
        import apps.gateway.signals
