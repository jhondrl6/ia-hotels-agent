"""
Tests FASE-F: Financial placeholders (Comisión OTA + Evidence Tiers).

Tests:
- test_financial_placeholders_filled: New placeholders are populated (not raw ${...})
- test_evidence_tier_default_c: Default tier is C when no GA4
- test_evidence_tier_a_with_ga4: Tier is A when GA4 is enabled
- test_scenario_table_rows_format: Scenario table has 3 rows with correct format
- test_backward_compat_loss_6_months: loss_6_months recalculated with central value
- test_disclaimer_present: Disclaimer is non-empty
- test_financial_title_label_no_ota: Label dice "Pérdida Mensual", no "Comisión OTA"
- test_ota_commission_real_from_breakdown: ota_commission_real_formatted viene del breakdown
- test_opportunity_cost_field_present: opportunity_cost_formatted presente y coincide
"""
import pytest
from unittest.mock import MagicMock
from modules.commercial_documents.v4_diagnostic_generator import V4DiagnosticGenerator
from modules.commercial_documents.data_structures import (
    FinancialScenarios,
    FinancialBreakdown,
    Scenario,
    format_cop,
)


def make_scenarios(
    central_cons=7_000_000,
    central_real=3_741_696,
    central_opt=1_000_000,
):
    """Helper: crear FinancialScenarios con monthly_loss_central set.

    FASE-B (D4): semántica real — conservative es el PEOR caso (mayor pérdida),
    realistic el más probable y optimistic el mejor caso.
    """
    return FinancialScenarios(
        conservative=Scenario(
            monthly_loss_min=5_000_000,
            monthly_loss_max=9_000_000,
            probability=0.7,
            description="Conservador",
            monthly_loss_central=central_cons,
        ),
        realistic=Scenario(
            monthly_loss_min=2_000_000,
            monthly_loss_max=5_500_000,
            probability=0.2,
            description="Realista",
            monthly_loss_central=central_real,
        ),
        optimistic=Scenario(
            monthly_loss_min=-1_000_000,
            monthly_loss_max=2_500_000,
            probability=0.1,
            description="Optimista",
            monthly_loss_central=central_opt,
        ),
    )


class TestFinancialPlaceholders:
    """Test _build_financial_placeholders() method."""

    def test_placeholders_filled_no_ga4(self):
        """Without GA4, placeholders are populated with defaults (Tier C)."""
        gen = V4DiagnosticGenerator()
        scenarios = make_scenarios()

        result = gen._build_financial_placeholders(scenarios, analytics_data=None)

        # All keys present
        for key in [
            'ota_commission_formatted',
            'ota_commission_basis',
            'ota_commission_source',
            'scenario_table_rows',
            'evidence_tier',
            'financial_disclaimer',
            'financial_source_ref',
            'financial_value_central',
            'financial_value_min',
            'financial_value_max',
            'financial_method',
            'loss_6_months',
        ]:
            assert key in result, f"Missing key: {key}"

        # No raw placeholders remain
        for key, val in result.items():
            assert '${' not in str(val), f"Key '{key}' has raw placeholder: {val}"

    def test_evidence_tier_default_c(self):
        """Default tier without GA4 is C."""
        gen = V4DiagnosticGenerator()
        scenarios = make_scenarios()

        result = gen._build_financial_placeholders(scenarios, analytics_data=None)

        assert result['evidence_tier'] == 'C'

    def test_evidence_tier_a_with_ga4(self):
        """With GA4 enabled, tier is A."""
        gen = V4DiagnosticGenerator()
        scenarios = make_scenarios()

        result = gen._build_financial_placeholders(
            scenarios,
            analytics_data={"use_ga4": True},
        )

        assert result['evidence_tier'] == 'A'

    def test_scenario_table_has_3_rows(self):
        """Scenario table must have 3 rows (Conservador/Realista/Optimista)."""
        gen = V4DiagnosticGenerator()
        scenarios = make_scenarios()

        result = gen._build_financial_placeholders(scenarios)
        table = result['scenario_table_rows']

        rows = [r for r in table.strip().split('\n') if r.strip()]
        assert len(rows) == 3, f"Expected 3 rows, got {len(rows)}"

    def test_scenario_table_format(self):
        """Each row is a valid markdown table row with | separators."""
        gen = V4DiagnosticGenerator()
        scenarios = make_scenarios()

        result = gen._build_financial_placeholders(scenarios)
        table = result['scenario_table_rows']

        valid_names = ('Peor caso (conservador)', 'Más probable', 'Mejor caso (optimista)')
        for row in table.strip().split('\n'):
            parts = [p.strip() for p in row.split('|') if p.strip()]
            assert len(parts) == 3, f"Row should have 3 columns: {row}"
            # Column 0: scenario name
            assert parts[0] in valid_names, f"Unexpected scenario name: {parts[0]}"
            # Column 1: formatted COP
            assert 'COP/mes' in parts[1]
            # Column 2: probability
            assert '%' in parts[2]

    def test_uses_central_value_not_max(self):
        """ota_commission_formatted uses central value, not monthly_loss_max."""
        gen = V4DiagnosticGenerator()
        scenarios = make_scenarios(central_real=2_610_000)

        result = gen._build_financial_placeholders(scenarios)

        # Should use central (2,610,000), not max (3,132,000)
        # format_cop uses dots: $2.610.000 COP
        assert '2.610.000' in result['ota_commission_formatted']
        assert result['financial_value_central'] == '2610000'

    def test_loss_6_months_uses_central(self):
        """loss_6_months is calculated from central value * 6."""
        gen = V4DiagnosticGenerator()
        scenarios = make_scenarios(central_real=2_610_000)

        result = gen._build_financial_placeholders(scenarios)

        expected_6m = 2_610_000 * 6  # 15,660,000
        assert result['loss_6_months'] == format_cop(expected_6m)

    def test_disclaimer_non_empty(self):
        """Disclaimer must be a non-empty string."""
        gen = V4DiagnosticGenerator()
        scenarios = make_scenarios()

        result = gen._build_financial_placeholders(scenarios)

        assert len(result['financial_disclaimer']) > 20
        assert 'estimaci' in result['financial_disclaimer'].lower() or \
               'datos' in result['financial_disclaimer'].lower()

    def test_financial_method_derived_from_peso_source(self):
        """FASE-B (D4): financial_method se deriva de la fuente real de pesos,
        nunca hardcodeado como 'proportional_normalized'."""
        gen = V4DiagnosticGenerator()
        scenarios = make_scenarios()

        # Sin pesos dinámicos → pain_weights_normalized (default)
        result = gen._build_financial_placeholders(scenarios)
        assert result['financial_method'] == 'pain_weights_normalized'

        # Con DynamicImpactCalculator activo → dynamic_impact_normalized
        result_dyn = gen._build_financial_placeholders(
            scenarios,
            brechas_pesos=[
                {"pain_id": "low_gbp_score", "impacto": 60.0, "peso_source": "dynamic_impact"}
            ],
        )
        assert result_dyn['financial_method'] == 'dynamic_impact_normalized'

    def test_recuperacion_proyectada_6m_curva_unica(self):
        """FASE-B (N1): recuperacion_proyectada_6m usa la curva compartida
        (fuga × recovery_realista × Σ curva), NO pain_ratio × recovery lineal."""
        from modules.financial_engine.pillar_maturity_curve import calcular_recuperacion_6m

        gen = V4DiagnosticGenerator()
        scenarios = make_scenarios(central_real=2_610_000)

        result = gen._build_financial_placeholders(scenarios)

        # recovery realista = 0.35 (config/scenarios.yaml) × Σ(CURVA_4_PILARES) = 3.85
        expected = int(calcular_recuperacion_6m(2_610_000, 0.35))
        assert result['recuperacion_proyectada_6m'] == format_cop(expected)

    def test_curva_maduracion_note_replaces_pain_ratio(self):
        """FASE-B (N1): curva_maduracion_note reemplaza pain_ratio_note y pain_pct
        ya no participa como multiplicador de recuperación."""
        gen = V4DiagnosticGenerator()
        scenarios = make_scenarios()

        result = gen._build_financial_placeholders(scenarios)
        assert 'curva_maduracion_note' in result
        assert '3.85' in result['curva_maduracion_note']
        assert 'pain_pct' not in result
        assert 'pain_ratio_note' not in result

    def test_financial_value_range_label_declares_realistic(self):
        """FASE-B (D4): el rango del frontmatter es del escenario MÁS PROBABLE y
        el label lo declara explícitamente (evita fuga mínima negativa en PDF)."""
        gen = V4DiagnosticGenerator()
        scenarios = make_scenarios()

        result = gen._build_financial_placeholders(scenarios)
        assert 'financial_value_range_label' in result
        assert 'más probable' in result['financial_value_range_label']
        assert '20%' in result['financial_value_range_label']

    def test_financial_title_label_no_ota(self):
        """Label NO dice 'Comisión OTA' — ahora dice 'Pérdida Mensual Estimada'."""
        gen = V4DiagnosticGenerator()
        scenarios = make_scenarios()

        # FASE-B: labels son honestos, NO dicen "Comisión OTA"
        result = gen._build_financial_placeholders(scenarios, source_reliability="verified")
        assert 'Pérdida Mensual' in result['financial_title_label']
        assert 'Comisión OTA' not in result['financial_title_label']

        result_unverified = gen._build_financial_placeholders(scenarios, source_reliability="unverified")
        assert 'Pérdida Mensual' in result_unverified['financial_title_label']
        assert 'Comisión OTA' not in result_unverified['financial_title_label']

    def test_ota_commission_real_from_breakdown(self):
        """ota_commission_real_formatted viene del breakdown, no del scenario loss."""
        gen = V4DiagnosticGenerator()
        scenarios = make_scenarios(central_real=2_610_000)

        # Breakdown con comision OTA real de $5,400,000
        breakdown = FinancialBreakdown(
            monthly_ota_commission_cop=5_400_000,
            ota_commission_basis="120 noches OTA × $300K ADR × 15%",
            ota_commission_source="onboarding",
            shift_savings_cop=540_000,
            shift_percentage=0.10,
            shift_source="benchmark",
            ia_revenue_cop=2_250_000,
            ia_boost_percentage=0.05,
            ia_source="estimado",
            evidence_tier="C",
            disclaimer="Test",
        )

        result = gen._build_financial_placeholders(
            scenarios, financial_breakdown=breakdown
        )

        # El valor principal (ota_commission_formatted) es el costo de oportunidad
        assert '2.610.000' in result['ota_commission_formatted']
        # El campo nuevo tiene la OTA real del breakdown
        assert result['ota_commission_real_formatted'] is not None
        assert '5.400.000' in result['ota_commission_real_formatted']

    def test_opportunity_cost_field_present(self):
        """opportunity_cost_formatted es el valor principal del escenario."""
        gen = V4DiagnosticGenerator()
        scenarios = make_scenarios(central_real=2_610_000)

        result = gen._build_financial_placeholders(scenarios)

        # Campo nuevo
        assert 'opportunity_cost_formatted' in result
        assert '2.610.000' in result['opportunity_cost_formatted']
        # Debe coincidir con ota_commission_formatted (backward compat)
        assert result['opportunity_cost_formatted'] == result['ota_commission_formatted']
