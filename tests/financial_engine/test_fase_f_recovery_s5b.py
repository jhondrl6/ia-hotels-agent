"""Tests FASE-F recovery (S5b): occupancy label en camino FASE-K de main.py.

El fix S5 de FASE-D cubrió harness_handlers.py y los dicts financial_sources,
pero NO el bloque FASE-K de main.py (construcción de HotelFinancialData para
ScenarioCalculator.calculate_breakdown) ni el input de PrecisionValidator
(GAP-4). Ambos recalculaban la condición con prioridad regional, produciendo
`breakdown.data_sources.occupancy == "regional"` con valor real de onboarding
(detectado por V8 del run E2E de FASE-F, lección L28).

S5b: ambos sitios reutilizan `_occupancy_source` (resuelto en FASE 3 con
prioridad onboarding > regional > default).
"""

import re
from pathlib import Path

import pytest

from modules.financial_engine.scenario_calculator import (
    HotelFinancialData,
    ScenarioCalculator,
)

MAIN_PY = Path(__file__).resolve().parent.parent.parent / "main.py"


class TestS5bStaticContract:
    """Contrato estático: main.py no recalcula la condición de occupancy_source
    en los sitios posteriores a FASE 3 (regresión L28)."""

    def test_fase_k_breakdown_uses_resolved_label(self):
        """La construcción FASE-K pasa occupancy_source=_occupancy_source."""
        src = MAIN_PY.read_text(encoding="utf-8")
        assert re.search(
            r"occupancy_source=_occupancy_source", src
        ), "El bloque FASE-K debe reutilizar _occupancy_source (fix S5b)"

    def test_precision_validator_uses_resolved_label(self):
        """El input de PrecisionValidator (GAP-4) usa el label resuelto."""
        src = MAIN_PY.read_text(encoding="utf-8")
        assert re.search(
            r"_occ_source\s*=\s*_occupancy_source", src
        ), "PrecisionValidator debe recibir _occupancy_source (fix S5b)"

    def test_no_stale_regional_priority_condition(self):
        """Ningún sitio post-FASE-3 recalcula 'regional' con prioridad sobre onboarding."""
        src = MAIN_PY.read_text(encoding="utf-8")
        stale = re.findall(
            r"occupancy_source\s*=\s*'regional'\s*if\s+feature_flags", src
        ) + re.findall(
            r"_occ_source\s*=\s*\"regional\"\s*if\s+feature_flags", src
        )
        assert not stale, (
            f"Condición divergente encontrada ({len(stale)} sitio(s)): "
            "el label debe reutilizar _occupancy_source, no recalcularse"
        )


class TestS5bFaseKBehavior:
    """Comportamiento del camino FASE-K con wiring S5b (caso Zione)."""

    def _fase3_label(self, reservas_mes, rooms, should_use_regional):
        """Replica la resolución de _occupancy_source en FASE 3 de main.py."""
        if reservas_mes and rooms:
            return "onboarding"
        return "regional" if should_use_regional else "default"

    def test_fase_k_breakdown_label_onboarding_con_region_validada(self):
        """Con reservas_mes de onboarding, el breakdown dice 'onboarding'
        aunque la región califique para regional (bug V8)."""
        rooms, reservas_mes = 34, 800
        occupancy_rate = reservas_mes / (rooms * 30)  # 0.7843...

        _occupancy_source = self._fase3_label(
            reservas_mes, rooms, should_use_regional=True
        )
        assert _occupancy_source == "onboarding"

        hotel_data = HotelFinancialData(
            rooms=rooms,
            adr_cop=290000.0,
            occupancy_rate=occupancy_rate,
            direct_channel_percentage=0.4,
            ota_commission_rate=0.15,
            adr_source="user_provided",
            occupancy_source=_occupancy_source,  # wiring S5b
            channel_source="onboarding",
            ga4_enabled=False,
            gsc_enabled=False,
        )
        breakdown = ScenarioCalculator().calculate_breakdown(hotel_data)
        assert breakdown.hotel_data_sources["occupancy"] == "onboarding"

    def test_fase_k_breakdown_label_regional_sin_onboarding(self):
        """Sin reservas_mes y con región validada → 'regional' (no inventa onboarding)."""
        _occupancy_source = self._fase3_label(
            reservas_mes=None, rooms=34, should_use_regional=True
        )
        assert _occupancy_source == "regional"

        hotel_data = HotelFinancialData(
            rooms=34,
            adr_cop=290000.0,
            occupancy_rate=0.62,
            occupancy_source=_occupancy_source,
        )
        breakdown = ScenarioCalculator().calculate_breakdown(hotel_data)
        assert breakdown.hotel_data_sources["occupancy"] == "regional"

    def test_fase_k_breakdown_label_default_sin_nada(self):
        """Sin onboarding ni región validada → 'default'."""
        _occupancy_source = self._fase3_label(
            reservas_mes=None, rooms=34, should_use_regional=False
        )
        assert _occupancy_source == "default"

        hotel_data = HotelFinancialData(
            rooms=34,
            adr_cop=290000.0,
            occupancy_rate=0.50,
            occupancy_source=_occupancy_source,
        )
        breakdown = ScenarioCalculator().calculate_breakdown(hotel_data)
        assert breakdown.hotel_data_sources["occupancy"] == "default"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
