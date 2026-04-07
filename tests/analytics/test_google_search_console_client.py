"""
Tests para GoogleSearchConsoleClient.

Usa mocks - NO credenciales reales.
"""

import os
import sys
from unittest.mock import MagicMock, patch, mock_open
from datetime import datetime

import pytest

# Agregar project root al path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from modules.analytics.google_search_console_client import (
    GoogleSearchConsoleClient,
    GSCQueryData,
    GSCPageData,
    GSCReport,
    SCOPES,
)


class TestGSCQueryData:
    """Tests para la dataclass GSCQueryData."""

    def test_opportunity_score_high_impressions_low_ctr(self):
        """Query con alta impresion y bajo CTR = alto opportunity_score."""
        q = GSCQueryData(
            query="hotel bogota",
            clicks=10,
            impressions=10000,
            ctr=0.1,
            position=15.0,
        )
        # Expected: 10000 * (1 - 0.1/100) = 10000 * 0.999 = 9990.0
        assert q.opportunity_score > 9000

    def test_opportunity_score_zero_impressions(self):
        """Query sin impresiones = 0 opportunity_score."""
        q = GSCQueryData(query="obscure query", clicks=0, impressions=0, ctr=0.0, position=0.0)
        assert q.opportunity_score == 0.0


class TestGSCPageData:
    """Tests para la dataclass GSCPageData."""

    def test_page_data_creation(self):
        """Test que la dataclass se crea correctamente."""
        page = GSCPageData(
            url="https://example.com/page",
            clicks=50,
            impressions=500,
            ctr=10.0,
            position=3.2,
        )
        assert page.url == "https://example.com/page"
        assert page.clicks == 50
        assert page.impressions == 500


class TestGSCReport:
    """Tests para la dataclass GSCReport."""

    def test_default_not_available(self):
        """Report por defecto no esta disponible."""
        report = GSCReport()
        assert report.is_available is False

    def test_to_dict(self):
        """Test serializacion a dict."""
        report = GSCReport(
            is_available=True,
            start_date="2025-01-01",
            end_date="2025-01-30",
            total_clicks=100,
            total_impressions=5000,
            avg_ctr=2.0,
            avg_position=10.5,
            queries=[GSCQueryData(query="test", clicks=10, impressions=100, ctr=10.0, position=5.0)],
            pages=[],
        )
        d = report.to_dict()
        assert d["is_available"] is True
        assert d["total_clicks"] == 100
        assert d["total_impressions"] == 5000
        assert d["query_count"] == 1


class TestGoogleSearchConsoleClient:
    """Tests para GoogleSearchConsoleClient."""

    def test_not_configured_no_credentials(self):
        """Sin credenciales no esta configurado."""
        client = GoogleSearchConsoleClient(credentials_path=None, site_url=None)
        assert client.is_configured() is False

    def test_not_configured_no_site_url(self):
        """Con credenciales pero sin site_url no esta configurado."""
        client = GoogleSearchConsoleClient(
            credentials_path="/fake/path/key.json",
            site_url=None,
        )
        assert client.is_configured() is False

    @patch.object(os.path, "exists", return_value=True)
    def test_configured_with_credentials_and_site_url(self, mock_exists):
        """Con credenciales validas y site_url esta configurado."""
        client = GoogleSearchConsoleClient(
            credentials_path="/fake/path/key.json",
            site_url="https://example.com",
        )
        assert client.is_configured() is True

    @patch.object(os.path, "exists", return_value=True)
    def test_get_search_analytics_without_credentials_returns_empty_report(self, mock_exists):
        """Sin credenciales, get_search_analytics retorna report con is_available=False."""
        client = GoogleSearchConsoleClient(credentials_path=None, site_url=None)
        report = client.get_search_analytics(
            start_date="2025-01-01",
            end_date="2025-01-30",
        )
        assert report.is_available is False
        assert report.error_message is not None

    def test_get_search_analytics_with_nonexistent_credentials(self):
        """Con ruta de credenciales que no existe retorna empty report."""
        client = GoogleSearchConsoleClient(
            credentials_path="/nonexistent/path/key.json",
            site_url="https://example.com",
        )
        report = client.get_search_analytics()
        assert report.is_available is False
        assert "no encontrado" in (report.error_message or "").lower() or report.error_message is not None

    @patch.object(os.path, "exists", return_value=True)
    def test_get_search_analytics_with_mock_api(self, mock_exists):
        """Test con mock de la API real - datos de prueba."""
        # Mock the Google API discovery
        mock_service = MagicMock()
        mock_query_response = {
            'rows': [
                {
                    'keys': ['hotel bogota'],
                    'clicks': 50,
                    'impressions': 5000,
                    'ctr': 0.01,
                    'position': 8.5,
                },
                {
                    'keys': ['hotel medellin'],
                    'clicks': 30,
                    'impressions': 3000,
                    'ctr': 0.01,
                    'position': 12.0,
                },
            ]
        }
        mock_searchanalytics = MagicMock()
        mock_searchanalytics.query.return_value.execute.return_value = mock_query_response
        mock_service.searchanalytics.return_value = mock_searchanalytics

        with patch('googleapiclient.discovery.build', return_value=mock_service):
            with patch('google.oauth2.service_account') as mock_sa:
                mock_creds = MagicMock()
                mock_sa.Credentials.from_service_account_file.return_value = mock_creds

                client = GoogleSearchConsoleClient(
                    credentials_path="/fake/key.json",
                    site_url="https://example.com",
                )
                report = client.get_search_analytics(
                    start_date="2025-01-01",
                    end_date="2025-01-30",
                )

                assert report.is_available is True
                assert len(report.queries) == 2
                assert report.total_clicks == 80
                assert report.total_impressions == 8000

    @patch.object(os.path, "exists", return_value=True)
    def test_get_top_opportunities(self, mock_exists):
        """Test identificar oportunidades (alta impresion + bajo CTR)."""
        queries = [
            GSCQueryData(query="a", clicks=500, impressions=10000, ctr=5.0, position=3.0),
            GSCQueryData(query="b", clicks=10, impressions=10000, ctr=0.1, position=15.0),
            GSCQueryData(query="c", clicks=5, impressions=100, ctr=5.0, position=2.0),
        ]
        report = GSCReport(
            is_available=True,
            queries=queries,
        )

        # Sin API mockear, probar directamente con client no configurado
        client = GoogleSearchConsoleClient(
            credentials_path="/fake/key.json",
            site_url="https://example.com",
        )
        # get_top_opportunities no requiere API, solo analiza datos
        opportunities = client.get_top_opportunities(report, top_n=2)

        assert len(opportunities) == 2
        # "b" debe ser top opportunity (alta impresion, bajo CTR)
        assert opportunities[0].query == "b"
        # "a" debe ser segunda (aunque CTR alto, tiene mucho volumen)
        # opportunity_score = impressions * (1 - ctr/100)
        # a: 10000 * 0.95 = 9500
        # b: 10000 * 0.999 = 9990
        # c: 100 * 0.95 = 95
        assert opportunities[0].opportunity_score > opportunities[1].opportunity_score

    def test_get_top_opportunities_empty_report(self):
        """Report sin datos retorna lista vacia."""
        client = GoogleSearchConsoleClient()
        report = GSCReport(is_available=False)
        opportunities = client.get_top_opportunities(report)
        assert opportunities == []

    def test_scopes_constant(self):
        """Verificar que el scope es correcto."""
        assert SCOPES == ['https://www.googleapis.com/auth/webmasters.readonly']
