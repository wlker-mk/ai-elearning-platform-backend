@"
#!/bin/bash
set -e

echo '🚀 Starting analytics service...'

mkdir -p /app/logs

echo '⏳ Waiting for PostgreSQL...'
POSTGRES_HOST=\"${POSTGRES_HOST:-postgres}\"
POSTGRES_USER=\"${POSTGRES_USER:-postgres}\"
POSTGRES_DB=\"${POSTGRES_DB:-analytics_db}\"
POSTGRES_PASSWORD=\"${POSTGRES_PASSWORD:-rene}\"

until PGPASSWORD=\"\$POSTGRES_PASSWORD\" psql -h \"\$POSTGRES_HOST\" -U \"\$POSTGRES_USER\" -d \"\$POSTGRES_DB\" -c '\q'; do
    echo '📊 PostgreSQL not ready yet...'
    sleep 2
done
echo '✅ PostgreSQL is available'

echo '📋 Applying Django migrations...'
python manage.py migrate

echo '🎯 Starting Django server on port 8002...'
exec python manage.py runserver 0.0.0.0:8002
"@ | Out-File -FilePath "docker-entrypoint.sh" -Encoding utf8

# Donner les permissions
chmod +x docker-entrypoint.sh