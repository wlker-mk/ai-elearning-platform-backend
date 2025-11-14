from django.apps import AppConfig

class CoursesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.courses.courses'
    
    def ready(self):
        import apps.courses.courses.signals
