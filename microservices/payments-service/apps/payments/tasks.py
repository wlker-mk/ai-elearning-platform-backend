"""
apps/payments/tasks.py
T�ches asynchrones pour les paiements
"""
from celery import shared_task
from asgiref.sync import async_to_sync
import logging
from datetime import datetime, timedelta

from apps.payments.subscriptions.services import SubscriptionService
from apps.payments.billing.services import InvoiceService
from apps.payments.gateways.services import PaymentService

logger = logging.getLogger(__name__)


@shared_task(name='payments.check_expired_subscriptions')
def check_expired_subscriptions():
    """Vérifier et désactiver les abonnements expirés"""
    try:
        service = SubscriptionService()
        count = async_to_sync(service.check_and_expire_subscriptions)()
        logger.info(f"Expired {count} subscriptions")
        return {'expired': count}
    except Exception as e:
        logger.error(f"Error checking expired subscriptions: {str(e)}")
        raise


@shared_task(name='payments.process_subscription_renewals')
def process_subscription_renewals():
    """Traiter les renouvellements d'abonnements"""
    try:
        subscription_service = SubscriptionService()
        payment_service = PaymentService()
        
        subscriptions = async_to_sync(
            subscription_service.get_subscriptions_to_renew
        )()
        
        renewed_count = 0
        failed_count = 0
        
        for subscription in subscriptions:
            try:
                payment = async_to_sync(payment_service.create_payment)(
                    student_id=subscription.studentId,
                    amount=subscription.price,
                    currency=subscription.currency,
                    method=subscription.paymentMethod,
                    subscription_id=subscription.id,
                    description=f"Subscription renewal - {subscription.type}"
                )
                
                async_to_sync(payment_service.process_payment)(
                    payment.id,
                    'STRIPE'
                )
                
                renewed_count += 1
                logger.info(f"Renewed subscription: {subscription.id}")
                
            except Exception as e:
                failed_count += 1
                logger.error(f"Failed to renew subscription {subscription.id}: {str(e)}")
        
        return {
            'processed': len(subscriptions),
            'renewed': renewed_count,
            'failed': failed_count
        }
        
    except Exception as e:
        logger.error(f"Error processing renewals: {str(e)}")
        raise


@shared_task(name='payments.send_overdue_invoice_reminders')
def send_overdue_invoice_reminders():
    """Envoyer des rappels pour les factures en retard"""
    try:
        service = InvoiceService()
        overdue_invoices = async_to_sync(service.get_overdue_invoices)()
        
        reminder_count = 0
        for invoice in overdue_invoices:
            logger.info(f"Reminder needed for invoice: {invoice.invoiceNumber}")
            reminder_count += 1
        
        return {'reminders_sent': reminder_count}
        
    except Exception as e:
        logger.error(f"Error sending reminders: {str(e)}")
        raise


@shared_task(name='payments.generate_payment_reports')
def generate_payment_reports():
    """Générer des rapports de paiements mensuels"""
    try:
        service = PaymentService()
        
        start_date = datetime.now().replace(day=1) - timedelta(days=1)
        start_date = start_date.replace(day=1)
        end_date = datetime.now().replace(day=1)
        
        stats = async_to_sync(service.get_payment_statistics)(
            start_date=start_date,
            end_date=end_date
        )
        
        logger.info(f"Monthly report generated: {stats}")
        return stats
        
    except Exception as e:
        logger.error(f"Error generating reports: {str(e)}")
        raise
