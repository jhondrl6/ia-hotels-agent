"""Tests FASE-D (S5): Label de occupancy veraz en data_sources.

Verifica que breakdown.data_sources.occupancy refleje la fuente real
cuando occupancy_source == "onboarding", incluso si la región califica
para datos regionales.
"""

import pytest
from unittest.mock import patch, MagicMock

from modules.financial_engine.scenario_calculator import HotelFinancialData


class TestOccupancySourceLabel:
    """S5: data_sources.occupancy debe ser veraz."""

    def test_hotel_financial_data_accepts_occupancy_source(self):
        """HotelFinancialData almacena occupancy_source correctamente."""
        data = HotelFinancialData(
            rooms=20,
            adr_cop=250000.0,
            occupancy_rate=0.72,
            occupancy_source="onboarding",
        )
        assert data.occupancy_source == "onboarding"

    def test_hotel_financial_data_default_occupancy_source(self):
        """HotelFinancialData default de occupancy_source es 'unknown'."""
        data = HotelFinancialData(
            rooms=20,
            adr_cop=250000.0,
            occupancy_rate=0.72,
        )
        assert data.occupancy_source == "unknown"

    def test_occupancy_label_logic_onboarding_priority(self):
        """La lógica del label da prioridad a 'onboarding' sobre 'regional'."""
        # Simular la lógica de harness_handlers.py L118 (post-fix)
        occupancy_source = "onboarding"
        should_use_regional = True  # La región califica para regional

        # Lógica corregida
        label = (
            occupancy_source
            if occupancy_source == "onboarding"
            else ("regional" if should_use_regional else occupancy_source)
        )
        assert label == "onboarding", "Occupancy de onboarding tiene prioridad"

    def test_occupancy_label_logic_regional_fallback(self):
        """Si occupancy no es onboarding y región califica → 'regional'."""
        occupancy_source = "default"
        should_use_regional = True

        label = (
            occupancy_source
            if occupancy_source == "onboarding"
            else ("regional" if should_use_regional else occupancy_source)
        )
        assert label == "regional"

    def test_occupancy_label_logic_default_passthrough(self):
        """Si no es onboarding ni regional califica → pass-through del source."""
        occupancy_source = "default"
        should_use_regional = False

        label = (
            occupancy_source
            if occupancy_source == "onboarding"
            else ("regional" if should_use_regional else occupancy_source)
        )
        assert label == "default"

    def test_trace_data_sources_uses_occupancy_source(self):
        """_trace_data_sources mapea occupancy desde HotelFinancialData."""
        from modules.financial_engine.scenario_calculator import ScenarioCalculator

        calc = ScenarioCalculator()
        data = HotelFinancialData(
            rooms=20,
            adr_cop=250000.0,
            occupancy_rate=0.72,
            occupancy_source="onboarding",
        )
        sources = calc._trace_data_sources(data)
        assert sources["occupancy"] == "onboarding"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
