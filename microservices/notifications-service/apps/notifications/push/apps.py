from django.apps import AppConfig

class PushConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.notifications.push'
    
    def ready(self):
        import apps.notifications.push.signals
