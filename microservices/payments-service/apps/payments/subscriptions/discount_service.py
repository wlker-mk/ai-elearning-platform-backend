from typing import Optional, List
from datetime import datetime
from prisma import Prisma
from prisma.models import Discount
import logging

logger = logging.getLogger(__name__)


class DiscountService:
    """Service de gestion des codes de réduction"""
    
    def __init__(self):
        self.db = Prisma()
    
    async def connect(self):
        if not self.db.is_connected():
            await self.db.connect()
    
    async def disconnect(self):
        if self.db.is_connected():
            await self.db.disconnect()
    
    async def create_discount(
        self,
        code: str,
        discount_type: str,
        value: float,
        start_date: datetime,
        end_date: datetime,
        max_uses: Optional[int] = None,
        max_uses_per_user: int = 1
    ) -> Discount:
        """Créer un code de réduction"""
        try:
            await self.connect()
            
            # Vérifier si le code existe déjà
            existing = await self.db.discount.find_unique(where={'code': code})
            
            if existing:
                raise ValueError(f"Discount code {code} already exists")
            
            discount = await self.db.discount.create(
                data={
                    'code': code.upper(),
                    'type': discount_type,
                    'value': value,
                    'startDate': start_date,
                    'endDate': end_date,
                    'maxUses': max_uses,
                    'maxUsesPerUser': max_uses_per_user
                }
            )
            
            logger.info(f"Discount created: {code}")
            return discount
            
        except Exception as e:
            logger.error(f"Error creating discount: {str(e)}")
            raise
        finally:
            await self.disconnect()
    
    async def validate_discount(self, code: str, user_id: str) -> tuple[bool, str, Optional[Discount]]:
        """Valider un code de réduction"""
        try:
            await self.connect()
            
            discount = await self.db.discount.find_unique(
                where={'code': code.upper()}
            )
            
            if not discount:
                return False, "Invalid discount code", None
            
            now = datetime.now()
            
            # Vérifier les dates
            if now < discount.startDate:
                return False, "Discount code not yet active", None
            
            if now > discount.endDate:
                return False, "Discount code has expired", None
            
            # Vérifier le nombre maximum d'utilisations
            if discount.maxUses is not None and discount.usesCount >= discount.maxUses:
                return False, "Discount code has reached maximum uses", None
            
            # TODO: Vérifier l'utilisation par utilisateur
            # Nécessite une table supplémentaire pour tracker les utilisations
            
            return True, "Valid", discount
            
        except Exception as e:
            logger.error(f"Error validating discount: {str(e)}")
            return False, "Error validating discount", None
        finally:
            await self.disconnect()
    
    async def apply_discount(self, code: str, user_id: str) -> Optional[Discount]:
        """Appliquer un code de réduction"""
        try:
            await self.connect()
            
            discount = await self.db.discount.find_unique(
                where={'code': code.upper()}
            )
            
            if not discount:
                return None
            
            # Incrémenter le compteur d'utilisations
            updated_discount = await self.db.discount.update(
                where={'id': discount.id},
                data={'usesCount': discount.usesCount + 1}
            )
            
            logger.info(f"Discount applied: {code}")
            return updated_discount
            
        except Exception as e:
            logger.error(f"Error applying discount: {str(e)}")
            return None
        finally:
            await self.disconnect()
    
    async def get_active_discounts(self) -> List[Discount]:
        """Récupérer les codes de réduction actifs"""
        try:
            await self.connect()
            
            now = datetime.now()
            
            discounts = await self.db.discount.find_many(
                where={
                    'startDate': {'lte': now},
                    'endDate': {'gte': now}
                },
                order={'createdAt': 'desc'}
            )
            
            # Filtrer ceux qui n'ont pas atteint la limite
            active = [
                d for d in discounts
                if d.maxUses is None or d.usesCount < d.maxUses
            ]
            
            return active
            
        except Exception as e:
            logger.error(f"Error getting active discounts: {str(e)}")
            return []
        finally:
            await self.disconnect()