from django.apps import AppConfig

class EmailConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.notifications.email'
    
    def ready(self):
        import apps.notifications.email.signals
