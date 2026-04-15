"""Tests for cross validation functions: validate_address and validate_email."""

import pytest
from modules.data_validation.cross_validator import CrossValidator


def test_validate_address_match():
    """Test validate_address returns DataPoint with VERIFIED confidence for matching addresses."""
    validator = CrossValidator()
    dp = validator.validate_address("123 Main St", "123 Main St")
    assert dp is not None
    # Confidence should be VERIFIED because addresses match after normalization
    from modules.data_validation.confidence_taxonomy import ConfidenceLevel
    assert dp.confidence == ConfidenceLevel.VERIFIED


def test_validate_address_mismatch():
    """Test validate_address returns DataPoint with non-VERIFIED confidence for mismatched addresses."""
    validator = CrossValidator()
    dp = validator.validate_address("123 Main St", "456 Oak Ave")
    assert dp is not None
    from modules.data_validation.confidence_taxonomy import ConfidenceLevel
    # Confidence may be CONFLICT or UNKNOWN, but not VERIFIED
    assert dp.confidence != ConfidenceLevel.VERIFIED


def test_validate_email_valid():
    """Test validate_email returns DataPoint for valid email format."""
    validator = CrossValidator()
    dp = validator.validate_email("test@example.com")
    assert dp is not None
    # Should have email field
    assert dp.field_name == "email"


def test_validate_email_invalid():
    """Test validate_email returns None for invalid email format."""
    validator = CrossValidator()
    dp = validator.validate_email("invalid-email")
    assert dp is None