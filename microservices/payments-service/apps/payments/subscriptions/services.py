from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from prisma import Prisma
from prisma.models import Subscription
import logging
from shared.shared.payments.constants import SUBSCRIPTION_TYPE

logger = logging.getLogger(__name__)


class SubscriptionService:
    """Service de gestion des abonnements"""
    
    def __init__(self):
        self.db = Prisma()
    
    async def connect(self):
        if not self.db.is_connected():
            await self.db.connect()
    
    async def disconnect(self):
        if self.db.is_connected():
            await self.db.disconnect()
    
    async def create_subscription(
        self,
        student_id: str,
        subscription_type: str,
        payment_method: str,
        payment_id: Optional[str] = None,
        trial_days: int = 0
    ) -> Subscription:
        """Créer un abonnement"""
        try:
            await self.connect()
            
            # Vérifier si l'étudiant a déjà un abonnement actif
            existing = await self.db.subscription.find_first(
                where={
                    'studentId': student_id,
                    'isActive': True
                }
            )
            
            if existing:
                raise ValueError("Student already has an active subscription")
            
            # Récupérer les détails de l'abonnement
            sub_details = SUBSCRIPTION_TYPE.get(subscription_type)
            
            if not sub_details:
                raise ValueError(f"Invalid subscription type: {subscription_type}")
            
            # Calculer les dates
            start_date = datetime.now()
            duration_days = sub_details['duration_days']
            
            if duration_days > 0:
                end_date = start_date + timedelta(days=duration_days)
            else:
                # Pour FREE et LIFETIME
                end_date = start_date + timedelta(days=36500)  # 100 ans
            
            # Période d'essai
            trial_end_date = None
            if trial_days > 0:
                trial_end_date = start_date + timedelta(days=trial_days)
            
            # Prochaine date de facturation
            next_billing_date = None
            if subscription_type not in ['FREE', 'LIFETIME']:
                next_billing_date = end_date
            
            # Créer l'abonnement
            subscription = await self.db.subscription.create(
                data={
                    'studentId': student_id,
                    'type': subscription_type,
                    'startDate': start_date,
                    'endDate': end_date,
                    'trialEndDate': trial_end_date,
                    'isActive': True,
                    'price': sub_details['price'] or 0,
                    'paymentMethod': payment_method,
                    'autoRenew': subscription_type not in ['FREE', 'LIFETIME'],
                    'nextBillingDate': next_billing_date,
                    'lastPaymentId': payment_id
                }
            )
            
            logger.info(f"Subscription created: {subscription.id}")
            return subscription
            
        except Exception as e:
            logger.error(f"Error creating subscription: {str(e)}")
            raise
        finally:
            await self.disconnect()
    
    async def renew_subscription(
        self,
        subscription_id: str,
        payment_id: str
    ) -> Subscription:
        """Renouveler un abonnement"""
        try:
            await self.connect()
            
            subscription = await self.db.subscription.find_unique(
                where={'id': subscription_id}
            )
            
            if not subscription:
                raise ValueError("Subscription not found")
            
            # Récupérer les détails
            sub_details = SUBSCRIPTION_TYPE.get(subscription.type)
            duration_days = sub_details['duration_days']
            
            # Nouvelle date de fin
            new_end_date = subscription.endDate + timedelta(days=duration_days)
            new_billing_date = new_end_date
            
            # Mettre à jour l'abonnement
            updated_subscription = await self.db.subscription.update(
                where={'id': subscription_id},
                data={
                    'endDate': new_end_date,
                    'nextBillingDate': new_billing_date,
                    'lastPaymentId': payment_id,
                    'isActive': True,
                    'isCancelled': False
                }
            )
            
            logger.info(f"Subscription renewed: {subscription_id}")
            return updated_subscription
            
        except Exception as e:
            logger.error(f"Error renewing subscription: {str(e)}")
            raise
        finally:
            await self.disconnect()
    
    async def cancel_subscription(
        self,
        subscription_id: str,
        immediate: bool = False
    ) -> Subscription:
        """Annuler un abonnement"""
        try:
            await self.connect()
            
            subscription = await self.db.subscription.find_unique(
                where={'id': subscription_id}
            )
            
            if not subscription:
                raise ValueError("Subscription not found")
            
            update_data = {
                'isCancelled': True,
                'cancelledAt': datetime.now(),
                'autoRenew': False
            }
            
            # Annulation immédiate
            if immediate:
                update_data['isActive'] = False
                update_data['endDate'] = datetime.now()
            
            # Mettre à jour l'abonnement
            updated_subscription = await self.db.subscription.update(
                where={'id': subscription_id},
                data=update_data
            )
            
            logger.info(f"Subscription cancelled: {subscription_id}")
            return updated_subscription
            
        except Exception as e:
            logger.error(f"Error cancelling subscription: {str(e)}")
            raise
        finally:
            await self.disconnect()
    
    async def get_subscription(self, subscription_id: str) -> Optional[Subscription]:
        """Récupérer un abonnement"""
        try:
            await self.connect()
            return await self.db.subscription.find_unique(where={'id': subscription_id})
        except Exception as e:
            logger.error(f"Error getting subscription: {str(e)}")
            return None
        finally:
            await self.disconnect()
    
    async def get_student_subscription(self, student_id: str) -> Optional[Subscription]:
        """Récupérer l'abonnement actif d'un étudiant"""
        try:
            await self.connect()
            
            return await self.db.subscription.find_first(
                where={
                    'studentId': student_id,
                    'isActive': True
                }
            )
            
        except Exception as e:
            logger.error(f"Error getting student subscription: {str(e)}")
            return None
        finally:
            await self.disconnect()
    
    async def check_and_expire_subscriptions(self) -> int:
        """Vérifier et expirer les abonnements"""
        try:
            await self.connect()
            
            # Récupérer les abonnements expirés
            expired = await self.db.subscription.find_many(
                where={
                    'isActive': True,
                    'endDate': {'lt': datetime.now()}
                }
            )
            
            # Désactiver les abonnements expirés
            for subscription in expired:
                await self.db.subscription.update(
                    where={'id': subscription.id},
                    data={'isActive': False}
                )
            
            logger.info(f"Expired {len(expired)} subscriptions")
            return len(expired)
            
        except Exception as e:
            logger.error(f"Error expiring subscriptions: {str(e)}")
            return 0
        finally:
            await self.disconnect()
    
    async def get_subscriptions_to_renew(self) -> List[Subscription]:
        """Récupérer les abonnements à renouveler"""
        try:
            await self.connect()
            
            # Abonnements dont la date de renouvellement approche (dans 3 jours)
            renewal_date = datetime.now() + timedelta(days=3)
            
            subscriptions = await self.db.subscription.find_many(
                where={
                    'isActive': True,
                    'autoRenew': True,
                    'isCancelled': False,
                    'nextBillingDate': {'lte': renewal_date}
                }
            )
            
            return subscriptions
            
        except Exception as e:
            logger.error(f"Error getting subscriptions to renew: {str(e)}")
            return []
        finally:
            await self.disconnect()
