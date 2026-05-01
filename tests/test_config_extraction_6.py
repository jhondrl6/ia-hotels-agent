"""
Tests for FASE-CONFIG-6: Config Reconnect + Deprecación Módulos Huérfanos.

Verifies:
- settings.yaml has deprecation header
- 4 orphaned modules emit DeprecationWarning on import
- modules/analytics/__init__.py only exports GA4 and GSC
- AnalyticsStatus.is_any_missing() and is_complete() only check GA4 + GSC
- GoogleAnalyticsClient and GoogleSearchConsoleClient still work
"""

import pytest
import warnings


# ============================================================
# Tests: Config Deprecation
# ============================================================

class TestSettingsYamlDeprecation:
    """Tests for settings.yaml deprecation header."""

    def test_settings_yaml_has_deprecation_header(self):
        """settings.yaml contains deprecation warning header."""
        with open('config/settings.yaml', 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert '⚠️ LEGACY' in content or 'deprecado' in content.lower()
        assert 'config/pricing.yaml' in content
        assert 'config/regional_benchmarks.yaml' in content


# ============================================================
# Tests: Deprecated Module Warnings
# ============================================================

class TestDeprecatedModulesWarning:
    """Tests for DeprecationWarning on import of orphaned modules."""

    def test_profound_client_emits_deprecation_warning(self):
        """ProfoundClient import emits DeprecationWarning."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            import importlib
            import sys
            
            # Remove from cache if already imported
            for mod in list(sys.modules.keys()):
                if 'profound' in mod:
                    del sys.modules[mod]
            
            import modules.analytics.profound_client as pc
            
            deprecation_warnings = [
                x for x in w
                if issubclass(x.category, DeprecationWarning)
                and 'deprecad' in str(x.message).lower()
            ]
            assert len(deprecation_warnings) > 0, "No DeprecationWarning found for ProfoundClient"

    def test_semrush_client_emits_deprecation_warning(self):
        """SemrushClient import emits DeprecationWarning."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            import importlib
            import sys
            
            for mod in list(sys.modules.keys()):
                if 'semrush' in mod:
                    del sys.modules[mod]
            
            import modules.analytics.semrush_client as sc
            
            deprecation_warnings = [
                x for x in w
                if issubclass(x.category, DeprecationWarning)
                and 'deprecad' in str(x.message).lower()
            ]
            assert len(deprecation_warnings) > 0, "No DeprecationWarning found for SemrushClient"

    def test_data_aggregator_emits_deprecation_warning(self):
        """AnalyticsAggregator import emits DeprecationWarning."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            import importlib
            import sys
            
            for mod in list(sys.modules.keys()):
                if 'data_aggregator' in mod:
                    del sys.modules[mod]
            
            import modules.analytics.data_aggregator as da
            
            deprecation_warnings = [
                x for x in w
                if issubclass(x.category, DeprecationWarning)
                and 'deprecad' in str(x.message).lower()
            ]
            assert len(deprecation_warnings) > 0, "No DeprecationWarning found for AnalyticsAggregator"

    def test_aeo_metrics_gen_emits_deprecation_warning(self):
        """aeo_metrics_gen import emits DeprecationWarning."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            import importlib
            import sys
            
            for mod in list(sys.modules.keys()):
                if 'aeo_metrics' in mod:
                    del sys.modules[mod]
            
            import modules.delivery.generators.aeo_metrics_gen as aeo
            
            deprecation_warnings = [
                x for x in w
                if issubclass(x.category, DeprecationWarning)
                and 'deprecad' in str(x.message).lower()
            ]
            assert len(deprecation_warnings) > 0, "No DeprecationWarning found for aeo_metrics_gen"


# ============================================================
# Tests: Analytics __init__.py Cleanup
# ============================================================

class TestAnalyticsInitCleanup:
    """Tests for modules/analytics/__init__.py cleanup."""

    def test_init_only_exports_ga4_and_gsc(self):
        """__init__.py only exports GoogleAnalyticsClient and GoogleSearchConsoleClient."""
        from modules.analytics import __all__
        
        assert 'GoogleAnalyticsClient' in __all__
        assert 'GoogleSearchConsoleClient' in __all__
        assert 'ProfoundClient' not in __all__
        assert 'SemrushClient' not in __all__
        assert 'AnalyticsAggregator' not in __all__
        assert 'UnifiedAnalyticsData' not in __all__
        assert 'ConfidenceLevel' not in __all__

    def test_ga4_client_importable(self):
        """GoogleAnalyticsClient can still be imported."""
        from modules.analytics import GoogleAnalyticsClient
        assert callable(GoogleAnalyticsClient)

    def test_gsc_client_importable(self):
        """GoogleSearchConsoleClient can still be imported."""
        from modules.analytics import GoogleSearchConsoleClient
        assert callable(GoogleSearchConsoleClient)


# ============================================================
# Tests: AnalyticsStatus Bug Fix
# ============================================================

class TestAnalyticsStatusBugFix:
    """Tests for AnalyticsStatus.is_any_missing() and is_complete()."""

    def test_is_any_missing_true_when_ga4_unavailable(self):
        """is_any_missing() returns True when GA4 is unavailable."""
        from data_models.analytics_status import AnalyticsStatus
        
        status = AnalyticsStatus(ga4_available=False, gsc_available=True)
        assert status.is_any_missing() is True

    def test_is_any_missing_true_when_gsc_unavailable(self):
        """is_any_missing() returns True when GSC is unavailable."""
        from data_models.analytics_status import AnalyticsStatus
        
        status = AnalyticsStatus(ga4_available=True, gsc_available=False)
        assert status.is_any_missing() is True

    def test_is_any_missing_false_when_both_available(self):
        """is_any_missing() returns False when both GA4 and GSC are available."""
        from data_models.analytics_status import AnalyticsStatus
        
        status = AnalyticsStatus(ga4_available=True, gsc_available=True)
        assert status.is_any_missing() is False

    def test_is_complete_true_when_both_available(self):
        """is_complete() returns True when both GA4 and GSC are available."""
        from data_models.analytics_status import AnalyticsStatus
        
        status = AnalyticsStatus(ga4_available=True, gsc_available=True)
        assert status.is_complete() is True

    def test_is_complete_false_when_ga4_unavailable(self):
        """is_complete() returns False when GA4 is unavailable."""
        from data_models.analytics_status import AnalyticsStatus
        
        status = AnalyticsStatus(ga4_available=False, gsc_available=True)
        assert status.is_complete() is False

    def test_is_complete_false_when_gsc_unavailable(self):
        """is_complete() returns False when GSC is unavailable."""
        from data_models.analytics_status import AnalyticsStatus
        
        status = AnalyticsStatus(ga4_available=True, gsc_available=False)
        assert status.is_complete() is False

    def test_profound_semrush_not_considered_in_is_any_missing(self):
        """is_any_missing() does NOT consider deprecated profound/semrush fields."""
        from data_models.analytics_status import AnalyticsStatus
        
        # Both GA4 and GSC available, but profound/semrush unavailable
        # This should return False (nothing ACTIVE is missing)
        status = AnalyticsStatus(
            ga4_available=True,
            gsc_available=True,
            profound_available=False,  # deprecated
            semrush_available=False   # deprecated
        )
        assert status.is_any_missing() is False

    def test_missing_credentials_ignores_deprecated_sources(self):
        """missing_credentials() does NOT list PROFOUND_API_KEY or SEMRUSH_API_KEY."""
        from data_models.analytics_status import AnalyticsStatus
        
        status = AnalyticsStatus(
            profound_error="api_key not configured",
            semrush_error="api_key missing"
        )
        creds = status.missing_credentials()
        assert "PROFOUND_API_KEY" not in creds
        assert "SEMRUSH_API_KEY" not in creds

    def test_missing_credentials_lists_ga4(self):
        """missing_credentials() lists GA4 when credentials error."""
        from data_models.analytics_status import AnalyticsStatus
        
        status = AnalyticsStatus(ga4_error="credentials file not found")
        creds = status.missing_credentials()
        assert any("GA4" in c for c in creds)

    def test_summary_for_template_no_profound_semrush(self):
        """summary_for_template() only shows GA4 and GSC, not Profound/Semrush."""
        from data_models.analytics_status import AnalyticsStatus
        
        status = AnalyticsStatus(ga4_available=True, gsc_available=True)
        summary = status.summary_for_template()
        assert "Profound" not in summary
        assert "Semrush" not in summary
        assert "GA4" in summary
        assert "GSC" in summary

    def test_deprecated_helpers_return_placeholder(self):
        """profound_status_for_template/semrush_status_for_template return deprecation msg."""
        from data_models.analytics_status import AnalyticsStatus
        
        status = AnalyticsStatus()
        assert "deprecado" in status.profound_status_for_template().lower()
        assert "deprecado" in status.semrush_status_for_template().lower()
