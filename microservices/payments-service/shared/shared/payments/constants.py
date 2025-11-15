# Payment Constants
PAYMENT_STATUS = {
    'PENDING': 'PENDING',
    'PROCESSING': 'PROCESSING',
    'COMPLETED': 'COMPLETED',
    'FAILED': 'FAILED',
    'REFUNDED': 'REFUNDED',
    'CANCELLED': 'CANCELLED',
    'DISPUTED': 'DISPUTED',
    'EXPIRED': 'EXPIRED',
}

PAYMENT_METHOD = {
    'CREDIT_CARD': 'CREDIT_CARD',
    'DEBIT_CARD': 'DEBIT_CARD',
    'PAYPAL': 'PAYPAL',
    'STRIPE': 'STRIPE',
    'BANK_TRANSFER': 'BANK_TRANSFER',
    'MOBILE_MONEY': 'MOBILE_MONEY',
    'CRYPTO': 'CRYPTO',
    'APPLE_PAY': 'APPLE_PAY',
    'GOOGLE_PAY': 'GOOGLE_PAY',
}

SUBSCRIPTION_TYPE = {
    'FREE': {'name': 'Free', 'price': 0, 'duration_days': 0},
    'MONTHLY': {'name': 'Monthly', 'price': 29.99, 'duration_days': 30},
    'QUARTERLY': {'name': 'Quarterly', 'price': 79.99, 'duration_days': 90},
    'SEMI_ANNUAL': {'name': 'Semi-Annual', 'price': 149.99, 'duration_days': 180},
    'ANNUAL': {'name': 'Annual', 'price': 279.99, 'duration_days': 365},
    'LIFETIME': {'name': 'Lifetime', 'price': 999.99, 'duration_days': 36500},
    'ENTERPRISE': {'name': 'Enterprise', 'price': None, 'duration_days': 365},
    'STUDENT': {'name': 'Student', 'price': 19.99, 'duration_days': 30},
    'TEAM': {'name': 'Team', 'price': 99.99, 'duration_days': 30},
}

DISCOUNT_TYPE = {
    'PERCENTAGE': 'PERCENTAGE',
    'FIXED_AMOUNT': 'FIXED_AMOUNT',
    'BUNDLE': 'BUNDLE',
    'EARLY_BIRD': 'EARLY_BIRD',
    'FLASH_SALE': 'FLASH_SALE',
}

# Platform Fees
PLATFORM_FEE_PERCENTAGE = 0.10  # 10%
PROCESSING_FEE_PERCENTAGE = 0.029  # 2.9%
PROCESSING_FEE_FIXED = 0.30  # $0.30

# Currency
DEFAULT_CURRENCY = 'USD'
SUPPORTED_CURRENCIES = ['USD', 'EUR', 'GBP', 'CAD', 'AUD', 'JPY', 'CNY']

# Tax Rates (by country)
TAX_RATES = {
    'US': 0.08,   # 8%
    'FR': 0.20,   # 20%
    'UK': 0.20,   # 20%
    'DE': 0.19,   # 19%
    'CA': 0.13,   # 13%
}