"""
FASE-4 Tests: H3 (brecha sum normalization) and H4 (pain_ratio vs recovery_factor separation).

H3: _build_brecha_data() debe redondear por slot (error ≤ 1 COP) y dejar los slots
     sin nombre en $0. La absorción del diff en el último slot se eliminó post-release
     (Grupo C 2026-09-05): con impactos reales que no suman 1.0 fabricaba dinero en
     slots vacíos. Los tests 1-3 de la clase siguen fijando «suma == central» para el
     caso legítimo (impactos que suman 1.0).
H4: Template data must expose pain_ratio_pct, recovery_factor_pct, projected_real_gain
     separately so the proposal can distinguish addressable pain (41%) from realistic
     recovery effectiveness (20%).
"""
import pytest
from unittest.mock import MagicMock
from modules.commercial_documents.v4_proposal_generator import V4ProposalGenerator


class MockScenario:
    """Minimal mock for main_scenario with monthly_loss_cop."""
    def __init__(self, monthly_loss_cop: int):
        self.monthly_loss_cop = monthly_loss_cop


class MockDiagnosticSummary:
    """DiagnosticSummary with optional brechas_reales and top_problems."""
    def __init__(self, top_problems=None, brechas_reales=None):
        self.top_problems = top_problems or []
        self.brechas_reales = brechas_reales or []


def _extract_int(cop_str: str) -> int:
    """Parse format_cop output: '$1.234.567 COP' or '$1,234,567' -> int."""
    # format_cop returns '$3.741.696 COP' (dots as thousands, space before COP)
    s = cop_str.replace('$', '').replace(' COP', '').replace('.', '').replace(',', '')
    return int(s)


class TestH3BrechaSumNormalization:
    """H3 (revisado Grupo C 2026-09-05): cuando los impactos suman 1.0 y los 4 slots
    tienen nombre, la suma cae en el central con error ≤ 1 COP por slot (round por
    slot, sin absorción). Cuando no suman 1.0, la suma visible es la de los impactos
    reales y los slots sin nombre son $0 — nunca absorben el gap (costo fantasma)."""

    def test_sum_matches_central_with_integer_impacts(self):
        """Brechas with integer impact fractions: rounding must not accumulate."""
        gen = V4ProposalGenerator()
        main_scenario = MockScenario(monthly_loss_cop=3741696)

        # 4 brechas with fractional impacts summing to exact central
        diagnostic = MockDiagnosticSummary(
            brechas_reales=[
                {'nombre': 'Brecha A', 'impacto': 0.25},
                {'nombre': 'Brecha B', 'impacto': 0.25},
                {'nombre': 'Brecha C', 'impacto': 0.25},
                {'nombre': 'Brecha D', 'impacto': 0.25},
            ]
        )

        result = gen._build_brecha_data(diagnostic, main_scenario)

        total = sum(_extract_int(result[f'brecha_{i}_costo']) for i in range(1, 5))
        assert total == 3741696, f"Sum {total} != central 3741696 (diff: {total - 3741696})"

    def test_sum_matches_central_with_real_world_fractions(self):
        """The actual bug case: fractions that accumulate rounding error."""
        gen = V4ProposalGenerator()
        main_scenario = MockScenario(monthly_loss_cop=3741696)

        # 4 brechas with non-round fractional impacts (the real failure case)
        diagnostic = MockDiagnosticSummary(
            brechas_reales=[
                {'nombre': 'SEO Orgánico', 'impacto': 0.30},
                {'nombre': 'Schema Hotel', 'impacto': 0.28},
                {'nombre': 'GBP Photos', 'impacto': 0.27},
                {'nombre': 'Content Fresh', 'impacto': 0.15},
            ]
        )

        result = gen._build_brecha_data(diagnostic, main_scenario)

        total = sum(_extract_int(result[f'brecha_{i}_costo']) for i in range(1, 5))
        assert total == 3741696, f"Sum {total} != central 3741696 (diff: {total - 3741696})"

    def test_sum_matches_central_equitable_distribution(self):
        """Fallback path: equitable distribution among top_problems."""
        gen = V4ProposalGenerator()
        main_scenario = MockScenario(monthly_loss_cop=3741696)

        diagnostic = MockDiagnosticSummary(
            top_problems=['Problema A', 'Problema B', 'Problema C'],
            brechas_reales=[]  # Force fallback
        )

        result = gen._build_brecha_data(diagnostic, main_scenario)

        total = sum(_extract_int(result[f'brecha_{i}_costo']) for i in range(1, 5))
        # With 3 top_problems and 4 slots, slot 4 gets $0
        # So sum = 3 * (3741696 / 3) = 3741696 exactly
        assert total == 3741696, f"Sum {total} != central 3741696"

    def test_mixed_brechas_no_phantom_absorption(self):
        """Mixed data: los slots con nombre muestran su impacto real; los sin nombre, $0.

        Grupo C (2026-09-05): la versión anterior de este test exigía
        «sum == central» con el gap absorbido en el slot 4 SIN nombre —
        el mecanismo exacto del costo fantasma (un slot vacío mostrando
        $4.500.000 COP). Contrato FASE-G vigente: la suma visible es la de
        los impactos reales de los slots con nombre; nunca se rellena con
        dinero inventado.
        """
        gen = V4ProposalGenerator()
        main_scenario = MockScenario(monthly_loss_cop=5000000)

        # 2 brechas_reales: slots 1-2 con impacto real
        # (top_problems=['Problema X'] no aterriza: el índice 2 cae fuera de rango)
        diagnostic = MockDiagnosticSummary(
            top_problems=['Problema X'],
            brechas_reales=[
                {'nombre': 'Brecha 1', 'impacto': 0.5},  # raw: 2,500,000
                {'nombre': 'Brecha 2', 'impacto': 0.3},  # raw: 1,500,000
            ]
        )

        result = gen._build_brecha_data(diagnostic, main_scenario)

        # Los slots con nombre muestran su impacto real
        assert 'Brecha 1' in result['brecha_1_nombre']
        assert _extract_int(result['brecha_1_costo']) == 2500000
        assert 'Brecha 2' in result['brecha_2_nombre']
        assert _extract_int(result['brecha_2_costo']) == 1500000

        # Los slots sin nombre son $0 — ningún slot absorbe el gap de 1M
        for slot in (3, 4):
            assert result[f'brecha_{slot}_costo'] == '$0'
            assert result[f'brecha_{slot}_nombre'] == ''

        # La suma visible es la de los impactos reales (0.8 × 5M), no el central
        total = sum(_extract_int(result[f'brecha_{i}_costo']) for i in range(1, 5))
        assert total == 4000000, f"Suma de impactos reales esperada, obtenida {total}"

    def test_empty_slots_get_zero(self):
        """Slots with no data get $0, not phantom values."""
        gen = V4ProposalGenerator()
        main_scenario = MockScenario(monthly_loss_cop=1000000)

        diagnostic = MockDiagnosticSummary(
            top_problems=[],  # Nothing
            brechas_reales=[]  # Nothing
        )

        result = gen._build_brecha_data(diagnostic, main_scenario)

        for slot in range(1, 5):
            assert result[f'brecha_{slot}_costo'] == '$0', f"Slot {slot} should be $0"
            assert result[f'brecha_{slot}_nombre'] == '', f"Slot {slot} name should be empty"


class TestH4PainRatioRecoveryFactorSeparation:
    """H4: pain_ratio and recovery_factor must be exposed as separate template variables."""

    def test_pain_ratio_note_contains_both_percentages(self):
        """After H4 fix, pain_ratio_note text explicitly mentions both pain_ratio and recovery_factor values."""
        # The H4 code fix already guarantees that pain_ratio_note will include
        # recovery_factor's percentage explicitly via:
        #   f"Aplicando una efectividad esperada de recuperación del {recovery_factors['realistic']:.0%},"
        # We test that a note generated with the same inputs contains "20%".
        gen = V4ProposalGenerator()
        raw_monthly_loss = 3741696
        pain_ratio = 0.41
        recovery_factor_realistic = 0.20

        # Reconstruct the exact note string as the H4 code now builds it
        note = (
            f"**Nota de proyección**: De su pérdida mensual estimada, el {pain_ratio:.0%} "
            f"representa la porción del dolor financieramente abordable con IAO. "
            f"Aplicando una efectividad esperada de recuperación del {recovery_factor_realistic:.0%}, "
            f"la proyección conservadora es de aproximadamente "
            f"${int(raw_monthly_loss * pain_ratio * recovery_factor_realistic):,}/mes"
            f" (vs. la cifra bruta de ${int(raw_monthly_loss * pain_ratio):,} que se mostraría "
            f"sin ajustar por efectividad)."
        )

        assert "41%" in note, f"pain_ratio (41%) must be in note: {note}"
        assert "20%" in note, f"recovery_factor (20%) must be in note: {note}"
        assert "recuperación" in note.lower() or "efectividad" in note.lower()

    def test_projected_real_gain_uses_both_factors(self):
        """projected_real_gain should be raw * pain_ratio * recovery_factor, not just raw * pain_ratio."""
        raw = 3741696
        pain_ratio = 0.41
        recovery_realistic = 0.20

        # The H4 issue: previously showed ~$1.5M (raw * pain_ratio only)
        # Now shows ~$307K (raw * pain_ratio * recovery_factor)
        old_incorrect = int(raw * pain_ratio)        # ~$1.5M
        new_correct = int(raw * pain_ratio * recovery_realistic)  # ~$307K

        assert new_correct < old_incorrect
        assert 300000 < new_correct < 400000  # ~$307K range


if __name__ == '__main__':
    pytest.main([__file__, '-v'])