"""
Geographic Validation Module for GBP Auditor
============================================

This module provides geographic validation functionality for Google Business Profile
auditing, ensuring that hotels are located within acceptable distance thresholds
from their expected locations.

Author: IA Hoteles Agent
Version: 1.0.0
"""

import os
import logging
import math
import requests
from typing import Dict, Optional, Tuple, Any
from dataclasses import dataclass
from functools import lru_cache

try:  # Dependencias opcionales
    import googlemaps  # type: ignore
except ImportError:  # pragma: no cover - entornos sin cliente oficial
    googlemaps = None

try:
    from geopy.distance import geodesic  # type: ignore
except ImportError:  # pragma: no cover - fallback a Haversine
    geodesic = None

try:
    from geopy.exc import GeocoderUnavailable, GeocoderTimedOut  # type: ignore
except ImportError:  # pragma: no cover - definir excepciones básicas
    class GeocoderUnavailable(Exception):
        """Fallback exception when geopy is not installed."""

    class GeocoderTimedOut(Exception):
        """Fallback exception when geopy is not installed."""

# Configure logging
logger = logging.getLogger(__name__)


def _haversine_distance_km(coord_a: Tuple[float, float], coord_b: Tuple[float, float]) -> float:
    """Calcula distancia Haversine en kilómetros entre dos coordenadas."""
    lat1, lon1 = coord_a
    lat2, lon2 = coord_b

    # Convertir a radianes
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    earth_radius_km = 6371.0
    return earth_radius_km * c


def _distance_km(coord_a: Tuple[float, float], coord_b: Tuple[float, float]) -> float:
    """Calcula distancia entre coordenadas usando geopy si está disponible."""
    if geodesic is not None:
        return geodesic(coord_a, coord_b).kilometers
    return _haversine_distance_km(coord_a, coord_b)

@dataclass
class ValidationResult:
    """Result of geographic validation"""
    is_valid: bool
    distance_km: float
    threshold_km: float
    expected_location: Tuple[float, float]
    actual_location: Tuple[float, float]
    hotel_name: str
    expected_city: str
    confidence: float
    error_message: Optional[str] = None
    api_calls_used: int = 0
    expected_address: Optional[str] = None
    actual_address: Optional[str] = None
    actual_city: Optional[str] = None
    actual_state: Optional[str] = None
    actual_country: Optional[str] = None
    actual_place_id: Optional[str] = None
    resolved_location: Optional[str] = None
    photo_count: Optional[int] = None

@dataclass
class LocationInfo:
    """Location information for a hotel"""
    name: str
    address: str
    coordinates: Tuple[float, float]
    city: str
    country: str
    state: str = ""
    place_id: Optional[str] = None

class GeoValidator:
    """
    Geographic validator for hotel locations using Google Maps API.
    
    This class validates that hotels found in Google Maps are within
    acceptable distance thresholds from their expected locations.
    """
    
    # Default distance thresholds by region (in kilometers)
    DEFAULT_THRESHOLDS = {
        'default': 30.0,
        'coastal': 50.0,  # Higher threshold for coastal tourist areas
        'metropolitan': 20.0,  # Lower threshold for dense urban areas
        'rural': 40.0  # Higher threshold for rural areas
    }
    
    # API call limits for cost control
    MAX_DAILY_CALLS = 1000
    MAX_CALLS_PER_VALIDATION = 3
    
    def __init__(self, api_key: Optional[str] = None, cache_enabled: bool = True):
        """
        Initialize GeoValidator with Google Maps API key.
        
        Args:
            api_key: Google Maps API key. If None, will try to get from environment.
            cache_enabled: Whether to enable caching of geocoding results.
        """
        # Try GOOGLE_MAPS_API_KEY first, then fallback to GOOGLE_API_KEY
        self.api_key = (api_key or 
                       os.getenv('GOOGLE_MAPS_API_KEY') or 
                       os.getenv('GOOGLE_API_KEY'))
        self.cache_enabled = cache_enabled
        self.api_calls_today = 0
        self._availability_reason: Optional[str] = None
        
        if not self.api_key:
            logger.warning("No Google Maps API key provided. Geographic validation will be disabled.")
            self.client = None
            self._availability_reason = "missing_api_key"
        elif googlemaps is None:
            logger.warning("python-googlemaps no instalado; validación geográfica se omite")
            self.client = None
            self._availability_reason = "missing_googlemaps_lib"
        else:
            try:
                self.client = googlemaps.Client(key=self.api_key)
                logger.info("Google Maps client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Google Maps client: {e}")
                self.client = None
                self._availability_reason = f"client_error: {e}"
    
    def is_available(self) -> bool:
        """Check if geographic validation is available."""
        return self.client is not None
    
    def _get_threshold_for_region(self, city: str, country: str) -> float:
        """
        Get appropriate distance threshold for a specific region.
        
        Args:
            city: City name
            country: Country name
            
        Returns:
            Distance threshold in kilometers
        """
        # Region-specific threshold logic
        city_lower = city.lower()
        country_lower = country.lower()
        
        # Coastal tourist areas with higher thresholds
        coastal_cities = ['cartagena', 'santa marta', 'barú', 'cabo', 'cancún', 'punta cana']
        if any(coastal in city_lower for coastal in coastal_cities):
            return self.DEFAULT_THRESHOLDS['coastal']
        
        # Major metropolitan areas with lower thresholds
        metro_cities = ['bogotá', 'medellín', 'cali', 'mexico city', 'são paulo', 'buenos aires']
        if any(metro in city_lower for metro in metro_cities):
            return self.DEFAULT_THRESHOLDS['metropolitan']
        
        # Default threshold
        return self.DEFAULT_THRESHOLDS['default']
    
    @lru_cache(maxsize=500) if 'cache_enabled' in locals() else lambda f: f
    def _geocode_address(self, address: str) -> Optional[LocationInfo]:
        """
        Geocode an address to get coordinates.
        
        Args:
            address: Address to geocode
            
        Returns:
            LocationInfo with coordinates or None if failed
        """
        if not self.client:
            logger.error("Google Maps client not available")
            return None
        
        try:
            logger.debug(f"Geocoding address: {address}")
            result = self.client.geocode(address, language='es')
            
            if not result or len(result) == 0:
                logger.warning(f"No geocoding results for address: {address}")
                return None
            
            geocode_result = result[0]
            location = geocode_result['geometry']['location']
            coordinates = (location['lat'], location['lng'])
            
            # Extract administrative components from address
            city = ""
            country = ""
            state = ""
            for component in geocode_result['address_components']:
                if 'locality' in component['types']:
                    city = component['long_name']
                elif 'administrative_area_level_2' in component['types'] and not city:
                    city = component['long_name']
                if 'administrative_area_level_1' in component['types'] and not state:
                    state = component['long_name']
                elif 'country' in component['types']:
                    country = component['long_name']

            if not state:
                for component in geocode_result['address_components']:
                    if 'administrative_area_level_2' in component['types']:
                        state = component['long_name']
                        break
            
            place_id = geocode_result.get('place_id')
            
            return LocationInfo(
                name=geocode_result.get('formatted_address', address),
                address=geocode_result['formatted_address'],
                coordinates=coordinates,
                city=city,
                country=country,
                state=state,
                place_id=place_id
            )
            
        except (GeocoderUnavailable, GeocoderTimedOut) as e:
            logger.error(f"Geocoding service unavailable: {e}")
            return None
        except Exception as e:
            logger.error(f"Error geocoding address '{address}': {e}")
            return None
    
    def _search_hotel_location(
        self,
        hotel_name: str,
        city: str,
        expected_coordinates: Optional[Tuple[float, float]] = None
    ) -> Tuple[Optional[LocationInfo], int]:
        """
        Search for hotel location using Google Geocoding API.
        
        Args:
            hotel_name: Name of the hotel
            city: Expected city
            expected_coordinates: Coordinates of expected location (if available)
        
        Returns:
            Tuple[LocationInfo | None, api_calls_used]
        """
        if not self.client:
            logger.error("Google Maps client not available")
            return None, 0

        try:
            queries = []
            if city:
                queries.append(f"{hotel_name}, {city}, Colombia")
            queries.append(f"{hotel_name}, Colombia")

            best_match: Optional[LocationInfo] = None
            api_calls_used = 0
            seen_queries = set()

            for search_query in queries:
                if not search_query:
                    continue
                normalized_query = search_query.lower()
                if normalized_query in seen_queries:
                    continue
                seen_queries.add(normalized_query)

                logger.debug(f"Searching for hotel: {search_query}")
                result = self.client.geocode(
                    search_query,
                    language='es',
                    region='co'
                )
                api_calls_used += 1

                if not result:
                    continue

                geocode_result = result[0]
                location = geocode_result['geometry']['location']
                coordinates = (location['lat'], location['lng'])

                hotel_city = ""
                country = ""
                state = ""
                for component in geocode_result['address_components']:
                    if 'locality' in component['types']:
                        hotel_city = component['long_name']
                    elif 'administrative_area_level_2' in component['types'] and not hotel_city:
                        hotel_city = component['long_name']
                    if 'administrative_area_level_1' in component['types'] and not state:
                        state = component['long_name']
                    elif 'country' in component['types']:
                        country = component['long_name']

                if not hotel_city:
                    hotel_city = city

                if not state:
                    for component in geocode_result['address_components']:
                        if 'administrative_area_level_2' in component['types']:
                            state = component['long_name']
                            break

                location_info = LocationInfo(
                    name=geocode_result.get('formatted_address', search_query),
                    address=geocode_result['formatted_address'],
                    coordinates=coordinates,
                    city=hotel_city,
                    country=country,
                    state=state,
                    place_id=geocode_result.get('place_id')
                )

                distance_to_expected = None
                if expected_coordinates:
                    try:
                        distance_to_expected = _distance_km(expected_coordinates, coordinates)
                    except Exception:
                        distance_to_expected = None

                city_differs = (
                    bool(hotel_city)
                    and bool(city)
                    and hotel_city.lower() != city.lower()
                )

                if city_differs or (distance_to_expected is not None and distance_to_expected > 8.0):
                    return location_info, api_calls_used

                if best_match is None:
                    best_match = location_info

            if best_match is None:
                logger.warning(f"No geocoding results found for hotel: {hotel_name} en {city or 'Colombia'}")

            return best_match, api_calls_used

        except Exception as e:
            logger.error(f"Error searching for hotel '{hotel_name}' in '{city}': {e}")
            return None, 0
            
    def _get_place_details_new_api(self, place_id: str) -> Dict[str, Any]:
        """
        Fetch place details using the new Places API (v1).
        Requires 'Places API (New)' enabled in Google Cloud Console.
        
        Args:
            place_id: The unique identifier of the place.
            
        Returns:
            Dictionary with photos list if found.
        """
        if not self.api_key:
            return {}
            
        url = f"https://places.googleapis.com/v1/places/{place_id}"
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            # FieldMask is required for Places API (New) to specify return fields
            # Asking only for photos to minimize cost and latency
            "X-Goog-FieldMask": "photos"
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Places API (New) error: {response.status_code} - {response.text}")
                return {}
        except Exception as e:
            logger.error(f"Error calling Places API (New): {e}")
            return {}
    
    def validate_hotel_location(
        self,
        hotel_name: str,
        expected_city: str,
        expected_address: Optional[str] = None,
        custom_threshold_km: Optional[float] = None
    ) -> ValidationResult:
        """
        Validate that a hotel is within acceptable distance from expected location.
        
        Args:
            hotel_name: Name of the hotel to validate
            expected_city: Expected city where hotel should be located
            expected_address: Optional specific address for more precise validation
            custom_threshold_km: Custom distance threshold (overrides default)
            
        Returns:
            ValidationResult with validation outcome and details
        """
        api_calls_used = 0
        
        if not self.is_available():
            reason = self._availability_reason or "unavailable"
            return ValidationResult(
                is_valid=False,
                distance_km=0.0,
                threshold_km=0.0,
                expected_location=(0.0, 0.0),
                actual_location=(0.0, 0.0),
                hotel_name=hotel_name,
                expected_city=expected_city,
                confidence=0.0,
                error_message=f"Geographic validation not available ({reason})",
                api_calls_used=0
            )
        
        try:
            # Step 1: Get expected location coordinates
            expected_location_info = None
            if expected_address:
                expected_location_info = self._geocode_address(expected_address)
                api_calls_used += 1
            
            # If no specific address or geocoding failed, use city center
            if not expected_location_info:
                city_query = f"{expected_city}, Colombia"
                expected_location_info = self._geocode_address(city_query)
                api_calls_used += 1
            
            if not expected_location_info:
                return ValidationResult(
                    is_valid=False,
                    distance_km=0.0,
                    threshold_km=0.0,
                    expected_location=(0.0, 0.0),
                    actual_location=(0.0, 0.0),
                    hotel_name=hotel_name,
                    expected_city=expected_city,
                    confidence=0.0,
                    error_message=f"Could not geocode expected location: {expected_city}",
                    api_calls_used=api_calls_used
                )
            
            # Step 2: Find actual hotel location
            actual_location_info, search_calls = self._search_hotel_location(
                hotel_name,
                expected_city,
                expected_location_info.coordinates if expected_location_info else None
            )
            api_calls_used += search_calls
            
            if not actual_location_info:
                return ValidationResult(
                    is_valid=False,
                    distance_km=0.0,
                    threshold_km=0.0,
                    expected_location=expected_location_info.coordinates,
                    actual_location=(0.0, 0.0),
                    hotel_name=hotel_name,
                    expected_city=expected_city,
                    confidence=0.0,
                    error_message=f"Hotel not found in Google Maps: {hotel_name}",
                    api_calls_used=api_calls_used
                )
            
            # Step 3: Calculate distance
            distance_km = _distance_km(
                expected_location_info.coordinates,
                actual_location_info.coordinates
            )
            
            # Step 4: Determine threshold
            if custom_threshold_km:
                threshold_km = custom_threshold_km
            else:
                threshold_km = self._get_threshold_for_region(
                    expected_location_info.city,
                    expected_location_info.country
                )
            
            # Step 5: Determine validation result
            is_valid = distance_km <= threshold_km
            
            # Step 6: Extract extra data (like photos) via Place Details API (New)
            photo_count = 0
            if actual_location_info.place_id:
                details_result = self._get_place_details_new_api(actual_location_info.place_id)
                api_calls_used += 1  # Counting this HTTP call as an API use
                
                photos_list = details_result.get('photos', [])
                photo_count = len(photos_list)
                
                if photo_count > 0:
                    logger.debug(f"API Details for '{hotel_name}': Found {photo_count} photos (New API)")

            # Calculate confidence based on distance and name matching
            confidence = self._calculate_confidence(
                hotel_name,
                actual_location_info.name,
                distance_km,
                threshold_km
            )
            
            resolved_location = None
            if actual_location_info.city:
                resolved_parts = [actual_location_info.city]
                if actual_location_info.state:
                    resolved_parts.append(actual_location_info.state)
                elif actual_location_info.country:
                    resolved_parts.append(actual_location_info.country)
                resolved_location = ", ".join(part for part in resolved_parts if part)

            logger.info(
                f"Validation for '{hotel_name}': "
                f"Distance={distance_km:.2f}km, "
                f"Threshold={threshold_km}km, "
                f"Valid={is_valid}, "
                f"Confidence={confidence:.2f}"
            )
            
            return ValidationResult(
                is_valid=is_valid,
                distance_km=distance_km,
                threshold_km=threshold_km,
                expected_location=expected_location_info.coordinates,
                actual_location=actual_location_info.coordinates,
                hotel_name=hotel_name,
                expected_city=expected_city,
                confidence=confidence,
                api_calls_used=api_calls_used,
                expected_address=expected_location_info.address,
                actual_address=actual_location_info.address,
                actual_city=actual_location_info.city,
                actual_state=actual_location_info.state,
                actual_country=actual_location_info.country,
                actual_place_id=actual_location_info.place_id,
                resolved_location=resolved_location,
                photo_count=photo_count
            )
            
        except Exception as e:
            logger.error(f"Error during validation of hotel '{hotel_name}': {e}")
            return ValidationResult(
                is_valid=False,
                distance_km=0.0,
                threshold_km=0.0,
                expected_location=(0.0, 0.0),
                actual_location=(0.0, 0.0),
                hotel_name=hotel_name,
                expected_city=expected_city,
                confidence=0.0,
                error_message=f"Validation error: {str(e)}",
                api_calls_used=api_calls_used
            )
    
    def _calculate_confidence(
        self,
        expected_name: str,
        actual_name: str,
        distance_km: float,
        threshold_km: float
    ) -> float:
        """
        Calculate confidence score for validation result.
        
        Args:
            expected_name: Expected hotel name
            actual_name: Actual hotel name from Google Maps
            distance_km: Distance in kilometers
            threshold_km: Distance threshold
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        # Name similarity score (simple approach)
        expected_lower = expected_name.lower()
        actual_lower = actual_name.lower()
        
        # Check for exact match or partial match
        name_score = 0.0
        if expected_lower == actual_lower:
            name_score = 1.0
        elif expected_lower in actual_lower or actual_lower in expected_lower:
            name_score = 0.8
        else:
            # Check for word overlap
            expected_words = set(expected_lower.split())
            actual_words = set(actual_lower.split())
            if expected_words and actual_words:
                overlap = len(expected_words & actual_words)
                name_score = overlap / max(len(expected_words), len(actual_words))
        
        # Distance score (closer is better)
        distance_score = max(0.0, 1.0 - (distance_km / threshold_km))
        
        # Combined confidence (weighted average)
        confidence = (name_score * 0.6) + (distance_score * 0.4)
        
        return min(1.0, max(0.0, confidence))
    
    def get_validation_summary(self, results: list[ValidationResult]) -> Dict[str, Any]:
        """
        Generate summary statistics for multiple validation results.
        
        Args:
            results: List of ValidationResult objects
            
        Returns:
            Dictionary with summary statistics
        """
        if not results:
            return {
                'total_validations': 0,
                'valid_count': 0,
                'invalid_count': 0,
                'validity_rate': 0.0,
                'average_distance_km': 0.0,
                'average_confidence': 0.0,
                'total_api_calls': 0
            }
        
        valid_count = sum(1 for r in results if r.is_valid)
        total_distance = sum(r.distance_km for r in results)
        total_confidence = sum(r.confidence for r in results)
        total_api_calls = sum(r.api_calls_used for r in results)
        
        return {
            'total_validations': len(results),
            'valid_count': valid_count,
            'invalid_count': len(results) - valid_count,
            'validity_rate': valid_count / len(results),
            'average_distance_km': total_distance / len(results),
            'average_confidence': total_confidence / len(results),
            'total_api_calls': total_api_calls,
            'estimated_cost_usd': total_api_calls * 0.005  # $0.005 per API call estimate
        }

# Singleton instance for application-wide use
_validator_instance: Optional[GeoValidator] = None

def get_geo_validator() -> GeoValidator:
    """Get singleton instance of GeoValidator."""
    global _validator_instance
    if _validator_instance is None:
        _validator_instance = GeoValidator()
    return _validator_instance

def reset_geo_validator():
    """Reset singleton instance (useful for testing)."""
    global _validator_instance
    _validator_instance = None
