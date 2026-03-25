"""
Tests para SerpAPIClient - FASE 11 Extension

Pruebas de integracion con SerpAPI para obtener datos de hoteles
cuando Google Travel scraping esta bloqueado.
"""

import pytest
from unittest.mock import Mock, patch
from modules.scrapers.serpapi_client import SerpAPIClient, SerpHotelData


class TestSerpAPIClientExists:
    """Tests de existencia del cliente SerpAPI."""
    
    def test_serpapi_client_importable(self):
        """SerpAPIClient debe ser importable."""
        from modules.scrapers.serpapi_client import SerpAPIClient
        assert SerpAPIClient is not None
    
    def test_serpapi_client_has_search_method(self):
        """SerpAPIClient debe tener metodo search_hotel."""
        client = SerpAPIClient(api_key="test_key")
        assert hasattr(client, 'search_hotel')
        assert callable(client.search_hotel)
    
    def test_serpapi_client_has_get_usage_stats(self):
        """SerpAPIClient debe tener metodo get_usage_stats."""
        client = SerpAPIClient(api_key="test_key")
        assert hasattr(client, 'get_usage_stats')
        assert callable(client.get_usage_stats)


class TestSerpAPIClientAvailability:
    """Tests de disponibilidad de la API."""
    
    def test_client_available_with_api_key(self):
        """Cliente debe estar disponible cuando tiene API key."""
        client = SerpAPIClient(api_key="test_key_123")
        assert client.is_available is True
    
    def test_client_not_available_without_api_key(self):
        """Cliente no debe estar disponible sin API key."""
        with patch('modules.scrapers.serpapi_client.os.environ.get', return_value=None):
            client = SerpAPIClient()
            assert client.is_available is False
    
    def test_queries_remaining_initial(self):
        """Debe retornar 250 consultas restantes inicialmente."""
        client = SerpAPIClient(api_key="test_key")
        assert client.queries_remaining == 250


class TestSerpAPIClientSearch:
    """Tests del metodo search_hotel."""
    
    def test_search_returns_found_false_when_no_api_key(self):
        """Debe retornar found=False cuando no hay API key."""
        with patch('modules.scrapers.serpapi_client.os.environ.get', return_value=None):
            client = SerpAPIClient()
            result = client.search_hotel("Test Hotel", "Test Location")
            
            assert result['found'] is False
            assert result['error_type'] == 'API_NOT_CONFIGURED'
    
    @patch('modules.scrapers.serpapi_client.requests.Session')
    def test_search_returns_found_false_when_quota_exhausted(self, mock_session):
        """Debe retornar found=False cuando la cuota esta agotada."""
        client = SerpAPIClient(api_key="test_key")
        client._queries_used = 250  # Cuota agotada
        
        result = client.search_hotel("Test Hotel", "Test Location")
        
        assert result['found'] is False
        assert result['error_type'] == 'QUOTA_EXHAUSTED'
    
    @patch('modules.scrapers.serpapi_client.requests.Session')
    def test_search_returns_found_false_on_timeout(self, mock_session_class):
        """Debe retornar found=False en timeout."""
        import requests
        
        mock_session = Mock()
        mock_session.get.side_effect = requests.exceptions.Timeout()
        mock_session_class.return_value = mock_session
        
        client = SerpAPIClient(api_key="test_key")
        result = client.search_hotel("Test Hotel", "Test Location")
        
        assert result['found'] is False
        assert result['error_type'] == 'TIMEOUT'


class TestSerpHotelData:
    """Tests de la estructura SerpHotelData."""
    
    def test_serp_hotel_data_to_dict(self):
        """SerpHotelData debe convertir a dict correctamente."""
        data = SerpHotelData(
            name="Test Hotel",
            address="Test Address",
            rating=4.5,
            reviews=100,
            phone="+1234567890",
            website="https://test.com",
            place_id="test_place_id",
            found=True,
            search_query="Test Hotel",
            serpapi_qty_used=1
        )
        
        result = data.to_dict()
        
        assert result['name'] == "Test Hotel"
        assert result['address'] == "Test Address"
        assert result['rating'] == 4.5
        assert result['reviews'] == 100
        assert result['phone'] == "+1234567890"
        assert result['website'] == "https://test.com"
        assert result['place_id'] == "test_place_id"
        assert result['found'] is True
        assert result['source'] == 'serpapi'
        assert result['serpapi_qty_used'] == 1


class TestSerpAPIIntegration:
    """Tests de integracion con SerpAPI real (requiere API key)."""
    
    @pytest.mark.integration
    def test_serpapi_finds_hotelvisperas(self):
        """SerpAPI debe encontrar Hotel Visperas con datos correctos."""
        import os
        from dotenv import load_dotenv
        
        load_dotenv(r'C:\Users\Jhond\Github\iah-cli\.env')
        
        api_key = os.environ.get('SERPAPI_API_KEY')
        if not api_key:
            pytest.skip("SERPAPI_API_KEY not configured")
        
        client = SerpAPIClient(api_key=api_key)
        result = client.search_hotel("Hotel Visperas", "Santa Rosa de Cabal, Colombia")
        
        assert result['found'] is True
        assert 'VISPERAS' in result['name'].upper()
        assert result['rating'] > 0
        assert result['reviews'] > 0
        assert 'Santa Rosa' in result['address']
    
    @pytest.mark.integration
    def test_serpapi_usage_tracking(self):
        """SerpAPI debe trackear uso de consultas."""
        import os
        from dotenv import load_dotenv
        
        load_dotenv(r'C:\Users\Jhond\Github\iah-cli\.env')
        
        api_key = os.environ.get('SERPAPI_API_KEY')
        if not api_key:
            pytest.skip("SERPAPI_API_KEY not configured")
        
        client = SerpAPIClient(api_key=api_key)
        initial_usage = client.get_usage_stats()['queries_used']
        
        # Make a search
        client.search_hotel("Test Hotel", "Test Location")
        
        stats = client.get_usage_stats()
        assert stats['queries_used'] == initial_usage + 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
