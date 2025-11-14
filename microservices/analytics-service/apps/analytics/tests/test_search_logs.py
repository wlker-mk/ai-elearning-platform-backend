
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
import uuid


class SearchLogTestCase(TestCase):
    """Tests pour les logs de recherche"""
    
    def setUp(self):
        self.client = APIClient()
    
    def test_log_search(self):
        """Test d'enregistrement de recherche"""
        data = {
            'query': 'python programming',
            'results_count': 42
        }
        
        response = self.client.post('/api/analytics/search/log/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('query', response.data)
        self.assertEqual(response.data['results_count'], 42)
    
    def test_log_search_with_user(self):
        """Test d'enregistrement avec user_id"""
        user_id = str(uuid.uuid4())
        data = {
            'query': 'django tutorial',
            'results_count': 15,
            'user_id': user_id
        }
        
        response = self.client.post('/api/analytics/search/log/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user_id'], user_id)
    
    def test_log_zero_result_search(self):
        """Test de recherche sans résultats"""
        data = {
            'query': 'nonexistent topic xyz',
            'results_count': 0
        }
        
        response = self.client.post('/api/analytics/search/log/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['results_count'], 0)

