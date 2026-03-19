"""Tests para MetadataValidator.

Sprint 1: Validación de metadatos HTML para detectar configuraciones
por defecto de CMS (WordPress, etc.).
"""
import sys
import os

# Add project root to Python path BEFORE any other imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

import pytest

from modules.data_validation.metadata_validator import MetadataValidator
from enums.severity import Severity


@pytest.fixture
def validator():
    """Fixture que proporciona una instancia de MetadataValidator."""
    return MetadataValidator()


class TestDetectWordPressDefaultTitle:
    """Tests para detección de títulos por defecto de WordPress."""

    def test_detect_wordpress_default_title(self, validator):
        """Detecta 'My WordPress Blog' en el título."""
        html = '<html><head><title>Hotel Vísperas | My WordPress Blog</title><meta name="description" content="Hotel boutique en Oaxaca"></head></html>'
        claims = validator.analyze(html, "https://hotel.com")
        
        title_claims = [c for c in claims if c.field_path == "title"]
        assert len(title_claims) == 1
        assert title_claims[0].severity == Severity.CRITICAL
        assert "My WordPress Blog" in title_claims[0].message
        assert title_claims[0].field_path == "title"

    def test_detect_variation_just_another_wordpress(self, validator):
        """Detecta 'Just another WordPress site' en el título."""
        html = "<html><head><title>Hotel - Just another WordPress site</title></head></html>"
        claims = validator.analyze(html, "https://hotel.com")
        
        assert len(claims) >= 1
        assert any("Just another WordPress site" in c.message for c in claims)

    def test_detect_spanish_default(self, validator):
        """Detecta variación en español 'Sitio de WordPress'."""
        html = "<html><head><title>Mi Hotel - Sitio de WordPress</title></head></html>"
        claims = validator.analyze(html, "https://hotel.com")
        
        assert len(claims) >= 1
        assert any("Sitio de WordPress" in c.message for c in claims)


class TestDetectEmptyTitle:
    """Tests para detección de título vacío."""

    def test_detect_empty_title(self, validator):
        """Detecta título vacío (CRITICAL)."""
        html = '<html><head><title></title><meta name="description" content="Hotel boutique"></head></html>'
        claims = validator.analyze(html, "https://hotel.com")
        
        title_claims = [c for c in claims if c.field_path == "title"]
        assert len(title_claims) == 1
        assert title_claims[0].severity == Severity.CRITICAL
        assert "vacío" in title_claims[0].message.lower() or "empty" in title_claims[0].message.lower()

    def test_detect_missing_title_tag(self, validator):
        """Detecta ausencia completa del tag title."""
        html = '<html><head><meta name="description" content="Hotel boutique"></head></html>'
        claims = validator.analyze(html, "https://hotel.com")
        
        title_claims = [c for c in claims if c.field_path == "title"]
        assert len(title_claims) == 1
        assert title_claims[0].severity == Severity.CRITICAL

    def test_detect_whitespace_only_title(self, validator):
        """Detecta título con solo espacios en blanco."""
        html = '<html><head><title>   </title><meta name="description" content="Hotel boutique"></head></html>'
        claims = validator.analyze(html, "https://hotel.com")
        
        title_claims = [c for c in claims if c.field_path == "title"]
        assert len(title_claims) == 1
        assert title_claims[0].severity == Severity.CRITICAL


class TestDetectShortTitle:
    """Tests para detección de título muy corto."""

    def test_detect_short_title(self, validator):
        """Detecta título < 10 caracteres (HIGH)."""
        html = '<html><head><title>Hotel</title><meta name="description" content="Hotel boutique"></head></html>'
        claims = validator.analyze(html, "https://hotel.com")
        
        title_claims = [c for c in claims if c.field_path == "title"]
        assert len(title_claims) == 1
        assert title_claims[0].severity == Severity.HIGH
        assert "corto" in title_claims[0].message.lower() or "short" in title_claims[0].message.lower()
        assert "5" in title_claims[0].message or "5 caracteres" in title_claims[0].message

    def test_detect_nine_char_title(self, validator):
        """Detecta título de exactamente 9 caracteres."""
        html = '<html><head><title>Mi Hotel</title><meta name="description" content="Hotel boutique"></head></html>'  # 8 chars
        claims = validator.analyze(html, "https://hotel.com")
        
        title_claims = [c for c in claims if c.field_path == "title"]
        assert len(title_claims) == 1
        assert title_claims[0].severity == Severity.HIGH

    def test_title_exactly_ten_chars_is_valid(self, validator):
        """Título de exactamente 10 caracteres no genera claim."""
        html = "<html><head><title>Mi Hotel X</title></head></html>"  # 10 chars
        claims = validator.analyze(html, "https://hotel.com")
        
        # No debe haber claims de título corto
        title_claims = [c for c in claims if c.field_path == "title"]
        assert len(title_claims) == 0


class TestDetectEmptyDescription:
    """Tests para detección de meta description vacía."""

    def test_detect_empty_description(self, validator):
        """Detecta meta description vacía (HIGH)."""
        html = """
        <html>
        <head>
            <title>Hotel Vísperas | Hotel Boutique en Oaxaca</title>
            <meta name="description" content="">
        </head>
        </html>
        """
        claims = validator.analyze(html, "https://hotel.com")
        
        desc_claims = [c for c in claims if c.field_path == "meta.description"]
        assert len(desc_claims) == 1
        assert desc_claims[0].severity == Severity.HIGH
        assert "vacía" in desc_claims[0].message.lower() or "empty" in desc_claims[0].message.lower()

    def test_detect_missing_description(self, validator):
        """Detecta ausencia completa de meta description."""
        html = """
        <html>
        <head>
            <title>Hotel Vísperas</title>
        </head>
        </html>
        """
        claims = validator.analyze(html, "https://hotel.com")
        
        desc_claims = [c for c in claims if c.field_path == "meta.description"]
        assert len(desc_claims) == 1
        assert desc_claims[0].severity == Severity.HIGH

    def test_detect_whitespace_description(self, validator):
        """Detecta meta description con solo espacios."""
        html = """
        <html>
        <head>
            <title>Hotel Vísperas</title>
            <meta name="description" content="   ">
        </head>
        </html>
        """
        claims = validator.analyze(html, "https://hotel.com")
        
        desc_claims = [c for c in claims if c.field_path == "meta.description"]
        assert len(desc_claims) == 1
        assert desc_claims[0].severity == Severity.HIGH


class TestValidTitleNoClaims:
    """Tests para títulos válidos que no deben generar claims."""

    def test_valid_title_no_claims(self, validator):
        """Título válido no genera claims."""
        html = "<html><head><title>Hotel Vísperas | Hotel Boutique en Oaxaca</title></head></html>"
        claims = validator.analyze(html, "https://hotel.com")
        
        title_claims = [c for c in claims if c.field_path == "title"]
        assert len(title_claims) == 0

    def test_valid_long_title(self, validator):
        """Título largo y descriptivo es válido."""
        html = """
        <html>
        <head>
            <title>Hotel Vísperas - Hotel Boutique en el Centro Histórico de Oaxaca</title>
        </head>
        </html>
        """
        claims = validator.analyze(html, "https://hotel.com")
        
        title_claims = [c for c in claims if c.field_path == "title"]
        assert len(title_claims) == 0

    def test_valid_title_with_description(self, validator):
        """Título y descripción válidos no generan claims."""
        html = """
        <html>
        <head>
            <title>Hotel Vísperas | Hotel Boutique en Oaxaca</title>
            <meta name="description" content="Descubre Hotel Vísperas, un boutique hotel en el corazón de Oaxaca. Habitaciones elegantes, servicio personalizado y ubicación privilegiada.">
        </head>
        </html>
        """
        claims = validator.analyze(html, "https://hotel.com")
        
        assert len(claims) == 0


class TestGenericDescriptions:
    """Tests para descripciones genéricas."""

    def test_detect_generic_description_sample_page(self, validator):
        """Detecta 'This is a sample page' en description."""
        html = """
        <html>
        <head>
            <title>Hotel Vísperas</title>
            <meta name="description" content="This is a sample page for demonstration">
        </head>
        </html>
        """
        claims = validator.analyze(html, "https://hotel.com")
        
        desc_claims = [c for c in claims if c.field_path == "meta.description"]
        assert len(desc_claims) == 1
        assert desc_claims[0].severity == Severity.MEDIUM
        assert "genérico" in desc_claims[0].message.lower() or "generic" in desc_claims[0].message.lower()


class TestCMSDetection:
    """Tests para detección de CMS."""

    def test_detect_wordpress_cms(self, validator):
        """Detecta WordPress por wp-content."""
        html = '<html><head><title>Hotel</title></head><body><script src="/wp-content/themes/hotel/main.js"></script></body></html>'
        
        cms = validator.detect_cms(html)
        
        assert cms == "wordpress"

    def test_detect_shopify_cms(self, validator):
        """Detecta Shopify por cdn.shopify.com."""
        html = '<html><head><title>Hotel</title></head><body><script src="https://cdn.shopify.com/s/files/1/xxx.js"></script></body></html>'
        
        cms = validator.detect_cms(html)
        
        assert cms == "shopify"

    def test_detect_wix_cms(self, validator):
        """Detecta Wix por wix.com."""
        html = '<html><head><title>Hotel</title></head><body><script src="https://static.wix.com/xxx.js"></script></body></html>'
        
        cms = validator.detect_cms(html)
        
        assert cms == "wix"

    def test_detect_custom_cms(self, validator):
        """Detecta custom cuando no hay patrones conocidos."""
        html = '<html><head><title>Hotel</title></head><body><script src="/assets/main.js"></script></body></html>'
        
        cms = validator.detect_cms(html)
        
        assert cms == "custom"


class TestEdgeCases:
    """Tests para casos edge."""

    def test_title_with_whitespace(self, validator):
        """Título con whitespace es procesado correctamente."""
        html = "<html><head><title>   Hotel   </title></head><body></body></html>"
        
        claims = validator.analyze(html, "https://hotel.com")
        
        # "Hotel" tiene 5 caracteres, debe generar claim HIGH
        title_claims = [c for c in claims if c.field_path == "title"]
        assert len(title_claims) == 1
        assert title_claims[0].severity == Severity.HIGH

    def test_multiple_default_strings(self, validator):
        """Custom validator con strings adicionales."""
        custom_strings = ["My WordPress Blog", "Sitio en construcción"]
        custom_validator = MetadataValidator(default_strings=custom_strings)
        
        html = '<html><head><title>Sitio en construcción</title><meta name="description" content="Hotel boutique"></head><body></body></html>'
        
        claims = custom_validator.analyze(html, "https://hotel.com")
        
        title_claims = [c for c in claims if c.field_path == "title"]
        assert len(title_claims) == 1
        assert title_claims[0].severity == Severity.CRITICAL
        assert "Sitio en construcción" in title_claims[0].message
