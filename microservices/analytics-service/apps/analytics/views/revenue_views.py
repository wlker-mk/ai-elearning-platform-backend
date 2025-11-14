from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from asgiref.sync import async_to_sync
from datetime import date, timedelta
import logging

from apps.analytics.services import RevenueReportService
from apps.analytics.serializers import RevenueReportSerializer, CreateRevenueReportSerializer

logger = logging.getLogger(__name__)


class RevenueReportView(APIView):
    """Vue pour gérer les rapports de revenus"""
    
    permission_classes = [IsAdminUser]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = RevenueReportService()
    
    def post(self, request):
        """Créer/Mettre à jour un rapport"""
        try:
            serializer = CreateRevenueReportSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            report = async_to_sync(self.service.create_or_update_report)(
                report_date=serializer.validated_data['date'],
                revenue=serializer.validated_data['revenue'],
                orders=serializer.validated_data['orders']
            )
            
            response_serializer = RevenueReportSerializer(report)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error creating revenue report: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DailyRevenueView(APIView):
    """Vue pour récupérer les revenus quotidiens"""
    
    permission_classes = [IsAdminUser]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = RevenueReportService()
    
    def get(self, request):
        """Récupérer les revenus quotidiens"""
        try:
            days = int(request.query_params.get('days', 30))
            
            reports = async_to_sync(self.service.get_daily_reports)(days=days)
            
            return Response(reports, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting daily revenue: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MonthlyRevenueSummaryView(APIView):
    """Vue pour récupérer le résumé mensuel"""
    
    permission_classes = [IsAdminUser]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = RevenueReportService()
    
    def get(self, request):
        """Récupérer le résumé mensuel"""
        try:
            year = int(request.query_params.get('year', date.today().year))
            month = int(request.query_params.get('month', date.today().month))
            
            summary = async_to_sync(self.service.get_monthly_summary)(
                year=year,
                month=month
            )
            
            return Response(summary, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting monthly summary: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
