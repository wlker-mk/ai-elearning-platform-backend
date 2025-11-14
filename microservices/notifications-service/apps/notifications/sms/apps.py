from django.apps import AppConfig

class SmsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.notifications.sms'
    
    def ready(self):
        import apps.notifications.sms.signals
