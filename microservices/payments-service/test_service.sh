#!/bin/bash
set -e

echo "🧪 TESTS DU PAYMENT SERVICE"
echo "======================================"

BASE_URL="http://localhost:8006"

echo -e "\n1️⃣  Health Check..."
curl -s "$BASE_URL/health" | jq '.' || echo "Service non démarré"

echo -e "\n2️⃣  Actuator Health..."
curl -s "$BASE_URL/actuator/health" | jq '.' || echo "Actuator non accessible"

echo -e "\n3️⃣  Swagger UI..."
curl -s -o /dev/null -w "Status: %{http_code}\n" "$BASE_URL/swagger-ui.html"

echo -e "\n======================================"
echo "✨ Tests terminés!"
echo "📚 Swagger UI: $BASE_URL/swagger-ui.html"
