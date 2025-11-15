from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from asgiref.sync import async_to_sync
import logging

from apps.payments import SubscriptionService, DiscountService
from apps.payments.serializers import (
    SubscriptionSerializer,
    CreateSubscriptionSerializer,
    CancelSubscriptionSerializer,
    DiscountSerializer,
    CreateDiscountSerializer,
    ValidateDiscountSerializer
)

logger = logging.getLogger(__name__)


class SubscriptionView(APIView):
    """Vue pour gérer les abonnements"""
    
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = SubscriptionService()
    
    def get(self, request, subscription_id=None):
        """Récupérer un abonnement"""
        try:
            if subscription_id:
                subscription = async_to_sync(self.service.get_subscription)(subscription_id)
            else:
                student_id = request.query_params.get('student_id', str(request.user.id))
                subscription = async_to_sync(self.service.get_student_subscription)(student_id)
            
            if not subscription:
                return Response(
                    {'error': 'Subscription not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            serializer = SubscriptionSerializer(subscription)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting subscription: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        """Créer un abonnement"""
        try:
            serializer = CreateSubscriptionSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            subscription = async_to_sync(self.service.create_subscription)(
                student_id=str(serializer.validated_data['student_id']),
                subscription_type=serializer.validated_data['type'],
                payment_method=serializer.validated_data['payment_method'],
                payment_id=str(serializer.validated_data.get('payment_id')) if serializer.validated_data.get('payment_id') else None,
                trial_days=serializer.validated_data['trial_days']
            )
            
            response_serializer = SubscriptionSerializer(subscription)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error creating subscription: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CancelSubscriptionView(APIView):
    """Vue pour annuler un abonnement"""
    
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = SubscriptionService()
    
    def post(self, request, subscription_id):
        """Annuler un abonnement"""
        try:
            serializer = CancelSubscriptionSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            subscription = async_to_sync(self.service.cancel_subscription)(
                subscription_id,
                serializer.validated_data['immediate']
            )
            
            response_serializer = SubscriptionSerializer(subscription)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
            
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error cancelling subscription: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DiscountView(APIView):
    """Vue pour gérer les codes de réduction"""
    
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = DiscountService()
    
    def get(self, request):
        """Récupérer les codes actifs"""
        try:
            discounts = async_to_sync(self.service.get_active_discounts)()
            
            serializer = DiscountSerializer(discounts, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting discounts: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        """Créer un code de réduction (Admin uniquement)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            serializer = CreateDiscountSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            discount = async_to_sync(self.service.create_discount)(
                code=serializer.validated_data['code'],
                discount_type=serializer.validated_data['type'],
                value=serializer.validated_data['value'],
                start_date=serializer.validated_data['start_date'],
                end_date=serializer.validated_data['end_date'],
                max_uses=serializer.validated_data.get('max_uses'),
                max_uses_per_user=serializer.validated_data['max_uses_per_user']
            )
            
            response_serializer = DiscountSerializer(discount)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error creating discount: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ValidateDiscountView(APIView):
    """Vue pour valider un code de réduction"""
    
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = DiscountService()
    
    def post(self, request):
        """Valider un code"""
        try:
            serializer = ValidateDiscountSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            is_valid, message, discount = async_to_sync(self.service.validate_discount)(
                serializer.validated_data['code'],
                str(serializer.validated_data['user_id'])
            )
            
            if not is_valid:
                return Response(
                    {'valid': False, 'message': message},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            response_serializer = DiscountSerializer(discount)
            return Response({
                'valid': True,
                'message': message,
                'discount': response_serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error validating discount: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
