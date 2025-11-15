from typing import Dict, Any, Optional
import logging
import requests
from .base import PaymentGateway

logger = logging.getLogger(__name__)


class PayPalGateway(PaymentGateway):
    """Passerelle de paiement PayPal"""
    
    BASE_URL_SANDBOX = 'https://api-m.sandbox.paypal.com'
    BASE_URL_LIVE = 'https://api-m.paypal.com'
    
    def __init__(self, api_key: str, secret_key: str, **kwargs):
        super().__init__(api_key, secret_key, **kwargs)
        self.base_url = self.BASE_URL_SANDBOX if kwargs.get('sandbox', True) else self.BASE_URL_LIVE
        self.access_token = None
    
    def _get_access_token(self) -> str:
        """Obtenir un token d'accès PayPal"""
        if self.access_token:
            return self.access_token
        
        try:
            response = requests.post(
                f"{self.base_url}/v1/oauth2/token",
                auth=(self.api_key, self.secret_key),
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                data={'grant_type': 'client_credentials'}
            )
            response.raise_for_status()
            
            self.access_token = response.json()['access_token']
            return self.access_token
            
        except requests.RequestException as e:
            logger.error(f"PayPal token error: {str(e)}")
            raise
    
    def create_payment_intent(
        self,
        amount: float,
        currency: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Créer un ordre de paiement PayPal"""
        try:
            token = self._get_access_token()
            
            response = requests.post(
                f"{self.base_url}/v2/checkout/orders",
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {token}'
                },
                json={
                    'intent': 'CAPTURE',
                    'purchase_units': [{
                        'amount': {
                            'currency_code': currency,
                            'value': str(amount)
                        }
                    }]
                }
            )
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'id': data['id'],
                'status': data['status'],
                'amount': amount,
                'currency': currency
            }
            
        except requests.RequestException as e:
            logger.error(f"PayPal create order error: {str(e)}")
            raise
    
    def confirm_payment(self, payment_intent_id: str) -> Dict[str, Any]:
        """Capturer un paiement PayPal"""
        try:
            token = self._get_access_token()
            
            response = requests.post(
                f"{self.base_url}/v2/checkout/orders/{payment_intent_id}/capture",
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {token}'
                }
            )
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'id': data['id'],
                'status': data['status']
            }
            
        except requests.RequestException as e:
            logger.error(f"PayPal capture error: {str(e)}")
            raise
    
    def refund_payment(
        self,
        payment_id: str,
        amount: Optional[float] = None
    ) -> Dict[str, Any]:
        """Rembourser un paiement PayPal"""
        try:
            token = self._get_access_token()
            
            refund_data = {}
            if amount is not None:
                refund_data['amount'] = {
                    'value': str(amount),
                    'currency_code': 'USD'
                }
            
            response = requests.post(
                f"{self.base_url}/v2/payments/captures/{payment_id}/refund",
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {token}'
                },
                json=refund_data
            )
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'id': data['id'],
                'status': data['status']
            }
            
        except requests.RequestException as e:
            logger.error(f"PayPal refund error: {str(e)}")
            raise
    
    def get_payment_status(self, payment_id: str) -> str:
        """Récupérer le statut d'un paiement PayPal"""
        try:
            token = self._get_access_token()
            
            response = requests.get(
                f"{self.base_url}/v2/checkout/orders/{payment_id}",
                headers={'Authorization': f'Bearer {token}'}
            )
            response.raise_for_status()
            
            data = response.json()
            
            status_mapping = {
                'CREATED': 'PENDING',
                'SAVED': 'PENDING',
                'APPROVED': 'PROCESSING',
                'COMPLETED': 'COMPLETED',
                'VOIDED': 'CANCELLED',
            }
            
            return status_mapping.get(data['status'], 'PENDING')
            
        except requests.RequestException as e:
            logger.error(f"PayPal status error: {str(e)}")
            return 'FAILED'
    
    def create_customer(self, email: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """PayPal n'utilise pas de création de client explicite"""
        return email
    
    def create_subscription(
        self,
        customer_id: str,
        plan_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Créer un abonnement PayPal"""
        # Implémentation simplifiée
        raise NotImplementedError("PayPal subscriptions not implemented")
    
    def cancel_subscription(self, subscription_id: str) -> bool:
        """Annuler un abonnement PayPal"""
        raise NotImplementedError("PayPal subscriptions not implemented")