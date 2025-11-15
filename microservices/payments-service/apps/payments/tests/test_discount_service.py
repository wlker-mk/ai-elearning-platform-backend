import pytest
from datetime import datetime, timedelta
import uuid
from apps.payments.subscriptions.discount_service import DiscountService

pytestmark = pytest.mark.django_db


@pytest.mark.asyncio
class TestDiscountService:
    """Tests pour le service de codes de réduction"""
    
    async def test_create_discount(self):
        """Test de création de code promo"""
        service = DiscountService()
        
        start_date = datetime.now()
        end_date = start_date + timedelta(days=30)
        
        discount = await service.create_discount(
            code='SUMMER2024',
            discount_type='PERCENTAGE',
            value=20.0,
            start_date=start_date,
            end_date=end_date,
            max_uses=1000
        )
        
        assert discount is not None
        assert discount.code == 'SUMMER2024'
        assert discount.value == 20.0
        assert discount.usesCount == 0
    
    async def test_validate_discount(self):
        """Test de validation de code"""
        service = DiscountService()
        
        start_date = datetime.now()
        end_date = start_date + timedelta(days=30)
        
        await service.create_discount(
            code='VALID2024',
            discount_type='PERCENTAGE',
            value=15.0,
            start_date=start_date,
            end_date=end_date
        )
        
        is_valid, message, discount = await service.validate_discount(
            'VALID2024',
            str(uuid.uuid4())
        )
        
        assert is_valid is True
        assert discount is not None
    
    async def test_expired_discount(self):
        """Test de code expiré"""
        service = DiscountService()
        
        # Code expiré hier
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now() - timedelta(days=1)
        
        await service.create_discount(
            code='EXPIRED',
            discount_type='PERCENTAGE',
            value=10.0,
            start_date=start_date,
            end_date=end_date
        )
        
        is_valid, message, _ = await service.validate_discount(
            'EXPIRED',
            str(uuid.uuid4())
        )
        
        assert is_valid is False
        assert 'expired' in message.lower()
    
    async def test_max_uses_reached(self):
        """Test de limite d'utilisation atteinte"""
        service = DiscountService()
        
        start_date = datetime.now()
        end_date = start_date + timedelta(days=30)
        
        discount = await service.create_discount(
            code='LIMITED',
            discount_type='FIXED_AMOUNT',
            value=10.0,
            start_date=start_date,
            end_date=end_date,
            max_uses=2
        )
        
        # Utiliser 2 fois
        user1 = str(uuid.uuid4())
        user2 = str(uuid.uuid4())
        
        await service.apply_discount('LIMITED', user1)
        await service.apply_discount('LIMITED', user2)
        
        # La 3ème tentative devrait échouer
        is_valid, message, _ = await service.validate_discount(
            'LIMITED',
            str(uuid.uuid4())
        )
        
        assert is_valid is False

