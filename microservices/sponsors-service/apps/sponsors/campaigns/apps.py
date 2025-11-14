from django.apps import AppConfig

class CampaignsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.sponsors.campaigns'
    
    def ready(self):
        import apps.sponsors.campaigns.signals
