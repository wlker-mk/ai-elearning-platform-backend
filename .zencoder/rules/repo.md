---
description: Repository Information Overview
alwaysApply: true
---

# Repository Information Overview

## Repository Summary
Plateforme d'e-learning modulaire orchestrant vingt et un microservices Django 5.0 connectés via RabbitMQ, Redis et PostgreSQL, empaquetés avec Docker Compose pour couvrir authentification, gestion des utilisateurs, cours, paiements, analytics et intégrations IA.

## Repository Structure
- **microservices/**: vingt et un services Python isolés avec configuration Django, Prisma et Docker.
- **docker/**: images personnalisées pour nginx, postgres et redis, plus configuration d'entrée.
- **scripts/**: automatisations Bash/Python pour déploiement, sauvegarde, migrations et vérification de santé.
- **tests/**: arborescences unit, integration et e2e (squelettes prêts pour pytest).
- **docs/**: documentation API et guides d'opérations (actuellement placeholders vides dans certains sous-dossiers).
- **k8s/** & **infrastructure/** & **terraform/**: emplacements réservés pour manifestes IAAS/PAAS futurs.
- **shared/** & **celery_app/**: dossiers partagés et hooks asynchrones (actuellement vides côté racine).
- **static/** & **media/** & **logs/**: assets statiques, fichiers utilisateurs et stockage de logs montés dans les conteneurs.
- **.github/workflows/**: pipeline CI/CD placeholder sans fichiers .yml.

### Main Repository Components
- **docker-compose.yml**: définit l'infrastructure réseau bridge `elearning-network`, volumes persistants et les 21 services applicatifs.
- **Makefile**: raccourcis pour build, up/down, logs, tests, migrations, backup et health check.
- **requirements.txt**: paquetages Python partagés (Django 5.0.1, DRF, Celery, Prisma Client, psycopg2, Redis, Sentry, Stripe, outils QA).
- **pytest.ini**: configuration Pytest pour testpaths `tests`, markers unit/integration/e2e, coverage et module `config.settings.base`.
- **.env.example**: variables d'environnement couvrant DB/Redis/RabbitMQ/Elasticsearch, secrets JWT, clés AWS/Stripe et Sentry.
- **scripts/*.sh**: automatisations orchestrant Docker Compose et Prisma.
- **scripts/health_check.py**: vérification HTTP `/api/health/` sur ports 8001–8021.

## Projects

### Python Microservices Platform
**Configuration Files**: `docker-compose.yml`, `microservices/*/Dockerfile`, `microservices/*/requirements.txt`, `microservices/*/config/config/settings/*.py`, `microservices/*/prisma/schema.prisma`

#### Language & Runtime
**Language**: Python 3.11 (images `python:3.11-slim` dans chaque Dockerfile).
**Runtime**: Django 5.0 + Django REST Framework avec Prisma Client Python pour accès PostgreSQL.
**Build System**: Gestion Django (`manage.py`) complétée par Prisma migrations et Gunicorn en production.
**Package Manager**: pip via `requirements.txt` par microservice et dépendances partagées racine.

#### Dependencies
**Main Dependencies**:
- Django 5.0.1, djangorestframework 3.14.0, django-cors-headers, django-filter pour API REST.
- Prisma 0.11.0 + psycopg2-binary pour base de données relationnelle.
- Celery 5.3.4, django-celery-beat/results avec RabbitMQ et Redis.
- Boto3 & django-storages pour stockage S3, Stripe SDK pour paiements, prometheus-client & sentry-sdk pour observabilité.
- Requests, python-decouple, python-dotenv, Pillow, drf-spectacular pour utilitaires et documentation.
**Development Dependencies**:
- pytest 7.4.4, pytest-django, pytest-cov, factory-boy.
- black 23.12.1, flake8 7.0.0, isort 5.13.2 pour qualité de code.

#### Build & Installation
```bash
cp .env.example .env
make build
make up
./scripts/migrate_all.sh
make ps
```

#### Docker
- **Images**: Chaque service construit depuis son dossier via `Dockerfile` (Python 3.11 slim, installation gcc & client PostgreSQL, pip install, entrypoint Gunicorn).
- **Entry Scripts**: `docker-entrypoint.sh` exécute `pg_isready`, `prisma generate`, `prisma migrate deploy`, `python manage.py migrate`, puis lance Gunicorn sur le port dédié.
- **Infrastructure Services**: Postgres 15-alpine (script SQL créant toutes les bases), Redis 7-alpine (config LRU), RabbitMQ management, Elasticsearch 8.11.0, Nginx reverse proxy.
- **Volumes**: `postgres_data`, `redis_data`, `rabbitmq_data`, `elasticsearch_data`, plus montage `./logs:/app/logs` dans chaque conteneur applicatif.

#### Testing
- **Framework**: Pytest avec support Django (`pytest.ini`).
- **Test Locations**: `tests/unit`, `tests/integration`, `tests/e2e` (squelettes) et `microservices/*/apps/**/tests/` pour tests spécifiques aux apps (ex. `microservices/auth-service/apps/authentication/tests/`).
- **Markers**: `unit`, `integration`, `e2e` configurés dans pytest.ini.
- **Commands**: `pytest tests/unit`, `pytest tests/integration`, `make test` (équivaut à `pytest tests/`).

#### Service Matrix
| Service | Port | Directory | Main Entry | Notes |
|---------|------|-----------|------------|-------|
| auth-service | 8001 | `microservices/auth-service/` | `config.wsgi` (Gunicorn) | Authentification JWT, Prisma schema pour utilisateurs et tokens.
| user-service | 8002 | `microservices/user-service/` | `config.wsgi` | Profils étudiants/instructeurs, tests modulaires par domaine.
| courses-service | 8003 | `microservices/courses-service/` | `config.wsgi` | Gestion cours, inscriptions, dépendances identiques.
| quizzes-service | 8004 | `microservices/quizzes-service/` | `config.wsgi` | Services d'évaluation.
| bookings-service | 8005 | `microservices/bookings-service/` | `config.wsgi` | Réservations et planning.
| payments-service | 8006 | `microservices/payments-service/` | `config.wsgi` | Intégration Stripe.
| notifications-service | 8007 | `microservices/notifications-service/` | `config.wsgi` | Notifications temps réel.
| webinars-service | 8008 | `microservices/webinars-service/` | `config.wsgi` | Gestion webinars & streaming.
| gamification-service | 8009 | `microservices/gamification-service/` | `config.wsgi` | Badges, points, leaderboards.
| chatbot-service | 8010 | `microservices/chatbot-service/` | `config.wsgi` | Intégration IA conversationnelle.
| analytics-service | 8011 | `microservices/analytics-service/` | `config.wsgi` | Agrégation métriques.
| communications-service | 8012 | `microservices/communications-service/` | `config.wsgi` | Messagerie et email.
| search-service | 8013 | `microservices/search-service/` | `config.wsgi` | Connecté à Elasticsearch 8.11.0.
| storage-service | 8014 | `microservices/storage-service/` | `config.wsgi` | Gestion fichiers & S3.
| security-service | 8015 | `microservices/security-service/` | `config.wsgi` | Surveillance sécurité, policies.
| monitoring-service | 8016 | `microservices/monitoring-service/` | `config.wsgi` | Exposition métriques Prometheus.
| ai-gateway | 8017 | `microservices/ai-gateway/` | `config.wsgi` | Orchestration modèles IA via Prisma schema spécifique.
| cache-service | 8018 | `microservices/cache-service/` | `config.wsgi` | API cache Redis.
| api-gateway | 8019 | `microservices/api-gateway/` | `config.wsgi` | Routage agrégé.
| i18n-service | 8020 | `microservices/i18n-service/` | `config.wsgi` | Localisation et traductions.
| sponsors-service | 8021 | `microservices/sponsors-service/` | `config.wsgi` | Gestion sponsors & partenariats.

#### Application Configuration
- **Settings**: `config/config/settings/base.py` par service configure `SECRET_KEY` via `decouple`, PostgreSQL driver, Redis, Celery broker et logging vers `/app/logs/app.log`.
- **Prisma Schemas**: `microservices/*/prisma/schema.prisma` définissent modèles PostgreSQL (ex. utilisateurs, sessions, tokens) et `datasource db` via `DATABASE_URL`.
- **Local Development**: `microservices/*/docker-compose.yml` expose le service avec `python manage.py runserver` connecté à PostgreSQL local et Redis local.
- **Shared Utilities**: dossiers `microservices/*/shared/shared/` contiennent middlewares, utils et authentification réutilisable.

### Infrastructure & Platform Support

#### Container Infrastructure
- **Nginx**: `docker/nginx/Dockerfile` basé sur `nginx:alpine`, configuration globale `docker/nginx/nginx.conf`, sites à placer sous `/etc/nginx/sites-enabled/` (non fournis).
- **PostgreSQL**: `docker/postgres/Dockerfile` + script `docker/postgres/init-scripts/01-create-databases.sql` générant toutes les bases par microservice.
- **Redis**: `docker/redis/Dockerfile` + `docker/redis/redis.conf` configurant mémoire 256 MB et politique `allkeys-lru`.

#### Automation & Ops
- **scripts/deploy.sh**: pipeline de déploiement Git pull → build → down → up → migrations.
- **scripts/migrate_all.sh**: exécute `prisma migrate deploy` dans chaque conteneur via `docker-compose exec`.
- **scripts/backup.sh**: sauvegardes PostgreSQL (`pg_dumpall`) et Redis (`redis-cli --rdb`).
- **scripts/health_check.py**: sonde endpoints `/api/health/` avec timeout 5s et statut agrégé.
- **Makefile**: fournit cibles `build`, `up`, `down`, `logs`, `test`, `migrate`, `shell`, `clean`, `restart`, `ps`, `backup`, `health`.

#### Configuration & Secrets
- **.env.example**: centralise URLs (DB, Redis, RabbitMQ, Elasticsearch), drapeaux Django, JWT, secrets Stripe/S3/Sentry.
- **Logs & Media**: dossiers `logs/`, `media/avatars|certificates|uploads`, `static/` pour admin et front.
- **Shared & Celery**: racine `celery_app/` (préparation pour tasks globaux) et `shared/` (composants transverses), actuellement placeholders.

#### Testing & Quality
- **pytest.ini**: active `--cov=.` avec rapports HTML et terminal, markers stricts.
- **tests/**: structure multi-niveaux prête pour coverage complet (fichiers à ajouter par domaine).
- **Microservice Tests**: chaque app métier inclut sous-domaine `tests/` (p. ex. `microservices/user-service/apps/users/profiles/tests/test_views.py`).

#### Documentation & Deployment Aids
- **README.md**: guide d'installation rapide, rappel microservices, commandes Docker/Prisma/tests.
- **docs/**: placeholders pour `api/`, `deployment/`, `development/` (contenu à compléter).
- **.github/workflows/**, `k8s/`, `terraform/`, `infrastructure/`: espaces réservés pour futures pipelines CI/CD, manifestes Kubernetes, IaC Terraform et scripts infra.
