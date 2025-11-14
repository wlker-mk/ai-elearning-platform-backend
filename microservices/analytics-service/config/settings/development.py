from .base import *
from django.http import JsonResponse

DEBUG = True

ALLOWED_HOSTS = ['*']

CORS_ALLOW_ALL_ORIGINS = True

# Development-specific settings
INSTALLED_APPS += [
    'django_extensions',
]