"""
Tests for the cross_validator module.

This module contains comprehensive tests for data validation across multiple sources
including web scraping, user input, GBP API, and benchmarks.
"""

import pytest
from datetime import datetime
from modules.data_validation.cross_validator import CrossValidator, normalize_phone_number
from modules.data_validation.confidence_taxonomy import DataPoint, DataSource, ConfidenceLevel


class TestCrossValidator:
    """Test suite for CrossValidator class."""

    def test_init(self):
        """Test that CrossValidator initializes with empty data_points dict."""
        validator = CrossValidator()
        assert validator.data_points == {}
        assert isinstance(validator.data_points, dict)

    def test_add_scraped_data(self):
        """Test adding data from web scraping source."""
        validator = CrossValidator()
        validator.add_scraped_data("hotel_name", "Hotel Test")

        assert "hotel_name" in validator.data_points
        data_point = validator.data_points["hotel_name"]
        assert len(data_point._sources) == 1
        assert data_point._sources[0].source_type == "web_scraping"
        assert data_point._sources[0].value == "Hotel Test"
        assert data_point._sources[0].timestamp is not None

    def test_add_user_input(self):
        """Test adding data from user input source."""
        validator = CrossValidator()
        validator.add_user_input("num_rooms", 50)

        assert "num_rooms" in validator.data_points
        data_point = validator.data_points["num_rooms"]
        assert len(data_point._sources) == 1
        assert data_point._sources[0].source_type == "user_input"
        assert data_point._sources[0].value == 50
        assert data_point._sources[0].timestamp is not None

    def test_add_gbp_data(self):
        """Test adding data from Google Business Profile API source."""
        validator = CrossValidator()
        validator.add_gbp_data("phone", "3113973744")

        assert "phone" in validator.data_points
        data_point = validator.data_points["phone"]
        assert len(data_point._sources) == 1
        assert data_point._sources[0].source_type == "gbp_api"
        assert data_point._sources[0].value == "3113973744"
        assert data_point._sources[0].timestamp is not None

    def test_add_benchmark_data(self):
        """Test adding data from benchmark source with region."""
        validator = CrossValidator()
        validator.add_benchmark_data("occupancy_rate", 0.75, region="Bogota")

        assert "occupancy_rate" in validator.data_points
        data_point = validator.data_points["occupancy_rate"]
        assert len(data_point._sources) == 1
        assert data_point._sources[0].source_type == "benchmark"
        assert data_point._sources[0].value == 0.75
        assert data_point._sources[0].metadata["region"] == "Bogota"
        assert data_point._sources[0].timestamp is not None

    def test_get_validated_field_returns_data_point(self):
        """Test that get_validated_field returns DataPoint if field exists."""
        validator = CrossValidator()
        validator.add_user_input("address", "Calle 123 #45-67")

        result = validator.get_validated_field("address")
        assert result is not None
        assert isinstance(result, DataPoint)
        assert result.field_name == "address"

    def test_get_validated_field_returns_none(self):
        """Test that get_validated_field returns None if field doesn't exist."""
        validator = CrossValidator()

        result = validator.get_validated_field("nonexistent_field")
        assert result is None

    def test_validate_whatsapp_matching_values_verified(self):
        """Test WhatsApp validation with matching web and GBP values returns VERIFIED."""
        validator = CrossValidator()
        result = validator.validate_whatsapp(
            web_value="311-397-3744",
            gbp_value="+573113973744"
        )

        assert isinstance(result, DataPoint)
        assert result.confidence == ConfidenceLevel.VERIFIED
        assert result.value == "3113973744"

    def test_validate_whatsapp_only_web_estimated(self):
        """Test WhatsApp validation with only web value returns ESTIMATED."""
        validator = CrossValidator()
        result = validator.validate_whatsapp(web_value="311-397-3744")

        assert isinstance(result, DataPoint)
        assert result.confidence == ConfidenceLevel.ESTIMATED
        assert result.value == "3113973744"

    def test_validate_whatsapp_conflicting_values(self):
        """Test WhatsApp validation with conflicting values returns CONFLICT."""
        validator = CrossValidator()
        result = validator.validate_whatsapp(
            web_value="311-397-3744",
            gbp_value="300-123-4567"
        )

        assert isinstance(result, DataPoint)
        assert result.confidence == ConfidenceLevel.CONFLICT

    def test_validate_whatsapp_various_formats(self):
        """Test WhatsApp validation handles various phone formats."""
        validator = CrossValidator()

        # Test matching numbers in different formats
        result = validator.validate_whatsapp(
            web_value="(311) 397-3744",
            gbp_value="311 397 3744"
        )
        assert result.confidence == ConfidenceLevel.VERIFIED
        assert result.value == "3113973744"

        # Test with +57 prefix
        result = validator.validate_whatsapp(
            web_value="+573113973744",
            user_value="573113973744"
        )
        assert result.confidence == ConfidenceLevel.VERIFIED
        assert result.value == "3113973744"

    def test_validate_adr_user_matches_benchmark_verified(self):
        """Test ADR validation when user input matches benchmark returns VERIFIED."""
        validator = CrossValidator()
        result = validator.validate_adr(
            user_input=150.0,
            benchmark_region=150.0
        )

        assert isinstance(result, DataPoint)
        assert result.confidence == ConfidenceLevel.VERIFIED
        assert result.value == 150.0

    def test_validate_adr_only_benchmark_estimated(self):
        """Test ADR validation with only benchmark returns ESTIMATED."""
        validator = CrossValidator()
        result = validator.validate_adr(benchmark_region=200.0)

        assert isinstance(result, DataPoint)
        assert result.confidence == ConfidenceLevel.ESTIMATED
        assert result.value == 200.0

    def test_validate_adr_large_discrepancies_conflict(self):
        """Test ADR validation with large discrepancies returns CONFLICT."""
        validator = CrossValidator()
        result = validator.validate_adr(
            user_input=100.0,
            benchmark_region=300.0
        )

        assert isinstance(result, DataPoint)
        assert result.confidence == ConfidenceLevel.CONFLICT

    def test_validate_adr_scraped_price_parsing(self):
        """Test ADR validation with scraped price string parsing."""
        validator = CrossValidator()
        result = validator.validate_adr(
            scraped_price="$150.50",
            user_input=150.50
        )

        assert isinstance(result, DataPoint)
        assert result.confidence == ConfidenceLevel.ESTIMATED
        assert result.value == 150.50

    def test_get_all_validations_returns_all_fields(self):
        """Test that get_all_validations returns dict with all fields."""
        validator = CrossValidator()
        validator.add_user_input("field1", "value1")
        validator.add_gbp_data("field2", "value2")
        validator.add_benchmark_data("field3", 123, "region")

        result = validator.get_all_validations()

        assert isinstance(result, dict)
        assert len(result) == 3
        assert "field1" in result
        assert "field2" in result
        assert "field3" in result
        assert "value" in result["field1"]
        assert "confidence" in result["field1"]

    def test_get_all_validations_empty(self):
        """Test that get_all_validations returns empty dict when no fields."""
        validator = CrossValidator()

        result = validator.get_all_validations()

        assert isinstance(result, dict)
        assert result == {}

    def test_get_conflict_report_returns_conflicts(self):
        """Test that get_conflict_report returns only CONFLICT/UNKNOWN fields."""
        validator = CrossValidator()

        # Add a verified field
        validator.add_user_input("verified_field", "value1")
        validator.add_gbp_data("verified_field", "value1")

        # Add a conflict field
        validator.validate_adr(user_input=100.0, benchmark_region=300.0)

        result = validator.get_conflict_report()

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["field_name"] == "adr"
        assert result[0]["confidence"] == "conflict"

    def test_get_conflict_report_empty(self):
        """Test that get_conflict_report returns empty list if no conflicts."""
        validator = CrossValidator()
        validator.add_user_input("field1", "value1")
        validator.add_gbp_data("field1", "value1")

        result = validator.get_conflict_report()

        assert isinstance(result, list)
        assert result == []


class TestNormalizePhoneNumber:
    """Test suite for normalize_phone_number function."""

    def test_remove_non_numeric(self):
        """Test that non-numeric characters are removed."""
        result = normalize_phone_number("abc311-397-3744xyz")
        assert result == "3113973744"

    def test_handle_colombian_country_code(self):
        """Test handling of Colombian country code (57)."""
        result = normalize_phone_number("573113973744")
        assert result == "3113973744"

        result = normalize_phone_number("+573113973744")
        assert result == "3113973744"

    def test_various_formats(self):
        """Test normalization of various phone number formats."""
        expected = "3113973744"

        # Dash format
        assert normalize_phone_number("311-397-3744") == expected

        # Plain format
        assert normalize_phone_number("3113973744") == expected

        # +57 prefix
        assert normalize_phone_number("+573113973744") == expected

        # 57 prefix without +
        assert normalize_phone_number("573113973744") == expected

        # Parentheses format
        assert normalize_phone_number("(311) 397-3744") == expected

    def test_empty_string(self):
        """Test normalization of empty string."""
        result = normalize_phone_number("")
        assert result == ""

    def test_none_value(self):
        """Test normalization of None value."""
        result = normalize_phone_number(None)
        assert result == ""

    def test_leading_zero_format(self):
        """Test handling of leading zero format (old Colombian format)."""
        result = normalize_phone_number("03113973744")
        assert result == "3113973744"

    def test_area_code_60_prefix(self):
        """Test handling of area code 60X prefix."""
        result = normalize_phone_number("6013113973744")
        assert result == "13113973744"

        result = normalize_phone_number("6033973744")
        assert result == "33973744"
