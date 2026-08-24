"""Tests recovery FASE-R0-E: FinancialFactors ausente en run_v4_complete_mode.

El commit 3e88251 (2026-08-21, "FIX V6") reemplazó `ota_commission_rate=0.15`
por `FinancialFactors().get_comision_ota()['base']` en el bloque FASE-K de
main.py SIN agregar el import en el scope de `run_v4_complete_mode`. El
NameError era atrapado por el except del bloque → `financial_breakdown=None`
→ `AssessmentBuilder.with_financial` inyectaba tier default "C" → gate
`tier_c_onboarding_required` BLOCKED falso → eliminación de documentos
comerciales (detectado en corrida E2E de FASE-R0-E, lección L-NC8).

Fix: `from modules.utils.financial_factors import FinancialFactors` agregado
al bloque de imports de `run_v4_complete_mode`.
"""

import ast
from pathlib import Path

from modules.assessment_builder import AssessmentBuilder
from modules.financial_engine.scenario_calculator import (
    HotelFinancialData,
    ScenarioCalculator,
)
from modules.utils.financial_factors import FinancialFactors

MAIN_PY = Path(__file__).resolve().parent.parent.parent / "main.py"

# Datos reales de onboarding Zi One Luxury (Tier A, 4 campos confirmados)
ZIONE_ROOMS = 34
ZIONE_ADR = 290000
ZIONE_OCCUPANCY = 0.7843137254901961
ZIONE_DIRECT_PCT = 0.4


class TestR0ERecoveryStaticContract:
    """Contrato estático: run_v4_complete_mode importa FinancialFactors."""

    def test_import_financial_factors_present_in_v4complete(self):
        """El scope de run_v4_complete_mode debe importar FinancialFactors."""
        tree = ast.parse(MAIN_PY.read_text(encoding="utf-8"))
        func = next(
            (
                node
                for node in ast.walk(tree)
                if isinstance(node, ast.FunctionDef)
                and node.name == "run_v4_complete_mode"
            ),
            None,
        )
        assert func is not None, "run_v4_complete_mode no encontrada en main.py"
        imports = [
            n
            for n in ast.walk(func)
            if isinstance(n, ast.ImportFrom)
            and n.module == "modules.utils.financial_factors"
            and any(a.name == "FinancialFactors" for a in n.names)
        ]
        assert imports, (
            "run_v4_complete_mode debe importar FinancialFactors desde "
            "modules.utils.financial_factors (fix recovery FASE-R0-E)"
        )

    def test_import_precedes_fase_k_usage(self):
        """El import debe aparecer ANTES del uso en el bloque FASE-K."""
        tree = ast.parse(MAIN_PY.read_text(encoding="utf-8"))
        func = next(
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
            and node.name == "run_v4_complete_mode"
        )
        import_line = None
        usage_line = None
        for node in ast.walk(func):
            if (
                isinstance(node, ast.ImportFrom)
                and node.module == "modules.utils.financial_factors"
                and any(a.name == "FinancialFactors" for a in node.names)
            ):
                import_line = node.lineno
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id == "FinancialFactors":
                    usage_line = node.lineno
        assert import_line is not None, "Import de FinancialFactors ausente"
        assert usage_line is not None, "Uso de FinancialFactors no encontrado"
        assert import_line < usage_line, (
            f"Import (L{import_line}) debe preceder al uso (L{usage_line})"
        )


class TestR0ERecoveryFaseKBehavior:
    """El bloque FASE-K (reproducido) construye el breakdown sin excepción."""

    def test_breakdown_construction_with_config_commission(self):
        """La construcción exacta del bloque FASE-K no lanza NameError ni otra excepción."""
        sc = ScenarioCalculator()
        hotel_fin_data = HotelFinancialData(
            rooms=ZIONE_ROOMS,
            adr_cop=ZIONE_ADR,
            occupancy_rate=ZIONE_OCCUPANCY,
            direct_channel_percentage=ZIONE_DIRECT_PCT,
            ota_commission_rate=FinancialFactors().get_comision_ota()["base"],
            adr_source="onboarding",
            occupancy_source="onboarding",
            channel_source="onboarding",
            ga4_enabled=False,
            gsc_enabled=False,
        )
        breakdown = sc.calculate_breakdown(hotel_fin_data)
        assert breakdown is not None

    def test_zione_evidence_tier_matches_baseline(self):
        """Zione (onboarding Tier A) debe producir tier B+ (idéntico al baseline)."""
        sc = ScenarioCalculator()
        hotel_fin_data = HotelFinancialData(
            rooms=ZIONE_ROOMS,
            adr_cop=ZIONE_ADR,
            occupancy_rate=ZIONE_OCCUPANCY,
            direct_channel_percentage=ZIONE_DIRECT_PCT,
            ota_commission_rate=FinancialFactors().get_comision_ota()["base"],
            adr_source="onboarding",
            occupancy_source="onboarding",
            channel_source="onboarding",
            ga4_enabled=False,
            gsc_enabled=False,
        )
        breakdown = sc.calculate_breakdown(hotel_fin_data)
        assert breakdown.evidence_tier == "B+", (
            f"Tier esperado B+ (baseline 20260821), obtenido {breakdown.evidence_tier}"
        )


class TestR0ERecoveryAssessmentTierChain:
    """Cadena completa: breakdown → assessment dict → gate no bloqueado."""

    def _build_breakdown(self):
        sc = ScenarioCalculator()
        hotel_fin_data = HotelFinancialData(
            rooms=ZIONE_ROOMS,
            adr_cop=ZIONE_ADR,
            occupancy_rate=ZIONE_OCCUPANCY,
            direct_channel_percentage=ZIONE_DIRECT_PCT,
            ota_commission_rate=FinancialFactors().get_comision_ota()["base"],
            adr_source="onboarding",
            occupancy_source="onboarding",
            channel_source="onboarding",
            ga4_enabled=False,
            gsc_enabled=False,
        )
        return sc.calculate_breakdown(hotel_fin_data)

    def test_assessment_tier_not_default_c_with_breakdown(self):
        """Con breakdown real, el assessment NO recibe el tier default 'C'."""
        builder = AssessmentBuilder()
        builder.with_core("https://zione.co/", "Zi One Luxury")
        builder.with_financial(
            ZIONE_ROOMS,
            ZIONE_ADR,
            ZIONE_OCCUPANCY,
            ZIONE_DIRECT_PCT,
            {"adr_cop": "onboarding"},
            self._build_breakdown(),
        )
        assessment = builder.build()
        assert assessment["financial_evidence_tier"] == "B+"

    def test_tier_c_gate_passes_with_real_tier(self):
        """El gate tier_c_onboarding_required PASA con tier real B+."""
        from modules.quality_gates.publication_gates import (
            PublicationGateConfig,
            PublicationGatesOrchestrator,
        )

        builder = AssessmentBuilder()
        builder.with_core("https://zione.co/", "Zi One Luxury")
        builder.with_financial(
            ZIONE_ROOMS,
            ZIONE_ADR,
            ZIONE_OCCUPANCY,
            ZIONE_DIRECT_PCT,
            {"adr_cop": "onboarding"},
            self._build_breakdown(),
        )
        assessment = builder.build()
        gates = PublicationGatesOrchestrator(PublicationGateConfig())
        result = gates._tier_c_onboarding_gate(assessment)
        assert result.passed, (
            f"Gate tier_c debe PASAR con tier B+; status={result.status}, "
            f"message={result.message}"
        )
