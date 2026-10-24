"""
Booking.com Scraper - STUB RETIRADO (`D24`)

Este modulo es el stub de T8B: nunca hizo scraping. El scraper real del producto vive en
`modules/providers/autonomous_researcher.py` (httpx + BeautifulSoup con fallback verificado de
GBP) y NO se toca desde aqui.

`scrape()` declaraba `found=True` con `rating`, `review_count` y `price_range` en `None` y
`photos` vacio: leia como "medimos y no hay nada" cuando era "no medimos nada" (`DA-C3`).
Hoy devuelve el estado retirado - `found=False`, `data={}` y `data_status=STUB_RETIRADO`.
"""

from typing import Dict, Any, Optional, List
import logging
import json

logger = logging.getLogger(__name__)

# Estado que publica el stub retirado: nunca `found=True` con datos en None (`D24`/`DA-C3`).
ESTADO_STUB_RETIRADO = "STUB_RETIRADO"


class BookingScraper:
    """
    Stub de Booking.com: RETIRADO.

    Conserva la firma para que el export legacy de `modules.scrapers` no reviente, pero ya no
    finge un dato: `scrape()` devuelve el estado retirado. El scraper real del producto es
    `modules.providers.autonomous_researcher.BookingScraper`.
    """
    
    SOURCE_NAME = 'booking'
    
    def __init__(self):
        self.source_name = self.SOURCE_NAME
    
    def scrape(self, hotel_name: str, url: Optional[str] = None) -> Dict[str, Any]:
        """
        Devuelve el estado retirado del stub.

        Args:
            hotel_name: Nombre del hotel consultado (solo para la URL de busqueda)
            url: URL especifica (opcional)

        Returns:
            Dict con:
                - source: nombre de la fuente
                - found: siempre False
                - data: siempre vacio
                - data_status: ESTADO_STUB_RETIRADO
                - url: URL usada para la consulta
        """
        result = {
            'source': self.source_name,
            'found': False,
            'data': {},
            'data_status': ESTADO_STUB_RETIRADO,
            'url': url or self._build_search_url(hotel_name)
        }
        
        logger.info(
            f"[BookingScraper] Stub retirado (D24): {hotel_name} -> {ESTADO_STUB_RETIRADO}"
        )
        
        return result
    
    def _build_search_url(self, hotel_name: str) -> str:
        """Construye URL de búsqueda para Booking.com."""
        query = hotel_name.replace(' ', '+')
        return f"https://www.booking.com/search.html?ss={query}"
    
    def parse_review(self, raw_review: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parsea un review raw de Booking.
        
        Args:
            raw_review: Dict raw del review
            
        Returns:
            Dict parseado con campos normalizados
        """
        return {
            'author': raw_review.get('author_name', 'Anonymous'),
            'rating': raw_review.get('review评分'),  # Booking usa diferentes escalas
            'text': raw_review.get('review_text', ''),
            'date': raw_review.get('date_stayed', ''),
            'title': raw_review.get('review_title', ''),
            'source': self.source_name
        }
    
    def extract_amenities(self, raw_html: str) -> List[str]:
        """
        Extrae lista de amenities del HTML raw.
        
        Args:
            raw_html: HTML de la página del hotel
            
        Returns:
            Lista de amenidades encontradas
        """
        # T8B: Implementation - regex o BeautifulSoup para parsear
        amenities = []
        
        # Placeholder - en producción haríamos parsing real
        common_amenities = [
            'Free WiFi', 'Pool', 'Spa', 'Gym', 
            'Restaurant', 'Bar', 'Room Service',
            'Parking', 'Air Conditioning', 'Pet Friendly'
        ]
        
        return amenities


def create_booking_scraper() -> BookingScraper:
    """Factory function para crear BookingScraper."""
    return BookingScraper()
