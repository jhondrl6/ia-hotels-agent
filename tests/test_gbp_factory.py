"""Tests for GBP Auditor Factory with fallback."""

import pytest
from unittest.mock import patch, MagicMock


class TestGBPFactory:
    """Tests for gbp_factory module."""
    
    @pytest.mark.skip(reason="Requiere configuracion/Playwright externa")
    def test_get_gbp_auditor_returns_instance(self):
        """Test that get_gbp_auditor returns a valid instance."""
        from modules.scrapers.gbp_factory import get_gbp_auditor
        
        auditor = get_gbp_auditor(prefer_playwright=False)
        assert auditor is not None
        
    @pytest.mark.skip(reason="Requiere configuracion/Playwright externa")
    def test_get_gbp_auditor_selenium_fallback(self):
        """Test that Selenium is used when Playwright is not preferred."""
        from modules.scrapers.gbp_factory import get_gbp_auditor
        
        auditor = get_gbp_auditor(prefer_playwright=False)
        assert auditor is not None
        assert "GBPAuditor" in type(auditor).__name__
        
    @pytest.mark.skip(reason="Requiere configuracion/Playwright externa")
    def test_gbp_auditor_auto_wrapper(self):
        """Test GBPAuditorAuto wrapper."""
        from modules.scrapers.gbp_factory import GBPAuditorAuto
        
        auditor = GBPAuditorAuto(headless=True, prefer_playwright=False)
        assert auditor.driver_type in ['playwright', 'selenium']
        
    @pytest.mark.skip(reason="Requiere configuracion/Playwright externa")
    def test_gbp_auditor_auto_interface(self):
        """Test that GBPAuditorAuto exposes same interface."""
        from modules.scrapers.gbp_factory import GBPAuditorAuto
        
        auditor = GBPAuditorAuto(headless=True, prefer_playwright=False)
        assert hasattr(auditor, 'check_google_profile')
        assert hasattr(auditor, 'validate_location_only')
        assert hasattr(auditor, 'driver_type')
        
    @pytest.mark.skip(reason="Requiere configuracion/Playwright externa")
    def test_gbp_auditor_auto_auditor_property(self):
        """Test that GBPAuditorAuto exposes auditor property."""
        from modules.scrapers.gbp_factory import GBPAuditorAuto
        
        auditor = GBPAuditorAuto(headless=True, prefer_playwright=False)
        assert auditor.auditor is not None
        
    @patch('modules.scrapers.gbp_factory.get_gbp_auditor')
    def test_gbp_auditor_auto_delegates_check_google_profile(self, mock_get_auditor):
        """Test that check_google_profile is delegated to underlying auditor."""
        mock_auditor = MagicMock()
        mock_auditor.check_google_profile.return_value = {"score": 85}
        mock_get_auditor.return_value = mock_auditor
        
        from modules.scrapers.gbp_factory import GBPAuditorAuto
        
        auditor = GBPAuditorAuto(headless=True)
        result = auditor.check_google_profile("Hotel Test", "City Test")
        
        assert result == {"score": 85}
        mock_auditor.check_google_profile.assert_called_once()
        
    @patch('modules.scrapers.gbp_factory.get_gbp_auditor')
    def test_gbp_auditor_auto_delegates_validate_location(self, mock_get_auditor):
        """Test that validate_location_only is delegated to underlying auditor."""
        mock_auditor = MagicMock()
        mock_auditor.validate_location_only.return_value = {"valid": True}
        mock_get_auditor.return_value = mock_auditor
        
        from modules.scrapers.gbp_factory import GBPAuditorAuto
        
        auditor = GBPAuditorAuto(headless=True)
        result = auditor.validate_location_only("Hotel Test", "City Test")
        
        assert result == {"valid": True}
        mock_auditor.validate_location_only.assert_called_once()


class TestGBPFactoryFallback:
    """Tests for fallback behavior."""
    
    @pytest.mark.skip(reason="Requiere configuracion/Playwright externa")
    def test_fallback_to_selenium_when_playwright_disabled(self):
        """Test that Selenium is used when prefer_playwright=False."""
        from modules.scrapers.gbp_factory import get_gbp_auditor
        
        auditor = get_gbp_auditor(prefer_playwright=False)
        assert "GBPAuditor" in type(auditor).__name__
        assert "Playwright" not in type(auditor).__name__
