"""Test F5: Comisión OTA parametrizada con rango y fuente.

Este test verifica que la comisión OTA se lee desde config/financial_defaults.yaml
en lugar de estar hardcodeada en 0.15 (15%). El rango correcto es 18-22% con base 20%.

FASE-P1-B del plan CREDIBILIDAD-NUMERICA-2026-08-20.
"""
import pytest
from modules.utils.financial_factors import FinancialFactors


class TestOTACommissionParametrized:
    """Tests para la comisión OTA parametrizada (F5)."""

    @pytest.fixture
    def factors(self):
        """Fixture que crea una instancia de FinancialFactors."""
        return FinancialFactors()

    def test_comision_ota_base_is_020(self, factors):
        """F5: La comisión OTA base debe ser 0.20 (20%), no 0.15 (15%)."""
        ota = factors.get_comision_ota()
        assert ota['base'] == 0.20, f"Esperado 0.20, obtenido {ota['base']}"

    def test_comision_ota_range(self, factors):
        """F5: El rango de comisión OTA debe ser 18-22%."""
        ota = factors.get_comision_ota()
        assert ota['min'] == 0.18, f"Esperado min 0.18, obtenido {ota['min']}"
        assert ota['max'] == 0.22, f"Esperado max 0.22, obtenido {ota['max']}"

    def test_comision_ota_source_exists(self, factors):
        """F5: La fuente de comisión OTA debe estar documentada."""
        ota = factors.get_comision_ota()
        assert 'source' in ota, "Falta 'source' en comisión OTA"
        assert len(ota['source']) > 0, "Source no puede estar vacío"
        assert 'financial_defaults.yaml' in ota['source'], \
            f"Source debe referenciar financial_defaults.yaml, obtenido: {ota['source']}"

    def test_financial_factors_config_has_source(self, factors):
        """F5: FinancialFactorsConfig debe incluir comision_ota_source."""
        config = factors.get_config('default')
        assert hasattr(config, 'comision_ota_source'), \
            "FinancialFactorsConfig debe tener campo comision_ota_source"
        assert len(config.comision_ota_source) > 0, \
            "comision_ota_source no puede estar vacío"

    def test_scenario_calculator_uses_config(self):
        """F5: ScenarioCalculator debe usar comisión OTA de config."""
        from modules.financial_engine.scenario_calculator import ScenarioCalculator

        calc = ScenarioCalculator()
        # El default debe ser 0.20 (de config), no 0.15
        assert calc.default_ota_commission == 0.20, \
            f"ScenarioCalculator debe usar 0.20, obtenido {calc.default_ota_commission}"

    def test_hotel_financial_data_default(self):
        """F5: HotelFinancialData debe tener default 0.20 para ota_commission_rate."""
        from modules.financial_engine.scenario_calculator import HotelFinancialData

        # Crear con defaults mínimos
        data = HotelFinancialData(
            rooms=20,
            adr_cop=300000,
            occupancy_rate=0.50
        )
        assert data.ota_commission_rate == 0.20, \
            f"HotelFinancialData default debe ser 0.20, obtenido {data.ota_commission_rate}"

    def test_calculator_v2_default(self):
        """F5: calculate_financial_scenarios debe tener default 0.20."""
        from modules.financial_engine.calculator_v2 import calculate_financial_scenarios
        import inspect

        sig = inspect.signature(calculate_financial_scenarios)
        ota_param = sig.parameters['ota_commission_rate']
        assert ota_param.default == 0.20, \
            f"calculate_financial_scenarios default debe ser 0.20, obtenido {ota_param.default}"

    def test_inputs_contract_default(self):
        """F5: FinancialInputsContract debe tener default 0.20."""
        from modules.financial_engine.inputs_contract import FinancialInputsContract

        contract = FinancialInputsContract(
            rooms=20,
            adr_cop=300000,
            occupancy_rate=0.50
        )
        assert contract.ota_commission_rate == 0.20, \
            f"FinancialInputsContract default debe ser 0.20, obtenido {contract.ota_commission_rate}"

    def test_financial_evidence_default(self):
        """F5: FinancialEvidence debe tener default 0.20 para ota_commission_rate."""
        from modules.financial_engine.financial_evidence import FinancialEvidence

        evidence = FinancialEvidence(
            adr_cop=__import__('modules.financial_engine.financial_evidence', fromlist=['FieldEvidence']).FieldEvidence(
                value=300000, source='test', epistemic_status=__import__('modules.financial_engine.financial_evidence', fromlist=['EpistemicStatus']).EpistemicStatus.MEASURED
            ),
            occupancy_rate=__import__('modules.financial_engine.financial_evidence', fromlist=['FieldEvidence']).FieldEvidence(
                value=0.50, source='test', epistemic_status=__import__('modules.financial_engine.financial_evidence', fromlist=['EpistemicStatus']).EpistemicStatus.MEASURED
            ),
            direct_channel_percentage=__import__('modules.financial_engine.financial_evidence', fromlist=['FieldEvidence']).FieldEvidence(
                value=0.30, source='test', epistemic_status=__import__('modules.financial_engine.financial_evidence', fromlist=['EpistemicStatus']).EpistemicStatus.MEASURED
            )
        )
        assert evidence.ota_commission_rate.value == 0.20, \
            f"FinancialEvidence default debe ser 0.20, obtenido {evidence.ota_commission_rate.value}"

    def test_trace_data_sources_uses_config(self):
        """F5: _trace_data_sources debe usar fuente de config, no 'industry_standard_15pct'."""
        from modules.financial_engine.scenario_calculator import ScenarioCalculator, HotelFinancialData

        calc = ScenarioCalculator()
        hotel_data = HotelFinancialData(
            rooms=20,
            adr_cop=300000,
            occupancy_rate=0.50
        )
        sources = calc._trace_data_sources(hotel_data)
        assert 'industry_standard_15pct' not in sources['ota_commission'], \
            f"Source no debe ser 'industry_standard_15pct', obtenido: {sources['ota_commission']}"
        assert 'financial_defaults.yaml' in sources['ota_commission'], \
            f"Source debe referenciar financial_defaults.yaml, obtenido: {sources['ota_commission']}"

    def test_two_phase_flow_uses_config(self):
        """F5: two_phase_flow debe usar comisión OTA de config."""
        # Verificar que el módulo importa FinancialFactors
        import modules.orchestration_v4.two_phase_flow as tpf
        assert hasattr(tpf, 'FinancialFactors'), \
            "two_phase_flow debe importar FinancialFactors"

    def test_benchmarks_default_data(self):
        """F5: DEFAULT_DATA en benchmarks.py debe tener comision_ota_base = 0.20."""
        from modules.utils.benchmarks import DEFAULT_DATA

        default_region = DEFAULT_DATA['regiones']['default']
        assert default_region['comision_ota_base'] == 0.20, \
            f"DEFAULT_DATA comision_ota_base debe ser 0.20, obtenido {default_region['comision_ota_base']}"
