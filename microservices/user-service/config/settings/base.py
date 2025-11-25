import os
from datetime import timedelta
from pathlib import Path
from urllib.parse import urlparse
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent.parent
LOG_DIR = BASE_DIR / 'logs'
LOG_DIR.mkdir(parents=True, exist_ok=True)

SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-this-in-production')

DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1,0.0.0.0,backend,user-service', cast=lambda v: [s.strip() for s in v.split(',')])

# APPLICATIONS CONFIGURÉES POUR ÉVITER LES CONFLITS AVEC PRISMA
INSTALLED_APPS = [
    # Applications Django essentielles (sans conflits de base de données)
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party
    'rest_framework',
    'corsheaders',
    'django_filters',
    'django_celery_results',
    
    # Local apps
    'apps.users',
    'apps.users.students', 
    'apps.users.instructors',
    'apps.users.profiles',
]

# ⚠️ COMENTÉ - En conflit avec Prisma
# AUTH_USER_MODEL = 'users.User'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database Configuration
DATABASE_URL = config('DATABASE_URL', default='')

if DATABASE_URL:
    parsed_url = urlparse(DATABASE_URL)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': parsed_url.path[1:] or config('POSTGRES_DB', default='user_service_db'),
            'USER': parsed_url.username or config('POSTGRES_USER', default='postgres'),
            'PASSWORD': parsed_url.password or config('POSTGRES_PASSWORD', default='postgres'),
            'HOST': parsed_url.hostname or config('POSTGRES_HOST', default='postgres'),
            'PORT': str(parsed_url.port) if parsed_url.port else config('POSTGRES_PORT', default='5432'),
            'CONN_MAX_AGE': 600,
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('POSTGRES_DB', default='user_service_db'),
            'USER': config('POSTGRES_USER', default='postgres'),
            'PASSWORD': config('POSTGRES_PASSWORD', default='postgres'),
            'HOST': config('POSTGRES_HOST', default='postgres'),
            'PORT': config('POSTGRES_PORT', default='5432'),
            'CONN_MAX_AGE': 600,
        }
    }

# ⚠️ COMENTÉ - En conflit avec l'authentification Django
# AUTH_PASSWORD_VALIDATORS = []

# REST Framework Configuration (sans authentification Django)
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',  # Temporaire pour tests
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': config('DEFAULT_PAGE_SIZE', default=20, cast=int),
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.FormParser',
    ],
    'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler',
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
    }
}

# ⚠️ COMENTÉ - En conflit avec l'authentification Django
# SIMPLE_JWT = {}

# CORS Configuration
CORS_ALLOW_ALL_ORIGINS = config('CORS_ALLOW_ALL_ORIGINS', default=False, cast=bool)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",      # ← AJOUTER (Vite dev server)
    "http://127.0.0.1:5173",   
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://frontend:3000",
]
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",      # ← AJOUTER
    "http://127.0.0.1:5173", 
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://frontend:3000",
]
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Redis Configuration
REDIS_URL = config('REDIS_URL', default='redis://redis:6379')

# Celery Configuration
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default=config('RABBITMQ_URL', default=REDIS_URL))
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='django-db')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_RESULT_EXTENDED = True
CELERY_TASK_ROUTES = {
    'apps.users.tasks.send_welcome_email': {'queue': 'email'},
    'apps.users.tasks.process_user_upload': {'queue': 'media'},
}

# Cache Configuration
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
        },
        'KEY_PREFIX': 'user_service',
        'TIMEOUT': 300,
    }
}

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': config('LOG_LEVEL', default='INFO'),
            'class': 'logging.FileHandler',
            'filename': str(LOG_DIR / 'app.log'),
            'formatter': 'verbose',
        },
        'console': {
            'level': config('LOG_LEVEL', default='INFO'),
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': str(LOG_DIR / 'error.log'),
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file', 'error_file'],
        'level': config('LOG_LEVEL', default='INFO'),
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file', 'error_file'],
            'level': config('DJANGO_LOG_LEVEL', default='INFO'),
            'propagate': False,
        },
        'apps.users': {
            'handlers': ['console', 'file', 'error_file'],
            'level': config('LOG_LEVEL', default='DEBUG'),
            'propagate': False,
        },
    },
}

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Security Settings
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# Custom settings
APPEND_SLASH = True
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760

# User-service specific settings
USERNAME_MIN_LENGTH = 3
USERNAME_MAX_LENGTH = 30
PASSWORD_MIN_LENGTH = 8
MAX_LOGIN_ATTEMPTS = 5
LOGIN_TIMEOUT_MINUTES = 15

# Email settings
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@userservice.com')