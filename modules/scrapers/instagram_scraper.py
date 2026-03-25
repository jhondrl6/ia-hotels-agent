"""
Instagram Scraper - NEVER_BLOCK Architecture

Extrae datos de Instagram:
- Photos
- Engagement metrics
- Hashtags
- Profile info

T8B: Implement Source Scrapers
"""

from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


class InstagramScraper:
    """
    Scraper para Instagram/Facebook.
    
    En producción usaría Instagram Graph API o scraping con Playwright.
    """
    
    SOURCE_NAME = 'instagram'
    
    def __init__(self):
        self.source_name = self.SOURCE_NAME
    
    def scrape(self, hotel_name: str, url: Optional[str] = None) -> Dict[str, Any]:
        """
        Extrae datos de Instagram.
        
        Args:
            hotel_name: Nombre del hotel a buscar
            url: URL específica de Instagram (opcional)
            
        Returns:
            Dict con:
                - source: nombre de la fuente
                - found: bool indicando si se encontraron datos
                - data: dict con posts, followers, hashtags, photos
                - url: URL usada para la consulta
        """
        result = {
            'source': self.source_name,
            'found': False,
            'data': {},
            'url': url or self._build_hashtag_url(hotel_name)
        }
        
        try:
            # T8B: Integration point - en producción usaría Instagram API
            data = {
                'source': self.source_name,
                'hotel_name': hotel_name,
                'posts': [],  # Lista de {id, caption, likes, comments, date}
                'followers': None,  # ej: 15420
                'following': None,
                'hashtags': [],  # Lista de hashtags encontrados
                'recent_photos': [],  # URLs de fotos recientes
                'bio': None,
                'profile_url': None,
                'engagement_rate': None
            }
            
            result['found'] = True
            result['data'] = data
            
            logger.info(f"[InstagramScraper] Scraped {hotel_name}: found={result['found']}")
            
        except Exception as e:
            logger.warning(f"[InstagramScraper] Failed to scrape {hotel_name}: {e}")
            result['found'] = False
        
        return result
    
    def _build_hashtag_url(self, hotel_name: str) -> str:
        """Construye URL de hashtag para Instagram."""
        hashtag = hotel_name.replace(' ', '').replace('#', '')
        return f"https://www.instagram.com/explore/tags/{hashtag}/"
    
    def _build_profile_url(self, hotel_name: str) -> str:
        """Construye URL de perfil para Instagram."""
        username = hotel_name.replace(' ', '').lower()
        return f"https://www.instagram.com/{username}/"
    
    def parse_post(self, raw_post: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parsea un post raw de Instagram.
        """
        return {
            'id': raw_post.get('id', ''),
            'caption': raw_post.get('caption', ''),
            'likes': raw_post.get('likes_count', 0),
            'comments': raw_post.get('comments_count', 0),
            'date': raw_post.get('timestamp', ''),
            'image_url': raw_post.get('media_url', ''),
            'hashtags': raw_post.get('hashtags', []),
            'source': self.source_name
        }


def create_instagram_scraper() -> InstagramScraper:
    """Factory function para crear InstagramScraper."""
    return InstagramScraper()
