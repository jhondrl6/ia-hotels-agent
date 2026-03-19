"""
Tests for the confidence_taxonomy module.

This module provides comprehensive test coverage for the confidence taxonomy system,
including confidence levels, data sources, validation results, and the core
ConfidenceTaxonomy and DataPoint classes.
"""

import pytest
from datetime import datetime
from modules.data_validation.confidence_taxonomy import (
    ConfidenceLevel,
    DataSource,
    ValidationResult,
    ConfidenceTaxonomy,
    DataPoint,
)


class TestConfidenceLevel:
    """Tests for the ConfidenceLevel enum."""

    @pytest.mark.parametrize("level,expected_value", [
        (ConfidenceLevel.VERIFIED, "verified"),
        (ConfidenceLevel.ESTIMATED, "estimated"),
        (ConfidenceLevel.CONFLICT, "conflict"),
        (ConfidenceLevel.UNKNOWN, "unknown"),
    ])
    def test_level_values(self, level, expected_value):
        """Test that enum values are correct."""
        assert level.value == expected_value

    @pytest.mark.parametrize("level_name", [
        "VERIFIED", "ESTIMATED", "CONFLICT", "UNKNOWN"
    ])
    def test_all_levels_exist(self, level_name):
        """Test that all confidence levels exist in the enum."""
        assert hasattr(ConfidenceLevel, level_name)


class TestDataSource:
    """Tests for the DataSource dataclass."""

    def test_creation_with_all_fields(self):
        """Test creating a DataSource with all fields specified."""
        metadata = {"url": "https://example.com", "scraped_at": "2024-01-01"}
        source = DataSource(
            source_type="web_scraping",
            value="Test Hotel",
            timestamp="2024-01-15T10:00:00",
            metadata=metadata,
        )
        assert source.source_type == "web_scraping"
        assert source.value == "Test Hotel"
        assert source.timestamp == "2024-01-15T10:00:00"
        assert source.metadata == metadata

    def test_default_metadata(self):
        """Test that metadata defaults to an empty dict."""
        source = DataSource(
            source_type="user_input",
            value="123",
            timestamp="2024-01-15T10:00:00",
        )
        assert source.metadata == {}


class TestValidationResult:
    """Tests for the ValidationResult dataclass."""

    def test_creation_with_all_fields(self):
        """Test creating a ValidationResult with all fields."""
        sources = [
            DataSource("web_scraping", "Value", "2024-01-15", {"url": "test"})
        ]
        result = ValidationResult(
            confidence_level=ConfidenceLevel.VERIFIED,
            final_value="Final Value",
            sources_used=sources,
            match_percentage=100.0,
            discrepancies=["diff1", "diff2"],
            requires_manual_review=True,
            can_use_in_assets=True,
            disclaimer="Test disclaimer",
            icon="✓",
        )
        assert result.confidence_level == ConfidenceLevel.VERIFIED
        assert result.final_value == "Final Value"
        assert result.sources_used == sources
        assert result.match_percentage == 100.0
        assert result.discrepancies == ["diff1", "diff2"]
        assert result.requires_manual_review is True
        assert result.can_use_in_assets is True
        assert result.disclaimer == "Test disclaimer"
        assert result.icon == "✓"

    def test_default_values(self):
        """Test that ValidationResult uses correct default values."""
        sources = [DataSource("api", "val", "2024-01-15")]
        result = ValidationResult(
            confidence_level=ConfidenceLevel.UNKNOWN,
            final_value=None,
            sources_used=sources,
            match_percentage=0.0,
        )
        assert result.discrepancies == []
        assert result.requires_manual_review is False
        assert result.can_use_in_assets is False
        assert result.disclaimer is None
        assert result.icon == ""


class TestConfidenceTaxonomy:
    """Tests for the ConfidenceTaxonomy class."""

    @pytest.mark.parametrize("level,expected_info", [
        (ConfidenceLevel.VERIFIED, {
            "description": "Data confirmed by multiple independent sources with high consistency",
            "min_sources": 2,
            "min_match_percentage": 90.0,
            "can_use_in_assets": True,
            "requires_review": False,
            "icon": "✓",
            "color": "green",
        }),
        (ConfidenceLevel.ESTIMATED, {
            "description": "Data from single reliable source or multiple sources with minor discrepancies",
            "min_sources": 1,
            "min_match_percentage": 70.0,
            "can_use_in_assets": True,
            "requires_review": False,
            "icon": "~",
            "color": "yellow",
        }),
        (ConfidenceLevel.CONFLICT, {
            "description": "Significant discrepancies between sources requiring manual resolution",
            "min_sources": 2,
            "min_match_percentage": 0.0,
            "can_use_in_assets": False,
            "requires_review": True,
            "icon": "⚠",
            "color": "orange",
        }),
        (ConfidenceLevel.UNKNOWN, {
            "description": "No reliable data sources available",
            "min_sources": 0,
            "min_match_percentage": 0.0,
            "can_use_in_assets": False,
            "requires_review": True,
            "icon": "?",
            "color": "gray",
        }),
    ])
    def test_get_taxonomy_info(self, level, expected_info):
        """Test getting taxonomy info for all confidence levels."""
        info = ConfidenceTaxonomy.get_taxonomy_info(level)
        assert info["description"] == expected_info["description"]
        assert info["min_sources"] == expected_info["min_sources"]
        assert info["min_match_percentage"] == expected_info["min_match_percentage"]
        assert info["can_use_in_assets"] == expected_info["can_use_in_assets"]
        assert info["requires_review"] == expected_info["requires_review"]
        assert info["icon"] == expected_info["icon"]
        assert info["color"] == expected_info["color"]

    @pytest.mark.parametrize("values,expected_pct", [
        (["test_value"], 100.0),
        (["value", "value"], 100.0),
        (["value1", "value2"], 0.0),
        (["same", "same", "different"], pytest.approx(33.33, rel=0.01)),
        ([], 0.0),
    ])
    def test_calculate_match_percentage(self, values, expected_pct):
        """Test match percentage calculation."""
        result = ConfidenceTaxonomy.calculate_match_percentage(values)
        assert result == expected_pct

    @pytest.mark.parametrize("phone_input,expected", [
        ("(311) 397-3744", "3113973744"),
        ("+573113973744", "3113973744"),
        ("311-397-3744", "3113973744"),
        ("3113973744", "3113973744"),
        ("311 397 3744", "3113973744"),
        ("", None),
        (None, None),
    ])
    def test_normalize_phone(self, phone_input, expected):
        """Test phone normalization."""
        result = ConfidenceTaxonomy._normalize_phone(phone_input)
        assert result == expected

    @pytest.mark.parametrize("sources,match_pct,expected_level", [
        ([], 0.0, ConfidenceLevel.UNKNOWN),
        ([DataSource("web", "val", "2024-01-15")], 100.0, ConfidenceLevel.ESTIMATED),
        ([
            DataSource("web", "val", "2024-01-15"),
            DataSource("api", "val", "2024-01-15"),
        ], 100.0, ConfidenceLevel.VERIFIED),
        ([
            DataSource("web", "val1", "2024-01-15"),
            DataSource("api", "val2", "2024-01-15"),
        ], 50.0, ConfidenceLevel.CONFLICT),
        ([
            DataSource("web", "val", "2024-01-15"),
            DataSource("api", "val", "2024-01-15"),
        ], 75.0, ConfidenceLevel.ESTIMATED),
    ])
    def test_determine_confidence_level(self, sources, match_pct, expected_level):
        """Test confidence level determination."""
        result = ConfidenceTaxonomy.determine_confidence_level(sources, match_pct)
        assert result == expected_level

    @pytest.mark.parametrize("level,sources,expect_disclaimer", [
        (ConfidenceLevel.VERIFIED, [DataSource("web", "val", "2024-01-15")], False),
        (ConfidenceLevel.ESTIMATED,
         [DataSource("web_scraping", "val", "2024-01-15"), DataSource("api_external", "val", "2024-01-15")],
         True),
        (ConfidenceLevel.CONFLICT,
         [DataSource("web", "val1", "2024-01-15"), DataSource("api", "val2", "2024-01-15")],
         True),
        (ConfidenceLevel.UNKNOWN, [], True),
    ])
    def test_generate_disclaimer(self, level, sources, expect_disclaimer):
        """Test disclaimer generation."""
        result = ConfidenceTaxonomy._generate_disclaimer(level, "test_field", sources)
        if expect_disclaimer:
            assert result is not None
            if level == ConfidenceLevel.ESTIMATED:
                assert "Dato estimado basado en:" in result
            elif level == ConfidenceLevel.CONFLICT:
                assert "Conflicto detectado" in result
                assert "Requiere revisión manual" in result
            elif level == ConfidenceLevel.UNKNOWN:
                assert "Sin datos disponibles" in result
        else:
            assert result is None


class TestDataPoint:
    """Tests for the DataPoint class."""

    def test_init(self):
        """Test DataPoint initialization."""
        dp = DataPoint("hotel_name")
        assert dp.field_name == "hotel_name"
        assert dp.value is None
        assert dp.confidence == ConfidenceLevel.UNKNOWN
        assert dp.can_use is False

    def test_add_source(self):
        """Test adding a source to a DataPoint."""
        dp = DataPoint("hotel_name")
        source = DataSource("web_scraping", "Test Hotel", "2024-01-15")
        dp.add_source(source)
        
        assert len(dp._sources) == 1
        assert dp._sources[0].value == "Test Hotel"
        # After adding source, should recalculate
        assert dp.value == "Test Hotel"
        assert dp.confidence == ConfidenceLevel.ESTIMATED

    def test_add_multiple_sources(self):
        """Test adding multiple sources."""
        dp = DataPoint("phone")
        dp.add_source(DataSource("web", "311-397-3744", "2024-01-15"))
        dp.add_source(DataSource("api", "3113973744", "2024-01-15"))
        
        assert len(dp._sources) == 2
        # Phone numbers should match after normalization
        assert dp.confidence == ConfidenceLevel.VERIFIED

    @pytest.mark.parametrize("source_value,expected_value", [
        ("test@example.com", "test@example.com"),
        (None, None),
    ])
    def test_value_property(self, source_value, expected_value):
        """Test the value property returns correct final value."""
        dp = DataPoint("email")
        if source_value:
            dp.add_source(DataSource("web", source_value, "2024-01-15"))
        assert dp.value == expected_value

    @pytest.mark.parametrize("has_sources,expected_confidence", [
        (False, ConfidenceLevel.UNKNOWN),
        (True, ConfidenceLevel.ESTIMATED),
    ])
    def test_confidence_property(self, has_sources, expected_confidence):
        """Test the confidence property returns correct level."""
        dp = DataPoint("name")
        if has_sources:
            dp.add_source(DataSource("web", "Hotel", "2024-01-15"))
        assert dp.confidence == expected_confidence

    @pytest.mark.parametrize("sources,expected_can_use", [
        ([
            DataSource("web", "Hotel Name", "2024-01-15"),
            DataSource("api", "Hotel Name", "2024-01-15"),
        ], True),  # VERIFIED
        ([
            DataSource("web", "Hotel Name", "2024-01-15"),
        ], True),  # ESTIMATED
        ([
            DataSource("web", "Name A", "2024-01-15"),
            DataSource("api", "Name B", "2024-01-15"),
        ], False),  # CONFLICT
        ([], False),  # UNKNOWN
    ])
    def test_can_use_property(self, sources, expected_can_use):
        """Test can_use property returns correct value."""
        dp = DataPoint("test_field")
        for source in sources:
            dp.add_source(source)
        assert dp.can_use is expected_can_use

    def test_to_dict(self):
        """Test conversion to dictionary."""
        dp = DataPoint("website")
        dp.add_source(DataSource("web_scraping", "https://hotel.com", "2024-01-15", {"url": "src"}))
        
        result = dp.to_dict()
        
        assert result["field_name"] == "website"
        assert result["value"] == "https://hotel.com"
        assert result["confidence"] == "estimated"
        assert result["can_use"] is True
        assert result["match_percentage"] == 100.0
        assert result["sources_count"] == 1
        assert len(result["sources"]) == 1
        assert result["sources"][0]["source_type"] == "web_scraping"
        assert result["sources"][0]["value"] == "https://hotel.com"
        assert result["sources"][0]["timestamp"] == "2024-01-15"
        assert result["sources"][0]["metadata"] == {"url": "src"}
        assert "discrepancies" in result
        assert "requires_manual_review" in result
        assert "disclaimer" in result
        assert "icon" in result

    def test_to_dict_no_sources(self):
        """Test to_dict with no sources."""
        dp = DataPoint("empty_field")
        result = dp.to_dict()
        
        assert result["field_name"] == "empty_field"
        assert result["value"] is None
        assert result["confidence"] == "unknown"
        assert result["can_use"] is False
        assert result["match_percentage"] == 0.0
        assert result["sources_count"] == 0
        assert result["sources"] == []
        assert result["discrepancies"] == ["No data sources available"]
        assert result["requires_manual_review"] is True
        assert "Sin datos disponibles" in result["disclaimer"]
        assert result["icon"] == "?"

    def test_determine_final_value_most_common(self):
        """Test that final value uses most common non-None value."""
        dp = DataPoint("category")
        dp.add_source(DataSource("a", "Boutique", "2024-01-15"))
        dp.add_source(DataSource("b", "Boutique", "2024-01-15"))
        dp.add_source(DataSource("c", "Luxury", "2024-01-15"))
        
        assert dp.value == "Boutique"

    def test_find_discrepancies(self):
        """Test that discrepancies are found between sources."""
        dp = DataPoint("address")
        dp.add_source(DataSource("web", "123 Main St", "2024-01-15"))
        dp.add_source(DataSource("api", "456 Oak Ave", "2024-01-15"))
        
        discrepancies = dp._validation_result.discrepancies
        assert len(discrepancies) == 1
        assert "web (123 Main St) != api (456 Oak Ave)" in discrepancies[0]

    def test_no_discrepancies_for_single_source(self):
        """Test that single source has no discrepancies."""
        dp = DataPoint("field")
        dp.add_source(DataSource("web", "value", "2024-01-15"))
        
        assert dp._validation_result.discrepancies == []
