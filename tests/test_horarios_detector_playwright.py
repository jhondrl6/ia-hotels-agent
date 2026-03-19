"""
Tests for HorariosDetectorPlaywright
"""
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
from modules.utils.horarios_detector_playwright import HorariosDetectorPlaywright
from playwright.sync_api import TimeoutError as PlaywrightTimeout


class TestHorariosDetectorPlaywright:
    """Unit tests for HorariosDetectorPlaywright class."""

    @pytest.fixture
    def mock_page(self):
        """Create a mock Playwright Page object."""
        page = MagicMock()
        page.wait_for_selector = MagicMock()
        page.query_selector = MagicMock()
        page.content = MagicMock(return_value='')
        return page

    @pytest.fixture
    def detector(self, mock_page):
        """Create a HorariosDetectorPlaywright instance with mock page."""
        return HorariosDetectorPlaywright(mock_page)

    def test_detect_simple_horarios(self, detector, mock_page):
        """Test detection with simple time range like '9:00 - 18:00'."""
        mock_page.wait_for_selector.side_effect = PlaywrightTimeout("Not found")
        mock_page.query_selector.return_value = None
        mock_page.content.return_value = "Horario de atención: 9:00 - 18:00 de Lunes a Viernes"

        tiene_horarios, confidence, metadata = detector.detect_horarios(timeout=1)

        assert tiene_horarios is True
        assert confidence >= 0.5
        assert metadata['detection_method'] in ['text_analysis', 'css_selector']

    def test_detect_24h_horarios(self, detector, mock_page):
        """Test detection with '24 horas' pattern."""
        mock_page.wait_for_selector.side_effect = PlaywrightTimeout("Not found")
        mock_page.query_selector.return_value = None
        mock_page.content.return_value = "Servicio disponible 24 horas"

        tiene_horarios, confidence, metadata = detector.detect_horarios(timeout=1)

        assert tiene_horarios is True
        assert confidence >= 0.9
        assert metadata['detection_method'] == '24h_detection'

    def test_detect_time_formats(self, detector, mock_page):
        """Test detection of time formats like 'Check-in: 3:00 pm, Check-out: 12:00 pm'."""
        mock_page.wait_for_selector.side_effect = PlaywrightTimeout("Not found")
        mock_page.query_selector.return_value = None
        mock_page.content.return_value = "Check-in: 3:00 pm, Check-out: 12:00 pm"

        tiene_horarios, confidence, metadata = detector.detect_horarios(timeout=1)

        assert tiene_horarios is True
        assert len(metadata['time_formats_found']) > 0

    def test_interface_compatibility_with_selenium(self):
        """Verify interface is compatible with HorariosDetector (Selenium)."""
        from modules.utils.horarios_detector import HorariosDetector

        selenium_methods = set(
            m for m in dir(HorariosDetector) 
            if not m.startswith('_') and callable(getattr(HorariosDetector, m))
        )
        playwright_methods = set(
            m for m in dir(HorariosDetectorPlaywright) 
            if not m.startswith('_') and callable(getattr(HorariosDetectorPlaywright, m))
        )

        critical_methods = {'detect_horarios'}
        for method in critical_methods:
            assert method in selenium_methods
            assert method in playwright_methods

    def test_return_type_tuple(self, detector, mock_page):
        """Verify return type is Tuple[bool, float, dict]."""
        mock_page.wait_for_selector.side_effect = PlaywrightTimeout("Not found")
        mock_page.query_selector.return_value = None
        mock_page.content.return_value = "No schedule info"

        result = detector.detect_horarios(timeout=1)

        assert isinstance(result, tuple)
        assert len(result) == 3
        assert isinstance(result[0], bool)
        assert isinstance(result[1], float)
        assert isinstance(result[2], dict)

    def test_timeout_respected(self, detector, mock_page):
        """Verify timeout parameter is passed to wait_for_selector."""
        mock_page.wait_for_selector.side_effect = PlaywrightTimeout("Timeout")
        mock_page.query_selector.return_value = None
        mock_page.content.return_value = "No schedule"

        detector.detect_horarios(timeout=2)

        for call in mock_page.wait_for_selector.call_args_list:
            assert call[1].get('timeout') == 2000

    def test_css_selector_detection(self, detector, mock_page):
        """Test detection via CSS selector."""
        mock_element = MagicMock()
        mock_element.text_content.return_value = "Horario: 9am - 6pm"
        mock_element.get_attribute.return_value = "Horario de atención"
        mock_page.wait_for_selector.return_value = mock_element

        tiene_horarios, confidence, metadata = detector.detect_horarios(timeout=1)

        assert tiene_horarios is True
        assert metadata['detection_method'] == 'css_selector'

    def test_no_horarios_detected(self, detector, mock_page):
        """Test when no horarios information is present."""
        mock_page.wait_for_selector.side_effect = PlaywrightTimeout("Not found")
        mock_page.query_selector.return_value = None
        mock_page.content.return_value = "This is a random page without any schedule information."

        tiene_horarios, confidence, metadata = detector.detect_horarios(timeout=1)

        assert tiene_horarios is False
        assert confidence == 0.0
        assert metadata['detection_method'] == 'not_found'

    def test_keywords_extraction(self, detector):
        """Test keyword extraction from text."""
        keywords = detector._extract_matched_keywords(
            "Horario de entrada: 3pm. Horario de salida: 12pm"
        )

        assert len(keywords) > 0
        assert any(k in ['horario', 'entrada', 'salida'] for k in keywords)

    def test_24h_pattern_detection(self, detector):
        """Test 24h pattern detection."""
        detector.detection_evidence = []

        assert detector._detect_always_open("Recepción 24 horas") is True
        assert detector._detect_always_open("Open 24/7") is True
        assert detector._detect_always_open("24h service") is True
        assert detector._detect_always_open("Horario: 9am - 6pm") is False

    def test_confidence_with_multiple_time_formats(self, detector, mock_page):
        """Test confidence increases with multiple time formats."""
        mock_page.wait_for_selector.side_effect = PlaywrightTimeout("Not found")
        mock_page.query_selector.return_value = None
        mock_page.content.return_value = (
            "Lunes a Viernes: 9:00 am - 6:00 pm\n"
            "Sábados: 10:00 am - 2:00 pm\n"
            "Domingos: Cerrado"
        )

        tiene_horarios, confidence, metadata = detector.detect_horarios(timeout=1)

        assert tiene_horarios is True
        assert confidence >= 0.5
        assert len(metadata['time_formats_found']) >= 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
