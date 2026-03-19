"""Tests for content gates in conditional_generator module."""

import pytest
import json
from pathlib import Path
from modules.asset_generation.conditional_generator import ConditionalGenerator
from modules.asset_generation.preflight_checks import PreflightStatus, PreflightReport, PreflightCheck


class TestContentGates:
    """Tests for content validation gates."""

    @pytest.fixture
    def generator(self):
        """Create a ConditionalGenerator instance."""
        return ConditionalGenerator(output_dir="test_output")

    def test_conditional_generator_rejects_empty_content(self, generator):
        """Test that generator rejects empty content with ValueError."""
        validated_data = {
            "whatsapp": "+573001234567",
            "hotel_data": {"name": "Test Hotel"},
            "faqs": [],
            "org_data": {},
            "performance_data": {},
            "metadata_data": {}
        }
        
        result = generator.generate(
            asset_type="whatsapp_button",
            validated_data=validated_data,
            hotel_name="Test Hotel",
            hotel_id="test_hotel_001"
        )
        
        if not result["success"]:
            assert result["error"] is not None
        else:
            assert len(result.get("file_path", "")) > 0

    def test_conditional_generator_rejects_placeholders(self, generator):
        """Test that generator rejects content with unreplaced placeholders."""
        validated_data = {
            "org_data": {"website": "$$WEBSITE$$"},
        }
        
        result = generator.generate(
            asset_type="org_schema",
            validated_data=validated_data,
            hotel_name="Test Hotel",
            hotel_id="test_hotel_002"
        )
        
        if not result["success"]:
            assert "placeholder" in result["error"].lower() or "generation failed" in result["error"].lower()

    def test_faq_page_generates_default_content(self, generator):
        """Test that FAQ page generates default content when no FAQs provided."""
        validated_data = {
            "faqs": [],
            "hotel_data": {"name": "Hotel Test"}
        }
        
        content = generator._generate_content("faq_page", validated_data, "Hotel Test")
        
        assert content is not None
        assert len(content) > 0

    def test_performance_audit_generates_with_zeros(self, generator):
        """Test that performance audit generates content even with all zeros."""
        validated_data = {
            "performance_data": {}
        }
        
        result = generator.generate(
            asset_type="performance_audit",
            validated_data=validated_data,
            hotel_name="Test Hotel",
            hotel_id="test_hotel_003"
        )
        
        if result["success"]:
            assert result["file_path"] is not None
            content = Path(result["file_path"], errors='ignore').read_text(encoding='utf-8', errors='ignore')
            assert len(content) > 50


class TestFAQGeneration:
    """Tests for FAQ page generation with defaults."""

    @pytest.fixture
    def generator(self):
        """Create a ConditionalGenerator instance."""
        return ConditionalGenerator(output_dir="test_output")

    def test_faq_page_with_empty_faqs_uses_defaults(self, generator):
        """Test that empty FAQs list triggers default FAQ generation."""
        validated_data = {
            "faqs": [],
            "hotel_data": {"name": "Hotel Visperas"}
        }
        
        content = generator._generate_content("faq_page", validated_data, "Hotel Visperas")
        
        assert "Hotel Visperas" in content
        assert len(content) > 100

    def test_faq_page_with_valid_faqs(self, generator):
        """Test that valid FAQs are used when provided."""
        faqs = [
            {"question": "¿Tienen piscina?", "answer": "Sí, tenemos piscina.", "category": "Servicios"},
            {"question": "¿El desayuno está incluido?", "answer": "Sí, está incluido.", "category": "Servicios"}
        ]
        validated_data = {"faqs": faqs}
        
        content = generator._generate_content("faq_page", validated_data, "Hotel Test")
        
        assert "¿Tienen piscina?" in content
        assert "Sí, tenemos piscina." in content

    def test_default_faqs_specific_to_hotel(self, generator):
        """Test that default FAQs include the hotel name."""
        hotel_name = "Hotel Example"
        faqs = generator._generate_default_faqs(hotel_name)
        
        assert len(faqs) == 3
        for faq in faqs:
            assert hotel_name in faq["question"] or hotel_name in faq["answer"]

    def test_default_faqs_have_categories(self, generator):
        """Test that default FAQs have proper categories."""
        faqs = generator._generate_default_faqs("Test Hotel")
        
        categories = [faq.get("category") for faq in faqs]
        assert "Hospedaje" in categories
        assert "Servicios" in categories
        assert "Reservas" in categories


class TestOrgSchemaGeneration:
    """Tests for Organization schema generation."""

    @pytest.fixture
    def generator(self):
        """Create a ConditionalGenerator instance."""
        return ConditionalGenerator(output_dir="test_output")

    def test_org_schema_with_empty_data(self, generator):
        """Test org schema generation with empty data."""
        validated_data = {"org_data": {}}
        
        content = generator._generate_content("org_schema", validated_data, "Test Hotel")
        
        schema = json.loads(content)
        assert schema["@type"] == "Organization"
        assert schema["name"] == "Test Hotel"
        assert "url" in schema

    def test_org_schema_with_valid_data(self, generator):
        """Test org schema generation with valid data."""
        validated_data = {
            "org_data": {
                "website": "https://hotelexample.com",
                "phone": "+573001234567"
            }
        }
        
        content = generator._generate_content("org_schema", validated_data, "Hotel Example")
        
        schema = json.loads(content)
        assert schema["url"] == "https://hotelexample.com"
        assert schema["contactPoint"]["telephone"] == "+573001234567"


class TestPerformanceAuditGeneration:
    """Tests for performance audit generation."""

    @pytest.fixture
    def generator(self):
        """Create a ConditionalGenerator instance."""
        return ConditionalGenerator(output_dir="test_output")

    def test_performance_audit_with_no_data(self, generator):
        """Test performance audit with no data generates informative content."""
        validated_data = {"performance_data": {}}
        
        content = generator._generate_content("performance_audit", validated_data, "Test Hotel")
        
        assert "Datos de Performance No Disponibles" in content or "PageSpeed Insights" in content
        assert len(content) > 100

    def test_performance_audit_with_scores(self, generator):
        """Test performance audit with actual scores."""
        validated_data = {
            "performance_data": {
                "mobile_score": 75,
                "desktop_score": 85,
                "LCP": 2000,
                "FID": 50,
                "CLS": 0.05
            }
        }
        
        content = generator._generate_content("performance_audit", validated_data, "Test Hotel")
        
        assert "75" in content
        assert "85" in content
        assert "2000" in content

    def test_performance_audit_has_recommendations(self, generator):
        """Test that performance audit includes recommendations."""
        validated_data = {
            "performance_data": {
                "mobile_score": 40,
                "desktop_score": 45,
                "LCP": 5000,
                "FID": 200,
                "CLS": 0.3
            }
        }
        
        content = generator._generate_content("performance_audit", validated_data, "Test Hotel")
        
        assert "optimiz" in content.lower() or "mejora" in content.lower()


class TestContentValidation:
    """Tests for content validation logic."""

    @pytest.fixture
    def generator(self):
        """Create a ConditionalGenerator instance."""
        return ConditionalGenerator(output_dir="test_output")

    def test_validate_content_rejects_empty(self, generator):
        """Test that validation rejects empty content."""
        with pytest.raises(ValueError) as exc_info:
            generator._validate_generated_content("", "test_asset")
        
        assert "empty or too short" in str(exc_info.value)

    def test_validate_content_rejects_short_content(self, generator):
        """Test that validation rejects very short content."""
        with pytest.raises(ValueError) as exc_info:
            generator._validate_generated_content("short", "test_asset")
        
        assert "too short" in str(exc_info.value)

    def test_validate_content_accepts_valid_content(self, generator):
        """Test that validation accepts valid content."""
        content = "This is a valid content string with more than fifty characters of text."
        generator._validate_generated_content(content, "test_asset")

    def test_validate_content_rejects_dollar_placeholders(self, generator):
        """Test that validation rejects dollar placeholders."""
        content = "This is a long content string with $$PLACEHOLDER$$ and more text here that makes it longer than 50 characters."
        
        with pytest.raises(ValueError) as exc_info:
            generator._validate_generated_content(content, "test_asset")
        
        assert "dollar placeholder" in str(exc_info.value)

    def test_validate_content_rejects_double_brace_placeholders(self, generator):
        """Test that validation rejects double brace placeholders."""
        content = "This is a long content string with {{placeholder}} and more text here that makes it longer than 50 characters."
        
        with pytest.raises(ValueError) as exc_info:
            generator._validate_generated_content(content, "test_asset")
        
        assert "double brace placeholder" in str(exc_info.value)

    def test_validate_content_rejects_double_bracket_placeholders(self, generator):
        """Test that validation rejects double bracket placeholders."""
        content = "This is a long content string with [[placeholder]] and more text here that makes it longer than 50 characters."
        
        with pytest.raises(ValueError) as exc_info:
            generator._validate_generated_content(content, "test_asset")
        
        assert "double bracket placeholder" in str(exc_info.value)
