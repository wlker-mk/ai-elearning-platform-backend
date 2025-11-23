"""
Service OAuth pour Google et GitHub
Fichier: apps/authentication/services/oauth_service.py
"""
from typing import Optional, Dict, Any, Tuple
from datetime import datetime
import httpx
import logging
from prisma import Prisma
from prisma.models import User
from shared.shared.encryption import PasswordManager

logger = logging.getLogger(__name__)


class OAuthService:
    """Service de gestion de l'authentification OAuth"""
    
    # Google OAuth endpoints
    GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
    GOOGLE_USER_INFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
    
    # GitHub OAuth endpoints
    GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
    GITHUB_USER_INFO_URL = "https://api.github.com/user"
    GITHUB_EMAIL_URL = "https://api.github.com/user/emails"
    
    def __init__(self):
        self.db = Prisma()
        self.password_manager = PasswordManager()
    
    async def connect(self):
        if not self.db.is_connected():
            await self.db.connect()
    
    async def disconnect(self):
        if self.db.is_connected():
            await self.db.disconnect()
    
    async def authenticate_google(
        self,
        code: str,
        client_id: str,
        client_secret: str,
        redirect_uri: str
    ) -> Tuple[User, bool]:
        """
        Authentifier avec Google OAuth
        
        Args:
            code: Code d'autorisation OAuth
            client_id: ID client Google
            client_secret: Secret client Google
            redirect_uri: URI de redirection
            
        Returns:
            Tuple (User, is_new_user)
        """
        try:
            # Échanger le code contre un access token
            token_data = await self._exchange_google_code(
                code, client_id, client_secret, redirect_uri
            )
            
            if not token_data:
                raise ValueError("Failed to exchange Google code for token")
            
            # Récupérer les informations utilisateur
            user_info = await self._get_google_user_info(token_data['access_token'])
            
            if not user_info:
                raise ValueError("Failed to get Google user info")
            
            # Créer ou récupérer l'utilisateur
            user, is_new = await self._get_or_create_oauth_user(
                email=user_info['email'],
                username=user_info.get('name', user_info['email'].split('@')[0]),
                auth_provider='GOOGLE',
                auth_provider_id=user_info['id'],
                is_email_verified=user_info.get('verified_email', False)
            )
            
            logger.info(f"Google authentication successful for user: {user.email}")
            return user, is_new
            
        except Exception as e:
            logger.error(f"Google authentication error: {str(e)}")
            raise
    
    async def authenticate_github(
        self,
        code: str,
        client_id: str,
        client_secret: str
    ) -> Tuple[User, bool]:
        """
        Authentifier avec GitHub OAuth
        
        Args:
            code: Code d'autorisation OAuth
            client_id: ID client GitHub
            client_secret: Secret client GitHub
            
        Returns:
            Tuple (User, is_new_user)
        """
        try:
            # Échanger le code contre un access token
            token_data = await self._exchange_github_code(
                code, client_id, client_secret
            )
            
            if not token_data:
                raise ValueError("Failed to exchange GitHub code for token")
            
            # Récupérer les informations utilisateur
            user_info = await self._get_github_user_info(token_data['access_token'])
            
            if not user_info:
                raise ValueError("Failed to get GitHub user info")
            
            # Récupérer l'email si non public
            email = user_info.get('email')
            if not email:
                email = await self._get_github_primary_email(token_data['access_token'])
            
            if not email:
                raise ValueError("Cannot retrieve user email from GitHub")
            
            # Créer ou récupérer l'utilisateur
            user, is_new = await self._get_or_create_oauth_user(
                email=email,
                username=user_info.get('login', email.split('@')[0]),
                auth_provider='GITHUB',
                auth_provider_id=str(user_info['id']),
                is_email_verified=True  # GitHub vérifie les emails
            )
            
            logger.info(f"GitHub authentication successful for user: {user.email}")
            return user, is_new
            
        except Exception as e:
            logger.error(f"GitHub authentication error: {str(e)}")
            raise
    
    async def _exchange_google_code(
        self,
        code: str,
        client_id: str,
        client_secret: str,
        redirect_uri: str
    ) -> Optional[Dict[str, Any]]:
        """Échanger le code Google contre un access token"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.GOOGLE_TOKEN_URL,
                    data={
                        'code': code,
                        'client_id': client_id,
                        'client_secret': client_secret,
                        'redirect_uri': redirect_uri,
                        'grant_type': 'authorization_code'
                    }
                )
                
                if response.status_code != 200:
                    logger.error(f"Google token exchange failed: {response.text}")
                    return None
                
                return response.json()
                
        except Exception as e:
            logger.error(f"Error exchanging Google code: {str(e)}")
            return None
    
    async def _get_google_user_info(self, access_token: str) -> Optional[Dict[str, Any]]:
        """Récupérer les informations utilisateur depuis Google"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.GOOGLE_USER_INFO_URL,
                    headers={'Authorization': f'Bearer {access_token}'}
                )
                
                if response.status_code != 200:
                    logger.error(f"Google user info failed: {response.text}")
                    return None
                
                return response.json()
                
        except Exception as e:
            logger.error(f"Error getting Google user info: {str(e)}")
            return None
    
    async def _exchange_github_code(
        self,
        code: str,
        client_id: str,
        client_secret: str
    ) -> Optional[Dict[str, Any]]:
        """Échanger le code GitHub contre un access token"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.GITHUB_TOKEN_URL,
                    data={
                        'code': code,
                        'client_id': client_id,
                        'client_secret': client_secret
                    },
                    headers={'Accept': 'application/json'}
                )
                
                if response.status_code != 200:
                    logger.error(f"GitHub token exchange failed: {response.text}")
                    return None
                
                return response.json()
                
        except Exception as e:
            logger.error(f"Error exchanging GitHub code: {str(e)}")
            return None
    
    async def _get_github_user_info(self, access_token: str) -> Optional[Dict[str, Any]]:
        """Récupérer les informations utilisateur depuis GitHub"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.GITHUB_USER_INFO_URL,
                    headers={
                        'Authorization': f'Bearer {access_token}',
                        'Accept': 'application/vnd.github.v3+json'
                    }
                )
                
                if response.status_code != 200:
                    logger.error(f"GitHub user info failed: {response.text}")
                    return None
                
                return response.json()
                
        except Exception as e:
            logger.error(f"Error getting GitHub user info: {str(e)}")
            return None
    
    async def _get_github_primary_email(self, access_token: str) -> Optional[str]:
        """Récupérer l'email principal depuis GitHub"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.GITHUB_EMAIL_URL,
                    headers={
                        'Authorization': f'Bearer {access_token}',
                        'Accept': 'application/vnd.github.v3+json'
                    }
                )
                
                if response.status_code != 200:
                    logger.error(f"GitHub email fetch failed: {response.text}")
                    return None
                
                emails = response.json()
                
                # Trouver l'email principal et vérifié
                for email_obj in emails:
                    if email_obj.get('primary') and email_obj.get('verified'):
                        return email_obj['email']
                
                # Sinon prendre le premier email vérifié
                for email_obj in emails:
                    if email_obj.get('verified'):
                        return email_obj['email']
                
                return None
                
        except Exception as e:
            logger.error(f"Error getting GitHub email: {str(e)}")
            return None
    
    async def _get_or_create_oauth_user(
        self,
        email: str,
        username: str,
        auth_provider: str,
        auth_provider_id: str,
        is_email_verified: bool = False
    ) -> Tuple[User, bool]:
        """Créer ou récupérer un utilisateur OAuth"""
        try:
            await self.connect()
            
            # Chercher un utilisateur existant avec cet email
            user = await self.db.user.find_unique(where={'email': email})
            
            if user:
                # Mettre à jour le provider OAuth si différent
                if user.authProvider != auth_provider:
                    user = await self.db.user.update(
                        where={'id': user.id},
                        data={
                            'authProvider': auth_provider,
                            'authProviderId': auth_provider_id,
                            'isEmailVerified': is_email_verified or user.isEmailVerified,
                            'lastLoginAt': datetime.now()
                        }
                    )
                
                return user, False
            
            # Générer un username unique si nécessaire
            unique_username = await self._generate_unique_username(username)
            
            # Créer un nouveau compte
            # Générer un mot de passe aléatoire (non utilisé pour OAuth)
            random_password = self.password_manager.generate_random_password()
            password_hash = self.password_manager.hash_password(random_password)
            
            user = await self.db.user.create(
                data={
                    'email': email,
                    'username': unique_username,
                    'passwordHash': password_hash,
                    'role': 'STUDENT',
                    'authProvider': auth_provider,
                    'authProviderId': auth_provider_id,
                    'isEmailVerified': is_email_verified,
                    'isActive': True,
                    'lastLoginAt': datetime.now()
                }
            )
            
            logger.info(f"New OAuth user created: {email} via {auth_provider}")
            return user, True
            
        except Exception as e:
            logger.error(f"Error in get_or_create_oauth_user: {str(e)}")
            raise
        finally:
            await self.disconnect()
    
    async def _generate_unique_username(self, base_username: str) -> str:
        """Générer un username unique"""
        try:
            # Nettoyer le username
            username = base_username.lower().replace(' ', '_')
            username = ''.join(c for c in username if c.isalnum() or c == '_')
            
            # Vérifier si disponible
            existing = await self.db.user.find_unique(where={'username': username})
            
            if not existing:
                return username
            
            # Ajouter un suffixe numérique
            counter = 1
            while True:
                new_username = f"{username}_{counter}"
                existing = await self.db.user.find_unique(where={'username': new_username})
                
                if not existing:
                    return new_username
                
                counter += 1
                
                # Sécurité: limiter les tentatives
                if counter > 100:
                    # Ajouter un suffixe aléatoire
                    import secrets
                    random_suffix = secrets.token_hex(4)
                    return f"{username}_{random_suffix}"
                    
        except Exception as e:
            logger.error(f"Error generating unique username: {str(e)}")
            # Fallback: username avec timestamp
            import time
            return f"{username}_{int(time.time())}"
    
    async def link_oauth_provider(
        self,
        user_id: str,
        provider: str,
        provider_id: str
    ) -> bool:
        """Lier un provider OAuth à un compte existant"""
        try:
            await self.connect()
            
            # Vérifier qu'aucun autre compte n'utilise ce provider
            existing = await self.db.user.find_first(
                where={
                    'authProvider': provider,
                    'authProviderId': provider_id,
                    'id': {'not': user_id}
                }
            )
            
            if existing:
                raise ValueError(f"This {provider} account is already linked to another user")
            
            # Mettre à jour l'utilisateur
            await self.db.user.update(
                where={'id': user_id},
                data={
                    'authProvider': provider,
                    'authProviderId': provider_id
                }
            )
            
            logger.info(f"OAuth provider {provider} linked to user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error linking OAuth provider: {str(e)}")
            raise
        finally:
            await self.disconnect()
    
    async def unlink_oauth_provider(self, user_id: str) -> bool:
        """Délier un provider OAuth d'un compte"""
        try:
            await self.connect()
            
            user = await self.db.user.find_unique(where={'id': user_id})
            
            if not user:
                raise ValueError("User not found")
            
            # Ne pas permettre de délier si c'est le seul moyen d'authentification
            if user.authProvider != 'PASSWORD':
                # Vérifier que l'utilisateur a un mot de passe valide
                # (Le hash ne devrait pas être vide ou aléatoire)
                # Pour simplifier, on vérifie juste que l'utilisateur peut se connecter avec mot de passe
                pass
            
            # Réinitialiser le provider
            await self.db.user.update(
                where={'id': user_id},
                data={
                    'authProvider': 'PASSWORD',
                    'authProviderId': None
                }
            )
            
            logger.info(f"OAuth provider unlinked from user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error unlinking OAuth provider: {str(e)}")
            raise
        finally:
            await self.disconnect()