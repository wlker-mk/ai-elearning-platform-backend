#!/bin/bash
set -e

echo "🚀 Running Prisma migrations for all services..."


echo "📦 Migrating auth-service..."
docker-compose exec auth-service prisma migrate deploy

echo "📦 Migrating user-service..."
docker-compose exec user-service prisma migrate deploy

echo "📦 Migrating courses-service..."
docker-compose exec courses-service prisma migrate deploy

echo "📦 Migrating quizzes-service..."
docker-compose exec quizzes-service prisma migrate deploy

echo "📦 Migrating bookings-service..."
docker-compose exec bookings-service prisma migrate deploy

echo "📦 Migrating payments-service..."
docker-compose exec payments-service prisma migrate deploy

echo "📦 Migrating notifications-service..."
docker-compose exec notifications-service prisma migrate deploy

echo "📦 Migrating webinars-service..."
docker-compose exec webinars-service prisma migrate deploy

echo "📦 Migrating gamification-service..."
docker-compose exec gamification-service prisma migrate deploy

echo "📦 Migrating chatbot-service..."
docker-compose exec chatbot-service prisma migrate deploy

echo "📦 Migrating analytics-service..."
docker-compose exec analytics-service prisma migrate deploy

echo "📦 Migrating communications-service..."
docker-compose exec communications-service prisma migrate deploy

echo "📦 Migrating search-service..."
docker-compose exec search-service prisma migrate deploy

echo "📦 Migrating storage-service..."
docker-compose exec storage-service prisma migrate deploy

echo "📦 Migrating security-service..."
docker-compose exec security-service prisma migrate deploy

echo "📦 Migrating monitoring-service..."
docker-compose exec monitoring-service prisma migrate deploy

echo "📦 Migrating ai-gateway..."
docker-compose exec ai-gateway prisma migrate deploy

echo "📦 Migrating i18n-service..."
docker-compose exec i18n-service prisma migrate deploy

echo "📦 Migrating sponsors-service..."
docker-compose exec sponsors-service prisma migrate deploy

echo "✅ All migrations completed!"
