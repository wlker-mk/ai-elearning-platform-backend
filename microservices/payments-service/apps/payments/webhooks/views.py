"""
apps/payments/webhooks/views.py
Gestion des webhooks Stripe et PayPal
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from asgiref.sync import async_to_sync
import logging
import json
import stripe

from apps.payments.gateways.services import PaymentService
from apps.payments.subscriptions.services import SubscriptionService
from django.conf import settings

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(APIView):
    """Vue pour gérer les webhooks Stripe"""
    
    permission_classes = []
    authentication_classes = []
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.payment_service = PaymentService()
        self.subscription_service = SubscriptionService()
        stripe.api_key = settings.STRIPE_CONFIG.get('SECRET_KEY', '')
    
    def post(self, request):
        """Traiter les événements Stripe"""
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        
        try:
            event = stripe.Webhook.construct_event(
                payload, 
                sig_header, 
                settings.STRIPE_CONFIG.get('WEBHOOK_SECRET', '')
            )
        except ValueError as e:
            logger.error(f"Invalid payload: {str(e)}")
            return Response(
                {'error': 'Invalid payload'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid signature: {str(e)}")
            return Response(
                {'error': 'Invalid signature'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        event_type = event['type']
        
        try:
            if event_type == 'payment_intent.succeeded':
                self._handle_payment_succeeded(event['data']['object'])
            elif event_type == 'payment_intent.payment_failed':
                self._handle_payment_failed(event['data']['object'])
            elif event_type == 'charge.refunded':
                self._handle_refund(event['data']['object'])
            else:
                logger.info(f"Unhandled event type: {event_type}")
            
            return Response({'status': 'success'}, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error processing webhook: {str(e)}")
            return Response(
                {'error': 'Webhook processing failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _handle_payment_succeeded(self, payment_intent):
        """G�rer le succ�s d'un paiement"""
        payment_id = payment_intent.get('metadata', {}).get('payment_id')
        if payment_id:
            async_to_sync(self.payment_service.confirm_payment)(
                payment_id,
                payment_intent['id']
            )
            logger.info(f"Payment succeeded: {payment_id}")
    
    def _handle_payment_failed(self, payment_intent):
        """G�rer l'�chec d'un paiement"""
        payment_id = payment_intent.get('metadata', {}).get('payment_id')
        if payment_id:
            async_to_sync(self.payment_service.connect)()
            async_to_sync(self.payment_service.db.payment.update)(
                where={'id': payment_id},
                data={'status': 'FAILED'}
            )
            async_to_sync(self.payment_service.disconnect)()
            logger.warning(f"Payment failed: {payment_id}")
    
    def _handle_refund(self, charge):
        """Gérer un remboursement"""
        payment_intent_id = charge.get('payment_intent')
        logger.info(f"Refund processed for: {payment_intent_id}")


@method_decorator(csrf_exempt, name='dispatch')
class PayPalWebhookView(APIView):
    """Vue pour gérer les webhooks PayPal"""
    
    permission_classes = []
    authentication_classes = []
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.payment_service = PaymentService()
    
    def post(self, request):
        """Traiter les événements PayPal"""
        try:
            event = json.loads(request.body)
            event_type = event.get('event_type')
            
            if event_type == 'PAYMENT.CAPTURE.COMPLETED':
                self._handle_payment_completed(event)
            elif event_type == 'PAYMENT.CAPTURE.DENIED':
                self._handle_payment_denied(event)
            else:
                logger.info(f"Unhandled PayPal event: {event_type}")
            
            return Response({'status': 'success'}, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error processing PayPal webhook: {str(e)}")
            return Response(
                {'error': 'Webhook processing failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _handle_payment_completed(self, event):
        """Gérer un paiement complété"""
        resource = event.get('resource', {})
        payment_id = resource.get('custom_id')
        if payment_id:
            async_to_sync(self.payment_service.confirm_payment)(
                payment_id,
                resource.get('id')
            )
            logger.info(f"PayPal payment completed: {payment_id}")
    
    def _handle_payment_denied(self, event):
        """Gérer un paiement refusé"""
        resource = event.get('resource', {})
        payment_id = resource.get('custom_id')
        if payment_id:
            async_to_sync(self.payment_service.connect)()
            async_to_sync(self.payment_service.db.payment.update)(
                where={'id': payment_id},
                data={'status': 'FAILED'}
            )
            async_to_sync(self.payment_service.disconnect)()
            logger.warning(f"PayPal payment denied: {payment_id}")
