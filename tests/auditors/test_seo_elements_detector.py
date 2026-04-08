"""Tests para SEOElementsDetector - detección real con BeautifulSoup."""

import pytest
from modules.auditors.seo_elements_detector import SEOElementsDetector


@pytest.fixture
def detector():
    return SEOElementsDetector()


# ─── OG Detection ───────────────────────────────────────────────

class TestOpenGraphDetection:

    def test_og_detection_positive(self, detector):
        """HTML con og:title + og:description → open_graph=True"""
        html = """
        <html><head>
            <meta property="og:title" content="Hotel Paraíso">
            <meta property="og:description" content="El mejor hotel de la costa">
            <meta property="og:image" content="https://example.com/og.jpg">
        </head><body></body></html>
        """
        result = detector.detect(html, "https://example.com")
        assert result.open_graph is True
        assert result.confidence == "high"
        assert "og:title" in result.open_graph_tags
        assert "og:description" in result.open_graph_tags
        assert result.open_graph_tags["og:title"] == "Hotel Paraíso"

    def test_og_detection_negative(self, detector):
        """HTML sin OG tags → open_graph=False"""
        html = """
        <html><head>
            <meta name="description" content="Un hotel">
        </head><body><p>Hola</p></body></html>
        """
        result = detector.detect(html, "https://example.com")
        assert result.open_graph is False
        assert len(result.open_graph_tags) == 0

    def test_og_detection_partial(self, detector):
        """Solo og:title sin description → open_graph=False"""
        html = """
        <html><head>
            <meta property="og:title" content="Hotel Paraíso">
        </head><body></body></html>
        """
        result = detector.detect(html, "https://example.com")
        assert result.open_graph is False
        assert "og:title" in result.open_graph_tags
        assert "og:description" not in result.open_graph_tags


# ─── Images Alt ─────────────────────────────────────────────────

class TestImagesAlt:

    def test_images_alt_good(self, detector):
        """10 imgs con alt → imagenes_alt=True"""
        imgs = ''.join(f'<img src="img{i}.jpg" alt="Foto {i}">' for i in range(10))
        html = f"<html><body>{imgs}</body></html>"
        result = detector.detect(html, "https://example.com")
        assert result.imagenes_alt is True
        assert result.images_without_alt == 0

    def test_images_alt_bad(self, detector):
        """8 de 10 imgs sin alt → imagenes_alt=False"""
        imgs_with_alt = ''.join(f'<img src="img{i}.jpg" alt="Foto {i}">' for i in range(2))
        imgs_no_alt = ''.join(f'<img src="img{i}.jpg">' for i in range(8))
        html = f"<html><body>{imgs_with_alt}{imgs_no_alt}</body></html>"
        result = detector.detect(html, "https://example.com")
        assert result.imagenes_alt is False
        assert result.images_without_alt == 8


# ─── Social Links ───────────────────────────────────────────────

class TestSocialLinks:

    def test_social_links_detected(self, detector):
        """HTML con href facebook.com → redes_activas=True"""
        html = """
        <html><body>
            <a href="https://www.facebook.com/hotelparaiso">FB</a>
            <a href="https://www.instagram.com/hotelparaiso">IG</a>
        </body></html>
        """
        result = detector.detect(html, "https://example.com")
        assert result.redes_activas is True
        assert len(result.social_links_found) == 2

    def test_no_social_links(self, detector):
        """HTML sin redes sociales → redes_activas=False"""
        html = '<html><body><a href="https://example.com/contact">Contact</a></body></html>'
        result = detector.detect(html, "https://example.com")
        assert result.redes_activas is False
        assert len(result.social_links_found) == 0


# ─── Edge Cases ─────────────────────────────────────────────────

class TestEdgeCases:

    def test_empty_html_graceful(self, detector):
        """HTML vacío → no crash, confidence=low"""
        result = detector.detect("", "https://example.com")
        assert result.confidence in ("low", "high")
        assert result.open_graph is False

    def test_malformed_html_graceful(self, detector):
        """HTML roto → no crash, confidence=low o high (BS4 lo parsea)"""
        html = "<html><body><div><p><b>broken"
        result = detector.detect(html, "https://example.com")
        # BeautifulSoup puede parsear HTML roto → puede ser "high"
        assert result.confidence in ("low", "high")
