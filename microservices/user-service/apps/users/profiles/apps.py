from django.apps import AppConfig

class ProfilesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users.profiles'
    
    def ready(self):
        import apps.users.profiles.signals
