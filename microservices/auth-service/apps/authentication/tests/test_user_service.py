"""
Tests pour UserService
Fichier: apps/authentication/tests/test_user_service.py
"""
import pytest
from apps.authentication.services import UserService
from shared.shared.exceptions import (
    UserAlreadyExistsError,
    WeakPasswordError,
    InvalidCredentialsError,
    AccountLockedError
)


@pytest.mark.asyncio
class TestUserService:
    """Tests pour le service utilisateur"""
    
    @pytest.fixture
    async def user_service(self):
        """Fixture pour créer une instance de UserService"""
        service = UserService()
        await service.connect()
        yield service
        await service.disconnect()
    
    async def test_create_user_success(self, user_service):
        """Test de création d'utilisateur réussie"""
        user = await user_service.create_user(
            email="test@example.com",
            username="testuser",
            password="SecurePass123!",
            role="STUDENT"
        )
        
        assert user is not None
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.role == "STUDENT"
        assert user.isEmailVerified is False
        assert user.isActive is True
        
        # Cleanup
        await user_service.db.user.delete(where={'id': user.id})
    
    async def test_create_user_duplicate_email(self, user_service):
        """Test de création avec email existant"""
        # Créer le premier utilisateur
        user1 = await user_service.create_user(
            email="duplicate@example.com",
            username="user1",
            password="SecurePass123!",
            role="STUDENT"
        )
        
        # Tenter de créer un second avec le même email
        with pytest.raises(UserAlreadyExistsError):
            await user_service.create_user(
                email="duplicate@example.com",
                username="user2",
                password="SecurePass123!",
                role="STUDENT"
            )
        
        # Cleanup
        await user_service.db.user.delete(where={'id': user1.id})
    
    async def test_create_user_weak_password(self, user_service):
        """Test avec mot de passe faible"""
        with pytest.raises(WeakPasswordError):
            await user_service.create_user(
                email="weak@example.com",
                username="weakuser",
                password="weak",  # Trop faible
                role="STUDENT"
            )
    
    async def test_authenticate_user_success(self, user_service):
        """Test d'authentification réussie"""
        # Créer un utilisateur
        user = await user_service.create_user(
            email="auth@example.com",
            username="authuser",
            password="SecurePass123!",
            role="STUDENT"
        )
        
        # Vérifier l'email pour permettre la connexion
        await user_service.db.user.update(
            where={'id': user.id},
            data={'isEmailVerified': True}
        )
        
        # Authentifier
        authenticated_user = await user_service.authenticate_user(
            email="auth@example.com",
            password="SecurePass123!"
        )
        
        assert authenticated_user is not None
        assert authenticated_user.id == user.id
        
        # Cleanup
        await user_service.db.user.delete(where={'id': user.id})
    
    async def test_authenticate_user_wrong_password(self, user_service):
        """Test avec mauvais mot de passe"""
        # Créer un utilisateur
        user = await user_service.create_user(
            email="wrong@example.com",
            username="wronguser",
            password="SecurePass123!",
            role="STUDENT"
        )
        
        # Vérifier l'email
        await user_service.db.user.update(
            where={'id': user.id},
            data={'isEmailVerified': True}
        )
        
        # Tenter avec mauvais mot de passe
        with pytest.raises(InvalidCredentialsError):
            await user_service.authenticate_user(
                email="wrong@example.com",
                password="WrongPassword123!"
            )
        
        # Cleanup
        await user_service.db.user.delete(where={'id': user.id})
    
    async def test_account_locking(self, user_service):
        """Test du verrouillage de compte après tentatives échouées"""
        # Créer un utilisateur
        user = await user_service.create_user(
            email="lock@example.com",
            username="lockuser",
            password="SecurePass123!",
            role="STUDENT"
        )
        
        # Vérifier l'email
        await user_service.db.user.update(
            where={'id': user.id},
            data={'isEmailVerified': True}
        )
        
        # Faire 5 tentatives échouées
        for i in range(5):
            try:
                await user_service.authenticate_user(
                    email="lock@example.com",
                    password="WrongPassword!"
                )
            except InvalidCredentialsError:
                pass
        
        # La 6ème tentative devrait lever AccountLockedError
        with pytest.raises(AccountLockedError):
            await user_service.authenticate_user(
                email="lock@example.com",
                password="SecurePass123!"  # Même avec bon mot de passe
            )
        
        # Cleanup
        await user_service.db.user.delete(where={'id': user.id})
    
    async def test_verify_email(self, user_service):
        """Test de vérification d'email"""
        # Créer un utilisateur
        user = await user_service.create_user(
            email="verify@example.com",
            username="verifyuser",
            password="SecurePass123!",
            role="STUDENT"
        )
        
        # Récupérer le token
        token = user.emailVerificationToken
        
        # Vérifier l'email
        success = await user_service.verify_email(token)
        assert success is True
        
        # Vérifier que l'email est marqué comme vérifié
        updated_user = await user_service.get_user(user.id)
        assert updated_user.isEmailVerified is True
        
        # Cleanup
        await user_service.db.user.delete(where={'id': user.id})
    
    async def test_change_password(self, user_service):
        """Test de changement de mot de passe"""
        # Créer un utilisateur
        user = await user_service.create_user(
            email="change@example.com",
            username="changeuser",
            password="OldPass123!",
            role="STUDENT"
        )
        
        # Changer le mot de passe
        success = await user_service.change_password(
            user_id=user.id,
            current_password="OldPass123!",
            new_password="NewPass123!"
        )
        
        assert success is True
        
        # Vérifier qu'on peut se connecter avec le nouveau mot de passe
        await user_service.db.user.update(
            where={'id': user.id},
            data={'isEmailVerified': True}
        )
        
        authenticated = await user_service.authenticate_user(
            email="change@example.com",
            password="NewPass123!"
        )
        
        assert authenticated is not None
        
        # Cleanup
        await user_service.db.user.delete(where={'id': user.id})
    
    async def test_password_reset_flow(self, user_service):
        """Test du flow complet de reset de mot de passe"""
        # Créer un utilisateur
        user = await user_service.create_user(
            email="reset@example.com",
            username="resetuser",
            password="OldPass123!",
            role="STUDENT"
        )
        
        # Demander un reset
        token = await user_service.request_password_reset("reset@example.com")
        assert token is not None
        
        # Réinitialiser avec le token
        success = await user_service.reset_password(token, "NewPass456!")
        assert success is True
        
        # Vérifier qu'on peut se connecter avec le nouveau mot de passe
        await user_service.db.user.update(
            where={'id': user.id},
            data={'isEmailVerified': True}
        )
        
        authenticated = await user_service.authenticate_user(
            email="reset@example.com",
            password="NewPass456!"
        )
        
        assert authenticated is not None
        
        # Cleanup
        await user_service.db.user.delete(where={'id': user.id})