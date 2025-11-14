import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional
import pyotp


class TokenManager:
    """Gestionnaire de tokens sécurisé"""
    
    @staticmethod
    def generate_token(length: int = 32) -> str:
        """Générer un token aléatoire sécurisé"""
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def generate_verification_token() -> str:
        """Générer un token de vérification d'email"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def generate_reset_token() -> str:
        """Générer un token de réinitialisation de mot de passe"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def hash_token(token: str) -> str:
        """Hash un token pour stockage sécurisé"""
        return hashlib.sha256(token.encode()).hexdigest()
    
    @staticmethod
    def generate_mfa_secret() -> str:
        """Générer un secret MFA (TOTP)"""
        return pyotp.random_base32()
    
    @staticmethod
    def generate_totp_uri(secret: str, email: str, issuer: str = "LMS Platform") -> str:
        """Générer un URI TOTP pour QR code"""
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(name=email, issuer_name=issuer)
    
    @staticmethod
    def verify_totp(secret: str, code: str) -> bool:
        """Vérifier un code TOTP"""
        try:
            totp = pyotp.TOTP(secret)
            return totp.verify(code, valid_window=1)
        except Exception:
            return False
    
    @staticmethod
    def generate_session_token() -> str:
        """Générer un token de session"""
        return secrets.token_urlsafe(48)
    
    @staticmethod
    def is_token_expired(expires_at: datetime) -> bool:
        """Vérifier si un token est expiré"""
        return datetime.now() > expires_at
