from django.utils.deprecation import MiddlewareMixin
import jwt
from django.conf import settings

class JWTAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                request.user_id = payload.get('user_id')
            except jwt.InvalidTokenError:
                pass
        
        return None
