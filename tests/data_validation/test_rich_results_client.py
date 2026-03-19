"""Tests for Rich Results Test Client."""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

from modules.data_validation.external_apis.rich_results_client import (
    RichResultsTestClient,
    RichResultsTestResult,
    SchemaValidationResult,
    SchemaType,
)
from modules.data_validation.confidence_taxonomy import ConfidenceLevel


class TestRichResultsClient:
    """Tests for RichResultsTestClient."""
    
    def test_init_with_api_key(self):
        """Test initialization with API key."""
        client = RichResultsTestClient(api_key="test_key")
        assert client.api_key == "test_key"
        assert client.is_available is True
    
    def test_init_without_api_key(self, monkeypatch):
        """Test initialization without API key."""
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        monkeypatch.delenv("RICH_RESULTS_API_KEY", raising=False)
        
        client = RichResultsTestClient()
        assert client.is_available is False
    
    def test_test_url_without_api_key(self, monkeypatch):
        """Test that URL test returns error without API key."""
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        client = RichResultsTestClient()
        
        result = client.test_url("https://example.com")
        
        assert result.status == "ERROR"
        assert "API key not configured" in result.error_message


class TestSchemaValidation:
    """Tests for schema validation logic."""
    
    def test_validate_hotel_schema_complete(self):
        """Test validating a complete Hotel schema."""
        client = RichResultsTestClient(api_key="test")
        
        data = {
            "@type": "Hotel",
            "name": "Test Hotel",
            "address": {
                "@type": "PostalAddress",
                "streetAddress": "123 Main St"
            },
            "telephone": "+5712345678",
            "image": "https://example.com/image.jpg",
            "url": "https://example.com",
            "priceRange": "$$"
        }
        
        errors, warnings = client._validate_hotel_schema(data)
        
        assert len(errors) == 0
        # Should have warnings for recommended fields that are present
        assert len(warnings) == 0
    
    def test_validate_hotel_schema_missing_required(self):
        """Test validating Hotel schema with missing required fields."""
        client = RichResultsTestClient(api_key="test")
        
        data = {
            "@type": "Hotel",
            "telephone": "+5712345678"
            # Missing name and address
        }
        
        errors, warnings = client._validate_hotel_schema(data)
        
        assert len(errors) == 2
        assert any(e["field"] == "name" for e in errors)
        assert any(e["field"] == "address" for e in errors)
    
    def test_validate_hotel_schema_missing_recommended(self):
        """Test validating Hotel schema with missing recommended fields."""
        client = RichResultsTestClient(api_key="test")
        
        data = {
            "@type": "Hotel",
            "name": "Test Hotel",
            "address": "123 Main St"
        }
        
        errors, warnings = client._validate_hotel_schema(data)
        
        assert len(errors) == 0
        # Should warn about missing recommended fields
        assert len(warnings) > 0
        assert any(w["field"] == "telephone" for w in warnings)
        assert any(w["field"] == "image" for w in warnings)
    
    def test_validate_faq_schema_valid(self):
        """Test validating a valid FAQPage schema."""
        client = RichResultsTestClient(api_key="test")
        
        data = {
            "@type": "FAQPage",
            "mainEntity": [
                {"@type": "Question", "name": "Q1"},
                {"@type": "Question", "name": "Q2"},
                {"@type": "Question", "name": "Q3"}
            ]
        }
        
        errors, warnings = client._validate_faq_schema(data)
        
        assert len(errors) == 0
        assert len(warnings) == 0
    
    def test_validate_faq_schema_too_few_questions(self):
        """Test validating FAQPage with too few questions."""
        client = RichResultsTestClient(api_key="test")
        
        data = {
            "@type": "FAQPage",
            "mainEntity": [
                {"@type": "Question", "name": "Q1"}
            ]
        }
        
        errors, warnings = client._validate_faq_schema(data)
        
        assert len(errors) == 0
        assert len(warnings) == 1
        assert "only 1 questions" in warnings[0]["message"]
    
    def test_validate_faq_schema_missing_main_entity(self):
        """Test validating FAQPage without mainEntity."""
        client = RichResultsTestClient(api_key="test")
        
        data = {
            "@type": "FAQPage"
        }
        
        errors, warnings = client._validate_faq_schema(data)
        
        assert len(errors) == 1
        assert errors[0]["field"] == "mainEntity"
    
    def test_validate_org_schema_valid(self):
        """Test validating a valid Organization schema."""
        client = RichResultsTestClient(api_key="test")
        
        data = {
            "@type": "Organization",
            "name": "Test Org",
            "logo": "https://example.com/logo.png"
        }
        
        errors, warnings = client._validate_org_schema(data)
        
        assert len(errors) == 0
        assert len(warnings) == 0
    
    def test_validate_org_schema_missing_name(self):
        """Test validating Organization without name."""
        client = RichResultsTestClient(api_key="test")
        
        data = {
            "@type": "Organization",
            "logo": "https://example.com/logo.png"
        }
        
        errors, warnings = client._validate_org_schema(data)
        
        assert len(errors) == 1
        assert errors[0]["field"] == "name"
    
    def test_validate_org_schema_missing_logo(self):
        """Test validating Organization without logo."""
        client = RichResultsTestClient(api_key="test")
        
        data = {
            "@type": "Organization",
            "name": "Test Org"
        }
        
        errors, warnings = client._validate_org_schema(data)
        
        assert len(errors) == 0
        assert len(warnings) == 1
        assert warnings[0]["field"] == "logo"


class TestSchemaParsing:
    """Tests for schema parsing from JSON-LD."""
    
    def test_parse_single_schema(self):
        """Test parsing a single schema object."""
        client = RichResultsTestClient(api_key="test")
        
        data = {
            "@type": "Hotel",
            "name": "Test Hotel",
            "address": "123 Main St"
        }
        
        result = client._validate_single_schema(data)
        
        assert result is not None
        assert result.schema_type == "Hotel"
        assert result.detected is True
        assert result.properties["name"] == "Test Hotel"
    
    def test_parse_graph_syntax(self):
        """Test parsing @graph syntax with multiple schemas."""
        client = RichResultsTestClient(api_key="test")
        
        data = {
            "@context": "https://schema.org",
            "@graph": [
                {"@type": "Hotel", "name": "Test Hotel", "address": "123 Main St"},
                {"@type": "Organization", "name": "Test Org"}
            ]
        }
        
        results = client._validate_schema(data)
        
        assert len(results) == 2
        assert results[0].schema_type == "Hotel"
        assert results[1].schema_type == "Organization"
    
    def test_parse_namespaced_type(self):
        """Test parsing schema type with namespace prefix."""
        client = RichResultsTestClient(api_key="test")
        
        data = {
            "@type": "schema:Hotel",
            "name": "Test Hotel",
            "address": "123 Main St"
        }
        
        result = client._validate_single_schema(data)
        
        assert result is not None
        assert result.schema_type == "Hotel"
    
    def test_parse_empty_type_returns_none(self):
        """Test that empty @type returns None."""
        client = RichResultsTestClient(api_key="test")
        
        data = {
            "name": "Test"
        }
        
        result = client._validate_single_schema(data)
        
        assert result is None


class TestExtractProperties:
    """Tests for property extraction."""
    
    def test_extract_basic_properties(self):
        """Test extracting basic schema properties."""
        client = RichResultsTestClient(api_key="test")
        
        data = {
            "name": "Test Hotel",
            "telephone": "+5712345678",
            "url": "https://example.com",
            "priceRange": "$$",
            "description": "A nice hotel"
        }
        
        props = client._extract_properties(data)
        
        assert props["name"] == "Test Hotel"
        assert props["telephone"] == "+5712345678"
        assert props["url"] == "https://example.com"
    
    def test_extract_nested_address(self):
        """Test extracting nested address object."""
        client = RichResultsTestClient(api_key="test")
        
        data = {
            "name": "Test Hotel",
            "address": {
                "@type": "PostalAddress",
                "streetAddress": "123 Main St",
                "addressLocality": "Bogota"
            }
        }
        
        props = client._extract_properties(data)
        
        assert "address" in props
        assert "123 Main St" in props["address"]


class TestHotelSchemaReport:
    """Tests for get_hotel_schema_report method."""
    
    @patch.object(RichResultsTestClient, '_analyze_page_directly')
    def test_report_with_hotel_schema(self, mock_analyze):
        """Test report when Hotel schema is present."""
        client = RichResultsTestClient(api_key="test")
        
        mock_result = RichResultsTestResult(
            url="https://example.com",
            status="COMPLETE",
            schemas=[
                SchemaValidationResult(
                    schema_type="Hotel",
                    detected=True,
                    valid=True,
                    properties={"name": "Test Hotel"}
                )
            ]
        )
        mock_analyze.return_value = mock_result
        
        report = client.get_hotel_schema_report("https://example.com")
        
        assert report["has_hotel_schema"] is True
        assert report["schema_valid"] is True
        assert report["confidence"] == ConfidenceLevel.VERIFIED.value
    
    @patch.object(RichResultsTestClient, '_analyze_page_directly')
    def test_report_with_localbusiness_fallback(self, mock_analyze):
        """Test report falls back to LocalBusiness schema."""
        client = RichResultsTestClient(api_key="test")
        
        mock_result = RichResultsTestResult(
            url="https://example.com",
            status="COMPLETE",
            schemas=[
                SchemaValidationResult(
                    schema_type="LocalBusiness",
                    detected=True,
                    valid=True,
                    properties={"name": "Test Business"}
                )
            ]
        )
        mock_analyze.return_value = mock_result
        
        report = client.get_hotel_schema_report("https://example.com")
        
        assert report["has_hotel_schema"] is False
        assert report["has_localbusiness_schema"] is True
        assert report["confidence"] == ConfidenceLevel.ESTIMATED.value
    
    @patch.object(RichResultsTestClient, '_analyze_page_directly')
    def test_report_no_schema(self, mock_analyze):
        """Test report when no schema is present."""
        client = RichResultsTestClient(api_key="test")
        
        mock_result = RichResultsTestResult(
            url="https://example.com",
            status="COMPLETE",
            schemas=[]
        )
        mock_analyze.return_value = mock_result
        
        report = client.get_hotel_schema_report("https://example.com")
        
        assert report["has_hotel_schema"] is False
        assert report["confidence"] == ConfidenceLevel.UNKNOWN.value
    
    @patch.object(RichResultsTestClient, '_analyze_page_directly')
    def test_report_with_lodgingbusiness_schema(self, mock_analyze):
        """Test report recognizes LodgingBusiness as valid hotel schema."""
        client = RichResultsTestClient(api_key="test")
        
        mock_result = RichResultsTestResult(
            url="https://example.com",
            status="COMPLETE",
            schemas=[
                SchemaValidationResult(
                    schema_type="LodgingBusiness",
                    detected=True,
                    valid=True,
                    properties={"name": "Hotel Vísperas"}
                )
            ]
        )
        mock_analyze.return_value = mock_result
        
        report = client.get_hotel_schema_report("https://example.com")
        
        assert report["has_hotel_schema"] is True
        assert report["has_lodgingbusiness_schema"] is True
        assert report["confidence"] == ConfidenceLevel.ESTIMATED.value


class TestFaqSchemaReport:
    """Tests for get_faq_schema_report method."""
    
    @patch.object(RichResultsTestClient, '_analyze_page_directly')
    def test_report_with_faq_schema(self, mock_analyze):
        """Test report when FAQPage schema is present."""
        client = RichResultsTestClient(api_key="test")
        
        mock_result = RichResultsTestResult(
            url="https://example.com",
            status="COMPLETE",
            schemas=[
                SchemaValidationResult(
                    schema_type="FAQPage",
                    detected=True,
                    valid=True,
                    properties={"mainEntity": [1, 2, 3]}
                )
            ]
        )
        mock_analyze.return_value = mock_result
        
        report = client.get_faq_schema_report("https://example.com")
        
        assert report["has_faq_schema"] is True
        assert report["schema_valid"] is True
        assert report["confidence"] == ConfidenceLevel.VERIFIED.value
    
    @patch.object(RichResultsTestClient, '_analyze_page_directly')
    def test_report_no_faq_schema(self, mock_analyze):
        """Test report when FAQPage schema is not present."""
        client = RichResultsTestClient(api_key="test")
        
        mock_result = RichResultsTestResult(
            url="https://example.com",
            status="COMPLETE",
            schemas=[]
        )
        mock_analyze.return_value = mock_result
        
        report = client.get_faq_schema_report("https://example.com")
        
        assert report["has_faq_schema"] is False
        assert report["confidence"] == ConfidenceLevel.UNKNOWN.value
