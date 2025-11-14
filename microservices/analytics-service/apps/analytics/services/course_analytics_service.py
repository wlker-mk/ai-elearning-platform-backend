from typing import Optional, Dict, Any, List
from datetime import datetime, date, timedelta
from collections import defaultdict
from prisma import Prisma
import logging

logger = logging.getLogger(__name__)


class CourseAnalyticsService:
    """Service pour gérer les analytics de cours"""
    
    def __init__(self):
        self.db = Prisma()
    
    async def connect(self):
        if not self.db.is_connected():
            await self.db.connect()
    
    async def disconnect(self):
        if self.db.is_connected():
            await self.db.disconnect()
    
    async def create_or_update_analytics(
        self,
        course_id: str,
        analytics_date: date,
        views: int = 0,
        enrollments: int = 0,
        completions: int = 0,
        rating: Optional[float] = None
    ):
        """Créer ou mettre à jour les analytics d'un cours"""
        try:
            await self.connect()
            
            # Essayer de récupérer les analytics existantes
            existing = await self.db.courseanalytics.find_unique(
                where={
                    'courseId_date': {
                        'courseId': course_id,
                        'date': analytics_date
                    }
                }
            )
            
            if existing:
                # Mettre à jour
                update_data = {
                    'views': existing.views + views,
                    'enrollments': existing.enrollments + enrollments,
                    'completions': existing.completions + completions
                }
                
                # Mettre à jour la note moyenne si fournie
                if rating is not None:
                    if existing.avgRating is not None:
                        # Calculer la nouvelle moyenne (approximation simple)
                        update_data['avgRating'] = (existing.avgRating + rating) / 2
                    else:
                        update_data['avgRating'] = rating
                
                analytics = await self.db.courseanalytics.update(
                    where={'id': existing.id},
                    data=update_data
                )
            else:
                # Créer
                analytics = await self.db.courseanalytics.create(
                    data={
                        'courseId': course_id,
                        'date': analytics_date,
                        'views': views,
                        'enrollments': enrollments,
                        'completions': completions,
                        'avgRating': rating
                    }
                )
            
            logger.info(f"Course analytics updated: {course_id} - {analytics_date}")
            return analytics
            
        except Exception as e:
            logger.error(f"Error creating/updating course analytics: {str(e)}")
            raise
        finally:
            await self.disconnect()
    
    async def increment_views(
        self,
        course_id: str,
        analytics_date: Optional[date] = None
    ):
        """Incrémenter les vues d'un cours"""
        if analytics_date is None:
            analytics_date = date.today()
        
        return await self.create_or_update_analytics(
            course_id,
            analytics_date,
            views=1
        )
    
    async def increment_enrollments(
        self,
        course_id: str,
        analytics_date: Optional[date] = None
    ):
        """Incrémenter les inscriptions d'un cours"""
        if analytics_date is None:
            analytics_date = date.today()
        
        return await self.create_or_update_analytics(
            course_id,
            analytics_date,
            enrollments=1
        )
    
    async def increment_completions(
        self,
        course_id: str,
        analytics_date: Optional[date] = None
    ):
        """Incrémenter les complétions d'un cours"""
        if analytics_date is None:
            analytics_date = date.today()
        
        return await self.create_or_update_analytics(
            course_id,
            analytics_date,
            completions=1
        )
    
    async def update_rating(
        self,
        course_id: str,
        rating: float,
        analytics_date: Optional[date] = None
    ):
        """Mettre à jour la note d'un cours"""
        if analytics_date is None:
            analytics_date = date.today()
        
        return await self.create_or_update_analytics(
            course_id,
            analytics_date,
            rating=rating
        )
    
    async def get_analytics(
        self,
        course_id: str,
        analytics_date: date
    ):
        """Récupérer les analytics d'un cours pour une date"""
        try:
            await self.connect()
            
            return await self.db.courseanalytics.find_unique(
                where={
                    'courseId_date': {
                        'courseId': course_id,
                        'date': analytics_date
                    }
                }
            )
            
        except Exception as e:
            logger.error(f"Error getting course analytics: {str(e)}")
            raise
        finally:
            await self.disconnect()
    
    async def get_analytics_range(
        self,
        course_id: str,
        start_date: date,
        end_date: date
    ) -> List[Dict[str, Any]]:
        """Récupérer les analytics sur une période"""
        try:
            await self.connect()
            
            analytics = await self.db.courseanalytics.find_many(
                where={
                    'courseId': course_id,
                    'date': {
                        'gte': start_date,
                        'lte': end_date
                    }
                },
                order={'date': 'asc'}
            )
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting analytics range: {str(e)}")
            raise
        finally:
            await self.disconnect()
    
    async def get_total_stats(
        self,
        course_id: str,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """Récupérer les statistiques totales d'un cours"""
        try:
            analytics_list = await self.get_analytics_range(
                course_id,
                start_date,
                end_date
            )
            
            if not analytics_list:
                return {
                    'total_views': 0,
                    'total_enrollments': 0,
                    'total_completions': 0,
                    'avg_rating': None,
                    'conversion_rate': 0.0,
                    'completion_rate': 0.0
                }
            
            total_views = sum(a.views for a in analytics_list)
            total_enrollments = sum(a.enrollments for a in analytics_list)
            total_completions = sum(a.completions for a in analytics_list)
            
            # Calculer la note moyenne
            ratings = [a.avgRating for a in analytics_list if a.avgRating is not None]
            avg_rating = sum(ratings) / len(ratings) if ratings else None
            
            # Calculer les taux
            conversion_rate = (total_enrollments / total_views * 100) if total_views > 0 else 0.0
            completion_rate = (total_completions / total_enrollments * 100) if total_enrollments > 0 else 0.0
            
            return {
                'total_views': total_views,
                'total_enrollments': total_enrollments,
                'total_completions': total_completions,
                'avg_rating': round(avg_rating, 2) if avg_rating else None,
                'conversion_rate': round(conversion_rate, 2),
                'completion_rate': round(completion_rate, 2)
            }
            
        except Exception as e:
            logger.error(f"Error getting total stats: {str(e)}")
            raise
    
    async def get_daily_analytics(
        self,
        course_id: str,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Récupérer les analytics quotidiennes"""
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=days-1)
            
            analytics_list = await self.get_analytics_range(
                course_id,
                start_date,
                end_date
            )
            
            # Créer un dictionnaire pour un accès rapide
            analytics_dict = {
                a.date.strftime('%Y-%m-%d'): a
                for a in analytics_list
            }
            
            # Créer une liste pour tous les jours
            result = []
            current_date = start_date
            while current_date <= end_date:
                date_key = current_date.strftime('%Y-%m-%d')
                analytics = analytics_dict.get(date_key)
                
                result.append({
                    'date': date_key,
                    'views': analytics.views if analytics else 0,
                    'enrollments': analytics.enrollments if analytics else 0,
                    'completions': analytics.completions if analytics else 0,
                    'avg_rating': analytics.avgRating if analytics else None
                })
                
                current_date += timedelta(days=1)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting daily analytics: {str(e)}")
            raise
    
    async def get_top_courses(
        self,
        metric: str = 'views',
        limit: int = 10,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Récupérer les meilleurs cours selon une métrique"""
        try:
            await self.connect()
            
            end_date = date.today()
            start_date = end_date - timedelta(days=days-1)
            
            analytics_list = await self.db.courseanalytics.find_many(
                where={
                    'date': {
                        'gte': start_date,
                        'lte': end_date
                    }
                }
            )
            
            # Grouper par cours
            course_stats = defaultdict(lambda: {
                'views': 0,
                'enrollments': 0,
                'completions': 0
            })
            
            for analytics in analytics_list:
                course_stats[analytics.courseId]['views'] += analytics.views
                course_stats[analytics.courseId]['enrollments'] += analytics.enrollments
                course_stats[analytics.courseId]['completions'] += analytics.completions
            
            # Trier selon la métrique
            sorted_courses = sorted(
                course_stats.items(),
                key=lambda x: x[1][metric],
                reverse=True
            )[:limit]
            
            return [
                {
                    'course_id': course_id,
                    **stats
                }
                for course_id, stats in sorted_courses
            ]
            
        except Exception as e:
            logger.error(f"Error getting top courses: {str(e)}")
            raise
        finally:
            await self.disconnect()