"""Tests for FinancialInputsContract validation."""

import pytest
from modules.financial_engine.inputs_contract import (
    FinancialInputsContract,
    ValidationResult,
    ValidationSeverity,
)


class TestFinancialInputsContract:
    """Test suite for input validation."""
    
    def test_valid_basic_inputs(self):
        """Test validation with valid basic inputs."""
        contract = FinancialInputsContract(
            rooms=25,
            adr_cop=350000.0,
            occupancy_rate=0.65,
        )
        
        result = contract.validate()
        
        assert result.is_valid is True
        assert len(result.errors) == 0
        assert result.normalized["rooms"] == 25
        assert result.normalized["adr_cop"] == 350000.0
        assert result.normalized["occupancy_rate"] == 0.65
    
    def test_rooms_validation(self):
        """Test rooms field validation."""
        # Negative rooms
        contract = FinancialInputsContract(rooms=-5, adr_cop=300000.0)
        result = contract.validate()
        assert result.is_valid is False
        assert any(e.field == "rooms" for e in result.errors)
        
        # Zero rooms
        contract = FinancialInputsContract(rooms=0, adr_cop=300000.0)
        result = contract.validate()
        assert result.is_valid is False
        
        # Too many rooms
        contract = FinancialInputsContract(rooms=1000, adr_cop=300000.0)
        result = contract.validate()
        assert result.is_valid is False
        assert any(e.severity == ValidationSeverity.ERROR for e in result.errors)
    
    def test_adr_validation(self):
        """Test ADR field validation."""
        # Negative ADR
        contract = FinancialInputsContract(rooms=10, adr_cop=-100000.0)
        result = contract.validate()
        assert result.is_valid is False
        
        # Zero ADR
        contract = FinancialInputsContract(rooms=10, adr_cop=0)
        result = contract.validate()
        assert result.is_valid is False
        
        # Very high ADR (error)
        contract = FinancialInputsContract(rooms=10, adr_cop=10_000_000.0)
        result = contract.validate()
        assert result.is_valid is False
    
    def test_occupancy_normalization(self):
        """Test occupancy rate normalization."""
        # Input as percentage (65)
        contract = FinancialInputsContract(
            rooms=10,
            adr_cop=300000.0,
            occupancy_rate=65.0,
        )
        result = contract.validate()
        assert result.is_valid is True
        assert result.normalized["occupancy_rate"] == 0.65
        
        # Input as decimal (0.65)
        contract = FinancialInputsContract(
            rooms=10,
            adr_cop=300000.0,
            occupancy_rate=0.65,
        )
        result = contract.validate()
        assert result.is_valid is True
        assert result.normalized["occupancy_rate"] == 0.65
    
    def test_direct_channel_normalization(self):
        """Test direct channel percentage normalization."""
        # Input as percentage (20)
        contract = FinancialInputsContract(
            rooms=10,
            adr_cop=300000.0,
            direct_channel_percentage=20.0,
        )
        result = contract.validate()
        assert result.is_valid is True
        assert result.normalized["direct_channel_percentage"] == 0.20
    
    def test_whatsapp_optional(self):
        """Test that WhatsApp is optional."""
        # Without WhatsApp
        contract = FinancialInputsContract(
            rooms=10,
            adr_cop=300000.0,
        )
        result = contract.validate()
        assert result.is_valid is True
        assert "whatsapp_number" not in result.normalized
        
        # With WhatsApp (just stored, not validated in simplified version)
        contract = FinancialInputsContract(
            rooms=10,
            adr_cop=300000.0,
            whatsapp_number="+57 300 123 4567",
        )
        result = contract.validate()
        assert result.is_valid is True
    
    def test_region_validation(self):
        """Test region validation."""
        # Known region
        contract = FinancialInputsContract(
            rooms=10,
            adr_cop=300000.0,
            region="eje_cafetero",
        )
        result = contract.validate()
        assert result.is_valid is True
        assert result.normalized["region"] == "eje_cafetero"
        
        # Unknown region (warning, defaults to "default")
        contract = FinancialInputsContract(
            rooms=10,
            adr_cop=300000.0,
            region="unknown_region",
        )
        result = contract.validate()
        assert result.is_valid is True
        assert result.normalized["region"] == "default"
        assert any(e.field == "region" for e in result.warnings)
    
    def test_from_dict(self):
        """Test creating contract from dictionary."""
        data = {
            "rooms": 30,
            "adr_cop": 450000.0,
            "occupancy_rate": 70.0,
            "region": "caribe",
        }
        
        contract = FinancialInputsContract.from_dict(data)
        result = contract.validate()
        
        assert result.is_valid is True
        assert result.normalized["rooms"] == 30
        assert result.normalized["occupancy_rate"] == 0.70
    
    def test_to_hotel_financial_data(self):
        """Test conversion to HotelFinancialData format."""
        contract = FinancialInputsContract(
            rooms=20,
            adr_cop=400000.0,
            occupancy_rate=0.60,
        )
        
        data = contract.to_hotel_financial_data()
        
        assert data["rooms"] == 20
        assert data["adr_cop"] == 400000.0
        assert data["occupancy_rate"] == 0.60
        assert "ota_presence" in data
    
    def test_invalid_raises_error(self):
        """Test that invalid inputs raise ValueError."""
        contract = FinancialInputsContract(rooms=-10, adr_cop=-50000.0)
        
        with pytest.raises(ValueError, match="Validation failed"):
            contract.to_hotel_financial_data()


class TestValidationEdgeCases:
    """Edge case tests."""
    
    def test_string_adr(self):
        """Test ADR as string."""
        contract = FinancialInputsContract(
            rooms=10,
            adr_cop="350000.50",
        )
        result = contract.validate()
        assert result.is_valid is True
        assert result.normalized["adr_cop"] == 350000.50
    
    def test_occupancy_out_of_range(self):
        """Test occupancy outside valid range."""
        contract = FinancialInputsContract(
            rooms=10,
            adr_cop=300000.0,
            occupancy_rate=150.0,
        )
        result = contract.validate()
        assert result.is_valid is False
    
    def test_all_optional_defaults(self):
        """Test that optional fields have sensible defaults."""
        contract = FinancialInputsContract(
            rooms=10,
            adr_cop=300000.0,
        )
        
        result = contract.validate()
        
        assert result.normalized["occupancy_rate"] == 0.50
        assert result.normalized["direct_channel_percentage"] == 0.0
        assert result.normalized["ota_commission_rate"] == 0.15
        assert result.normalized["region"] == "default"
