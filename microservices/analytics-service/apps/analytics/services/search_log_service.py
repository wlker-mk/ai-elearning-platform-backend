from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from prisma import Prisma
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class SearchLogService:
    """Service pour gérer les logs de recherche"""
    
    def __init__(self):
        self.db = Prisma()
    
    async def connect(self):
        if not self.db.is_connected():
            await self.db.connect()
    
    async def disconnect(self):
        if self.db.is_connected():
            await self.db.disconnect()
    
    async def log_search(
        self,
        query: str,
        results_count: int,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        clicked_result: Optional[str] = None
    ):
        """Enregistrer une recherche"""
        try:
            await self.connect()
            
            log = await self.db.searchlog.create(
                data={
                    'query': query.lower().strip(),
                    'userId': user_id,
                    'ipAddress': ip_address,
                    'resultsCount': results_count,
                    'clickedResult': clicked_result,
                    'searchedAt': datetime.now()
                }
            )
            
            logger.info(f"Search logged: {query}")
            return log
            
        except Exception as e:
            logger.error(f"Error logging search: {str(e)}")
            raise
        finally:
            await self.disconnect()
    
    async def update_clicked_result(
        self,
        search_id: str,
        clicked_result: str
    ):
        """Mettre à jour le résultat cliqué"""
        try:
            await self.connect()
            
            log = await self.db.searchlog.update(
                where={'id': search_id},
                data={'clickedResult': clicked_result}
            )
            
            return log
            
        except Exception as e:
            logger.error(f"Error updating clicked result: {str(e)}")
            raise
        finally:
            await self.disconnect()
    
    async def get_popular_searches(
        self,
        limit: int = 10,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Récupérer les recherches les plus populaires"""
        try:
            await self.connect()
            
            start_date = datetime.now() - timedelta(days=days)
            
            logs = await self.db.searchlog.find_many(
                where={'searchedAt': {'gte': start_date}}
            )
            
            # Grouper par query
            query_counts = defaultdict(int)
            for log in logs:
                query_counts[log.query] += 1
            
            # Trier et limiter
            sorted_queries = sorted(
                query_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:limit]
            
            return [
                {'query': query, 'count': count}
                for query, count in sorted_queries
            ]
            
        except Exception as e:
            logger.error(f"Error getting popular searches: {str(e)}")
            raise
        finally:
            await self.disconnect()
    
    async def get_zero_result_searches(
        self,
        limit: int = 10,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Récupérer les recherches sans résultats"""
        try:
            await self.connect()
            
            start_date = datetime.now() - timedelta(days=days)
            
            logs = await self.db.searchlog.find_many(
                where={
                    'resultsCount': 0,
                    'searchedAt': {'gte': start_date}
                }
            )
            
            # Grouper par query
            query_counts = defaultdict(int)
            for log in logs:
                query_counts[log.query] += 1
            
            # Trier et limiter
            sorted_queries = sorted(
                query_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:limit]
            
            return [
                {'query': query, 'count': count}
                for query, count in sorted_queries
            ]
            
        except Exception as e:
            logger.error(f"Error getting zero result searches: {str(e)}")
            raise
        finally:
            await self.disconnect()
    
    async def get_user_search_history(
        self,
        user_id: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Récupérer l'historique de recherche d'un utilisateur"""
        try:
            await self.connect()
            
            logs = await self.db.searchlog.find_many(
                where={'userId': user_id},
                order={'searchedAt': 'desc'},
                take=limit
            )
            
            return logs
            
        except Exception as e:
            logger.error(f"Error getting user search history: {str(e)}")
            raise
        finally:
            await self.disconnect()
    
    async def get_search_trends(
        self,
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """Récupérer les tendances de recherche"""
        try:
            await self.connect()
            
            start_date = datetime.now() - timedelta(days=days)
            
            logs = await self.db.searchlog.find_many(
                where={'searchedAt': {'gte': start_date}},
                order={'searchedAt': 'asc'}
            )
            
            # Grouper par jour et query
            daily_queries = defaultdict(lambda: defaultdict(int))
            for log in logs:
                date_key = log.searchedAt.strftime('%Y-%m-%d')
                daily_queries[date_key][log.query] += 1
            
            # Formater les résultats
            result = []
            for i in range(days):
                date = start_date + timedelta(days=i)
                date_key = date.strftime('%Y-%m-%d')
                
                queries = daily_queries.get(date_key, {})
                top_queries = sorted(
                    queries.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:5]
                
                result.append({
                    'date': date_key,
                    'total_searches': sum(queries.values()),
                    'top_queries': [
                        {'query': q, 'count': c}
                        for q, c in top_queries
                    ]
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting search trends: {str(e)}")
            raise
        finally:
            await self.disconnect()
    
    async def get_click_through_rate(
        self,
        query: Optional[str] = None,
        days: int = 30
    ) -> float:
        """Calculer le taux de clic (CTR)"""
        try:
            await self.connect()
            
            start_date = datetime.now() - timedelta(days=days)
            
            where_clause = {'searchedAt': {'gte': start_date}}
            if query:
                where_clause['query'] = query.lower().strip()
            
            total_searches = await self.db.searchlog.count(where=where_clause)
            
            if total_searches == 0:
                return 0.0
            
            where_clause['clickedResult'] = {'not': None}
            searches_with_clicks = await self.db.searchlog.count(where=where_clause)
            
            ctr = (searches_with_clicks / total_searches) * 100
            return round(ctr, 2)
            
        except Exception as e:
            logger.error(f"Error calculating CTR: {str(e)}")
            raise
        finally:
            await self.disconnect()