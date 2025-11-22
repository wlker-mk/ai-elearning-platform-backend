#!/bin/bash

# Start script for Payment Service with Docker Compose

set -e

echo "🚀 Starting Payment Service with Docker Compose..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "📝 Please update the .env file with your actual configuration before running again."
    exit 1
fi

# Load environment variables
source .env

# Validate required environment variables
required_vars=("STRIPE_SECRET_KEY" "STRIPE_PUBLISHABLE_KEY" "PAYPAL_CLIENT_ID" "PAYPAL_CLIENT_SECRET")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ] || [[ "${!var}" == *"your_"* ]]; then
        echo "❌ Please set $var in .env file"
        exit 1
    fi
done

echo "✅ Environment variables validated"

# Build and start services
echo "🐳 Building and starting containers..."
docker-compose up -d --build

echo "⏳ Waiting for services to be healthy..."

# Wait for PostgreSQL
echo "📊 Waiting for PostgreSQL..."
until docker exec payments_postgres pg_isready -U postgres > /dev/null 2>&1; do
    sleep 2
done

# Wait for Redis
echo "🔴 Waiting for Redis..."
until docker exec payments_redis redis-cli ping | grep -q "PONG"; do
    sleep 2
done

# Wait for Payment Service
echo "💳 Waiting for Payment Service..."
until curl -s http://localhost:8006/actuator/health > /dev/null; do
    sleep 5
done

echo "✅ All services are up and running!"

# Display service information
echo ""
echo "=============================================="
echo "🎉 Payment Service Started Successfully!"
echo "=============================================="
echo "📊 PostgreSQL:      localhost:5434"
echo "🔴 Redis:           localhost:6381"
echo "💳 Payment Service: http://localhost:8006"
echo "📚 Swagger UI:      http://localhost:8006/api/swagger-ui.html"
echo "🔧 Actuator Health: http://localhost:8006/actuator/health"
echo "=============================================="
echo ""