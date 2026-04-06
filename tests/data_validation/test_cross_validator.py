"""Tests for cross validation functions: validate_address and validate_email."""

import pytest


def test_validate_address_match():
    """Test validate_address returns True for matching addresses."""
    from src.validators.cross_validator import validate_address

    result = validate_address("123 Main St", "123 Main St")
    assert result is True


def test_validate_address_mismatch():
    """Test validate_address returns False for mismatched addresses."""
    from src.validators.cross_validator import validate_address

    result = validate_address("123 Main St", "456 Oak Ave")
    assert result is False


def test_validate_email_valid():
    """Test validate_email returns True for valid email formats."""
    from src.validators.cross_validator import validate_email

    result = validate_email("test@example.com")
    assert result is True


def test_validate_email_invalid():
    """Test validate_email returns False for invalid email formats."""
    from src.validators.cross_validator import validate_email

    result = validate_email("invalid-email")
    assert result is False
