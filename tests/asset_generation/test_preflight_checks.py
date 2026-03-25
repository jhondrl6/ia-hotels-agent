"""Tests for preflight_checks module."""

import pytest
from datetime import datetime
from modules.asset_generation.preflight_checks import (
    PreflightStatus,
    PreflightCheck,
    PreflightReport,
    PreflightChecker,
)
from modules.data_validation import DataPoint, DataSource


class TestPreflightStatus:
    """Tests for PreflightStatus enum."""

    @pytest.mark.parametrize("status,expected_value", [
        (PreflightStatus.PASSED, "passed"),
        (PreflightStatus.WARNING, "warning"),
        (PreflightStatus.BLOCKED, "blocked"),
    ])
    def test_preflight_status_enum_values(self, status, expected_value):
        """Test that PreflightStatus enum has correct values."""
        assert status.value == expected_value

    @pytest.mark.parametrize("status_name", [
        "PASSED", "WARNING", "BLOCKED"
    ])
    def test_preflight_status_enum_members(self, status_name):
        """Test that all expected enum members exist."""
        assert hasattr(PreflightStatus, status_name)


class TestPreflightCheck:
    """Tests for PreflightCheck dataclass."""

    @pytest.mark.parametrize("status,can_generate,fallback_action", [
        (PreflightStatus.PASSED, True, None),
        (PreflightStatus.WARNING, True, "use_default"),
        (PreflightStatus.BLOCKED, False, None),
    ])
    def test_preflight_check_creation(self, status, can_generate, fallback_action):
        """Test creating a PreflightCheck instance."""
        check = PreflightCheck(
            check_name="test_check",
            field_name="test_field",
            required_confidence=0.8,
            status=status,
            message="Test message",
            can_generate=can_generate,
            fallback_action=fallback_action,
        )
        assert check.check_name == "test_check"
        assert check.field_name == "test_field"
        assert check.required_confidence == 0.8
        assert check.status == status
        assert check.message == "Test message"
        assert check.can_generate is can_generate
        assert check.fallback_action == fallback_action


class TestPreflightReport:
    """Tests for PreflightReport dataclass."""

    @pytest.mark.parametrize("overall_status,can_proceed,warnings_count,blocking_count", [
        (PreflightStatus.PASSED, True, 0, 0),
        (PreflightStatus.WARNING, True, 2, 0),
        (PreflightStatus.BLOCKED, False, 0, 1),
    ])
    def test_preflight_report_creation(self, overall_status, can_proceed, warnings_count, blocking_count):
        """Test creating a PreflightReport instance."""
        warnings = ["Warning 1", "Warning 2"] if warnings_count > 0 else []
        blocking = ["Missing field"] if blocking_count > 0 else []
        
        check = PreflightCheck(
            check_name="test_check",
            field_name="test_field",
            required_confidence=0.8,
            status=PreflightStatus.PASSED,
            message="Test passed",
            can_generate=True,
        )
        
        report = PreflightReport(
            asset_type="test_asset",
            overall_status=overall_status,
            checks=[check],
            can_proceed=can_proceed,
            warnings=warnings,
            blocking_issues=blocking,
        )
        assert report.asset_type == "test_asset"
        assert report.overall_status == overall_status
        assert len(report.checks) == 1
        assert report.can_proceed is can_proceed
        assert len(report.warnings) == warnings_count
        assert len(report.blocking_issues) == blocking_count


class TestPreflightCheckerInitialization:
    """Tests for PreflightChecker initialization."""

    def test_preflight_checker_initialization(self):
        """Test that PreflightChecker initializes correctly."""
        checker = PreflightChecker()
        assert checker is not None
        assert hasattr(checker, "ASSET_REQUIREMENTS")
        assert "whatsapp_button" in checker.ASSET_REQUIREMENTS
        assert "faq_page" in checker.ASSET_REQUIREMENTS
        assert "hotel_schema" in checker.ASSET_REQUIREMENTS
        assert "financial_projection" in checker.ASSET_REQUIREMENTS

    def test_asset_requirements_structure(self):
        """Test that ASSET_REQUIREMENTS has correct structure."""
        checker = PreflightChecker()
        for asset_type, requirements in checker.ASSET_REQUIREMENTS.items():
            assert "required_confidence" in requirements
            assert "required_field" in requirements
            assert "block_on_failure" in requirements
            assert "fallback" in requirements


class TestPreflightCheckerCheckAsset:
    """Tests for PreflightChecker.check_asset method."""

    def test_check_asset_returns_preflight_report(self):
        """Test that check_asset returns a PreflightReport."""
        checker = PreflightChecker()
        dp = DataPoint("whatsapp")
        dp.add_source(DataSource("test", "1234567890", datetime.now().isoformat()))
        validated_data = {"whatsapp": dp}
        report = checker.check_asset("whatsapp_button", validated_data)
        assert isinstance(report, PreflightReport)

    @pytest.mark.parametrize("asset_type,expected_status", [
        ("unknown_type", PreflightStatus.BLOCKED),
    ])
    def test_check_asset_unknown_asset_type(self, asset_type, expected_status):
        """Test check_asset with unknown asset type returns BLOCKED."""
        checker = PreflightChecker()
        report = checker.check_asset(asset_type, {})
        assert report.overall_status == expected_status
        assert report.can_proceed is False

    @pytest.mark.parametrize("sources_count,expected_status", [
        (2, PreflightStatus.PASSED),  # Multiple matching sources = high confidence
        (1, PreflightStatus.PASSED),  # Single source = 100% match
        (0, PreflightStatus.WARNING),  # NEVER_BLOCK: No sources = fallback as WARNING
    ])
    def test_check_asset_confidence_levels(self, sources_count, expected_status):
        """Test check_asset returns correct status based on confidence."""
        checker = PreflightChecker()
        dp = DataPoint("whatsapp")
        
        if sources_count > 0:
            # Use same value for matching, different for non-matching
            value = "1234567890"
            for i in range(sources_count):
                dp.add_source(DataSource(f"source{i}", value, datetime.now().isoformat()))
        
        validated_data = {"whatsapp": dp}
        report = checker.check_asset("whatsapp_button", validated_data)
        # NEVER_BLOCK: 0 sources with fallback becomes WARNING, not BLOCKED
        assert report.overall_status == expected_status

    def test_check_asset_missing_field(self):
        """Test check_asset when required field is missing - NEVER_BLOCK: uses fallback."""
        checker = PreflightChecker()
        validated_data = {}  # Empty data
        report = checker.check_asset("whatsapp_button", validated_data)
        # NEVER_BLOCK: Even with missing field, uses fallback and becomes WARNING
        assert report.overall_status == PreflightStatus.WARNING
        assert report.can_proceed is True
        assert len(report.warnings) > 0


class TestPreflightCheckerEvaluateCheck:
    """Tests for PreflightChecker._evaluate_check method."""

    @pytest.mark.parametrize("sources_count,required_confidence,expected_status", [
        (2, 0.5, PreflightStatus.PASSED),  # Multiple sources, low requirement
        (1, 0.95, PreflightStatus.PASSED),  # Single source = 100% match
        (0, 0.9, PreflightStatus.BLOCKED),  # No sources
    ])
    def test_evaluate_check_returns_correct_status(self, sources_count, required_confidence, expected_status):
        """Test _evaluate_check returns correct status based on confidence."""
        checker = PreflightChecker()
        dp = DataPoint("test_field")
        
        if sources_count > 0:
            value = "test_value"
            for i in range(sources_count):
                dp.add_source(DataSource(f"s{i}", value, datetime.now().isoformat()))
        
        check = checker._evaluate_check("test_field", dp, required_confidence)
        assert check.status == expected_status


class TestPreflightCheckerGetters:
    """Tests for PreflightChecker getter methods."""

    @pytest.mark.parametrize("issues_count,warnings_count", [
        (2, 0),
        (0, 3),
        (1, 2),
    ])
    def test_get_blocking_issues_and_warnings(self, issues_count, warnings_count):
        """Test get_blocking_issues and get_warnings return correct items."""
        checker = PreflightChecker()
        
        issues = [f"Issue {i+1}" for i in range(issues_count)]
        warnings = [f"Warning {i+1}" for i in range(warnings_count)]
        
        if issues:
            report = PreflightReport(
                asset_type="test",
                overall_status=PreflightStatus.BLOCKED,
                checks=[],
                can_proceed=False,
                warnings=[],
                blocking_issues=issues,
            )
            result = checker.get_blocking_issues(report)
            assert len(result) == issues_count
        else:
            report = PreflightReport(
                asset_type="test",
                overall_status=PreflightStatus.WARNING,
                checks=[],
                can_proceed=True,
                warnings=warnings,
                blocking_issues=[],
            )
            result = checker.get_warnings(report)
            assert len(result) == warnings_count


class TestPreflightCheckerFormatReport:
    """Tests for PreflightChecker.format_report_for_display method."""

    @pytest.mark.parametrize("overall_status,has_warnings,has_blocking", [
        (PreflightStatus.PASSED, False, False),
        (PreflightStatus.WARNING, True, False),
        (PreflightStatus.BLOCKED, False, True),
    ])
    def test_format_report_for_display(self, overall_status, has_warnings, has_blocking):
        """Test format_report_for_display returns correct output."""
        checker = PreflightChecker()
        
        check = PreflightCheck(
            check_name="test_check",
            field_name="test_field",
            required_confidence=0.8,
            status=overall_status,
            message="Test message",
            can_generate=True,
        )
        
        warnings = ["Test warning"] if has_warnings else []
        blocking = ["Blocking issue"] if has_blocking else []
        
        report = PreflightReport(
            asset_type="test_asset",
            overall_status=overall_status,
            checks=[check],
            can_proceed=not has_blocking,
            warnings=warnings,
            blocking_issues=blocking,
        )
        
        formatted = checker.format_report_for_display(report)
        assert isinstance(formatted, str)
        assert "Preflight Report: test_asset" in formatted
        assert overall_status.value.upper() in formatted
        
        if has_warnings:
            assert "Warnings:" in formatted
        if has_blocking:
            assert "Blocking Issues:" in formatted
