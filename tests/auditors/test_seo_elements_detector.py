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


# ─── SPA Rendering (FASE-4: BUG-6) ──────────────────────────────

class TestSPARendering:

    @pytest.fixture
    def auditor(self):
        from modules.auditors.v4_comprehensive import V4ComprehensiveAuditor
        return V4ComprehensiveAuditor()

    def test_is_spa_detection_true(self, auditor):
        """SPA app shell (scripts, no meta, no OG) → _is_spa=True"""
        spa_html = """<!doctype html>
        <html lang="en">
        <head>
            <script src="app.js"></script>
        </head>
        <body><div id="root"></div></body>
        </html>"""
        assert auditor._is_spa(spa_html) is True

    def test_is_spa_detection_false_with_og(self, auditor):
        """HTML with OG tags → _is_spa=False"""
        normal_html = """<html><head>
            <meta charset="utf-8">
            <meta property="og:title" content="Hotel Test">
            <meta property="og:description" content="A test hotel">
        </head><body></body></html>"""
        assert auditor._is_spa(normal_html) is False

    def test_is_spa_detection_false_many_meta(self, auditor):
        """HTML with many meta tags (not SPA) → _is_spa=False"""
        rich_html = """<html><head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width">
            <meta name="description" content="A hotel website">
            <meta name="keywords" content="hotel, luxury">
        </head><body><p>Welcome to Hotel Test</p></body></html>"""
        assert auditor._is_spa(rich_html) is False

    def test_is_spa_detection_empty(self, auditor):
        """Empty HTML → _is_spa=False (no crash)"""
        assert auditor._is_spa("") is False

    def test_render_with_playwright_mock(self, auditor):
        """Mock _render_with_playwright → rendered HTML with OG tags is used by _run_seo_elements_audit."""
        RENDERED_HTML = """<html><head>
            <meta property="og:title" content="Luxor Hotel">
            <meta property="og:description" content="Beachfront luxury">
        </head><body><h1>Luxor Hotel</h1></body></html>"""

        # Patch the _render_with_playwright method to return our rendered HTML
        original = auditor._render_with_playwright
        auditor._render_with_playwright = lambda url, timeout=15000: RENDERED_HTML

        try:
            # SPA HTML that would trigger Playwright rendering
            spa_html = '<html><head><script src="app.js"></script></head><body></body></html>'
            result = auditor._run_seo_elements_audit(spa_html, "https://luxorhotel.com.co")
            # The rendered HTML has OG tags → open_graph should be True
            assert result.open_graph is True
            assert result.confidence == "high"
            assert "og:title" in result.open_graph_tags
            assert result.open_graph_tags["og:title"] == "Luxor Hotel"
        finally:
            auditor._render_with_playwright = original

    def test_fallback_when_playwright_fails(self, auditor):
        """_render_with_playwright returns None → fallback to static BeautifulSoup (no crash)."""
        # Patch _render_with_playwright to simulate failure
        original = auditor._render_with_playwright
        auditor._render_with_playwright = lambda url, timeout=15000: None

        try:
            static_html = """<html><head>
                <meta name="description" content="A hotel">
            </head><body><p>Welcome</p></body></html>"""

            result = auditor._run_seo_elements_audit(static_html, "https://example.com")
            # Should not crash; result reflects static HTML
            assert result.open_graph is False  # No OG in static HTML
            assert result.confidence in ("low", "high")
        finally:
            auditor._render_with_playwright = original

    def test_fallback_non_spa_skips_playwright(self, auditor):
        """Non-SPA HTML bypasses Playwright entirely (_render_with_playwright never called)."""
        call_count = [0]

        def counting_render(url, timeout=15000):
            call_count[0] += 1
            return "<html></html>"

        original = auditor._render_with_playwright
        auditor._render_with_playwright = counting_render

        try:
            # Normal HTML with meta tags and OG → not detected as SPA
            normal_html = """<html><head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width">
                <meta property="og:title" content="Hotel Normal">
                <meta property="og:description" content="A normal hotel site">
            </head><body></body></html>"""

            result = auditor._run_seo_elements_audit(normal_html, "https://example.com")
            assert result.open_graph is True
            assert call_count[0] == 0  # Playwright never called
        finally:
            auditor._render_with_playwright = original
