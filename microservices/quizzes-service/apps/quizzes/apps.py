from django.apps import AppConfig

class QuizzesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.quizzes'
    
    def ready(self):
        import apps.quizzes.signals
