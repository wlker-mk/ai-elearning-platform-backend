from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date


class RevenueReportTestCase(TestCase):
    """Tests pour les rapports de revenus"""
    
    def setUp(self):
        self.client = APIClient()
        # Authentifier en tant qu'admin
        # self.client.force_authenticate(user=self.admin_user)
    
    def test_create_revenue_report(self):
        """Test de création de rapport de revenus"""
        data = {
            'date': str(date.today()),
            'revenue': 1250.50,
            'orders': 25
        }
        
        response = self.client.post('/api/analytics/revenue/report/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('total_revenue', response.data)
        self.assertEqual(response.data['total_revenue'], 1250.50)
    
    def test_update_existing_report(self):
        """Test de mise à jour d'un rapport existant"""
        today = str(date.today())
        
        # Créer le premier rapport
        data1 = {'date': today, 'revenue': 1000.0, 'orders': 20}
        self.client.post('/api/analytics/revenue/report/', data1, format='json')
        
        # Mettre à jour avec plus de revenus
        data2 = {'date': today, 'revenue': 500.0, 'orders': 10}
        response = self.client.post('/api/analytics/revenue/report/', data2, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['total_revenue'], 1500.0)
        self.assertEqual(response.data['total_orders'], 30)