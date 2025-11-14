from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from asgiref.sync import async_to_sync
import logging

from apps.analytics.services import SearchLogService
from apps.analytics.serializers import SearchLogSerializer, LogSearchSerializer

logger = logging.getLogger(__name__)


class LogSearchView(APIView):
    """Vue pour enregistrer les recherches"""
    
    permission_classes = [AllowAny]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = SearchLogService()
    
    def post(self, request):
        """Enregistrer une recherche"""
        try:
            serializer = LogSearchSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            ip_address = self.get_client_ip(request)
            
            log = async_to_sync(self.service.log_search)(
                query=serializer.validated_data['query'],
                results_count=serializer.validated_data['results_count'],
                user_id=str(serializer.validated_data.get('user_id')) if serializer.validated_data.get('user_id') else None,
                ip_address=ip_address,
                clicked_result=serializer.validated_data.get('clicked_result')
            )
            
            response_serializer = SearchLogSerializer(log)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error logging search: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class PopularSearchesView(APIView):
    """Vue pour récupérer les recherches populaires"""
    
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = SearchLogService()
    
    def get(self, request):
        """Récupérer les recherches populaires"""
        try:
            limit = int(request.query_params.get('limit', 10))
            days = int(request.query_params.get('days', 30))
            
            searches = async_to_sync(self.service.get_popular_searches)(
                limit=limit,
                days=days
            )
            
            return Response(searches, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting popular searches: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ZeroResultSearchesView(APIView):
    """Vue pour récupérer les recherches sans résultats"""
    
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = SearchLogService()
    
    def get(self, request):
        """Récupérer les recherches sans résultats"""
        try:
            limit = int(request.query_params.get('limit', 10))
            days = int(request.query_params.get('days', 30))
            
            searches = async_to_sync(self.service.get_zero_result_searches)(
                limit=limit,
                days=days
            )
            
            return Response(searches, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting zero result searches: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SearchTrendsView(APIView):
    """Vue pour récupérer les tendances de recherche"""
    
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = SearchLogService()
    
    def get(self, request):
        """Récupérer les tendances"""
        try:
            days = int(request.query_params.get('days', 7))
            
            trends = async_to_sync(self.service.get_search_trends)(days=days)
            
            return Response(trends, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting search trends: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )