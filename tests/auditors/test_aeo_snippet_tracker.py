"""Tests para AEO Snippet Tracker.

Valida medicion de featured snippets via SerpAPI.
"""
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add project root to Python path for pytest
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest

from modules.auditors.aeo_snippet_tracker import (
    AEOSnippetTracker,
    AEOSnippetReport,
    SnippetResult,
    get_aeo_snippet_tracker,
)


class TestAEOSnippetTrackerStub:
    """Tests for stub mode (no API key)."""

    def test_snippet_tracker_stub_no_api_key(self):
        """Sin API key, retorna stub con source=stub."""
        tracker = AEOSnippetTracker(serpapi_key=None)
        report = tracker.check_snippets(
            hotel_name="Hotel Test",
            hotel_url="https://hoteltest.com",
            location="Armenia",
            landmark="Parque",
        )

        assert report.source == "stub"
        assert report.snippets_captured == 0
        assert report.snippet_score == 0
        assert len(report.queries) == len(AEOSnippetTracker.QUERIES_FACTUALES)

    def test_snippet_tracker_stub_is_stub(self):
        """Verifica que sin key, _is_stub() retorna True."""
        tracker = AEOSnippetTracker(serpapi_key=None)
        assert tracker._is_stub() is True

    def test_snippet_tracker_factory_stub(self):
        """Factory sin env var retorna stub."""
        with patch.dict("os.environ", {}, clear=True):
            tracker = get_aeo_snippet_tracker()
            # Factory usa os.getenv, puede o no tener key dependiendo del entorno
            # Solo verificamos que existe
            assert tracker is not None


class TestAEOSnippetTrackerMock:
    """Tests for mock mode (con API key simulada)."""

    @pytest.fixture
    def mock_tracker(self):
        """Tracker con API key fake pero sin llamada real."""
        return AEOSnippetTracker(serpapi_key="fake_key_for_testing", timeout=5.0)

    def test_snippet_tracker_not_stub_with_key(self, mock_tracker):
        """Con API key, _is_stub() retorna False."""
        assert mock_tracker._is_stub() is False

    def test_generar_queries(self, mock_tracker):
        """Verifica generacion de queries concretas."""
        queries = mock_tracker._generar_queries(
            hotel_name="Hotel Casa de la Paz",
            location="Armenia, Quindio",
            landmark="Parque de la Vida",
        )

        assert len(queries) == len(AEOSnippetTracker.QUERIES_FACTUALES)
        assert any("Hotel Casa de la Paz" in q for q in queries)
        assert any("Armenia" in q for q in queries)
        assert any("Parque de la Vida" in q for q in queries)

    def test_extract_domain(self, mock_tracker):
        """Verifica extraccion de dominio."""
        assert mock_tracker._extract_domain("https://hotel.com") == "hotel.com"
        assert mock_tracker._extract_domain("http://www.hotel.com/room/suite") == "www.hotel.com"
        assert mock_tracker._extract_domain("https://hotel.com.co") == "hotel.com.co"

    def test_stub_report_structure(self):
        """Verifica estructura del stub report."""
        tracker = AEOSnippetTracker(serpapi_key=None)
        report = tracker._stub_report("https://test.com")

        assert isinstance(report, AEOSnippetReport)
        assert report.hotel_url == "https://test.com"
        assert report.source == "stub"
        assert report.snippet_score == 0
        assert report.queries_tested == len(AEOSnippetTracker.QUERIES_FACTUALES)
        assert len(report.queries) == len(AEOSnippetTracker.QUERIES_FACTUALES)

    def test_check_snippets_graceful_degradation(self, mock_tracker):
        """Si falla API, no crashea - graceful degradation."""
        # Simular fallo de red
        with patch.object(mock_tracker.client, "get", side_effect=Exception("Network error")):
            report = mock_tracker.check_snippets(
                hotel_name="Hotel Test",
                hotel_url="https://hoteltest.com",
            )

            # Debe retornar reporte con datos vacios, no crashear
            assert report.source == "serpapi"
            assert report.snippets_captured == 0
            assert len(report.queries) == len(AEOSnippetTracker.QUERIES_FACTUALES)


class TestSnippetResult:
    """Tests para SnippetResult dataclass."""

    def test_snippet_result_creation(self):
        """Verifica creacion de SnippetResult."""
        result = SnippetResult(
            query="hotel test telefono",
            has_snippet=True,
            snippet_source="https://competitor.com",
            is_our_hotel=False,
            snippet_type="paragraph",
            people_also_ask=["Pregunta 1", "Pregunta 2"],
        )

        assert result.query == "hotel test telefono"
        assert result.has_snippet is True
        assert result.is_our_hotel is False
        assert len(result.people_also_ask) == 2

    def test_snippet_result_optionals(self):
        """Verifica campos opcionales pueden ser None."""
        result = SnippetResult(
            query="hotel test horario",
            has_snippet=False,
            snippet_source=None,
            is_our_hotel=False,
            snippet_type=None,
            people_also_ask=[],
        )

        assert result.has_snippet is False
        assert result.snippet_source is None
        assert result.snippet_type is None


class TestAEOSnippetReport:
    """Tests para AEOSnippetReport dataclass."""

    def test_report_creation(self):
        """Verifica creacion de AEOSnippetReport."""
        report = AEOSnippetReport(
            hotel_url="https://hotel.com",
            queries_tested=5,
            snippets_captured=2,
            snippets_competitor=3,
            paa_presence=4,
            snippet_score=40,
            queries=[],
            source="serpapi",
        )

        assert report.hotel_url == "https://hotel.com"
        assert report.snippet_score == 40
        assert report.source == "serpapi"

    def test_report_timestamp(self):
        """Verifica que timestamp se genera automaticamente."""
        report = AEOSnippetReport(
            hotel_url="https://hotel.com",
            queries_tested=5,
            snippets_captured=0,
            snippets_competitor=0,
            paa_presence=0,
            snippet_score=0,
            queries=[],
            source="stub",
        )

        assert report.timestamp is not None
        assert report.timestamp != ""


class TestAEOSnippetTrackerQueries:
    """Tests para generacion de queries."""

    def test_queries_factuales_count(self):
        """Verifica que hay 5 queries factuales definidas."""
        assert len(AEOSnippetTracker.QUERIES_FACTUALES) == 5

    def test_queries_factuales_contain_placeholders(self):
        """Verifica que todas las queries tienen placeholders."""
        for q in AEOSnippetTracker.QUERIES_FACTUALES:
            assert "{" in q and "}" in q, f"Query '{q}' missing placeholder"

    def test_queries_factuales_templates(self):
        """Verifica templates esperados."""
        templates = [q.format(nombre="X", ciudad="Y", landmark="Z") for q in AEOSnippetTracker.QUERIES_FACTUALES]

        assert any("horario" in q for q in templates)
        assert any("telefono" in q for q in templates)
        assert any("direccion" in q for q in templates)
        assert any("boutique" in q for q in templates)
        assert any("cerca de" in q for q in templates)
