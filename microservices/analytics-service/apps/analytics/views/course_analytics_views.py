from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from asgiref.sync import async_to_sync
from datetime import date, timedelta
import logging

from apps.analytics.services import CourseAnalyticsService
from apps.analytics.serializers import CourseAnalyticsSerializer, UpdateCourseAnalyticsSerializer

logger = logging.getLogger(__name__)


class CourseAnalyticsView(APIView):
    """Vue pour gérer les analytics de cours"""
    
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = CourseAnalyticsService()
    
    def post(self, request):
        """Mettre à jour les analytics"""
        try:
            serializer = UpdateCourseAnalyticsSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            analytics_date = serializer.validated_data.get('date', date.today())
            
            analytics = async_to_sync(self.service.create_or_update_analytics)(
                course_id=str(serializer.validated_data['course_id']),
                analytics_date=analytics_date,
                views=serializer.validated_data.get('views', 0),
                enrollments=serializer.validated_data.get('enrollments', 0),
                completions=serializer.validated_data.get('completions', 0),
                rating=serializer.validated_data.get('rating')
            )
            
            response_serializer = CourseAnalyticsSerializer(analytics)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error updating course analytics: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CourseStatsView(APIView):
    """Vue pour récupérer les statistiques d'un cours"""
    
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = CourseAnalyticsService()
    
    def get(self, request, course_id):
        """Récupérer les statistiques"""
        try:
            days = int(request.query_params.get('days', 30))
            
            end_date = date.today()
            start_date = end_date - timedelta(days=days-1)
            
            total_stats = async_to_sync(self.service.get_total_stats)(
                course_id=course_id,
                start_date=start_date,
                end_date=end_date
            )
            
            daily_analytics = async_to_sync(self.service.get_daily_analytics)(
                course_id=course_id,
                days=days
            )
            
            return Response({
                'course_id': course_id,
                'period_days': days,
                'total_stats': total_stats,
                'daily_analytics': daily_analytics
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting course stats: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TopCoursesView(APIView):
    """Vue pour récupérer les meilleurs cours"""
    
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = CourseAnalyticsService()
    
    def get(self, request):
        """Récupérer les meilleurs cours"""
        try:
            metric = request.query_params.get('metric', 'views')
            limit = int(request.query_params.get('limit', 10))
            days = int(request.query_params.get('days', 30))
            
            top_courses = async_to_sync(self.service.get_top_courses)(
                metric=metric,
                limit=limit,
                days=days
            )
            
            return Response(top_courses, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting top courses: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
