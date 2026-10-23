"""FASE-B (CURA-DEUDAS-PRODUCTO-Y-CONTRATO-TIER-2026-10-22) — AC1: contrato
plantilla↔tier para los 2 claims de totalidad del revisor.

Los 2 claims emitidos por el baseline («Protección total para usted» y
«Transparencia total») solo se emiten con tier A; con tier no-A sale la variante
honesta. La propuesta usa `{{if financial_evidence_tier ==/!= "A"}}` sobre
`_preprocess_conditionals`; el diagnóstico recibe el mismo contrato con los
strings precomputados `garantias_titulo`/`garantias_cuerpo`
(`_build_financial_placeholders`).

Los tests de sobre-presentación invocan el revisor REAL
(`HonestyReviewer.review` / `coincidencias_lenguaje_de_verificacion` /
`_scan_sobre_presentacion`) sobre el texto renderizado; no buscan strings
sueltos para juzgarla. Las afirmaciones de copy (qué variante se emite, labels
financieros intactos) son de contenido y así queda declarado.

Ruta de render de la propuesta: `_render_template` (la misma entrada que usa
`generate()` después de ensamblar datos). `generate()` completo de la propuesta
está excluido de la suite (conftest PATHOLOGICAL_FILES: fuga de RAM en
`_prepare_template_data`), y el plan autoriza la ruta de render de plantilla.

Mutación (R2.8): la condición del render desactivada —el A-bloque siempre
visible— hace que el revisor vuelva a emitir los 2 claims (par rojo/verde en
`evidence/CURA-DEUDAS-PRODUCTO-Y-CONTRATO-TIER-2026-10-22/FASE-B/`).
"""

import json
from pathlib import Path

import pytest

from modules.commercial_documents.data_structures import (
    FinancialBreakdown,
    FinancialScenarios,
    Scenario,
)
from modules.commercial_documents.v4_diagnostic_generator import V4DiagnosticGenerator
from modules.commercial_documents.v4_proposal_generator import V4ProposalGenerator
from modules.quality_gates.tribunal.evidence_tier import resolve_evidence_tier
from modules.quality_gates.tribunal.honesty_reviewer import (
    FINDING_OVER_PRESENTATION,
    HonestyReviewer,
    coincidencias_lenguaje_de_verificacion,
)
from modules.quality_gates.tribunal.llm_extractor import MockPromiseExtractor

REPO = Path(__file__).resolve().parents[2]
TPL_PROPUESTA = (
    REPO / "modules/commercial_documents/templates/propuesta_v6_template.md"
)

# Los 2 claims de totalidad (variantes por tier) y sus frases exactas.
CLAIM_1_A = "Protección total para usted"
CLAIM_1_HONESTA = "Protección para usted"
CLAIM_2_A = "Transparencia total"
CLAIM_2_HONESTA = "Transparencia en cada cifra"

# Labels financieros que NO se tocan (grep de 7 líneas = 2 claims + 5 no-to-camar).
LABELS_FINANCIEROS = (
    "fuga total estimada",
    "**Total recuperación proyectada",
    "**100% suyo**",
    "| Fee mensual (×6) | **OPEX** | $7.200.000 COP |",
    "### 2. Resultados garantizados",
)

# Datos de render con montos reales (el filtro estructural del revisor juzga
# filas de tabla y líneas con monto con la forma real del texto renderizado).
DATOS_FINANCIEROS = {
    "fuga_total_6m": "$21.067.200 COP",
    "total_recuperacion_6m": "$4.731.342 COP",
    "capex_total": "$2.500.000 COP",
    "opex_total_6m": "$7.200.000 COP",
}


def renderizar_propuesta(tier: str) -> str:
    """Render real de la plantilla de propuesta con el tier dado (B+, A, …)."""
    data = {
        "financial_evidence_tier": tier,
        "has_onboarding": "True",
        "testimonials_present": "false",
        **DATOS_FINANCIEROS,
    }
    generador = V4ProposalGenerator()
    return generador._render_template(TPL_PROPUESTA.read_text(encoding="utf-8"), data)


def _scenarios_minimos() -> FinancialScenarios:
    def escenario(central: int, prob: float, descripcion: str) -> Scenario:
        return Scenario(
            monthly_loss_min=int(central * 0.8),
            monthly_loss_max=int(central * 1.2),
            probability=prob,
            description=descripcion,
            monthly_loss_central=central,
        )

    return FinancialScenarios(
        conservative=escenario(3_200_000, 0.7, "Conservador"),
        realistic=escenario(2_610_000, 0.2, "Realista"),
        optimistic=escenario(2_100_000, 0.1, "Optimista"),
    )


def _breakdown(tier: str) -> FinancialBreakdown:
    return FinancialBreakdown(
        monthly_ota_commission_cop=5_400_000,
        ota_commission_basis="onboarding",
        ota_commission_source="onboarding",
        shift_savings_cop=540_000,
        shift_percentage=0.10,
        shift_source="benchmark",
        ia_revenue_cop=2_250_000,
        ia_boost_percentage=0.05,
        ia_source="estimado",
        evidence_tier=tier,
        disclaimer="Datos operativos verificados de su hotel (test FASE-B).",
    )


def claims_del_diagnostico(tier: str) -> tuple[str, str]:
    """Strings precomputados REALES del diagnóstico para el tier dado."""
    generador = V4DiagnosticGenerator()
    placeholders = generador._build_financial_placeholders(
        _scenarios_minimos(), financial_breakdown=_breakdown(tier)
    )
    return placeholders["garantias_titulo"], placeholders["garantias_cuerpo"]


def montar_run(tmp_path: Path, propuesta: str, diagnostico: str, tier: str):
    """Run real (v4_audit + deliveries) como lo deja el pipeline, con ambos renders."""
    v4_audit = tmp_path / "v4_complete" / "hotelx" / "v4_audit"
    v4_audit.mkdir(parents=True)
    deliveries = tmp_path / "v4_complete" / "deliveries"
    deliveries.mkdir(parents=True)

    (v4_audit / "financial_scenarios_20261023.json").write_text(
        json.dumps(
            {"scenarios": {"conservative": 1, "realistic": 2, "optimistic": 3},
             "breakdown": {"evidence_tier": tier}}
        ),
        encoding="utf-8",
    )
    (v4_audit / "02_PROPUESTA_COMERCIAL_20261023.md").write_text(
        propuesta, encoding="utf-8"
    )
    (v4_audit / "01_DIAGNOSTICO_Y_OPORTUNIDAD_20261023.md").write_text(
        diagnostico, encoding="utf-8"
    )
    (v4_audit / "commercial_gates_report.json").write_text(
        json.dumps({"results": []}), encoding="utf-8"
    )
    return v4_audit, deliveries


def revisar(v4_audit: Path, deliveries: Path) -> dict:
    return HonestyReviewer(v4_audit, deliveries).review(
        extractor=MockPromiseExtractor([])
    )


def resolucion(tier: str):
    return resolve_evidence_tier(
        {"breakdown": {"evidence_tier": tier}},
        None,
        scenarios_name="financial_scenarios_20261023.json",
    )


def diagnostico_render(tier: str) -> str:
    """Región de claims del diagnóstico tal como la renderiza el contrato."""
    titulo, cuerpo = claims_del_diagnostico(tier)
    return f"## {titulo}\n\n{cuerpo}\n"


# ── AC1: diente con el revisor real ─────────────────────────────────────


def test_render_bplus_summary_over_presentations_cero(tmp_path):
    """AC1: propuesta y diagnóstico renderizados con B+ → 0 emisiones del revisor."""
    propuesta = renderizar_propuesta("B+")
    diagnostico = diagnostico_render("B+")
    v4_audit, deliveries = montar_run(tmp_path, propuesta, diagnostico, "B+")

    reporte = revisar(v4_audit, deliveries)

    assert reporte["summary"]["over_presentations"] == 0
    emitidos = [
        f for f in reporte["findings"]
        if f.get("finding_type") == FINDING_OVER_PRESENTATION
    ]
    assert emitidos == []


def test_render_a_variante_respaldada_escaner_apagado_por_diseno():
    """AC1: con tier A se emite la variante respaldada y el escáner no emite (diseño)."""
    propuesta = renderizar_propuesta("A")
    assert CLAIM_1_A in propuesta and CLAIM_2_A in propuesta
    assert CLAIM_1_HONESTA not in propuesta and CLAIM_2_HONESTA not in propuesta

    # El escáner real del revisor está apagado por diseño con tier A declarado.
    escaner = HonestyReviewer(Path("."), Path("."))
    assert escaner._scan_sobre_presentacion(propuesta, resolucion("A")) == []

    # Los strings de claims del diagnóstico con tier A son la variante respaldada.
    titulo, cuerpo = claims_del_diagnostico("A")
    assert CLAIM_1_A in titulo and CLAIM_2_A in cuerpo
    assert coincidencias_lenguaje_de_verificacion(f"{titulo}\n{cuerpo}\n")


def test_render_bplus_variantes_honestas_en_ambos_documentos():
    """Los 2 claims emiten su variante honesta en propuesta y diagnóstico con B+."""
    propuesta = renderizar_propuesta("B+")
    assert CLAIM_1_HONESTA in propuesta and CLAIM_2_HONESTA in propuesta
    assert CLAIM_1_A not in propuesta and CLAIM_2_A not in propuesta

    titulo, cuerpo = claims_del_diagnostico("B+")
    assert CLAIM_1_HONESTA in titulo and CLAIM_2_HONESTA in cuerpo
    assert CLAIM_1_A not in titulo and CLAIM_2_A not in cuerpo

    # Contrato con diente: los strings de claims B+ pasan el escáner real del revisor.
    assert coincidencias_lenguaje_de_verificacion(f"{titulo}\n{cuerpo}\n") == []


def test_labels_financieros_intactos():
    """Los labels financieros «no tocar» siguen renderizados sin cambios."""
    propuesta = renderizar_propuesta("B+")
    for label in LABELS_FINANCIEROS:
        assert label in propuesta, f"label financiero perdido: {label}"
    # El label del diagnóstico también sobrevive (contenido de plantilla estático).
    diagnostico = V4DiagnosticGenerator()._render_template(
        (REPO / "modules/commercial_documents/templates/diagnostico_v6_template.md")
        .read_text(encoding="utf-8"),
        {"garantias_titulo": claims_del_diagnostico("B+")[0],
         "garantias_cuerpo": claims_del_diagnostico("B+")[1],
         "fuga_total_6m": "$21.067.200 COP",
         "recuperacion_proyectada_6m": "$4.731.342 COP"},
    )
    assert "Fuga total estimada" in diagnostico


# ── R2.8: mutación — la condición desactivada vuelve a emitir los 2 claims ──


def test_mutante_condicion_desactivada_reemite_los_2_claims(tmp_path, monkeypatch):
    """Par rojo: con la condición del render desactivada el revisor emite 2 claims."""
    original = V4ProposalGenerator._preprocess_conditionals

    def mutante(self, template_content, data):
        # Condición desactivada hacia la totalidad: el tier "no manda".
        datos = dict(data)
        datos["financial_evidence_tier"] = "A"
        return original(self, template_content, datos)

    monkeypatch.setattr(V4ProposalGenerator, "_preprocess_conditionals", mutante)

    propuesta = renderizar_propuesta("B+")
    v4_audit, deliveries = montar_run(
        tmp_path, propuesta, diagnostico_render("B+"), "B+"
    )
    reporte = revisar(v4_audit, deliveries)

    # El revisor real vuelve a emitir exactamente los 2 claims (rojo del mutante).
    assert reporte["summary"]["over_presentations"] == 2
    lineas = {
        f["matched_line"]
        for f in reporte["findings"]
        if f.get("finding_type") == FINDING_OVER_PRESENTATION
    }
    assert any("GARANTÍAS" in linea for linea in lineas)
    assert any("Transparencia" in linea for linea in lineas)


def test_mutante_strings_diagnostico_forzados_a_reemite_claims(monkeypatch):
    """Par rojo (diagnóstico): strings forzados a la variante A en tier B+."""
    original = V4DiagnosticGenerator._build_financial_placeholders

    def mutante(self, *args, **kwargs):
        datos = original(self, *args, **kwargs)
        datos["garantias_titulo"] = f"🛡️ GARANTÍAS: {CLAIM_1_A}"
        datos["garantias_cuerpo"] = (
            f"**{CLAIM_2_A}**: reporte mensual con métricas reales de su hotel."
        )
        return datos

    monkeypatch.setattr(V4DiagnosticGenerator, "_build_financial_placeholders", mutante)

    titulo, cuerpo = claims_del_diagnostico("B+")
    hallazgos = coincidencias_lenguaje_de_verificacion(f"{titulo}\n{cuerpo}\n")

    assert any(h["literal"].lower() == "total" for h in hallazgos)


# ── Tarea 4: contrato del preprocesador (== sigue intacto; != nuevo) ──────


def test_preprocesador_igualdad_sigue_intacto():
    generador = V4ProposalGenerator()
    plantilla = 'A{{if financial_evidence_tier == "A"}}-total{{endif}}B'
    assert generador._preprocess_conditionals(plantilla, {"financial_evidence_tier": "A"}) == "A-totalB"
    assert generador._preprocess_conditionals(plantilla, {"financial_evidence_tier": "B+"}) == "AB"


def test_preprocesador_desigualdad_emite_variante_honesta_sin_tier():
    generador = V4ProposalGenerator()
    plantilla = 'A{{if financial_evidence_tier != "A"}}-honesta{{endif}}B'
    # Sin tier declarado la variante honesta es la única posible (fail-safe).
    assert generador._preprocess_conditionals(plantilla, {}) == "A-honestaB"
    assert generador._preprocess_conditionals(plantilla, {"financial_evidence_tier": "A"}) == "AB"
