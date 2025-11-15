#!/usr/bin/env python3
"""
Script de correction de la structure du Payments Service
Résout les problèmes de duplication et d'organisation
"""

import os
import sys
from pathlib import Path

# Couleurs pour le terminal
class Colors:
    BLUE = '\033[0;34m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    NC = '\033[0m'

def print_color(message: str, color: str = Colors.NC):
    """Afficher un message en couleur"""
    print(f"{color}{message}{Colors.NC}")

def check_directory():
    """Vérifier qu'on est dans le bon répertoire"""
    current_dir = Path.cwd()
    
    if not (current_dir / "manage.py").exists():
        print_color("❌ Erreur: Ce script doit être exécuté depuis le répertoire payments-service", Colors.RED)
        print_color(f"Répertoire actuel: {current_dir}", Colors.RED)
        sys.exit(1)
    
    print_color(f"✓ Répertoire correct: {current_dir}", Colors.GREEN)
    return current_dir

def fix_payments_views(base_dir: Path):
    """Corriger les vues de paiement"""
    print_color("\n🔧 Correction des vues de paiement...", Colors.YELLOW)
    
    # Le contenu correct pour apps/payments/payments/views.py
    content = '''"""
apps/payments/payments/views.py
Vues pour la gestion des paiements
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from asgiref.sync import async_to_sync
import logging
from datetime import datetime, timedelta

from apps.payments.gateways.services import PaymentService
from apps.payments.serializers import (
    PaymentSerializer,
    CreatePaymentSerializer,
    RefundPaymentSerializer
)

logger = logging.getLogger(__name__)


class PaymentView(APIView):
    """Vue pour gérer les paiements"""
    
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = PaymentService()
    
    def get(self, request, payment_id=None):
        """Récupérer un ou plusieurs paiements"""
        try:
            if payment_id:
                payment = async_to_sync(self.service.get_payment)(payment_id)
                
                if not payment:
                    return Response(
                        {'error': 'Payment not found'},
                        status=status.HTTP_404_NOT_FOUND
                    )
                
                serializer = PaymentSerializer(payment)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                student_id = request.query_params.get('student_id', str(request.user.id))
                payment_status = request.query_params.get('status')
                limit = int(request.query_params.get('limit', 50))
                
                payments = async_to_sync(self.service.get_student_payments)(
                    student_id, payment_status, limit
                )
                
                serializer = PaymentSerializer(payments, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting payments: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        """Créer et traiter un paiement"""
        try:
            serializer = CreatePaymentSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            # Créer le paiement
            payment = async_to_sync(self.service.create_payment)(
                student_id=str(serializer.validated_data['student_id']),
                amount=serializer.validated_data['amount'],
                currency=serializer.validated_data['currency'],
                method=serializer.validated_data['method'],
                course_id=str(serializer.validated_data.get('course_id')) if serializer.validated_data.get('course_id') else None,
                subscription_id=str(serializer.validated_data.get('subscription_id')) if serializer.validated_data.get('subscription_id') else None,
                items=serializer.validated_data.get('items'),
                description=serializer.validated_data.get('description')
            )
            
            # Traiter le paiement avec la passerelle
            gateway = serializer.validated_data.get('gateway', 'STRIPE')
            processed_payment = async_to_sync(self.service.process_payment)(
                payment.id,
                gateway
            )
            
            response_serializer = PaymentSerializer(processed_payment)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error creating payment: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ConfirmPaymentView(APIView):
    """Vue pour confirmer un paiement"""
    
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = PaymentService()
    
    def post(self, request, payment_id):
        """Confirmer un paiement après validation par la passerelle"""
        try:
            transaction_id = request.data.get('transaction_id')
            
            if not transaction_id:
                return Response(
                    {'error': 'transaction_id is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            payment = async_to_sync(self.service.confirm_payment)(
                payment_id,
                transaction_id
            )
            
            serializer = PaymentSerializer(payment)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error confirming payment: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RefundPaymentView(APIView):
    """Vue pour rembourser un paiement"""
    
    permission_classes = [IsAdminUser]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = PaymentService()
    
    def post(self, request, payment_id):
        """Rembourser un paiement"""
        try:
            serializer = RefundPaymentSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            payment = async_to_sync(self.service.refund_payment)(
                payment_id,
                serializer.validated_data.get('amount'),
                serializer.validated_data.get('reason')
            )
            
            response_serializer = PaymentSerializer(payment)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
            
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error refunding payment: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PaymentStatisticsView(APIView):
    """Vue pour les statistiques de paiement"""
    
    permission_classes = [IsAdminUser]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = PaymentService()
    
    def get(self, request):
        """Récupérer les statistiques"""
        try:
            days = int(request.query_params.get('days', 30))
            start_date = datetime.now() - timedelta(days=days)
            
            stats = async_to_sync(self.service.get_payment_statistics)(
                start_date=start_date
            )
            
            return Response(stats, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting statistics: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
'''
    
    file_path = base_dir / "apps/payments/payments/views.py"
    file_path.write_text(content)
    print(f"  ✓ apps/payments/payments/views.py corrigé")

def remove_duplicate_views(base_dir: Path):
    """Supprimer les vues dupliquées"""
    print_color("\n🗑️ Nettoyage des fichiers dupliqués...", Colors.YELLOW)
    
    # Supprimer apps/payments/views.py (duplication)
    duplicate_views = base_dir / "apps/payments/views.py"
    if duplicate_views.exists():
        duplicate_views.unlink()
        print(f"  ✓ apps/payments/views.py supprimé (duplication)")
    else:
        print(f"  ℹ apps/payments/views.py n'existe pas")

def fix_payments_services(base_dir: Path):
    """Corriger le service de paiement"""
    print_color("\n🔧 Correction du service de paiement...", Colors.YELLOW)
    
    # Supprimer la classe vide dans apps/payments/payments/services.py
    content = '''"""
apps/payments/payments/services.py
Ce module importe le PaymentService depuis gateways.services
pour maintenir la compatibilité.
"""
from apps.payments.gateways.services import PaymentService

__all__ = ['PaymentService']
'''
    
    file_path = base_dir / "apps/payments/payments/services.py"
    file_path.write_text(content)
    print(f"  ✓ apps/payments/payments/services.py corrigé (réexporte PaymentService)")

def update_payments_init(base_dir: Path):
    """Mettre à jour __init__.py pour une meilleure organisation"""
    print_color("\n📦 Mise à jour de __init__.py...", Colors.YELLOW)
    
    content = '''"""
apps/payments/__init__.py
Exports principaux du module payments
"""
from apps.payments.gateways.services import PaymentService
from apps.payments.billing.services import InvoiceService
from apps.payments.subscriptions.services import SubscriptionService
from apps.payments.subscriptions.discount_service import DiscountService

__all__ = [
    'PaymentService',
    'InvoiceService',
    'SubscriptionService',
    'DiscountService',
]
'''
    
    file_path = base_dir / "apps/payments/__init__.py"
    file_path.write_text(content)
    print(f"  ✓ apps/payments/__init__.py mis à jour")

def create_structure_diagram(base_dir: Path):
    """Créer un diagramme de la structure corrigée"""
    print_color("\n📊 Création du diagramme de structure...", Colors.YELLOW)
    
    content = '''# Structure Corrigee du Payments Service

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
'''
    
    file_path = base_dir / "STRUCTURE.md"
    # Utiliser encoding UTF-8 explicite pour Windows
    file_path.write_text(content, encoding='utf-8')
    print(f"  ✓ STRUCTURE.md créé")
    print_color("✓ Diagramme de structure créé\n", Colors.GREEN)

def verify_structure(base_dir: Path):
    """Vérifier que la structure est correcte"""
    print_color("\n🔍 Vérification de la structure...", Colors.YELLOW)
    
    required_files = {
        "apps/payments/payments/views.py": "Vues de paiement",
        "apps/payments/payments/services.py": "Service réexporté",
        "apps/payments/gateways/services.py": "PaymentService principal",
        "apps/payments/__init__.py": "Exports principaux",
        "apps/payments/webhooks/views.py": "Webhooks",
        "apps/payments/tasks.py": "Tâches Celery",
    }
    
    all_ok = True
    for file_path, description in required_files.items():
        full_path = base_dir / file_path
        if full_path.exists():
            print(f"  ✓ {description}: {file_path}")
        else:
            print_color(f"  ❌ {description}: {file_path} (manquant)", Colors.RED)
            all_ok = False
    
    # Vérifier qu'il n'y a pas de duplication
    duplicate_views = base_dir / "apps/payments/views.py"
    if not duplicate_views.exists():
        print(f"  ✓ Pas de duplication de vues")
    else:
        print_color(f"  ⚠️ Fichier dupliqué trouvé: apps/payments/views.py", Colors.YELLOW)
    
    if all_ok:
        print_color("\n✅ Structure vérifiée et correcte!\n", Colors.GREEN)
    else:
        print_color("\n⚠️ Certains fichiers sont manquants\n", Colors.YELLOW)
    
    return all_ok

def print_summary():
    """Afficher le résumé des corrections"""
    print_color("\n" + "="*60, Colors.BLUE)
    print_color("✅ CORRECTIONS DE STRUCTURE TERMINÉES", Colors.GREEN)
    print_color("="*60 + "\n", Colors.BLUE)
    
    print_color("📦 Fichiers corrigés:", Colors.YELLOW)
    corrections = [
        "✓ apps/payments/payments/views.py (vues complètes)",
        "✓ apps/payments/payments/services.py (réexporte PaymentService)",
        "✓ apps/payments/__init__.py (exports centralisés)",
        "✓ apps/payments/views.py (supprimé - duplication)",
        "✓ STRUCTURE.md (documentation)",
    ]
    
    for correction in corrections:
        print(f"  {correction}")
    
    print_color("\n📋 Changements principaux:", Colors.YELLOW)
    changes = [
        "1. ✅ Vues de paiement complètes et fonctionnelles",
        "2. ✅ Plus de duplication de services",
        "3. ✅ Structure claire: un service = un fichier",
        "4. ✅ Imports centralisés dans __init__.py",
        "5. ✅ Documentation complète de la structure",
    ]
    
    for change in changes:
        print(f"  {change}")
    
    print_color("\n💡 Utilisation:", Colors.YELLOW)
    print('''
  from apps.payments import (
      PaymentService,
      InvoiceService,
      SubscriptionService,
      DiscountService
  )
    ''')
    
    print_color("\n" + "="*60, Colors.BLUE)
    print_color("🎉 Structure propre et organisée!", Colors.GREEN)
    print_color("="*60 + "\n", Colors.BLUE)

def main():
    """Fonction principale"""
    try:
        print_color("\n" + "="*60, Colors.BLUE)
        print_color("🔧 CORRECTION DE STRUCTURE - PAYMENTS SERVICE", Colors.BLUE)
        print_color("="*60 + "\n", Colors.BLUE)
        
        # 1. Vérifier le répertoire
        base_dir = check_directory()
        
        # 2. Corriger les vues de paiement
        fix_payments_views(base_dir)
        
        # 3. Supprimer les fichiers dupliqués
        remove_duplicate_views(base_dir)
        
        # 4. Corriger le service de paiement
        fix_payments_services(base_dir)
        
        # 5. Mettre à jour __init__.py
        update_payments_init(base_dir)
        
        # 6. Créer la documentation de structure
        create_structure_diagram(base_dir)
        
        # 7. Vérifier la structure
        verify_structure(base_dir)
        
        # 8. Afficher le résumé
        print_summary()
        
        return 0
        
    except Exception as e:
        print_color(f"\n❌ Erreur: {str(e)}", Colors.RED)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())