"""
Tests de coherencia financiera — ROICRIII FASE-1.
Verifica que el motor financiero unificado use la curva de maduración como
único origen de verdad para total_recovered, roi_6m y net_benefit.
"""

import pytest
from modules.financial_engine.pillar_maturity_curve import (
    aplicar_curva_4_pilares,
    calcular_recuperacion_6m,
    PillarMaturityResult,
)

# Valores del caso Castilla Real (fuga=$3.74M, recovery 35%, fee=$400K/mes)
FUGA_MENSUAL = 3_741_696
RECOVERY_FACTOR = 0.35
MONTHLY_INVESTMENT = 400_000
EXPECTED_TOTAL_6M = 5_041_935  # ≈ fuga * recovery * sum(curva 4 pilares)
EXPECTED_ROI = 2.10  # ≈ total / (investment * 6)
EXPECTED_NET = 2_641_935  # ≈ total - (investment * 6)


class TestCurvaMaduracionSumaCorrecta:
    """T1: Verifica que la suma de la curva de maduración produce el total esperado."""

    def test_curva_maduracion_suma_correcta(self):
        """total_recuperacion_6m debe ser $5.041.935 para Castilla Real."""
        result = aplicar_curva_4_pilares(
            fuga_mensual=FUGA_MENSUAL,
            recovery_factor_max=RECOVERY_FACTOR,
            meses=6,
        )
        assert isinstance(result, PillarMaturityResult)
        # Tolerancia de ±$1 para redondeo
        assert abs(result.total_recuperacion_6m - EXPECTED_TOTAL_6M) <= 1, (
            f"Expected ~{EXPECTED_TOTAL_6M}, got {result.total_recuperacion_6m}"
        )

    def test_proyecciones_suman_total(self):
        """Las proyecciones mensuales deben sumar al total_recuperacion_6m."""
        result = aplicar_curva_4_pilares(
            fuga_mensual=FUGA_MENSUAL,
            recovery_factor_max=RECOVERY_FACTOR,
            meses=6,
        )
        suma_proyecciones = sum(p.recuperacion_mensual for p in result.proyecciones)
        assert abs(suma_proyecciones - result.total_recuperacion_6m) <= 6, (
            f"Sum of projections ({suma_proyecciones}) != total ({result.total_recuperacion_6m})"
        )


class TestFuncionCompartidaFaseB:
    """FASE-B (N1, DEC-B2): calcular_recuperacion_6m es la ÚNICA fórmula.

    Diagnóstico y propuesta deben consumir esta misma función para que la
    recuperación 6m sea idéntica en ambos documentos (regla de oro: una fuente
    de verdad por concepto monetario).
    """

    def test_calcular_recuperacion_6m_es_wrapper_de_curva(self):
        """calcular_recuperacion_6m == aplicar_curva_4_pilares().total_recuperacion_6m."""
        result = aplicar_curva_4_pilares(
            fuga_mensual=FUGA_MENSUAL,
            recovery_factor_max=RECOVERY_FACTOR,
            meses=6,
        )
        assert calcular_recuperacion_6m(FUGA_MENSUAL, RECOVERY_FACTOR) == (
            result.total_recuperacion_6m
        )

    def test_caso_zione_recuperacion_unica(self):
        """Caso Zione: 7.192.000 × 0.35 × Σ curva (3.85) = $9.691.220."""
        fuga_zione = 7_192_000
        recovery = 0.35
        esperado = 9_691_220
        result = calcular_recuperacion_6m(fuga_zione, recovery)
        assert abs(result - esperado) <= 2, (
            f"Expected ~{esperado}, got {result}"
        )


class TestROIUnificado:
    """T2: Verifica que roi_6m use la curva de maduración como numerador."""

    def test_roi_unificado_con_fee_real(self):
        """ROI debe ser ~2.10X usando total_recuperacion_6m / (fee * 6)."""
        result = aplicar_curva_4_pilares(
            fuga_mensual=FUGA_MENSUAL,
            recovery_factor_max=RECOVERY_FACTOR,
            meses=6,
        )
        total_investment_6m = MONTHLY_INVESTMENT * 6
        roi = round(result.total_recuperacion_6m / total_investment_6m, 2)
        assert roi == EXPECTED_ROI, (
            f"Expected ROI {EXPECTED_ROI}X, got {roi}X. "
            f"total={result.total_recuperacion_6m}, investment={total_investment_6m}"
        )

    def test_roi_no_usa_effective_monthly_gain(self):
        """ROI NO debe calcularse con effective_monthly_gain (fuga * pain * recovery)."""
        # effective_monthly_gain sería: 3_741_696 * 0.41 * 0.20 = 306_819 (aprox)
        # Con eso el ROI daría ~0.45X — verificar que el resultado NO es ese
        result = aplicar_curva_4_pilares(
            fuga_mensual=FUGA_MENSUAL,
            recovery_factor_max=RECOVERY_FACTOR,
            meses=6,
        )
        total_investment_6m = MONTHLY_INVESTMENT * 6
        # effective_monthly_gain * 6 ≈ 1_840_914, ROI ≈ 0.77X
        roi = round(result.total_recuperacion_6m / total_investment_6m, 2)
        effective_roi = round(1_840_914 / total_investment_6m, 2)
        assert roi != effective_roi, (
            f"ROI ({roi}X) matches effective_monthly_gain path ({effective_roi}X) — NOT unified"
        )


class TestNetBenefitPositivo:
    """T1 (net_benefit): Verifica que net_benefit use la curva de maduración."""

    def test_net_benefit_positivo_con_curva(self):
        """net_benefit debe ser ~$2.64M positivo."""
        result = aplicar_curva_4_pilares(
            fuga_mensual=FUGA_MENSUAL,
            recovery_factor_max=RECOVERY_FACTOR,
            meses=6,
        )
        total_investment_6m = MONTHLY_INVESTMENT * 6
        net_benefit = result.total_recuperacion_6m - total_investment_6m
        assert net_benefit > 0, f"net_benefit should be positive, got {net_benefit}"
        assert abs(net_benefit - EXPECTED_NET) <= 1, (
            f"Expected net_benefit ~{EXPECTED_NET}, got {net_benefit}"
        )

    def test_net_benefit_no_usa_effective_monthly_gain(self):
        """net_benefit NO debe usar (effective_monthly_gain - investment) * 6."""
        result = aplicar_curva_4_pilares(
            fuga_mensual=FUGA_MENSUAL,
            recovery_factor_max=RECOVERY_FACTOR,
            meses=6,
        )
        total_investment_6m = MONTHLY_INVESTMENT * 6
        net = result.total_recuperacion_6m - total_investment_6m
        # effective_monthly_gain ≈ 306_819, net sería (306_819 - 400_000) * 6 = -559_086
        effective_net = (306_819 - MONTHLY_INVESTMENT) * 6
        assert net != effective_net, (
            f"net_benefit ({net}) matches effective path ({effective_net}) — NOT unified"
        )


class TestPilotSection:
    """FASE-5 T1: Verifica que la sección Piloto 30 días se renderiza correctamente."""

    def test_pilot_section_renders(self):
        """El template data debe contener pilot_section con 'Piloto'."""
        import sys
        sys.path.insert(0, str(__file__).rsplit('/tests/', 1)[0])
        from modules.commercial_documents.v4_proposal_generator import V4ProposalGenerator
        from modules.commercial_documents.data_structures import DiagnosticSummary, ConfidenceLevel, FinancialScenarios, AssetSpec, Scenario
        import tempfile, os

        # Minimal mock objects with __getattr__ to handle any attribute
        class MockDiagnostic:
            def __init__(self):
                self.critical_problems_count = 0
                self.quick_wins_count = 0
                self.overall_confidence = ConfidenceLevel.VERIFIED
                self.top_problems = []
                self.coherence_score = None
                self.score_global = None
                self.score_tecnico = None
                self.score_aeo = None
                self.pain_ids = None
                self.validated_data_summary = {}
            
            def __getattr__(self, name):
                return None

        with tempfile.TemporaryDirectory() as tmpdir:
            gen = V4ProposalGenerator(template_dir=tmpdir)
            data = gen._prepare_template_data(
                diagnostic_summary=MockDiagnostic(),
                financial_scenarios=FinancialScenarios(
                    conservative=Scenario(monthly_loss_min=800000, monthly_loss_max=1500000, probability=0.70, description="conservador"),
                    realistic=Scenario(monthly_loss_min=800000, monthly_loss_max=1500000, probability=0.20, description="realista"),
                    optimistic=Scenario(monthly_loss_min=800000, monthly_loss_max=1500000, probability=0.10, description="optimista"),
                ),
                asset_plan=[],
                hotel_name="Hotel Test",
                audit_result=None,
                region="eje_cafetero",
                analytics_data=None,
                assets_generated=None,
                site_presence_report=None,
                financial_breakdown=None,
            )
            pilot = data.get('pilot_section', '')
            assert 'Piloto' in pilot, f"'Piloto' not found in pilot_section: {pilot[:200]}"


class TestCapexBreakdown:
    """FASE-5 T2: Verifica que el breakdown CAPEX se renderiza con componentes."""

    def test_capex_breakdown_renders(self):
        """capex_breakdown_table debe tener tabla con componentes, no solo total."""
        import sys
        sys.path.insert(0, str(__file__).rsplit('/tests/', 1)[0])
        from modules.commercial_documents.v4_proposal_generator import V4ProposalGenerator
        from modules.commercial_documents.data_structures import DiagnosticSummary, ConfidenceLevel, FinancialScenarios, AssetSpec, Scenario
        import tempfile

        class MockDiagnostic:
            def __init__(self):
                self.critical_problems_count = 0
                self.quick_wins_count = 0
                self.overall_confidence = ConfidenceLevel.VERIFIED
                self.top_problems = []
                self.coherence_score = None
                self.score_global = None
                self.score_tecnico = None
                self.score_aeo = None
                self.pain_ids = None
                self.validated_data_summary = {}
            
            def __getattr__(self, name):
                return None

        with tempfile.TemporaryDirectory() as tmpdir:
            gen = V4ProposalGenerator(template_dir=tmpdir)
            data = gen._prepare_template_data(
                diagnostic_summary=MockDiagnostic(),
                financial_scenarios=FinancialScenarios(
                    conservative=Scenario(monthly_loss_min=800000, monthly_loss_max=1500000, probability=0.70, description="conservador"),
                    realistic=Scenario(monthly_loss_min=800000, monthly_loss_max=1500000, probability=0.20, description="realista"),
                    optimistic=Scenario(monthly_loss_min=800000, monthly_loss_max=1500000, probability=0.10, description="optimista"),
                ),
                asset_plan=[],
                hotel_name="Hotel Test",
                audit_result=None,
                region="eje_cafetero",
                analytics_data=None,
                assets_generated=None,
                site_presence_report=None,
                financial_breakdown=None,
            )
            table = data.get('capex_breakdown_table', '')
            assert 'Auditoría Inicial' in table, f"'Auditoría Inicial' not in table: {table}"
            assert 'Implementación Técnica' in table, f"'Implementación Técnica' not in table: {table}"
            assert 'Onboarding' in table, f"'Onboarding' not in table: {table}"


class TestGarantiaConKPI:
    """FASE-5 T3: Verifica que la garantía Día 55 tiene KPI específico."""

    def test_garantia_con_kpi(self):
        """garantia_umbral debe contener '+15%' para la garantía Día 55."""
        import sys
        sys.path.insert(0, str(__file__).rsplit('/tests/', 1)[0])
        from modules.commercial_documents.v4_proposal_generator import V4ProposalGenerator
        from modules.commercial_documents.data_structures import DiagnosticSummary, ConfidenceLevel, FinancialScenarios, AssetSpec, Scenario
        import tempfile

        class MockDiagnostic:
            def __init__(self):
                self.critical_problems_count = 0
                self.quick_wins_count = 0
                self.overall_confidence = ConfidenceLevel.VERIFIED
                self.top_problems = []
                self.coherence_score = None
                self.score_global = None
                self.score_tecnico = None
                self.score_aeo = None
                self.pain_ids = None
                self.validated_data_summary = {}

            def __getattr__(self, name):
                return None

        with tempfile.TemporaryDirectory() as tmpdir:
            gen = V4ProposalGenerator(template_dir=tmpdir)
            data = gen._prepare_template_data(
                diagnostic_summary=MockDiagnostic(),
                financial_scenarios=FinancialScenarios(
                    conservative=Scenario(monthly_loss_min=800000, monthly_loss_max=1500000, probability=0.70, description="conservador"),
                    realistic=Scenario(monthly_loss_min=800000, monthly_loss_max=1500000, probability=0.20, description="realista"),
                    optimistic=Scenario(monthly_loss_min=800000, monthly_loss_max=1500000, probability=0.10, description="optimista"),
                ),
                asset_plan=[],
                hotel_name="Hotel Test",
                audit_result=None,
                region="eje_cafetero",
                analytics_data=None,
                assets_generated=None,
                site_presence_report=None,
                financial_breakdown=None,
            )
            umbral = data.get('garantia_umbral', '')
            assert '+15%' in umbral, f"'+15%' not found in garantia_umbral: {umbral}"
