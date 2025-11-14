from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
import uuid


class CourseViewTestCase(TestCase):
    """Tests pour le tracking des vues de cours"""
    
    def setUp(self):
        self.client = APIClient()
        self.course_id = str(uuid.uuid4())
    
    def test_track_course_view(self):
        """Test de tracking d'une vue de cours"""
        data = {
            'course_id': self.course_id,
            'country': 'USA',
            'city': 'New York',
            'source': 'organic'
        }
        
        response = self.client.post('/api/analytics/course-views/track/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('course_id', response.data)
        self.assertEqual(response.data['country'], 'USA')
    
    def test_get_course_view_stats(self):
        """Test de récupération des statistiques"""
        # Créer d'abord quelques vues
        for _ in range(5):
            self.test_track_course_view()
        
        # Authentifier pour les stats
        # self.client.force_authenticate(user=self.user)
        
        response = self.client.get(f'/api/analytics/course-views/stats/{self.course_id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_views', response.data)