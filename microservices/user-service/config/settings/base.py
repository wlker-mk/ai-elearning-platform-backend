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

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party
    'rest_framework',
    'corsheaders',
    'django_filters',
    'django_celery_results',
    'rest_framework_simplejwt',
    
    # Local apps
    'apps.users',
    'apps.users.students', 
    'apps.users.instructors',
    'apps.users.profiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
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
                'django.contrib.auth.context_processors.auth',
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
            'CONN_MAX_AGE': 600,  # Optimisé pour les connexions persistantes
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

# Password validation (renforcée pour user-service)
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        'OPTIONS': {
            'user_attributes': ('username', 'email', 'first_name', 'last_name'),
            'max_similarity': 0.7,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# REST Framework Configuration (optimisé pour user-service)
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
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
        'login': '10/minute',  # Protection contre le brute force
    }
}

# Simple JWT Configuration (optimisé pour la sécurité)
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(
        minutes=config('JWT_ACCESS_TOKEN_LIFETIME', default='15', cast=int)
    ),
    'REFRESH_TOKEN_LIFETIME': timedelta(
        days=config('JWT_REFRESH_TOKEN_LIFETIME', default=7, cast=int)
    ),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': config('JWT_ALGORITHM', default='HS256'),
    'SIGNING_KEY': config('JWT_SECRET_KEY', default=SECRET_KEY),
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',
    'JTI_CLAIM': 'jti',
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

# CORS Configuration
CORS_ALLOW_ALL_ORIGINS = config('CORS_ALLOW_ALL_ORIGINS', default=False, cast=bool)
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='http://localhost:3000,http://127.0.0.1:3000', cast=lambda v: [s.strip() for s in v.split(',')] if v else [])
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', default='', cast=lambda v: [s.strip() for s in v.split(',')] if v else [])
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

# Cache Configuration (optimisé pour user-service)
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
        },
        'KEY_PREFIX': 'user_service',
        'TIMEOUT': 300,  # 5 minutes pour les données utilisateur fréquentes
    }
}

# Session Configuration (si nécessaire pour l'admin)
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
SESSION_CACHE_ALIAS = 'default'

# Logging Configuration (enrichi pour user-service)
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
        'user_audit': {
            'format': '{asctime} - {levelname} - user_id:{user_id} - action:{action} - ip:{ip_address} - {message}',
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
        'audit_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': str(LOG_DIR / 'audit.log'),
            'formatter': 'user_audit',
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
            'handlers': ['console', 'file', 'error_file', 'audit_file'],
            'level': config('LOG_LEVEL', default='DEBUG'),
            'propagate': False,
        },
        'audit': {
            'handlers': ['audit_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Security Settings
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# Custom settings pour user-service
APPEND_SLASH = True
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB - suffisant pour user-service
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB - pour les avatars utilisateurs

# User-service specific settings
USERNAME_MIN_LENGTH = 3
USERNAME_MAX_LENGTH = 30
PASSWORD_MIN_LENGTH = 8
MAX_LOGIN_ATTEMPTS = 5
LOGIN_TIMEOUT_MINUTES = 15

# Email settings (pour les notifications utilisateur)
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@userservice.com')