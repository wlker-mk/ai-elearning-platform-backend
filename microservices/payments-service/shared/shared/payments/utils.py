from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any


def calculate_platform_fee(amount: float, percentage: float = 0.10) -> float:
    """Calculer les frais de plateforme"""
    return round(amount * percentage, 2)


def calculate_processing_fee(amount: float, percentage: float = 0.029, fixed: float = 0.30) -> float:
    """Calculer les frais de traitement"""
    return round((amount * percentage) + fixed, 2)


def calculate_net_amount(amount: float, platform_fee: float, processing_fee: float) -> float:
    """Calculer le montant net"""
    return round(amount - platform_fee - processing_fee, 2)


def calculate_tax(amount: float, country_code: str, tax_rates: Dict[str, float]) -> float:
    """Calculer la taxe"""
    tax_rate = tax_rates.get(country_code, 0)
    return round(amount * tax_rate, 2)


def apply_discount(amount: float, discount_type: str, discount_value: float) -> float:
    """Appliquer une réduction"""
    if discount_type == 'PERCENTAGE':
        discount = amount * (discount_value / 100)
    elif discount_type == 'FIXED_AMOUNT':
        discount = discount_value
    else:
        discount = 0
    
    return round(max(0, amount - discount), 2)


def format_currency(amount: float, currency: str = 'USD') -> str:
    """Formater un montant en devise"""
    symbols = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'CAD': 'CA$',
        'AUD': 'A$',
        'JPY': '¥',
        'CNY': '¥',
    }
    
    symbol = symbols.get(currency, currency)
    
    if currency == 'JPY' or currency == 'CNY':
        return f"{symbol}{int(amount)}"
    
    return f"{symbol}{amount:,.2f}"


def generate_invoice_number() -> str:
    """Générer un numéro de facture unique"""
    import random
    import string
    from datetime import datetime
    
    date_part = datetime.now().strftime('%Y%m%d')
    random_part = ''.join(random.choices(string.digits, k=6))
    
    return f"INV-{date_part}-{random_part}"
