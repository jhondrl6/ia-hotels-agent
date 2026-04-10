"""Test de regresion: HTML ilegible nunca debe generar diagnosticos falsos.
Caso original: Brotli encoding no decodificado producia basura binaria que
el pipeline trataba como HTML valido, generando falsos positivos en brechas.
"""
import pytest


class TestHtmlIntegrity:
    """Valida _validate_html_integrity contra escenarios de HTML corrupto."""

    @pytest.fixture
    def auditor(self):
        from modules.auditors.v4_comprehensive import V4ComprehensiveAuditor
        return V4ComprehensiveAuditor.__new__(V4ComprehensiveAuditor)

    def test_brotli_binary_rejected(self, auditor):
        """HTML binario (Brotli sin decodificar) debe rechazarse."""
        # Simula basura binaria real del bug original
        binary_html = '\x1f\x8b\x08\x00\x00\x00\x00\x00' + 'A' * 500
        assert auditor._validate_html_integrity(binary_html, 'https://test.com') is False

    def test_empty_html_rejected(self, auditor):
        """HTML vacio o muy corto debe rechazarse."""
        assert auditor._validate_html_integrity('', 'https://test.com') is False
        assert auditor._validate_html_integrity('<p>hi</p>', 'https://test.com') is False

    def test_valid_html_accepted(self, auditor):
        """HTML real debe aceptarse."""
        valid = '<!DOCTYPE html><html><head><title>Test Hotel Website</title></head><body><div class="content"><h1>Welcome to Our Hotel</h1><p>Experience luxury accommodations with stunning views and exceptional service.</p></div></body></html>'
        assert auditor._validate_html_integrity(valid, 'https://test.com') is True

    def test_html_with_joinchat_accepted(self, auditor):
        """HTML con plugin Joinchat debe aceptarse (caso amaziliahotel.com)."""
        html = '<!DOCTYPE html><html><body><div class="joinchat" data-settings=\'{"telephone":"573104019049"}\'></div><div class="content"><h1>Amazili Hotel</h1><p>Welcome to our hotel in the coffee region.</p></div></body></html>'
        assert auditor._validate_html_integrity(html, 'https://test.com') is True

    def test_error_page_rejected(self, auditor):
        """Pagina de error/redirect sin estructura debe rechazarse."""
        # Cloudflare challenge page (JavaScript only, sin HTML real)
        js_only = '<script>challenge_platform()</script>' + 'x' * 500
        assert auditor._validate_html_integrity(js_only, 'https://test.com') is False
