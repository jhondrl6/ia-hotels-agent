"""Tests for Google Places Client error types."""
import pytest
from unittest.mock import Mock, patch
from modules.scrapers.google_places_client import GooglePlacesClient, PlaceData


class TestGooglePlacesErrorTypes:
    """Test error_type field in Places responses."""
    
    @pytest.mark.skip(reason="Requiere Google API key configurada")
    def test_no_api_key_returns_error_place(self):
        """When no API key, should return PlaceData with error_type."""
        client = GooglePlacesClient(api_key=None)
        
        # search_nearby_lodging should return list with error PlaceData
        results = client.search_nearby_lodging(lat=4.0, lng=-74.0)
        
        assert len(results) == 1
        assert results[0].place_found is False
        assert results[0].error_type == "NO_API_KEY"
        assert results[0].error_message is not None
    
    @patch('requests.get')
    def test_quota_exceeded_returns_error_type(self, mock_get):
        """When quota exceeded (429), should return error_type."""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_get.return_value = mock_response
        
        client = GooglePlacesClient(api_key="test_key")
        
        # Access protected method or use public method
        # This is a simplified example
        result = client.get_place_details("place_id_123")
        
        # Should return PlaceData with error
        assert result is not None
        assert result.place_found is False
        assert result.error_type == "QUOTA_EXCEEDED"
    
    @patch('requests.get')
    def test_timeout_returns_error_type(self, mock_get):
        """When timeout, should return error_type."""
        import requests
        mock_get.side_effect = requests.Timeout()
        
        client = GooglePlacesClient(api_key="test_key")
        result = client.get_place_details("place_id_123")
        
        assert result.place_found is False
        assert result.error_type == "TIMEOUT"
