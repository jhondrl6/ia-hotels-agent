"""
Google Places API Client
========================
Cliente unificado para Google Places API (New) con:
- Cálculo de geo_score real (no estimado)
- Sistema de caché con TTL configurable
- Manejo de rate limiting
- Costo tracking

Basado en INFORME_PUNTOS_ESTIMACION.md v2.1

Fórmula geo_score:
    geo_score = (rating/5*30) + (reviews/100*2) + (fotos*0.5) +
                (10 if has_hours) + (10 if has_website)
"""

import os
import json
import time
import logging
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class PlaceData:
    """Estructura de datos de un lugar desde Places API."""
    place_id: str
    name: str
    rating: float
    reviews: int
    photos: int
    has_hours: bool
    has_website: bool
    website_url: Optional[str]
    phone: Optional[str]
    address: str
    city: str
    lat: float
    lng: float
    geo_score: int
    geo_score_formula: Dict[str, float]
    data_source: str
    fetched_at: str
    # Campos de diagnóstico de errores
    place_found: bool = True
    error_type: Optional[str] = None  # "NO_API_KEY", "ZERO_RESULTS", "QUOTA_EXCEEDED", "TIMEOUT", "API_ERROR", "PARSE_ERROR"
    error_message: Optional[str] = None
    search_query: Optional[str] = None


@dataclass
class GeoScoreBreakdown:
    """Desglose del cálculo de geo_score."""
    rating_score: float
    reviews_score: float
    photos_score: float
    hours_score: float
    website_score: float
    total: int


class GooglePlacesClient:
    """
    Cliente para Google Places API (New) con caché y cálculo de geo_score.
    
    Features:
    - Caché persistente con TTL configurable (default 30 días)
    - Cálculo de geo_score según fórmula del INFORME_PUNTOS_ESTIMACION
    - Rate limiting automático
    - Tracking de costos
    """
    
    BASE_URL = "https://places.googleapis.com/v1"
    
    SEARCH_FIELDS = "places.displayName,places.rating,places.userRatingCount,places.location,places.id,places.photos,places.regularOpeningHours,places.websiteUri,places.nationalPhoneNumber,places.formattedAddress,places.addressComponents"
    DETAILS_FIELDS = "displayName,rating,userRatingCount,photos,regularOpeningHours,websiteUri,nationalPhoneNumber,formattedAddress,addressComponents"
    
    DEFAULT_CACHE_TTL_DAYS = 30
    DEFAULT_CACHE_PATH = "data/cache/places_cache.json"
    
    MIN_REQUEST_INTERVAL = 0.1
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        cache_ttl_days: int = DEFAULT_CACHE_TTL_DAYS,
        cache_path: str = DEFAULT_CACHE_PATH
    ):
        """
        Inicializa el cliente de Google Places API.
        
        Args:
            api_key: Google Maps API key (si None, usa GOOGLE_MAPS_API_KEY env)
            cache_ttl_days: TTL del caché en días
            cache_path: Ruta al archivo de caché
        """
        self.api_key = api_key or os.getenv('GOOGLE_MAPS_API_KEY')
        self.cache_ttl = timedelta(days=cache_ttl_days)
        self.cache_path = Path(cache_path)
        self._cache: Dict[str, Dict] = {}
        self._last_request_time = 0.0
        self._request_count = 0
        self._cache_hits = 0
        
        self._load_cache()
        
        if not self.api_key:
            logger.warning("GOOGLE_MAPS_API_KEY no configurada - Places API no disponible")
    
    @property
    def is_available(self) -> bool:
        """Verifica si el cliente API está disponible."""
        return bool(self.api_key)
    
    def _load_cache(self) -> None:
        """Carga el caché desde disco."""
        try:
            if self.cache_path.exists():
                with open(self.cache_path, 'r', encoding='utf-8') as f:
                    self._cache = json.load(f)
                logger.info(f"Cache loaded: {len(self._cache)} entries")
        except Exception as e:
            logger.warning(f"Could not load cache: {e}")
            self._cache = {}
    
    def _save_cache(self) -> None:
        """Guarda el caché en disco."""
        try:
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.cache_path, 'w', encoding='utf-8') as f:
                json.dump(self._cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"Could not save cache: {e}")
    
    def _get_cache_key(self, place_id: str) -> str:
        """Genera clave de caché para un lugar."""
        return place_id
    
    def _get_cached_place(self, place_id: str) -> Optional[PlaceData]:
        """Obtiene lugar desde caché si es válido."""
        key = self._get_cache_key(place_id)
        cached = self._cache.get(key)
        
        if not cached:
            return None
        
        try:
            fetched_at = datetime.fromisoformat(cached.get('fetched_at', ''))
            if datetime.now() - fetched_at > self.cache_ttl:
                logger.debug(f"Cache expired for {place_id}")
                return None
        except Exception:
            return None
        
        self._cache_hits += 1
        return PlaceData(**cached)
    
    def _cache_place(self, place: PlaceData) -> None:
        """Guarda lugar en caché."""
        key = self._get_cache_key(place.place_id)
        self._cache[key] = asdict(place)
        self._save_cache()
    
    def _rate_limit(self) -> None:
        """Aplica rate limiting entre requests."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.MIN_REQUEST_INTERVAL:
            time.sleep(self.MIN_REQUEST_INTERVAL - elapsed)
        self._last_request_time = time.time()
    
    def calculate_geo_score(
        self,
        rating: float,
        reviews: int,
        photos: int,
        has_hours: bool,
        has_website: bool
    ) -> GeoScoreBreakdown:
        """
        Calcula geo_score usando la fórmula del INFORME_PUNTOS_ESTIMACION.md.
        
        Fórmula:
            geo_score = (rating/5*30) + (reviews/100*2) + (fotos*0.5) +
                        (10 if has_hours) + (10 if has_website)
        
        Max posible: 30 + 20 + 20 + 10 + 10 = 90
        Normalizado a escala 0-100.
        
        Args:
            rating: Rating de 0-5
            reviews: Número de reseñas de usuarios
            photos: Número de fotos
            has_hours: Si tiene horarios disponibles
            has_website: Si tiene sitio web disponible
            
        Returns:
            GeoScoreBreakdown con cálculo detallado
        """
        rating_score = (rating / 5.0) * 30.0 if rating else 0
        
        reviews_score = min((reviews / 100.0) * 2.0, 20.0)
        
        photos_score = min(photos * 0.5, 20.0)
        
        hours_score = 10.0 if has_hours else 0.0
        
        website_score = 10.0 if has_website else 0.0
        
        raw_total = rating_score + reviews_score + photos_score + hours_score + website_score
        total = int(min(raw_total * (100.0 / 90.0), 100.0))
        
        return GeoScoreBreakdown(
            rating_score=round(rating_score, 2),
            reviews_score=round(reviews_score, 2),
            photos_score=round(photos_score, 2),
            hours_score=hours_score,
            website_score=website_score,
            total=total
        )
    
    def _create_error_place(
        self,
        error_type: str,
        error_message: str,
        search_query: Optional[str] = None,
        place_id: str = ""
    ) -> PlaceData:
        """Crea un PlaceData para casos de error."""
        return PlaceData(
            place_id=place_id or "error",
            name="",
            rating=0.0,
            reviews=0,
            photos=0,
            has_hours=False,
            has_website=False,
            website_url=None,
            phone=None,
            address="",
            city="",
            lat=0.0,
            lng=0.0,
            geo_score=0,
            geo_score_formula={},
            data_source="error",
            fetched_at=datetime.now().isoformat(),
            place_found=False,
            error_type=error_type,
            error_message=error_message,
            search_query=search_query
        )

    def search_nearby_lodging(
        self,
        lat: float,
        lng: float,
        radius_km: float = 15.0,
        max_results: int = 20
    ) -> List[PlaceData]:
        """
        Busca lugares de hospedaje cercanos a una ubicación.
        
        Args:
            lat: Latitud
            lng: Longitud
            radius_km: Radio de búsqueda en kilómetros
            max_results: Número máximo de resultados
            
        Returns:
            Lista de objetos PlaceData con geo_score calculado
        """
        if not self.is_available:
            logger.warning("API not available")
            return [self._create_error_place(
                error_type="NO_API_KEY",
                error_message="Google Places API key not configured",
                search_query=f"lat:{lat}, lng:{lng}, radius:{radius_km}km"
            )]
        
        self._rate_limit()
        self._request_count += 1
        
        try:
            url = f"{self.BASE_URL}/places:searchNearby"
            
            headers = {
                'Content-Type': 'application/json',
                'X-Goog-Api-Key': self.api_key,
                'X-Goog-FieldMask': self.SEARCH_FIELDS
            }
            
            payload = {
                'includedTypes': ['lodging'],
                'maxResultCount': max_results,
                'locationRestriction': {
                    'circle': {
                        'center': {
                            'latitude': lat,
                            'longitude': lng
                        },
                        'radius': radius_km * 1000
                    }
                }
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            
            # Manejo específico de errores HTTP
            if response.status_code == 429:
                logger.error("API quota exceeded (429)")
                return [self._create_error_place(
                    error_type="QUOTA_EXCEEDED",
                    error_message="API quota exceeded - too many requests",
                    search_query=f"lat:{lat}, lng:{lng}, radius:{radius_km}km"
                )]
            
            if response.status_code == 403:
                logger.error("API key invalid or restricted (403)")
                return [self._create_error_place(
                    error_type="API_ERROR",
                    error_message="API key invalid or restricted",
                    search_query=f"lat:{lat}, lng:{lng}, radius:{radius_km}km"
                )]
            
            response.raise_for_status()
            data = response.json()
            
            places_raw = data.get('places', [])
            
            # Sin resultados
            if not places_raw:
                logger.warning(f"No places found for lat:{lat}, lng:{lng}")
                return [self._create_error_place(
                    error_type="ZERO_RESULTS",
                    error_message=f"No lodging places found within {radius_km}km radius",
                    search_query=f"lat:{lat}, lng:{lng}, radius:{radius_km}km"
                )]
            
            places = []
            for place in places_raw:
                place_data = self._parse_place_response(place)
                if place_data:
                    places.append(place_data)
            
            # Si no se pudo parsear ningún lugar
            if not places:
                return [self._create_error_place(
                    error_type="PARSE_ERROR",
                    error_message="Found places but could not parse any valid place data",
                    search_query=f"lat:{lat}, lng:{lng}, radius:{radius_km}km"
                )]
            
            return places
            
        except requests.Timeout:
            logger.error("Request to Places API timed out")
            return [self._create_error_place(
                error_type="TIMEOUT",
                error_message="Request to Places API timed out after 15 seconds",
                search_query=f"lat:{lat}, lng:{lng}, radius:{radius_km}km"
            )]
        except requests.RequestException as e:
            logger.error(f"Request error in nearby search: {e}")
            return [self._create_error_place(
                error_type="API_ERROR",
                error_message=f"Request error: {str(e)}",
                search_query=f"lat:{lat}, lng:{lng}, radius:{radius_km}km"
            )]
        except Exception as e:
            logger.error(f"Error in nearby search: {e}")
            return [self._create_error_place(
                error_type="API_ERROR",
                error_message=f"Unexpected error: {str(e)}",
                search_query=f"lat:{lat}, lng:{lng}, radius:{radius_km}km"
            )]
    
    def get_place_details(self, place_id: str) -> Optional[PlaceData]:
        """
        Obtiene información detallada de un lugar.
        
        Primero verifica caché, luego API si es necesario.
        
        Args:
            place_id: Google Place ID
            
        Returns:
            PlaceData o PlaceData con error si no se encuentra
        """
        cached = self._get_cached_place(place_id)
        if cached:
            return cached
        
        if not self.is_available:
            return self._create_error_place(
                error_type="NO_API_KEY",
                error_message="Google Places API key not configured",
                place_id=place_id
            )
        
        self._rate_limit()
        self._request_count += 1
        
        try:
            url = f"{self.BASE_URL}/places/{place_id}"
            
            headers = {
                'Content-Type': 'application/json',
                'X-Goog-Api-Key': self.api_key,
                'X-Goog-FieldMask': self.DETAILS_FIELDS
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            # Manejo específico de errores HTTP
            if response.status_code == 429:
                logger.error(f"API quota exceeded (429) for place_id: {place_id}")
                return self._create_error_place(
                    error_type="QUOTA_EXCEEDED",
                    error_message="API quota exceeded - too many requests",
                    place_id=place_id
                )
            
            if response.status_code == 403:
                logger.error(f"API key invalid or restricted (403) for place_id: {place_id}")
                return self._create_error_place(
                    error_type="API_ERROR",
                    error_message="API key invalid or restricted",
                    place_id=place_id
                )
            
            if response.status_code == 404:
                logger.warning(f"Place not found (404) for place_id: {place_id}")
                return self._create_error_place(
                    error_type="ZERO_RESULTS",
                    error_message=f"Place with ID '{place_id}' not found",
                    place_id=place_id
                )
            
            response.raise_for_status()
            data = response.json()
            
            # Verificar si la respuesta está vacía o no tiene datos
            if not data or not data.get('id'):
                return self._create_error_place(
                    error_type="ZERO_RESULTS",
                    error_message=f"Empty response for place_id: {place_id}",
                    place_id=place_id
                )
            
            place_data = self._parse_place_response(data)
            
            # Si no se pudo parsear, retornar error
            if not place_data:
                return self._create_error_place(
                    error_type="PARSE_ERROR",
                    error_message=f"Could not parse place data for place_id: {place_id}",
                    place_id=place_id
                )
            
            self._cache_place(place_data)
            return place_data
            
        except requests.Timeout:
            logger.error(f"Request to Places API timed out for place_id: {place_id}")
            return self._create_error_place(
                error_type="TIMEOUT",
                error_message="Request to Places API timed out after 10 seconds",
                place_id=place_id
            )
        except requests.RequestException as e:
            logger.error(f"Request error getting place details for {place_id}: {e}")
            return self._create_error_place(
                error_type="API_ERROR",
                error_message=f"Request error: {str(e)}",
                place_id=place_id
            )
        except Exception as e:
            logger.error(f"Error getting place details for {place_id}: {e}")
            return self._create_error_place(
                error_type="API_ERROR",
                error_message=f"Unexpected error: {str(e)}",
                place_id=place_id
            )
    
    def _parse_place_response(self, place: Dict[str, Any]) -> Optional[PlaceData]:
        """Parsea respuesta de Places API a PlaceData.
        
        Returns:
            PlaceData si se parseó correctamente, None si hay error de parseo
        """
        try:
            display_name = place.get('displayName', {})
            name = display_name.get('text', '') if isinstance(display_name, dict) else str(display_name)
            
            if not name:
                logger.warning(f"Place data missing name, place_id: {place.get('id', 'unknown')}")
                return None
            
            place_id = place.get('id', '')
            rating = place.get('rating', 0.0) or 0.0
            reviews = place.get('userRatingCount', 0) or 0
            photos = len(place.get('photos', []))
            has_hours = bool(place.get('regularOpeningHours'))
            website_url = place.get('websiteUri')
            has_website = bool(website_url)
            phone = place.get('nationalPhoneNumber')
            address = place.get('formattedAddress', '')
            
            location = place.get('location', {})
            lat = location.get('latitude', 0.0) or 0.0
            lng = location.get('longitude', 0.0) or 0.0
            
            city = ''
            for component in place.get('addressComponents', []):
                if 'locality' in component.get('types', []):
                    city = component.get('longText', component.get('shortText', ''))
                    break
            
            geo_breakdown = self.calculate_geo_score(
                rating=rating,
                reviews=reviews,
                photos=photos,
                has_hours=has_hours,
                has_website=has_website
            )
            
            return PlaceData(
                place_id=place_id,
                name=name,
                rating=rating,
                reviews=reviews,
                photos=photos,
                has_hours=has_hours,
                has_website=has_website,
                website_url=website_url,
                phone=phone,
                address=address,
                city=city,
                lat=lat,
                lng=lng,
                geo_score=geo_breakdown.total,
                geo_score_formula=asdict(geo_breakdown),
                data_source='places_api',
                fetched_at=datetime.now().isoformat(),
                place_found=True,
                error_type=None,
                error_message=None,
                search_query=None
            )
            
        except Exception as e:
            logger.error(f"Error parsing place response: {e}")
            return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del cliente."""
        return {
            'api_available': self.is_available,
            'total_requests': self._request_count,
            'cache_hits': self._cache_hits,
            'cache_entries': len(self._cache),
            'estimated_cost_usd': self._request_count * 0.005,
        }
    
    def clear_cache(self) -> None:
        """Limpia todos los datos del caché."""
        self._cache = {}
        self._save_cache()
        logger.info("Cache cleared")


_client_instance: Optional[GooglePlacesClient] = None


def get_places_client() -> GooglePlacesClient:
    """Obtiene instancia singleton de GooglePlacesClient."""
    global _client_instance
    if _client_instance is None:
        _client_instance = GooglePlacesClient()
    return _client_instance


def reset_places_client():
    """Reinicia instancia singleton (útil para testing)."""
    global _client_instance
    _client_instance = None