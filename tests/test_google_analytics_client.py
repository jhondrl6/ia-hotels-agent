"""
Tests for GoogleAnalyticsClient.

Tests cover:
- Initialization and configuration validation
- Graceful fallback when GA4 is unavailable
- IndirectTrafficMetrics creation from GA4 responses
- is_available() behavior
"""
import os
import pytest
from unittest.mock import patch, MagicMock
from modules.analytics.google_analytics_client import GoogleAnalyticsClient
from data_models.aeo_kpis import IndirectTrafficMetrics


class TestGoogleAnalyticsClientInit:
    """Tests for GoogleAnalyticsClient initialization."""

    def test_init_with_explicit_params(self):
        """Test initialization with explicit property_id and credentials_path."""
        client = GoogleAnalyticsClient(
            property_id="123456",
            credentials_path="/path/to/creds.json"
        )
        assert client.property_id == "123456"
        assert client.credentials_path == "/path/to/creds.json"
        assert client._client is None
        assert client._initialized is False

    def test_init_from_env_vars(self):
        """Test initialization from environment variables."""
        with patch.dict(os.environ, {
            "GA4_PROPERTY_ID": "999888",
            "GA4_CREDENTIALS_PATH": "/env/path/creds.json"
        }):
            client = GoogleAnalyticsClient()
            assert client.property_id == "999888"
            assert client.credentials_path == "/env/path/creds.json"

    def test_init_defaults_to_none(self):
        """Test initialization with no config defaults to None."""
        with patch.dict(os.environ, {}, clear=True):
            client = GoogleAnalyticsClient()
            assert client.property_id is None
            assert client.credentials_path is None


class TestGoogleAnalyticsClientAvailability:
    """Tests for is_available() and fallback behavior."""

    def test_not_available_without_property_id(self):
        """GA4 is not available when property_id is missing."""
        client = GoogleAnalyticsClient(
            property_id=None,
            credentials_path="/some/path.json"
        )
        assert client.is_available() is False
        assert "GA4_PROPERTY_ID" in (client._init_error or "")

    def test_not_available_without_credentials_path(self):
        """GA4 is not available when credentials_path is missing."""
        client = GoogleAnalyticsClient(
            property_id="123456",
            credentials_path=None
        )
        assert client.is_available() is False
        assert "GA4_CREDENTIALS_PATH" in (client._init_error or "")

    def test_not_available_when_credentials_file_missing(self):
        """GA4 is not available when credentials file does not exist."""
        client = GoogleAnalyticsClient(
            property_id="123456",
            credentials_path="/nonexistent/creds.json"
        )
        assert client.is_available() is False
        assert "no encontrado" in (client._init_error or "")

    def test_not_available_on_import_error(self):
        """GA4 gracefully reports missing library."""
        client = GoogleAnalyticsClient(
            property_id="123456",
            credentials_path="/some/path.json"
        )
        with patch('os.path.exists', return_value=True):
            with patch.dict('sys.modules', {
                'google.analytics.data': None,
                'google.oauth2': None,
            }):
                result = client._initialize()
                assert result is False
                assert "Librería" in (client._init_error or "")


class TestGoogleAnalyticsClientFallback:
    """Tests for graceful fallback when GA4 is unavailable."""

    def test_get_indirect_traffic_fallback(self):
        """get_indirect_traffic returns safe defaults when GA4 unavailable."""
        client = GoogleAnalyticsClient(
            property_id=None,
            credentials_path=None
        )
        result = client.get_indirect_traffic()

        assert result["sessions_indirect"] == 0
        assert result["sessions_direct"] == 0
        assert result["sessions_referral"] == 0
        assert result["top_sources"] == []
        assert result["data_source"] == "N/A"
        assert result["note"] is not None

    def test_get_indirect_traffic_date_range_accepted(self):
        """get_indirect_traffic accepts date_range parameter."""
        client = GoogleAnalyticsClient(property_id=None)
        result = client.get_indirect_traffic(date_range="last_90_days")
        assert result["data_source"] == "N/A"

    def test_initialize_returns_cached_on_second_call(self):
        """_initialize returns cached result on subsequent calls."""
        client = GoogleAnalyticsClient(property_id=None)
        assert client._initialize() is False
        assert client._initialize() is False
        assert client._initialized is True


class TestIndirectTrafficMetricsFromGA4:
    """Tests for IndirectTrafficMetrics.from_ga4_response()."""

    def test_from_ga4_response_full(self):
        """Test creating IndirectTrafficMetrics from a full GA4 response."""
        response = {
            "sessions_indirect": 150,
            "sessions_direct": 80,
            "sessions_referral": 30,
            "data_source": "GA4",
            "top_sources": [
                {"source": "Organic Search", "sessions": 100},
                {"source": "Referral", "sessions": 30},
            ],
            "date_range": "last_30_days",
            "note": None,
        }
        metrics = IndirectTrafficMetrics.from_ga4_response(response)

        assert metrics.sessions_indirect == 150
        assert metrics.sessions_direct == 80
        assert metrics.sessions_referral == 30
        assert metrics.data_source == "GA4"
        assert len(metrics.top_sources) == 2
        assert metrics.date_range == "last_30_days"
        assert metrics.note is None

    def test_from_ga4_response_empty(self):
        """Test creating IndirectTrafficMetrics from empty response."""
        metrics = IndirectTrafficMetrics.from_ga4_response({})

        assert metrics.sessions_indirect == 0
        assert metrics.sessions_direct == 0
        assert metrics.sessions_referral == 0
        assert metrics.data_source == "N/A"
        assert metrics.top_sources == []
        assert metrics.date_range is None
        assert metrics.note is None

    def test_to_dict_includes_date_range_and_note(self):
        """Test that to_dict includes date_range and note fields."""
        metrics = IndirectTrafficMetrics(
            sessions_indirect=50,
            data_source="GA4",
            date_range="last_30_days",
            note="Test note",
        )
        d = metrics.to_dict()

        assert d["sessions_indirect"] == 50
        assert d["data_source"] == "GA4"
        assert d["date_range"] == "last_30_days"
        assert d["note"] == "Test note"

    def test_to_dict_defaults(self):
        """Test to_dict with default values."""
        metrics = IndirectTrafficMetrics()
        d = metrics.to_dict()

        assert d["date_range"] is None
        assert d["note"] is None
