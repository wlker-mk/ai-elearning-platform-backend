from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from asgiref.sync import async_to_sync
import logging

from apps.analytics.services import VideoAnalyticsService
from apps.analytics.serializers import (
    VideoAnalyticsSerializer,
    UpdateWatchTimeSerializer,
    UpdateCompletionSerializer,
    VideoEventSerializer
)

logger = logging.getLogger(__name__)


class VideoAnalyticsView(APIView):
    """Vue pour gérer les analytics vidéo"""
    
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = VideoAnalyticsService()
    
    def get(self, request):
        """Récupérer les analytics d'une vidéo"""
        try:
            lesson_id = request.query_params.get('lesson_id')
            student_id = request.query_params.get('student_id')
            
            if not lesson_id or not student_id:
                return Response(
                    {'error': 'lesson_id and student_id are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            analytics = async_to_sync(self.service.get_analytics)(
                lesson_id, student_id
            )
            
            if not analytics:
                return Response(
                    {'error': 'Analytics not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            serializer = VideoAnalyticsSerializer(analytics)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting video analytics: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UpdateWatchTimeView(APIView):
    """Vue pour mettre à jour le temps de visionnage"""
    
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = VideoAnalyticsService()
    
    def post(self, request):
        """Mettre à jour le temps de visionnage"""
        try:
            serializer = UpdateWatchTimeSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            analytics = async_to_sync(self.service.update_watch_time)(
                str(serializer.validated_data['lesson_id']),
                str(serializer.validated_data['student_id']),
                serializer.validated_data['watch_time'],
                serializer.validated_data['position']
            )
            
            response_serializer = VideoAnalyticsSerializer(analytics)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error updating watch time: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UpdateCompletionView(APIView):
    """Vue pour mettre à jour le taux de complétion"""
    
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = VideoAnalyticsService()
    
    def post(self, request):
        """Mettre à jour le taux de complétion"""
        try:
            serializer = UpdateCompletionSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            analytics = async_to_sync(self.service.update_completion_rate)(
                str(serializer.validated_data['lesson_id']),
                str(serializer.validated_data['student_id']),
                serializer.validated_data['completion_rate']
            )
            
            response_serializer = VideoAnalyticsSerializer(analytics)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error updating completion: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class VideoEventView(APIView):
    """Vue pour enregistrer les événements vidéo"""
    
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = VideoAnalyticsService()
    
    def post(self, request):
        """Enregistrer un événement vidéo"""
        try:
            serializer = VideoEventSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            lesson_id = str(serializer.validated_data['lesson_id'])
            student_id = str(serializer.validated_data['student_id'])
            event_type = serializer.validated_data['event_type']
            
            if event_type == 'pause':
                analytics = async_to_sync(self.service.increment_pause_count)(
                    lesson_id, student_id
                )
            elif event_type == 'rewind':
                analytics = async_to_sync(self.service.increment_rewind_count)(
                    lesson_id, student_id
                )
            elif event_type == 'speed_change':
                analytics = async_to_sync(self.service.increment_speed_changes)(
                    lesson_id, student_id
                )
            elif event_type == 'quality':
                quality = serializer.validated_data.get('quality')
                if not quality:
                    return Response(
                        {'error': 'quality is required for quality event'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                analytics = async_to_sync(self.service.update_quality)(
                    lesson_id, student_id, quality
                )
            else:
                return Response(
                    {'error': 'Invalid event type'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            response_serializer = VideoAnalyticsSerializer(analytics)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error recording video event: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LessonEngagementView(APIView):
    """Vue pour récupérer les statistiques d'engagement d'une leçon"""
    
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = VideoAnalyticsService()
    
    def get(self, request, lesson_id):
        """Récupérer les stats d'engagement"""
        try:
            stats = async_to_sync(self.service.get_engagement_stats)(lesson_id)
            
            return Response(stats, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting engagement stats: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )