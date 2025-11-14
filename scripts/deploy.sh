#!/bin/bash
set -e

echo "🚀 Deploying AI E-Learning Platform..."

# Pull latest changes
git pull origin main

# Build containers
docker-compose build

# Stop old containers
docker-compose down

# Start new containers
docker-compose up -d

# Run migrations
./scripts/migrate_all.sh

echo "✅ Deployment completed!"
