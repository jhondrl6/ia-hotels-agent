"""SEO Elements Detector - Stubs para elementos sin detector real.

Este módulo proporciona detectores básicos para elementos SEO.
Actualmente son stubs que retornan默认值 False hasta que se implementen
detectores reales usando BeautifulSoup/Playwright.
"""

from dataclasses import dataclass
from typing import Optional, Dict, List


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
    """
    Detecta presencia de elementos SEO en páginas web.
    
    Stacy actual: Stub que retorna todos默认值 False.
    Implementación completa requiere BeautifulSoup.
    """
    
    def __init__(self):
        self.confidence = "estimated"
    
    def detect(self, html: str, url: str) -> SEOElementsResult:
        """
        Detecta presencia de elementos SEO en el HTML.
        
        Args:
            html: Contenido HTML de la página
            url: URL de la página (para validación)
            
        Returns:
            SEOElementsResult con campos individuales
            
        TODO (implementación completa):
        - Usar BeautifulSoup para parseo
        - Detectar og:image, og:title, og:description
        - Contar imágenes sin atributo alt
        - Buscar enlaces a redes sociales conocidas
        """
        return SEOElementsResult(
            open_graph=False,  # TODO: implementar con BeautifulSoup
            imagenes_alt=False,  # TODO: implementar con BeautifulSoup
            redes_activas=False,  # TODO: implementar con BeautifulSoup
            confidence="estimated",
            notes="Stub detector - awaiting BeautifulSoup implementation"
        )
    
    def _detect_open_graph(self, soup) -> tuple[bool, Dict[str, str]]:
        """Detect Open Graph tags. Requires BeautifulSoup."""
        # PLACEHOLDER - would use soup.find_all('meta', property='og:*')
        return False, {}
    
    def _detect_images_alt(self, soup) -> tuple[bool, int]:
        """Count images without alt text. Requires BeautifulSoup."""
        # PLACEHOLDER - would use soup.find_all('img')
        return False, 0
    
    def _detect_social_links(self, soup, url: str) -> tuple[bool, List[str]]:
        """Detect social media links. Requires BeautifulSoup."""
        # PLACEHOLDER - would search for known social domain patterns
        return False, []
