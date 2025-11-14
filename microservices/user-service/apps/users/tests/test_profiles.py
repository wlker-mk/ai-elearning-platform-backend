from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
import uuid

User = get_user_model()


class ProfileTestCase(TestCase):
    """Tests pour les profils utilisateurs"""
    
    def setUp(self):
        """Configuration initiale des tests"""
        self.client = APIClient()
        
        # Créer un utilisateur de test
        self.user = User.objects.create_user(
            id=uuid.uuid4(),
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        
        # Authentifier le client
        self.client.force_authenticate(user=self.user)
    
    def test_create_profile(self):
        """Test de création de profil"""
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'phone_number': '+1234567890',
            'country': 'USA',
            'city': 'New York'
        }
        
        response = self.client.post('/api/users/profiles/me/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['first_name'], 'John')
        self.assertEqual(response.data['last_name'], 'Doe')
    
    def test_get_profile(self):
        """Test de récupération de profil"""
        # Créer d'abord un profil
        self.test_create_profile()
        
        response = self.client.get('/api/users/profiles/me/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('first_name', response.data)
    
    def test_update_profile(self):
        """Test de mise à jour de profil"""
        # Créer d'abord un profil
        self.test_create_profile()
        
        data = {
            'bio': 'Updated bio',
            'website': 'https://example.com'
        }
        
        response = self.client.put('/api/users/profiles/me/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['bio'], 'Updated bio')
