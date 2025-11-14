from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
import uuid

User = get_user_model()


class StudentTestCase(TestCase):
    """Tests pour les étudiants"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            id=uuid.uuid4(),
            email='student@example.com',
            username='student',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_create_student(self):
        """Test de création de profil étudiant"""
        data = {
            'preferred_categories': ['Programming', 'Data Science']
        }
        
        response = self.client.post('/api/users/students/me/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('student_code', response.data)
        self.assertEqual(response.data['level'], 1)
    
    def test_add_experience(self):
        """Test d'ajout d'expérience"""
        # Créer d'abord un profil étudiant
        self.test_create_student()
        
        data = {'points': 150}
        response = self.client.post('/api/users/students/experience/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(response.data['experience_points'], 0)
    
    def test_update_streak(self):
        """Test de mise à jour du streak"""
        self.test_create_student()
        
        response = self.client.post('/api/users/students/streak/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data['streak'], 1)
    
    def test_leaderboard(self):
        """Test du classement"""
        response = self.client.get('/api/users/students/leaderboard/?limit=10')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
