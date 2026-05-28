"""
tests/test_roi_unification.py
ROICRII FASE-1 — Unificar ROI: verifica motor unico roi_formatter

Tests:
  T1: _calculate_roi NO existe como metodo de la clase
  T2: calcular_metricas_roi() produce roi_saas con :.2f (2 decimales)
  T3: Solo UN motor de ROI (0 metodos inline, 1 import activo)
  T4: Castilla Real: roi_saas > 0 (no negativo)
  T5: roi_cap funciona correctamente
  T6: formatear_roi_para_propuesta usa :.2f
"""

import pytest
import sys
import inspect

sys.path.insert(0, str(__file__).rsplit('/', 2)[0])

from modules.financial_engine.roi_formatter import (
    calcular_metricas_roi,
    formatear_roi_para_propuesta,
    ROIMetrics,
)


class TestInlineMethodsDeleted:
    """T1 + T3: Verificar que no hay metodos inline de ROI."""

    def test_calculate_roi_method_does_not_exist(self):
        """_calculate_roi no debe existir como metodo de V4ProposalGenerator."""
        from modules.commercial_documents.v4_proposal_generator import V4ProposalGenerator
        methods = [name for name, _ in inspect.getmembers(V4ProposalGenerator, predicate=inspect.isfunction)]
        assert '_calculate_roi' not in methods, (
            "'_calculate_roi' method found in V4ProposalGenerator — should be deleted"
        )

    def test_calculate_roi_saas_method_does_not_exist(self):
        """_calculate_roi_saas no debe existir como metodo de V4ProposalGenerator."""
        from modules.commercial_documents.v4_proposal_generator import V4ProposalGenerator
        methods = [name for name, _ in inspect.getmembers(V4ProposalGenerator, predicate=inspect.isfunction)]
        assert '_calculate_roi_saas' not in methods, (
            "'_calculate_roi_saas' method found in V4ProposalGenerator — should be deleted"
        )

    def test_roi_formatter_is_imported(self):
        """V4ProposalGenerator debe importar calcular_metricas_roi y formatear_roi_para_propuesta."""
        import modules.commercial_documents.v4_proposal_generator as v4pg
        assert hasattr(v4pg, 'calcular_metricas_roi'), "calcular_metricas_roi not imported"
        assert hasattr(v4pg, 'formatear_roi_para_propuesta'), "formatear_roi_para_propuesta not imported"


class TestROIFormatterPrecision:
    """T2: Verificar formato :.2f en calcular_metricas_roi + formatear."""

    def test_calcular_metricas_roi_rounds_2_decimals(self):
        """calcular_metricas_roi redondea roi_saas a 2 decimales."""
        # 100 / 30 = 3.333... -> round to 3.33
        metrics = calcular_metricas_roi(
            recuperacion_total=100.0,
            inversion_opex=30.0,
            inversion_capex=0.0,
        )
        assert metrics.roi_saas == pytest.approx(3.33, abs=0.005), (
            f"Expected roi_saas ~3.33, got {metrics.roi_saas}"
        )

    def test_formatear_roi_usa_2f(self):
        """formatear_roi_para_propuesta produce roi_saas con .2f."""
        metrics = calcular_metricas_roi(
            recuperacion_total=105.0,
            inversion_opex=100.0,
            inversion_capex=10.0,
        )
        result = formatear_roi_para_propuesta(metrics)
        assert 'X' in result['roi_saas'], f"Expected 'X' suffix, got {result['roi_saas']}"
        # Extract the numeric part: "1.05X" -> check 2 decimal places
        numeric = result['roi_saas'].rstrip('X')
        integer_part, _, decimal_part = numeric.partition('.')
        assert len(decimal_part) == 2, (
            f"Expected 2 decimal places in '{result['roi_saas']}', got {len(decimal_part)}"
        )

    def test_formatear_roi_precision_1_05(self):
        """ROI 1.05 debe mostrarse como 1.05X, no 1.1X."""
        metrics = calcular_metricas_roi(
            recuperacion_total=105.0,
            inversion_opex=100.0,
            inversion_capex=10.0,
        )
        result = formatear_roi_para_propuesta(metrics)
        assert result['roi_saas'] == '1.05X', (
            f"Expected '1.05X', got '{result['roi_saas']}' — :.1f would show 1.1X"
        )


class TestROICap:
    """T5: Verificar que el cap funciona."""

    def test_roi_cap_applied(self):
        """Con roi_cap=5.0, ROI 7.5x debe cap a 5.0."""
        metrics = calcular_metricas_roi(
            recuperacion_total=750.0,
            inversion_opex=100.0,
            inversion_capex=0.0,
            roi_cap=5.0,
        )
        assert metrics.roi_saas == 5.0, (
            f"Expected capped at 5.0, got {metrics.roi_saas}"
        )

    def test_roi_no_cap_when_below(self):
        """Sin cap, ROI 3.5x debe mantenerse."""
        metrics = calcular_metricas_roi(
            recuperacion_total=350.0,
            inversion_opex=100.0,
            inversion_capex=0.0,
            roi_cap=5.0,
        )
        assert metrics.roi_saas == 3.5, (
            f"Expected 3.5, got {metrics.roi_saas}"
        )

    def test_roi_no_cap_when_none(self):
        """roi_cap=None no debe aplicar cap."""
        metrics = calcular_metricas_roi(
            recuperacion_total=1000.0,
            inversion_opex=100.0,
            inversion_capex=0.0,
            roi_cap=None,
        )
        assert metrics.roi_saas == 10.0, (
            f"Expected 10.0 with cap=None, got {metrics.roi_saas}"
        )


class TestCastillaReal:
    """T4: ROI para Castilla Real debe ser positivo."""

    def test_castilla_real_roi_positive(self):
        """Parámetros típicos de Castilla Real deben producir roi_saas > 0."""
        # Castilla Real: ~$3.7M/mes fee, ~$1.5M/mes recuperacion, 6 meses
        metrics = calcular_metricas_roi(
            recuperacion_total=9_164_160.0,  # ~$1.5M * 6
            inversion_opex=22_446_000.0,      # ~$3.74M * 6
            inversion_capex=3_500_000.0,      # setup fee
            meses_proyeccion=6,
        )
        assert metrics.roi_saas > 0, (
            f"Expected roi_saas > 0 for Castilla Real, got {metrics.roi_saas}"
        )
        # Should be around 0.41X based on known Castilla Real numbers
        assert 0.30 <= metrics.roi_saas <= 0.60, (
            f"Expected roi_saas in [0.30, 0.60] range, got {metrics.roi_saas}"
        )


class TestSingleROIMotor:
    """T3: Solo un motor de ROI."""

    def test_single_roi_engine(self):
        """Verifica que calcular_metricas_roi es el unico motor (no dupes)."""
        import modules.financial_engine.roi_formatter as rf
        # Count public functions related to ROI calculation
        funcs = [name for name, obj in inspect.getmembers(rf, inspect.isfunction)
                 if 'roi' in name.lower() and not name.startswith('_')]
        # Should have exactly calcular_metricas_roi and formatear_roi_para_propuesta
        assert 'calcular_metricas_roi' in funcs
        assert 'formatear_roi_para_propuesta' in funcs
        # No other public ROI functions
        assert len(funcs) == 2, f"Expected 2 public ROI functions, got {len(funcs)}: {funcs}"
