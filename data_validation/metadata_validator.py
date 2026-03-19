"""Validador de metadatos para detección de configuraciones por defecto de CMS.

Sprint 1, Fase 1: Detecta strings por defecto de WordPress y otros CMS
que indican sitios no configurados profesionalmente.
"""
from typing import List, Optional

from bs4 import BeautifulSoup

from data_models.claim import Claim
from enums.severity import Severity

DEFAULT_WORDPRESS_STRINGS = [
    "My WordPress Blog",
    "My WordPress Website",
    "Just another WordPress site",
    "Just another WordPress blog",
    "Sitio de WordPress",
    "Mi sitio web",
    "Un sitio de WordPress",
    "Otro sitio de WordPress",
    "Mi blog de WordPress",
]

GENERIC_DESCRIPTIONS = [
    "This is an example page",
    "This is a sample page",
    "Page not found",
    "Just another WordPress site",
]


class MetadataValidator:
    """Valida metadatos HTML para detectar configuraciones por defecto de CMS."""

    def __init__(self, default_strings: Optional[List[str]] = None):
        """Inicializa el validador con strings por defecto configurables.

        Args:
            default_strings: Lista opcional de strings por defecto a detectar.
                           Si no se proporciona, usa DEFAULT_WORDPRESS_STRINGS.
        """
        self.default_strings = default_strings or DEFAULT_WORDPRESS_STRINGS

    def analyze(self, html_content: str, url: str) -> List[Claim]:
        """Analiza el HTML para detectar metadatos por defecto.

        Extrae el título y meta description del HTML, detecta si contienen
        strings por defecto de CMS, y genera Claims con la severidad apropiada.

        Args:
            html_content: Contenido HTML del sitio web.
            url: URL del sitio analizado (para metadata).

        Returns:
            List[Claim]: Lista de claims generados, puede estar vacía.
        """
        claims: List[Claim] = []
        soup = BeautifulSoup(html_content, "html.parser")

        title = self._extract_title(soup)
        description = self._extract_description(soup)

        title_claim = self.validate_title(title)
        if title_claim:
            claims.append(title_claim)

        description_claim = self.validate_description(description)
        if description_claim:
            claims.append(description_claim)

        return claims

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extrae el título del HTML parseado.

        Args:
            soup: Objeto BeautifulSoup con el HTML parseado.

        Returns:
            str: Contenido del tag <title> o string vacío si no existe.
        """
        title_tag = soup.find("title")
        if title_tag and title_tag.string:
            return title_tag.string.strip()
        return ""

    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extrae la meta description del HTML parseado.

        Args:
            soup: Objeto BeautifulSoup con el HTML parseado.

        Returns:
            str: Contenido del meta description o string vacío si no existe.
        """
        meta = soup.find("meta", attrs={"name": "description"})
        if meta and meta.get("content"):
            return meta["content"].strip()
        return ""

    def detect_cms(self, html_content: str) -> str:
        """Detecta el CMS utilizado basado en patrones en el HTML.

        Args:
            html_content: Contenido HTML del sitio web.

        Returns:
            str: Identificador del CMS detectado: "wordpress", "shopify",
                 "wix", o "custom" si no se detecta ninguno conocido.
        """
        soup = BeautifulSoup(html_content, "html.parser")
        html_str = str(soup).lower()

        if any(marker in html_str for marker in [
            "wp-content",
            "wp-includes",
            "wordpress",
            'meta name="generator" content="wordpress',
        ]):
            return "wordpress"

        if any(marker in html_str for marker in [
            "cdn.shopify.com",
            "shopify.com",
            'meta name="shopify',
        ]):
            return "shopify"

        if any(marker in html_str for marker in [
            "wix.com",
            "wixsite",
            "x-wix",
            'meta name="generator" content="wix',
        ]):
            return "wix"

        return "custom"

    def validate_title(self, title: str) -> Optional[Claim]:
        """Valida el título de la página contra strings por defecto.

        Args:
            title: El título de la página extraído del HTML.

        Returns:
            Optional[Claim]: Claim CRITICAL si el título coincide con strings
            por defecto, está vacío, o es muy corto. None si es válido.
        """
        if not title:
            return Claim(
                source_id="metadata_validator",
                evidence_excerpt="<empty>",
                severity=Severity.CRITICAL,
                category="metadata",
                message="El título de la página está vacío",
                confidence=0.95,
                field_path="title",
            )

        for default_string in self.default_strings:
            if default_string.lower() in title.lower():
                return Claim(
                    source_id="metadata_validator",
                    evidence_excerpt=title,
                    severity=Severity.CRITICAL,
                    category="metadata",
                    message=f"Título contiene string por defecto de CMS: '{default_string}'",
                    confidence=0.95,
                    field_path="title",
                )

        if len(title) < 10:
            return Claim(
                source_id="metadata_validator",
                evidence_excerpt=title,
                severity=Severity.HIGH,
                category="metadata",
                message=f"Título demasiado corto ({len(title)} caracteres, mínimo 10)",
                confidence=0.95,
                field_path="title",
            )

        return None

    def validate_description(self, description: str) -> Optional[Claim]:
        """Valida la meta description contra patrones genéricos.

        Args:
            description: El contenido de la meta description.

        Returns:
            Optional[Claim]: Claim HIGH si está vacía, MEDIUM si es genérica.
            None si es válida.
        """
        if not description:
            return Claim(
                source_id="metadata_validator",
                evidence_excerpt="<empty>",
                severity=Severity.HIGH,
                category="metadata",
                message="Meta description está vacía",
                confidence=0.95,
                field_path="meta.description",
            )

        for generic in GENERIC_DESCRIPTIONS:
            if generic.lower() in description.lower():
                return Claim(
                    source_id="metadata_validator",
                    evidence_excerpt=description,
                    severity=Severity.MEDIUM,
                    category="metadata",
                    message=f"Meta description contiene texto genérico: '{generic}'",
                    confidence=0.95,
                    field_path="meta.description",
                )

        return None
