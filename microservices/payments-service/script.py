#!/usr/bin/env python3
"""
Script de correction du Payments Service
Exécuter depuis le répertoire microservices/payments-service/
"""

import os
import sys
from pathlib import Path
from typing import Dict, List

# Couleurs pour le terminal
class Colors:
    BLUE = '\033[0;34m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    NC = '\033[0m'  # No Color

def print_color(message: str, color: str = Colors.NC):
    """Afficher un message en couleur"""
    print(f"{color}{message}{Colors.NC}")

def check_directory():
    """Vérifier qu'on est dans le bon répertoire"""
    current_dir = Path.cwd()
    
    # Vérifier qu'on est dans payments-service
    if not (current_dir / "manage.py").exists():
        print_color("❌ Erreur: Ce script doit être exécuté depuis le répertoire payments-service", Colors.RED)
        print_color(f"Répertoire actuel: {current_dir}", Colors.RED)
        sys.exit(1)
    
    print_color(f"✓ Répertoire correct: {current_dir}", Colors.GREEN)
    return current_dir

def create_directories(base_dir: Path):
    """Créer les répertoires manquants"""
    print_color("\n📁 Création des répertoires manquants...", Colors.YELLOW)
    
    directories = [
        "apps/payments/webhooks",
        "apps/payments/webhooks/tests",
        "prisma/migrations",
        "logs",
        "static",
        "media",
        "tests",
    ]
    
    for directory in directories:
        dir_path = base_dir / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"  ✓ {directory}")
    
    print_color("✓ Répertoires créés\n", Colors.GREEN)

def create_init_files(base_dir: Path):
    """Créer les fichiers __init__.py manquants"""
    print_color("📄 Création des fichiers __init__.py...", Colors.YELLOW)
    
    init_files = [
        "apps/payments/webhooks/__init__.py",
        "apps/payments/webhooks/tests/__init__.py",
    ]
    
    for init_file in init_files:
        file_path = base_dir / init_file
        file_path.touch(exist_ok=True)
        print(f"  ✓ {init_file}")
    
    print_color("✓ Fichiers __init__.py créés\n", Colors.GREEN)

def create_webhooks_views(base_dir: Path):
    """Créer le fichier views.py pour les webhooks"""
    print_color("🔗 Création du module webhooks/views.py...", Colors.YELLOW)
    
    content = '''"""
apps/payments/webhooks/views.py
Gestion des webhooks Stripe et PayPal
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from asgiref.sync import async_to_sync
import logging
import json
import stripe

from apps.payments.gateways.services import PaymentService
from apps.payments.subscriptions.services import SubscriptionService
from django.conf import settings

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(APIView):
    """Vue pour gérer les webhooks Stripe"""
    
    permission_classes = []
    authentication_classes = []
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.payment_service = PaymentService()
        self.subscription_service = SubscriptionService()
        stripe.api_key = settings.STRIPE_CONFIG.get('SECRET_KEY', '')
    
    def post(self, request):
        """Traiter les événements Stripe"""
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        
        try:
            event = stripe.Webhook.construct_event(
                payload, 
                sig_header, 
                settings.STRIPE_CONFIG.get('WEBHOOK_SECRET', '')
            )
        except ValueError as e:
            logger.error(f"Invalid payload: {str(e)}")
            return Response(
                {'error': 'Invalid payload'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid signature: {str(e)}")
            return Response(
                {'error': 'Invalid signature'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        event_type = event['type']
        
        try:
            if event_type == 'payment_intent.succeeded':
                self._handle_payment_succeeded(event['data']['object'])
            elif event_type == 'payment_intent.payment_failed':
                self._handle_payment_failed(event['data']['object'])
            elif event_type == 'charge.refunded':
                self._handle_refund(event['data']['object'])
            else:
                logger.info(f"Unhandled event type: {event_type}")
            
            return Response({'status': 'success'}, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error processing webhook: {str(e)}")
            return Response(
                {'error': 'Webhook processing failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _handle_payment_succeeded(self, payment_intent):
        """Gérer le succès d'un paiement"""
        payment_id = payment_intent.get('metadata', {}).get('payment_id')
        if payment_id:
            async_to_sync(self.payment_service.confirm_payment)(
                payment_id,
                payment_intent['id']
            )
            logger.info(f"Payment succeeded: {payment_id}")
    
    def _handle_payment_failed(self, payment_intent):
        """Gérer l'échec d'un paiement"""
        payment_id = payment_intent.get('metadata', {}).get('payment_id')
        if payment_id:
            async_to_sync(self.payment_service.connect)()
            async_to_sync(self.payment_service.db.payment.update)(
                where={'id': payment_id},
                data={'status': 'FAILED'}
            )
            async_to_sync(self.payment_service.disconnect)()
            logger.warning(f"Payment failed: {payment_id}")
    
    def _handle_refund(self, charge):
        """Gérer un remboursement"""
        payment_intent_id = charge.get('payment_intent')
        logger.info(f"Refund processed for: {payment_intent_id}")


@method_decorator(csrf_exempt, name='dispatch')
class PayPalWebhookView(APIView):
    """Vue pour gérer les webhooks PayPal"""
    
    permission_classes = []
    authentication_classes = []
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.payment_service = PaymentService()
    
    def post(self, request):
        """Traiter les événements PayPal"""
        try:
            event = json.loads(request.body)
            event_type = event.get('event_type')
            
            if event_type == 'PAYMENT.CAPTURE.COMPLETED':
                self._handle_payment_completed(event)
            elif event_type == 'PAYMENT.CAPTURE.DENIED':
                self._handle_payment_denied(event)
            else:
                logger.info(f"Unhandled PayPal event: {event_type}")
            
            return Response({'status': 'success'}, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error processing PayPal webhook: {str(e)}")
            return Response(
                {'error': 'Webhook processing failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _handle_payment_completed(self, event):
        """Gérer un paiement complété"""
        resource = event.get('resource', {})
        payment_id = resource.get('custom_id')
        if payment_id:
            async_to_sync(self.payment_service.confirm_payment)(
                payment_id,
                resource.get('id')
            )
            logger.info(f"PayPal payment completed: {payment_id}")
    
    def _handle_payment_denied(self, event):
        """Gérer un paiement refusé"""
        resource = event.get('resource', {})
        payment_id = resource.get('custom_id')
        if payment_id:
            async_to_sync(self.payment_service.connect)()
            async_to_sync(self.payment_service.db.payment.update)(
                where={'id': payment_id},
                data={'status': 'FAILED'}
            )
            async_to_sync(self.payment_service.disconnect)()
            logger.warning(f"PayPal payment denied: {payment_id}")
'''
    
    file_path = base_dir / "apps/payments/webhooks/views.py"
    file_path.write_text(content)
    print(f"  ✓ apps/payments/webhooks/views.py")
    print_color("✓ Webhooks views créé\n", Colors.GREEN)

def create_webhooks_urls(base_dir: Path):
    """Créer le fichier urls.py pour les webhooks"""
    print_color("🔗 Création du module webhooks/urls.py...", Colors.YELLOW)
    
    content = '''"""
apps/payments/webhooks/urls.py
"""
from django.urls import path
from apps.payments.webhooks.views import (
    StripeWebhookView,
    PayPalWebhookView
)

app_name = 'webhooks'

urlpatterns = [
    path('stripe/', StripeWebhookView.as_view(), name='stripe-webhook'),
    path('paypal/', PayPalWebhookView.as_view(), name='paypal-webhook'),
]
'''
    
    file_path = base_dir / "apps/payments/webhooks/urls.py"
    file_path.write_text(content)
    print(f"  ✓ apps/payments/webhooks/urls.py")
    print_color("✓ Webhooks urls créé\n", Colors.GREEN)

def create_celery_tasks(base_dir: Path):
    """Créer le fichier tasks.py"""
    print_color("⚙️ Création des tâches Celery...", Colors.YELLOW)
    
    content = '''"""
apps/payments/tasks.py
Tâches asynchrones pour les paiements
"""
from celery import shared_task
from asgiref.sync import async_to_sync
import logging
from datetime import datetime, timedelta

from apps.payments.subscriptions.services import SubscriptionService
from apps.payments.billing.services import InvoiceService
from apps.payments.gateways.services import PaymentService

logger = logging.getLogger(__name__)


@shared_task(name='payments.check_expired_subscriptions')
def check_expired_subscriptions():
    """Vérifier et désactiver les abonnements expirés"""
    try:
        service = SubscriptionService()
        count = async_to_sync(service.check_and_expire_subscriptions)()
        logger.info(f"Expired {count} subscriptions")
        return {'expired': count}
    except Exception as e:
        logger.error(f"Error checking expired subscriptions: {str(e)}")
        raise


@shared_task(name='payments.process_subscription_renewals')
def process_subscription_renewals():
    """Traiter les renouvellements d'abonnements"""
    try:
        subscription_service = SubscriptionService()
        payment_service = PaymentService()
        
        subscriptions = async_to_sync(
            subscription_service.get_subscriptions_to_renew
        )()
        
        renewed_count = 0
        failed_count = 0
        
        for subscription in subscriptions:
            try:
                payment = async_to_sync(payment_service.create_payment)(
                    student_id=subscription.studentId,
                    amount=subscription.price,
                    currency=subscription.currency,
                    method=subscription.paymentMethod,
                    subscription_id=subscription.id,
                    description=f"Subscription renewal - {subscription.type}"
                )
                
                async_to_sync(payment_service.process_payment)(
                    payment.id,
                    'STRIPE'
                )
                
                renewed_count += 1
                logger.info(f"Renewed subscription: {subscription.id}")
                
            except Exception as e:
                failed_count += 1
                logger.error(f"Failed to renew subscription {subscription.id}: {str(e)}")
        
        return {
            'processed': len(subscriptions),
            'renewed': renewed_count,
            'failed': failed_count
        }
        
    except Exception as e:
        logger.error(f"Error processing renewals: {str(e)}")
        raise


@shared_task(name='payments.send_overdue_invoice_reminders')
def send_overdue_invoice_reminders():
    """Envoyer des rappels pour les factures en retard"""
    try:
        service = InvoiceService()
        overdue_invoices = async_to_sync(service.get_overdue_invoices)()
        
        reminder_count = 0
        for invoice in overdue_invoices:
            logger.info(f"Reminder needed for invoice: {invoice.invoiceNumber}")
            reminder_count += 1
        
        return {'reminders_sent': reminder_count}
        
    except Exception as e:
        logger.error(f"Error sending reminders: {str(e)}")
        raise


@shared_task(name='payments.generate_payment_reports')
def generate_payment_reports():
    """Générer des rapports de paiements mensuels"""
    try:
        service = PaymentService()
        
        start_date = datetime.now().replace(day=1) - timedelta(days=1)
        start_date = start_date.replace(day=1)
        end_date = datetime.now().replace(day=1)
        
        stats = async_to_sync(service.get_payment_statistics)(
            start_date=start_date,
            end_date=end_date
        )
        
        logger.info(f"Monthly report generated: {stats}")
        return stats
        
    except Exception as e:
        logger.error(f"Error generating reports: {str(e)}")
        raise
'''
    
    file_path = base_dir / "apps/payments/tasks.py"
    file_path.write_text(content)
    print(f"  ✓ apps/payments/tasks.py")
    print_color("✓ Tâches Celery créées\n", Colors.GREEN)

def create_celery_config(base_dir: Path):
    """Créer la configuration Celery"""
    print_color("⚙️ Configuration Celery...", Colors.YELLOW)
    
    content = '''"""
config/celery.py
Configuration Celery pour le service de paiements
"""
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

app = Celery('payments_service')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Configuration des tâches périodiques
app.conf.beat_schedule = {
    'check-expired-subscriptions': {
        'task': 'payments.check_expired_subscriptions',
        'schedule': crontab(hour=2, minute=0),
    },
    'process-subscription-renewals': {
        'task': 'payments.process_subscription_renewals',
        'schedule': crontab(hour=3, minute=0),
    },
    'send-overdue-invoice-reminders': {
        'task': 'payments.send_overdue_invoice_reminders',
        'schedule': crontab(hour=9, minute=0),
    },
    'generate-payment-reports': {
        'task': 'payments.generate_payment_reports',
        'schedule': crontab(hour=6, minute=0, day_of_month=1),
    },
}

app.conf.task_routes = {
    'payments.*': {'queue': 'payments'},
}

app.conf.task_time_limit = 600
app.conf.task_soft_time_limit = 540

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
'''
    
    file_path = base_dir / "config/celery.py"
    file_path.write_text(content)
    print(f"  ✓ config/celery.py")
    
    # Modifier config/__init__.py
    init_content = '''from .celery import app as celery_app

__all__ = ('celery_app',)
'''
    
    init_path = base_dir / "config/__init__.py"
    init_path.write_text(init_content)
    print(f"  ✓ config/__init__.py")
    
    print_color("✓ Configuration Celery créée\n", Colors.GREEN)

def update_payments_urls(base_dir: Path):
    """Mettre à jour les URLs principales"""
    print_color("🔗 Mise à jour des URLs...", Colors.YELLOW)
    
    content = '''from django.urls import path, include

app_name = 'payments'

urlpatterns = [
    path('payments/', include('apps.payments.payments.urls')),
    path('invoices/', include('apps.payments.billing.urls')),
    path('subscriptions/', include('apps.payments.subscriptions.urls')),
    path('webhooks/', include('apps.payments.webhooks.urls')),
]
'''
    
    file_path = base_dir / "apps/payments/urls.py"
    file_path.write_text(content)
    print(f"  ✓ apps/payments/urls.py")
    print_color("✓ URLs mises à jour\n", Colors.GREEN)

def update_requirements(base_dir: Path):
    """Mettre à jour requirements.txt"""
    print_color("📦 Mise à jour des dépendances...", Colors.YELLOW)
    
    content = '''# Django
Django==5.0.1
djangorestframework==3.14.0
djangorestframework-simplejwt==5.3.1
django-cors-headers==4.3.1
django-filter==23.5
django-extensions==3.2.3

# Database
psycopg2-binary==2.9.9
prisma==0.11.0

# Cache & Queue
redis==5.0.1
celery==5.3.4
django-redis==5.4.0
django-celery-beat==2.5.0

# Payment Gateways
stripe==7.8.0
paypalrestsdk==1.13.1

# Auth & Security
PyJWT==2.8.0
cryptography==41.0.7

# Utils
python-decouple==3.8
requests==2.31.0
python-dateutil==2.8.2

# Server
gunicorn==21.2.0
uvicorn[standard]==0.25.0
whitenoise==6.6.0

# Testing
pytest==7.4.3
pytest-django==4.7.0
pytest-asyncio==0.23.2
pytest-cov==4.1.0
factory-boy==3.3.0

# PDF Generation
reportlab==4.0.7

# Monitoring
sentry-sdk==1.39.1
'''
    
    file_path = base_dir / "requirements.txt"
    file_path.write_text(content)
    print(f"  ✓ requirements.txt")
    print_color("✓ Dépendances mises à jour\n", Colors.GREEN)

def update_docker_compose(base_dir: Path):
    """Mettre à jour docker-compose.yml"""
    print_color("🐳 Mise à jour Docker Compose...", Colors.YELLOW)
    
    content = '''services:
  payments-postgres:
    image: postgres:15
    container_name: payments_postgres
    restart: always
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: rene
      POSTGRES_DB: payments_db
    ports:
      - "5434:5432"
    volumes:
      - payments_postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d payments_db"]
      interval: 10s
      timeout: 5s
      retries: 5

  payments-redis:
    image: redis:7-alpine
    container_name: payments_redis
    restart: always
    ports:
      - "6381:6379"
    volumes:
      - payments_redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  payments-service:
    build: .
    container_name: payments_service
    volumes:
      - .:/app
      - payments_logs:/app/logs
    ports:
      - "8003:8003"
    depends_on:
      payments-postgres:
        condition: service_healthy
      payments-redis:
        condition: service_healthy
    environment:
      DEBUG: "True"
      SECRET_KEY: "votre-secret-key-payments-service-super-securisee-ici"
      POSTGRES_HOST: "payments-postgres"
      POSTGRES_DB: "payments_db"
      POSTGRES_USER: "postgres"
      POSTGRES_PASSWORD: "rene"
      POSTGRES_PORT: "5432"
      DATABASE_URL: "postgresql://postgres:rene@payments-postgres:5432/payments_db"
      REDIS_URL: "redis://payments-redis:6379/0"
      CELERY_BROKER_URL: "redis://payments-redis:6379/1"
      CELERY_RESULT_BACKEND: "redis://payments-redis:6379/1"
      ALLOWED_HOSTS: "localhost,127.0.0.1,0.0.0.0,backend,payments-service"
      DJANGO_SETTINGS_MODULE: "config.settings.development"
      LOG_LEVEL: "INFO"
      STRIPE_SECRET_KEY: "${STRIPE_SECRET_KEY:-sk_test_your_key}"
      STRIPE_PUBLISHABLE_KEY: "${STRIPE_PUBLISHABLE_KEY:-pk_test_your_key}"
      STRIPE_WEBHOOK_SECRET: "${STRIPE_WEBHOOK_SECRET:-whsec_your_secret}"
      PAYPAL_CLIENT_ID: "${PAYPAL_CLIENT_ID:-your_client_id}"
      PAYPAL_CLIENT_SECRET: "${PAYPAL_CLIENT_SECRET:-your_secret}"
      PAYPAL_MODE: "sandbox"
      DEFAULT_CURRENCY: "USD"
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:8003/api/payments/health/ || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  payments-celery-worker:
    build: .
    container_name: payments_celery_worker
    command: celery -A config worker --loglevel=info --concurrency=4 -Q payments
    volumes:
      - .:/app
      - payments_logs:/app/logs
    depends_on:
      - payments-redis
      - payments-postgres
      - payments-service
    environment:
      DEBUG: "True"
      SECRET_KEY: "votre-secret-key-payments-service-super-securisee-ici"
      DATABASE_URL: "postgresql://postgres:rene@payments-postgres:5432/payments_db"
      REDIS_URL: "redis://payments-redis:6379/0"
      CELERY_BROKER_URL: "redis://payments-redis:6379/1"
      CELERY_RESULT_BACKEND: "redis://payments-redis:6379/1"
      DJANGO_SETTINGS_MODULE: "config.settings.development"

  payments-celery-beat:
    build: .
    container_name: payments_celery_beat
    command: celery -A config beat --loglevel=info
    volumes:
      - .:/app
      - payments_logs:/app/logs
    depends_on:
      - payments-redis
      - payments-postgres
      - payments-service
    environment:
      DEBUG: "True"
      SECRET_KEY: "votre-secret-key-payments-service-super-securisee-ici"
      DATABASE_URL: "postgresql://postgres:rene@payments-postgres:5432/payments_db"
      REDIS_URL: "redis://payments-redis:6379/0"
      CELERY_BROKER_URL: "redis://payments-redis:6379/1"
      CELERY_RESULT_BACKEND: "redis://payments-redis:6379/1"
      DJANGO_SETTINGS_MODULE: "config.settings.development"

volumes:
  payments_postgres_data:
  payments_redis_data:
  payments_logs:
'''
    
    file_path = base_dir / "docker-compose.yml"
    file_path.write_text(content)
    print(f"  ✓ docker-compose.yml")
    print_color("✓ Docker Compose mis à jour\n", Colors.GREEN)

def update_settings(base_dir: Path):
    """Mettre à jour les settings Django"""
    print_color("⚙️ Mise à jour des settings...", Colors.YELLOW)
    
    settings_file = base_dir / "config/settings/base.py"
    
    if settings_file.exists():
        content = settings_file.read_text()
        
        # Vérifier si django_celery_beat est déjà présent
        if 'django_celery_beat' not in content:
            # Ajouter après "# Third party"
            content = content.replace(
                "# Third party",
                "# Third party\n    'django_celery_beat',"
            )
            settings_file.write_text(content)
            print(f"  ✓ Ajout de django_celery_beat aux INSTALLED_APPS")
        else:
            print(f"  ℹ django_celery_beat déjà présent")
    
    print_color("✓ Settings mis à jour\n", Colors.GREEN)

def create_env_example(base_dir: Path):
    """Créer le fichier .env.example"""
    print_color("📝 Création de .env.example...", Colors.YELLOW)
    
    content = '''# Django
DEBUG=True
SECRET_KEY=your-secret-key-here
DJANGO_SETTINGS_MODULE=config.settings.development
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://postgres:postgres@payments-postgres:5432/payments_db
POSTGRES_HOST=payments-postgres
POSTGRES_DB=payments_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_PORT=5432

# Redis & Celery
REDIS_URL=redis://payments-redis:6379/0
CELERY_BROKER_URL=redis://payments-redis:6379/1
CELERY_RESULT_BACKEND=redis://payments-redis:6379/1

# Stripe
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
STRIPE_WEBHOOK_SECRET=whsec_your_stripe_webhook_secret

# PayPal
PAYPAL_CLIENT_ID=your_paypal_client_id
PAYPAL_CLIENT_SECRET=your_paypal_secret
PAYPAL_MODE=sandbox

# Service Configuration
SERVICE_PORT=8003
LOG_LEVEL=INFO
DEFAULT_CURRENCY=USD
SUPPORTED_CURRENCIES=USD,EUR,GBP,CAD,AUD

# Monitoring (Optional)
SENTRY_DSN=

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
'''
    
    file_path = base_dir / ".env.example"
    file_path.write_text(content)
    print(f"  ✓ .env.example")
    print_color("✓ .env.example créé\n", Colors.GREEN)

def create_makefile(base_dir: Path):
    """Créer un Makefile"""
    print_color("🛠️ Création du Makefile...", Colors.YELLOW)
    
    content = '''.PHONY: help install migrate test run docker-up docker-down docker-logs

help:
\t@echo "Commandes disponibles:"
\t@echo "  make install          - Installer les dépendances"
\t@echo "  make migrate          - Appliquer les migrations"
\t@echo "  make test             - Lancer les tests"
\t@echo "  make run              - Lancer le serveur de développement"
\t@echo "  make docker-up        - Démarrer les services Docker"
\t@echo "  make docker-down      - Arrêter les services Docker"
\t@echo "  make docker-logs      - Voir les logs Docker"
\t@echo "  make prisma-generate  - Générer le client Prisma"
\t@echo "  make celery-worker    - Lancer le worker Celery"

install:
\tpip install -r requirements.txt

migrate:
\tpython manage.py migrate

prisma-generate:
\tprisma generate

prisma-migrate:
\tprisma migrate dev

test:
\tpytest

run:
\tpython manage.py runserver 8003

docker-up:
\tdocker-compose up -d

docker-down:
\tdocker-compose down

docker-logs:
\tdocker-compose logs -f

celery-worker:
\tcelery -A config worker --loglevel=info -Q payments
'''
    
    file_path = base_dir / "Makefile"
    file_path.write_text(content)
    print(f"  ✓ Makefile")
    print_color("✓ Makefile créé\n", Colors.GREEN)

def create_readme_update(base_dir: Path):
    """Créer un fichier avec les instructions de mise à jour"""
    print_color("📚 Création des instructions...", Colors.YELLOW)
    
    content = '''# Instructions de Mise à Jour

## ✅ Corrections Appliquées

1. ✓ Module webhooks créé (Stripe & PayPal)
2. ✓ Tâches Celery configurées
3. ✓ Configuration Celery complète
4. ✓ URLs mises à jour
5. ✓ Requirements.txt complété
6. ✓ Docker Compose avec Celery worker et beat
7. ✓ Settings Django mis à jour
8. ✓ Fichier .env.example créé
9. ✓ Makefile ajouté

## 📋 Prochaines Étapes

### 1. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 2. Générer le client Prisma
```bash
prisma generate
```

### 3. Créer les migrations Prisma
```bash
prisma migrate dev --name init
```

### 4. Appliquer les migrations Django
```bash
python manage.py migrate
```

### 5. Configurer les variables d'environnement
Copier `.env.example` vers `.env` et remplir avec vos vraies clés:
```bash
cp .env.example .env
# Éditer .env avec vos clés Stripe/PayPal
```

### 6. Lancer avec Docker
```bash
docker-compose up -d
```

### 7. Vérifier les services
- Service principal: http://localhost:8003/api/payments/health/
- PostgreSQL: localhost:5434
- Redis: localhost:6381

## 🔧 Commandes Utiles

### Développement local
```bash
make install          # Installer les dépendances
make run              # Lancer le serveur
make test             # Lancer les tests
```

### Docker
```bash
make docker-up        # Démarrer les services
make docker-down      # Arrêter les services
make docker-logs      # Voir les logs
```

### Prisma
```bash
make prisma-generate  # Générer le client
prisma migrate dev    # Créer une migration
prisma studio         # Interface graphique
```

### Celery
```bash
make celery-worker    # Lancer le worker
celery -A config beat # Lancer le scheduler
```

## 🧪 Tests

### Tester les webhooks localement

**Stripe:**
```bash
# Installer Stripe CLI
stripe listen --forward-to localhost:8003/api/webhooks/stripe/

# Déclencher un événement test
stripe trigger payment_intent.succeeded
```

**PayPal:**
Utiliser le simulateur IPN de PayPal Sandbox

### Tester les paiements

```python
import requests

# Créer un paiement
response = requests.post(
    'http://localhost:8003/api/payments/',
    json={
        'student_id': 'uuid-here',
        'amount': 99.99,
        'currency': 'USD',
        'method': 'STRIPE',
        'gateway': 'STRIPE'
    },
    headers={'Authorization': 'Bearer YOUR_TOKEN'}
)
```

## ⚠️ Points d'Attention

1. **Clés API**: Remplacer les clés de test dans `.env`
2. **Webhooks**: Configurer les URLs dans les dashboards Stripe/PayPal
3. **Email**: Intégrer un service d'email pour les rappels
4. **PDF**: Implémenter la génération de PDF pour les factures
5. **Tests**: Ajouter plus de tests unitaires et d'intégration
6. **Monitoring**: Configurer Sentry en production

## 📊 Architecture

```
payments-service/
├── apps/
│   └── payments/
│       ├── billing/          # Gestion des factures
│       ├── gateways/         # Passerelles de paiement
│       ├── payments/         # Gestion des paiements
│       ├── subscriptions/    # Gestion des abonnements
│       ├── webhooks/         # Webhooks Stripe/PayPal ✨ NOUVEAU
│       └── tasks.py          # Tâches Celery ✨ NOUVEAU
├── config/
│   ├── celery.py            # Configuration Celery ✨ NOUVEAU
│   └── settings/
└── prisma/
    └── schema.prisma
```

## 🚀 Déploiement

### Production
1. Définir `DJANGO_ENV=production`
2. Configurer les variables d'environnement de production
3. Utiliser `gunicorn` au lieu de `runserver`
4. Activer HTTPS
5. Configurer un reverse proxy (Nginx)
6. Activer Sentry pour le monitoring

### Variables d'environnement production
```bash
DEBUG=False
ALLOWED_HOSTS=your-domain.com
CORS_ALLOWED_ORIGINS=https://your-frontend.com
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
SENTRY_DSN=https://...
```

## 📝 Notes

- Les webhooks nécessitent HTTPS en production
- Les tâches Celery s'exécutent automatiquement selon le schedule
- Les migrations Prisma sont automatiques au démarrage du conteneur
- Les logs sont dans le dossier `logs/`
'''
    
    file_path = base_dir / "UPDATE_INSTRUCTIONS.md"
    file_path.write_text(content)
    print(f"  ✓ UPDATE_INSTRUCTIONS.md")
    print_color("✓ Instructions créées\n", Colors.GREEN)

def print_summary():
    """Afficher le résumé des corrections"""
    print_color("\n" + "="*60, Colors.BLUE)
    print_color("✅ CORRECTIONS TERMINÉES", Colors.GREEN)
    print_color("="*60 + "\n", Colors.BLUE)
    
    print_color("📦 Fichiers créés/modifiés:", Colors.YELLOW)
    files_created = [
        "✓ apps/payments/webhooks/views.py",
        "✓ apps/payments/webhooks/urls.py",
        "✓ apps/payments/webhooks/__init__.py",
        "✓ apps/payments/tasks.py",
        "✓ config/celery.py",
        "✓ config/__init__.py (modifié)",
        "✓ apps/payments/urls.py (modifié)",
        "✓ requirements.txt (mis à jour)",
        "✓ docker-compose.yml (mis à jour)",
        "✓ config/settings/base.py (mis à jour)",
        "✓ .env.example",
        "✓ Makefile",
        "✓ UPDATE_INSTRUCTIONS.md",
    ]
    
    for file in files_created:
        print(f"  {file}")
    
    print_color("\n📋 Prochaines étapes:", Colors.YELLOW)
    next_steps = [
        "1. Lire UPDATE_INSTRUCTIONS.md pour les détails",
        "2. Installer les dépendances: pip install -r requirements.txt",
        "3. Générer Prisma: prisma generate",
        "4. Créer migrations: prisma migrate dev --name init",
        "5. Configurer .env avec vos clés API",
        "6. Lancer: docker-compose up -d",
        "7. Tester: http://localhost:8003/api/payments/health/",
    ]
    
    for step in next_steps:
        print(f"  {step}")
    
    print_color("\n" + "="*60, Colors.BLUE)
    print_color("🎉 Service de paiement prêt à l'emploi!", Colors.GREEN)
    print_color("="*60 + "\n", Colors.BLUE)

def main():
    """Fonction principale"""
    try:
        print_color("\n" + "="*60, Colors.BLUE)
        print_color("🔧 SCRIPT DE CORRECTION - PAYMENTS SERVICE", Colors.BLUE)
        print_color("="*60 + "\n", Colors.BLUE)
        
        # 1. Vérifier le répertoire
        base_dir = check_directory()
        
        # 2. Créer les répertoires
        create_directories(base_dir)
        
        # 3. Créer les fichiers __init__.py
        create_init_files(base_dir)
        
        # 4. Créer le module webhooks
        create_webhooks_views(base_dir)
        create_webhooks_urls(base_dir)
        
        # 5. Créer les tâches Celery
        create_celery_tasks(base_dir)
        create_celery_config(base_dir)
        
        # 6. Mettre à jour les URLs
        update_payments_urls(base_dir)
        
        # 7. Mettre à jour les dépendances
        update_requirements(base_dir)
        
        # 8. Mettre à jour Docker Compose
        update_docker_compose(base_dir)
        
        # 9. Mettre à jour les settings
        update_settings(base_dir)
        
        # 10. Créer .env.example
        create_env_example(base_dir)
        
        # 11. Créer Makefile
        create_makefile(base_dir)
        
        # 12. Créer les instructions
        create_readme_update(base_dir)
        
        # 13. Afficher le résumé
        print_summary()
        
        return 0
        
    except Exception as e:
        print_color(f"\n❌ Erreur: {str(e)}", Colors.RED)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())