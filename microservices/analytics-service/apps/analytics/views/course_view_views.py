from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from asgiref.sync import async_to_sync
from datetime import datetime, timedelta
import logging

from apps.analytics.services import CourseViewService
from apps.analytics.serializers import (
    CourseViewSerializer,
    TrackCourseViewSerializer
)

logger = logging.getLogger(__name__)


class TrackCourseViewView(APIView):
    """Vue pour tracker les vues de cours"""
    
    permission_classes = [AllowAny]  # Accessible publiquement
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = CourseViewService()
    
    def post(self, request):
        """Enregistrer une vue de cours"""
        try:
            serializer = TrackCourseViewSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            # Récupérer les informations de la requête
            ip_address = self.get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT')
            
            view = async_to_sync(self.service.track_view)(
                course_id=str(serializer.validated_data['course_id']),
                user_id=str(serializer.validated_data.get('user_id')) if serializer.validated_data.get('user_id') else None,
                ip_address=ip_address,
                user_agent=user_agent,
                country=serializer.validated_data.get('country'),
                city=serializer.validated_data.get('city'),
                referrer=serializer.validated_data.get('referrer'),
                source=serializer.validated_data.get('source')
            )
            
            response_serializer = CourseViewSerializer(view)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error tracking course view: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get_client_ip(self, request):
        """Récupérer l'IP du client"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class CourseViewStatsView(APIView):
    """Vue pour récupérer les statistiques de vues"""
    
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = CourseViewService()
    
    def get(self, request, course_id):
        """Récupérer les statistiques de vues d'un cours"""
        try:
            days = int(request.query_params.get('days', 30))
            
            # Stats basiques
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            total_views = async_to_sync(self.service.get_total_views)(
                course_id, start_date, end_date
            )
            
            unique_viewers = async_to_sync(self.service.get_unique_viewers)(
                course_id, start_date, end_date
            )
            
            daily_views = async_to_sync(self.service.get_daily_views)(
                course_id, days
            )
            
            views_by_country = async_to_sync(self.service.get_views_by_country)(
                course_id, limit=10
            )
            
            views_by_source = async_to_sync(self.service.get_views_by_source)(
                course_id
            )
            
            return Response({
                'course_id': course_id,
                'period_days': days,
                'total_views': total_views,
                'unique_viewers': unique_viewers,
                'daily_views': daily_views,
                'views_by_country': views_by_country,
                'views_by_source': views_by_source
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting course view stats: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )