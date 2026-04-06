"""Tests para SEOElementsDetector.

Valida detección de elementos SEO en contenido HTML.
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest

from modules.auditors.seo_elements_detector import (
    SEOElementsDetector,
    SEOElementsResult,
)


@pytest.fixture
def detector():
    """Fixture que proporciona una instancia de SEOElementsDetector."""
    return SEOElementsDetector()


@pytest.fixture
def sample_html():
    """Sample HTML content with SEO elements for testing."""
    return """
    <html>
    <head>
        <title>Hotel Visperas - Servicios y Habitaciones</title>
        <meta name="description" content="Hotel Visperas ofrece servicios de primera clase">
        <meta name="keywords" content="hotel, reservas, piscina, restaurante">
    </head>
    <body>
        <h1>Bienvenidos al Hotel Visperas</h1>
        <h2>Nuestros Servicios</h2>
        <img src="img/hotel.jpg" alt="Fachada del hotel">
        <a href="/habitaciones">Ver habitaciones</a>
    </body>
    </html>
    """


@pytest.fixture
def html_missing_seo():
    """HTML content missing SEO elements."""
    return """
    <html>
    <body>
        <h1>Content</h1>
        <p>Some text here.</p>
    </body>
    </html>
    """


class TestSEOElementsDetector:
    """Tests for SEOElementsDetector class."""

    def test_detector_basic(self, detector, sample_html):
        """Test that detector returns SEOElementsResult."""
        result = detector.analyze(sample_html, "https://example.com")
        
        assert isinstance(result, SEOElementsResult)
        assert 0 <= result.score <= 100

    def test_detector_score_types(self, detector, sample_html):
        """Test that all score fields are numeric."""
        result = detector.analyze(sample_html, "https://example.com")
        
        assert isinstance(result.score, (int, float))
        assert isinstance(result.title_score, (int, float))
        assert isinstance(result.meta_description_score, (int, float))
        assert isinstance(result.headings_score, (int, float))
        assert isinstance(result.images_score, (int, float))
        assert isinstance(result.links_score, (int, float))

    def test_detector_has_recommendations(self, detector, sample_html):
        """Test that recommendations are generated."""
        result = detector.analyze(sample_html, "https://example.com")
        
        assert isinstance(result.recommendations, list)
        assert all(isinstance(r, str) for r in result.recommendations)

    def test_detector_elements_found(self, detector, sample_html):
        """Test that elements_found dict is populated."""
        result = detector.analyze(sample_html, "https://example.com")
        
        assert isinstance(result.elements_found, dict)

    def test_detector_missing_seo(self, detector, html_missing_seo):
        """Test detection when SEO elements are missing."""
        result = detector.analyze(html_missing_seo, "https://example.com")
        
        assert result.score < 100
        assert len(result.recommendations) > 0

    def test_detector_empty_html(self, detector):
        """Test handling of empty/minimal HTML."""
        result = detector.analyze("<html><body></body></html>", "https://example.com")
        
        assert isinstance(result, SEOElementsResult)
        assert result.score == 0

    def test_seo_elements_result_creation(self):
        """Test SEOElementsResult dataclass creation."""
        result = SEOElementsResult(
            score=75.0,
            title_score=80.0,
            meta_description_score=70.0,
            headings_score=90.0,
            images_score=60.0,
            links_score=85.0,
            elements_found={"title": True, "meta_description": True},
            recommendations=["Add alt text to images"],
        )
        
        assert result.score == 75.0
        assert result.title_score == 80.0
        assert result.elements_found["title"] is True

    def test_analyze_method_exists(self, detector):
        """Test that analyze method exists and is callable."""
        assert hasattr(detector, "analyze")
        assert callable(getattr(detector, "analyze"))

    def test_seo_elements_detector_returns_stub_values(self, detector):
        """Test that detector returns stub values when implementation is missing."""
        result = detector.analyze("<html><body>Test</body></html>", "https://example.com")
        
        # Stub values should be returned (TDD RED phase - implementation missing)
        assert result.score is not None
        assert result.title_score is not None
        assert result.meta_description_score is not None
        assert result.headings_score is not None
        assert result.images_score is not None
        assert result.links_score is not None

    def test_detect_returns_seo_elements_result_with_false_values(self, detector):
        """Test that detect method returns SEOElementsResult with false/missing values."""
        result = detector.detect("<html><body>No SEO elements</body></html>", "https://example.com")
        
        # Should return SEOElementsResult with False values for missing elements
        assert isinstance(result, SEOElementsResult)
        assert result.elements_found.get("title") is False
        assert result.elements_found.get("meta_description") is False
        assert result.elements_found.get("h1") is False

    def test_confidence_is_estimated(self, detector):
        """Test that confidence score is estimated based on element presence."""
        result = detector.analyze("<html><body>Minimal content</body></html>", "https://example.com")
        
        # Confidence should be estimated (between 0 and 1)
        assert hasattr(result, "confidence")
        assert isinstance(result.confidence, (int, float))
        assert 0.0 <= result.confidence <= 1.0
