import pytest
from datetime import datetime, date
import uuid

# Ces tests nécessitent une base de données de test
pytestmark = pytest.mark.django_db


@pytest.mark.asyncio
class TestCourseViewService:
    """Tests unitaires pour CourseViewService"""
    
    async def test_track_view(self):
        """Test de tracking d'une vue"""
        from apps.analytics.services import CourseViewService
        
        service = CourseViewService()
        course_id = str(uuid.uuid4())
        
        view = await service.track_view(
            course_id=course_id,
            country='USA',
            city='New York'
        )
        
        assert view is not None
        assert view.courseId == course_id
        assert view.country == 'USA'
    
    async def test_get_total_views(self):
        """Test de comptage des vues"""
        from apps.analytics.services import CourseViewService
        
        service = CourseViewService()
        course_id = str(uuid.uuid4())
        
        # Créer quelques vues
        for _ in range(5):
            await service.track_view(course_id=course_id)
        
        count = await service.get_total_views(course_id)
        assert count >= 5


@pytest.mark.asyncio
class TestVideoAnalyticsService:
    """Tests unitaires pour VideoAnalyticsService"""
    
    async def test_create_analytics(self):
        """Test de création d'analytics vidéo"""
        from apps.analytics.services import VideoAnalyticsService
        
        service = VideoAnalyticsService()
        lesson_id = str(uuid.uuid4())
        student_id = str(uuid.uuid4())
        
        analytics = await service.create_or_get_analytics(lesson_id, student_id)
        
        assert analytics is not None
        assert analytics.lessonId == lesson_id
        assert analytics.studentId == student_id
        assert analytics.totalWatchTime == 0
    
    async def test_update_watch_time(self):
        """Test de mise à jour du temps de visionnage"""
        from apps.analytics.services import VideoAnalyticsService
        
        service = VideoAnalyticsService()
        lesson_id = str(uuid.uuid4())
        student_id = str(uuid.uuid4())
        
        # Première mise à jour
        analytics = await service.update_watch_time(lesson_id, student_id, 60, 60)
        assert analytics.totalWatchTime >= 60
        
        # Deuxième mise à jour
        analytics = await service.update_watch_time(lesson_id, student_id, 30, 90)
        assert analytics.totalWatchTime >= 90


@pytest.mark.asyncio
class TestSearchLogService:
    """Tests unitaires pour SearchLogService"""
    
    async def test_log_search(self):
        """Test d'enregistrement de recherche"""
        from apps.analytics.services import SearchLogService
        
        service = SearchLogService()
        
        log = await service.log_search(
            query='python programming',
            results_count=42
        )
        
        assert log is not None
        assert log.query == 'python programming'
        assert log.resultsCount == 42
    
    async def test_get_popular_searches(self):
        """Test de récupération des recherches populaires"""
        from apps.analytics.services import SearchLogService
        
        service = SearchLogService()
        
        # Créer quelques recherches
        for _ in range(3):
            await service.log_search('popular query', 10)
        
        await service.log_search('rare query', 5)
        
        popular = await service.get_popular_searches(limit=5)
        
        assert len(popular) > 0
        assert popular[0]['query'] == 'popular query'

