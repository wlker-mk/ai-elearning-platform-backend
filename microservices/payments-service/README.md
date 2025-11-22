# Payment Service - Spring Boot

Microservice de gestion des paiements pour une plateforme LMS (Learning Management System).

## 🚀 Fonctionnalités

### 💳 Gestion des Paiements
- **Intégration Stripe**: Cartes de crédit/débit, Apple Pay, Google Pay
- **Intégration PayPal**: Paiements PayPal complets
- **Multi-devises**: Support USD, EUR, GBP, CAD, etc.
- **Frais de plateforme**: Calcul automatique des commissions
- **Remboursements**: Complets ou partiels
- **Webhooks**: Gestion asynchrone des événements

### 🔄 Abonnements
- **Types variés**: Monthly, Quarterly, Annual, Lifetime
- **Auto-renouvellement**: Renouvellement automatique géré
- **Périodes d'essai**: Support des trials
- **Annulation**: Gestion de l'annulation avec conservation

### 🎁 Codes Promo
- **Types de réduction**: Pourcentage, montant fixe
- **Limites d'utilisation**: Par code et par utilisateur
- **Validité temporelle**: Dates de début et fin
- **Validation automatique**: Vérification lors de l'application

### 📄 Facturation
- **Génération automatique**: Factures créées automatiquement
- **Export PDF**: Génération de factures PDF
- **Suivi des paiements**: État en temps réel
- **Gestion des impayés**: Rappels automatiques

## 📦 Prérequis

- Java 17+
- Maven 3.8+
- PostgreSQL 15+
- Docker & Docker Compose
- Compte Stripe (pour production)
- Compte PayPal Developer (pour production)

## 🛠️ Installation

### 1. Cloner le repository
```bash
git clone <repository-url>
cd payment-service
```

### 2. Configuration des variables d'environnement
Créer un fichier `.env` :
```bash
cp .env.example .env
# Éditer .env avec vos clés API
```

### 3. Build du projet
```bash
mvn clean install
```

### 4. Exécuter les migrations
```bash
mvn flyway:migrate
```

### 5. Lancer l'application
```bash
# En local
mvn spring-boot:run

# Avec Docker
docker-compose up -d
```

## 🔧 Configuration

### Variables d'Environnement

| Variable | Description | Défaut |
|----------|-------------|--------|
| `DATABASE_URL` | URL de la base de données | jdbc:postgresql://localhost:5432/payment_db |
| `POSTGRES_USER` | Utilisateur PostgreSQL | postgres |
| `POSTGRES_PASSWORD` | Mot de passe PostgreSQL | postgres |
| `STRIPE_API_KEY` | Clé secrète Stripe | - |
| `STRIPE_WEBHOOK_SECRET` | Secret webhook Stripe | - |
| `PAYPAL_CLIENT_ID` | Client ID PayPal | - |
| `PAYPAL_CLIENT_SECRET` | Secret PayPal | - |
| `PAYPAL_MODE` | Mode PayPal (sandbox/live) | sandbox |
| `PLATFORM_FEE_PERCENTAGE` | Pourcentage de commission | 10.0 |

### Configuration Stripe

1. Créer un compte sur [https://stripe.com](https://stripe.com)
2. Récupérer les clés API: Dashboard → Developers → API keys
3. Configurer les webhooks:
   - URL: `https://your-domain.com/api/webhooks/stripe`
   - Events à sélectionner:
     - `payment_intent.succeeded`
     - `payment_intent.payment_failed`
     - `charge.refunded`

### Configuration PayPal

1. Créer un compte développeur: [https://developer.paypal.com](https://developer.paypal.com)
2. Créer une application Sandbox
3. Récupérer Client ID et Secret
4. Configurer les webhooks dans l'application

## 📚 API Documentation

L'API est documentée avec OpenAPI/Swagger.

**Accès**: http://localhost:8006/api/swagger-ui.html

### Endpoints Principaux

#### Paiements

**POST /api/payments**
```json
{
  "studentId": "student-uuid",
  "amount": 99.99,
  "currency": "USD",
  "method": "STRIPE",
  "courseId": "course-uuid",
  "discountCode": "PROMO20",
  "description": "Course payment"
}
```

**GET /api/payments/{paymentId}**
Récupérer un paiement

**GET /api/payments/student/{studentId}**
Récupérer les paiements d'un étudiant

**POST /api/payments/{paymentId}/refund**
Rembourser un paiement

#### Abonnements

**POST /api/subscriptions**
```json
{
  "studentId": "student-uuid",
  "type": "MONTHLY",
  "paymentMethod": "STRIPE",
  "autoRenew": true
}
```

**POST /api/subscriptions/{subscriptionId}/cancel**
Annuler un abonnement

#### Webhooks

**POST /api/webhooks/stripe**
Endpoint pour les webhooks Stripe

**POST /api/webhooks/paypal**
Endpoint pour les webhooks PayPal

## 🧪 Tests

### Lancer tous les tests
```bash
mvn test
```

### Tests d'intégration
```bash
mvn verify
```

### Coverage
```bash
mvn clean test jacoco:report
# Rapport dans: target/site/jacoco/index.html
```

## 🐳 Docker

### Build de l'image
```bash
docker build -t payment-service:latest .
```

### Lancer avec Docker Compose
```bash
docker-compose up -d
```

### Vérifier les logs
```bash
docker-compose logs -f payment-service
```

### Arrêter les services
```bash
docker-compose down
```

## 📊 Monitoring

### Health Check
```bash
curl http://localhost:8006/api/health
```

### Actuator Endpoints
- `/actuator/health` - État de santé
- `/actuator/metrics` - Métriques
- `/actuator/prometheus` - Métriques Prometheus
- `/actuator/info` - Informations

### Métriques Prometheus
Exposées sur: http://localhost:8006/api/actuator/prometheus

### Grafana Dashboards
Importer les dashboards depuis: `/monitoring/grafana/`

## 🔒 Sécurité

### Authentification
- JWT Token requis pour tous les endpoints (sauf webhooks)
- Header: `Authorization: Bearer <token>`

### Webhooks
- Vérification de signature Stripe
- Vérification de signature PayPal
- Endpoints exempts d'authentification

### Meilleures Pratiques
- Jamais de clés API en dur dans le code
- Variables d'environnement pour les secrets
- HTTPS obligatoire en production
- Validation des entrées
- Protection CSRF désactivée pour webhooks uniquement

## 🔄 Circuit Breaker

Le service utilise Resilience4j pour la tolérance aux pannes:

- **Stripe Gateway**: Circuit breaker configuré
- **PayPal Gateway**: Circuit breaker configuré
- **Retry Policy**: 3 tentatives avec backoff exponentiel

Configuration dans `application.yml`

## 📈 Observabilité

### Logs
- Format: JSON structuré
- Niveaux: DEBUG (dev), INFO (prod)
- Rotation: 10MB par fichier, 30 jours de rétention

### Traces
- Spring Boot Actuator
- Micrometer pour les métriques
- Compatible avec Prometheus + Grafana

## 🚀 Déploiement

### Production avec Docker
```bash
docker run -d \
  --name payment-service \
  -p 8006:8006 \
  -e DATABASE_URL=<prod-db-url> \
  -e STRIPE_API_KEY=<live-key> \
  payment-service:latest
```

### Kubernetes
Fichiers de déploiement dans `/k8s/`:
```bash
kubectl apply -f k8s/
```

### CI/CD
- GitHub Actions workflow dans `.github/workflows/`
- Build automatique sur push
- Tests automatiques
- Déploiement automatique (si configuré)

## 🐛 Troubleshooting

### Erreur de connexion à la base de données
```bash
# Vérifier que PostgreSQL est démarré
docker-compose ps

# Vérifier les logs
docker-compose logs postgres
```

### Webhooks non reçus
1. Vérifier la configuration dans le dashboard Stripe/PayPal
2. Utiliser Stripe CLI pour tester localement:
```bash
stripe listen --forward-to localhost:8006/api/webhooks/stripe
```

### Tests échouent
```bash
# Nettoyer et rebuilder
mvn clean install

# Vérifier H2 pour les tests
mvn test -DskipTests=false
```

## 📝 Contribution

1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit (`git commit -m 'Add AmazingFeature'`)
4. Push (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📄 License

MIT

## 👥 Auteurs

- Votre équipe

## 🔗 Liens Utiles

- [Documentation Stripe](https://stripe.com/docs)
- [Documentation PayPal](https://developer.paypal.com/docs)
- [Spring Boot Docs](https://spring.io/projects/spring-boot)
- [OpenAPI Specification](https://swagger.io/specification/)