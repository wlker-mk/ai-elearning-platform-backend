"""
Tests pour OAuthService
Fichier: apps/authentication/tests/test_oauth_service.py
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from apps.authentication.services import OAuthService


@pytest.mark.asyncio
class TestOAuthService:
    """Tests pour le service OAuth"""
    
    @pytest.fixture
    async def oauth_service(self):
        """Fixture pour créer une instance de OAuthService"""
        service = OAuthService()
        await service.connect()
        yield service
        await service.disconnect()
    
    # ========== Google OAuth Tests ==========
    
    async def test_google_oauth_new_user(self, oauth_service):
        """Test d'authentification Google pour un nouvel utilisateur"""
        with patch.object(oauth_service, '_exchange_google_code') as mock_exchange, \
             patch.object(oauth_service, '_get_google_user_info') as mock_user_info:
            
            # Mock les réponses
            mock_exchange.return_value = {'access_token': 'fake_token'}
            mock_user_info.return_value = {
                'id': 'google_123',
                'email': 'newuser@example.com',
                'name': 'New User',
                'verified_email': True
            }
            
            # Authentifier
            user, is_new = await oauth_service.authenticate_google(
                code='fake_code',
                client_id='fake_client_id',
                client_secret='fake_client_secret',
                redirect_uri='http://localhost:3000/callback'
            )
            
            assert user is not None
            assert is_new is True
            assert user.email == 'newuser@example.com'
            assert user.authProvider == 'GOOGLE'
            assert user.authProviderId == 'google_123'
            assert user.isEmailVerified is True
            
            # Cleanup
            await oauth_service.db.user.delete(where={'id': user.id})
    
    async def test_google_oauth_existing_user(self, oauth_service):
        """Test d'authentification Google pour un utilisateur existant"""
        # Créer un utilisateur d'abord
        from apps.authentication.services import UserService
        user_service = UserService()
        
        existing_user = await user_service.create_user(
            email='existing@example.com',
            username='existinguser',
            password='SecurePass123!',
            role='STUDENT'
        )
        
        with patch.object(oauth_service, '_exchange_google_code') as mock_exchange, \
             patch.object(oauth_service, '_get_google_user_info') as mock_user_info:
            
            mock_exchange.return_value = {'access_token': 'fake_token'}
            mock_user_info.return_value = {
                'id': 'google_456',
                'email': 'existing@example.com',
                'name': 'Existing User',
                'verified_email': True
            }
            
            user, is_new = await oauth_service.authenticate_google(
                code='fake_code',
                client_id='fake_client_id',
                client_secret='fake_client_secret',
                redirect_uri='http://localhost:3000/callback'
            )
            
            assert user is not None
            assert is_new is False
            assert user.id == existing_user.id
            assert user.authProvider == 'GOOGLE'
            assert user.authProviderId == 'google_456'
        
        # Cleanup
        await oauth_service.db.user.delete(where={'id': existing_user.id})
    
    async def test_google_oauth_invalid_code(self, oauth_service):
        """Test avec code Google invalide"""
        with patch.object(oauth_service, '_exchange_google_code') as mock_exchange:
            mock_exchange.return_value = None
            
            with pytest.raises(ValueError, match="Failed to exchange Google code"):
                await oauth_service.authenticate_google(
                    code='invalid_code',
                    client_id='fake_client_id',
                    client_secret='fake_client_secret',
                    redirect_uri='http://localhost:3000/callback'
                )
    
    # ========== GitHub OAuth Tests ==========
    
    async def test_github_oauth_new_user(self, oauth_service):
        """Test d'authentification GitHub pour un nouvel utilisateur"""
        with patch.object(oauth_service, '_exchange_github_code') as mock_exchange, \
             patch.object(oauth_service, '_get_github_user_info') as mock_user_info:
            
            mock_exchange.return_value = {'access_token': 'fake_token'}
            mock_user_info.return_value = {
                'id': 12345,
                'login': 'githubuser',
                'email': 'github@example.com'
            }
            
            user, is_new = await oauth_service.authenticate_github(
                code='fake_code',
                client_id='fake_client_id',
                client_secret='fake_client_secret'
            )
            
            assert user is not None
            assert is_new is True
            assert user.email == 'github@example.com'
            assert user.authProvider == 'GITHUB'
            assert user.authProviderId == '12345'
            assert user.isEmailVerified is True
            
            # Cleanup
            await oauth_service.db.user.delete(where={'id': user.id})
    
    async def test_github_oauth_no_public_email(self, oauth_service):
        """Test GitHub OAuth quand l'email n'est pas public"""
        with patch.object(oauth_service, '_exchange_github_code') as mock_exchange, \
             patch.object(oauth_service, '_get_github_user_info') as mock_user_info, \
             patch.object(oauth_service, '_get_github_primary_email') as mock_email:
            
            mock_exchange.return_value = {'access_token': 'fake_token'}
            mock_user_info.return_value = {
                'id': 67890,
                'login': 'privateuser',
                'email': None  # Email non public
            }
            mock_email.return_value = 'private@example.com'
            
            user, is_new = await oauth_service.authenticate_github(
                code='fake_code',
                client_id='fake_client_id',
                client_secret='fake_client_secret'
            )
            
            assert user is not None
            assert user.email == 'private@example.com'
            
            # Cleanup
            await oauth_service.db.user.delete(where={'id': user.id})
    
    async def test_github_oauth_no_email_found(self, oauth_service):
        """Test GitHub OAuth quand aucun email n'est trouvé"""
        with patch.object(oauth_service, '_exchange_github_code') as mock_exchange, \
             patch.object(oauth_service, '_get_github_user_info') as mock_user_info, \
             patch.object(oauth_service, '_get_github_primary_email') as mock_email:
            
            mock_exchange.return_value = {'access_token': 'fake_token'}
            mock_user_info.return_value = {
                'id': 99999,
                'login': 'noemail',
                'email': None
            }
            mock_email.return_value = None
            
            with pytest.raises(ValueError, match="Cannot retrieve user email"):
                await oauth_service.authenticate_github(
                    code='fake_code',
                    client_id='fake_client_id',
                    client_secret='fake_client_secret'
                )
    
    async def test_github_oauth_existing_user(self, oauth_service):
        """Test GitHub OAuth pour un utilisateur existant"""
        from apps.authentication.services import UserService
        user_service = UserService()
        
        existing_user = await user_service.create_user(
            email='github-existing@example.com',
            username='githubexisting',
            password='SecurePass123!',
            role='STUDENT'
        )
        
        with patch.object(oauth_service, '_exchange_github_code') as mock_exchange, \
             patch.object(oauth_service, '_get_github_user_info') as mock_user_info:
            
            mock_exchange.return_value = {'access_token': 'fake_token'}
            mock_user_info.return_value = {
                'id': 11111,
                'login': 'existinggh',
                'email': 'github-existing@example.com'
            }
            
            user, is_new = await oauth_service.authenticate_github(
                code='fake_code',
                client_id='fake_client_id',
                client_secret='fake_client_secret'
            )
            
            assert user is not None
            assert is_new is False
            assert user.id == existing_user.id
            assert user.authProvider == 'GITHUB'
        
        # Cleanup
        await oauth_service.db.user.delete(where={'id': existing_user.id})
    
    # ========== Username Generation Tests ==========
    
    async def test_generate_unique_username(self, oauth_service):
        """Test de génération de username unique"""
        base_username = 'testuser'
        
        # Créer un utilisateur avec ce username
        from apps.authentication.services import UserService
        user_service = UserService()
        
        user1 = await user_service.create_user(
            email='user1@example.com',
            username='testuser',
            password='SecurePass123!',
            role='STUDENT'
        )
        
        # Générer un username unique
        unique_username = await oauth_service._generate_unique_username(base_username)
        
        assert unique_username != 'testuser'
        assert 'testuser' in unique_username
        
        # Cleanup
        await oauth_service.db.user.delete(where={'id': user1.id})
    
    async def test_generate_unique_username_with_special_chars(self, oauth_service):
        """Test de génération avec caractères spéciaux"""
        base_username = 'Test User@123!'
        
        unique_username = await oauth_service._generate_unique_username(base_username)
        
        # Devrait être nettoyé
        assert '@' not in unique_username
        assert '!' not in unique_username
        assert ' ' not in unique_username
    
    # ========== Link/Unlink Tests ==========
    
    async def test_link_oauth_provider(self, oauth_service):
        """Test de liaison d'un provider OAuth"""
        from apps.authentication.services import UserService
        user_service = UserService()
        
        user = await user_service.create_user(
            email='link@example.com',
            username='linkuser',
            password='SecurePass123!',
            role='STUDENT'
        )
        
        # Lier Google
        success = await oauth_service.link_oauth_provider(
            user_id=user.id,
            provider='GOOGLE',
            provider_id='google_link_123'
        )
        
        assert success is True
        
        # Vérifier
        updated_user = await oauth_service.db.user.find_unique(where={'id': user.id})
        assert updated_user.authProvider == 'GOOGLE'
        assert updated_user.authProviderId == 'google_link_123'
        
        # Cleanup
        await oauth_service.db.user.delete(where={'id': user.id})
    
    async def test_link_oauth_provider_already_linked(self, oauth_service):
        """Test de liaison quand le provider est déjà lié à un autre compte"""
        from apps.authentication.services import UserService
        user_service = UserService()
        
        # Créer deux utilisateurs
        user1 = await user_service.create_user(
            email='user1-link@example.com',
            username='user1link',
            password='SecurePass123!',
            role='STUDENT'
        )
        
        user2 = await user_service.create_user(
            email='user2-link@example.com',
            username='user2link',
            password='SecurePass123!',
            role='STUDENT'
        )
        
        # Lier Google à user1
        await oauth_service.link_oauth_provider(
            user_id=user1.id,
            provider='GOOGLE',
            provider_id='shared_google_123'
        )
        
        # Tenter de lier le même provider à user2
        with pytest.raises(ValueError, match="already linked"):
            await oauth_service.link_oauth_provider(
                user_id=user2.id,
                provider='GOOGLE',
                provider_id='shared_google_123'
            )
        
        # Cleanup
        await oauth_service.db.user.delete(where={'id': user1.id})
        await oauth_service.db.user.delete(where={'id': user2.id})
    
    async def test_unlink_oauth_provider(self, oauth_service):
        """Test de déliaison d'un provider OAuth"""
        from apps.authentication.services import UserService
        user_service = UserService()
        
        user = await user_service.create_user(
            email='unlink@example.com',
            username='unlinkuser',
            password='SecurePass123!',
            role='STUDENT'
        )
        
        # Lier Google d'abord
        await oauth_service.link_oauth_provider(
            user_id=user.id,
            provider='GOOGLE',
            provider_id='google_unlink_123'
        )
        
        # Délier
        success = await oauth_service.unlink_oauth_provider(user_id=user.id)
        
        assert success is True
        
        # Vérifier
        updated_user = await oauth_service.db.user.find_unique(where={'id': user.id})
        assert updated_user.authProvider == 'PASSWORD'
        assert updated_user.authProviderId is None
        
        # Cleanup
        await oauth_service.db.user.delete(where={'id': user.id})
    
    # ========== HTTP Client Tests ==========
    
    @pytest.mark.parametrize("status_code,expected", [
        (200, True),
        (400, False),
        (401, False),
        (500, False),
    ])
    async def test_exchange_google_code_status_codes(self, oauth_service, status_code, expected):
        """Test des différents codes de statut pour l'échange de code Google"""
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = status_code
            mock_response.json.return_value = {'access_token': 'token'} if status_code == 200 else {}
            mock_post.return_value = mock_response
            
            result = await oauth_service._exchange_google_code(
                'code', 'client_id', 'client_secret', 'redirect_uri'
            )
            
            if expected:
                assert result is not None
            else:
                assert result is None
    
    @pytest.mark.parametrize("status_code,expected", [
        (200, True),
        (400, False),
        (401, False),
        (500, False),
    ])
    async def test_exchange_github_code_status_codes(self, oauth_service, status_code, expected):
        """Test des différents codes de statut pour l'échange de code GitHub"""
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = status_code
            mock_response.json.return_value = {'access_token': 'token'} if status_code == 200 else {}
            mock_post.return_value = mock_response
            
            result = await oauth_service._exchange_github_code(
                'code', 'client_id', 'client_secret'
            )
            
            if expected:
                assert result is not None
            else:
                assert result is None