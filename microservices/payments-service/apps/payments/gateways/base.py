from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class PaymentGateway(ABC):
    """Interface de base pour les passerelles de paiement"""
    
    def __init__(self, api_key: str, secret_key: str, **kwargs):
        self.api_key = api_key
        self.secret_key = secret_key
        self.config = kwargs
    
    @abstractmethod
    def create_payment_intent(
        self,
        amount: float,
        currency: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Créer une intention de paiement"""
        pass
    
    @abstractmethod
    def confirm_payment(self, payment_intent_id: str) -> Dict[str, Any]:
        """Confirmer un paiement"""
        pass
    
    @abstractmethod
    def refund_payment(
        self,
        payment_id: str,
        amount: Optional[float] = None
    ) -> Dict[str, Any]:
        """Rembourser un paiement"""
        pass
    
    @abstractmethod
    def get_payment_status(self, payment_id: str) -> str:
        """Récupérer le statut d'un paiement"""
        pass
    
    @abstractmethod
    def create_customer(self, email: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Créer un client"""
        pass
    
    @abstractmethod
    def create_subscription(
        self,
        customer_id: str,
        plan_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Créer un abonnement"""
        pass
    
    @abstractmethod
    def cancel_subscription(self, subscription_id: str) -> bool:
        """Annuler un abonnement"""
        pass