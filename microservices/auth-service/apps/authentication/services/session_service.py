from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from prisma import Prisma
from prisma.models import Session, RefreshToken
import logging
from shared.shared.encryption import TokenManager

logger = logging.getLogger(__name__)


class SessionService:
    """Service de gestion des sessions"""
    
    SESSION_DURATION_HOURS = 24
    REFRESH_TOKEN_DURATION_DAYS = 30
    
    def __init__(self):
        self.db = Prisma()
        self.token_manager = TokenManager()
    
    async def connect(self):
        if not self.db.is_connected():
            await self.db.connect()
    
    async def disconnect(self):
        if self.db.is_connected():
            await self.db.disconnect()
    
    async def create_session(
        self,
        user_id: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        device: Optional[str] = None
    ) -> Session:
        """Créer une nouvelle session"""
        try:
            await self.connect()
            
            # Générer un token de session
            token = self.token_manager.generate_session_token()
            expires_at = datetime.now() + timedelta(hours=self.SESSION_DURATION_HOURS)
            
            session = await self.db.session.create(
                data={
                    'userId': user_id,
                    'token': token,
                    'expiresAt': expires_at,
                    'ipAddress': ip_address,
                    'userAgent': user_agent,
                    'device': device,
                    'isValid': True
                }
            )
            
            logger.info(f"Session created for user: {user_id}")
            return session
            
        except Exception as e:
            logger.error(f"Error creating session: {str(e)}")
            raise
        finally:
            await self.disconnect()
    
    async def create_refresh_token(
        self,
        user_id: str,
        device_id: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> RefreshToken:
        """Créer un refresh token"""
        try:
            await self.connect()
            
            token = self.token_manager.generate_token(64)
            expires_at = datetime.now() + timedelta(days=self.REFRESH_TOKEN_DURATION_DAYS)
            
            refresh_token = await self.db.refreshtoken.create(
                data={
                    'userId': user_id,
                    'token': token,
                    'expiresAt': expires_at,
                    'deviceId': device_id,
                    'ipAddress': ip_address,
                    'isRevoked': False
                }
            )
            
            logger.info(f"Refresh token created for user: {user_id}")
            return refresh_token
            
        except Exception as e:
            logger.error(f"Error creating refresh token: {str(e)}")
            raise
        finally:
            await self.disconnect()
    
    async def validate_session(self, token: str) -> Optional[Session]:
        """Valider une session"""
        try:
            await self.connect()
            
            session = await self.db.session.find_unique(
                where={'token': token}
            )
            
            if not session:
                return None
            
            # Vérifier si la session est valide et non expirée
            if not session.isValid or session.expiresAt < datetime.now():
                return None
            
            return session
            
        except Exception as e:
            logger.error(f"Error validating session: {str(e)}")
            return None
        finally:
            await self.disconnect()
    
    async def validate_refresh_token(self, token: str) -> Optional[RefreshToken]:
        """Valider un refresh token"""
        try:
            await self.connect()
            
            refresh_token = await self.db.refreshtoken.find_unique(
                where={'token': token}
            )
            
            if not refresh_token:
                return None
            
            # Vérifier si le token n'est pas révoqué et non expiré
            if refresh_token.isRevoked or refresh_token.expiresAt < datetime.now():
                return None
            
            return refresh_token
            
        except Exception as e:
            logger.error(f"Error validating refresh token: {str(e)}")
            return None
        finally:
            await self.disconnect()
    
    async def refresh_session(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """Rafraîchir une session avec un refresh token"""
        try:
            await self.connect()
            
            # Valider le refresh token
            token_obj = await self.validate_refresh_token(refresh_token)
            
            if not token_obj:
                return None
            
            # Créer une nouvelle session
            new_session = await self.create_session(token_obj.userId)
            
            # Créer un nouveau refresh token
            new_refresh_token = await self.create_refresh_token(
                token_obj.userId,
                token_obj.deviceId,
                token_obj.ipAddress
            )
            
            # Révoquer l'ancien refresh token
            await self.revoke_refresh_token(refresh_token)
            
            return {
                'session_token': new_session.token,
                'refresh_token': new_refresh_token.token,
                'expires_at': new_session.expiresAt
            }
            
        except Exception as e:
            logger.error(f"Error refreshing session: {str(e)}")
            return None
        finally:
            await self.disconnect()
    
    async def invalidate_session(self, token: str) -> bool:
        """Invalider une session (logout)"""
        try:
            await self.connect()
            
            await self.db.session.update(
                where={'token': token},
                data={'isValid': False}
            )
            
            logger.info(f"Session invalidated: {token[:10]}...")
            return True
            
        except Exception as e:
            logger.error(f"Error invalidating session: {str(e)}")
            return False
        finally:
            await self.disconnect()
    
    async def revoke_refresh_token(self, token: str) -> bool:
        """Révoquer un refresh token"""
        try:
            await self.connect()
            
            await self.db.refreshtoken.update(
                where={'token': token},
                data={
                    'isRevoked': True,
                    'revokedAt': datetime.now()
                }
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error revoking refresh token: {str(e)}")
            return False
        finally:
            await self.disconnect()
    
    async def get_user_sessions(self, user_id: str) -> List[Session]:
        """Récupérer toutes les sessions d'un utilisateur"""
        try:
            await self.connect()
            
            sessions = await self.db.session.find_many(
                where={
                    'userId': user_id,
                    'isValid': True,
                    'expiresAt': {'gt': datetime.now()}
                },
                order={'createdAt': 'desc'}
            )
            
            return sessions
            
        except Exception as e:
            logger.error(f"Error getting user sessions: {str(e)}")
            return []
        finally:
            await self.disconnect()
    
    async def revoke_all_sessions(self, user_id: str, except_token: Optional[str] = None) -> int:
        """Révoquer toutes les sessions d'un utilisateur"""
        try:
            await self.connect()
            
            where_clause = {'userId': user_id}
            if except_token:
                where_clause['token'] = {'not': except_token}
            
            result = await self.db.session.update_many(
                where=where_clause,
                data={'isValid': False}
            )
            
            logger.info(f"All sessions revoked for user: {user_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error revoking all sessions: {str(e)}")
            return 0
        finally:
            await self.disconnect()
    
    async def cleanup_expired_sessions(self) -> int:
        """Nettoyer les sessions expirées"""
        try:
            await self.connect()
            
            result = await self.db.session.delete_many(
                where={'expiresAt': {'lt': datetime.now()}}
            )
            
            logger.info(f"Cleaned up {result} expired sessions")
            return result
            
        except Exception as e:
            logger.error(f"Error cleaning up sessions: {str(e)}")
            return 0
        finally:
            await self.disconnect()