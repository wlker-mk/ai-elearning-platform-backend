import pytest
from datetime import datetime
import uuid
from apps.payments import PaymentService

pytestmark = pytest.mark.django_db


@pytest.mark.asyncio
class TestPaymentService:
    """Tests pour le service de paiement"""
    
    async def test_create_payment(self):
        """Test de création de paiement"""
        service = PaymentService()
        
        student_id = str(uuid.uuid4())
        payment = await service.create_payment(
            student_id=student_id,
            amount=99.99,
            currency='USD',
            method='STRIPE',
            course_id=str(uuid.uuid4()),
            description='Course purchase'
        )
        
        assert payment is not None
        assert payment.amount == 99.99
        assert payment.status == 'PENDING'
        assert payment.processingFee > 0
        assert payment.platformFee > 0
    
    async def test_payment_fee_calculation(self):
        """Test du calcul des frais"""
        service = PaymentService()
        
        payment = await service.create_payment(
            student_id=str(uuid.uuid4()),
            amount=100.00,
            currency='USD',
            method='STRIPE'
        )
        
        # Frais de traitement: 100 * 0.029 + 0.30 = 3.20
        # Frais de plateforme: 100 * 0.10 = 10.00
        # Net: 100 - 3.20 - 10.00 = 86.80
        
        assert payment.processingFee == 3.20
        assert payment.platformFee == 10.00
        assert payment.netAmount == 86.80
    
    async def test_confirm_payment(self):
        """Test de confirmation de paiement"""
        service = PaymentService()
        
        payment = await service.create_payment(
            student_id=str(uuid.uuid4()),
            amount=99.99,
            currency='USD',
            method='STRIPE'
        )
        
        # Confirmer
        confirmed = await service.confirm_payment(
            payment.id,
            'txn_123456'
        )
        
        assert confirmed.status == 'COMPLETED'
        assert confirmed.transactionId == 'txn_123456'
        assert confirmed.paidAt is not None
    
    async def test_refund_payment(self):
        """Test de remboursement"""
        service = PaymentService()
        
        # Créer et confirmer un paiement
        payment = await service.create_payment(
            student_id=str(uuid.uuid4()),
            amount=99.99,
            currency='USD',
            method='STRIPE'
        )
        
        await service.confirm_payment(payment.id, 'txn_123')
        
        # Rembourser
        refunded = await service.refund_payment(payment.id, amount=50.00)
        
        assert refunded.status == 'REFUNDED'
        assert refunded.isRefunded is True
        assert refunded.refundedAmount == 50.00
    
    async def test_payment_statistics(self):
        """Test des statistiques de paiement"""
        service = PaymentService()
        
        student_id = str(uuid.uuid4())
        
        # Créer plusieurs paiements
        for _ in range(3):
            payment = await service.create_payment(
                student_id=student_id,
                amount=100.00,
                currency='USD',
                method='STRIPE'
            )
            await service.confirm_payment(payment.id, f'txn_{_}')
        
        # Créer un paiement échoué
        failed = await service.create_payment(
            student_id=student_id,
            amount=50.00,
            currency='USD',
            method='STRIPE'
        )
        
        stats = await service.get_payment_statistics()
        
        assert stats['total_payments'] >= 4
        assert stats['completed'] >= 3
        assert stats['total_amount'] >= 300.00
