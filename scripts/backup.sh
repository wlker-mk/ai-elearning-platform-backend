#!/bin/bash
set -e

BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

echo "📦 Creating backup..."

# Backup PostgreSQL
docker-compose exec -T postgres pg_dumpall -U postgres > $BACKUP_DIR/postgres.sql

# Backup Redis
docker-compose exec -T redis redis-cli --rdb $BACKUP_DIR/redis.rdb

echo "✅ Backup completed: $BACKUP_DIR"
