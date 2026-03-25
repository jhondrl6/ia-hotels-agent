"""
Google Travel Scraper - FASE 11A

Scraper para Google Travel/Hotels (diferente API que Google Places).

Google Travel es un agregador de hoteles con informacion de precios,
disponibilidad y opiniones. El endpoint principal es:
    https://www.google.com/travel/hotels/entity/{entity_id}

Diferencia con Google Places API:
- Places API: places.googleapis.com/v1 - Busca en Maps/Nearby
- Travel API: google.com/travel/hotels - Agregador de hoteles

Basado en la realidad de Hotel Visperas:
- URL: https://www.google.com/travel/hotels/entity/ChcIqp2ZrdfnspElGgsvZy8xdGhobGtqYhAB
- Nombre: HOTEL VISPERAS
- Ubicacion: Km. 4 vía Termales, vereda La Leona, Santa Rosa de Cabal, Risaralda
"""

import json
import logging
import re
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus

import requests

logger = logging.getLogger(__name__)


@dataclass
class TravelPlaceData:
    """Estructura de datos de un lugar desde Google Travel."""
    name: str = ""
    address: str = ""
    rating: float = 0.0
    reviews: int = 0
    photos: int = 0
    phone: Optional[str] = None
    website: Optional[str] = None
    place_id: Optional[str] = None
    location: Optional[str] = None
    # Metadatos de diagnostico
    found: bool = False
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    search_query: Optional[str] = None
    source: str = "google_travel"

    def to_dict(self) -> Dict[str, Any]:
        """Convierte a dict para compatibilidad con ResearchOutput."""
        return {
            'name': self.name,
            'address': self.address,
            'rating': self.rating,
            'reviews': self.reviews,
            'photos': self.photos,
            'phone': self.phone,
            'website': self.website,
            'place_id': self.place_id,
            'location': self.location,
            'found': self.found,
            'source': self.source
        }


class GoogleTravelScraper:
    """Scraper para Google Travel/Hotels.

    Este scraper captura datos de hoteles que aparecen en Google Travel,
    incluyendo hoteles que pueden no estar en Google Places API pero
    si aparecen en el agregador de viajes de Google.

    Attributes:
        base_url: URL base de Google Travel
        timeout: Timeout para requests en segundos
        user_agent: User-Agent para requests
        delay: Delay entre requests para evitar rate limiting
    """

    BASE_URL = "https://www.google.com/travel/hotels"
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ]

    # Patrones para extraer datos del HTML/JSON de Google Travel
    JSON_LD_PATTERN = re.compile(
        r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        re.DOTALL | re.IGNORECASE
    )

    HOTEL_ENTITY_PATTERN = re.compile(
        r'["\']@type["\']\s*:\s*["\']Hotel["\']',
        re.IGNORECASE
    )

    RATING_PATTERN = re.compile(
        r'["\']ratingValue["\']\s*:\s*["\']?([\d.]+)["\']?',
        re.IGNORECASE
    )

    REVIEW_COUNT_PATTERN = re.compile(
        r'["\']reviewCount["\']\s*:\s*["\']?([\d,]+)["\']?',
        re.IGNORECASE
    )

    ADDRESS_LOCALITY_PATTERN = re.compile(
        r'["\']addressLocality["\']\s*:\s*["\']([^"\']+)["\']',
        re.IGNORECASE
    )

    ADDRESS_REGION_PATTERN = re.compile(
        r'["\']addressRegion["\']\s*:\s*["\']([^"\']+)["\']',
        re.IGNORECASE
    )

    STREET_ADDRESS_PATTERN = re.compile(
        r'["\']streetAddress["\']\s*:\s*["\']([^"\']+)["\']',
        re.IGNORECASE
    )

    def __init__(self, timeout: int = 30, delay: float = 2.0):
        """Inicializa el scraper.

        Args:
            timeout: Timeout para requests en segundos
            delay: Delay entre requests para evitar rate limiting
        """
        self.timeout = timeout
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })

    def _get_random_user_agent(self) -> str:
        """Retorna un User-Agent aleatorio para evitar bloqueo."""
        import random
        return random.choice(self.USER_AGENTS)

    def _build_search_url(self, hotel_name: str, location: str = None) -> str:
        """Construye URL de busqueda para Google Travel.

        Args:
            hotel_name: Nombre del hotel a buscar
            location: Ubicacion opcional (ciudad, region)

        Returns:
            URL completa para la busqueda
        """
        query = hotel_name
        if location:
            query = f"{hotel_name}, {location}"

        # Google Travel usa busqueda por query
        encoded_query = quote_plus(query)
        return f"{self.BASE_URL}?q={encoded_query}"

    def _build_entity_url(self, entity_id: str) -> str:
        """Construye URL directa a entidad de hotel.

        Args:
            entity_id: Entity ID de Google Travel (ej: ChcIqp2ZrdfnspElGgsvZy8xdGhobGtqYhAB)

        Returns:
            URL directa a la entidad
        """
        return f"{self.BASE_URL}/entity/{entity_id}"

    def _extract_json_ld_data(self, html: str) -> Optional[Dict[str, Any]]:
        """Extrae datos de JSON-LD en el HTML.

        Args:
            html: Contenido HTML de la pagina

        Returns:
            Dict con datos estructurados o None si no se encuentra
        """
        matches = self.JSON_LD_PATTERN.findall(html)
        for match in matches:
            try:
                data = json.loads(match)
                # Buscar tipo Hotel
                if isinstance(data, dict):
                    if data.get('@type') == 'Hotel' or 'Hotel' in str(data.get('@type', '')):
                        return data
                    # Buscar en @graph
                    if '@graph' in data:
                        for item in data['@graph']:
                            if item.get('@type') == 'Hotel' or 'Hotel' in str(item.get('@type', '')):
                                return item
                elif isinstance(data, list):
                    for item in data:
                        if item.get('@type') == 'Hotel' or 'Hotel' in str(item.get('@type', '')):
                            return item
            except json.JSONDecodeError:
                continue
        return None

    def _parse_rating(self, text: str) -> float:
        """Parsea rating de texto.

        Args:
            text: Texto conteniendo rating

        Returns:
            Rating como float o 0.0 si no se puede parsear
        """
        if not text:
            return 0.0
        match = self.RATING_PATTERN.search(text)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                return 0.0
        return 0.0

    def _parse_review_count(self, text: str) -> int:
        """Parsea cantidad de reviews de texto.

        Args:
            text: Texto conteniendo review count

        Returns:
            Cantidad de reviews como int o 0 si no se puede parsear
        """
        if not text:
            return 0
        match = self.REVIEW_COUNT_PATTERN.search(text)
        if match:
            try:
                return int(match.group(1).replace(',', ''))
            except ValueError:
                return 0
        return 0

    def _parse_address(self, data: Dict[str, Any]) -> str:
        """Construye direccion completa desde JSON-LD.

        Args:
            data: Dict con datos de direccion

        Returns:
            String con direccion completa
        """
        parts = []

        street = data.get('address', {}).get('streetAddress', '')
        if street:
            parts.append(street)

        locality = data.get('address', {}).get('addressLocality', '')
        if locality:
            parts.append(locality)

        region = data.get('address', {}).get('addressRegion', '')
        if region:
            parts.append(region)

        country = data.get('address', {}).get('addressCountry', '')
        if country:
            if isinstance(country, dict):
                country = country.get('name', '')
            parts.append(country)

        return ', '.join(parts) if parts else ''

    def scrape_hotel(self, hotel_name: str, location: str = None) -> Dict[str, Any]:
        """Scrapes hotel data from Google Travel.

        Args:
            hotel_name: Nombre del hotel
            location: Ubicacion opcional (ciudad, region)

        Returns:
            Dict con datos del hotel o dict con found=False si no se encuentra
        """
        try:
            # Intentar busqueda por query
            url = self._build_search_url(hotel_name, location)
            return self._fetch_and_parse(url, search_query=f"{hotel_name}, {location or ''}")

        except requests.exceptions.Timeout:
            logger.warning(f"Timeout fetching Google Travel for: {hotel_name}")
            return TravelPlaceData(
                found=False,
                error_type="TIMEOUT",
                error_message="Request timed out",
                search_query=hotel_name
            ).to_dict()

        except requests.exceptions.RequestException as e:
            logger.warning(f"Request error fetching Google Travel for {hotel_name}: {e}")
            return TravelPlaceData(
                found=False,
                error_type="REQUEST_ERROR",
                error_message=str(e),
                search_query=hotel_name
            ).to_dict()

    def scrape_by_entity_id(self, entity_id: str, hotel_name: str = None) -> Dict[str, Any]:
        """Scrapes hotel data directly by Google Travel entity ID.

        Args:
            entity_id: Google Travel entity ID (ej: ChcIqp2ZrdfnspElGgsvZy8xdGhobGtqYhAB)
            hotel_name: Nombre del hotel (para logging)

        Returns:
            Dict con datos del hotel o dict con found=False si no se encuentra
        """
        try:
            url = self._build_entity_url(entity_id)
            result = self._fetch_and_parse(url, search_query=hotel_name or entity_id)
            if result.get('found'):
                result['place_id'] = entity_id
            return result

        except Exception as e:
            logger.warning(f"Error fetching entity {entity_id}: {e}")
            return TravelPlaceData(
                found=False,
                error_type="ENTITY_ERROR",
                error_message=str(e),
                search_query=hotel_name,
                place_id=entity_id
            ).to_dict()

    def _fetch_and_parse(self, url: str, search_query: str = None) -> Dict[str, Any]:
        """Fetch y parse de una URL de Google Travel.

        Args:
            url: URL a fetch
            search_query: Query de busqueda para logging

        Returns:
            Dict con datos del hotel
        """
        # Delay para evitar rate limiting
        time.sleep(self.delay)

        headers = {
            'User-Agent': self._get_random_user_agent()
        }

        response = self.session.get(url, headers=headers, timeout=self.timeout)

        if response.status_code == 404:
            logger.info(f"Google Travel: Hotel not found (404) for query: {search_query}")
            return TravelPlaceData(
                found=False,
                error_type="NOT_FOUND",
                error_message="Hotel not found in Google Travel",
                search_query=search_query
            ).to_dict()

        if response.status_code != 200:
            logger.warning(f"Google Travel: HTTP {response.status_code} for query: {search_query}")
            return TravelPlaceData(
                found=False,
                error_type="HTTP_ERROR",
                error_message=f"HTTP {response.status_code}",
                search_query=search_query
            ).to_dict()

        # Intentar parsear JSON-LD
        data = self._extract_json_ld_data(response.text)

        if data:
            return self._parse_hotel_data(data, search_query)

        # Si no hay JSON-LD, buscar en el HTML con patrones
        return self._parse_html_fallback(response.text, search_query)

    def _parse_hotel_data(self, data: Dict[str, Any], search_query: str = None) -> Dict[str, Any]:
        """Parsea datos de hotel desde JSON-LD.

        Args:
            data: Dict con datos del hotel
            search_query: Query de busqueda original

        Returns:
            Dict con datos parseados
        """
        result = TravelPlaceData(
            name=data.get('name', ''),
            address=self._parse_address(data),
            rating=self._parse_rating(str(data.get('aggregateRating', {}))),
            reviews=self._parse_review_count(str(data.get('aggregateRating', {}))),
            phone=data.get('address', {}).get('telephone'),
            website=data.get('url') or data.get('website'),
            location=search_query,
            found=True,
            search_query=search_query
        )

        # Extraer fotos si disponible
        if 'image' in data:
            if isinstance(data['image'], list):
                result.photos = len(data['image'])
            else:
                result.photos = 1

        return result.to_dict()

    def _parse_html_fallback(self, html: str, search_query: str = None) -> Dict[str, Any]:
        """Fallback parser cuando JSON-LD no esta disponible.

        Args:
            html: Contenido HTML
            search_query: Query de busqueda

        Returns:
            Dict con datos extraidos o found=False
        """
        # Buscar patrones basicos en el HTML
        name_match = re.search(r'<title>([^<]+)</title>', html)
        name = name_match.group(1) if name_match else ''

        # Limpiar nombre del title
        if ' - ' in name:
            name = name.split(' - ')[0].strip()
        if '|' in name:
            name = name.split('|')[0].strip()

        rating_match = self.RATING_PATTERN.search(html)
        rating = float(rating_match.group(1)) if rating_match else 0.0

        reviews_match = self.REVIEW_COUNT_PATTERN.search(html)
        reviews = int(reviews_match.group(1).replace(',', '')) if reviews_match else 0

        address_parts = []
        locality_match = self.ADDRESS_LOCALITY_PATTERN.search(html)
        if locality_match:
            address_parts.append(locality_match.group(1))

        region_match = self.ADDRESS_REGION_PATTERN.search(html)
        if region_match:
            address_parts.append(region_match.group(1))

        address = ', '.join(address_parts) if address_parts else ''

        if not name or name == '':
            return TravelPlaceData(
                found=False,
                error_type="PARSE_ERROR",
                error_message="Could not parse hotel data from HTML",
                search_query=search_query
            ).to_dict()

        return TravelPlaceData(
            name=name,
            address=address,
            rating=rating,
            reviews=reviews,
            found=True,
            search_query=search_query
        ).to_dict()

    def close(self):
        """Cierra la sesion HTTP."""
        self.session.close()


# Para uso directo
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python google_travel_scraper.py <hotel_name> [location]")
        sys.exit(1)

    hotel_name = sys.argv[1]
    location = sys.argv[2] if len(sys.argv) > 2 else None

    scraper = GoogleTravelScraper(delay=1.0)
    result = scraper.scrape_hotel(hotel_name, location)

    print(json.dumps(result, indent=2, ensure_ascii=False))
    scraper.close()
