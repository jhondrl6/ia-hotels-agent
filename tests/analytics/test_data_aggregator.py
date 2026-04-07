"""
Tests para AnalyticsAggregator y UnifiedAnalyticsData.

Usa mocks - NO credenciales reales.
"""

import os
import sys
from unittest.mock import MagicMock, patch

import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from modules.analytics.data_aggregator import (
    AnalyticsAggregator,
    UnifiedAnalyticsData,
    ConfidenceLevel,
)
from modules.analytics.google_search_console_client import (
    GSCReport,
    GSCQueryData,
)


class TestUnifiedAnalyticsData:
    """Tests para UnifiedAnalyticsData."""

    def test_default_is_low_confidence(self):
        """Sin datos, confianza es LOW."""
        data = UnifiedAnalyticsData()
        assert data.confidence_level == ConfidenceLevel.LOW
        assert data.ga4_available is False
        assert data.gsc_available is False

    def test_to_dict(self):
        """Test serializacion."""
        data = UnifiedAnalyticsData(
            confidence_level=ConfidenceLevel.MEDIUM,
            ga4_available=True,
            gsc_total_impressions=5000,
        )
        d = data.to_dict()
        assert d["confidence_level"] == "MEDIUM"
        assert d["ga4_available"] is True
        assert d["gsc_total_impressions"] == 5000

    def test_summary_text_empty(self):
        """Sin fuentes, summary muestra Ninguna."""
        data = UnifiedAnalyticsData()
        text = data.summary_text()
        assert "Confianza: LOW" in text
        assert "Ninguna" in text


class TestComputeConfidence:
    """Tests para _compute_confidence."""

    def test_confidence_high_both_sources(self):
        """Ambas fuentes disponibles = HIGH."""
        agg = AnalyticsAggregator()
        assert agg._compute_confidence(True, True) == ConfidenceLevel.HIGH

    def test_confidence_medium_ga4_only(self):
        """Solo GA4 = MEDIUM."""
        agg = AnalyticsAggregator()
        assert agg._compute_confidence(True, False) == ConfidenceLevel.MEDIUM

    def test_confidence_medium_gsc_only(self):
        """Solo GSC = MEDIUM."""
        agg = AnalyticsAggregator()
        assert agg._compute_confidence(False, True) == ConfidenceLevel.MEDIUM

    def test_confidence_low_no_sources(self):
        """Sin fuentes = LOW."""
        agg = AnalyticsAggregator()
        assert agg._compute_confidence(False, False) == ConfidenceLevel.LOW


class TestIAVisibilityEstimation:
    """Tests para _estimate_ia_visibility."""

    def test_visibility_with_gsc_data(self):
        """Con datos GSC calcula visibilidad."""
        agg = AnalyticsAggregator()
        data = UnifiedAnalyticsData(
            gsc_available=True,
            gsc_total_impressions=5000,
            gsc_avg_ctr=3.0,
            gsc_avg_position=8.0,
        )
        visibility = agg._estimate_ia_visibility(data)
        assert visibility > 0.0
        assert visibility <= 100.0

    def test_visibility_with_ga4_only(self):
        """Con solo GA4 calcula visibilidad."""
        agg = AnalyticsAggregator()
        data = UnifiedAnalyticsData(
            ga4_available=True,
            ga4_sessions_indirect=100,
            ga4_sessions_direct=300,
            ga4_sessions_referral=100,
        )
        visibility = agg._estimate_ia_visibility(data)
        # 100/500 * 100 = 20%
        assert visibility == pytest.approx(20.0, abs=0.1)

    def test_visibility_no_data(self):
        """Sin datos, visibilidad es 0."""
        agg = AnalyticsAggregator()
        data = UnifiedAnalyticsData()
        visibility = agg._estimate_ia_visibility(data)
        assert visibility == 0.0


class TestOrganicHealthScore:
    """Tests para _compute_organic_health_score."""

    def test_health_excellent(self):
        """Excelente: muchas impresiones, buen CTR, buena posicion."""
        agg = AnalyticsAggregator()
        data = UnifiedAnalyticsData(
            gsc_available=True,
            gsc_total_impressions=2000,
            gsc_avg_ctr=6.0,
            gsc_avg_position=3.0,
        )
        score = agg._compute_organic_health_score(data)
        # 30 (imp >1000) + 35 (ctr >5) + 35 (pos <=5) = 100
        assert score >= 90

    def test_health_mediocre(self):
        """Mediocre: pocas impresiones, bajo CTR, mala posicion."""
        agg = AnalyticsAggregator()
        data = UnifiedAnalyticsData(
            gsc_available=True,
            gsc_total_impressions=50,
            gsc_avg_ctr=0.5,
            gsc_avg_position=25.0,
        )
        score = agg._compute_organic_health_score(data)
        # 10 (imp 0-100) + 5 (ctr 0-1) + 5 (pos >20) = 20
        assert score <= 30

    def test_health_no_gsc_with_ga4(self):
        """Sin GSC pero con GA4 retorna 40."""
        agg = AnalyticsAggregator()
        data = UnifiedAnalyticsData(
            ga4_available=True,
            gsc_available=False,
        )
        assert agg._compute_organic_health_score(data) == 40.0

    def test_health_no_sources(self):
        """Sin ninguna fuente retorna 10."""
        agg = AnalyticsAggregator()
        data = UnifiedAnalyticsData(
            ga4_available=False,
            gsc_available=False,
        )
        assert agg._compute_organic_health_score(data) == 10.0


class TestCollectWithMocks:
    """Tests integrales con mocks."""

    def test_collect_no_clients(self):
        """Sin clientes (ambos None) retorna datos vacios."""
        agg = AnalyticsAggregator(ga4_client=None, gsc_client=None)
        result = agg.collect("2025-01-01", "2025-01-30")
        assert result.ga4_available is False
        assert result.gsc_available is False
        assert result.confidence_level == ConfidenceLevel.LOW

    def test_collect_with_mock_ga4_only(self):
        """Solo GA4 configurado = MEDIUM confidence."""
        mock_ga4 = MagicMock()
        mock_ga4.is_available.return_value = True
        mock_ga4.get_indirect_traffic.return_value = {
            "data_source": "GA4",
            "sessions_indirect": 100,
            "sessions_direct": 300,
            "sessions_referral": 50,
            "top_sources": [{"source": "Direct", "sessions": 300}],
        }

        agg = AnalyticsAggregator(ga4_client=mock_ga4, gsc_client=None)
        result = agg.collect("2025-01-01", "2025-01-30")

        assert result.ga4_available is True
        assert result.gsc_available is False
        assert result.confidence_level == ConfidenceLevel.MEDIUM
        assert result.ga4_sessions_indirect == 100

    def test_collect_with_mock_gsc_only(self):
        """Solo GSC configurado = MEDIUM confidence."""
        mock_gsc = MagicMock()
        mock_gsc.is_configured.return_value = True
        mock_gsc.get_search_analytics.return_value = GSCReport(
            is_available=True,
            total_clicks=50,
            total_impressions=5000,
            avg_ctr=1.0,
            avg_position=10.0,
            queries=[
                GSCQueryData(query="hotel test", clicks=20, impressions=2000, ctr=1.0, position=9.0),
            ],
        )
        mock_gsc.get_top_opportunities.return_value = []

        agg = AnalyticsAggregator(ga4_client=None, gsc_client=mock_gsc)
        result = agg.collect("2025-01-01", "2025-01-30")

        assert result.gsc_available is True
        assert result.ga4_available is False
        assert result.confidence_level == ConfidenceLevel.MEDIUM
        assert result.gsc_total_impressions == 5000
        assert len(result.gsc_top_queries) == 1

    def test_collect_with_both_mocks(self):
        """Ambos configurados = HIGH confidence."""
        mock_ga4 = MagicMock()
        mock_ga4.is_available.return_value = True
        mock_ga4.get_indirect_traffic.return_value = {
            "data_source": "GA4",
            "sessions_indirect": 200,
            "sessions_direct": 400,
            "sessions_referral": 100,
            "top_sources": [],
        }

        mock_gsc = MagicMock()
        mock_gsc.is_configured.return_value = True
        mock_gsc.get_search_analytics.return_value = GSCReport(
            is_available=True,
            total_clicks=100,
            total_impressions=10000,
            avg_ctr=2.0,
            avg_position=8.0,
        )
        mock_gsc.get_top_opportunities.return_value = []

        agg = AnalyticsAggregator(ga4_client=mock_ga4, gsc_client=mock_gsc)
        result = agg.collect("2025-01-01", "2025-01-30")

        assert result.confidence_level == ConfidenceLevel.HIGH
        assert result.ga4_available is True
        assert result.gsc_available is True
        assert result.gsc_total_impressions == 10000

    def test_graceful_failure(self):
        """GA4 falla, GSC funciona = degrada graciosamente."""
        mock_ga4 = MagicMock()
        mock_ga4.is_available.side_effect = Exception("GA4 crashed")

        mock_gsc = MagicMock()
        mock_gsc.is_configured.return_value = True
        mock_gsc.get_search_analytics.return_value = GSCReport(
            is_available=True,
            total_clicks=30,
            total_impressions=3000,
            avg_ctr=1.0,
            avg_position=12.0,
        )
        mock_gsc.get_top_opportunities.return_value = []

        agg = AnalyticsAggregator(ga4_client=mock_ga4, gsc_client=mock_gsc)
        result = agg.collect()  # No exceptions should occur

        assert result.gsc_available is True
        assert result.ga4_available is False
        assert result.confidence_level == ConfidenceLevel.MEDIUM
