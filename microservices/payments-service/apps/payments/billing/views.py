from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from asgiref.sync import async_to_sync
import logging

from apps.payments import InvoiceService
from apps.payments.serializers import (
    InvoiceSerializer,
    CreateInvoiceSerializer
)

logger = logging.getLogger(__name__)


class InvoiceView(APIView):
    """Vue pour gérer les factures"""
    
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = InvoiceService()
    
    def get(self, request, invoice_id=None):
        """Récupérer une ou plusieurs factures"""
        try:
            if invoice_id:
                invoice = async_to_sync(self.service.get_invoice)(invoice_id)
                
                if not invoice:
                    return Response(
                        {'error': 'Invoice not found'},
                        status=status.HTTP_404_NOT_FOUND
                    )
                
                serializer = InvoiceSerializer(invoice)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                student_id = request.query_params.get('student_id', str(request.user.id))
                invoice_status = request.query_params.get('status')
                limit = int(request.query_params.get('limit', 50))
                
                invoices = async_to_sync(self.service.get_student_invoices)(
                    student_id, invoice_status, limit
                )
                
                serializer = InvoiceSerializer(invoices, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting invoices: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        """Créer une facture"""
        try:
            serializer = CreateInvoiceSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            invoice = async_to_sync(self.service.create_invoice)(
                student_id=str(serializer.validated_data['student_id']),
                items=serializer.validated_data['items'],
                currency=serializer.validated_data['currency'],
                tax_country=serializer.validated_data.get('tax_country'),
                discount_amount=serializer.validated_data['discount_amount'],
                due_days=serializer.validated_data['due_days']
            )
            
            response_serializer = InvoiceSerializer(invoice)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error creating invoice: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class InvoiceByNumberView(APIView):
    """Vue pour récupérer une facture par numéro"""
    
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = InvoiceService()
    
    def get(self, request, invoice_number):
        """Récupérer une facture par son numéro"""
        try:
            invoice = async_to_sync(self.service.get_invoice_by_number)(invoice_number)
            
            if not invoice:
                return Response(
                    {'error': 'Invoice not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            serializer = InvoiceSerializer(invoice)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting invoice: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class OverdueInvoicesView(APIView):
    """Vue pour récupérer les factures en retard"""
    
    permission_classes = [IsAdminUser]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = InvoiceService()
    
    def get(self, request):
        """Récupérer les factures en retard"""
        try:
            invoices = async_to_sync(self.service.get_overdue_invoices)()
            
            serializer = InvoiceSerializer(invoices, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting overdue invoices: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
