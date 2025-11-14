from .base import *

DEBUG = True

ALLOWED_HOSTS = ['*']

CORS_ALLOW_ALL_ORIGINS = True

# Development-specific settings
INSTALLED_APPS += [
    'django_extensions',
]
