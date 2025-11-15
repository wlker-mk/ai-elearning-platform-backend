import pytest
from datetime import datetime, timedelta
import uuid
from apps.payments import SubscriptionService

pytestmark = pytest.mark.django_db


@pytest.mark.asyncio
class TestSubscriptionService:
    """Tests pour le service d'abonnement"""
    
    async def test_create_subscription(self):
        """Test de création d'abonnement"""
        service = SubscriptionService()
        
        student_id = str(uuid.uuid4())
        subscription = await service.create_subscription(
            student_id=student_id,
            subscription_type='MONTHLY',
            payment_method='STRIPE'
        )
        
        assert subscription is not None
        assert subscription.type == 'MONTHLY'
        assert subscription.isActive is True
        assert subscription.price == 29.99
    
    async def test_subscription_with_trial(self):
        """Test d'abonnement avec période d'essai"""
        service = SubscriptionService()
        
        subscription = await service.create_subscription(
            student_id=str(uuid.uuid4()),
            subscription_type='MONTHLY',
            payment_method='STRIPE',
            trial_days=7
        )
        
        assert subscription.trialEndDate is not None
        trial_duration = (subscription.trialEndDate - subscription.startDate).days
        assert trial_duration == 7
    
    async def test_cancel_subscription(self):
        """Test d'annulation d'abonnement"""
        service = SubscriptionService()
        
        subscription = await service.create_subscription(
            student_id=str(uuid.uuid4()),
            subscription_type='MONTHLY',
            payment_method='STRIPE'
        )
        
        # Annuler
        cancelled = await service.cancel_subscription(
            subscription.id,
            immediate=False
        )
        
        assert cancelled.isCancelled is True
        assert cancelled.cancelledAt is not None
        assert cancelled.isActive is True  # Toujours actif jusqu'à la fin
    
    async def test_immediate_cancel(self):
        """Test d'annulation immédiate"""
        service = SubscriptionService()
        
        subscription = await service.create_subscription(
            student_id=str(uuid.uuid4()),
            subscription_type='MONTHLY',
            payment_method='STRIPE'
        )
        
        cancelled = await service.cancel_subscription(
            subscription.id,
            immediate=True
        )
        
        assert cancelled.isActive is False
    
    async def test_renew_subscription(self):
        """Test de renouvellement"""
        service = SubscriptionService()
        
        subscription = await service.create_subscription(
            student_id=str(uuid.uuid4()),
            subscription_type='MONTHLY',
            payment_method='STRIPE'
        )
        
        original_end_date = subscription.endDate
        
        # Renouveler
        renewed = await service.renew_subscription(
            subscription.id,
            'payment_123'
        )
        
        assert renewed.endDate > original_end_date
        assert renewed.lastPaymentId == 'payment_123'