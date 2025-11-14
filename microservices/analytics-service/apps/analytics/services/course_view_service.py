from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from prisma import Prisma
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class CourseViewService:
    """Service pour gérer les vues de cours"""
    
    def __init__(self):
        self.db = Prisma()
    
    async def connect(self):
        if not self.db.is_connected():
            await self.db.connect()
    
    async def disconnect(self):
        if self.db.is_connected():
            await self.db.disconnect()
    
    async def track_view(
        self,
        course_id: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        country: Optional[str] = None,
        city: Optional[str] = None,
        referrer: Optional[str] = None,
        source: Optional[str] = None
    ):
        """Enregistrer une vue de cours"""
        try:
            await self.connect()
            
            view = await self.db.courseview.create(
                data={
                    'courseId': course_id,
                    'userId': user_id,
                    'ipAddress': ip_address,
                    'userAgent': user_agent,
                    'country': country,
                    'city': city,
                    'referrer': referrer,
                    'source': source,
                    'viewedAt': datetime.now()
                }
            )
            
            logger.info(f"Course view tracked: {course_id}")
            return view
            
        except Exception as e:
            logger.error(f"Error tracking course view: {str(e)}")
            raise
        finally:
            await self.disconnect()
    
    async def get_course_views(
        self,
        course_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Récupérer les vues d'un cours"""
        try:
            await self.connect()
            
            where_clause = {'courseId': course_id}
            
            if start_date or end_date:
                where_clause['viewedAt'] = {}
                if start_date:
                    where_clause['viewedAt']['gte'] = start_date
                if end_date:
                    where_clause['viewedAt']['lte'] = end_date
            
            views = await self.db.courseview.find_many(
                where=where_clause,
                order={'viewedAt': 'desc'}
            )
            
            return views
            
        except Exception as e:
            logger.error(f"Error fetching course views: {str(e)}")
            raise
        finally:
            await self.disconnect()
    
    async def get_total_views(
        self,
        course_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> int:
        """Compter le nombre total de vues"""
        try:
            await self.connect()
            
            where_clause = {'courseId': course_id}
            
            if start_date or end_date:
                where_clause['viewedAt'] = {}
                if start_date:
                    where_clause['viewedAt']['gte'] = start_date
                if end_date:
                    where_clause['viewedAt']['lte'] = end_date
            
            count = await self.db.courseview.count(where=where_clause)
            return count
            
        except Exception as e:
            logger.error(f"Error counting views: {str(e)}")
            raise
        finally:
            await self.disconnect()
    
    async def get_unique_viewers(
        self,
        course_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> int:
        """Compter le nombre de viewers uniques"""
        try:
            await self.connect()
            
            where_clause = {'courseId': course_id, 'userId': {'not': None}}
            
            if start_date or end_date:
                where_clause['viewedAt'] = {}
                if start_date:
                    where_clause['viewedAt']['gte'] = start_date
                if end_date:
                    where_clause['viewedAt']['lte'] = end_date
            
            views = await self.db.courseview.find_many(
                where=where_clause,
                distinct=['userId']
            )
            
            return len(views)
            
        except Exception as e:
            logger.error(f"Error counting unique viewers: {str(e)}")
            raise
        finally:
            await self.disconnect()
    
    async def get_views_by_country(
        self,
        course_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Récupérer les vues par pays"""
        try:
            await self.connect()
            
            views = await self.db.courseview.find_many(
                where={'courseId': course_id, 'country': {'not': None}},
                order={'viewedAt': 'desc'}
            )
            
            # Grouper par pays
            country_counts = defaultdict(int)
            for view in views:
                if view.country:
                    country_counts[view.country] += 1
            
            # Trier et limiter
            sorted_countries = sorted(
                country_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:limit]
            
            return [
                {'country': country, 'views': count}
                for country, count in sorted_countries
            ]
            
        except Exception as e:
            logger.error(f"Error getting views by country: {str(e)}")
            raise
        finally:
            await self.disconnect()
    
    async def get_views_by_source(
        self,
        course_id: str
    ) -> List[Dict[str, Any]]:
        """Récupérer les vues par source de traffic"""
        try:
            await self.connect()
            
            views = await self.db.courseview.find_many(
                where={'courseId': course_id, 'source': {'not': None}}
            )
            
            # Grouper par source
            source_counts = defaultdict(int)
            for view in views:
                if view.source:
                    source_counts[view.source] += 1
            
            return [
                {'source': source, 'views': count}
                for source, count in source_counts.items()
            ]
            
        except Exception as e:
            logger.error(f"Error getting views by source: {str(e)}")
            raise
        finally:
            await self.disconnect()
    
    async def get_daily_views(
        self,
        course_id: str,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Récupérer les vues quotidiennes"""
        try:
            await self.connect()
            
            start_date = datetime.now() - timedelta(days=days)
            
            views = await self.db.courseview.find_many(
                where={
                    'courseId': course_id,
                    'viewedAt': {'gte': start_date}
                },
                order={'viewedAt': 'asc'}
            )
            
            # Grouper par jour
            daily_counts = defaultdict(int)
            for view in views:
                date_key = view.viewedAt.strftime('%Y-%m-%d')
                daily_counts[date_key] += 1
            
            # Créer une liste pour tous les jours
            result = []
            for i in range(days):
                date = start_date + timedelta(days=i)
                date_key = date.strftime('%Y-%m-%d')
                result.append({
                    'date': date_key,
                    'views': daily_counts.get(date_key, 0)
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting daily views: {str(e)}")
            raise
        finally:
            await self.disconnect()
    
    async def get_views_statistics(
        self,
        course_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """Obtenir les statistiques complètes des vues"""
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            total_views = await self.get_total_views(course_id, start_date)
            unique_viewers = await self.get_unique_viewers(course_id, start_date)
            views_by_country = await self.get_views_by_country(course_id)
            views_by_source = await self.get_views_by_source(course_id)
            daily_views = await self.get_daily_views(course_id, days)
            
            return {
                'totalViews': total_views,
                'uniqueViewers': unique_viewers,
                'viewsByCountry': views_by_country,
                'viewsBySource': views_by_source,
                'dailyViews': daily_views,
                'period': f'Last {days} days'
            }
            
        except Exception as e:
            logger.error(f"Error getting views statistics: {str(e)}")
            raise