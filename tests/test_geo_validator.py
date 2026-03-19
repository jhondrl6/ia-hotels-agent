#!/usr/bin/env python3
"""
Unit Tests for GeoValidator Module
===================================

Tests the geographic validation functionality for hotel locations.

Author: IA Hoteles Agent
Version: 1.0.0
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import os
import sys
from pathlib import Path

# Add project root to path
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from modules.utils.geo_validator import GeoValidator, ValidationResult, LocationInfo, get_geo_validator, reset_geo_validator


class TestGeoValidator(unittest.TestCase):
    """Test cases for GeoValidator class"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Mock API key for testing
        self.test_api_key = "test_google_maps_api_key_12345"
        self.validator = GeoValidator(api_key=self.test_api_key)
    
    def tearDown(self):
        """Clean up after tests"""
        # Reset singleton instance
        from modules.utils.geo_validator import reset_geo_validator
        reset_geo_validator()
    
    @patch('modules.utils.geo_validator.googlemaps.Client')
    def test_initialization_with_api_key(self, mock_client):
        """Test GeoValidator initialization with API key"""
        validator = GeoValidator(api_key=self.test_api_key)
        mock_client.assert_called_once_with(key=self.test_api_key)
        self.assertTrue(validator.is_available())
    
    @patch.dict(os.environ, {'GOOGLE_MAPS_API_KEY': '', 'GOOGLE_API_KEY': ''}, clear=True)
    def test_initialization_without_api_key(self):
        """Test GeoValidator initialization without API key"""
        validator = GeoValidator(api_key=None)
        self.assertFalse(validator.is_available())
        self.assertIsNone(validator.client)
    
    @patch('modules.utils.geo_validator.os.getenv')
    def test_initialization_from_environment(self, mock_getenv):
        """Test GeoValidator initialization from environment variable"""
        mock_getenv.return_value = self.test_api_key
        validator = GeoValidator()
        self.assertEqual(validator.api_key, self.test_api_key)
    
    def test_get_threshold_for_region(self):
        """Test region-specific threshold selection"""
        # Test coastal cities
        threshold = self.validator._get_threshold_for_region('cartagena', 'Colombia')
        self.assertEqual(threshold, 50.0)
        
        # Test metropolitan cities
        threshold = self.validator._get_threshold_for_region('bogotá', 'Colombia')
        self.assertEqual(threshold, 20.0)
        
        # Test default threshold
        threshold = self.validator._get_threshold_for_region('manizales', 'Colombia')
        self.assertEqual(threshold, 30.0)
    
    @patch('modules.utils.geo_validator.googlemaps.Client')
    def test_geocode_address_success(self, mock_client_class):
        """Test successful address geocoding"""
        # Mock Google Maps client
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Mock geocoding response
        mock_geocode_result = {
            'formatted_address': 'Cra. 10 #80-44, Manizales, Caldas, Colombia',
            'geometry': {
                'location': {'lat': 5.0641, 'lng': -75.5196}
            },
            'address_components': [
                {'long_name': 'Manizales', 'types': ['locality']},
                {'long_name': 'Colombia', 'types': ['country']}
            ],
            'place_id': 'test_place_id'
        }
        mock_client.geocode.return_value = [mock_geocode_result]
        
        # Create validator with mocked client
        validator = GeoValidator(api_key=self.test_api_key)
        
        # Test geocoding
        result = validator._geocode_address('Cra. 10 #80-44, Manizales')
        
        self.assertIsNotNone(result)
        self.assertIsInstance(result, LocationInfo)
        self.assertEqual(result.coordinates, (5.0641, -75.5196))
        self.assertEqual(result.city, 'Manizales')
        self.assertEqual(result.country, 'Colombia')
        self.assertEqual(result.place_id, 'test_place_id')
    
    @patch('modules.utils.geo_validator.googlemaps.Client')
    def test_geocode_address_failure(self, mock_client_class):
        """Test address geocoding failure"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.geocode.return_value = None
        
        validator = GeoValidator(api_key=self.test_api_key)
        result = validator._geocode_address('invalid address')
        
        self.assertIsNone(result)
    
    @patch('modules.utils.geo_validator.googlemaps.Client')
    def test_search_hotel_location_success(self, mock_client_class):
        """Test successful hotel location search"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Mock Places API response
        mock_places_result = {
            'results': [{
                'name': 'Hotel Vísperas',
                'geometry': {
                    'location': {'lat': 5.0641, 'lng': -75.5196}
                },
                'vicinity': 'Manizales, Caldas',
                'place_id': 'hotel_place_id'
            }]
        }
        mock_client.places.return_value = mock_places_result
        
        validator = GeoValidator(api_key=self.test_api_key)
        result = validator._search_hotel_location('Hotel Vísperas', 'Manizales')
        
        self.assertIsNotNone(result)
        self.assertIsInstance(result, LocationInfo)
        self.assertEqual(result.name, 'Hotel Vísperas')
        self.assertEqual(result.coordinates, (5.0641, -75.5196))
    
    @patch('modules.utils.geo_validator.googlemaps.Client')
    def test_search_hotel_location_not_found(self, mock_client_class):
        """Test hotel location search when not found"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.places.return_value = {'results': []}
        
        validator = GeoValidator(api_key=self.test_api_key)
        result = validator._search_hotel_location('Nonexistent Hotel', 'Manizales')
        
        self.assertIsNone(result)
    
    def test_calculate_confidence(self):
        """Test confidence score calculation"""
        # Test exact name match and close distance
        confidence = self.validator._calculate_confidence(
            'Hotel Vísperas', 'Hotel Vísperas', 5.0, 30.0
        )
        self.assertGreater(confidence, 0.8)
        
        # Test partial name match and far distance
        confidence = self.validator._calculate_confidence(
            'Hotel Vísperas', 'Vísperas Hotel', 25.0, 30.0
        )
        self.assertGreater(confidence, 0.5)
        
        # Test no name match and very far distance
        confidence = self.validator._calculate_confidence(
            'Hotel Vísperas', 'Completely Different Hotel', 50.0, 30.0
        )
        self.assertLess(confidence, 0.5)
    
    @patch('modules.utils.geo_validator.googlemaps.Client')
    def test_validate_hotel_location_success(self, mock_client_class):
        """Test complete hotel location validation success"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Mock geocoding response for expected location
        mock_geocode_result = {
            'formatted_address': 'Manizales, Caldas, Colombia',
            'geometry': {'location': {'lat': 5.0641, 'lng': -75.5196}},
            'address_components': [
                {'long_name': 'Manizales', 'types': ['locality']},
                {'long_name': 'Colombia', 'types': ['country']}
            ]
        }
        
        # Mock Places API response for actual hotel
        mock_places_result = {
            'results': [{
                'name': 'Hotel Vísperas',
                'geometry': {'location': {'lat': 5.0650, 'lng': -75.5200}},
                'vicinity': 'Manizales, Caldas'
            }]
        }
        
        mock_client.geocode.return_value = [mock_geocode_result]
        mock_client.places.return_value = mock_places_result
        
        validator = GeoValidator(api_key=self.test_api_key)
        result = validator.validate_hotel_location('Hotel Vísperas', 'Manizales')
        
        self.assertIsInstance(result, ValidationResult)
        self.assertTrue(result.is_valid)
        self.assertLess(result.distance_km, 1.0)  # Should be very close
        self.assertEqual(result.hotel_name, 'Hotel Vísperas')
        self.assertEqual(result.expected_city, 'Manizales')
        self.assertGreater(result.confidence, 0.8)
    
    @patch('modules.utils.geo_validator.googlemaps.Client')
    def test_validate_hotel_location_failure(self, mock_client_class):
        """Test hotel location validation failure (too far)"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Mock geocoding response for expected location (Manizales)
        mock_geocode_result = {
            'formatted_address': 'Manizales, Caldas, Colombia',
            'geometry': {'location': {'lat': 5.0641, 'lng': -75.5196}},
            'address_components': [
                {'long_name': 'Manizales', 'types': ['locality']},
                {'long_name': 'Colombia', 'types': ['country']}
            ]
        }
        
        # Mock Places API response for hotel in different city (Bogotá)
        mock_places_result = {
            'results': [{
                'name': 'Hotel Vísperas',
                'geometry': {'location': {'lat': 4.7110, 'lng': -74.0721}},  # Bogotá coordinates
                'vicinity': 'Bogotá, Cundinamarca'
            }]
        }
        
        mock_client.geocode.return_value = [mock_geocode_result]
        mock_client.places.return_value = mock_places_result
        
        validator = GeoValidator(api_key=self.test_api_key)
        result = validator.validate_hotel_location('Hotel Vísperas', 'Manizales')
        
        self.assertIsInstance(result, ValidationResult)
        self.assertFalse(result.is_valid)  # Should be invalid (too far)
        self.assertGreater(result.distance_km, 100.0)  # Should be very far (Manizales to Bogotá)
        self.assertEqual(result.hotel_name, 'Hotel Vísperas')
        self.assertEqual(result.expected_city, 'Manizales')
    
    @patch.dict(os.environ, {'GOOGLE_MAPS_API_KEY': '', 'GOOGLE_API_KEY': ''}, clear=True)
    def test_validate_hotel_location_no_api_key(self):
        """Test validation when no API key is available"""
        validator = GeoValidator(api_key=None)
        result = validator.validate_hotel_location('Hotel Vísperas', 'Manizales')
        
        self.assertIsInstance(result, ValidationResult)
        self.assertFalse(result.is_valid)
        self.assertIsNotNone(result.error_message)
        self.assertIn('not available', result.error_message)
    
    def test_get_validation_summary_empty(self):
        """Test validation summary with empty results"""
        summary = self.validator.get_validation_summary([])
        
        self.assertEqual(summary['total_validations'], 0)
        self.assertEqual(summary['valid_count'], 0)
        self.assertEqual(summary['invalid_count'], 0)
        self.assertEqual(summary['validity_rate'], 0.0)
    
    def test_get_validation_summary_with_results(self):
        """Test validation summary with results"""
        # Create mock validation results
        results = [
            ValidationResult(
                is_valid=True, distance_km=5.0, threshold_km=30.0,
                expected_location=(5.0641, -75.5196), actual_location=(5.0650, -75.5200),
                hotel_name='Hotel 1', expected_city='Manizales', confidence=0.9, api_calls_used=2
            ),
            ValidationResult(
                is_valid=False, distance_km=50.0, threshold_km=30.0,
                expected_location=(5.0641, -75.5196), actual_location=(4.7110, -74.0721),
                hotel_name='Hotel 2', expected_city='Manizales', confidence=0.3, api_calls_used=2
            )
        ]
        
        summary = self.validator.get_validation_summary(results)
        
        self.assertEqual(summary['total_validations'], 2)
        self.assertEqual(summary['valid_count'], 1)
        self.assertEqual(summary['invalid_count'], 1)
        self.assertEqual(summary['validity_rate'], 0.5)
        self.assertEqual(summary['average_distance_km'], 27.5)
        self.assertEqual(summary['average_confidence'], 0.6)
        self.assertEqual(summary['total_api_calls'], 4)


class TestGeoValidatorSingleton(unittest.TestCase):
    """Test cases for GeoValidator singleton functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Reset singleton instance before each test
        from modules.utils.geo_validator import reset_geo_validator
        reset_geo_validator()
    
    def tearDown(self):
        """Clean up after tests"""
        from modules.utils.geo_validator import reset_geo_validator
        reset_geo_validator()
    
    @patch.dict(os.environ, {'GOOGLE_MAPS_API_KEY': 'test_key_12345'})
    def test_get_geo_validator_singleton(self):
        """Test that get_geo_validator returns singleton instance"""
        validator1 = get_geo_validator()
        validator2 = get_geo_validator()
        
        self.assertIs(validator1, validator2)
    
    @patch.dict(os.environ, {'GOOGLE_MAPS_API_KEY': 'test_key_12345'})
    def test_reset_geo_validator(self):
        """Test that reset_geo_validator creates new instance"""
        validator1 = get_geo_validator()
        reset_geo_validator()
        validator2 = get_geo_validator()
        
        self.assertIsNot(validator1, validator2)


class TestValidationResult(unittest.TestCase):
    """Test cases for ValidationResult dataclass"""
    
    def test_validation_result_creation(self):
        """Test ValidationResult creation and attributes"""
        result = ValidationResult(
            is_valid=True,
            distance_km=10.5,
            threshold_km=30.0,
            expected_location=(5.0641, -75.5196),
            actual_location=(5.0650, -75.5200),
            hotel_name='Test Hotel',
            expected_city='Test City',
            confidence=0.85,
            error_message=None,
            api_calls_used=2
        )
        
        self.assertTrue(result.is_valid)
        self.assertEqual(result.distance_km, 10.5)
        self.assertEqual(result.threshold_km, 30.0)
        self.assertEqual(result.hotel_name, 'Test Hotel')
        self.assertEqual(result.expected_city, 'Test City')
        self.assertEqual(result.confidence, 0.85)
        self.assertIsNone(result.error_message)
        self.assertEqual(result.api_calls_used, 2)


class TestLocationInfo(unittest.TestCase):
    """Test cases for LocationInfo dataclass"""
    
    def test_location_info_creation(self):
        """Test LocationInfo creation and attributes"""
        location = LocationInfo(
            name='Test Hotel',
            address='Test Address, Test City',
            coordinates=(5.0641, -75.5196),
            city='Test City',
            country='Test Country',
            place_id='test_place_id'
        )
        
        self.assertEqual(location.name, 'Test Hotel')
        self.assertEqual(location.address, 'Test Address, Test City')
        self.assertEqual(location.coordinates, (5.0641, -75.5196))
        self.assertEqual(location.city, 'Test City')
        self.assertEqual(location.country, 'Test Country')
        self.assertEqual(location.place_id, 'test_place_id')


if __name__ == '__main__':
    # Configure test environment
    os.environ['PYTHONPATH'] = str(PROJECT_ROOT)
    
    # Run tests
    unittest.main(verbosity=2)
