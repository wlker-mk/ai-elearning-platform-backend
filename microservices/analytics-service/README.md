# Analytics Service - Guide Docker

## 🚀 Démarrage Rapide

### 1. Préparation

```bash
# Copier le fichier .env
cp .env.example .env

# Éditer le fichier .env avec vos configurations
nano .env
```

### 2. Construction et Lancement

```bash
# Construire les images
docker-compose build

# Démarrer les services
docker-compose up -d

# Voir les logs
docker-compose logs -f analytics-service
```

### 3. Vérification

```bash
# Vérifier que les services sont actifs
docker-compose ps

# Tester le endpoint de santé
curl http://localhost:8011/api/health/
```

## 📦 Services Inclus

### PostgreSQL
- Port: `5433` (externe) → `5432` (interne)
- Database: `analytics_db`
- User: `postgres`
- Password: `rene`

### Redis
- Port: `6380` (externe) → `6379` (interne)
- Usage: Cache + Celery broker

### Analytics Service
- Port: `8011`
- Framework: Django + Prisma
- API: REST

## 🛠️ Commandes Utiles

### Avec Make (Recommandé)

```bash
# Voir toutes les commandes disponibles
make help

# Démarrer
make up

# Voir les logs
make logs

# Shell Django
make django-shell

# Tests
make test

# Migrations
make migrate

# Reset complet
make reset
```

### Sans Make

```bash
# Démarrer
docker-compose up -d

# Arrêter
docker-compose down

# Logs
docker-compose logs -f

# Shell
docker-compose exec analytics-service bash

# Migrations Django
docker-compose exec analytics-service python manage.py migrate

# Migrations Prisma
docker-compose exec analytics-service prisma migrate deploy

# Tests
docker-compose exec analytics-service pytest
```

## 🔧 Configuration

### Variables d'Environnement Importantes

```bash
# Développement
DEBUG=True
DJANGO_ENV=development

# Production
DEBUG=False
DJANGO_ENV=production
SECRET_KEY=<generate-secure-key>
```

### Génération de SECRET_KEY

```python
# Dans le shell Django
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

## 📊 Prisma

### Workflow

```bash
# 1. Modifier le schema
nano prisma/schema.prisma

# 2. Créer une migration
docker-compose exec analytics-service prisma migrate dev --name nom_migration

# 3. Générer le client
docker-compose exec analytics-service prisma generate

# 4. Appliquer en production
docker-compose exec analytics-service prisma migrate deploy
```

### Prisma Studio

```bash
# Ouvrir l'interface graphique
docker-compose exec analytics-service prisma studio
# Accéder à: http://localhost:5555
```

## 🧪 Tests

```bash
# Tous les tests
make test

# Avec couverture
make test-coverage

# Tests spécifiques
docker-compose exec analytics-service pytest apps/analytics/tests/test_course_views.py

# Mode verbose
docker-compose exec analytics-service pytest -v
```

## 📝 Logs

### Localisation des Logs

- Application: `./logs/app.log`
- Accès: `./logs/access.log` (production)
- Erreurs: `./logs/error.log` (production)
- Docker: `docker-compose logs`

### Commandes Logs

```bash
# Logs en temps réel
docker-compose logs -f analytics-service

# Dernières 100 lignes
docker-compose logs --tail=100 analytics-service

# Tous les services
docker-compose logs -f
```

## 🔒 Sécurité

### Checklist Production

- [ ] Changer `SECRET_KEY` (50+ caractères)
- [ ] `DEBUG=False`
- [ ] Configurer `ALLOWED_HOSTS`
- [ ] Activer SSL/HTTPS
- [ ] Configurer CORS correctement
- [ ] Utiliser des mots de passe forts
- [ ] Configurer Sentry pour le monitoring
- [ ] Backup réguliers de la base de données

## 🐛 Troubleshooting

### Service ne démarre pas

```bash
# Vérifier les logs
docker-compose logs analytics-service

# Vérifier la santé
docker-compose ps

# Redémarrer proprement
docker-compose down
docker-compose up -d
```

### PostgreSQL n'est pas prêt

```bash
# Vérifier la santé de PostgreSQL
docker-compose exec postgres pg_isready -U postgres

# Voir les logs PostgreSQL
docker-compose logs postgres
```

### Erreur de migration

```bash
# Réinitialiser les migrations (ATTENTION: perte de données)
docker-compose down -v
docker-compose up -d
docker-compose exec analytics-service python manage.py migrate
```

### Prisma Client non généré

```bash
# Régénérer le client
docker-compose exec analytics-service prisma generate
docker-compose restart analytics-service
```

## 📦 Backup & Restore

### Backup

```bash
# Base de données
make db-backup

# Ou manuellement
docker-compose exec postgres pg_dump -U postgres analytics_db > backup.sql
```

### Restore

```bash
# Depuis un fichier
make db-restore file=backup.sql

# Ou manuellement
docker-compose exec -T postgres psql -U postgres analytics_db < backup.sql
```

## 🚀 Déploiement

### Production avec Docker

```bash
# 1. Configurer l'environnement
export DJANGO_ENV=production
export DEBUG=False

# 2. Build optimisé
docker-compose -f docker-compose.prod.yml build

# 3. Lancer
docker-compose -f docker-compose.prod.yml up -d

# 4. Vérifier
curl https://your-domain.com/api/health/
```

## 📚 Ressources

- [Django Documentation](https://docs.djangoproject.com/)
- [Prisma Documentation](https://www.prisma.io/docs/)
- [Docker Documentation](https://docs.docker.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

## 🤝 Support

En cas de problème:
1. Vérifier les logs: `make logs`
2. Vérifier la santé: `make ps`
3. Consulter la documentation
4. Ouvrir une issue sur GitHub

# Installation
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configuration
cp .env.example .env
# Éditer .env

# Base de données
prisma generate
prisma migrate deploy
python manage.py migrate

# Lancement
python manage.py runserver 8001

# Avec Docker
docker-compose up -d
```

### 📡 Endpoints principaux :
```
# Course Views
POST   /api/analytics/course-views/track/
GET    /api/analytics/course-views/stats/{course_id}/

# Video Analytics
POST   /api/analytics/video/watch-time/
POST   /api/analytics/video/completion/
POST   /api/analytics/video/event/
GET    /api/analytics/video/engagement/{lesson_id}/

# Search Logs
POST   /api/analytics/search/log/
GET    /api/analytics/search/popular/
GET    /api/analytics/search/zero-results/
GET    /api/analytics/search/trends/

# User Activity
POST   /api/analytics/activity/track/
GET    /api/analytics/activity/history/{user_id}/
GET    /api/analytics/activity/stats/{user_id}/

# Revenue
POST   /api/analytics/revenue/report/
GET    /api/analytics/revenue/daily/
GET    /api/analytics/revenue/monthly/

# Course Analytics
POST   /api/analytics/course/analytics/
GET    /api/analytics/course/stats/{course_id}/
GET    /api/analytics/course/top/