from django.apps import AppConfig

class InstructorsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users.instructors'
    
    def ready(self):
        import apps.users.instructors.signals
