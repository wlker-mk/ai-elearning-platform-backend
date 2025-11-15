from typing import Optional
from .stripe_gateway import StripeGateway
from .paypal_gateway import PayPalGateway
from .base import PaymentGateway
import os


class PaymentGatewayFactory:
    """Factory pour créer des passerelles de paiement"""
    
    @staticmethod
    def create_gateway(gateway_type: str) -> Optional[PaymentGateway]:
        """Créer une passerelle de paiement"""
        
        if gateway_type.upper() == 'STRIPE':
            return StripeGateway(
                api_key=os.getenv('STRIPE_PUBLISHABLE_KEY', ''),
                secret_key=os.getenv('STRIPE_SECRET_KEY', '')
            )
        
        elif gateway_type.upper() == 'PAYPAL':
            return PayPalGateway(
                api_key=os.getenv('PAYPAL_CLIENT_ID', ''),
                secret_key=os.getenv('PAYPAL_SECRET', ''),
                sandbox=os.getenv('PAYPAL_SANDBOX', 'True') == 'True'
            )
        
        return None