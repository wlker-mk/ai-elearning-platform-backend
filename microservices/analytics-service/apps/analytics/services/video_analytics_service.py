from typing import Optional, Dict, Any, List
from datetime import datetime
from prisma import Prisma
import logging

logger = logging.getLogger(__name__)


class VideoAnalyticsService:
    """Service pour gérer les analytics vidéo"""
    
    def __init__(self):
        self.db = Prisma()
    
    async def connect(self):
        if not self.db.is_connected():
            await self.db.connect()
    
    async def disconnect(self):
        if self.db.is_connected():
            await self.db.disconnect()
    
    async def create_or_get_analytics(
        self,
        lesson_id: str,
        student_id: str
    ):
        """Créer ou récupérer les analytics d'une vidéo"""
        try:
            await self.connect()
            
            # Essayer de récupérer
            analytics = await self.db.videoanalytics.find_unique(
                where={
                    'lessonId_studentId': {
                        'lessonId': lesson_id,
                        'studentId': student_id
                    }
                }
            )
            
            if analytics:
                return analytics
            
            # Créer si n'existe pas
            analytics = await self.db.videoanalytics.create(
                data={
                    'lessonId': lesson_id,
                    'studentId': student_id,
                    'totalWatchTime': 0,
                    'completionRate': 0.0,
                    'pauseCount': 0,
                    'rewindCount': 0,
                    'speedChanges': 0,
                    'lastPosition': 0
                }
            )
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error creating/getting video analytics: {str(e)}")
            raise
        finally:
            await self.disconnect()
    
    async def update_watch_time(
        self,
        lesson_id: str,
        student_id: str,
        watch_time: int,
        position: int
    ):
        """Mettre à jour le temps de visionnage"""
        try:
            await self.connect()
            
            analytics = await self.create_or_get_analytics(lesson_id, student_id)
            
            updated = await self.db.videoanalytics.update(
                where={'id': analytics.id},
                data={
                    'totalWatchTime': analytics.totalWatchTime + watch_time,
                    'lastPosition': position
                }
            )
            
            logger.info(f"Watch time updated: {lesson_id} - {student_id}")
            return updated
            
        except Exception as e:
            logger.error(f"Error updating watch time: {str(e)}")
            raise
        finally:
            await self.disconnect()
    
    async def update_completion_rate(
        self,
        lesson_id: str,
        student_id: str,
        completion_rate: float
    ):
        """Mettre à jour le taux de complétion"""
        try:
            await self.connect()
            
            analytics = await self.create_or_get_analytics(lesson_id, student_id)
            
            # Prendre le maximum entre l'ancien et le nouveau taux
            new_rate = max(analytics.completionRate, completion_rate)
            
            updated = await self.db.videoanalytics.update(
                where={'id': analytics.id},
                data={'completionRate': new_rate}
            )
            
            return updated
            
        except Exception as e:
            logger.error(f"Error updating completion rate: {str(e)}")
            raise
        finally:
            await self.disconnect()
    
    async def increment_pause_count(
        self,
        lesson_id: str,
        student_id: str
    ):
        """Incrémenter le compteur de pauses"""
        try:
            await self.connect()
            
            analytics = await self.create_or_get_analytics(lesson_id, student_id)
            
            updated = await self.db.videoanalytics.update(
                where={'id': analytics.id},
                data={'pauseCount': analytics.pauseCount + 1}
            )
            
            return updated
            
        except Exception as e:
            logger.error(f"Error incrementing pause count: {str(e)}")
            raise
        finally:
            await self.disconnect()
    
    async def increment_rewind_count(
        self,
        lesson_id: str,
        student_id: str
    ):
        """Incrémenter le compteur de retours arrière"""
        try:
            await self.connect()
            
            analytics = await self.create_or_get_analytics(lesson_id, student_id)
            
            updated = await self.db.videoanalytics.update(
                where={'id': analytics.id},
                data={'rewindCount': analytics.rewindCount + 1}
            )
            
            return updated
            
        except Exception as e:
            logger.error(f"Error incrementing rewind count: {str(e)}")
            raise
        finally:
            await self.disconnect()
    
    async def increment_speed_changes(
        self,
        lesson_id: str,
        student_id: str
    ):
        """Incrémenter le compteur de changements de vitesse"""
        try:
            await self.connect()
            
            analytics = await self.create_or_get_analytics(lesson_id, student_id)
            
            updated = await self.db.videoanalytics.update(
                where={'id': analytics.id},
                data={'speedChanges': analytics.speedChanges + 1}
            )
            
            return updated
            
        except Exception as e:
            logger.error(f"Error incrementing speed changes: {str(e)}")
            raise
        finally:
            await self.disconnect()
    
    async def update_quality(
        self,
        lesson_id: str,
        student_id: str,
        quality: str
    ):
        """Mettre à jour la qualité moyenne"""
        try:
            await self.connect()
            
            analytics = await self.create_or_get_analytics(lesson_id, student_id)
            
            updated = await self.db.videoanalytics.update(
                where={'id': analytics.id},
                data={'avgQuality': quality}
            )
            
            return updated
            
        except Exception as e:
            logger.error(f"Error updating quality: {str(e)}")
            raise
        finally:
            await self.disconnect()
    
    async def get_analytics(
        self,
        lesson_id: str,
        student_id: str
    ):
        """Récupérer les analytics d'une vidéo"""
        try:
            await self.connect()
            
            return await self.db.videoanalytics.find_unique(
                where={
                    'lessonId_studentId': {
                        'lessonId': lesson_id,
                        'studentId': student_id
                    }
                }
            )
            
        except Exception as e:
            logger.error(f"Error getting video analytics: {str(e)}")
            raise
        finally:
            await self.disconnect()
    
    async def get_lesson_analytics(
        self,
        lesson_id: str
    ) -> List[Dict[str, Any]]:
        """Récupérer toutes les analytics d'une leçon"""
        try:
            await self.connect()
            
            return await self.db.videoanalytics.find_many(
                where={'lessonId': lesson_id}
            )
            
        except Exception as e:
            logger.error(f"Error getting lesson analytics: {str(e)}")
            raise
        finally:
            await self.disconnect()
    
    async def get_student_analytics(
        self,
        student_id: str
    ) -> List[Dict[str, Any]]:
        """Récupérer toutes les analytics d'un étudiant"""
        try:
            await self.connect()
            
            return await self.db.videoanalytics.find_many(
                where={'studentId': student_id},
                order={'updatedAt': 'desc'}
            )
            
        except Exception as e:
            logger.error(f"Error getting student analytics: {str(e)}")
            raise
        finally:
            await self.disconnect()
    
    async def get_average_completion_rate(
        self,
        lesson_id: str
    ) -> float:
        """Calculer le taux de complétion moyen d'une leçon"""
        try:
            await self.connect()
            
            analytics_list = await self.get_lesson_analytics(lesson_id)
            
            if not analytics_list:
                return 0.0
            
            total = sum(a.completionRate for a in analytics_list)
            return round(total / len(analytics_list), 2)
            
        except Exception as e:
            logger.error(f"Error calculating avg completion rate: {str(e)}")
            raise
        finally:
            await self.disconnect()
    
    async def get_engagement_stats(
        self,
        lesson_id: str
    ) -> Dict[str, Any]:
        """Récupérer les statistiques d'engagement d'une leçon"""
        try:
            await self.connect()
            
            analytics_list = await self.get_lesson_analytics(lesson_id)
            
            if not analytics_list:
                return {
                    'total_students': 0,
                    'avg_watch_time': 0,
                    'avg_completion_rate': 0.0,
                    'avg_pauses': 0,
                    'avg_rewinds': 0,
                    'avg_speed_changes': 0
                }
            
            total = len(analytics_list)
            
            return {
                'total_students': total,
                'avg_watch_time': sum(a.totalWatchTime for a in analytics_list) // total,
                'avg_completion_rate': round(sum(a.completionRate for a in analytics_list) / total, 2),
                'avg_pauses': sum(a.pauseCount for a in analytics_list) // total,
                'avg_rewinds': sum(a.rewindCount for a in analytics_list) // total,
                'avg_speed_changes': sum(a.speedChanges for a in analytics_list) // total
            }
            
        except Exception as e:
            logger.error(f"Error getting engagement stats: {str(e)}")
            raise
        finally:
            await self.disconnect()