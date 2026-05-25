"""
Tests FIN-3: Precision-based financial rendering.

Tests:
1. test_tier_a_shows_exact_money - Sin advertencia, cifra exacta
2. test_tier_c_shows_range_not_exact - Rango "~$X–$Y", no cifra puntual
3. test_tier_c_shows_warning - Bloque de advertencia presente
4. test_tier_c_shows_onboarding_cta - CTA de onboarding presente
5. test_regional_benchmark_source_label - "benchmark regional" en label
6. test_template_vars_injected_correctly - Variables en template_vars dict
7. test_financial_breakdown_section_only_when_exact - Breakdown solo Tier A
8. test_monthly_loss_display_format - Formato correcto del display
"""
import pytest
from unittest.mock import MagicMock
from modules.commercial_documents.v4_diagnostic_generator import V4DiagnosticGenerator
from modules.commercial_documents.data_structures import (
    FinancialScenarios,
    FinancialBreakdown,
    Scenario,
    ValidationSummary,
    ValidatedField,
    ConfidenceLevel,
    format_cop,
)


def make_scenarios(
    central_cons=2_000_000,
    central_real=2_610_000,
    central_opt=3_100_000,
    min_real=2_000_000,
    max_real=3_132_000,
):
    """Helper: create FinancialScenarios with monthly_loss_central set."""
    return FinancialScenarios(
        conservative=Scenario(
            monthly_loss_min=1_500_000,
            monthly_loss_max=2_500_000,
            probability=0.7,
            description="Conservador",
            monthly_loss_central=central_cons,
        ),
        realistic=Scenario(
            monthly_loss_min=min_real,
            monthly_loss_max=max_real,
            probability=0.2,
            description="Realista",
            monthly_loss_central=central_real,
        ),
        optimistic=Scenario(
            monthly_loss_min=2_500_000,
            monthly_loss_max=3_700_000,
            probability=0.1,
            description="Optimista",
            monthly_loss_central=central_opt,
        ),
    )


def make_validation_summary_tier_a():
    """Validation summary with Tier A data (all MEASURED sources)."""
    fields = [
        ValidatedField(
            field_name="adr_cop",
            value=150000.0,
            confidence=ConfidenceLevel.VERIFIED,
            sources=["user_provided"],
        ),
        ValidatedField(
            field_name="occupancy_rate",
            value=0.65,
            confidence=ConfidenceLevel.VERIFIED,
            sources=["user_provided"],
        ),
        ValidatedField(
            field_name="direct_channel_percentage",
            value=0.30,
            confidence=ConfidenceLevel.VERIFIED,
            sources=["user_provided"],
        ),
    ]
    return ValidationSummary(fields=fields, overall_confidence=ConfidenceLevel.VERIFIED, conflicts=[])


def make_validation_summary_tier_b():
    """Validation summary with Tier B data (one REGIONAL_BENCHMARK source)."""
    fields = [
        ValidatedField(
            field_name="adr_cop",
            value=150000.0,
            confidence=ConfidenceLevel.ESTIMATED,
            sources=["regional_v410"],
        ),
        ValidatedField(
            field_name="occupancy_rate",
            value=0.65,
            confidence=ConfidenceLevel.ESTIMATED,
            sources=["web_scraping"],
        ),
        ValidatedField(
            field_name="direct_channel_percentage",
            value=0.30,
            confidence=ConfidenceLevel.ESTIMATED,
            sources=["web_scraping"],
        ),
    ]
    return ValidationSummary(fields=fields, overall_confidence=ConfidenceLevel.ESTIMATED, conflicts=[])


def make_validation_summary_tier_c():
    """Validation summary with Tier C data (DEFAULTED/estimated sources)."""
    fields = [
        ValidatedField(
            field_name="adr_cop",
            value=150000.0,
            confidence=ConfidenceLevel.ESTIMATED,
            sources=["estimated"],
        ),
        ValidatedField(
            field_name="occupancy_rate",
            value=0.65,
            confidence=ConfidenceLevel.ESTIMATED,
            sources=["estimated"],
        ),
        ValidatedField(
            field_name="direct_channel_percentage",
            value=0.30,
            confidence=ConfidenceLevel.ESTIMATED,
            sources=["estimated"],
        ),
    ]
    return ValidationSummary(fields=fields, overall_confidence=ConfidenceLevel.ESTIMATED, conflicts=[])


class TestPrecisionRendering:
    """Test _prepare_financial_template_vars() for precision-based rendering."""

    def test_tier_a_shows_exact_money(self):
        """Tier A: Sin advertencia, cifra exacta."""
        gen = V4DiagnosticGenerator()
        scenarios = make_scenarios()
        validation_summary = make_validation_summary_tier_a()

        result = gen._prepare_financial_template_vars(
            scenarios, validation_summary, analytics_data=None,
            ota_commission_basis="Estimación basada en escenario realista",
            ota_commission_source="onboarding",
            ota_commission_real_formatted="$5.400.000 COP",
        )

        # Tier A should show exact money
        assert result['can_show_exact_money'] is True
        assert result['precision_tier'] == 'A'
        
        # monthly_loss_display should be exact (not a range)
        assert '~' not in result['monthly_loss_display']
        assert '–' not in result['monthly_loss_display']
        
        # No warning for Tier A
        assert result['precision_warning'] == ''
        
        # No CTA for Tier A
        assert result['show_onboarding_cta'] == ''

    def test_tier_c_shows_range_not_exact(self):
        """Tier C: Rango '~$X–$Y', no cifra puntual."""
        gen = V4DiagnosticGenerator()
        scenarios = make_scenarios(min_real=2_000_000, max_real=3_132_000)
        validation_summary = make_validation_summary_tier_c()

        result = gen._prepare_financial_template_vars(
            scenarios, validation_summary, analytics_data=None,
            ota_commission_basis="Estimación basada en escenario realista",
            ota_commission_source="benchmark",
            ota_commission_real_formatted="$5.400.000 COP",
        )

        # Tier C should NOT show exact money
        assert result['can_show_exact_money'] is False
        assert result['precision_tier'] == 'C'
        
        # monthly_loss_display should be a range
        assert '~' in result['monthly_loss_display']
        assert '–' in result['monthly_loss_display']
        assert '2.000.000' in result['monthly_loss_display']
        assert '3.132.000' in result['monthly_loss_display']

    def test_tier_c_shows_warning(self):
        """Tier C: Bloque de advertencia presente."""
        gen = V4DiagnosticGenerator()
        scenarios = make_scenarios()
        validation_summary = make_validation_summary_tier_c()

        result = gen._prepare_financial_template_vars(
            scenarios, validation_summary, analytics_data=None,
        )

        # FASE-B: disclaimer converted to opportunity hook (formerly "⚠️ Precisión limitada — Tier C")
        assert result['precision_warning'] != ''
        assert 'OPORTUNIDAD DE AUDITORÍA' in result['precision_warning']

    def test_tier_c_shows_onboarding_cta(self):
        """Tier C: CTA de onboarding presente y específico."""
        gen = V4DiagnosticGenerator()
        scenarios = make_scenarios()
        validation_summary = make_validation_summary_tier_c()

        result = gen._prepare_financial_template_vars(
            scenarios, validation_summary, analytics_data=None,
        )

        cta = result['show_onboarding_cta']
        assert cta != ''
        assert 'onboarding' in cta.lower()
        assert 'Quiere saber su cifra exacta' in cta
        # Verificar que los 4 datos requeridos están mencionados
        assert 'habitaciones' in cta.lower()
        assert 'reservas' in cta.lower()
        assert 'reserva' in cta.lower()
        assert 'canal directo' in cta.lower()

    def test_tier_b_shows_warning(self):
        """Tier B: Bloque de advertencia presente con contenido diferenciado."""
        gen = V4DiagnosticGenerator()
        scenarios = make_scenarios()
        validation_summary = make_validation_summary_tier_b()

        result = gen._prepare_financial_template_vars(
            scenarios, validation_summary, analytics_data=None,
        )

        # Warning should be present for Tier B
        assert result['precision_warning'] != ''
        assert 'OPORTUNIDAD DE AUDITORÍA' in result['precision_warning']

    def test_regional_benchmark_source_label(self):
        """Label de fuente ADR indica 'benchmark regional' para fuentes regional_v410."""
        gen = V4DiagnosticGenerator()
        scenarios = make_scenarios()
        validation_summary = make_validation_summary_tier_b()  # has regional_v410

        result = gen._prepare_financial_template_vars(
            scenarios, validation_summary, analytics_data=None,
        )

        assert result['adr_source_label'] == 'benchmark regional'

    def test_user_provided_source_label(self):
        """Label de fuente ADR indica 'datos del hotel' para fuentes user_provided."""
        gen = V4DiagnosticGenerator()
        scenarios = make_scenarios()
        validation_summary = make_validation_summary_tier_a()  # has user_provided

        result = gen._prepare_financial_template_vars(
            scenarios, validation_summary, analytics_data=None,
        )

        assert result['adr_source_label'] == 'datos del hotel'

    def test_template_vars_injected_correctly(self):
        """Todas las variables de precision estan en el dict retornado."""
        gen = V4DiagnosticGenerator()
        scenarios = make_scenarios()
        validation_summary = make_validation_summary_tier_c()

        result = gen._prepare_financial_template_vars(
            scenarios, validation_summary, analytics_data=None,
        )

        # All required keys present
        required_keys = [
            'monthly_loss_display',
            'precision_tier',
            'can_show_exact_money',
            'precision_warning',
            'show_onboarding_cta',
            'adr_source_label',
            'financial_breakdown_section',
        ]
        for key in required_keys:
            assert key in result, f"Missing key: {key}"

    def test_financial_breakdown_section_only_when_exact(self):
        """Financial breakdown section solo presente cuando can_show_exact=True."""
        gen = V4DiagnosticGenerator()
        scenarios = make_scenarios()

        # Tier C - no breakdown
        result_c = gen._prepare_financial_template_vars(
            scenarios, make_validation_summary_tier_c(), analytics_data=None,
            ota_commission_basis="test basis",
            ota_commission_source="benchmark",
        )
        assert result_c['financial_breakdown_section'] == ''

        # Tier A - has breakdown
        result_a = gen._prepare_financial_template_vars(
            scenarios, make_validation_summary_tier_a(), analytics_data=None,
            ota_commission_basis="test basis",
            ota_commission_source="onboarding",
            ota_commission_real_formatted="$5.400.000 COP",
        )
        assert result_a['financial_breakdown_section'] != ''
        assert 'Desglose' in result_a['financial_breakdown_section']
        assert 'test basis' in result_a['financial_breakdown_section']

    def test_monthly_loss_display_format_exact(self):
        """monthly_loss_display formato correcto para Tier A (exacto)."""
        gen = V4DiagnosticGenerator()
        scenarios = make_scenarios(central_real=2_610_000)
        validation_summary = make_validation_summary_tier_a()

        result = gen._prepare_financial_template_vars(
            scenarios, validation_summary, analytics_data=None,
        )

        # Should use format_cop format (no ~, no range)
        assert '2.610.000' in result['monthly_loss_display']
        assert '~' not in result['monthly_loss_display']

    def test_monthly_loss_display_format_range(self):
        """monthly_loss_display formato correcto para Tier C (rango)."""
        gen = V4DiagnosticGenerator()
        scenarios = make_scenarios(min_real=2_000_000, max_real=3_132_000)
        validation_summary = make_validation_summary_tier_c()

        result = gen._prepare_financial_template_vars(
            scenarios, validation_summary, analytics_data=None,
        )

        # Should be range format with ~
        assert result['monthly_loss_display'].startswith('~')
        assert '2.000.000' in result['monthly_loss_display']
        assert '3.132.000' in result['monthly_loss_display']
        assert 'COP/mes' in result['monthly_loss_display']

    def test_no_validation_summary_defaults_tier_c(self):
        """Sin validation_summary, se asume Tier C (conservador)."""
        gen = V4DiagnosticGenerator()
        scenarios = make_scenarios()

        result = gen._prepare_financial_template_vars(
            scenarios, None, analytics_data=None,
        )

        assert result['precision_tier'] == 'C'
        assert result['can_show_exact_money'] is False
        assert '~' in result['monthly_loss_display']
        assert result['precision_warning'] != ''
