from django.apps import AppConfig

class SponsorshipsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.sponsors.sponsorships'
    
    def ready(self):
        import apps.sponsors.sponsorships.signals
