import pytest
from rest_framework.test import APIClient

@pytest.mark.django_db
class TestViews:
    def setup_method(self):
        self.client = APIClient()
    
    def test_list_endpoint(self):
        response = self.client.get('/api/')
        assert response.status_code == 200
