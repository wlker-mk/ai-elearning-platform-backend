import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        logger.info(f"{request.method} {request.path}")
        return None
    
    def process_response(self, request, response):
        logger.info(f"{request.method} {request.path} - {response.status_code}")
        return response
