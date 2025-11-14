#!/bin/bash
set -e

echo "🚀 Starting cache-service..."

# Wait for PostgreSQL
echo "⏳ Waiting for PostgreSQL..."
while ! pg_isready -h postgres -p 5432 > /dev/null 2> /dev/null; do
    echo "Waiting for PostgreSQL..."
    sleep 1
done

echo "✅ PostgreSQL is ready!"

echo "🔄 Running Django migrations..."
python manage.py migrate --noinput

echo "✅ cache-service is ready!"

exec "$@"
