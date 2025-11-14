from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from prisma import Prisma
from prisma.models import LoginHistory
import logging
from shared.shared.utils.ip_utils import parse_user_agent

logger = logging.getLogger(__name__)


class LoginHistoryService:
    """Service de gestion de l'historique de connexion"""
    
    def __init__(self):
        self.db = Prisma()
    
    async def connect(self):
        if not self.db.is_connected():
            await self.db.connect()
    
    async def disconnect(self):
        if self.db.is_connected():
            await self.db.disconnect()
    
    async def log_login_attempt(
        self,
        user_id: str,
        success: bool,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        failure_reason: Optional[str] = None,
        location: Optional[str] = None,
        country: Optional[str] = None,
        city: Optional[str] = None
    ) -> LoginHistory:
        """Enregistrer une tentative de connexion"""
        try:
            await self.connect()
            
            # Parser le user agent
            device_info = parse_user_agent(user_agent or '')
            
            log = await self.db.loginhistory.create(
                data={
                    'userId': user_id,
                    'success': success,
                    'failureReason': failure_reason,
                    'ipAddress': ip_address,
                    'userAgent': user_agent,
                    'location': location,
                    'country': country,
                    'city': city,
                    'device': device_info['device'],
                    'browser': device_info['browser'],
                    'os': device_info['os'],
                    'loginAt': datetime.now()
                }
            )
            
            logger.info(f"Login attempt logged for user: {user_id} - Success: {success}")
            return log
            
        except Exception as e:
            logger.error(f"Error logging login attempt: {str(e)}")
            raise
        finally:
            await self.disconnect()
    
    async def get_user_login_history(
        self,
        user_id: str,
        limit: int = 50,
        success_only: bool = False
    ) -> List[LoginHistory]:
        """Récupérer l'historique de connexion d'un utilisateur"""
        try:
            await self.connect()
            
            where_clause = {'userId': user_id}
            if success_only:
                where_clause['success'] = True
            
            history = await self.db.loginhistory.find_many(
                where=where_clause,
                order={'loginAt': 'desc'},
                take=limit
            )
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting login history: {str(e)}")
            return []
        finally:
            await self.disconnect()
    
    async def get_failed_login_attempts(
        self,
        user_id: str,
        days: int = 7
    ) -> List[LoginHistory]:
        """Récupérer les tentatives de connexion échouées"""
        try:
            await self.connect()
            
            start_date = datetime.now() - timedelta(days=days)
            
            history = await self.db.loginhistory.find_many(
                where={
                    'userId': user_id,
                    'success': False,
                    'loginAt': {'gte': start_date}
                },
                order={'loginAt': 'desc'}
            )
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting failed attempts: {str(e)}")
            return []
        finally:
            await self.disconnect()
    
    async def get_login_statistics(
        self,
        user_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """Récupérer les statistiques de connexion"""
        try:
            await self.connect()
            
            start_date = datetime.now() - timedelta(days=days)
            
            history = await self.db.loginhistory.find_many(
                where={
                    'userId': user_id,
                    'loginAt': {'gte': start_date}
                }
            )
            
            total = len(history)
            successful = sum(1 for h in history if h.success)
            failed = total - successful
            
            # Compter par appareil
            devices = {}
            browsers = {}
            countries = {}
            
            for h in history:
                if h.device:
                    devices[h.device] = devices.get(h.device, 0) + 1
                if h.browser:
                    browsers[h.browser] = browsers.get(h.browser, 0) + 1
                if h.country:
                    countries[h.country] = countries.get(h.country, 0) + 1
            
            return {
                'total_attempts': total,
                'successful_logins': successful,
                'failed_logins': failed,
                'success_rate': round((successful / total * 100) if total > 0 else 0, 2),
                'devices': devices,
                'browsers': browsers,
                'countries': countries,
                'period_days': days
            }
            
        except Exception as e:
            logger.error(f"Error getting login statistics: {str(e)}")
            return {}
        finally:
            await self.disconnect()