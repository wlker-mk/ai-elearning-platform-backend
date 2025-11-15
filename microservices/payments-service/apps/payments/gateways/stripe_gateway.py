from typing import Dict, Any, Optional
import logging
import stripe
from .base import PaymentGateway

logger = logging.getLogger(__name__)


class StripeGateway(PaymentGateway):
    """Passerelle de paiement Stripe"""
    
    def __init__(self, api_key: str, secret_key: str, **kwargs):
        super().__init__(api_key, secret_key, **kwargs)
        stripe.api_key = self.secret_key
    
    def create_payment_intent(
        self,
        amount: float,
        currency: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Créer une intention de paiement Stripe"""
        try:
            # Stripe utilise les centimes
            amount_cents = int(amount * 100)
            
            payment_intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=currency.lower(),
                metadata=metadata or {},
                automatic_payment_methods={'enabled': True}
            )
            
            return {
                'id': payment_intent.id,
                'client_secret': payment_intent.client_secret,
                'status': payment_intent.status,
                'amount': amount,
                'currency': currency
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe payment intent error: {str(e)}")
            raise
    
    def confirm_payment(self, payment_intent_id: str) -> Dict[str, Any]:
        """Confirmer un paiement Stripe"""
        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            return {
                'id': payment_intent.id,
                'status': payment_intent.status,
                'amount': payment_intent.amount / 100,
                'currency': payment_intent.currency.upper()
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe confirm payment error: {str(e)}")
            raise
    
    def refund_payment(
        self,
        payment_id: str,
        amount: Optional[float] = None
    ) -> Dict[str, Any]:
        """Rembourser un paiement Stripe"""
        try:
            refund_data = {'payment_intent': payment_id}
            
            if amount is not None:
                refund_data['amount'] = int(amount * 100)
            
            refund = stripe.Refund.create(**refund_data)
            
            return {
                'id': refund.id,
                'status': refund.status,
                'amount': refund.amount / 100,
                'currency': refund.currency.upper()
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe refund error: {str(e)}")
            raise
    
    def get_payment_status(self, payment_id: str) -> str:
        """Récupérer le statut d'un paiement Stripe"""
        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_id)
            
            status_mapping = {
                'requires_payment_method': 'PENDING',
                'requires_confirmation': 'PENDING',
                'requires_action': 'PROCESSING',
                'processing': 'PROCESSING',
                'succeeded': 'COMPLETED',
                'canceled': 'CANCELLED',
            }
            
            return status_mapping.get(payment_intent.status, 'PENDING')
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe status error: {str(e)}")
            return 'FAILED'
    
    def create_customer(self, email: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Créer un client Stripe"""
        try:
            customer = stripe.Customer.create(
                email=email,
                metadata=metadata or {}
            )
            
            return customer.id
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe create customer error: {str(e)}")
            raise
    
    def create_subscription(
        self,
        customer_id: str,
        plan_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Créer un abonnement Stripe"""
        try:
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{'price': plan_id}],
                metadata=metadata or {}
            )
            
            return {
                'id': subscription.id,
                'status': subscription.status,
                'current_period_end': subscription.current_period_end
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe create subscription error: {str(e)}")
            raise
    
    def cancel_subscription(self, subscription_id: str) -> bool:
        """Annuler un abonnement Stripe"""
        try:
            stripe.Subscription.delete(subscription_id)
            return True
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe cancel subscription error: {str(e)}")
            return False
