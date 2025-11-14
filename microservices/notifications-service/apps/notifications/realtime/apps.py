from django.apps import AppConfig

class RealtimeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.notifications.realtime'
    
    def ready(self):
        import apps.notifications.realtime.signals
