"""Tests for asset_metadata module."""

import pytest
from datetime import datetime
from modules.asset_generation.asset_metadata import (
    AssetMetadata,
    AssetMetadataEnforcer,
)
from modules.data_validation.confidence_taxonomy import ConfidenceLevel


class TestAssetMetadata:
    """Tests for AssetMetadata dataclass."""

    def test_asset_metadata_creation(self):
        """Test creating an AssetMetadata instance."""
        metadata = AssetMetadata(
            asset_name="test_asset",
            asset_type="html",
            generated_at=datetime.now(),
            confidence_level=ConfidenceLevel.VERIFIED,
            confidence_score=0.95,
            validation_sources=["web_scraping", "gbp_api"],
            preflight_status="PASSED",
            can_use=True,
        )
        assert metadata.asset_name == "test_asset"
        assert metadata.asset_type == "html"
        assert isinstance(metadata.generated_at, datetime)
        assert metadata.confidence_level == ConfidenceLevel.VERIFIED
        assert metadata.confidence_score == 0.95
        assert metadata.validation_sources == ["web_scraping", "gbp_api"]
        assert metadata.preflight_status == "PASSED"
        assert metadata.can_use is True
        assert metadata.disclaimer is None
        assert metadata.generated_by == "IAH_v4.0"
        assert metadata.version == "4.0.0"

    def test_asset_metadata_all_required_fields(self):
        """Test that AssetMetadata has all required fields."""
        now = datetime.now()
        metadata = AssetMetadata(
            asset_name="test",
            asset_type="json",
            generated_at=now,
            confidence_level=ConfidenceLevel.ESTIMATED,
            confidence_score=0.7,
            validation_sources=["benchmark"],
            preflight_status="WARNING",
            can_use=True,
            disclaimer="Test disclaimer",
            generated_by="test_generator",
            version="1.0.0",
        )
        assert metadata.asset_name == "test"
        assert metadata.asset_type == "json"
        assert metadata.generated_at == now
        assert metadata.confidence_level == ConfidenceLevel.ESTIMATED
        assert metadata.confidence_score == 0.7
        assert metadata.validation_sources == ["benchmark"]
        assert metadata.preflight_status == "WARNING"
        assert metadata.can_use is True
        assert metadata.disclaimer == "Test disclaimer"
        assert metadata.generated_by == "test_generator"
        assert metadata.version == "1.0.0"


class TestAssetMetadataEnforcerInitialization:
    """Tests for AssetMetadataEnforcer initialization."""

    def test_asset_metadata_enforcer_initialization(self):
        """Test that AssetMetadataEnforcer initializes correctly."""
        enforcer = AssetMetadataEnforcer()
        assert enforcer is not None
        assert hasattr(enforcer, "REQUIRED_FIELDS")
        assert hasattr(enforcer, "VALID_PREFLIGHT_STATUSES")
        assert hasattr(enforcer, "VALID_ASSET_TYPES")
        assert enforcer._validation_errors == []

    def test_required_fields_list(self):
        """Test that REQUIRED_FIELDS contains expected fields."""
        enforcer = AssetMetadataEnforcer()
        expected_fields = [
            "asset_name",
            "asset_type",
            "generated_at",
            "confidence_level",
            "confidence_score",
            "validation_sources",
            "preflight_status",
            "can_use",
        ]
        for field in expected_fields:
            assert field in enforcer.REQUIRED_FIELDS

    def test_valid_preflight_statuses(self):
        """Test that VALID_PREFLIGHT_STATUSES contains expected values."""
        enforcer = AssetMetadataEnforcer()
        assert "PASSED" in enforcer.VALID_PREFLIGHT_STATUSES
        assert "WARNING" in enforcer.VALID_PREFLIGHT_STATUSES
        assert "BLOCKED" in enforcer.VALID_PREFLIGHT_STATUSES


class TestAssetMetadataEnforcerCreateMetadata:
    """Tests for AssetMetadataEnforcer.create_metadata method."""

    def test_create_metadata_sets_can_use_correctly(self):
        """Test that create_metadata sets can_use based on confidence."""
        enforcer = AssetMetadataEnforcer()
        # High confidence should be usable
        metadata = enforcer.create_metadata(
            asset_name="high_confidence_asset",
            asset_type="html",
            confidence_level=ConfidenceLevel.VERIFIED,
            confidence_score=0.9,
            validation_sources=["web_scraping"],
            preflight_status="PASSED",
        )
        assert metadata.can_use is True

        # Low confidence should not be usable
        metadata_low = enforcer.create_metadata(
            asset_name="low_confidence_asset",
            asset_type="html",
            confidence_level=ConfidenceLevel.UNKNOWN,
            confidence_score=0.3,
            validation_sources=[],
            preflight_status="BLOCKED",
        )
        assert metadata_low.can_use is False

    def test_create_metadata_generates_disclaimer_for_low_confidence(self):
        """Test that create_metadata generates disclaimer for low confidence."""
        enforcer = AssetMetadataEnforcer()
        # Low confidence should have disclaimer
        metadata = enforcer.create_metadata(
            asset_name="low_confidence",
            asset_type="html",
            confidence_level=ConfidenceLevel.UNKNOWN,
            confidence_score=0.3,
            validation_sources=[],
            preflight_status="WARNING",
        )
        assert metadata.disclaimer is not None
        assert "⚠️" in metadata.disclaimer or "insuficientes" in metadata.disclaimer

    def test_create_metadata_no_disclaimer_for_high_confidence(self):
        """Test that high confidence assets have no disclaimer."""
        enforcer = AssetMetadataEnforcer()
        metadata = enforcer.create_metadata(
            asset_name="high_confidence",
            asset_type="html",
            confidence_level=ConfidenceLevel.VERIFIED,
            confidence_score=0.95,
            validation_sources=["web_scraping", "gbp_api"],
            preflight_status="PASSED",
        )
        assert metadata.disclaimer is None

    def test_create_metadata_invalid_preflight_status(self):
        """Test that invalid preflight_status raises ValueError."""
        enforcer = AssetMetadataEnforcer()
        with pytest.raises(ValueError) as exc_info:
            enforcer.create_metadata(
                asset_name="test",
                asset_type="html",
                confidence_level=ConfidenceLevel.VERIFIED,
                confidence_score=0.9,
                validation_sources=["test"],
                preflight_status="INVALID",
            )
        assert "Invalid preflight_status" in str(exc_info.value)

    def test_create_metadata_generates_datetime(self):
        """Test that create_metadata sets generated_at to current time."""
        enforcer = AssetMetadataEnforcer()
        before = datetime.now()
        metadata = enforcer.create_metadata(
            asset_name="test",
            asset_type="html",
            confidence_level=ConfidenceLevel.VERIFIED,
            confidence_score=0.9,
            validation_sources=["test"],
            preflight_status="PASSED",
        )
        after = datetime.now()
        assert before <= metadata.generated_at <= after


class TestAssetMetadataEnforcerValidateMetadata:
    """Tests for AssetMetadataEnforcer.validate_metadata method."""

    def test_validate_metadata_returns_true_for_valid(self):
        """Test validate_metadata returns True for valid metadata."""
        enforcer = AssetMetadataEnforcer()
        metadata = AssetMetadata(
            asset_name="valid_asset",
            asset_type="html",
            generated_at=datetime.now(),
            confidence_level=ConfidenceLevel.VERIFIED,
            confidence_score=0.9,
            validation_sources=["test"],
            preflight_status="PASSED",
            can_use=True,
        )
        assert enforcer.validate_metadata(metadata) is True
        assert enforcer.get_validation_errors() == []

    def test_validate_metadata_returns_false_for_invalid(self):
        """Test validate_metadata returns False for invalid metadata."""
        enforcer = AssetMetadataEnforcer()
        metadata = AssetMetadata(
            asset_name=None,  # Missing required field
            asset_type="html",
            generated_at=datetime.now(),
            confidence_level=ConfidenceLevel.VERIFIED,
            confidence_score=0.9,
            validation_sources=["test"],
            preflight_status="PASSED",
            can_use=True,
        )
        assert enforcer.validate_metadata(metadata) is False
        assert len(enforcer.get_validation_errors()) > 0

    def test_validate_metadata_invalid_confidence_score_range(self):
        """Test validate_metadata catches out-of-range confidence_score."""
        enforcer = AssetMetadataEnforcer()
        metadata = AssetMetadata(
            asset_name="test",
            asset_type="html",
            generated_at=datetime.now(),
            confidence_level=ConfidenceLevel.VERIFIED,
            confidence_score=1.5,  # Invalid: > 1.0
            validation_sources=["test"],
            preflight_status="PASSED",
            can_use=True,
        )
        assert enforcer.validate_metadata(metadata) is False
        assert any("confidence_score" in err for err in enforcer.get_validation_errors())

    def test_validate_metadata_invalid_generated_at_type(self):
        """Test validate_metadata catches invalid generated_at type."""
        enforcer = AssetMetadataEnforcer()
        metadata = AssetMetadata(
            asset_name="test",
            asset_type="html",
            generated_at="not a datetime",  # Invalid type
            confidence_level=ConfidenceLevel.VERIFIED,
            confidence_score=0.9,
            validation_sources=["test"],
            preflight_status="PASSED",
            can_use=True,
        )
        assert enforcer.validate_metadata(metadata) is False
        assert any("generated_at" in err for err in enforcer.get_validation_errors())

    def test_validate_metadata_invalid_confidence_level_type(self):
        """Test validate_metadata catches invalid confidence_level type."""
        enforcer = AssetMetadataEnforcer()
        metadata = AssetMetadata(
            asset_name="test",
            asset_type="html",
            generated_at=datetime.now(),
            confidence_level="verified",  # Should be enum, not string
            confidence_score=0.9,
            validation_sources=["test"],
            preflight_status="PASSED",
            can_use=True,
        )
        assert enforcer.validate_metadata(metadata) is False
        assert any("confidence_level" in err for err in enforcer.get_validation_errors())

    def test_validate_metadata_invalid_preflight_status(self):
        """Test validate_metadata catches invalid preflight_status."""
        enforcer = AssetMetadataEnforcer()
        metadata = AssetMetadata(
            asset_name="test",
            asset_type="html",
            generated_at=datetime.now(),
            confidence_level=ConfidenceLevel.VERIFIED,
            confidence_score=0.9,
            validation_sources=["test"],
            preflight_status="INVALID",
            can_use=True,
        )
        assert enforcer.validate_metadata(metadata) is False
        assert any("preflight_status" in err for err in enforcer.get_validation_errors())


class TestAssetMetadataEnforcerInjectMetadata:
    """Tests for AssetMetadataEnforcer.inject_metadata_into_asset method."""

    def test_inject_metadata_into_asset_html(self):
        """Test inject metadata into HTML content."""
        enforcer = AssetMetadataEnforcer()
        metadata = AssetMetadata(
            asset_name="test",
            asset_type="html",
            generated_at=datetime.now(),
            confidence_level=ConfidenceLevel.VERIFIED,
            confidence_score=0.9,
            validation_sources=["test"],
            preflight_status="PASSED",
            can_use=True,
        )
        content = "<div>Test HTML</div>"
        result = enforcer.inject_metadata_into_asset(content, metadata, "html")
        assert "IAH_METADATA_START" in result
        assert "IAH_METADATA_END" in result
        assert "<div>Test HTML</div>" in result
        assert result.startswith("<!-- IAH_METADATA_START")

    def test_inject_metadata_into_asset_json(self):
        """Test inject metadata into JSON content."""
        enforcer = AssetMetadataEnforcer()
        metadata = AssetMetadata(
            asset_name="test",
            asset_type="json",
            generated_at=datetime.now(),
            confidence_level=ConfidenceLevel.VERIFIED,
            confidence_score=0.9,
            validation_sources=["test"],
            preflight_status="PASSED",
            can_use=True,
        )
        content = '{"key": "value"}'
        result = enforcer.inject_metadata_into_asset(content, metadata, "json")
        assert "_metadata" in result
        assert '"key": "value"' in result
        # Should be valid JSON
        import json
        parsed = json.loads(result)
        assert "_metadata" in parsed

    def test_inject_metadata_into_asset_csv(self):
        """Test inject metadata into CSV content."""
        enforcer = AssetMetadataEnforcer()
        metadata = AssetMetadata(
            asset_name="test",
            asset_type="csv",
            generated_at=datetime.now(),
            confidence_level=ConfidenceLevel.VERIFIED,
            confidence_score=0.9,
            validation_sources=["test"],
            preflight_status="PASSED",
            can_use=True,
        )
        content = "id,name\n1,Test"
        result = enforcer.inject_metadata_into_asset(content, metadata, "csv")
        assert result.startswith("# ")
        assert "id,name" in result

    def test_inject_metadata_into_asset_markdown(self):
        """Test inject metadata into Markdown content."""
        enforcer = AssetMetadataEnforcer()
        metadata = AssetMetadata(
            asset_name="test",
            asset_type="markdown",
            generated_at=datetime.now(),
            confidence_level=ConfidenceLevel.VERIFIED,
            confidence_score=0.9,
            validation_sources=["test"],
            preflight_status="PASSED",
            can_use=True,
        )
        content = "# Test Markdown"
        result = enforcer.inject_metadata_into_asset(content, metadata, "markdown")
        assert result.startswith("---")
        assert "# Test Markdown" in result
        assert "asset_name" in result


class TestAssetMetadataEnforcerExtractMetadata:
    """Tests for AssetMetadataEnforcer.extract_metadata_from_asset method."""

    def test_extract_metadata_from_asset_html(self):
        """Test extract metadata from HTML content."""
        enforcer = AssetMetadataEnforcer()
        metadata = AssetMetadata(
            asset_name="test_asset",
            asset_type="html",
            generated_at=datetime(2024, 1, 15, 10, 30),
            confidence_level=ConfidenceLevel.VERIFIED,
            confidence_score=0.9,
            validation_sources=["web_scraping"],
            preflight_status="PASSED",
            can_use=True,
        )
        content = "<div>Test</div>"
        injected = enforcer.inject_metadata_into_asset(content, metadata, "html")
        extracted = enforcer.extract_metadata_from_asset(injected, "html")
        assert extracted is not None
        assert extracted.asset_name == "test_asset"

    def test_extract_metadata_from_asset_json(self):
        """Test extract metadata from JSON content."""
        enforcer = AssetMetadataEnforcer()
        metadata = AssetMetadata(
            asset_name="json_asset",
            asset_type="json",
            generated_at=datetime.now(),
            confidence_level=ConfidenceLevel.ESTIMATED,
            confidence_score=0.75,
            validation_sources=["benchmark"],
            preflight_status="WARNING",
            can_use=True,
        )
        content = '{"data": "test"}'
        injected = enforcer.inject_metadata_into_asset(content, metadata, "json")
        extracted = enforcer.extract_metadata_from_asset(injected, "json")
        assert extracted is not None
        assert extracted.asset_name == "json_asset"

    def test_extract_metadata_from_asset_csv(self):
        """Test extract metadata from CSV content."""
        enforcer = AssetMetadataEnforcer()
        metadata = AssetMetadata(
            asset_name="csv_asset",
            asset_type="csv",
            generated_at=datetime.now(),
            confidence_level=ConfidenceLevel.VERIFIED,
            confidence_score=0.9,
            validation_sources=["user_input"],
            preflight_status="PASSED",
            can_use=True,
        )
        content = "col1,col2\nval1,val2"
        injected = enforcer.inject_metadata_into_asset(content, metadata, "csv")
        extracted = enforcer.extract_metadata_from_asset(injected, "csv")
        assert extracted is not None
        assert extracted.asset_name == "csv_asset"

    def test_extract_metadata_from_asset_markdown(self):
        """Test extract metadata from Markdown content."""
        enforcer = AssetMetadataEnforcer()
        metadata = AssetMetadata(
            asset_name="md_asset",
            asset_type="markdown",
            generated_at=datetime.now(),
            confidence_level=ConfidenceLevel.VERIFIED,
            confidence_score=0.9,
            validation_sources=["gbp_api"],
            preflight_status="PASSED",
            can_use=True,
        )
        content = "# Title\nContent here"
        injected = enforcer.inject_metadata_into_asset(content, metadata, "markdown")
        extracted = enforcer.extract_metadata_from_asset(injected, "markdown")
        assert extracted is not None
        assert extracted.asset_name == "md_asset"


class TestAssetMetadataEnforcerFormatMetadata:
    """Tests for AssetMetadataEnforcer.format_metadata_for_report method."""

    def test_format_metadata_for_report_returns_readable_text(self):
        """Test format_metadata_for_report returns readable text."""
        metadata = AssetMetadata(
            asset_name="test_asset",
            asset_type="html",
            generated_at=datetime(2024, 1, 15, 10, 30),
            confidence_level=ConfidenceLevel.VERIFIED,
            confidence_score=0.9,
            validation_sources=["web_scraping", "gbp_api"],
            preflight_status="PASSED",
            can_use=True,
        )
        formatted = AssetMetadataEnforcer.format_metadata_for_report(metadata)
        assert isinstance(formatted, str)
        assert "test_asset" in formatted
        assert "html" in formatted
        assert "90%" in formatted or "0.9" in formatted
        assert "web_scraping" in formatted
        assert "PASSED" in formatted

    def test_format_metadata_with_disclaimer(self):
        """Test format includes disclaimer when present."""
        metadata = AssetMetadata(
            asset_name="test_asset",
            asset_type="html",
            generated_at=datetime.now(),
            confidence_level=ConfidenceLevel.ESTIMATED,
            confidence_score=0.6,
            validation_sources=["benchmark"],
            preflight_status="WARNING",
            can_use=True,
            disclaimer="Test disclaimer message",
        )
        formatted = AssetMetadataEnforcer.format_metadata_for_report(metadata)
        assert "Nota:" in formatted
        assert "Test disclaimer message" in formatted


class TestAssetMetadataEnforcerCheckUsability:
    """Tests for AssetMetadataEnforcer.check_asset_usability method."""

    def test_check_asset_usability_returns_correct_status_usable(self):
        """Test check_asset_usability returns correct status for usable asset."""
        metadata = AssetMetadata(
            asset_name="usable_asset",
            asset_type="html",
            generated_at=datetime.now(),
            confidence_level=ConfidenceLevel.VERIFIED,
            confidence_score=0.9,
            validation_sources=["web_scraping"],
            preflight_status="PASSED",
            can_use=True,
        )
        result = AssetMetadataEnforcer.check_asset_usability(metadata)
        assert result["usable"] is True
        assert "validado" in result["reason"].lower() or "ready" in result["reason"].lower()

    def test_check_asset_usability_returns_correct_status_blocked(self):
        """Test check_asset_usability returns correct status for blocked asset."""
        metadata = AssetMetadata(
            asset_name="blocked_asset",
            asset_type="html",
            generated_at=datetime.now(),
            confidence_level=ConfidenceLevel.UNKNOWN,
            confidence_score=0.3,
            validation_sources=[],
            preflight_status="BLOCKED",
            can_use=False,
        )
        result = AssetMetadataEnforcer.check_asset_usability(metadata)
        assert result["usable"] is False
        assert "Bloqueado" in result["reason"] or "errores" in result["reason"]

    def test_check_asset_usability_returns_warnings(self):
        """Test check_asset_usability returns warnings for estimated assets."""
        metadata = AssetMetadata(
            asset_name="estimated_asset",
            asset_type="html",
            generated_at=datetime.now(),
            confidence_level=ConfidenceLevel.ESTIMATED,
            confidence_score=0.7,
            validation_sources=["benchmark"],
            preflight_status="WARNING",
            can_use=True,
        )
        result = AssetMetadataEnforcer.check_asset_usability(metadata)
        assert result["usable"] is True
        assert len(result["warnings"]) > 0
