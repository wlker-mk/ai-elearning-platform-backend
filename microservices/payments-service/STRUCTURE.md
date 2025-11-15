# Structure Corrigee du Payments Service

## Organisation des Modules

```
apps/payments/
├── __init__.py                    # Exports principaux
│
├── billing/                       # FACTURATION
│   ├── __init__.py
│   ├── services.py               # InvoiceService
│   ├── views.py                  # Vues de facturation
│   └── urls.py
│
├── gateways/                      # PASSERELLES DE PAIEMENT
│   ├── __init__.py
│   ├── base.py                   # Interface de base
│   ├── stripe_gateway.py         # Implementation Stripe
│   ├── paypal_gateway.py         # Implementation PayPal
│   ├── factory.py                # Factory pattern
│   └── services.py               # PaymentService (SERVICE PRINCIPAL)
│
├── payments/                      # GESTION DES PAIEMENTS
│   ├── __init__.py
│   ├── services.py               # Reexporte PaymentService
│   ├── views.py                  # Vues de paiement (CORRIGE)
│   └── urls.py
│
├── subscriptions/                 # ABONNEMENTS
│   ├── __init__.py
│   ├── services.py               # SubscriptionService
│   ├── discount_service.py       # DiscountService
│   ├── views.py                  # Vues d'abonnements
│   └── urls.py
│
├── webhooks/                      # WEBHOOKS
│   ├── __init__.py
│   ├── views.py                  # Webhooks Stripe/PayPal (NOUVEAU)
│   └── urls.py                   # Routes webhooks (NOUVEAU)
│
├── serializers.py                 # Serializers communs
├── tasks.py                       # Taches Celery (NOUVEAU)
└── urls.py                        # URLs principales
```

## Services Principaux

### 1. PaymentService (apps/payments/gateways/services.py)
**Responsabilite**: Gestion complete des paiements
- Creation de paiements
- Traitement via passerelles
- Confirmation et remboursements
- Statistiques

**Utilisation**:
```python
from apps.payments import PaymentService
# ou
from apps.payments.gateways.services import PaymentService
```

### 2. InvoiceService (apps/payments/billing/services.py)
**Responsabilite**: Gestion des factures
- Creation de factures
- Suivi des paiements
- Factures en retard
- Generation de PDF

### 3. SubscriptionService (apps/payments/subscriptions/services.py)
**Responsabilite**: Gestion des abonnements
- Creation d'abonnements
- Renouvellements
- Annulations
- Verification d'expiration

### 4. DiscountService (apps/payments/subscriptions/discount_service.py)
**Responsabilite**: Codes de reduction
- Creation de codes promo
- Validation
- Application de reductions

## Flux de Paiement

```
1. Client -> POST /api/payments/
   |
2. PaymentView (apps/payments/payments/views.py)
   |
3. PaymentService.create_payment()
   |
4. PaymentService.process_payment()
   |
5. StripeGateway / PayPalGateway
   |
6. Webhook -> ConfirmPaymentView
   |
7. PaymentService.confirm_payment()
```

## Corrections Appliquees

### 1. Vues de Paiement [OK]
- **Avant**: Fichier template vide dans `apps/payments/payments/views.py`
- **Apres**: Vues completes avec PaymentView, ConfirmPaymentView, RefundPaymentView, PaymentStatisticsView

### 2. Duplication de Vues [OK]
- **Avant**: Vues dans `apps/payments/views.py` ET `apps/payments/payments/views.py`
- **Apres**: Une seule source dans `apps/payments/payments/views.py`

### 3. Service de Paiement [OK]
- **Avant**: PaymentService dans gateways ET classe vide dans payments
- **Apres**: 
  - PaymentService principal dans `apps/payments/gateways/services.py`
  - Reexportation dans `apps/payments/payments/services.py` pour compatibilite
  - Import centralise dans `apps/payments/__init__.py`

### 4. Organisation [OK]
- Tous les services accessibles via `from apps.payments import ServiceName`
- Structure logique et coherente
- Pas de duplication de code

## Bonnes Pratiques

### Import des Services
```python
# [RECOMMANDE] (via __init__.py)
from apps.payments import PaymentService, InvoiceService

# [ALTERNATIVE] (import direct)
from apps.payments.gateways.services import PaymentService

# [A EVITER] (import depuis payments.services)
# Ne pas utiliser car c'est juste une reexportation
```

### Utilisation dans les Vues
```python
from rest_framework.views import APIView
from apps.payments import PaymentService

class MyView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.payment_service = PaymentService()
```

### Tests
```python
from apps.payments import PaymentService
import pytest

@pytest.mark.asyncio
async def test_create_payment():
    service = PaymentService()
    payment = await service.create_payment(...)
    assert payment.status == 'PENDING'
```

## Verification

### Tester l'import des services
```python
python manage.py shell

>>> from apps.payments import PaymentService, InvoiceService, SubscriptionService
>>> print("OK - Tous les imports fonctionnent")
```

### Tester les vues
```bash
# Verifier que les URLs sont bien configurees
python manage.py show_urls | grep payments

# Lancer le serveur
python manage.py runserver 8003

# Tester l'endpoint
curl http://localhost:8003/api/payments/health/
```

## Resultat

[OK] Structure claire et organisee
[OK] Pas de duplication de code
[OK] Services bien separes par responsabilite
[OK] Imports coherents et simples
[OK] Vues completes et fonctionnelles
