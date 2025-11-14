from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
import uuid

User = get_user_model()


class InstructorTestCase(TestCase):
    """Tests pour les instructeurs"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            id=uuid.uuid4(),
            email='instructor@example.com',
            username='instructor',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_create_instructor(self):
        """Test de création de profil instructeur"""
        data = {
            'title': 'Senior Developer',
            'headline': 'Expert in Python and Django',
            'specializations': ['Python', 'Django', 'REST API'],
            'expertise': ['Backend Development', 'Database Design'],
            'years_of_experience': 5,
            'hourly_rate': 50.00
        }
        
        response = self.client.post('/api/users/instructors/me/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('instructor_code', response.data)
        self.assertEqual(response.data['title'], 'Senior Developer')
    
    def test_get_instructor(self):
        """Test de récupération de profil instructeur"""
        self.test_create_instructor()
        
        response = self.client.get('/api/users/instructors/me/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('instructor_code', response.data)
    
    def test_search_instructors(self):
        """Test de recherche d'instructeurs"""
        response = self.client.get('/api/users/instructors/search/?specialization=Python')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
    
    def test_top_instructors(self):
        """Test des meilleurs instructeurs"""
        response = self.client.get('/api/users/instructors/top/?limit=5')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
