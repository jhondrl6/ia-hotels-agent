"""Tests for Google Places Client."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from pathlib import Path
import json

from modules.scrapers.google_places_client import (
    GooglePlacesClient,
    PlaceData,
    GeoScoreBreakdown,
    get_places_client,
    reset_places_client
)


class TestGeoScoreCalculation:
    """Tests for geo_score calculation."""
    
    def test_perfect_score(self):
        """Test perfect geo_score calculation."""
        client = GooglePlacesClient(api_key="test")
        
        result = client.calculate_geo_score(
            rating=5.0,
            reviews=1000,
            photos=40,
            has_hours=True,
            has_website=True
        )
        
        assert result.rating_score == 30.0
        assert result.reviews_score == 20.0
        assert result.photos_score == 20.0
        assert result.hours_score == 10.0
        assert result.website_score == 10.0
        assert result.total >= 90
    
    def test_low_score(self):
        """Test low geo_score calculation."""
        client = GooglePlacesClient(api_key="test")
        
        result = client.calculate_geo_score(
            rating=3.0,
            reviews=10,
            photos=5,
            has_hours=False,
            has_website=False
        )
        
        assert result.rating_score == 18.0
        assert result.reviews_score == 0.2
        assert result.photos_score == 2.5
        assert result.hours_score == 0.0
        assert result.website_score == 0.0
        assert result.total < 50
    
    def test_reviews_cap(self):
        """Test that reviews score is capped at 20."""
        client = GooglePlacesClient(api_key="test")
        
        result = client.calculate_geo_score(
            rating=5.0,
            reviews=10000,
            photos=0,
            has_hours=False,
            has_website=False
        )
        
        assert result.reviews_score == 20.0
    
    def test_photos_cap(self):
        """Test that photos score is capped at 20."""
        client = GooglePlacesClient(api_key="test")
        
        result = client.calculate_geo_score(
            rating=5.0,
            reviews=0,
            photos=100,
            has_hours=False,
            has_website=False
        )
        
        assert result.photos_score == 20.0
    
    def test_zero_rating(self):
        """Test geo_score with zero rating."""
        client = GooglePlacesClient(api_key="test")
        
        result = client.calculate_geo_score(
            rating=0.0,
            reviews=50,
            photos=10,
            has_hours=True,
            has_website=True
        )
        
        assert result.rating_score == 0.0
        assert result.reviews_score == 1.0
        assert result.photos_score == 5.0
        assert result.total < 35
    
    def test_total_never_exceeds_100(self):
        """Test that total score never exceeds 100."""
        client = GooglePlacesClient(api_key="test")
        
        result = client.calculate_geo_score(
            rating=5.0,
            reviews=5000,
            photos=200,
            has_hours=True,
            has_website=True
        )
        
        assert result.total <= 100


class TestCacheSystem:
    """Tests for cache functionality."""
    
    def test_cache_ttl_valid(self, tmp_path):
        """Test that valid cache entries are returned."""
        cache_file = tmp_path / "cache.json"
        client = GooglePlacesClient(
            api_key="test",
            cache_path=str(cache_file)
        )
        
        place = PlaceData(
            place_id="test123",
            name="Test Hotel",
            rating=4.5,
            reviews=100,
            photos=20,
            has_hours=True,
            has_website=True,
            website_url="https://example.com",
            phone="+5712345678",
            address="Test Address",
            city="Test City",
            lat=0.0,
            lng=0.0,
            geo_score=85,
            geo_score_formula={},
            data_source="places_api",
            fetched_at=datetime.now().isoformat()
        )
        
        client._cache_place(place)
        
        cached = client._get_cached_place("test123")
        
        assert cached is not None
        assert cached.name == "Test Hotel"
    
    def test_cache_ttl_expired(self, tmp_path):
        """Test that expired cache entries are not returned."""
        cache_file = tmp_path / "cache.json"
        client = GooglePlacesClient(
            api_key="test",
            cache_ttl_days=1,
            cache_path=str(cache_file)
        )
        
        place = PlaceData(
            place_id="test123",
            name="Test Hotel",
            rating=4.5,
            reviews=100,
            photos=20,
            has_hours=True,
            has_website=True,
            website_url="https://example.com",
            phone="+5712345678",
            address="Test Address",
            city="Test City",
            lat=0.0,
            lng=0.0,
            geo_score=85,
            geo_score_formula={},
            data_source="places_api",
            fetched_at=(datetime.now() - timedelta(days=2)).isoformat()
        )
        
        client._cache_place(place)
        
        cached = client._get_cached_place("test123")
        
        assert cached is None
    
    def test_cache_persists_to_disk(self, tmp_path):
        """Test that cache is persisted to disk."""
        cache_file = tmp_path / "cache.json"
        
        client1 = GooglePlacesClient(
            api_key="test",
            cache_path=str(cache_file)
        )
        
        place = PlaceData(
            place_id="persist_test",
            name="Persistent Hotel",
            rating=4.0,
            reviews=50,
            photos=10,
            has_hours=True,
            has_website=False,
            website_url=None,
            phone=None,
            address="Address",
            city="City",
            lat=1.0,
            lng=1.0,
            geo_score=60,
            geo_score_formula={},
            data_source="places_api",
            fetched_at=datetime.now().isoformat()
        )
        
        client1._cache_place(place)
        
        client2 = GooglePlacesClient(
            api_key="test",
            cache_path=str(cache_file)
        )
        
        cached = client2._get_cached_place("persist_test")
        
        assert cached is not None
        assert cached.name == "Persistent Hotel"
    
    def test_clear_cache(self, tmp_path):
        """Test that clear_cache removes all entries."""
        cache_file = tmp_path / "cache.json"
        client = GooglePlacesClient(
            api_key="test",
            cache_path=str(cache_file)
        )
        
        place = PlaceData(
            place_id="to_clear",
            name="Hotel to Clear",
            rating=4.0,
            reviews=50,
            photos=10,
            has_hours=True,
            has_website=False,
            website_url=None,
            phone=None,
            address="Address",
            city="City",
            lat=1.0,
            lng=1.0,
            geo_score=60,
            geo_score_formula={},
            data_source="places_api",
            fetched_at=datetime.now().isoformat()
        )
        
        client._cache_place(place)
        client.clear_cache()
        
        assert client._get_cached_place("to_clear") is None
        assert len(client._cache) == 0


class TestPlaceDataParsing:
    """Tests for Places API response parsing."""
    
    def test_parse_valid_response(self):
        """Test parsing a valid Places API response."""
        client = GooglePlacesClient(api_key="test")
        
        api_response = {
            'id': 'ChIJ12345',
            'displayName': {'text': 'Hotel Test', 'languageCode': 'es'},
            'rating': 4.5,
            'userRatingCount': 150,
            'photos': [{'name': 'photo1'}, {'name': 'photo2'}],
            'regularOpeningHours': {'periods': []},
            'websiteUri': 'https://hoteltest.com',
            'nationalPhoneNumber': '+57 123 456 7890',
            'formattedAddress': 'Calle 123, Bogotá, Colombia',
            'location': {'latitude': 4.6097, 'longitude': -74.0817},
            'addressComponents': [
                {'longText': 'Bogotá', 'types': ['locality']},
                {'longText': 'Colombia', 'types': ['country']}
            ]
        }
        
        result = client._parse_place_response(api_response)
        
        assert result is not None
        assert result.name == 'Hotel Test'
        assert result.place_id == 'ChIJ12345'
        assert result.rating == 4.5
        assert result.reviews == 150
        assert result.photos == 2
        assert result.has_hours is True
        assert result.has_website is True
        assert result.website_url == 'https://hoteltest.com'
        assert result.phone == '+57 123 456 7890'
        assert result.city == 'Bogotá'
        assert result.lat == 4.6097
        assert result.lng == -74.0817
    
    def test_parse_minimal_response(self):
        """Test parsing a minimal Places API response."""
        client = GooglePlacesClient(api_key="test")
        
        api_response = {
            'id': 'minimal123',
            'displayName': {'text': 'Minimal Hotel'}
        }
        
        result = client._parse_place_response(api_response)
        
        assert result is not None
        assert result.name == 'Minimal Hotel'
        assert result.rating == 0.0
        assert result.reviews == 0
        assert result.photos == 0
        assert result.has_hours is False
        assert result.has_website is False
    
    def test_parse_empty_name_returns_none(self):
        """Test that empty name returns None."""
        client = GooglePlacesClient(api_key="test")
        
        api_response = {
            'id': 'no_name',
            'displayName': {}
        }
        
        result = client._parse_place_response(api_response)
        
        assert result is None


class TestAvailability:
    """Tests for API availability."""
    
    def test_available_with_api_key(self):
        """Test client is available when API key is provided."""
        client = GooglePlacesClient(api_key="test_key")
        assert client.is_available is True
    
    def test_unavailable_without_api_key(self, monkeypatch):
        """Test client is unavailable when no API key."""
        monkeypatch.delenv('GOOGLE_MAPS_API_KEY', raising=False)
        client = GooglePlacesClient()
        assert client.is_available is False


class TestStatistics:
    """Tests for client statistics."""
    
    def test_initial_stats(self):
        """Test initial statistics are zero."""
        client = GooglePlacesClient(api_key="test")
        
        stats = client.get_stats()
        
        assert stats['api_available'] is True
        assert stats['total_requests'] == 0
        assert stats['cache_hits'] == 0
        assert stats['estimated_cost_usd'] == 0.0
    
    def test_cache_hits_increment(self, tmp_path):
        """Test that cache hits are tracked."""
        cache_file = tmp_path / "cache.json"
        client = GooglePlacesClient(
            api_key="test",
            cache_path=str(cache_file)
        )
        
        place = PlaceData(
            place_id="hit_test",
            name="Hit Test Hotel",
            rating=4.0,
            reviews=50,
            photos=10,
            has_hours=True,
            has_website=False,
            website_url=None,
            phone=None,
            address="Address",
            city="City",
            lat=1.0,
            lng=1.0,
            geo_score=60,
            geo_score_formula={},
            data_source="places_api",
            fetched_at=datetime.now().isoformat()
        )
        
        client._cache_place(place)
        client._get_cached_place("hit_test")
        client._get_cached_place("hit_test")
        
        stats = client.get_stats()
        
        assert stats['cache_hits'] == 2


class TestSingleton:
    """Tests for singleton pattern."""
    
    def test_singleton_returns_same_instance(self):
        """Test that get_places_client returns same instance."""
        reset_places_client()
        
        client1 = get_places_client()
        client2 = get_places_client()
        
        assert client1 is client2
    
    def test_reset_creates_new_instance(self):
        """Test that reset_places_client allows new instance."""
        reset_places_client()
        client1 = get_places_client()
        
        reset_places_client()
        client2 = get_places_client()
        
        assert client1 is not client2


class TestRateLimiting:
    """Tests for rate limiting functionality."""
    
    def test_rate_limiting_applies_delay(self):
        """Test that rate limiting adds delay between requests."""
        client = GooglePlacesClient(api_key="test")
        client.MIN_REQUEST_INTERVAL = 0.05
        
        import time
        start = time.time()
        client._rate_limit()
        client._rate_limit()
        elapsed = time.time() - start
        
        assert elapsed >= 0.05


class TestSearchNearbyLodging:
    """Tests for nearby lodging search."""
    
    @patch('modules.scrapers.google_places_client.requests.post')
    def test_search_returns_places(self, mock_post):
        """Test that search returns parsed places."""
        client = GooglePlacesClient(api_key="test_key")
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'places': [
                {
                    'id': 'place1',
                    'displayName': {'text': 'Hotel One'},
                    'rating': 4.5,
                    'userRatingCount': 100,
                    'photos': [],
                    'location': {'latitude': 4.0, 'longitude': -74.0},
                    'addressComponents': []
                }
            ]
        }
        mock_post.return_value = mock_response
        
        results = client.search_nearby_lodging(lat=4.0, lng=-74.0)
        
        assert len(results) == 1
        assert results[0].name == 'Hotel One'
    
    def test_search_without_api_key_returns_empty(self, monkeypatch):
        """Test that search without API key returns empty list."""
        monkeypatch.delenv('GOOGLE_MAPS_API_KEY', raising=False)
        monkeypatch.delenv('GOOGLE_API_KEY', raising=False)
        
        client = GooglePlacesClient(api_key=None)
        
        assert client.is_available is False
        
        results = client.search_nearby_lodging(lat=4.0, lng=-74.0)
        # Now returns PlaceData with error info instead of empty list
        assert len(results) == 1
        assert results[0].place_found is False
        assert results[0].error_type == "NO_API_KEY"


class TestGetPlaceDetails:
    """Tests for place details retrieval."""
    
    @patch('modules.scrapers.google_places_client.requests.get')
    def test_get_details_returns_place(self, mock_get):
        """Test that get_place_details returns parsed place."""
        client = GooglePlacesClient(api_key="test_key")
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': 'detail123',
            'displayName': {'text': 'Detail Hotel'},
            'rating': 4.0,
            'userRatingCount': 50,
            'photos': [],
            'location': {'latitude': 1.0, 'longitude': 1.0},
            'addressComponents': []
        }
        mock_get.return_value = mock_response
        
        result = client.get_place_details("detail123")
        
        assert result is not None
        assert result.name == 'Detail Hotel'
        assert result.data_source == 'places_api'
    
    def test_get_details_returns_cached(self, tmp_path):
        """Test that get_place_details returns cached data."""
        cache_file = tmp_path / "cache.json"
        client = GooglePlacesClient(
            api_key="test_key",
            cache_path=str(cache_file)
        )
        
        place = PlaceData(
            place_id="cached_place",
            name="Cached Hotel",
            rating=4.0,
            reviews=50,
            photos=10,
            has_hours=True,
            has_website=False,
            website_url=None,
            phone=None,
            address="Address",
            city="City",
            lat=1.0,
            lng=1.0,
            geo_score=60,
            geo_score_formula={},
            data_source="cache",
            fetched_at=datetime.now().isoformat()
        )
        
        client._cache_place(place)
        
        result = client.get_place_details("cached_place")
        
        assert result is not None
        assert result.name == "Cached Hotel"
