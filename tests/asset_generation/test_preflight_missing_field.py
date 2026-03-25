"""Tests for preflight missing field with fallback."""
import pytest
from modules.asset_generation.preflight_checks import (
    PreflightChecker, PreflightStatus, PreflightReport
)
from modules.data_validation import DataPoint, ConfidenceLevel


class TestPreflightMissingFieldFallback:
    """Test preflight behavior when required field is missing."""

    def test_missing_field_with_block_on_failure_false_converts_to_warning(self):
        """When block_on_failure=False and field missing, should be WARNING."""
        checker = PreflightChecker()

        # Empty validated_data - field "faqs" is missing
        validated_data = {}

        # faq_page has block_on_failure=False
        report = checker.check_asset("faq_page", validated_data)

        assert report.overall_status == PreflightStatus.WARNING
        assert report.can_proceed is True
        assert len(report.warnings) > 0
        assert "Missing field" in report.warnings[0] or "fallback" in report.warnings[0].lower()

    def test_missing_field_with_block_on_failure_true_is_blocked(self):
        """When block_on_failure=True and field missing, NEVER_BLOCK: uses fallback as WARNING."""
        checker = PreflightChecker()

        # Empty validated_data - field "whatsapp" is missing
        validated_data = {}

        # whatsapp_button has block_on_failure=True, but NEVER_BLOCK converts to WARNING
        report = checker.check_asset("whatsapp_button", validated_data)

        # NEVER_BLOCK: Even block_on_failure=True se convierte a WARNING con fallback
        assert report.overall_status == PreflightStatus.WARNING
        assert report.can_proceed is True
        assert len(report.warnings) > 0

    def test_missing_field_fallback_action_is_set(self):
        """Fallback action should be set when field missing and block_on_failure=False."""
        checker = PreflightChecker()

        validated_data = {}
        report = checker.check_asset("faq_page", validated_data)

        # Should have at least one check with fallback_action
        checks_with_fallback = [c for c in report.checks if c.fallback_action]
        assert len(checks_with_fallback) > 0
        assert checks_with_fallback[0].fallback_action == "generate_with_actual_count"
