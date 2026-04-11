"""Tests for FASE-A: FinancialBreakdown, Scenario.monthly_loss_central, EvidenceTier."""
import pytest
from modules.commercial_documents.data_structures import (
    Scenario,
    FinancialBreakdown,
    EvidenceTier,
)


# --- Scenario backward compatibility ---

def test_scenario_backward_compat():
    """Scenario sin monthly_loss_central usa monthly_loss_max como antes."""
    s = Scenario(monthly_loss_min=100, monthly_loss_max=120, probability=0.5, description="test")
    assert s.monthly_loss_central is None
    assert "$120 COP" in s.format_loss_cop()
    assert s.is_equilibrium_or_gain() is False


def test_scenario_backward_compat_equilibrium():
    """Scenario con loss_max <= 0 mantiene equilibrium check sin central."""
    s = Scenario(monthly_loss_min=-100, monthly_loss_max=-50, probability=0.5, description="test")
    assert s.is_equilibrium_or_gain() is True


# --- Scenario con monthly_loss_central ---

def test_scenario_with_central():
    """Scenario con monthly_loss_central usa central para formateo."""
    s = Scenario(
        monthly_loss_min=100, monthly_loss_max=120, probability=0.5,
        description="test", monthly_loss_central=110
    )
    assert "$110 COP" in s.format_loss_cop()


def test_scenario_with_central_equilibrium():
    """is_equilibrium_or_gain usa central cuando existe."""
    s_loss = Scenario(
        monthly_loss_min=50, monthly_loss_max=120, probability=0.5,
        description="test", monthly_loss_central=80  # 80 > 0 = pérdida
    )
    s_gain = Scenario(
        monthly_loss_min=-100, monthly_loss_max=10, probability=0.5,
        description="test", monthly_loss_central=-5  # -5 <= 0 = equilibrio
    )
    assert s_loss.is_equilibrium_or_gain() is False
    assert s_gain.is_equilibrium_or_gain() is True


def test_scenario_central_zero_equilibrium():
    """monthly_loss_central=0 es equilibrio."""
    s = Scenario(
        monthly_loss_min=-100, monthly_loss_max=50, probability=0.5,
        description="test", monthly_loss_central=0
    )
    assert s.is_equilibrium_or_gain() is True
    assert "Equilibrio" in s.format_loss_cop()


# --- FinancialBreakdown ---

def test_financial_breakdown_full():
    """FinancialBreakdown se instancia con todos los campos obligatorios."""
    fb = FinancialBreakdown(
        monthly_ota_commission_cop=5400000,
        ota_commission_basis="120 noches × $300K × 15%",
        ota_commission_source="onboarding",
        shift_savings_cop=540000,
        shift_percentage=0.10,
        shift_source="benchmark",
        ia_revenue_cop=2250000,
        ia_boost_percentage=0.05,
        ia_source="estimado",
        evidence_tier="C",
        disclaimer="Estimación basada en datos limitados."
    )
    assert fb.monthly_ota_commission_cop == 5400000
    assert fb.evidence_tier == "C"
    assert fb.hotel_data_sources == {}


def test_financial_breakdown_with_sources():
    """FinancialBreakdown con hotel_data_sources."""
    fb = FinancialBreakdown(
        monthly_ota_commission_cop=3000000,
        ota_commission_basis="80 noches × $250K × 15%",
        ota_commission_source="onboarding",
        shift_savings_cop=300000,
        shift_percentage=0.10,
        shift_source="benchmark",
        ia_revenue_cop=1500000,
        ia_boost_percentage=0.05,
        ia_source="scraping",
        evidence_tier="B",
        disclaimer="Estimación benchmarks.",
        hotel_data_sources={"adr": "onboarding", "rooms": "onboarding", "occupancy": "benchmark"}
    )
    assert fb.hotel_data_sources["adr"] == "onboarding"
    assert fb.hotel_data_sources["occupancy"] == "benchmark"


# --- EvidenceTier ---

def test_evidence_tier_disclaimers():
    """Cada EvidenceTier tiene disclaimer correcto."""
    assert "Google Analytics" in EvidenceTier.A.disclaimer
    assert "benchmarks" in EvidenceTier.B.disclaimer
    assert "limitados" in EvidenceTier.C.disclaimer


def test_evidence_tier_values():
    """EvidenceTier tiene los 3 valores esperados."""
    assert EvidenceTier.A.value == "A"
    assert EvidenceTier.B.value == "B"
    assert EvidenceTier.C.value == "C"
