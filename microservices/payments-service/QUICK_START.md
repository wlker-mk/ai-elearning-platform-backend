# 🚀 QUICK START - 5 Minutes

## Étape 1: Démarrer les services

```bash
docker-compose up -d postgres redis
sleep 10
```

## Étape 2: Lancer l'application

```bash
mvn spring-boot:run
```

## Étape 3: Tester

```bash
./test_service.sh
```

## Étape 4: Explorer l'API

Ouvrir: http://localhost:8006/swagger-ui.html

---

**C'est tout!** Le service fonctionne en mode fake (sans vraies clés API).

Pour activer Stripe/PayPal: Éditer `.env` avec vos vraies clés.
