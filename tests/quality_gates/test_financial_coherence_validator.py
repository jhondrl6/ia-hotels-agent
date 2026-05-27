"""
Tests for Financial Coherence Validator — Arbitraje Ético Gate (ROICR FASE-4A).

Tests:
- fee < 60% recovery → PASS
- fee > 60% recovery → BLOCK
- fee = 60% exacto → PASS (límite inclusivo)

El threshold es 0.60 (60%), DIFERENTE del Value-Capture Cap en pricing (0.50).
"""

import pytest
from modules.quality.financial_coherence_validator import (
    validar_arbitraje_etico,
    ValidationReport,
)


class TestValidarArbitrajeEtico:
    """Tests para el gate de arbitraje ético."""

    def test_fee_below_60_percent_recovery_passes(self):
        """fee < 60% del recovery → PASS."""
        data = {
            "monthly_fee": 1500000,
            "expected_monthly_recovery": 3000000,
        }
        result = validar_arbitraje_etico(data)
        
        assert result.is_valid is True
        assert len(result.errors) == 0
        assert result.fee_ratio == 0.5
        assert result.threshold == 0.60

    def test_fee_at_60_percent_exact_retail_passes(self):
        """fee = 60% exacto → PASS (límite inclusivo)."""
        data = {
            "monthly_fee": 1800000,
            "expected_monthly_recovery": 3000000,
        }
        result = validar_arbitraje_etico(data)
        
        assert result.is_valid is True
        assert len(result.errors) == 0
        assert result.fee_ratio == 0.6
        assert result.threshold == 0.60

    def test_fee_above_60_percent_recovery_blocks(self):
        """fee > 60% del recovery → BLOCK."""
        data = {
            "monthly_fee": 2000000,
            "expected_monthly_recovery": 3000000,
        }
        result = validar_arbitraje_etico(data)
        
        assert result.is_valid is False
        assert len(result.errors) > 0
        assert "ETHICS GATE" in result.errors[0]
        assert result.fee_ratio == pytest.approx(0.666, rel=0.01)
        assert result.threshold == 0.60

    def test_fee_at_61_percent_blocks(self):
        """fee = 61% del recovery → BLOCK."""
        data = {
            "monthly_fee": 1830000,
            "expected_monthly_recovery": 3000000,
        }
        result = validar_arbitraje_etico(data)
        
        assert result.is_valid is False
        assert "ETHICS GATE" in result.errors[0]

    def test_zero_fee_returns_invalid(self):
        """fee = 0 → inválido (no hay datos para validar)."""
        data = {
            "monthly_fee": 0,
            "expected_monthly_recovery": 3000000,
        }
        result = validar_arbitraje_etico(data)
        
        assert result.is_valid is False
        assert "no se puede validar" in result.errors[0].lower()

    def test_zero_recovery_returns_invalid(self):
        """recovery = 0 → inválido (división por cero)."""
        data = {
            "monthly_fee": 1500000,
            "expected_monthly_recovery": 0,
        }
        result = validar_arbitraje_etico(data)
        
        assert result.is_valid is False

    def test_missing_fee_key_returns_invalid(self):
        """Sin monthly_fee → inválido."""
        data = {
            "expected_monthly_recovery": 3000000,
        }
        result = validar_arbitraje_etico(data)
        
        assert result.is_valid is False

    def test_missing_recovery_key_returns_invalid(self):
        """Sin recovery → inválido."""
        data = {
            "monthly_fee": 1500000,
        }
        result = validar_arbitraje_etico(data)
        
        assert result.is_valid is False

    def test_alternative_keys_fee_and_recovery(self):
        """Keys alternativas: 'fee' y 'recovery'."""
        data = {
            "fee": 1200000,
            "recovery": 3000000,
        }
        result = validar_arbitraje_etico(data)
        
        assert result.is_valid is True
        assert result.fee_ratio == 0.4

    def test_high_fee_low_recovery_blocks(self):
        """fee muy alto vs recovery bajo → BLOCK flagrante."""
        data = {
            "monthly_fee": 5000000,
            "expected_monthly_recovery": 3000000,
        }
        result = validar_arbitraje_etico(data)
        
        assert result.is_valid is False
        assert "ETHICS GATE" in result.errors[0]
        assert result.fee_ratio == pytest.approx(1.666, rel=0.01)

    def test_small_fee_large_recovery_passes(self):
        """fee bajo vs recovery alto → PASS con margen."""
        data = {
            "monthly_fee": 500000,
            "expected_monthly_recovery": 5000000,
        }
        result = validar_arbitraje_etico(data)
        
        assert result.is_valid is True
        assert result.fee_ratio == 0.1

    def test_validation_report_to_dict(self):
        """ValidationReport.to_dict() funciona correctamente."""
        data = {
            "monthly_fee": 2000000,
            "expected_monthly_recovery": 3000000,
        }
        result = validar_arbitraje_etico(data)
        d = result.to_dict()
        
        assert d["is_valid"] is False
        assert "ETHICS GATE" in d["errors"][0]
        assert d["fee_ratio"] == pytest.approx(0.666, rel=0.01)
        assert d["threshold"] == 0.60
