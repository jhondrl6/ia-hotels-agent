"""
SerpAPI Client - FASE 11 Extension

Integración con SerpAPI para obtener datos de hoteles desde Google Travel
cuando el scraping directo está bloqueado.

SerpAPI respeta ToS de Google y proporciona datos estructurados.
Límite: 250 búsquedas/mes (plan gratuito).

Documentación: https://serpapi.com/google-hotels-api
"""

import json
import logging
import os
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from datetime import datetime

import requests

logger = logging.getLogger(__name__)


@dataclass
class SerpHotelData:
    """Estructura de datos de hotel desde SerpAPI."""
    name: str = ""
    address: str = ""
    rating: float = 0.0
    reviews: int = 0
    photos: int = 0
    phone: Optional[str] = None
    website: Optional[str] = None
    place_id: Optional[str] = None
    location: Optional[str] = None
    price_range: Optional[str] = None
    # Metadatos de diagnostico
    found: bool = False
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    search_query: Optional[str] = None
    source: str = "serpapi"
    serpapi_qty_used: int = 0  # Contador de uso de cuota

    def to_dict(self) -> Dict[str, Any]:
        """Convierte a dict para compatibilidad con ResearchOutput."""
        d = {
            'name': self.name,
            'address': self.address,
            'rating': self.rating,
            'reviews': self.reviews,
            'photos': self.photos,
            'phone': self.phone,
            'website': self.website,
            'place_id': self.place_id,
            'location': self.location,
            'price_range': self.price_range,
            'found': self.found,
            'source': self.source,
            'serpapi_qty_used': self.serpapi_qty_used
        }
        if self.error_type is not None:
            d['error_type'] = self.error_type
        if self.error_message is not None:
            d['error_message'] = self.error_message
        if self.search_query is not None:
            d['search_query'] = self.search_query
        return d


class SerpAPIClient:
    """Cliente para SerpAPI Google Hotels API.
    
    Proporciona datos de hoteles via SerpAPI cuando Google Travel
    scraping está bloqueado. Respeta ToS de Google.
    
    Attributes:
        api_key: API key de SerpAPI (SERPAPI_API_KEY env var)
        timeout: Timeout para requests en segundos
        base_url: URL base de SerpAPI
    """
    
    BASE_URL = "https://serpapi.com/search"
    
    def __init__(self, api_key: Optional[str] = None, timeout: int = 30):
        """Inicializa el cliente SerpAPI.
        
        Args:
            api_key: API key de SerpAPI. Si no se provee, busca en env vars.
            timeout: Timeout para requests en segundos
        """
        self.api_key = api_key or os.environ.get('SERPAPI_API_KEY')
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
        })
        
        # Contador de uso de cuota
        self._queries_used = 0
        self._monthly_limit = 250
    
    @property
    def is_available(self) -> bool:
        """Verifica si SerpAPI está configurado y disponible."""
        return bool(self.api_key)
    
    @property
    def queries_remaining(self) -> int:
        """Retorna búsquedas restantes en el mes."""
        return max(0, self._monthly_limit - self._queries_used)
    
    def search_hotel(self, hotel_name: str, location: str = None) -> Dict[str, Any]:
        """Busca datos de hotel via SerpAPI Google Hotels.
        
        Args:
            hotel_name: Nombre del hotel a buscar
            location: Ubicación opcional (ciudad, región)
            
        Returns:
            Dict con datos del hotel o dict con found=False si no se encuentra
        """
        if not self.is_available:
            logger.warning("SerpAPI no configurado (SERPAPI_API_KEY no encontrada)")
            return SerpHotelData(
                found=False,
                error_type="API_NOT_CONFIGURED",
                error_message="SerpAPI API key no configurada",
                search_query=hotel_name
            ).to_dict()
        
        if self._queries_used >= self._monthly_limit:
            logger.warning(f"SerpAPI quota exhausted ({self._queries_used}/{self._monthly_limit})")
            return SerpHotelData(
                found=False,
                error_type="QUOTA_EXHAUSTED",
                error_message=f"SerpAPI quota exhausted ({self._queries_used}/{self._monthly_limit})",
                search_query=hotel_name
            ).to_dict()
        
        try:
            # Construir query para Google Hotels
            query = hotel_name
            if location:
                query = f"{hotel_name}, {location}"
            
            # Usar engine 'google' standard - Knowledge Graph proporciona datos del hotel
            params = {
                'q': query,
                'engine': 'google',
                'api_key': self.api_key,
                'hl': 'es',  # Español
                'gl': 'co',  # Colombia
            }
            
            logger.info(f"SerpAPI: Searching for '{query}'")
            response = self.session.get(
                self.BASE_URL,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            self._queries_used += 1
            logger.info(f"SerpAPI: Query {self._queries_used}/{self._monthly_limit} used")
            
            data = response.json()
            return self._parse_hotel_results(data, hotel_name)
            
        except requests.exceptions.Timeout:
            logger.warning(f"SerpAPI timeout for: {hotel_name}")
            return SerpHotelData(
                found=False,
                error_type="TIMEOUT",
                error_message="SerpAPI request timed out",
                search_query=hotel_name
            ).to_dict()
            
        except requests.exceptions.HTTPError as e:
            logger.warning(f"SerpAPI HTTP error: {e}")
            return SerpHotelData(
                found=False,
                error_type="HTTP_ERROR",
                error_message=str(e),
                search_query=hotel_name
            ).to_dict()
            
        except Exception as e:
            logger.error(f"SerpAPI unexpected error: {e}")
            return SerpHotelData(
                found=False,
                error_type="UNKNOWN_ERROR",
                error_message=str(e),
                search_query=hotel_name
            ).to_dict()
    
    def _parse_hotel_results(self, data: Dict[str, Any], original_query: str) -> Dict[str, Any]:
        """Parsea resultados de SerpAPI Google Search con Knowledge Graph.
        
        Args:
            data: Respuesta JSON de SerpAPI
            original_query: Query original de busqueda
            
        Returns:
            Dict con datos del hotel
        """
        try:
            # Verificar Knowledge Graph (datos estructurados de Google)
            kg = data.get('knowledge_graph', {})
            
            if kg.get('entity_type') == 'hotels' or 'hotel' in kg.get('title', '').lower():
                name = kg.get('title', '')
                
                # Verificar match con query original
                if not (original_query.lower() in name.lower() or 
                        name.lower() in original_query.lower()):
                    # Buscar en local_results
                    return self._parse_local_results(data, original_query)
                
                # Extraer rating
                rating = 0.0
                rating_val = kg.get('rating')
                if rating_val:
                    try:
                        rating = float(rating_val)
                    except (ValueError, TypeError):
                        rating = 0.0
                
                # Reviews
                reviews = 0
                reviews_val = kg.get('review_count')
                if reviews_val:
                    try:
                        reviews = int(reviews_val)
                    except (ValueError, TypeError):
                        reviews = 0
                
                # Address (puede venir con encoding issue, limpiar)
                address = kg.get('dirección', kg.get('address', ''))
                if isinstance(address, list):
                    address = ', '.join([a.get('text', '') for a in address if isinstance(a, dict)])
                
                # Phone
                phone = kg.get('teléfono', kg.get('phone'))
                if isinstance(phone, list):
                    phone = phone[0] if phone else None
                
                # Website
                website = kg.get('website')
                
                # Price range
                price_range = None
                pricing = kg.get('pricing', {})
                if pricing:
                    offers = pricing.get('offers', [])
                    if offers:
                        first_price = offers[0].get('price', '')
                        if first_price:
                            price_range = first_price
                
                return SerpHotelData(
                    name=name,
                    address=address,
                    rating=rating,
                    reviews=reviews,
                    photos=0,
                    phone=phone,
                    website=website,
                    place_id=kg.get('place_id'),
                    location=address,
                    price_range=price_range,
                    found=True,
                    search_query=original_query,
                    serpapi_qty_used=self._queries_used
                ).to_dict()
            
            # Si no hay KG de hotel, buscar en local_results
            return self._parse_local_results(data, original_query)
            
        except Exception as e:
            logger.error(f"SerpAPI parse error: {e}")
            return SerpHotelData(
                found=False,
                error_type="PARSE_ERROR",
                error_message=str(e),
                search_query=original_query,
                serpapi_qty_used=self._queries_used
            ).to_dict()
    
    def _parse_local_results(self, data: Dict[str, Any], original_query: str) -> Dict[str, Any]:
        """Parsea local_results de SerpAPI como fallback.
        
        Args:
            data: Respuesta JSON de SerpAPI
            original_query: Query original de busqueda
            
        Returns:
            Dict con datos del hotel
        """
        local_results = data.get('local_results', [])
        
        for result in local_results:
            name = result.get('title', '')
            
            # Match parcial
            if name and (original_query.lower() in name.lower() or 
                        name.lower() in original_query.lower()):
                
                # Rating y reviews
                rating = 0.0
                rating_val = result.get('rating')
                if rating_val:
                    try:
                        rating = float(rating_val)
                    except (ValueError, TypeError):
                        rating = 0.0
                
                reviews = 0
                reviews_val = result.get('reviews')
                if reviews_val:
                    try:
                        reviews = int(str(reviews_val).replace(',', ''))
                    except (ValueError, TypeError):
                        reviews = 0
                
                # Address
                address = result.get('address', result.get('location', ''))
                
                # Phone
                phone = result.get('phone')
                
                return SerpHotelData(
                    name=name,
                    address=address,
                    rating=rating,
                    reviews=reviews,
                    photos=0,
                    phone=phone,
                    website=None,
                    place_id=None,
                    location=address,
                    found=True,
                    search_query=original_query,
                    serpapi_qty_used=self._queries_used
                ).to_dict()
        
        # Hotel no encontrado
        logger.info(f"SerpAPI: Hotel '{original_query}' not found in results")
        return SerpHotelData(
            found=False,
            error_type="HOTEL_NOT_FOUND",
            error_message=f"Hotel '{original_query}' not found in SerpAPI results",
            search_query=original_query,
            serpapi_qty_used=self._queries_used
        ).to_dict()
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Retorna estadísticas de uso de la API.
        
        Returns:
            Dict con queries_used, queries_remaining, monthly_limit
        """
        return {
            'queries_used': self._queries_used,
            'queries_remaining': self.queries_remaining,
            'monthly_limit': self._monthly_limit,
            'is_available': self.is_available
        }
