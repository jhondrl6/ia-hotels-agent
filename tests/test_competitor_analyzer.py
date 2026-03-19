"""Tests for updated CompetitorAnalyzer with Places Client."""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

from modules.analyzers.competitor_analyzer import CompetitorAnalyzer


class TestCompetitorAnalyzerWithPlacesClient:
    """Tests for CompetitorAnalyzer using GooglePlacesClient."""
    
    def test_uses_places_client_when_available(self):
        """Test that analyzer uses Places Client when available."""
        with patch('modules.analyzers.competitor_analyzer.get_places_client') as mock:
            mock_client = MagicMock()
            mock_client.is_available = True
            mock_client.search_nearby_lodging.return_value = []
            mock.return_value = mock_client
            
            analyzer = CompetitorAnalyzer()
            result = analyzer.get_nearby_competitors("Hotel Test", 4.6, -74.1)
            
            mock_client.search_nearby_lodging.assert_called_once()
    
    def test_fallback_to_legacy_when_places_unavailable(self):
        """Test fallback to legacy implementation when Places Client unavailable."""
        with patch('modules.analyzers.competitor_analyzer.get_places_client') as mock:
            mock_client = MagicMock()
            mock_client.is_available = False
            mock.return_value = mock_client
            
            analyzer = CompetitorAnalyzer()
            result = analyzer.get_nearby_competitors("Hotel Test", 4.6, -74.1)
            
            assert result == []
    
    def test_geo_score_is_real_not_estimated(self):
        """Test that geo_score comes from Places Client (real calculation)."""
        from modules.scrapers.google_places_client import PlaceData
        
        mock_place = PlaceData(
            place_id="test123",
            name="Competitor Hotel",
            rating=4.5,
            reviews=150,
            photos=25,
            has_hours=True,
            has_website=True,
            website_url="https://example.com",
            phone="+5712345678",
            address="Test Address",
            city="Test City",
            lat=4.61,
            lng=-74.08,
            geo_score=82,
            geo_score_formula={
                'rating_score': 27.0,
                'reviews_score': 3.0,
                'photos_score': 12.5,
                'hours_score': 10.0,
                'website_score': 10.0,
                'total': 82
            },
            data_source='places_api',
            fetched_at=datetime.now().isoformat()
        )
        
        with patch('modules.analyzers.competitor_analyzer.get_places_client') as mock:
            mock_client = MagicMock()
            mock_client.is_available = True
            mock_client.search_nearby_lodging.return_value = [mock_place]
            mock.return_value = mock_client
            
            analyzer = CompetitorAnalyzer()
            result = analyzer.get_nearby_competitors("Other Hotel", 4.6, -74.1)
            
            assert len(result) == 1
            assert result[0]['geo_score'] == 82
            assert result[0]['score_source'] == 'places_api_real'
            assert 'geo_score_formula' in result[0]

    def test_excludes_client_hotel_from_results(self):
        """Test that client hotel is excluded from competitor results."""
        from modules.scrapers.google_places_client import PlaceData
        
        mock_places = [
            PlaceData(
                place_id="test1",
                name="Hotel Test Cliente",
                rating=4.5,
                reviews=100,
                photos=20,
                has_hours=True,
                has_website=True,
                website_url=None,
                phone=None,
                address="Address 1",
                city="City",
                lat=4.61,
                lng=-74.08,
                geo_score=75,
                geo_score_formula={},
                data_source='places_api',
                fetched_at=datetime.now().isoformat()
            ),
            PlaceData(
                place_id="test2",
                name="Competidor Real",
                rating=4.0,
                reviews=80,
                photos=15,
                has_hours=True,
                has_website=False,
                website_url=None,
                phone=None,
                address="Address 2",
                city="City",
                lat=4.62,
                lng=-74.09,
                geo_score=65,
                geo_score_formula={},
                data_source='places_api',
                fetched_at=datetime.now().isoformat()
            )
        ]
        
        with patch('modules.analyzers.competitor_analyzer.get_places_client') as mock:
            mock_client = MagicMock()
            mock_client.is_available = True
            mock_client.search_nearby_lodging.return_value = mock_places
            mock.return_value = mock_client
            
            analyzer = CompetitorAnalyzer()
            result = analyzer.get_nearby_competitors("Hotel Test Cliente", 4.6, -74.1)
            
            assert len(result) == 1
            assert result[0]['nombre'] == "Competidor Real"

    def test_use_places_client_flag_disabled(self):
        """Test that use_places_client=False disables Places Client."""
        with patch('modules.analyzers.competitor_analyzer.get_places_client') as mock:
            mock.return_value = None
            
            analyzer = CompetitorAnalyzer(use_places_client=False)
            
            assert analyzer._places_client is None
            assert analyzer.use_places_client is False

    def test_returns_max_five_competitors(self):
        """Test that only top 5 competitors are returned."""
        from modules.scrapers.google_places_client import PlaceData
        
        mock_places = [
            PlaceData(
                place_id=f"test{i}",
                name=f"Hotel Competidor {i}",
                rating=4.0 + i * 0.1,
                reviews=100 + i * 10,
                photos=20 + i,
                has_hours=True,
                has_website=True,
                website_url=None,
                phone=None,
                address=f"Address {i}",
                city="City",
                lat=4.61 + i * 0.01,
                lng=-74.08 + i * 0.01,
                geo_score=60 + i * 5,
                geo_score_formula={},
                data_source='places_api',
                fetched_at=datetime.now().isoformat()
            )
            for i in range(10)
        ]
        
        with patch('modules.analyzers.competitor_analyzer.get_places_client') as mock:
            mock_client = MagicMock()
            mock_client.is_available = True
            mock_client.search_nearby_lodging.return_value = mock_places
            mock.return_value = mock_client
            
            analyzer = CompetitorAnalyzer()
            result = analyzer.get_nearby_competitors("Other Hotel", 4.6, -74.1)
            
            assert len(result) == 5


class TestIsSameHotel:
    """Tests for hotel name comparison."""
    
    def test_same_hotel_exact_match(self):
        """Test exact name match."""
        analyzer = CompetitorAnalyzer()
        assert analyzer._is_same_hotel("Hotel Luna", "Hotel Luna") is True
    
    def test_same_hotel_with_accent_variations(self):
        """Test name match with accent variations."""
        analyzer = CompetitorAnalyzer()
        assert analyzer._is_same_hotel("Hotel Termales", "Hotel Térmales") is True
    
    def test_same_hotel_with_extra_words(self):
        """Test name match with extra words."""
        analyzer = CompetitorAnalyzer()
        assert analyzer._is_same_hotel("Hotel Luna", "Hotel Luna Boutique") is True
    
    def test_different_hotels(self):
        """Test different hotel names."""
        analyzer = CompetitorAnalyzer()
        assert analyzer._is_same_hotel("Hotel Luna", "Hotel Sol") is False
    
    def test_substring_match(self):
        """Test substring match."""
        analyzer = CompetitorAnalyzer()
        assert analyzer._is_same_hotel("Termales", "Hotel Termales del Valle") is True
    
    def test_empty_names(self):
        """Test empty name handling."""
        analyzer = CompetitorAnalyzer()
        assert analyzer._is_same_hotel("", "Hotel Luna") is False
        assert analyzer._is_same_hotel("Hotel Luna", None) is False
