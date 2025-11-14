from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from prisma import Prisma
import logging
from collections import defaultdict
import json

logger = logging.getLogger(__name__)


class UserActivityService:
    """Service pour gérer l'activité des utilisateurs"""
    
    def __init__(self):
        self.db = Prisma()
    
    async def connect(self):
        if not self.db.is_connected():
            await self.db.connect()
    
    async def disconnect(self):
        if self.db.is_connected():
            await self.db.disconnect()
    
    async def track_activity(
        self,
        user_id: str,
        event_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Enregistrer une activité utilisateur"""
        try:
            await self.connect()
            
            activity = await self.db.useractivity.create(
                data={
                    'userId': user_id,
                    'eventType': event_type,
                    'metadata': metadata or {},
                    'createdAt': datetime.now()
                }
            )
            
            logger.info(f"User activity tracked: {user_id} - {event_type}")
            return activity
            
        except Exception as e:
            logger.error(f"Error tracking user activity: {str(e)}")
            raise
        finally:
            await self.disconnect()
    
    async def get_user_activities(
        self,
        user_id: str,
        event_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Récupérer les activités d'un utilisateur"""
        try:
            await self.connect()
            
            where_clause = {'userId': user_id}
            
            if event_type:
                where_clause['eventType'] = event_type
            
            if start_date or end_date:
                where_clause['createdAt'] = {}
                if start_date:
                    where_clause['createdAt']['gte'] = start_date
                if end_date:
                    where_clause['createdAt']['lte'] = end_date
            
            activities = await self.db.useractivity.find_many(
                where=where_clause,
                order={'createdAt': 'desc'},
                take=limit
            )
            
            return activities
            
        except Exception as e:
            logger.error(f"Error getting user activities: {str(e)}")
            raise
        finally:
            await self.disconnect()
    
    async def get_activity_count(
        self,
        user_id: str,
        event_type: Optional[str] = None,
        days: int = 30
    ) -> int:
        """Compter les activités d'un utilisateur"""
        try:
            await self.connect()
            
            start_date = datetime.now() - timedelta(days=days)
            
            where_clause = {
                'userId': user_id,
                'createdAt': {'gte': start_date}
            }
            
            if event_type:
                where_clause['eventType'] = event_type
            
            count = await self.db.useractivity.count(where=where_clause)
            return count
            
        except Exception as e:
            logger.error(f"Error counting activities: {str(e)}")
            raise
        finally:
            await self.disconnect()
    
    async def get_daily_activity(
        self,
        user_id: str,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Récupérer l'activité quotidienne d'un utilisateur"""
        try:
            await self.connect()
            
            start_date = datetime.now() - timedelta(days=days)
            
            activities = await self.db.useractivity.find_many(
                where={
                    'userId': user_id,
                    'createdAt': {'gte': start_date}
                },
                order={'createdAt': 'asc'}
            )
            
            # Grouper par jour
            daily_counts = defaultdict(int)
            for activity in activities:
                date_key = activity.createdAt.strftime('%Y-%m-%d')
                daily_counts[date_key] += 1
            
            # Créer une liste pour tous les jours
            result = []
            for i in range(days):
                date = start_date + timedelta(days=i)
                date_key = date.strftime('%Y-%m-%d')
                result.append({
                    'date': date_key,
                    'count': daily_counts.get(date_key, 0)
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting daily activity: {str(e)}")
            raise
        finally:
            await self.disconnect()
    
    async def get_activity_by_type(
        self,
        user_id: str,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Récupérer les activités groupées par type"""
        try:
            await self.connect()
            
            start_date = datetime.now() - timedelta(days=days)
            
            activities = await self.db.useractivity.find_many(
                where={
                    'userId': user_id,
                    'createdAt': {'gte': start_date}
                }
            )
            
            # Grouper par type
            type_counts = defaultdict(int)
            for activity in activities:
                type_counts[activity.eventType] += 1
            
            return [
                {'event_type': event_type, 'count': count}
                for event_type, count in sorted(
                    type_counts.items(),
                    key=lambda x: x[1],
                    reverse=True
                )
            ]
            
        except Exception as e:
            logger.error(f"Error getting activity by type: {str(e)}")
            raise
        finally:
            await self.disconnect()
    
    async def get_most_active_users(
        self,
        limit: int = 10,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Récupérer les utilisateurs les plus actifs"""
        try:
            await self.connect()
            
            start_date = datetime.now() - timedelta(days=days)
            
            activities = await self.db.useractivity.find_many(
                where={'createdAt': {'gte': start_date}}
            )
            
            # Grouper par utilisateur
            user_counts = defaultdict(int)
            for activity in activities:
                user_counts[activity.userId] += 1
            
            # Trier et limiter
            sorted_users = sorted(
                user_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:limit]
            
            return [
                {'user_id': user_id, 'activity_count': count}
                for user_id, count in sorted_users
            ]
            
        except Exception as e:
            logger.error(f"Error getting most active users: {str(e)}")
            raise
        finally:
            await self.disconnect()