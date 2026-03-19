"""Tests for No Defaults Validator.

Valida que el sistema bloquea cálculos financieros cuando
se detectan valores por defecto en campos críticos.
"""

import pytest
from modules.financial_engine.no_defaults_validator import (
    NoDefaultsValidator,
    NoDefaultsValidationResult,
    ValidationBlock,
    DefaultValueType,
    BlockReason,
)
from modules.financial_engine.scenario_calculator import HotelFinancialData


class TestNoDefaultsValidator:
    """Test cases for NoDefaultsValidator."""

    def test_validator_initialization(self):
        """Test validator initializes correctly."""
        validator = NoDefaultsValidator()
        assert validator is not None
        assert validator.CRITICAL_FIELDS == ["occupancy_rate", "direct_channel_percentage", "adr_cop"]

    def test_valid_data_passes(self):
        """Test that valid financial data passes validation."""
        validator = NoDefaultsValidator()
        
        data = {
            "rooms": 50,
            "adr_cop": 180000.0,
            "occupancy_rate": 0.70,
            "direct_channel_percentage": 0.20,
            "ota_commission_rate": 0.15,
        }
        
        result = validator.validate(data)
        
        assert result.can_calculate is True
        assert len(result.blocks) == 0
        assert result.has_blocks is False

    def test_occupancy_rate_zero_blocks(self):
        """Test that occupancy_rate=0 blocks calculation."""
        validator = NoDefaultsValidator()
        
        data = {
            "rooms": 50,
            "adr_cop": 180000.0,
            "occupancy_rate": 0,
            "direct_channel_percentage": 0.20,
        }
        
        result = validator.validate(data)
        
        assert result.can_calculate is False
        assert result.has_blocks is True
        assert any(b.field == "occupancy_rate" for b in result.blocks)
        assert any(b.default_type == DefaultValueType.ZERO for b in result.blocks)

    def test_direct_channel_zero_blocks(self):
        """Test that direct_channel_percentage=0 blocks calculation."""
        validator = NoDefaultsValidator()
        
        data = {
            "rooms": 50,
            "adr_cop": 180000.0,
            "occupancy_rate": 0.70,
            "direct_channel_percentage": 0,
        }
        
        result = validator.validate(data)
        
        assert result.can_calculate is False
        assert result.has_blocks is True
        assert any(b.field == "direct_channel_percentage" for b in result.blocks)

    def test_adr_cop_zero_blocks(self):
        """Test that adr_cop=0 blocks calculation."""
        validator = NoDefaultsValidator()
        
        data = {
            "rooms": 50,
            "adr_cop": 0,
            "occupancy_rate": 0.70,
            "direct_channel_percentage": 0.20,
        }
        
        result = validator.validate(data)
        
        assert result.can_calculate is False
        assert result.has_blocks is True
        assert any(b.field == "adr_cop" for b in result.blocks)

    def test_none_values_block(self):
        """Test that None values block calculation."""
        validator = NoDefaultsValidator()
        
        data = {
            "rooms": 50,
            "adr_cop": None,
            "occupancy_rate": None,
            "direct_channel_percentage": None,
        }
        
        result = validator.validate(data)
        
        assert result.can_calculate is False
        assert len(result.blocks) == 3  # All three critical fields

    def test_missing_fields_block(self):
        """Test that missing critical fields block calculation."""
        validator = NoDefaultsValidator()
        
        data = {
            "rooms": 50,
            # Missing all critical fields
        }
        
        result = validator.validate(data)
        
        assert result.can_calculate is False
        assert len(result.blocks) == 3

    def test_user_message_is_descriptive(self):
        """Test that user message explains what's wrong."""
        validator = NoDefaultsValidator()
        
        data = {
            "rooms": 50,
            "adr_cop": 0,
            "occupancy_rate": 0,
            "direct_channel_percentage": 0,
        }
        
        result = validator.validate(data)
        message = result.to_user_message()
        
        assert "BLOQUEADO" in message or "bloqueado" in message.lower()
        assert "occupancy_rate" in message
        assert "adr_cop" in message
        assert "direct_channel_percentage" in message
        assert "onboarding" in message.lower()

    def test_is_default_value_detects_defaults(self):
        """Test static method is_default_value."""
        assert NoDefaultsValidator.is_default_value(0) is True
        assert NoDefaultsValidator.is_default_value(0.0) is True
        assert NoDefaultsValidator.is_default_value(None) is True
        assert NoDefaultsValidator.is_default_value("") is True
        
        assert NoDefaultsValidator.is_default_value(1) is False
        assert NoDefaultsValidator.is_default_value(0.5) is False
        assert NoDefaultsValidator.is_default_value("test") is False

    def test_partial_defaults_partial_blocks(self):
        """Test that partial defaults still block."""
        validator = NoDefaultsValidator()
        
        data = {
            "rooms": 50,
            "adr_cop": 180000.0,  # Valid
            "occupancy_rate": 0,  # Invalid
            "direct_channel_percentage": 0.20,  # Valid
        }
        
        result = validator.validate(data)
        
        assert result.can_calculate is False
        assert len(result.blocks) == 1
        assert result.blocks[0].field == "occupancy_rate"


class TestValidationBlock:
    """Test cases for ValidationBlock dataclass."""

    def test_block_creation(self):
        """Test ValidationBlock creation."""
        block = ValidationBlock(
            field="occupancy_rate",
            value=0,
            default_type=DefaultValueType.ZERO,
            reason=BlockReason.OCCUPANCY_RATE_ZERO,
            message="Occupancy rate is zero",
            correction_hint="Provide actual occupancy rate",
        )
        
        assert block.field == "occupancy_rate"
        assert block.value == 0
        assert block.default_type == DefaultValueType.ZERO


class TestHotelVisperasScenario:
    """Test scenarios similar to Hotel Vísperas case."""

    def test_visperas_incomplete_data_blocked(self):
        """Test that incomplete data like Hotel Vísperas is blocked."""
        validator = NoDefaultsValidator()
        
        # Simulate incomplete data (like Hotel Vísperas)
        incomplete_data = {
            "rooms": 20,  # Known
            "adr_cop": 0,  # Default (unknown)
            "occupancy_rate": 0,  # Default (unknown)
            "direct_channel_percentage": 0,  # Default (unknown)
        }
        
        result = validator.validate(incomplete_data)
        
        assert result.can_calculate is False
        assert len(result.blocks) >= 2  # At least ADR and occupancy


class TestHotelFinancialDataObjectValidation:
    """Test cases for HotelFinancialData object validation (not dict)."""

    def test_hotel_financial_data_valid_object_passes(self):
        """Test that valid HotelFinancialData object passes validation."""
        validator = NoDefaultsValidator()
        
        data = HotelFinancialData(
            rooms=50,
            adr_cop=180000.0,
            occupancy_rate=0.70,
            direct_channel_percentage=0.20,
            ota_commission_rate=0.15,
        )
        
        result = validator.validate(data)
        
        assert result.can_calculate is True
        assert len(result.blocks) == 0
        assert result.has_blocks is False

    def test_hotel_financial_data_object_occupancy_zero_blocks(self):
        """Test that HotelFinancialData with occupancy_rate=0 blocks."""
        validator = NoDefaultsValidator()
        
        data = HotelFinancialData(
            rooms=50,
            adr_cop=180000.0,
            occupancy_rate=0,
            direct_channel_percentage=0.20,
        )
        
        result = validator.validate(data)
        
        assert result.can_calculate is False
        assert result.has_blocks is True
        assert any(b.field == "occupancy_rate" for b in result.blocks)
        assert any(b.default_type == DefaultValueType.ZERO for b in result.blocks)

    def test_hotel_financial_data_object_adr_zero_blocks(self):
        """Test that HotelFinancialData with adr_cop=0 blocks."""
        validator = NoDefaultsValidator()
        
        data = HotelFinancialData(
            rooms=50,
            adr_cop=0,
            occupancy_rate=0.70,
            direct_channel_percentage=0.20,
        )
        
        result = validator.validate(data)
        
        assert result.can_calculate is False
        assert result.has_blocks is True
        assert any(b.field == "adr_cop" for b in result.blocks)

    def test_hotel_financial_data_object_direct_channel_zero_blocks(self):
        """Test that HotelFinancialData with direct_channel_percentage=0 blocks."""
        validator = NoDefaultsValidator()
        
        data = HotelFinancialData(
            rooms=50,
            adr_cop=180000.0,
            occupancy_rate=0.70,
            direct_channel_percentage=0,
        )
        
        result = validator.validate(data)
        
        assert result.can_calculate is False
        assert result.has_blocks is True
        assert any(b.field == "direct_channel_percentage" for b in result.blocks)

    def test_dict_and_object_produce_same_result(self):
        """Test that dict and HotelFinancialData object produce identical validation results."""
        validator = NoDefaultsValidator()
        
        dict_data = {
            "rooms": 50,
            "adr_cop": 180000.0,
            "occupancy_rate": 0.70,
            "direct_channel_percentage": 0.20,
            "ota_commission_rate": 0.15,
        }
        
        object_data = HotelFinancialData(
            rooms=50,
            adr_cop=180000.0,
            occupancy_rate=0.70,
            direct_channel_percentage=0.20,
            ota_commission_rate=0.15,
        )
        
        dict_result = validator.validate(dict_data)
        object_result = validator.validate(object_data)
        
        assert dict_result.can_calculate == object_result.can_calculate
        assert len(dict_result.blocks) == len(object_result.blocks)

    def test_hotel_financial_data_with_none_occupancy_blocks(self):
        """Test that HotelFinancialData with None occupancy_rate blocks."""
        validator = NoDefaultsValidator()
        
        data = HotelFinancialData(
            rooms=50,
            adr_cop=180000.0,
            occupancy_rate=0.70,
            direct_channel_percentage=None,
        )
        
        result = validator.validate(data)
        
        assert result.can_calculate is False
        assert any(b.field == "direct_channel_percentage" for b in result.blocks)
