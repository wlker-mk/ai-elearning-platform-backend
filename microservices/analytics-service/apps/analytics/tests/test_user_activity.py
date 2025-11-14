from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
import uuid


class UserActivityTestCase(TestCase):
    """Tests pour l'activité utilisateur"""
    
    def setUp(self):
        self.client = APIClient()
        self.user_id = str(uuid.uuid4())
    
    def test_track_activity(self):
        """Test d'enregistrement d'activité"""
        data = {
            'user_id': self.user_id,
            'event_type': 'course_enrolled',
            'metadata': {
                'course_id': str(uuid.uuid4()),
                'category': 'programming'
            }
        }
        
        response = self.client.post('/api/analytics/activity/track/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('event_type', response.data)
        self.assertEqual(response.data['event_type'], 'course_enrolled')
    
    def test_track_multiple_activities(self):
        """Test d'enregistrement de multiples activités"""
        events = [
            'course_viewed',
            'lesson_started',
            'lesson_completed',
            'quiz_attempted'
        ]
        
        for event in events:
            data = {
                'user_id': self.user_id,
                'event_type': event
            }
            response = self.client.post('/api/analytics/activity/track/', data, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
