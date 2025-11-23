"""
Tests d'intégration pour les vues OAuth
Fichier: apps/authentication/tests/test_oauth_views.py
"""
import pytest
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, AsyncMock
from django.conf import settings


@pytest.mark.django_db
class TestOAuthViews:
    """Tests d'intégration pour les vues OAuth"""
    
    def setup_method(self):
        self.client = APIClient()
    
    # ========== Google OAuth Tests ==========
    
    def test_google_oauth_success_new_user(self):
        """Test d'authentification Google réussie pour un nouvel utilisateur"""
        with patch('apps.authentication.views.async_to_sync') as mock_async, \
             patch.dict(settings.__dict__, {
                 'GOOGLE_CLIENT_ID': 'test_client_id',
                 'GOOGLE_CLIENT_SECRET': 'test_client_secret'
             }):
            
            # Mock le service OAuth
            mock_user = type('User', (), {
                'id': 'user_123',
                'email': 'newuser@example.com',
                'username': 'newuser',
                'role': 'STUDENT',
                'isEmailVerified': True,
                'isActive': True,
                'isSuspended': False,
                'mfaEnabled': False,
                'lastLoginAt': None,
                'createdAt': '2024-01-01T00:00:00Z'
            })()
            
            mock_session = type('Session', (), {
                'token': 'session_token_123',
                'expiresAt': '2024-01-02T00:00:00Z'
            })()
            
            mock_refresh = type('RefreshToken', (), {
                'token': 'refresh_token_123'
            })()
            
            # Configure les mocks
            mock_async.side_effect = [
                (mock_user, True),  # authenticate_google
                mock_session,        # create_session
                mock_refresh,        # create_refresh_token
                None                 # log_login_attempt
            ]
            
            response = self.client.post('/api/auth/oauth/google/', {
                'code': 'fake_google_code',
                'redirect_uri': 'http://localhost:3000/callback'
            }, format='json')
            
            assert response.status_code == status.HTTP_200_OK
            assert 'access_token' in response.data
            assert 'refresh_token' in response.data
            assert response.data['is_new_user'] is True
    
    def test_google_oauth_missing_config(self):
        """Test Google OAuth sans configuration"""
        with patch.dict(settings.__dict__, {
            'GOOGLE_CLIENT_ID': None,
            'GOOGLE_CLIENT_SECRET': None
        }):
            response = self.client.post('/api/auth/oauth/google/', {
                'code': 'fake_code',
                'redirect_uri': 'http://localhost:3000/callback'
            }, format='json')
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert 'not configured' in str(response.data)
    
    def test_google_oauth_invalid_data(self):
        """Test Google OAuth avec données invalides"""
        response = self.client.post('/api/auth/oauth/google/', {
            'code': '',  # Code vide
        }, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    # ========== GitHub OAuth Tests ==========
    
    def test_github_oauth_success_new_user(self):
        """Test d'authentification GitHub réussie pour un nouvel utilisateur"""
        with patch('apps.authentication.views.async_to_sync') as mock_async, \
             patch.dict(settings.__dict__, {
                 'GITHUB_CLIENT_ID': 'test_client_id',
                 'GITHUB_CLIENT_SECRET': 'test_client_secret'
             }):
            
            mock_user = type('User', (), {
                'id': 'user_456',
                'email': 'githubuser@example.com',
                'username': 'githubuser',
                'role': 'STUDENT',
                'isEmailVerified': True,
                'isActive': True,
                'isSuspended': False,
                'mfaEnabled': False,
                'lastLoginAt': None,
                'createdAt': '2024-01-01T00:00:00Z'
            })()
            
            mock_session = type('Session', (), {
                'token': 'session_token_456',
                'expiresAt': '2024-01-02T00:00:00Z'
            })()
            
            mock_refresh = type('RefreshToken', (), {
                'token': 'refresh_token_456'
            })()
            
            mock_async.side_effect = [
                (mock_user, True),
                mock_session,
                mock_refresh,
                None
            ]
            
            response = self.client.post('/api/auth/oauth/github/', {
                'code': 'fake_github_code'
            }, format='json')
            
            assert response.status_code == status.HTTP_200_OK
            assert 'access_token' in response.data
            assert response.data['is_new_user'] is True
    
    def test_github_oauth_missing_config(self):
        """Test GitHub OAuth sans configuration"""
        with patch.dict(settings.__dict__, {
            'GITHUB_CLIENT_ID': None,
            'GITHUB_CLIENT_SECRET': None
        }):
            response = self.client.post('/api/auth/oauth/github/', {
                'code': 'fake_code'
            }, format='json')
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    
    def test_github_oauth_authentication_failed(self):
        """Test GitHub OAuth avec échec d'authentification"""
        with patch('apps.authentication.views.async_to_sync') as mock_async, \
             patch.dict(settings.__dict__, {
                 'GITHUB_CLIENT_ID': 'test_client_id',
                 'GITHUB_CLIENT_SECRET': 'test_client_secret'
             }):
            
            # Simuler une ValueError
            mock_async.side_effect = ValueError("Cannot retrieve user email")
            
            response = self.client.post('/api/auth/oauth/github/', {
                'code': 'fake_code'
            }, format='json')
            
            assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    # ========== Link OAuth Tests ==========
    
    def test_link_oauth_google_success(self):
        """Test de liaison Google OAuth réussie"""
        # Créer un utilisateur et se connecter
        from apps.authentication.services import UserService, SessionService
        from asgiref.sync import async_to_sync
        
        user_service = UserService()
        session_service = SessionService()
        
        user = async_to_sync(user_service.create_user)(
            email='linktest@example.com',
            username='linktest',
            password='SecurePass123!',
            role='STUDENT'
        )
        
        # Vérifier l'email
        async_to_sync(user_service.db.user.update)(
            where={'id': user.id},
            data={'isEmailVerified': True}
        )
        
        # Créer une session
        session = async_to_sync(session_service.create_session)(user_id=user.id)
        
        # Authentifier le client
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {session.token}')
        
        with patch('apps.authentication.views.async_to_sync') as mock_async, \
             patch.dict(settings.__dict__, {
                 'GOOGLE_CLIENT_ID': 'test_client_id',
                 'GOOGLE_CLIENT_SECRET': 'test_client_secret'
             }):
            
            # Mock les méthodes
            mock_async.side_effect = [
                {'access_token': 'fake_token'},  # _exchange_google_code
                {'id': 'google_123'},            # _get_google_user_info
                True                              # link_oauth_provider
            ]
            
            response = self.client.post('/api/auth/oauth/link/', {
                'provider': 'GOOGLE',
                'code': 'fake_code',
                'redirect_uri': 'http://localhost:3000/callback'
            }, format='json')
            
            assert response.status_code == status.HTTP_200_OK
            assert 'linked successfully' in response.data['message']
        
        # Cleanup
        async_to_sync(user_service.db.user.delete)(where={'id': user.id})
    
    def test_link_oauth_unauthorized(self):
        """Test de liaison OAuth sans authentification"""
        response = self.client.post('/api/auth/oauth/link/', {
            'provider': 'GOOGLE',
            'code': 'fake_code'
        }, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_link_oauth_invalid_provider(self):
        """Test de liaison avec provider invalide"""
        from apps.authentication.services import UserService, SessionService
        from asgiref.sync import async_to_sync
        
        user_service = UserService()
        session_service = SessionService()
        
        user = async_to_sync(user_service.create_user)(
            email='invalidprovider@example.com',
            username='invalidprovider',
            password='SecurePass123!',
            role='STUDENT'
        )
        
        async_to_sync(user_service.db.user.update)(
            where={'id': user.id},
            data={'isEmailVerified': True}
        )
        
        session = async_to_sync(session_service.create_session)(user_id=user.id)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {session.token}')
        
        response = self.client.post('/api/auth/oauth/link/', {
            'provider': 'INVALID',
            'code': 'fake_code'
        }, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Cleanup
        async_to_sync(user_service.db.user.delete)(where={'id': user.id})
    
    # ========== Unlink OAuth Tests ==========
    
    def test_unlink_oauth_success(self):
        """Test de déliaison OAuth réussie"""
        from apps.authentication.services import UserService, SessionService
        from asgiref.sync import async_to_sync
        
        user_service = UserService()
        session_service = SessionService()
        
        user = async_to_sync(user_service.create_user)(
            email='unlinktest@example.com',
            username='unlinktest',
            password='SecurePass123!',
            role='STUDENT'
        )
        
        async_to_sync(user_service.db.user.update)(
            where={'id': user.id},
            data={'isEmailVerified': True}
        )
        
        session = async_to_sync(session_service.create_session)(user_id=user.id)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {session.token}')
        
        with patch('apps.authentication.views.async_to_sync') as mock_async:
            mock_async.return_value = True
            
            response = self.client.post('/api/auth/oauth/unlink/', format='json')
            
            assert response.status_code == status.HTTP_200_OK
            assert 'unlinked successfully' in response.data['message']
        
        # Cleanup
        async_to_sync(user_service.db.user.delete)(where={'id': user.id})
    
    def test_unlink_oauth_unauthorized(self):
        """Test de déliaison OAuth sans authentification"""
        response = self.client.post('/api/auth/oauth/unlink/', format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED