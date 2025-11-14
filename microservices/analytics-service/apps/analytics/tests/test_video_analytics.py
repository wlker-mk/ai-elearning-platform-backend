from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
import uuid


class VideoAnalyticsTestCase(TestCase):
    """Tests pour les analytics vidéo"""
    
    def setUp(self):
        self.client = APIClient()
        self.lesson_id = str(uuid.uuid4())
        self.student_id = str(uuid.uuid4())
    
    def test_update_watch_time(self):
        """Test de mise à jour du temps de visionnage"""
        data = {
            'lesson_id': self.lesson_id,
            'student_id': self.student_id,
            'watch_time': 120,
            'position': 240
        }
        
        response = self.client.post('/api/analytics/video/watch-time/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_watch_time', response.data)
        self.assertGreaterEqual(response.data['total_watch_time'], 120)
    
    def test_update_completion_rate(self):
        """Test de mise à jour du taux de complétion"""
        data = {
            'lesson_id': self.lesson_id,
            'student_id': self.student_id,
            'completion_rate': 75.5
        }
        
        response = self.client.post('/api/analytics/video/completion/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('completion_rate', response.data)
        self.assertEqual(response.data['completion_rate'], 75.5)
    
    def test_video_pause_event(self):
        """Test d'événement pause"""
        data = {
            'lesson_id': self.lesson_id,
            'student_id': self.student_id,
            'event_type': 'pause'
        }
        
        response = self.client.post('/api/analytics/video/event/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(response.data['pause_count'], 0)
    
    def test_video_rewind_event(self):
        """Test d'événement rewind"""
        data = {
            'lesson_id': self.lesson_id,
            'student_id': self.student_id,
            'event_type': 'rewind'
        }
        
        response = self.client.post('/api/analytics/video/event/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(response.data['rewind_count'], 0)
