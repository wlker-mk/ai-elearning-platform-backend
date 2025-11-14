#!/bin/bash
set -e

echo "🚀 Starting payments-service..."

# Wait for PostgreSQL
echo "⏳ Waiting for PostgreSQL..."
while ! pg_isready -h postgres -p 5432 > /dev/null 2> /dev/null; do
    echo "Waiting for PostgreSQL..."
    sleep 1
done

echo "✅ PostgreSQL is ready!"

echo "🔄 Generating Prisma Client..."
prisma generate

echo "🔄 Running Prisma migrations..."
prisma migrate deploy

echo "🔄 Running Django migrations..."
python manage.py migrate --noinput

echo "✅ payments-service is ready!"

exec "$@"
