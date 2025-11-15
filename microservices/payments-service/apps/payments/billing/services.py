from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from prisma import Prisma
from prisma.models import Invoice
import logging
from shared.shared.payments.utils import generate_invoice_number, calculate_tax

logger = logging.getLogger(__name__)


class InvoiceService:
    """Service de gestion des factures"""
    
    def __init__(self):
        self.db = Prisma()
    
    async def connect(self):
        if not self.db.is_connected():
            await self.db.connect()
    
    async def disconnect(self):
        if self.db.is_connected():
            await self.db.disconnect()
    
    async def create_invoice(
        self,
        student_id: str,
        items: List[Dict[str, Any]],
        payment_id: Optional[str] = None,
        currency: str = 'USD',
        tax_country: Optional[str] = None,
        discount_amount: float = 0,
        due_days: int = 30
    ) -> Invoice:
        """Créer une facture"""
        try:
            await self.connect()
            
            # Calculer le sous-total
            subtotal = sum(item['price'] * item.get('quantity', 1) for item in items)
            
            # Calculer la taxe
            tax = 0
            if tax_country:
                from shared.shared.payments.constants import TAX_RATES
                tax = calculate_tax(subtotal, tax_country, TAX_RATES)
            
            # Calculer le total
            total = subtotal + tax - discount_amount
            amount_due = total
            
            # Générer le numéro de facture
            invoice_number = generate_invoice_number()
            
            # Date d'échéance
            due_date = datetime.now() + timedelta(days=due_days)
            
            # Créer la facture
            invoice = await self.db.invoice.create(
                data={
                    'invoiceNumber': invoice_number,
                    'studentId': student_id,
                    'paymentId': payment_id,
                    'subtotal': subtotal,
                    'tax': tax,
                    'discount': discount_amount,
                    'total': total,
                    'amountDue': amount_due,
                    'currency': currency,
                    'status': 'PENDING',
                    'items': items,
                    'dueDate': due_date
                }
            )
            
            logger.info(f"Invoice created: {invoice.invoiceNumber}")
            return invoice
            
        except Exception as e:
            logger.error(f"Error creating invoice: {str(e)}")
            raise
        finally:
            await self.disconnect()
    
    async def mark_invoice_paid(
        self,
        invoice_id: str,
        payment_id: str,
        amount_paid: float
    ) -> Invoice:
        """Marquer une facture comme payée"""
        try:
            await self.connect()
            
            invoice = await self.db.invoice.find_unique(where={'id': invoice_id})
            
            if not invoice:
                raise ValueError("Invoice not found")
            
            # Mettre à jour le montant payé
            new_amount_paid = invoice.amountPaid + amount_paid
            new_amount_due = invoice.total - new_amount_paid
            
            # Déterminer le statut
            if new_amount_due <= 0:
                status = 'COMPLETED'
                paid_at = datetime.now()
            else:
                status = 'PROCESSING'
                paid_at = None
            
            # Mettre à jour la facture
            updated_invoice = await self.db.invoice.update(
                where={'id': invoice_id},
                data={
                    'paymentId': payment_id,
                    'amountPaid': new_amount_paid,
                    'amountDue': max(0, new_amount_due),
                    'status': status,
                    'paidAt': paid_at
                }
            )
            
            logger.info(f"Invoice marked as paid: {invoice.invoiceNumber}")
            return updated_invoice
            
        except Exception as e:
            logger.error(f"Error marking invoice paid: {str(e)}")
            raise
        finally:
            await self.disconnect()
    
    async def get_invoice(self, invoice_id: str) -> Optional[Invoice]:
        """Récupérer une facture"""
        try:
            await self.connect()
            return await self.db.invoice.find_unique(where={'id': invoice_id})
        except Exception as e:
            logger.error(f"Error getting invoice: {str(e)}")
            return None
        finally:
            await self.disconnect()
    
    async def get_invoice_by_number(self, invoice_number: str) -> Optional[Invoice]:
        """Récupérer une facture par numéro"""
        try:
            await self.connect()
            return await self.db.invoice.find_unique(where={'invoiceNumber': invoice_number})
        except Exception as e:
            logger.error(f"Error getting invoice by number: {str(e)}")
            return None
        finally:
            await self.disconnect()
    
    async def get_student_invoices(
        self,
        student_id: str,
        status: Optional[str] = None,
        limit: int = 50
    ) -> List[Invoice]:
        """Récupérer les factures d'un étudiant"""
        try:
            await self.connect()
            
            where_clause = {'studentId': student_id}
            if status:
                where_clause['status'] = status
            
            invoices = await self.db.invoice.find_many(
                where=where_clause,
                order={'createdAt': 'desc'},
                take=limit
            )
            
            return invoices
            
        except Exception as e:
            logger.error(f"Error getting student invoices: {str(e)}")
            return []
        finally:
            await self.disconnect()
    
    async def get_overdue_invoices(self) -> List[Invoice]:
        """Récupérer les factures en retard"""
        try:
            await self.connect()
            
            invoices = await self.db.invoice.find_many(
                where={
                    'status': {'in': ['PENDING', 'PROCESSING']},
                    'dueDate': {'lt': datetime.now()}
                },
                order={'dueDate': 'asc'}
            )
            
            return invoices
            
        except Exception as e:
            logger.error(f"Error getting overdue invoices: {str(e)}")
            return []
        finally:
            await self.disconnect()
    
    async def generate_invoice_pdf(self, invoice_id: str) -> str:
        """Générer un PDF de facture"""
        # TODO: Implémenter la génération de PDF
        # Utiliser ReportLab ou WeasyPrint
        pass
