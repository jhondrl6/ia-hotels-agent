"""SEO Elements Detector - Detección real de elementos SEO.

Detecta Open Graph tags, imágenes sin alt, y enlaces sociales
usando BeautifulSoup para parseo de HTML.
"""

from dataclasses import dataclass
from typing import Optional, Dict, List


SOCIAL_DOMAINS = [
    'facebook.com', 'instagram.com', 'twitter.com', 'x.com',
    'linkedin.com', 'youtube.com', 'tiktok.com', 'pinterest.com'
]


@dataclass
class SEOElementsResult:
    """Result of SEO elements detection."""
    open_graph: bool = False
    imagenes_alt: bool = False
    redes_activas: bool = False
    confidence: str = "estimated"  # estimated | low | medium | high
    notes: str = ""
    open_graph_tags: Dict[str, str] = None  # Detalles de og tags encontrados
    images_without_alt: int = 0   # Count de imágenes sin alt
    social_links_found: List[str] = None  # Lista de URLs de redes sociales

    def __post_init__(self):
        if self.open_graph_tags is None:
            self.open_graph_tags = {}
        if self.images_without_alt is None:
            self.images_without_alt = 0
        if self.social_links_found is None:
            self.social_links_found = []


class SEOElementsDetector:
    """Detecta presencia de elementos SEO en páginas web usando BeautifulSoup."""

    def detect(self, html: str, url: str) -> SEOElementsResult:
        """
        Detecta presencia de elementos SEO en el HTML.

        Args:
            html: Contenido HTML de la página
            url: URL de la página (para validación de redes sociales)

        Returns:
            SEOElementsResult con campos individuales
        """
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')

            og_detected, og_tags = self._detect_open_graph(soup)
            alt_good, images_without_alt = self._detect_images_alt(soup)
            social_found, social_links = self._detect_social_links(soup, url)

            return SEOElementsResult(
                open_graph=og_detected,
                imagenes_alt=alt_good,
                redes_activas=social_found,
                confidence="high",
                notes=f"Detected {len(og_tags)} OG tags, {images_without_alt} imgs without alt",
                open_graph_tags=og_tags,
                images_without_alt=images_without_alt,
                social_links_found=social_links
            )
        except Exception as e:
            return SEOElementsResult(
                confidence="low",
                notes=f"Detection error: {str(e)}"
            )

    def _detect_open_graph(self, soup) -> tuple[bool, Dict[str, str]]:
        """Detect Open Graph tags using BeautifulSoup."""
        og_tags = {}
        for meta in soup.find_all('meta', property=True):
            prop = meta.get('property', '')
            if prop.startswith('og:'):
                og_tags[prop] = meta.get('content', '')
        # Mínimo: og:title + og:description para considerar "detectado"
        has_essential = 'og:title' in og_tags and 'og:description' in og_tags
        return has_essential, og_tags

    def _detect_images_alt(self, soup) -> tuple[bool, int]:
        """Count images without alt text."""
        images = soup.find_all('img')
        without_alt = sum(1 for img in images if not img.get('alt', '').strip())
        # "Bueno" si <20% de imágenes sin alt
        has_good_alt = (without_alt / max(len(images), 1)) < 0.2 if images else True
        return has_good_alt, without_alt

    def _detect_social_links(self, soup, url: str) -> tuple[bool, List[str]]:
        """Detect social media links."""
        found = []
        for a in soup.find_all('a', href=True):
            href = a['href'].lower()
            if any(domain in href for domain in SOCIAL_DOMAINS):
                if href not in found:
                    found.append(href)
        return len(found) > 0, found
