from django.apps import AppConfig

class I18nConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.i18n'
    
    def ready(self):
        import apps.i18n.signals
