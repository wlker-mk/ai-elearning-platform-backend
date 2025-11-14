from django.apps import AppConfig

class RewardsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.gamification.rewards'
    
    def ready(self):
        import apps.gamification.rewards.signals
