from typing import Optional, List, Tuple
from datetime import datetime
from prisma import Prisma
from prisma.models import User
import logging
from shared.shared.encryption import PasswordManager, TokenManager
from shared.shared.exceptions import InvalidMFACodeError
import qrcode
import io
import base64

logger = logging.getLogger(__name__)


class MFAService:
    """Service de gestion de l'authentification multi-facteurs"""
    
    def __init__(self):
        self.db = Prisma()
        self.password_manager = PasswordManager()
        self.token_manager = TokenManager()
    
    async def connect(self):
        if not self.db.is_connected():
            await self.db.connect()
    
    async def disconnect(self):
        if self.db.is_connected():
            await self.db.disconnect()
    
    async def enable_mfa(self, user_id: str) -> Tuple[str, str, List[str]]:
        """Activer le MFA pour un utilisateur"""
        try:
            await self.connect()
            
            user = await self.db.user.find_unique(where={'id': user_id})
            
            if not user:
                raise ValueError("User not found")
            
            # Générer un secret TOTP
            secret = self.token_manager.generate_mfa_secret()
            
            # Générer des codes de backup
            backup_codes = self.password_manager.generate_backup_codes()
            
            # Hash les codes de backup avant de les stocker
            hashed_backup_codes = [
                self.password_manager.hash_password(code)
                for code in backup_codes
            ]
            
            # Générer l'URI TOTP
            totp_uri = self.token_manager.generate_totp_uri(secret, user.email)
            
            # Mettre à jour l'utilisateur (ne pas activer tout de suite)
            await self.db.user.update(
                where={'id': user_id},
                data={
                    'mfaSecret': secret,
                    'backupCodes': hashed_backup_codes
                }
            )
            
            logger.info(f"MFA setup initiated for user: {user_id}")
            return secret, totp_uri, backup_codes
            
        except Exception as e:
            logger.error(f"Error enabling MFA: {str(e)}")
            raise
        finally:
            await self.disconnect()
    
    async def verify_and_activate_mfa(self, user_id: str, code: str) -> bool:
        """Vérifier le code TOTP et activer le MFA"""
        try:
            await self.connect()
            
            user = await self.db.user.find_unique(where={'id': user_id})
            
            if not user or not user.mfaSecret:
                return False
            
            # Vérifier le code TOTP
            if not self.token_manager.verify_totp(user.mfaSecret, code):
                raise InvalidMFACodeError()
            
            # Activer le MFA
            await self.db.user.update(
                where={'id': user_id},
                data={'mfaEnabled': True}
            )
            
            logger.info(f"MFA activated for user: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error activating MFA: {str(e)}")
            raise
        finally:
            await self.disconnect()
    
    async def verify_mfa_code(self, user_id: str, code: str) -> bool:
        """Vérifier un code MFA"""
        try:
            await self.connect()
            
            user = await self.db.user.find_unique(where={'id': user_id})
            
            if not user or not user.mfaEnabled or not user.mfaSecret:
                return False
            
            # Vérifier le code TOTP
            is_valid = self.token_manager.verify_totp(user.mfaSecret, code)
            
            if not is_valid:
                # Essayer avec les codes de backup
                is_valid = await self._verify_backup_code(user, code)
            
            return is_valid
            
        except Exception as e:
            logger.error(f"Error verifying MFA code: {str(e)}")
            return False
        finally:
            await self.disconnect()
    
    async def _verify_backup_code(self, user: User, code: str) -> bool:
        """Vérifier un code de backup"""
        if not user.backupCodes:
            return False
        
        # Vérifier chaque code de backup
        for i, hashed_code in enumerate(user.backupCodes):
            if self.password_manager.verify_password(code, hashed_code):
                # Retirer le code utilisé
                new_backup_codes = [
                    bc for j, bc in enumerate(user.backupCodes) if j != i
                ]
                
                await self.db.user.update(
                    where={'id': user.id},
                    data={'backupCodes': new_backup_codes}
                )
                
                logger.info(f"Backup code used for user: {user.id}")
                return True
        
        return False
    
    async def disable_mfa(self, user_id: str, password: str) -> bool:
        """Désactiver le MFA"""
        try:
            await self.connect()
            
            user = await self.db.user.find_unique(where={'id': user_id})
            
            if not user:
                return False
            
            # Vérifier le mot de passe
            if not self.password_manager.verify_password(password, user.passwordHash):
                raise InvalidMFACodeError("Invalid password")
            
            # Désactiver le MFA
            await self.db.user.update(
                where={'id': user_id},
                data={
                    'mfaEnabled': False,
                    'mfaSecret': None,
                    'backupCodes': []
                }
            )
            
            logger.info(f"MFA disabled for user: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error disabling MFA: {str(e)}")
            raise
        finally:
            await self.disconnect()
    
    async def regenerate_backup_codes(self, user_id: str) -> List[str]:
        """Régénérer les codes de backup"""
        try:
            await self.connect()
            
            # Générer de nouveaux codes
            backup_codes = self.password_manager.generate_backup_codes()
            
            # Hash les codes
            hashed_backup_codes = [
                self.password_manager.hash_password(code)
                for code in backup_codes
            ]
            
            # Mettre à jour
            await self.db.user.update(
                where={'id': user_id},
                data={'backupCodes': hashed_backup_codes}
            )
            
            logger.info(f"Backup codes regenerated for user: {user_id}")
            return backup_codes
            
        except Exception as e:
            logger.error(f"Error regenerating backup codes: {str(e)}")
            raise
        finally:
            await self.disconnect()
    
    def generate_qr_code(self, totp_uri: str) -> str:
        """Générer un QR code pour le TOTP URI"""
        try:
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(totp_uri)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convertir en base64
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/png;base64,{img_str}"
            
        except Exception as e:
            logger.error(f"Error generating QR code: {str(e)}")