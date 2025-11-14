from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date
import uuid


class CourseAnalyticsTestCase(TestCase):
    """Tests pour les analytics de cours"""
    
    def setUp(self):
        self.client = APIClient()
        self.course_id = str(uuid.uuid4())
    
    def test_update_course_analytics(self):
        """Test de mise à jour des analytics"""
        data = {
            'course_id': self.course_id,
            'date': str(date.today()),
            'views': 150,
            'enrollments': 25,
            'completions': 5,
            'rating': 4.5
        }
        
        response = self.client.post('/api/analytics/course/analytics/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('views', response.data)
        self.assertEqual(response.data['views'], 150)
    
    def test_increment_views(self):
        """Test d'incrémentation des vues"""
        today = str(date.today())
        
        # Premier update
        data1 = {'course_id': self.course_id, 'date': today, 'views': 100}
        self.client.post('/api/analytics/course/analytics/', data1, format='json')
        
        # Deuxième update
        data2 = {'course_id': self.course_id, 'date': today, 'views': 50}
        response = self.client.post('/api/analytics/course/analytics/', data2, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['views'], 150)
