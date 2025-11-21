// ============================================
// 📁 README.md
// ============================================
# Payment Service - Spring Boot

Service de paiement complet pour une plateforme LMS.

## 🚀 Fonctionnalités

### 💳 Paiements
- **Stripe Integration** : Cartes de crédit/débit, Apple Pay, Google Pay
- **PayPal Integration** : Paiements PayPal complets
- **Multiple Currencies** : Support de plusieurs devises
- **Processing Fees** : Calcul automatique des frais
- **Platform Fees** : Prélèvement de commission plateforme
- **Refunds** : Remboursements complets ou partiels
- **Webhooks** : Gestion des événements asynchrones

### 🎫 Abonnements
- **Types variés** : Monthly, Quarterly, Annual, Lifetime, etc.
- **Auto-renewal** : Renouvellement automatique
- **Trial periods** : Périodes d'essai
- **Cancellation** : Annulation avec conservation jusqu'à fin de période
- **Pricing tiers** : Différents niveaux de prix

### 🎁 Codes promo
- **Discount types** : Pourcentage, montant fixe, bundles
- **Usage limits** : Limites d'utilisation globales et par utilisateur
- **Time-bound** : Dates de début et fin
- **Validation** : Vérification automatique

### 📄 Facturation
- **Invoice generation** : Génération automatique
- **PDF export** : Export en PDF
- **Payment tracking** : Suivi des paiements
- **Overdue management** : Gestion des impayés

## 📦 Installation

### Prérequis
- Java 17+
- Maven 3.8+
- PostgreSQL 15+
- Docker & Docker Compose

### Build & Run

```bash
# Build
mvn clean package

# Run
java -jar target/payment-service-1.0.0.jar

# Avec Docker
docker-compose up -d
```

## 📚 API Documentation

### Payments

**POST /api/payments**
```json
{
  "studentId": "uuid",
  "amount": 99.99,
  "currency": "USD",
  "method": "STRIPE",
  "courseId": "uuid",
  "discountCode": "PROMO20",
  "cardToken": "tok_xxx"
}
```

**GET /api/payments/{paymentId}**
Récupère un paiement

**GET /api/payments/student/{studentId}**
Récupère tous les paiements d'un étudiant

**POST /api/payments/{paymentId}/refund?amount=50.00**
Rembourse un paiement

### Subscriptions

**POST /api/subscriptions**
```json
{
  "studentId": "uuid",
  "type": "MONTHLY",
  "paymentMethod": "STRIPE",
  "autoRenew": true,
  "cardToken": "tok_xxx"
}
```

**POST /api/subscriptions/{subscriptionId}/cancel**
Annule un abonnement

### Webhooks

**POST /api/webhooks/stripe**
Endpoint pour webhooks Stripe

**POST /api/webhooks/paypal**
Endpoint pour webhooks PayPal

## 🔐 Configuration Stripe

1. Créer un compte sur https://stripe.com
2. Récupérer les clés API (Dashboard > Developers > API keys)
3. Configurer les webhooks:
   - URL: `https://yourdomain.com/api/webhooks/stripe`
   - Events: `payment_intent.succeeded`, `payment_intent.payment_failed`, `charge.refunded`

## 🔐 Configuration PayPal

1. Créer un compte développeur sur https://developer.paypal.com
2. Créer une app sandbox
3. Récupérer Client ID et Secret
4. Configurer les webhooks dans l'app

## 🎯 Scheduled Tasks

- **Auto-renewals** : 2 AM daily
- **Expiration check** : 3 AM daily
- **Invoice reminders** : Configurable

## 📊 Database Schema

Le service utilise JPA/Hibernate avec PostgreSQL.

Tables principales:
- `payments` - Paiements
- `invoices` - Factures
- `subscriptions` - Abonnements
- `discounts` - Codes promo
- `transactions` - Transactions

## 🧪 Tests

```bash
mvn test
```

## 📝 Logs

Les logs sont configurés avec SLF4J + Logback:
- Console output en développement
- File output en production (`/var/log/payment-service/`)

## 🔒 Sécurité

- JWT Authentication
- HTTPS obligatoire en production
- Webhook signature verification
- Input validation
- SQL injection prevention (JPA)
- XSS protection

## 📈 Monitoring

Le service expose des endpoints actuator pour monitoring:
- `/actuator/health` - Health check
- `/actuator/metrics` - Métriques
- `/actuator/info` - Informations

## 🚀 Déploiement

### Docker Production

```bash
docker build -t payment-service:latest .
docker run -p 8003:8003 \
  -e DATABASE_URL=... \
  -e STRIPE_API_KEY=... \
  payment-service:latest
```

### Kubernetes

Fichiers de déploiement K8s disponibles dans `/k8s/`

## 📝 License

MIT
"""