from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from prisma import Prisma
from prisma.models import User
import logging
from shared.shared.encryption import PasswordManager, TokenManager
from shared.shared.exceptions import (
    UserAlreadyExistsError,
    WeakPasswordError,
    InvalidCredentialsError,
    AccountLockedError,
    AccountSuspendedError,
    EmailNotVerifiedError
)

logger = logging.getLogger(__name__)


class UserService:
    """Service de gestion des utilisateurs"""
    
    MAX_FAILED_ATTEMPTS = 5
    LOCK_DURATION_MINUTES = 30
    
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
    
    async def create_user(
        self,
        email: str,
        username: str,
        password: str,
        role: str = 'STUDENT'
    ) -> User:
        """Créer un nouveau utilisateur"""
        try:
            await self.connect()
            
            # Vérifier si l'utilisateur existe
            existing_user = await self.db.user.find_first(
                where={
                    'OR': [
                        {'email': email},
                        {'username': username}
                    ]
                }
            )
            
            if existing_user:
                raise UserAlreadyExistsError("User with this email or username already exists")
            
            # Vérifier la force du mot de passe
            is_strong, message = self.password_manager.is_strong_password(password)
            if not is_strong:
                raise WeakPasswordError(message)
            
            # Hash le mot de passe
            password_hash = self.password_manager.hash_password(password)
            
            # Générer un token de vérification d'email
            verification_token = self.token_manager.generate_verification_token()
            verification_expires = datetime.now() + timedelta(hours=24)
            
            # Créer l'utilisateur
            user = await self.db.user.create(
                data={
                    'email': email,
                    'username': username,
                    'passwordHash': password_hash,
                    'role': role,
                    'emailVerificationToken': verification_token,
                    'emailVerificationExpires': verification_expires,
                    'isActive': True,
                    'isEmailVerified': False
                }
            )
            
            logger.info(f"User created: {email}")
            return user
            
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise
        finally:
            await self.disconnect()
    
    async def authenticate_user(
        self,
        email: str,
        password: str,
        check_email_verified: bool = True
    ) -> User:
        """Authentifier un utilisateur"""
        try:
            await self.connect()
            
            # Récupérer l'utilisateur
            user = await self.db.user.find_unique(where={'email': email})
            
            if not user:
                raise InvalidCredentialsError()
            
            # Vérifier si le compte est verrouillé
            if user.lockedUntil and user.lockedUntil > datetime.now():
                raise AccountLockedError(
                    f"Account locked until {user.lockedUntil.strftime('%Y-%m-%d %H:%M:%S')}"
                )
            
            # Vérifier si le compte est suspendu
            if user.isSuspended:
                raise AccountSuspendedError(
                    f"Account suspended: {user.suspensionReason or 'No reason provided'}"
                )
            
            # Vérifier le mot de passe
            if not self.password_manager.verify_password(password, user.passwordHash):
                # Incrémenter les tentatives échouées
                await self._handle_failed_login(user)
                raise InvalidCredentialsError()
            
            # Vérifier si l'email est vérifié
            if check_email_verified and not user.isEmailVerified:
                raise EmailNotVerifiedError()
            
            # Reset les tentatives échouées
            await self.db.user.update(
                where={'id': user.id},
                data={
                    'failedLoginAttempts': 0,
                    'lockedUntil': None
                }
            )
            
            logger.info(f"User authenticated: {email}")
            return user
            
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            raise
        finally:
            await self.disconnect()
    
    async def _handle_failed_login(self, user: User):
        """Gérer les tentatives de connexion échouées"""
        failed_attempts = user.failedLoginAttempts + 1
        
        update_data = {'failedLoginAttempts': failed_attempts}
        
        # Verrouiller le compte après trop de tentatives
        if failed_attempts >= self.MAX_FAILED_ATTEMPTS:
            lock_until = datetime.now() + timedelta(minutes=self.LOCK_DURATION_MINUTES)
            update_data['lockedUntil'] = lock_until
            logger.warning(f"Account locked: {user.email}")
        
        await self.db.user.update(
            where={'id': user.id},
            data=update_data
        )
    
    async def verify_email(self, token: str) -> bool:
        """Vérifier l'email avec le token"""
        try:
            await self.connect()
            
            user = await self.db.user.find_first(
                where={'emailVerificationToken': token}
            )
            
            if not user:
                return False
            
            # Vérifier si le token n'est pas expiré
            if user.emailVerificationExpires and user.emailVerificationExpires < datetime.now():
                return False
            
            # Marquer l'email comme vérifié
            await self.db.user.update(
                where={'id': user.id},
                data={
                    'isEmailVerified': True,
                    'emailVerificationToken': None,
                    'emailVerificationExpires': None
                }
            )
            
            logger.info(f"Email verified: {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Error verifying email: {str(e)}")
            return False
        finally:
            await self.disconnect()
    
    async def request_password_reset(self, email: str) -> Optional[str]:
        """Demander une réinitialisation de mot de passe"""
        try:
            await self.connect()
            
            user = await self.db.user.find_unique(where={'email': email})
            
            if not user:
                # Ne pas révéler si l'email existe ou non
                return None
            
            # Générer un token de reset
            reset_token = self.token_manager.generate_reset_token()
            reset_expires = datetime.now() + timedelta(hours=1)
            
            await self.db.user.update(
                where={'id': user.id},
                data={
                    'resetPasswordToken': reset_token,
                    'resetPasswordExpires': reset_expires
                }
            )
            
            logger.info(f"Password reset requested: {email}")
            return reset_token
            
        except Exception as e:
            logger.error(f"Error requesting password reset: {str(e)}")
            return None
        finally:
            await self.disconnect()
    
    async def reset_password(self, token: str, new_password: str) -> bool:
        """Réinitialiser le mot de passe"""
        try:
            await self.connect()
            
            user = await self.db.user.find_first(
                where={'resetPasswordToken': token}
            )
            
            if not user:
                return False
            
            # Vérifier si le token n'est pas expiré
            if user.resetPasswordExpires and user.resetPasswordExpires < datetime.now():
                return False
            
            # Vérifier la force du nouveau mot de passe
            is_strong, message = self.password_manager.is_strong_password(new_password)
            if not is_strong:
                raise WeakPasswordError(message)
            
            # Hash le nouveau mot de passe
            password_hash = self.password_manager.hash_password(new_password)
            
            # Mettre à jour le mot de passe
            await self.db.user.update(
                where={'id': user.id},
                data={
                    'passwordHash': password_hash,
                    'resetPasswordToken': None,
                    'resetPasswordExpires': None,
                    'failedLoginAttempts': 0,
                    'lockedUntil': None
                }
            )
            
            logger.info(f"Password reset: {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Error resetting password: {str(e)}")
            return False
        finally:
            await self.disconnect()
    
    async def change_password(
        self,
        user_id: str,
        current_password: str,
        new_password: str
    ) -> bool:
        """Changer le mot de passe"""
        try:
            await self.connect()
            
            user = await self.db.user.find_unique(where={'id': user_id})
            
            if not user:
                return False
            
            # Vérifier le mot de passe actuel
            if not self.password_manager.verify_password(current_password, user.passwordHash):
                raise InvalidCredentialsError("Current password is incorrect")
            
            # Vérifier la force du nouveau mot de passe
            is_strong, message = self.password_manager.is_strong_password(new_password)
            if not is_strong:
                raise WeakPasswordError(message)
            
            # Hash le nouveau mot de passe
            password_hash = self.password_manager.hash_password(new_password)
            
            # Mettre à jour
            await self.db.user.update(
                where={'id': user_id},
                data={'passwordHash': password_hash}
            )
            
            logger.info(f"Password changed: {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Error changing password: {str(e)}")
            raise
        finally:
            await self.disconnect()
    
    async def get_user(self, user_id: str) -> Optional[User]:
        """Récupérer un utilisateur"""
        try:
            await self.connect()
            return await self.db.user.find_unique(where={'id': user_id})
        except Exception as e:
            logger.error(f"Error getting user: {str(e)}")
            return None
        finally:
            await self.disconnect()
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Récupérer un utilisateur par email"""
        try:
            await self.connect()
            return await self.db.user.find_unique(where={'email': email})
        except Exception as e:
            logger.error(f"Error getting user by email: {str(e)}")
            return None
        finally:
            await self.disconnect()
    
    async def update_last_login(self, user_id: str, ip_address: Optional[str] = None):
        """Mettre à jour la dernière connexion"""
        try:
            await self.connect()
            
            await self.db.user.update(
                where={'id': user_id},
                data={
                    'lastLoginAt': datetime.now(),
                    'lastLoginIp': ip_address
                }
            )
            
        except Exception as e:
            logger.error(f"Error updating last login: {str(e)}")
        finally:
            await self.disconnect()