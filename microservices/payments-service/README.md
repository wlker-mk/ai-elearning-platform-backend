"""
# Payments Service - Django + Prisma + Stripe/PayPal

Service de paiement complet pour une plateforme d'apprentissage en ligne.

## 🚀 Fonctionnalités

### 💳 Paiements
- **Multiples passerelles** : Stripe, PayPal
- **Méthodes de paiement** : Carte bancaire, PayPal, Apple Pay, Google Pay
- **Statuts** : PENDING, PROCESSING, COMPLETED, FAILED, REFUNDED
- **Frais** : Calcul automatique des frais de plateforme et de traitement
- **Remboursements** : Complets ou partiels
- **Historique** : Tracking complet de tous les paiements

### 📄 Facturation
- **Génération automatique** : Numéros de facture uniques
- **Taxes** : Calcul selon le pays
- **Réductions** : Support des codes promo
- **États** : PENDING, PROCESSING, COMPLETED
- **PDF** : Génération de factures PDF
- **Relances** : Détection des factures en retard

### 🔄 Abonnements
- **Types variés** : FREE, MONTHLY, QUARTERLY, ANNUAL, LIFETIME, etc.
- **Essai gratuit** : Période d'essai configurable
- **Renouvellement automatique** : Auto-renewal
- **Annulation** : Immédiate ou à la fin de la période
- **Gestion** : Dashboard complet

### 🎟️ Codes de réduction
- **Types** : Pourcentage, montant fixe, bundle, early bird, flash sale
- **Limitations** : Nombre d'utilisations global et par utilisateur
- **Dates** : Période de validité configurable
- **Validation** : Vérification en temps réel

### 💰 Fonctionnalités avancées
- **Multi-devise** : Support USD, EUR, GBP, etc.
- **Webhooks** : Notifications en temps réel
- **Analytics** : Statistiques détaillées
- **Sécurité** : Conformité PCI DSS via Stripe
- **Audit** : Logs complets de toutes les transactions

## 📦 Installation

### Prérequis
- Python 3.11+
- PostgreSQL 15+
- Compte Stripe et/ou PayPal

### Installation locale

```bash
# 1. Cloner et configurer
git clone <repo-url>
cd payments-service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Variables d'environnement
cp .env.example .env
# Éditer .env avec vos clés Stripe/PayPal

# 3. Base de données
prisma generate
prisma migrate deploy
python manage.py migrate

# 4. Lancer
python manage.py runserver 8003
```

### Installation avec Docker

```bash
docker-compose up -d
```

## 📚 Documentation API

### Paiements

**POST /api/payments/**
```json
{
  "student_id": "uuid",
  "amount": 99.99,
  "currency": "USD",
  "method": "STRIPE",
  "course_id": "uuid",
  "description": "Course purchase",
  "gateway": "STRIPE"
}
```

**GET /api/payments/?student_id=uuid&status=COMPLETED**

**POST /api/payments/{payment_id}/confirm/**
```json
{
  "transaction_id": "stripe_transaction_id"
}
```

**POST /api/payments/{payment_id}/refund/** (Admin)
```json
{
  "amount": 50.00,
  "reason": "Customer request"
}
```

**GET /api/payments/statistics/?days=30** (Admin)

### Factures

**POST /api/invoices/**
```json
{
  "student_id": "uuid",
  "items": [
    {
      "name": "Python Course",
      "price": 99.99,
      "quantity": 1
    }
  ],
  "currency": "USD",
  "tax_country": "US",
  "discount_amount": 10.00,
  "due_days": 30
}
```

**GET /api/invoices/?student_id=uuid&status=PENDING**

**GET /api/invoices/{invoice_id}/**

**GET /api/invoices/number/{invoice_number}/**

**GET /api/invoices/overdue/** (Admin)

### Abonnements

**POST /api/subscriptions/**
```json
{
  "student_id": "uuid",
  "type": "MONTHLY",
  "payment_method": "STRIPE",
  "trial_days": 7
}
```

**GET /api/subscriptions/?student_id=uuid**

**POST /api/subscriptions/{subscription_id}/cancel/**
```json
{
  "immediate": false
}
```

### Codes de réduction

**POST /api/subscriptions/discounts/** (Admin)
```json
{
  "code": "SUMMER2024",
  "type": "PERCENTAGE",
  "value": 20,
  "start_date": "2024-06-01T00:00:00Z",
  "end_date": "2024-08-31T23:59:59Z",
  "max_uses": 1000,
  "max_uses_per_user": 1
}
```

**GET /api/subscriptions/discounts/**

**POST /api/subscriptions/discounts/validate/**
```json
{
  "code": "SUMMER2024",
  "user_id": "uuid"
}
```

## 🔐 Webhooks

### Stripe Webhook
Configurez l'URL dans le dashboard Stripe :
```
https://your-domain.com/api/webhooks/stripe/
```

Events gérés :
- `payment_intent.succeeded`
- `payment_intent.payment_failed`
- `charge.refunded`
- `customer.subscription.created`
- `customer.subscription.updated`
- `customer.subscription.deleted`

### PayPal Webhook
Configurez l'URL dans le dashboard PayPal :
```
https://your-domain.com/api/webhooks/paypal/
```

## 💡 Cas d'usage

### 1. Achat de cours
```javascript
// 1. Créer le paiement
const payment = await fetch('/api/payments/', {
  method: 'POST',
  body: JSON.stringify({
    student_id: 'user-uuid',
    amount: 99.99,
    currency: 'USD',
    method: 'STRIPE',
    course_id: 'course-uuid',
    gateway: 'STRIPE'
  })
});

// 2. Afficher Stripe Checkout
const stripe = Stripe('pk_test_...');
await stripe.redirectToCheckout({
  sessionId: payment.external_reference
});

// 3. Confirmer après succès (webhook ou callback)
await fetch(`/api/payments/${payment.id}/confirm/`, {
  method: 'POST',
  body: JSON.stringify({
    transaction_id: 'stripe_txn_id'
  })
});
```

### 2. Abonnement avec essai gratuit
```javascript
// 1. Créer l'abonnement
const subscription = await fetch('/api/subscriptions/', {
  method: 'POST',
  body: JSON.stringify({
    student_id: 'user-uuid',
    type: 'MONTHLY',
    payment_method: 'STRIPE',
    trial_days: 7
  })
});

// Pas de paiement immédiat - essai gratuit de 7 jours
```

### 3. Application d'un code promo
```javascript
// 1. Valider le code
const validation = await fetch('/api/subscriptions/discounts/validate/', {
  method: 'POST',
  body: JSON.stringify({
    code: 'SUMMER2024',
    user_id: 'user-uuid'
  })
});

if (validation.valid) {
  // 2. Appliquer la réduction
  const discount = validation.discount;
  const newAmount = applyDiscount(originalAmount, discount.type, discount.value);
  
  // 3. Créer le paiement avec le montant réduit
  await createPayment(newAmount);
}
```

## 📊 Métriques

- **Taux de succès** : % de paiements réussis
- **Revenus** : Montant total, net, frais
- **Abonnements** : Actifs, annulés, taux de renouvellement
- **Remboursements** : Montant et taux
- **Codes promo** : Utilisations et économies

## 🔒 Sécurité

- **PCI DSS** : Conformité via Stripe
- **Tokens** : Pas de stockage de cartes
- **HTTPS** : Obligatoire en production
- **Webhooks** : Vérification de signature
- **Audit logs** : Toutes les transactions

## 📝 Licence

MIT
"""