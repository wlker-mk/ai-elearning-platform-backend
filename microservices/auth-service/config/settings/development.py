from decouple import config
from .base import *

DEBUG = True # Enable debug mode for development

ALLOWED_HOSTS = ['*']

CORS_ALLOW_ALL_ORIGINS = True

# Development-specific settings
INSTALLED_APPS += [
    'django_extensions',
]
