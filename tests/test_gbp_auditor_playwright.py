"""
Tests for GBPAuditorPlaywright - Interface compatibility with Selenium version.
"""
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest


class TestGBPAuditorPlaywrightInterface:
    """Test interface compatibility with GBPAuditor (Selenium)."""

    def test_same_public_methods(self):
        """Both classes should expose the same public methods."""
        from modules.scrapers.gbp_auditor import GBPAuditor
        from modules.scrapers.gbp_auditor_playwright import GBPAuditorPlaywright

        selenium_methods = set(m for m in dir(GBPAuditor) if not m.startswith('_') and callable(getattr(GBPAuditor, m)))
        playwright_methods = set(m for m in dir(GBPAuditorPlaywright) if not m.startswith('_') and callable(getattr(GBPAuditorPlaywright, m)))

        # Check critical public methods exist in both
        critical_methods = {
            'check_google_profile',
            'audit_competitor_profile',
            'generar_reporte_ejecutivo',
            'get_competitor_score',
            'calculate_gbp_activity_score_detailed',
            'validate_location_only',
        }

        for method in critical_methods:
            assert method in selenium_methods, f"Missing in Selenium: {method}"
            assert method in playwright_methods, f"Missing in Playwright: {method}"

    def test_same_constants(self):
        """Both classes should have the same class constants."""
        from modules.scrapers.gbp_auditor import GBPAuditor
        from modules.scrapers.gbp_auditor_playwright import GBPAuditorPlaywright

        assert GBPAuditor.PERDIDA_MENSUAL_BASE == GBPAuditorPlaywright.PERDIDA_MENSUAL_BASE
        assert GBPAuditor.CACHE_MAX_AGE_DAYS == GBPAuditorPlaywright.CACHE_MAX_AGE_DAYS
        assert GBPAuditor.IMPACTOS_FINANCIEROS == GBPAuditorPlaywright.IMPACTOS_FINANCIEROS

    def test_base_profile_structure(self):
        """Both classes should return the same profile structure."""
        from modules.scrapers.gbp_auditor import GBPAuditor
        from modules.scrapers.gbp_auditor_playwright import GBPAuditorPlaywright

        selenium_profile = GBPAuditor(headless=True)._base_profile()
        playwright_profile = GBPAuditorPlaywright(headless=True)._base_profile()

        assert set(selenium_profile.keys()) == set(playwright_profile.keys())

        # Check default values match
        for key in selenium_profile:
            assert selenium_profile[key] == playwright_profile[key], f"Mismatch for key: {key}"

    def test_static_methods_compatibility(self):
        """Static methods should produce identical results."""
        from modules.scrapers.gbp_auditor import GBPAuditor
        from modules.scrapers.gbp_auditor_playwright import GBPAuditorPlaywright

        selenium_auditor = GBPAuditor(headless=True)
        playwright_auditor = GBPAuditorPlaywright(headless=True)

        # Test _parse_int
        assert selenium_auditor._parse_int("1.5k") == playwright_auditor._parse_int("1.5k")
        assert selenium_auditor._parse_int("500") == playwright_auditor._parse_int("500")
        assert selenium_auditor._parse_int("2mil") == playwright_auditor._parse_int("2mil")

        # Test _parse_float
        assert selenium_auditor._parse_float("4.5") == playwright_auditor._parse_float("4.5")
        assert selenium_auditor._parse_float("3,5") == playwright_auditor._parse_float("3,5")

        # Test _build_cache_key
        assert selenium_auditor._build_cache_key("Hotel ABC", "Cartagena") == \
               playwright_auditor._build_cache_key("Hotel ABC", "Cartagena")

    def test_severity_calculation(self):
        """Severity calculation should match."""
        from modules.scrapers.gbp_auditor import GBPAuditor
        from modules.scrapers.gbp_auditor_playwright import GBPAuditorPlaywright

        test_values = [1_000_000, 600_000, 400_000, 100_000]

        for val in test_values:
            selenium_severity = GBPAuditor(headless=True)._calcular_severidad(val)
            playwright_severity = GBPAuditorPlaywright(headless=True)._calcular_severidad(val)
            assert selenium_severity == playwright_severity, f"Mismatch for value: {val}"


class TestGBPAuditorPlaywrightActivityScore:
    """Test Activity Score calculation for Playwright version."""

    def _create_mock_auditor(self, pesos=None):
        """Create a mock GBPAuditorPlaywright with configurable weights."""
        from modules.scrapers.gbp_auditor_playwright import GBPAuditorPlaywright

        auditor = GBPAuditorPlaywright.__new__(GBPAuditorPlaywright)
        auditor.benchmark_loader = MagicMock()

        default_pesos = {
            'posts_90d_peso': 0.35,
            'posts_90d_max': 5,
            'fotos_mes_peso': 0.25,
            'fotos_meta': 15,
            'reviews_response_peso': 0.40,
        }
        auditor.benchmark_loader.get_activity_weights.return_value = pesos or default_pesos
        return auditor

    def test_hotel_visperas_case(self):
        """Hotel Vísperas: 0 posts, 9 fotos, no response data -> should be ~15/100."""
        auditor = self._create_mock_auditor()

        profile_data = {
            'posts': 0,
            'fotos': 9,
            'reviews': 29,
            'meta': {}
        }

        score = auditor._calcular_activity_score(profile_data)

        assert score == 15, f"Expected 15, got {score}"

    def test_active_hotel(self):
        """Hotel with good activity: 5 posts, 20 fotos, 50% response rate."""
        auditor = self._create_mock_auditor()

        profile_data = {
            'posts': 5,
            'fotos': 20,
            'reviews': 10,
            'meta': {
                'reviews': {
                    'responded': 5,
                    'total': 10
                }
            }
        }

        score = auditor._calcular_activity_score(profile_data)

        assert score == 80, f"Expected 80, got {score}"

    def test_perfect_activity(self):
        """Hotel with perfect activity: max posts, max fotos, 100% responses."""
        auditor = self._create_mock_auditor()

        profile_data = {
            'posts': 5,
            'fotos': 15,
            'reviews': 10,
            'meta': {
                'reviews': {
                    'responded': 10,
                    'total': 10
                }
            }
        }

        score = auditor._calcular_activity_score(profile_data)

        assert score == 100, f"Expected 100, got {score}"

    def test_fallback_when_no_weights(self):
        """Should return 100 when benchmark weights are not available."""
        auditor = self._create_mock_auditor(pesos=None)
        auditor.benchmark_loader.get_activity_weights.return_value = None

        profile_data = {'posts': 0, 'fotos': 0}

        score = auditor._calcular_activity_score(profile_data)

        assert score == 100, f"Expected fallback 100, got {score}"


class TestHorariosDetectorPlaywright:
    """Test HorariosDetectorPlaywright functionality."""

    def test_keywords_defined(self):
        """Keywords should be defined for detection."""
        from modules.scrapers.gbp_auditor_playwright import HorariosDetectorPlaywright

        assert len(HorariosDetectorPlaywright.KEYWORDS_HORARIOS) > 0
        assert len(HorariosDetectorPlaywright.STRONG_KEYWORDS) > 0
        assert len(HorariosDetectorPlaywright.TIME_PATTERNS) > 0
        assert len(HorariosDetectorPlaywright.CSS_SELECTORS) > 0

    def test_time_pattern_detection(self):
        """Time patterns should be correctly extracted."""
        from modules.scrapers.gbp_auditor_playwright import HorariosDetectorPlaywright

        detector = HorariosDetectorPlaywright.__new__(HorariosDetectorPlaywright)

        times = detector._extract_time_formats("Check-in: 3:00 p.m. Check-out: 12:00 p.m.")
        assert len(times) > 0

    def test_keyword_extraction(self):
        """Keywords should be correctly extracted from text."""
        from modules.scrapers.gbp_auditor_playwright import HorariosDetectorPlaywright

        detector = HorariosDetectorPlaywright.__new__(HorariosDetectorPlaywright)

        keywords = detector._extract_matched_keywords("Horario de entrada: 3pm. Horario de salida: 12pm")
        assert 'horario' in keywords or 'entrada' in keywords or 'salida' in keywords

    def test_24h_detection(self):
        """24h patterns should be detected."""
        from modules.scrapers.gbp_auditor_playwright import HorariosDetectorPlaywright

        detector = HorariosDetectorPlaywright.__new__(HorariosDetectorPlaywright)
        detector.detection_evidence = []

        assert detector._detect_always_open("Recepción 24 horas") is True
        assert detector._detect_always_open("Open 24/7") is True
        assert detector._detect_always_open("Horario: 9am - 6pm") is False


class TestGBPAuditorPlaywrightBrowserLifecycle:
    """Test browser lifecycle management."""

    def test_init_does_not_launch_browser(self):
        """Browser should not be launched on __init__."""
        from modules.scrapers.gbp_auditor_playwright import GBPAuditorPlaywright

        auditor = GBPAuditorPlaywright(headless=True)

        assert auditor.browser is None
        assert auditor.page is None
        assert auditor._driver_status["available"] is False

    def test_close_browser_cleanup(self):
        """_close_browser should clean up all resources."""
        from modules.scrapers.gbp_auditor_playwright import GBPAuditorPlaywright

        auditor = GBPAuditorPlaywright(headless=True)

        # Mock browser objects
        auditor.page = MagicMock()
        auditor.context = MagicMock()
        auditor.browser = MagicMock()
        auditor._playwright = MagicMock()

        auditor._close_browser()

        assert auditor.page is None
        assert auditor.context is None
        assert auditor.browser is None
        assert auditor._playwright is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
