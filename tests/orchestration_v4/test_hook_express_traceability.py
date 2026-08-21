"""
Tests de contrato F11 (FASE-P1-C): trazabilidad del rango Hook → Express.

Contratos verificados:
- Al ejecutar el Express para un hotel que recibió Hook, se verifica que la
  cifra caiga dentro del corredor prometido (o se documenta por qué no).
- Se genera una sección de trazabilidad del rango para el output del Express.
- La narrativa de la delta explica la corrección benchmark → dato real.
"""

from pathlib import Path
from unittest.mock import patch

import pytest

from modules.orchestration_v4.two_phase_flow import (
    TwoPhaseOrchestrator,
    Phase1Result,
    HotelInputs,
    HookRangeTraceability,
)
from modules.orchestration_v4.onboarding_controller import OnboardingController


REPO_ROOT = Path(__file__).resolve().parents[2]
MASTER_PATH = REPO_ROOT / "data" / "benchmarks" / "regional_adr_2026.json"


def _make_phase1(loss_min: float = 1_000_000.0, loss_max: float = 5_000_000.0) -> Phase1Result:
    return Phase1Result(
        hotel_name="Hotel Test",
        hotel_url="https://www.hoteltest.com",
        region="eje_cafetero",
        hook_message="hook",
        loss_range_min=loss_min,
        loss_range_max=loss_max,
        next_step="complete_phase_2",
        confidence_level="low",
        disclaimer="benchmarks",
    )


class TestValidateHookRangeTraceability:
    """Mecanismo de verificación del corredor prometido por el Hook."""

    @pytest.fixture
    def orchestrator(self):
        return TwoPhaseOrchestrator()

    def test_express_within_corridor(self, orchestrator):
        """Cifra Express dentro del corredor → promesa validada."""
        report = orchestrator.validate_hook_range_traceability(_make_phase1(), 3_000_000.0)

        assert isinstance(report, HookRangeTraceability)
        assert report.within_corridor is True
        assert report.status == "DENTRO_CORREDOR"
        assert report.delta_pct == pytest.approx(0.0)
        assert "DENTRO" in report.narrative

    def test_express_below_corridor_documents_deviation(self, orchestrator):
        """Cifra por debajo del mínimo → se documenta la desviación."""
        report = orchestrator.validate_hook_range_traceability(_make_phase1(), 500_000.0)

        assert report.within_corridor is False
        assert report.status == "DEBAJO_CORREDOR"
        # 50% por debajo del mínimo (1.000.000)
        assert "50,0%" in report.narrative or "50.0%" in report.narrative
        assert "DEBAJO" in report.narrative

    def test_express_above_corridor_documents_deviation(self, orchestrator):
        """Cifra por encima del máximo → se documenta la desviación."""
        report = orchestrator.validate_hook_range_traceability(_make_phase1(), 6_000_000.0)

        assert report.within_corridor is False
        assert report.status == "ENCIMA_CORREDOR"
        # 20% por encima del máximo (5.000.000)
        assert "20,0%" in report.narrative or "20.0%" in report.narrative

    def test_express_on_boundaries_counts_as_within(self, orchestrator):
        """Los límites del corredor son inclusivos."""
        assert orchestrator.validate_hook_range_traceability(
            _make_phase1(), 1_000_000.0
        ).within_corridor is True
        assert orchestrator.validate_hook_range_traceability(
            _make_phase1(), 5_000_000.0
        ).within_corridor is True

    def test_narrative_explains_benchmark_to_real_correction(self, orchestrator):
        """La narrativa explica la corrección benchmark → dato real."""
        report = orchestrator.validate_hook_range_traceability(_make_phase1(), 3_000_000.0)

        assert "benchmark" in report.narrative.lower()
        assert "dato real" in report.narrative
        assert "eje_cafetero" in report.narrative
        # Cifra del Express presente en la narrativa
        assert "3.000.000" in report.narrative

    def test_report_to_dict_contract(self, orchestrator):
        """El reporte es serializable con todas sus keys."""
        report = orchestrator.validate_hook_range_traceability(_make_phase1(), 3_000_000.0)

        data = report.to_dict()
        assert set(data.keys()) == {
            "hook_range_min",
            "hook_range_max",
            "express_monthly_loss",
            "within_corridor",
            "status",
            "delta_pct",
            "region",
            "narrative",
        }


class TestFormatTraceabilitySection:
    """Sección de trazabilidad para el output del Express."""

    def test_section_contains_corridor_table_and_narrative(self):
        orchestrator = TwoPhaseOrchestrator()
        report = orchestrator.validate_hook_range_traceability(_make_phase1(), 3_000_000.0)

        section = TwoPhaseOrchestrator.format_traceability_section(report)

        assert "Trazabilidad del rango Hook" in section
        assert "1.000.000" in section  # mínimo del corredor
        assert "5.000.000" in section  # máximo del corredor
        assert "3.000.000" in section  # cifra Express
        assert "DENTRO_CORREDOR" in section
        assert "benchmark" in section.lower()

    def test_section_documents_out_of_corridor_status(self):
        orchestrator = TwoPhaseOrchestrator()
        report = orchestrator.validate_hook_range_traceability(_make_phase1(), 9_000_000.0)

        section = TwoPhaseOrchestrator.format_traceability_section(report)

        assert "ENCIMA_CORREDOR" in section
        assert "9.000.000" in section


class TestControllerTraceabilityIntegration:
    """Cierre del ciclo Hook → Express via OnboardingController."""

    def _run_full_flow(self):
        controller = OnboardingController(benchmark_master_path=str(MASTER_PATH))
        state = controller.start_onboarding(
            hotel_url="https://www.hoteltest.com",
            hotel_name="Hotel Test",
            region="eje_cafetero",
        )
        hotel_id = OnboardingController.generate_hotel_id("https://www.hoteltest.com")
        controller.submit_phase_2(
            hotel_id=hotel_id,
            inputs=HotelInputs(rooms=20, adr_cop=280_000.0, occupancy_rate=0.55),
        )
        return controller, hotel_id, state

    def test_traceability_uses_realista_scenario_as_express_value(self):
        """Sin valor explícito, la cifra Express sale del escenario realista."""
        controller, hotel_id, state = self._run_full_flow()

        report = controller.get_range_traceability(hotel_id)

        assert report is not None
        realista = state.phase_2_result.scenarios["realista"]
        assert report.express_monthly_loss == pytest.approx(
            realista["monthly_loss_cop"]
        )
        assert report.status in (
            "DENTRO_CORREDOR",
            "DEBAJO_CORREDOR",
            "ENCIMA_CORREDOR",
        )

    def test_traceability_with_explicit_express_value_inside_corridor(self):
        """Valor explícito dentro del corredor del hook generado con master."""
        controller, hotel_id, state = self._run_full_flow()

        midpoint = (
            state.phase_1_result.loss_range_min + state.phase_1_result.loss_range_max
        ) / 2.0
        report = controller.get_range_traceability(hotel_id, express_monthly_loss=midpoint)

        assert report is not None
        assert report.within_corridor is True
        assert report.status == "DENTRO_CORREDOR"

    def test_traceability_returns_none_without_phase1(self):
        """Sin Hook no hay promesa que verificar."""
        controller = OnboardingController(benchmark_master_path=str(MASTER_PATH))

        assert controller.get_range_traceability("hotel_inexistente") is None

    def test_traceability_returns_none_without_express_figure(self):
        """Con Hook pero sin Fase 2 (sin escenarios), no hay cifra Express."""
        controller = OnboardingController(benchmark_master_path=str(MASTER_PATH))
        controller.start_onboarding(
            hotel_url="https://www.hoteltest.com",
            hotel_name="Hotel Test",
            region="eje_cafetero",
        )
        hotel_id = OnboardingController.generate_hotel_id("https://www.hoteltest.com")

        assert controller.get_range_traceability(hotel_id) is None

    def test_traceability_section_renderable_from_full_flow(self):
        """La sección markdown se genera desde el flujo completo."""
        controller, hotel_id, _ = self._run_full_flow()

        report = controller.get_range_traceability(hotel_id)
        section = TwoPhaseOrchestrator.format_traceability_section(report)

        assert "Trazabilidad del rango Hook" in section
        assert report.region == "eje_cafetero"
