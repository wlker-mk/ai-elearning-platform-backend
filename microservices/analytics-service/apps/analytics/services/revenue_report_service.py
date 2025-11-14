from typing import Optional, Dict, Any, List
from datetime import datetime, date, timedelta
from prisma import Prisma
import logging

logger = logging.getLogger(__name__)


class RevenueReportService:
    """Service pour gérer les rapports de revenus"""
    
    def __init__(self):
        self.db = Prisma()
    
    async def connect(self):
        if not self.db.is_connected():
            await self.db.connect()
    
    async def disconnect(self):
        if self.db.is_connected():
            await self.db.disconnect()
    
    async def create_or_update_report(
        self,
        report_date: date,
        revenue: float,
        orders: int
    ):
        """Créer ou mettre à jour un rapport de revenus"""
        try:
            await self.connect()
            
            # Essayer de récupérer le rapport existant
            existing = await self.db.revenuereport.find_unique(
                where={'date': report_date}
            )
            
            if existing:
                # Mettre à jour
                report = await self.db.revenuereport.update(
                    where={'date': report_date},
                    data={
                        'totalRevenue': existing.totalRevenue + revenue,
                        'totalOrders': existing.totalOrders + orders
                    }
                )
            else:
                # Créer
                report = await self.db.revenuereport.create(
                    data={
                        'date': report_date,
                        'totalRevenue': revenue,
                        'totalOrders': orders
                    }
                )
            
            logger.info(f"Revenue report updated for {report_date}")
            return report
            
        except Exception as e:
            logger.error(f"Error creating/updating revenue report: {str(e)}")
            raise
        finally:
            await self.disconnect()
    
    async def get_report(
        self,
        report_date: date
    ):
        """Récupérer un rapport de revenus"""
        try:
            await self.connect()
            
            return await self.db.revenuereport.find_unique(
                where={'date': report_date}
            )
            
        except Exception as e:
            logger.error(f"Error getting revenue report: {str(e)}")
            raise
        finally:
            await self.disconnect()
    
    async def get_reports_range(
        self,
        start_date: date,
        end_date: date
    ) -> List[Dict[str, Any]]:
        """Récupérer les rapports sur une période"""
        try:
            await self.connect()
            
            reports = await self.db.revenuereport.find_many(
                where={
                    'date': {
                        'gte': start_date,
                        'lte': end_date
                    }
                },
                order={'date': 'asc'}
            )
            
            return reports
            
        except Exception as e:
            logger.error(f"Error getting revenue reports range: {str(e)}")
            raise
        finally:
            await self.disconnect()
    
    async def get_total_revenue(
        self,
        start_date: date,
        end_date: date
    ) -> float:
        """Calculer le revenu total sur une période"""
        try:
            await self.connect()
            
            reports = await self.get_reports_range(start_date, end_date)
            total = sum(report.totalRevenue for report in reports)
            
            return round(total, 2)
            
        except Exception as e:
            logger.error(f"Error calculating total revenue: {str(e)}")
            raise
        finally:
            await self.disconnect()
    
    async def get_total_orders(
        self,
        start_date: date,
        end_date: date
    ) -> int:
        """Compter le nombre total de commandes sur une période"""
        try:
            await self.connect()
            
            reports = await self.get_reports_range(start_date, end_date)
            total = sum(report.totalOrders for report in reports)
            
            return total
            
        except Exception as e:
            logger.error(f"Error calculating total orders: {str(e)}")
            raise
        finally:
            await self.disconnect()
    
    async def get_average_order_value(
        self,
        start_date: date,
        end_date: date
    ) -> float:
        """Calculer la valeur moyenne d'une commande"""
        try:
            await self.connect()
            
            reports = await self.get_reports_range(start_date, end_date)
            
            total_revenue = sum(report.totalRevenue for report in reports)
            total_orders = sum(report.totalOrders for report in reports)
            
            if total_orders == 0:
                return 0.0
            
            avg = total_revenue / total_orders
            return round(avg, 2)
            
        except Exception as e:
            logger.error(f"Error calculating average order value: {str(e)}")
            raise
        finally:
            await self.disconnect()
    
    async def get_daily_reports(
        self,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Récupérer les rapports quotidiens"""
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=days-1)
            
            reports = await self.get_reports_range(start_date, end_date)
            
            # Créer un dictionnaire pour un accès rapide
            reports_dict = {
                report.date.strftime('%Y-%m-%d'): report
                for report in reports
            }
            
            # Créer une liste pour tous les jours
            result = []
            current_date = start_date
            while current_date <= end_date:
                date_key = current_date.strftime('%Y-%m-%d')
                report = reports_dict.get(date_key)
                
                result.append({
                    'date': date_key,
                    'revenue': report.totalRevenue if report else 0.0,
                    'orders': report.totalOrders if report else 0
                })
                
                current_date += timedelta(days=1)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting daily reports: {str(e)}")
            raise
    
    async def get_monthly_summary(
        self,
        year: int,
        month: int
    ) -> Dict[str, Any]:
        """Récupérer le résumé mensuel"""
        try:
            # Calculer les dates de début et fin du mois
            start_date = date(year, month, 1)
            if month == 12:
                end_date = date(year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = date(year, month + 1, 1) - timedelta(days=1)
            
            reports = await self.get_reports_range(start_date, end_date)
            
            total_revenue = sum(report.totalRevenue for report in reports)
            total_orders = sum(report.totalOrders for report in reports)
            
            return {
                'year': year,
                'month': month,
                'total_revenue': round(total_revenue, 2),
                'total_orders': total_orders,
                'average_daily_revenue': round(total_revenue / len(reports), 2) if reports else 0.0,
                'average_order_value': round(total_revenue / total_orders, 2) if total_orders > 0 else 0.0,
                'days_with_sales': len(reports)
            }
            
        except Exception as e:
            logger.error(f"Error getting monthly summary: {str(e)}")
            raise