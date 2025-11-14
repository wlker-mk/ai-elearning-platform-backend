#!/bin/bash
echo "🛠️  Setting up development environment..."
docker-compose -f docker-compose.dev.yml up -d
echo "✅ Done!"
