from django.apps import AppConfig

class AchievementsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.gamification.achievements'
    
    def ready(self):
        import apps.gamification.achievements.signals
