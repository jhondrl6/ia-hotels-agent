"""
Tests de contrato F6 (FASE-P1-C): cableado del benchmark master al rango del
hook (T1, decisión D4) + cap de plausibilidad (T2, decisión D7).

Contratos verificados:
- Con master presente, el rango del hook usa sus valores (no los defaults 120000+).
- Sin master, cae a defaults conservadores documentados.
- Región sin match en el master NO produce rango 23x por accidente de key.
- El rango del hook queda acotado al ratio max/min configurable.
- El cap es configurable via config/financial_defaults.yaml (hook_range_max_ratio).
"""

from pathlib import Path
from unittest.mock import patch

import pytest

from modules.orchestration_v4.two_phase_flow import (
    TwoPhaseOrchestrator,
    HOOK_RANGE_MAX_RATIO_FALLBACK,
)
from modules.orchestration_v4.onboarding_controller import (
    OnboardingController,
    load_benchmark_master,
)
from modules.common.yaml_loader import YAMLLoadError


REPO_ROOT = Path(__file__).resolve().parents[2]
MASTER_PATH = REPO_ROOT / "data" / "benchmarks" / "regional_adr_2026.json"

# Fórmula de _estimate_monthly_loss con comisión 0.20:
# loss = rooms * 30 * occupancy * 0.70 * adr * 0.20 * 0.20
COMISION_PATCH_TARGET = "modules.orchestration_v4.two_phase_flow.FinancialFactors"
CONFIG_PATCH_TARGET = "modules.orchestration_v4.two_phase_flow.load_yaml_config"


@pytest.fixture
def patch_comision():
    """Fija la comisión OTA en 0.20 para cálculos determinísticos."""
    with patch(COMISION_PATCH_TARGET) as mock_cls:
        mock_cls.return_value.get_comision_ota.return_value = {"base": 0.20}
        yield mock_cls


@pytest.fixture
def master_plan_data():
    """Plan data sintético con el formato plano que consume el orquestador."""
    return {
        "regions": {
            "eje_test": {
                "min_rooms": 10,
                "max_rooms": 20,
                "min_adr": 200000,
                "max_adr": 300000,
                "min_occupancy": 0.50,
                "max_occupancy": 0.60,
            },
            "default": {
                "min_rooms": 15,
                "max_rooms": 50,
                "min_adr": 300000,
                "max_adr": 300000,
                "min_occupancy": 0.50,
                "max_occupancy": 0.50,
            },
        }
    }


class TestHookRangeWiring:
    """T1 (D4): el rango del hook usa el benchmark master, no defaults."""

    def test_hook_range_uses_master_values_when_present(self, patch_comision):
        """Con master presente, min/max se calculan con SUS valores."""
        plan_data = {
            "regions": {
                "eje_test": {
                    "min_rooms": 10,
                    "max_rooms": 20,
                    "min_adr": 200000,
                    "max_adr": 300000,
                    "min_occupancy": 0.50,
                    "max_occupancy": 0.60,
                }
            }
        }
        orchestrator = TwoPhaseOrchestrator(plan_maestro_data=plan_data)

        loss_min, loss_max = orchestrator._calculate_hook_range("eje_test")

        # min: 10 hab * 30 * 0.50 * 0.70 * 200000 * 0.20 * 0.20 = 840.000
        assert loss_min == pytest.approx(840_000.0)
        # max: 20 hab * 30 * 0.60 * 0.70 * 300000 * 0.20 * 0.20 = 3.024.000
        assert loss_max == pytest.approx(3_024_000.0)

    def test_without_master_falls_back_to_documented_defaults(self, patch_comision):
        """Sin master, defaults conservadores documentados (comportamiento explícito)."""
        orchestrator = TwoPhaseOrchestrator()

        loss_min, _ = orchestrator._calculate_hook_range("default")

        # min default: 15 hab * 30 * 0.40 * 0.70 * 120000 * 0.20 * 0.20 = 604.800
        assert loss_min == pytest.approx(604_800.0)

    def test_region_alias_normalization(self, patch_comision, master_plan_data):
        """Aliases y mayúsculas resuelven a la misma región del master."""
        master_plan_data["regions"]["eje_cafetero"] = master_plan_data["regions"].pop(
            "eje_test"
        )
        orchestrator = TwoPhaseOrchestrator(plan_maestro_data=master_plan_data)

        base = orchestrator._calculate_hook_range("eje_cafetero")
        assert orchestrator._calculate_hook_range("Eje Cafetero") == base
        assert orchestrator._calculate_hook_range("coffee_axis") == base
        assert orchestrator._calculate_hook_range("EJE_CAFETERO") == base

    def test_region_no_match_uses_master_default_not_23x(self, patch_comision, master_plan_data):
        """Región sin match ('colombia') cae al default del master, sin rango 23x."""
        orchestrator = TwoPhaseOrchestrator(plan_maestro_data=master_plan_data)

        loss_min, loss_max = orchestrator._calculate_hook_range("colombia")

        # default del master: adr 300000 fijo → ratio viene solo de rooms 15→50 (3.33x)
        expected_min = 15 * 30 * 0.50 * 0.70 * 300000 * 0.20 * 0.20
        assert loss_min == pytest.approx(expected_min)
        assert loss_max / loss_min <= HOOK_RANGE_MAX_RATIO_FALLBACK
        assert loss_max / loss_min < 10.0  # nunca el 23x del fallo F6 original


class TestMasterConversion:
    """load_benchmark_master convierte el master P1-A al formato del orquestador."""

    def test_load_real_master_converts_regions(self):
        """El master real se convierte con sus valores calibrados."""
        plan_data = load_benchmark_master(str(MASTER_PATH))

        assert plan_data["master_source"] == "regional_adr_2026"
        regions = plan_data["regions"]
        assert "eje_cafetero" in regions
        # Master P1-A eje_cafetero: boutique 280K, standard 260K
        assert regions["eje_cafetero"]["min_adr"] == 260_000
        assert regions["eje_cafetero"]["max_adr"] == 280_000
        assert regions["eje_cafetero"]["min_rooms"] == 10
        assert regions["eje_cafetero"]["max_rooms"] == 60
        # Región default del master (key "any") también se convierte
        assert "default" in regions

    def test_load_master_missing_path_returns_empty(self):
        """Master ausente → {} (el orquestador cae a defaults documentados)."""
        assert load_benchmark_master(str(REPO_ROOT / "no_existe.json")) == {}

    def test_controller_wires_master_to_orchestrator(self):
        """OnboardingController pasa el master al TwoPhaseOrchestrator (D4)."""
        controller = OnboardingController(benchmark_master_path=str(MASTER_PATH))

        plan_data = controller._orchestrator.plan_maestro_data
        assert plan_data.get("master_source") == "regional_adr_2026"
        assert plan_data["regions"]["eje_cafetero"]["max_adr"] == 280_000

    def test_controller_hook_range_uses_master(self, patch_comision):
        """End-to-end: el hook del controller usa el master real cableado."""
        controller = OnboardingController(benchmark_master_path=str(MASTER_PATH))

        state = controller.start_onboarding(
            hotel_url="https://www.hoteltest.com",
            hotel_name="Hotel Test",
            region="eje_cafetero",
        )

        phase1 = state.phase_1_result
        assert phase1 is not None
        # min con master: 10 hab * 30 * 0.512 * 0.70 * 260000 * 0.20 * 0.20 = 1.118.208
        assert phase1.loss_range_min == pytest.approx(1_118_208.0)
        # max original del master sería 7.225.344 (ratio 6.46x) → cap 5x
        assert phase1.loss_range_max == pytest.approx(1_118_208.0 * 5.0)
        assert phase1.loss_range_max / phase1.loss_range_min <= 5.0


class TestPlausibilityCap:
    """T2 (D7): cap de plausibilidad configurable sobre el rango del hook."""

    def test_cap_limits_ratio_on_default_path(self, patch_comision):
        """El path sin master (ratio 23x histórico de F6) queda acotado."""
        orchestrator = TwoPhaseOrchestrator()

        loss_min, loss_max = orchestrator._calculate_hook_range("default")

        assert loss_max / loss_min <= HOOK_RANGE_MAX_RATIO_FALLBACK
        assert loss_max == pytest.approx(loss_min * HOOK_RANGE_MAX_RATIO_FALLBACK)

    def test_cap_is_configurable(self, patch_comision):
        """El umbral del cap se lee de config/financial_defaults.yaml."""
        orchestrator = TwoPhaseOrchestrator()

        with patch(CONFIG_PATCH_TARGET, return_value={"hook_range_max_ratio": 3.0}):
            loss_min, loss_max = orchestrator._calculate_hook_range("default")

        assert loss_max / loss_min <= 3.0
        assert loss_max == pytest.approx(loss_min * 3.0)

    def test_cap_not_applied_when_range_within_threshold(self, patch_comision, master_plan_data):
        """Rango dentro del umbral NO se trunca (no altera datos válidos)."""
        orchestrator = TwoPhaseOrchestrator(plan_maestro_data=master_plan_data)

        loss_min, loss_max = orchestrator._calculate_hook_range("eje_test")

        # ratio 3.6x < 5.0 → intacto
        assert loss_max == pytest.approx(3_024_000.0)

    def test_hook_message_shows_capped_range(self, patch_comision):
        """El hook message muestra el rango ya acotado por el cap."""
        orchestrator = TwoPhaseOrchestrator()

        with patch(CONFIG_PATCH_TARGET, return_value={"hook_range_max_ratio": 3.0}):
            result = orchestrator.phase_1_hook(
                hotel_url="https://www.hoteltest.com",
                hotel_name="Hotel Test",
                region="default",
            )

        # min 604.800 → max capado a 1.814.400 (3x)
        assert "604.800" in result.hook_message
        assert "1.814.400" in result.hook_message
        assert result.loss_range_max == pytest.approx(604_800.0 * 3.0)

    def test_cap_fallback_when_config_unavailable(self):
        """Sin config disponible, el cap usa el fallback documentado."""
        with patch(CONFIG_PATCH_TARGET, side_effect=YAMLLoadError("no config")):
            assert (
                TwoPhaseOrchestrator._get_hook_range_max_ratio()
                == HOOK_RANGE_MAX_RATIO_FALLBACK
            )

    def test_cap_never_below_one(self):
        """Un valor inválido de config nunca produce ratio menor que 1.0."""
        with patch(CONFIG_PATCH_TARGET, return_value={"hook_range_max_ratio": 0.2}):
            assert TwoPhaseOrchestrator._get_hook_range_max_ratio() == 1.0
