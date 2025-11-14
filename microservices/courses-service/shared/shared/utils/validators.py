import re
from typing import Optional

def validate_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    pattern = r'^\+?1?\d{9,15}
    return bool(re.match(pattern, phone))

def validate_password_strength(password: str) -> Optional[str]:
    if len(password) < 8:
        return "Password must be at least 8 characters"
    if not re.search(r'[A-Z]', password):
        return "Password must contain uppercase letter"
    if not re.search(r'[a-z]', password):
        return "Password must contain lowercase letter"
    if not re.search(r'\d', password):
        return "Password must contain digit"
    return None
