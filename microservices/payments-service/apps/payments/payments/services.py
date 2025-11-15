"""
apps/payments/payments/services.py
Ce module importe le PaymentService depuis gateways.services
pour maintenir la compatibilité.
"""
from apps.payments.gateways.services import PaymentService

__all__ = ['PaymentService']
