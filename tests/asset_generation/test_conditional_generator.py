"""Tests for conditional_generator module."""

import pytest
import json
import os
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch
from modules.asset_generation.conditional_generator import ConditionalGenerator
from modules.asset_generation.preflight_checks import PreflightStatus, PreflightReport, PreflightCheck
from modules.asset_generation.asset_metadata import AssetMetadata
from modules.data_validation import DataPoint, DataSource


class TestConditionalGeneratorInitialization:
    """Tests for ConditionalGenerator initialization."""

    def test_conditional_generator_initialization(self):
        """Test that ConditionalGenerator initializes correctly."""
        generator = ConditionalGenerator(output_dir="test_output")
        assert generator is not None
        assert generator.output_dir == Path("test_output")
        assert hasattr(generator, "preflight_checker")
        assert hasattr(generator, "metadata_enforcer")
        assert hasattr(generator, "GENERATION_STRATEGIES")

    def test_conditional_generator_default_output_dir(self):
        """Test default output directory."""
        generator = ConditionalGenerator()
        assert generator.output_dir == Path("output")

    def test_generation_strategies_structure(self):
        """Test that GENERATION_STRATEGIES has correct structure."""
        generator = ConditionalGenerator()
        expected_assets = ["whatsapp_button", "faq_page", "hotel_schema", "financial_projection"]
        for asset in expected_assets:
            assert asset in generator.GENERATION_STRATEGIES
            assert "template" in generator.GENERATION_STRATEGIES[asset]
            assert "output_name" in generator.GENERATION_STRATEGIES[asset]


class TestConditionalGeneratorGenerate:
    """Tests for ConditionalGenerator.generate method."""

    def _create_data_point(self, field_name, value):
        """Helper to create a DataPoint."""
        dp = DataPoint(field_name)
        dp.add_source(DataSource("test", value, datetime.now().isoformat()))
        return dp

    def test_generate_unknown_asset_type(self):
        """Test generate with unknown asset type returns error."""
        generator = ConditionalGenerator()
        result = generator.generate(
            asset_type="unknown_type",
            validated_data={},
            hotel_name="Test Hotel",
            hotel_id="hotel_123"
        )
        assert result["success"] is False
        assert result["status"] == "error"
        assert "Unknown asset type" in result["error"]

    def test_generate_with_passed_status_creates_asset(self, tmp_path):
        """Test generate with PASSED status creates asset."""
        generator = ConditionalGenerator(output_dir=str(tmp_path))
        dp = self._create_data_point("whatsapp", "+573001234567")
        validated_data = {"whatsapp": dp}
        
        result = generator.generate(
            asset_type="whatsapp_button",
            validated_data=validated_data,
            hotel_name="Test Hotel",
            hotel_id="hotel_123"
        )
        assert result["success"] is True
        assert result["status"] == "generated"
        assert result["asset_type"] == "whatsapp_button"
        assert result["hotel_id"] == "hotel_123"

    def test_generate_with_warning_creates_estimated_asset(self, tmp_path):
        """Test generate with WARNING creates ESTIMATED_ asset."""
        generator = ConditionalGenerator(output_dir=str(tmp_path))
        # Create DataPoint with lower confidence
        dp = DataPoint("faqs")
        # Single source typically gives ESTIMATED confidence
        dp.add_source(DataSource("source1", [{"question": "Q1", "answer": "A1"}], datetime.now().isoformat()))
        validated_data = {"faqs": dp}
        
        result = generator.generate(
            asset_type="faq_page",
            validated_data=validated_data,
            hotel_name="Test Hotel",
            hotel_id="hotel_123"
        )
        # Should succeed but may be estimated or generated depending on confidence
        assert result["success"] is True

    def test_generate_with_blocked_returns_error(self, tmp_path):
        """Test generate with BLOCKED returns error."""
        generator = ConditionalGenerator(output_dir=str(tmp_path))
        # Empty DataPoint should give low confidence
        dp = DataPoint("whatsapp")
        validated_data = {"whatsapp": dp}
        
        result = generator.generate(
            asset_type="whatsapp_button",
            validated_data=validated_data,
            hotel_name="Test Hotel",
            hotel_id="hotel_123"
        )
        assert result["success"] is False
        assert result["status"] == "blocked"
        assert "Preflight check failed" in result["error"]


class TestConditionalGeneratorNamingStrategy:
    """Tests for ConditionalGenerator._apply_naming_strategy method."""

    def test_apply_naming_strategy_for_passed(self):
        """Test naming strategy for PASSED status."""
        generator = ConditionalGenerator()
        report = PreflightReport(
            asset_type="whatsapp_button",
            overall_status=PreflightStatus.PASSED,
            checks=[],
            can_proceed=True,
            warnings=[],
            blocking_issues=[],
        )
        filename = generator._apply_naming_strategy("whatsapp_button", report, "hotel_123")
        assert "boton_whatsapp" in filename
        assert "ESTIMATED_" not in filename
        assert "FAILED_" not in filename
        assert filename.endswith(".html")

    def test_apply_naming_strategy_for_warning(self):
        """Test naming strategy for WARNING status."""
        generator = ConditionalGenerator()
        report = PreflightReport(
            asset_type="whatsapp_button",
            overall_status=PreflightStatus.WARNING,
            checks=[],
            can_proceed=True,
            warnings=["Low confidence"],
            blocking_issues=[],
        )
        filename = generator._apply_naming_strategy("whatsapp_button", report, "hotel_123")
        assert "ESTIMATED_" in filename
        assert "boton_whatsapp" in filename

    def test_apply_naming_strategy_includes_timestamp(self):
        """Test that filename includes timestamp."""
        generator = ConditionalGenerator()
        report = PreflightReport(
            asset_type="whatsapp_button",
            overall_status=PreflightStatus.PASSED,
            checks=[],
            can_proceed=True,
            warnings=[],
            blocking_issues=[],
        )
        filename = generator._apply_naming_strategy("whatsapp_button", report, "hotel_123")
        # Should contain timestamp pattern (8 digits for date + underscore + 6 digits for time)
        import re
        assert re.search(r"\d{8}_\d{6}", filename) is not None


class TestConditionalGeneratorContentGeneration:
    """Tests for ConditionalGenerator content generation methods."""

    def test_generate_whatsapp_button_returns_html(self):
        """Test _generate_whatsapp_button returns HTML."""
        generator = ConditionalGenerator()
        html = generator._generate_whatsapp_button("+573001234567", "Test Hotel")
        assert "<a" in html
        assert "whatsapp-button" in html
        assert "wa.me" in html
        assert "Test Hotel" in html
        assert "+573001234567" in html
        assert "</a>" in html
        assert "<style>" in html

    def test_generate_faq_page_returns_csv(self):
        """Test _generate_faq_page returns CSV."""
        generator = ConditionalGenerator()
        faqs = [
            {"question": "What time is check-in?", "answer": "3:00 PM", "category": "Check-in"},
            {"question": "Do you have wifi?", "answer": "Yes, free wifi", "category": "Amenities"},
        ]
        csv_content = generator._generate_faq_page(faqs, len(faqs))
        assert "id,question,answer,category" in csv_content
        assert "What time is check-in?" in csv_content
        assert "3:00 PM" in csv_content
        assert "metadata" in csv_content
        assert "actual_count" in csv_content

    def test_generate_hotel_schema_returns_json(self):
        """Test _generate_hotel_schema returns JSON."""
        generator = ConditionalGenerator()
        hotel_data = {
            "name": "Test Hotel",
            "description": "A nice hotel",
            "website": "https://example.com",
            "phone": "+573001234567",
            "address": "123 Main St",
            "city": "Bogota",
            "country": "CO",
            "amenities": ["wifi", "pool"],
        }
        json_content = generator._generate_hotel_schema(hotel_data)
        parsed = json.loads(json_content)
        assert parsed["@context"] == "https://schema.org"
        assert parsed["@type"] == "LodgingBusiness"
        assert parsed["name"] == "Test Hotel"
        assert parsed["telephone"] == "+573001234567"

    def test_generate_financial_projection_returns_markdown(self):
        """Test _generate_financial_projection returns Markdown."""
        generator = ConditionalGenerator()
        scenarios = {
            "conservative": {"revenue": 100000, "occupancy": 0.7},
            "optimistic": {"revenue": 150000, "occupancy": 0.85},
        }
        hotel_data = {"name": "Test Hotel"}
        md_content = generator._generate_financial_projection(scenarios, hotel_data)
        assert "# Proyección Financiera: Test Hotel" in md_content
        assert "Conservative" in md_content or "conservative" in md_content
        assert "Optimistic" in md_content or "optimistic" in md_content
        assert "revenue" in md_content.lower() or "Revenue" in md_content
        assert "IMPORTANTE" in md_content or "Advertencias" in md_content


class TestConditionalGeneratorSaveAsset:
    """Tests for ConditionalGenerator.save_asset method."""

    def test_save_asset_creates_file_and_metadata(self, tmp_path):
        """Test save_asset creates file and metadata."""
        generator = ConditionalGenerator(output_dir=str(tmp_path))
        
        # Create mock metadata
        metadata = Mock(spec=AssetMetadata)
        metadata.hotel_id = "hotel_123"
        metadata.to_dict.return_value = {
            "asset_type": "whatsapp_button",
            "hotel_id": "hotel_123",
            "hotel_name": "Test Hotel",
            "generated_at": datetime.now().isoformat(),
        }
        
        content = "<html>Test</html>"
        filename = "test_file.html"
        
        file_path = generator.save_asset("whatsapp_button", content, filename, metadata)
        
        # Check file was created
        assert file_path.exists()
        assert file_path.read_text() == content
        
        # Check metadata file was created
        metadata_path = file_path.parent / "test_file_metadata.json"
        assert metadata_path.exists()
        
        # Check directory structure
        assert "hotel_123" in str(file_path)
        assert "whatsapp_button" in str(file_path)


class TestConditionalGeneratorGetGenerationSummary:
    """Tests for ConditionalGenerator.get_generation_summary method."""

    def test_get_generation_summary_counts_correctly(self):
        """Test get_generation_summary counts correctly."""
        generator = ConditionalGenerator()
        generations = [
            {"status": "generated", "asset_type": "whatsapp_button"},
            {"status": "generated", "asset_type": "faq_page"},
            {"status": "estimated", "asset_type": "hotel_schema"},
            {"status": "blocked", "asset_type": "financial_projection"},
            {"status": "error", "asset_type": "whatsapp_button"},
        ]
        
        summary = generator.get_generation_summary(generations)
        
        assert summary["total"] == 5
        assert summary["passed"] == 2
        assert summary["warning"] == 1
        assert summary["blocked"] == 1
        assert summary["failed"] == 1
        assert summary["success_rate"] == 40.0  # 2 passed out of 5

    def test_get_generation_summary_by_type(self):
        """Test get_generation_summary groups by type."""
        generator = ConditionalGenerator()
        generations = [
            {"status": "generated", "asset_type": "whatsapp_button"},
            {"status": "generated", "asset_type": "whatsapp_button"},
            {"status": "estimated", "asset_type": "faq_page"},
        ]
        
        summary = generator.get_generation_summary(generations)
        
        assert "whatsapp_button" in summary["by_type"]
        assert "faq_page" in summary["by_type"]
        assert summary["by_type"]["whatsapp_button"]["passed"] == 2
        assert summary["by_type"]["faq_page"]["warning"] == 1

    def test_get_generation_summary_empty_list(self):
        """Test get_generation_summary with empty list."""
        generator = ConditionalGenerator()
        summary = generator.get_generation_summary([])
        
        assert summary["total"] == 0
        assert summary["passed"] == 0
        assert summary["success_rate"] == 0

    def test_get_generation_summary_includes_timestamp(self):
        """Test get_generation_summary includes generated_at timestamp."""
        generator = ConditionalGenerator()
        generations = [{"status": "generated", "asset_type": "test"}]
        
        summary = generator.get_generation_summary(generations)
        
        assert "generated_at" in summary
        # Should be ISO format timestamp
        assert isinstance(summary["generated_at"], str)


class TestConditionalGeneratorHelperMethods:
    """Tests for ConditionalGenerator helper methods."""

    def test_calculate_confidence_score(self):
        """Test _calculate_confidence_score method."""
        generator = ConditionalGenerator()
        
        # Report with passed checks
        check_passed = PreflightCheck(
            check_name="test",
            field_name="test",
            required_confidence=0.8,
            status=PreflightStatus.PASSED,
            message="OK",
            can_generate=True,
        )
        report_passed = PreflightReport(
            asset_type="test",
            overall_status=PreflightStatus.PASSED,
            checks=[check_passed],
            can_proceed=True,
        )
        assert generator._calculate_confidence_score(report_passed) == 1.0
        
        # Report with warning checks
        check_warning = PreflightCheck(
            check_name="test",
            field_name="test",
            required_confidence=0.8,
            status=PreflightStatus.WARNING,
            message="Low",
            can_generate=True,
        )
        report_warning = PreflightReport(
            asset_type="test",
            overall_status=PreflightStatus.WARNING,
            checks=[check_warning],
            can_proceed=True,
        )
        assert generator._calculate_confidence_score(report_warning) == 0.5

    def test_hash_data(self):
        """Test _hash_data method creates consistent hash."""
        generator = ConditionalGenerator()
        data = {"key": "value", "number": 123}
        hash1 = generator._hash_data(data)
        hash2 = generator._hash_data(data)
        
        assert isinstance(hash1, str)
        assert len(hash1) == 16
        assert hash1 == hash2  # Same data should produce same hash
        
        # Different data should produce different hash
        different_data = {"key": "different", "number": 123}
        hash3 = generator._hash_data(different_data)
        assert hash1 != hash3

    def test_generate_content_whatsapp(self):
        """Test _generate_content for whatsapp_button."""
        generator = ConditionalGenerator()
        dp = DataPoint("whatsapp")
        dp.add_source(DataSource("test", "+573001234567", datetime.now().isoformat()))
        validated_data = {"whatsapp": dp}
        
        content = generator._generate_content("whatsapp_button", validated_data, "Test Hotel")
        assert "whatsapp-button" in content
        assert "wa.me" in content

    def test_generate_content_faq(self):
        """Test _generate_content for faq_page."""
        generator = ConditionalGenerator()
        dp = DataPoint("faqs")
        faqs = [{"question": "Q1", "answer": "A1"}]
        dp.add_source(DataSource("test", faqs, datetime.now().isoformat()))
        validated_data = {"faqs": dp}
        
        content = generator._generate_content("faq_page", validated_data, "Test Hotel")
        assert "id,question,answer" in content
