from typing import Optional, Dict, Any, List
from datetime import datetime
from prisma import Prisma
from prisma.models import Payment, Transaction
import logging
from shared.shared.payments.utils import (
    calculate_platform_fee,
    calculate_processing_fee,
    calculate_net_amount
)
from apps.payments.gateways.factory import PaymentGatewayFactory

logger = logging.getLogger(__name__)


class PaymentService:
    """Service de gestion des paiements"""
    
    def __init__(self):
        self.db = Prisma()
    
    async def connect(self):
        if not self.db.is_connected():
            await self.db.connect()
    
    async def disconnect(self):
        if self.db.is_connected():
            await self.db.disconnect()
    
    async def create_payment(
        self,
        student_id: str,
        amount: float,
        currency: str,
        method: str,
        course_id: Optional[str] = None,
        subscription_id: Optional[str] = None,
        items: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Payment:
        """Créer un nouveau paiement"""
        try:
            await self.connect()
            
            # Calculer les frais
            processing_fee = calculate_processing_fee(amount)
            platform_fee = calculate_platform_fee(amount)
            net_amount = calculate_net_amount(amount, platform_fee, processing_fee)
            
            # Créer le paiement
            payment = await self.db.payment.create(
                data={
                    'studentId': student_id,
                    'amount': amount,
                    'currency': currency,
                    'method': method,
                    'status': 'PENDING',
                    'courseId': course_id,
                    'subscriptionId': subscription_id,
                    'items': items or {},
                    'description': description,
                    'metadata': metadata or {},
                    'processingFee': processing_fee,
                    'platformFee': platform_fee,
                    'netAmount': net_amount
                }
            )
            
            logger.info(f"Payment created: {payment.id}")
            return payment
            
        except Exception as e:
            logger.error(f"Error creating payment: {str(e)}")
            raise
        finally:
            await self.disconnect()
    
    async def process_payment(
        self,
        payment_id: str,
        gateway_type: str
    ) -> Payment:
        """Traiter un paiement via une passerelle"""
        try:
            await self.connect()
            
            # Récupérer le paiement
            payment = await self.db.payment.find_unique(where={'id': payment_id})
            
            if not payment:
                raise ValueError("Payment not found")
            
            # Créer la passerelle
            gateway = PaymentGatewayFactory.create_gateway(gateway_type)
            
            if not gateway:
                raise ValueError(f"Gateway {gateway_type} not supported")
            
            # Mettre à jour le statut
            await self.db.payment.update(
                where={'id': payment_id},
                data={'status': 'PROCESSING'}
            )
            
            # Créer l'intention de paiement
            payment_intent = gateway.create_payment_intent(
                amount=payment.amount,
                currency=payment.currency,
                metadata={
                    'payment_id': payment.id,
                    'student_id': payment.studentId
                }
            )
            
            # Mettre à jour avec la référence externe
            updated_payment = await self.db.payment.update(
                where={'id': payment_id},
                data={
                    'externalReference': payment_intent['id'],
                    'gatewayResponse': payment_intent
                }
            )
            
            logger.info(f"Payment processed: {payment_id}")
            return updated_payment
            
        except Exception as e:
            logger.error(f"Error processing payment: {str(e)}")
            
            # Marquer comme échoué
            await self.db.payment.update(
                where={'id': payment_id},
                data={'status': 'FAILED'}
            )
            
            raise
        finally:
            await self.disconnect()
    
    async def confirm_payment(
        self,
        payment_id: str,
        transaction_id: str
    ) -> Payment:
        """Confirmer un paiement"""
        try:
            await self.connect()
            
            payment = await self.db.payment.update(
                where={'id': payment_id},
                data={
                    'status': 'COMPLETED',
                    'transactionId': transaction_id,
                    'paidAt': datetime.now()
                }
            )
            
            # Créer une transaction
            await self.db.transaction.create(
                data={
                    'paymentId': payment_id,
                    'type': 'payment',
                    'amount': payment.amount,
                    'currency': payment.currency,
                    'status': 'COMPLETED',
                    'gatewayId': transaction_id
                }
            )
            
            logger.info(f"Payment confirmed: {payment_id}")
            return payment
            
        except Exception as e:
            logger.error(f"Error confirming payment: {str(e)}")
            raise
        finally:
            await self.disconnect()
    
    async def refund_payment(
        self,
        payment_id: str,
        amount: Optional[float] = None,
        reason: Optional[str] = None
    ) -> Payment:
        """Rembourser un paiement"""
        try:
            await self.connect()
            
            payment = await self.db.payment.find_unique(where={'id': payment_id})
            
            if not payment:
                raise ValueError("Payment not found")
            
            if payment.status != 'COMPLETED':
                raise ValueError("Can only refund completed payments")
            
            # Montant à rembourser
            refund_amount = amount or payment.amount
            
            if refund_amount > payment.amount:
                raise ValueError("Refund amount exceeds payment amount")
            
            # Mettre à jour le paiement
            updated_payment = await self.db.payment.update(
                where={'id': payment_id},
                data={
                    'status': 'REFUNDED',
                    'isRefunded': True,
                    'refundedAmount': refund_amount,
                    'refundedAt': datetime.now()
                }
            )
            
            # Créer une transaction de remboursement
            await self.db.transaction.create(
                data={
                    'paymentId': payment_id,
                    'type': 'refund',
                    'amount': -refund_amount,
                    'currency': payment.currency,
                    'status': 'COMPLETED'
                }
            )
            
            logger.info(f"Payment refunded: {payment_id}")
            return updated_payment
            
        except Exception as e:
            logger.error(f"Error refunding payment: {str(e)}")
            raise
        finally:
            await self.disconnect()
    
    async def get_payment(self, payment_id: str) -> Optional[Payment]:
        """Récupérer un paiement"""
        try:
            await self.connect()
            return await self.db.payment.find_unique(where={'id': payment_id})
        except Exception as e:
            logger.error(f"Error getting payment: {str(e)}")
            return None
        finally:
            await self.disconnect()
    
    async def get_student_payments(
        self,
        student_id: str,
        status: Optional[str] = None,
        limit: int = 50
    ) -> List[Payment]:
        """Récupérer les paiements d'un étudiant"""
        try:
            await self.connect()
            
            where_clause = {'studentId': student_id}
            if status:
                where_clause['status'] = status
            
            payments = await self.db.payment.find_many(
                where=where_clause,
                order={'createdAt': 'desc'},
                take=limit
            )
            
            return payments
            
        except Exception as e:
            logger.error(f"Error getting student payments: {str(e)}")
            return []
        finally:
            await self.disconnect()
    
    async def get_payment_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Récupérer les statistiques de paiement"""
        try:
            await self.connect()
            
            where_clause = {}
            if start_date or end_date:
                where_clause['createdAt'] = {}
                if start_date:
                    where_clause['createdAt']['gte'] = start_date
                if end_date:
                    where_clause['createdAt']['lte'] = end_date
            
            payments = await self.db.payment.find_many(where=where_clause)
            
            total = len(payments)
            completed = sum(1 for p in payments if p.status == 'COMPLETED')
            failed = sum(1 for p in payments if p.status == 'FAILED')
            refunded = sum(1 for p in payments if p.status == 'REFUNDED')
            
            total_amount = sum(p.amount for p in payments if p.status == 'COMPLETED')
            total_platform_fees = sum(p.platformFee for p in payments if p.status == 'COMPLETED')
            total_net = sum(p.netAmount for p in payments if p.status == 'COMPLETED')
            
            return {
                'total_payments': total,
                'completed': completed,
                'failed': failed,
                'refunded': refunded,
                'success_rate': round((completed / total * 100) if total > 0 else 0, 2),
                'total_amount': round(total_amount, 2),
                'total_platform_fees': round(total_platform_fees, 2),
                'total_net_amount': round(total_net, 2)
            }
            
        except Exception as e:
            logger.error(f"Error getting payment statistics: {str(e)}")
            return {}
        finally:
            await self.disconnect()
