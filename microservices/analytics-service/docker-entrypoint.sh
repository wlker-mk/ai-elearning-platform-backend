#!/bin/bash
set -e

echo "🚀 Starting Analytics Service..."

# Création du dossier logs
mkdir -p /app/logs

# Configuration PostgreSQL
POSTGRES_HOST="${POSTGRES_HOST:-postgres}"
POSTGRES_USER="${POSTGRES_USER:-postgres}"
POSTGRES_DB="${POSTGRES_DB:-analytics_db}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-rene}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"

# Fonction d'attente PostgreSQL
wait_for_postgres() {
    echo "⏳ Waiting for PostgreSQL at ${POSTGRES_HOST}:${POSTGRES_PORT}..."
    
    max_attempts=30
    attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q' 2>/dev/null; then
            echo "✅ PostgreSQL is ready!"
            return 0
        fi
        
        attempt=$((attempt + 1))
        echo "📊 Attempt $attempt/$max_attempts - PostgreSQL not ready yet..."
        sleep 2
    done
    
    echo "❌ PostgreSQL connection timeout!"
    exit 1
}

# Attendre PostgreSQL
wait_for_postgres

# Générer le client Prisma
echo "🔧 Generating Prisma client..."
prisma generate

# Appliquer les migrations Prisma
echo "📋 Applying Prisma migrations..."
prisma migrate deploy || echo "⚠️ Prisma migrations failed (may already be applied)"

# Appliquer les migrations Django
echo "📋 Applying Django migrations..."
python manage.py migrate --noinput

# Collecter les fichiers statiques (production)
if [ "$DEBUG" = "False" ]; then
    echo "📦 Collecting static files..."
    python manage.py collectstatic --noinput
fi

# Créer un superuser si nécessaire (optionnel)
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "👤 Creating superuser..."
    python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists():
    User.objects.create_superuser('$DJANGO_SUPERUSER_USERNAME', '$DJANGO_SUPERUSER_EMAIL', '$DJANGO_SUPERUSER_PASSWORD')
    print('Superuser created')
else:
    print('Superuser already exists')
EOF
fi

# Seeding (optionnel)
if [ "$RUN_SEED" = "true" ]; then
    echo "🌱 Seeding database..."
    python prisma/seed.py || echo "⚠️ Seeding failed (may already be done)"
fi

# Démarrer le serveur
echo "🎯 Starting Django server on 0.0.0.0:8011..."
if [ "$DEBUG" = "True" ]; then
    exec python manage.py runserver 0.0.0.0:8011
else
    exec gunicorn config.wsgi:application \
        --bind 0.0.0.0:8011 \
        --workers 4 \
        --threads 2 \
        --timeout 120 \
        --access-logfile /app/logs/access.log \
        --error-logfile /app/logs/error.log \
        --log-level info
fi