from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from asgiref.sync import async_to_sync
import logging

from apps.payments import PaymentService
from apps.payments.serializers import (
    PaymentSerializer,
    CreatePaymentSerializer,
    RefundPaymentSerializer
)

logger = logging.getLogger(__name__)


class PaymentView(APIView):
    """Vue pour gérer les paiements"""
    
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = PaymentService()
    
    def get(self, request, payment_id=None):
        """Récupérer un ou plusieurs paiements"""
        try:
            if payment_id:
                # Récupérer un paiement spécifique
                payment = async_to_sync(self.service.get_payment)(payment_id)
                
                if not payment:
                    return Response(
                        {'error': 'Payment not found'},
                        status=status.HTTP_404_NOT_FOUND
                    )
                
                serializer = PaymentSerializer(payment)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                # Récupérer les paiements de l'utilisateur
                student_id = request.query_params.get('student_id', str(request.user.id))
                payment_status = request.query_params.get('status')
                limit = int(request.query_params.get('limit', 50))
                
                payments = async_to_sync(self.service.get_student_payments)(
                    student_id, payment_status, limit
                )
                
                serializer = PaymentSerializer(payments, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting payments: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        """Créer et traiter un paiement"""
        try:
            serializer = CreatePaymentSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            # Créer le paiement
            payment = async_to_sync(self.service.create_payment)(
                student_id=str(serializer.validated_data['student_id']),
                amount=serializer.validated_data['amount'],
                currency=serializer.validated_data['currency'],
                method=serializer.validated_data['method'],
                course_id=str(serializer.validated_data.get('course_id')) if serializer.validated_data.get('course_id') else None,
                subscription_id=str(serializer.validated_data.get('subscription_id')) if serializer.validated_data.get('subscription_id') else None,
                items=serializer.validated_data.get('items'),
                description=serializer.validated_data.get('description')
            )
            
            # Traiter le paiement avec la passerelle
            gateway = serializer.validated_data.get('gateway', 'STRIPE')
            processed_payment = async_to_sync(self.service.process_payment)(
                payment.id,
                gateway
            )
            
            response_serializer = PaymentSerializer(processed_payment)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error creating payment: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ConfirmPaymentView(APIView):
    """Vue pour confirmer un paiement"""
    
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = PaymentService()
    
    def post(self, request, payment_id):
        """Confirmer un paiement après validation par la passerelle"""
        try:
            transaction_id = request.data.get('transaction_id')
            
            if not transaction_id:
                return Response(
                    {'error': 'transaction_id is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            payment = async_to_sync(self.service.confirm_payment)(
                payment_id,
                transaction_id
            )
            
            serializer = PaymentSerializer(payment)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error confirming payment: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RefundPaymentView(APIView):
    """Vue pour rembourser un paiement"""
    
    permission_classes = [IsAdminUser]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = PaymentService()
    
    def post(self, request, payment_id):
        """Rembourser un paiement"""
        try:
            serializer = RefundPaymentSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            payment = async_to_sync(self.service.refund_payment)(
                payment_id,
                serializer.validated_data.get('amount'),
                serializer.validated_data.get('reason')
            )
            
            response_serializer = PaymentSerializer(payment)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
            
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error refunding payment: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PaymentStatisticsView(APIView):
    """Vue pour les statistiques de paiement"""
    
    permission_classes = [IsAdminUser]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = PaymentService()
    
    def get(self, request):
        """Récupérer les statistiques"""
        try:
            from datetime import datetime, timedelta
            
            days = int(request.query_params.get('days', 30))
            start_date = datetime.now() - timedelta(days=days)
            
            stats = async_to_sync(self.service.get_payment_statistics)(
                start_date=start_date
            )
            
            return Response(stats, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting statistics: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )