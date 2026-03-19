"""Tests for PageSpeed API with lab data only (no CrUX)."""
import pytest
from unittest.mock import Mock, patch
from modules.data_validation.external_apis.pagespeed_client import PageSpeedClient, PageSpeedResult


class TestPageSpeedLabDataOnly:
    """Test PageSpeed behavior when no CrUX field data available."""
    
    @patch('modules.data_validation.external_apis.pagespeed_client.requests.get')
    def test_analyze_url_returns_lighthouse_without_crux(self, mock_get):
        """When no CrUX data, should still return Lighthouse score."""
        # Mock response without loadingExperience.metrics (no CrUX)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "lighthouseResult": {
                "categories": {
                    "performance": {"score": 0.65}
                },
                "audits": {
                    "largest-contentful-paint": {"numericValue": 2500},
                    "total-blocking-time": {"numericValue": 200}
                }
            },
            "loadingExperience": {}  # No metrics = no CrUX
        }
        mock_get.return_value = mock_response
        
        client = PageSpeedClient(api_key="test_key")
        result = client.analyze_url("https://example.com", "mobile")
        
        assert result.performance_score == 65  # 0.65 * 100
        assert result.status == "LAB_DATA_ONLY"
        assert result.has_field_data is False
        assert result.lcp is not None  # Should have lab LCP
        assert result.tbt is not None  # Should have lab TBT
    
    @patch('modules.data_validation.external_apis.pagespeed_client.requests.get')
    def test_analyze_url_returns_verified_with_crux(self, mock_get):
        """When CrUX data available, should return VERIFIED status."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "lighthouseResult": {
                "categories": {
                    "performance": {"score": 0.70}
                },
                "audits": {}
            },
            "loadingExperience": {
                "metrics": {
                    "LARGEST_CONTENTFUL_PAINT_MS": {"percentile": 2000}
                }
            }
        }
        mock_get.return_value = mock_response
        
        client = PageSpeedClient(api_key="test_key")
        result = client.analyze_url("https://example.com", "mobile")
        
        assert result.performance_score == 70
        assert result.status == "VERIFIED"
        assert result.has_field_data is True
