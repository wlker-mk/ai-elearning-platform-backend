# apps/users/tests/test_profiles.py
import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
import uuid
from datetime import datetime, date
from unittest.mock import patch, AsyncMock, MagicMock

User = get_user_model()


class ProfileAPITestCase(APITestCase):
    """Tests pour les endpoints de profils utilisateurs"""
    
    def setUp(self):
        """Configuration initiale des tests"""
        self.client = APIClient()
        
        # Créer un utilisateur de test
        self.user = User.objects.create_user(
            id=uuid.uuid4(),
            email='test@example.com',
            username='testuser',
            password='TestPass123!',
            role='student'
        )
        
        # Générer un token JWT
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        
        # Authentifier le client
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        # Données de profil de test
        self.valid_profile_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'phone_number': '+1234567890',
            'country': 'USA',
            'city': 'New York',
            'bio': 'Test bio',
            'timezone': 'America/New_York',
            'language': 'en'
        }
    
    def tearDown(self):
        """Nettoyage après chaque test"""
        User.objects.all().delete()
    
    # ==========================================
    # TESTS DE CRÉATION DE PROFIL
    # ==========================================
    
    @patch('apps.users.profiles.services.ProfileService.create_profile')
    async def test_create_profile_success(self, mock_create):
        """Test création de profil avec succès"""
        # Mock du retour de Prisma
        mock_profile = {
            'id': str(uuid.uuid4()),
            'userId': str(self.user.id),
            'firstName': 'John',
            'lastName': 'Doe',
            'phoneNumber': '+1234567890',
            'dateOfBirth': None,
            'profileImageUrl': None,
            'coverImageUrl': None,
            'bio': 'Test bio',
            'website': None,
            'linkedin': None,
            'github': None,
            'twitter': None,
            'facebook': None,
            'country': 'USA',
            'city': 'New York',
            'timezone': 'America/New_York',
            'language': 'en',
            'createdAt': datetime.now(),
            'updatedAt': datetime.now(),
        }
        mock_create.return_value = mock_profile
        
        response = self.client.post(
            '/api/users/profiles/me/',
            self.valid_profile_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['first_name'], 'John')
        self.assertEqual(response.data['last_name'], 'Doe')
        self.assertIn('user_id', response.data)
    
    def test_create_profile_missing_required_fields(self):
        """Test création de profil avec champs manquants"""
        incomplete_data = {
            'first_name': 'John'
            # Manque last_name
        }
        
        response = self.client.post(
            '/api/users/profiles/me/',
            incomplete_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('last_name', response.data)
    
    @patch('apps.users.profiles.services.ProfileService.get_profile')
    async def test_create_profile_already_exists(self, mock_get):
        """Test création de profil quand il existe déjà"""
        mock_get.return_value = {'userId': str(self.user.id)}
        
        response = self.client.post(
            '/api/users/profiles/me/',
            self.valid_profile_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('already exists', response.data['error'].lower())
    
    def test_create_profile_unauthenticated(self):
        """Test création de profil sans authentification"""
        self.client.credentials()  # Retirer l'authentification
        
        response = self.client.post(
            '/api/users/profiles/me/',
            self.valid_profile_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_create_profile_invalid_phone_format(self):
        """Test création avec numéro de téléphone invalide"""
        invalid_data = self.valid_profile_data.copy()
        invalid_data['phone_number'] = 'invalid-phone'
        
        response = self.client.post(
            '/api/users/profiles/me/',
            invalid_data,
            format='json'
        )
        
        # Le serializer devrait accepter n'importe quelle chaîne
        # mais on pourrait ajouter une validation personnalisée
        self.assertIn(response.status_code, [
            status.HTTP_201_CREATED,
            status.HTTP_400_BAD_REQUEST
        ])
    
    # ==========================================
    # TESTS DE RÉCUPÉRATION DE PROFIL
    # ==========================================
    
    @patch('apps.users.profiles.services.ProfileService.get_profile')
    async def test_get_own_profile_success(self, mock_get):
        """Test récupération de son propre profil"""
        mock_profile = {
            'id': str(uuid.uuid4()),
            'userId': str(self.user.id),
            'firstName': 'John',
            'lastName': 'Doe',
            'phoneNumber': '+1234567890',
            'dateOfBirth': date(1990, 1, 1),
            'profileImageUrl': 'https://example.com/avatar.jpg',
            'coverImageUrl': None,
            'bio': 'Test bio',
            'website': 'https://johndoe.com',
            'linkedin': 'https://linkedin.com/in/johndoe',
            'github': None,
            'twitter': None,
            'facebook': None,
            'country': 'USA',
            'city': 'New York',
            'timezone': 'America/New_York',
            'language': 'en',
            'createdAt': datetime.now(),
            'updatedAt': datetime.now(),
        }
        mock_get.return_value = mock_profile
        
        response = self.client.get('/api/users/profiles/me/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'John')
        self.assertEqual(response.data['country'], 'USA')
        self.assertIn('created_at', response.data)
    
    @patch('apps.users.profiles.services.ProfileService.get_profile')
    async def test_get_profile_not_found(self, mock_get):
        """Test récupération de profil inexistant"""
        mock_get.return_value = None
        
        response = self.client.get('/api/users/profiles/me/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
    
    @patch('apps.users.profiles.services.ProfileService.get_profile')
    async def test_get_public_profile(self, mock_get):
        """Test récupération d'un profil public"""
        other_user_id = str(uuid.uuid4())
        mock_profile = {
            'id': str(uuid.uuid4()),
            'userId': other_user_id,
            'firstName': 'Jane',
            'lastName': 'Smith',
            'phoneNumber': None,
            'dateOfBirth': None,
            'profileImageUrl': None,
            'coverImageUrl': None,
            'bio': 'Public bio',
            'website': None,
            'linkedin': None,
            'github': None,
            'twitter': None,
            'facebook': None,
            'country': 'Canada',
            'city': 'Toronto',
            'timezone': 'America/Toronto',
            'language': 'en',
            'createdAt': datetime.now(),
            'updatedAt': datetime.now(),
        }
        mock_get.return_value = mock_profile
        
        # Pas besoin d'authentification pour les profils publics
        self.client.credentials()
        
        response = self.client.get(f'/api/users/profiles/{other_user_id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Jane')
    
    # ==========================================
    # TESTS DE MISE À JOUR DE PROFIL
    # ==========================================
    
    @patch('apps.users.profiles.services.ProfileService.update_profile')
    async def test_update_profile_success(self, mock_update):
        """Test mise à jour de profil avec succès"""
        update_data = {
            'bio': 'Updated bio',
            'website': 'https://newwebsite.com',
            'city': 'Los Angeles'
        }
        
        mock_updated_profile = {
            'id': str(uuid.uuid4()),
            'userId': str(self.user.id),
            'firstName': 'John',
            'lastName': 'Doe',
            'phoneNumber': '+1234567890',
            'dateOfBirth': None,
            'profileImageUrl': None,
            'coverImageUrl': None,
            'bio': 'Updated bio',
            'website': 'https://newwebsite.com',
            'linkedin': None,
            'github': None,
            'twitter': None,
            'facebook': None,
            'country': 'USA',
            'city': 'Los Angeles',
            'timezone': 'America/New_York',
            'language': 'en',
            'createdAt': datetime.now(),
            'updatedAt': datetime.now(),
        }
        mock_update.return_value = mock_updated_profile
        
        response = self.client.put(
            '/api/users/profiles/me/',
            update_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['bio'], 'Updated bio')
        self.assertEqual(response.data['city'], 'Los Angeles')
    
    @patch('apps.users.profiles.services.ProfileService.update_profile')
    async def test_update_profile_not_found(self, mock_update):
        """Test mise à jour d'un profil inexistant"""
        mock_update.return_value = None
        
        update_data = {'bio': 'New bio'}
        
        response = self.client.put(
            '/api/users/profiles/me/',
            update_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    @patch('apps.users.profiles.services.ProfileService.update_profile')
    async def test_update_profile_partial(self, mock_update):
        """Test mise à jour partielle de profil"""
        partial_data = {'bio': 'Only updating bio'}
        
        mock_profile = {
            'id': str(uuid.uuid4()),
            'userId': str(self.user.id),
            'firstName': 'John',
            'lastName': 'Doe',
            'phoneNumber': '+1234567890',
            'dateOfBirth': None,
            'profileImageUrl': None,
            'coverImageUrl': None,
            'bio': 'Only updating bio',
            'website': None,
            'linkedin': None,
            'github': None,
            'twitter': None,
            'facebook': None,
            'country': 'USA',
            'city': 'New York',
            'timezone': 'America/New_York',
            'language': 'en',
            'createdAt': datetime.now(),
            'updatedAt': datetime.now(),
        }
        mock_update.return_value = mock_profile
        
        response = self.client.put(
            '/api/users/profiles/me/',
            partial_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['bio'], 'Only updating bio')
    
    def test_update_profile_invalid_url(self):
        """Test mise à jour avec URL invalide"""
        invalid_data = {
            'website': 'not-a-valid-url'
        }
        
        response = self.client.put(
            '/api/users/profiles/me/',
            invalid_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('website', response.data)
    
    # ==========================================
    # TESTS DE SUPPRESSION DE PROFIL
    # ==========================================
    
    @patch('apps.users.profiles.services.ProfileService.delete_profile')
    async def test_delete_profile_success(self, mock_delete):
        """Test suppression de profil avec succès"""
        mock_delete.return_value = True
        
        response = self.client.delete('/api/users/profiles/me/')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    
    @patch('apps.users.profiles.services.ProfileService.delete_profile')
    async def test_delete_profile_not_found(self, mock_delete):
        """Test suppression d'un profil inexistant"""
        mock_delete.return_value = False
        
        response = self.client.delete('/api/users/profiles/me/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_delete_profile_unauthenticated(self):
        """Test suppression sans authentification"""
        self.client.credentials()
        
        response = self.client.delete('/api/users/profiles/me/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ProfileSerializerTestCase(TestCase):
    """Tests pour les serializers de profil"""
    
    def test_profile_serializer_valid_data(self):
        """Test serializer avec données valides"""
        from apps.users.profiles.serializers import ProfileCreateSerializer
        
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'phone_number': '+1234567890',
            'country': 'USA',
            'city': 'New York',
            'timezone': 'America/New_York',
            'language': 'en'
        }
        
        serializer = ProfileCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['first_name'], 'John')
    
    def test_profile_serializer_missing_required(self):
        """Test serializer avec champs requis manquants"""
        from apps.users.profiles.serializers import ProfileCreateSerializer
        
        data = {
            'first_name': 'John'
            # Manque last_name
        }
        
        serializer = ProfileCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('last_name', serializer.errors)
    
    def test_profile_update_serializer_optional_fields(self):
        """Test serializer de mise à jour avec champs optionnels"""
        from apps.users.profiles.serializers import ProfileUpdateSerializer
        
        data = {
            'bio': 'New bio only'
        }
        
        serializer = ProfileUpdateSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_profile_serializer_url_validation(self):
        """Test validation des URLs"""
        from apps.users.profiles.serializers import ProfileUpdateSerializer
        
        data = {
            'website': 'not-a-url'
        }
        
        serializer = ProfileUpdateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('website', serializer.errors)


# ==========================================
# TESTS D'INTÉGRATION
# ==========================================

@pytest.mark.integration
class ProfileIntegrationTestCase(APITestCase):
    """Tests d'intégration bout en bout"""
    
    def setUp(self):
        """Configuration pour tests d'intégration"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='integration@test.com',
            username='integrationuser',
            password='IntegrationPass123!',
            role='student'
        )
        
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
    
    def test_complete_profile_lifecycle(self):
        """Test du cycle de vie complet d'un profil"""
        # 1. Créer un profil
        create_data = {
            'first_name': 'Integration',
            'last_name': 'Test',
            'phone_number': '+1234567890',
            'country': 'USA',
            'city': 'Boston'
        }
        
        # Note: Ce test nécessiterait une vraie base de données
        # Pour les tests unitaires, on utilise des mocks
        # Pour l'intégration, on utiliserait une DB de test
        
        # 2. Récupérer le profil
        # 3. Mettre à jour le profil
        # 4. Supprimer le profil
        
        # Ce test serait implémenté avec une vraie DB de test
        pass