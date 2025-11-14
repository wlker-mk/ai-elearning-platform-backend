from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from asgiref.sync import async_to_sync
from apps.authentication.services import SessionService


class JWTAuthentication(BaseAuthentication):
    """Custom JWT Authentication en utilisant les sessions Prisma"""
    
    def __init__(self):
        self.session_service = SessionService()
    
    def authenticate(self, request):
        """Authentifier la requête"""
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        
        if not auth_header:
            return None
        
        try:
            # Format: Bearer <token>
            parts = auth_header.split()
            
            if parts[0].lower() != 'bearer':
                return None
            
            if len(parts) == 1:
                raise AuthenticationFailed('Invalid token header. No credentials provided.')
            elif len(parts) > 2:
                raise AuthenticationFailed('Invalid token header. Token string should not contain spaces.')
            
            token = parts[1]
            
            # Valider la session
            session = async_to_sync(self.session_service.validate_session)(token)
            
            if not session:
                raise AuthenticationFailed('Invalid or expired token')
            
            # Créer un objet user simple
            class SimpleUser:
                def __init__(self, user_id):
                    self.id = user_id
                    self.is_authenticated = True
            
            user = SimpleUser(session.userId)
            
            return (user, token)
            
        except Exception as e:
            raise AuthenticationFailed(str(e))