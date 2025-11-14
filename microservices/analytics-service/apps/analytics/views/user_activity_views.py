from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from asgiref.sync import async_to_sync
import logging

from apps.analytics.services import UserActivityService
from apps.analytics.serializers import UserActivitySerializer, TrackActivitySerializer

logger = logging.getLogger(__name__)


class TrackUserActivityView(APIView):
    """Vue pour enregistrer l'activité utilisateur"""
    
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = UserActivityService()
    
    def post(self, request):
        """Enregistrer une activité"""
        try:
            serializer = TrackActivitySerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            activity = async_to_sync(self.service.track_activity)(
                user_id=str(serializer.validated_data['user_id']),
                event_type=serializer.validated_data['event_type'],
                metadata=serializer.validated_data.get('metadata')
            )
            
            response_serializer = UserActivitySerializer(activity)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error tracking activity: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserActivityHistoryView(APIView):
    """Vue pour récupérer l'historique d'activité"""
    
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = UserActivityService()
    
    def get(self, request, user_id):
        """Récupérer l'historique"""
        try:
            event_type = request.query_params.get('event_type')
            limit = int(request.query_params.get('limit', 50))
            
            activities = async_to_sync(self.service.get_user_activities)(
                user_id=user_id,
                event_type=event_type,
                limit=limit
            )
            
            serializer = UserActivitySerializer(activities, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting activity history: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserActivityStatsView(APIView):
    """Vue pour récupérer les statistiques d'activité"""
    
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = UserActivityService()
    
    def get(self, request, user_id):
        """Récupérer les statistiques"""
        try:
            days = int(request.query_params.get('days', 30))
            
            daily_activity = async_to_sync(self.service.get_daily_activity)(
                user_id=user_id,
                days=days
            )
            
            activity_by_type = async_to_sync(self.service.get_activity_by_type)(
                user_id=user_id,
                days=days
            )
            
            total_count = async_to_sync(self.service.get_activity_count)(
                user_id=user_id,
                days=days
            )
            
            return Response({
                'user_id': user_id,
                'period_days': days,
                'total_activities': total_count,
                'daily_activity': daily_activity,
                'activity_by_type': activity_by_type
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting activity stats: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
