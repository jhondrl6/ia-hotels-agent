"""FASE-C2 (AC19) — un CRITICAL verificado no pierde fuerza por el estado del insumo.

Plan CURA-COSTURA-TRIBUNAL-2026-10-11. La fila 2 de la matriz §2.1 exigía
``status.is_ok`` para que un hallazgo CRITICAL (o la recomendación ``BLOQUEAR``)
bloquera el ZIP. El escaneo de texto completo que produce ese hallazgo **no
depende del LLM** (N5), así que condicionar su enforcement a la salud del insumo
no protege nada: el gate se aflojaba justo cuando el proveedor falla.

L-T4A.5: cada test lleva datos que **alcanzan** la rama que certifica, leídos por
``collect_reviewer_reports`` desde un JSON escrito en disco, no desde un DTO
construido a mano. L-CST-5: el par rojo/verde es un diferencial de estado (mismo
hallazgo, solo cambia el estado del insumo) y cada mutante declara qué diente no
puede detectar.

Lo que NO se cura aquí (declarado): la fila 3 (``verified_return_for_tests``)
conserva su exigencia ``is_ok`` — extenderla haría la entrega del run único
sensible a un fallo transitorio del proveedor.
"""

import json
from pathlib import Path

import pytest

from modules.quality_gates.tribunal.acta_writer import ActaWriter
from modules.quality_gates.tribunal.honesty_reviewer import (
    ARTIFACTO_PROPUESTA,
    FINDING_OVER_PRESENTATION,
    HonestyReviewer,
)
from modules.quality_gates.tribunal.judge import (
    VERDICT_BLOCKED,
    TribunalJudge,
    blocks_delivery_zip,
)
from modules.quality_gates.tribunal.llm_extractor import (
    ExtractionOutcome,
    ExtractionState,
    MockPromiseExtractor,
)
from modules.quality_gates.tribunal.outcome import (
    ReviewerReport,
    ReviewerStatus,
    collect_reviewer_reports,
)

ACCION_GENERICA = "VEREDICTO_BLOQUEANTE_SIN_HALLAZGO"

PROPUESTA_CON_CITA_OMITIDA = """# Propuesta Comercial

## Introduccion
Ofrecemos soluciones verificadas para su hotel.

## Alcance
Publicamos datos confirmados del mercado en su ficha.
"""

# Sin lenguaje de verificacion: bajo extraccion no-OK el unico hallazgo de Bot 4 es el
# estado no-evaluable del check, que es WARNING a proposito (AC11). Es el par del
# diferencial de no-sobre-bloqueo: mismo revisor, mismo estado de insumo, solo cambia
# la severidad.
PROPUESTA_SIN_LENGUAJE = """# Propuesta Comercial

## Introduccion
Le proponemos un boton de WhatsApp para reservas directas.
"""


class ExtractoraConEstado:
    """Extractor que devuelve el ExtractionOutcome que el test pida, sin LLM."""

    def __init__(self, outcome):
        self.outcome = outcome

    def extract_checked(self, proposal_text: str) -> ExtractionOutcome:
        return self.outcome


def no_evaluable(motivo="respuesta ilegible: el texto no decodifica como JSON"):
    return ExtractoraConEstado(
        ExtractionOutcome(state=ExtractionState.NO_EVALUABLE, reason=motivo)
    )


def fallido(motivo="proveedor falló: ConnectionError: sin salida"):
    return ExtractoraConEstado(
        ExtractionOutcome(state=ExtractionState.FALLIDO, reason=motivo)
    )


def _directorio(base: Path, propuesta: str, tier="B") -> Path:
    """v4_audit con los insumos minimos que leen Bot 4 y el Juez.

    ``tier=None`` deja el run sin artefacto que declare el piso: el check de
    sobre-presentacion pasa a publicar su estado no-evaluable (WARNING).
    """
    base.mkdir(parents=True, exist_ok=True)
    (base / "02_PROPUESTA_COMERCIAL_20260904_120000.md").write_text(propuesta, encoding="utf-8")
    if tier is not None:
        (base / "financial_scenarios_20260904_120000.json").write_text(
            json.dumps(
                {
                    "scenarios": {"conservative": 100, "realistic": 200, "optimistic": 300},
                    "breakdown": {"evidence_tier": tier},
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
    (base / "commercial_gates_report.json").write_text(
        json.dumps({"results": []}, ensure_ascii=False), encoding="utf-8"
    )
    (base / "proposal_asset_matrix.json").write_text(
        json.dumps({"entries": []}, ensure_ascii=False), encoding="utf-8"
    )
    return base


def _escribir_report(audit: Path, nombre: str, report: dict) -> Path:
    ruta = audit / nombre
    ruta.write_text(json.dumps(report, ensure_ascii=False), encoding="utf-8")
    return ruta


def _bot4_escrito_en_disco(audit: Path, reporte: dict) -> None:
    """Los otros tres Bots no se escriben: quedan NOT_RUN y no aportan bloqueo."""
    _escribir_report(audit, "revision_honestidad.json", reporte)


def _acta_con_bot4(audit: Path, tmp_path: Path, written=None):
    """La rama real: el report lo lee el lector del contrato desde el disco."""
    if written is None:
        written = {"honesty_reviewer": audit / "revision_honestidad.json"}
    reports = collect_reviewer_reports(audit, written=written)
    judge = TribunalJudge(audit, tmp_path / "deliveries", "hotelx")
    acta = judge.enrich(judge.evaluate(), reports)
    return acta, reports, judge


def _bot4(reports):
    return next(r for r in reports if r.reviewer == "honesty_reviewer")


# --- T1: la fila 2 no exige is_ok (predicados y fila 3 intacta) -----------------


@pytest.mark.parametrize(
    "estado",
    [
        ReviewerStatus.OK_WITH_FINDINGS,
        ReviewerStatus.INPUT_NOT_EVALUABLE,
    ],
)
def test_el_critical_bloquea_desde_cualquier_estado_leido(estado):
    """Mismo hallazgo CRITICAL, solo cambia el estado: el predicado no se afloja."""
    report = ReviewerReport(
        reviewer="honesty_reviewer",
        status=estado,
        findings_count=2,
        critical_count=1,
        recommendation="BLOQUEAR",
        report_path="revision_honestidad.json",
        clauses=("P6.5",),
    )

    assert report.verified_critical is True
    assert report.verified_block is True


def test_la_fila_3_conserva_su_exigencia_de_estado():
    """La extension rechazada no se cuela: DEVOLVER-PRUEBAS bajo no-OK no devuelve."""
    no_ok = ReviewerReport(
        reviewer="honesty_reviewer",
        status=ReviewerStatus.INPUT_NOT_EVALUABLE,
        findings_count=1,
        critical_count=1,
        recommendation="DEVOLVER-PRUEBAS",
    )
    ok = ReviewerReport(
        reviewer="honesty_reviewer",
        status=ReviewerStatus.OK_WITH_FINDINGS,
        findings_count=1,
        critical_count=1,
        recommendation="DEVOLVER-PRUEBAS",
    )

    assert ok.verified_return_for_tests is True
    assert no_ok.verified_return_for_tests is False


@pytest.mark.parametrize("vacio", [
    ReviewerStatus.NOT_RUN,
    ReviewerStatus.READER_FAILED,
    ReviewerStatus.ARTIFACT_MISSING,
])
def test_los_tres_estados_vacios_no_inventan_bloqueo(vacio):
    """Ausencia jamas es PASS, pero tampoco fabrica un CRITICAL que no existe."""
    report = ReviewerReport(reviewer="asset_reviewer", status=vacio)

    assert report.critical_count == 0
    assert report.recommendation is None
    assert report.verified_critical is False
    assert report.verified_block is False


# --- T1 sobre la rama real por disco (el diferencial de estado) ------------------


def test_critical_de_texto_completo_bloquea_bajo_extraccion_no_evaluable(tmp_path):
    """Bot 4 emite el CRITICAL por el scan de texto completo con el insumo NO-EVALUABLE."""
    audit = _directorio(tmp_path / "v4_audit", PROPUESTA_CON_CITA_OMITIDA)
    _bot4_escrito_en_disco(audit, HonestyReviewer(audit).review(no_evaluable()))

    acta, reports, _ = _acta_con_bot4(audit, tmp_path)
    bot4 = _bot4(reports)

    assert bot4.extraccion_estado == "NO-EVALUABLE"
    assert bot4.status is ReviewerStatus.INPUT_NOT_EVALUABLE
    assert bot4.critical_count == 2
    assert acta["verdict"] == VERDICT_BLOCKED
    assert blocks_delivery_zip(acta) is True


def test_critical_de_texto_completo_bloquea_bajo_extraccion_fallida(tmp_path):
    """El segundo estado no-OK del proveedor (FALLIDO) cae del mismo lado."""
    audit = _directorio(tmp_path / "v4_audit", PROPUESTA_CON_CITA_OMITIDA)
    _bot4_escrito_en_disco(audit, HonestyReviewer(audit).review(fallido()))

    acta, reports, _ = _acta_con_bot4(audit, tmp_path)
    bot4 = _bot4(reports)

    assert bot4.extraccion_estado == "FALLIDO"
    assert bot4.status is ReviewerStatus.INPUT_NOT_EVALUABLE
    assert bot4.critical_count == 2
    assert acta["verdict"] == VERDICT_BLOCKED
    assert blocks_delivery_zip(acta) is True


def test_el_control_del_diferencial_la_extraccion_ok_bloquea_igual(tmp_path):
    """Unica variable del par anterior: la extraccion pasa a OK y el bloqueo es el mismo."""
    audit = _directorio(tmp_path / "v4_audit", PROPUESTA_CON_CITA_OMITIDA)
    _bot4_escrito_en_disco(audit, HonestyReviewer(audit).review(MockPromiseExtractor([])))

    acta, reports, _ = _acta_con_bot4(audit, tmp_path)
    bot4 = _bot4(reports)

    assert bot4.status is ReviewerStatus.OK_WITH_FINDINGS
    assert bot4.critical_count == 2
    assert acta["verdict"] == VERDICT_BLOCKED
    assert blocks_delivery_zip(acta) is True


# --- T2: la accion correctiva nombra el hallazgo --------------------------------


def test_la_accion_correctiva_nombra_el_hallazgo_bajo_insumo_no_ok(tmp_path):
    """Sin la cura el BLOQUEADO quedaba disfrazado de la accion generica del veredicto."""
    audit = _directorio(tmp_path / "v4_audit", PROPUESTA_CON_CITA_OMITIDA)
    _bot4_escrito_en_disco(audit, HonestyReviewer(audit).review(no_evaluable()))

    acta, reports, judge = _acta_con_bot4(audit, tmp_path)
    outcome = judge.finalize(acta, reports, blocks=blocks_delivery_zip(acta))

    tipos = [a.finding_type for a in outcome.corrective_actions]
    assert FINDING_OVER_PRESENTATION in tipos
    assert ACCION_GENERICA not in tipos
    accion = next(a for a in outcome.corrective_actions if a.finding_type == FINDING_OVER_PRESENTATION)
    assert accion.severity == "CRITICAL"
    assert accion.owner == "comercial"
    assert accion.artifact == ARTIFACTO_PROPUESTA, "AC18: la accion nombra el artefacto del hallazgo"


# --- T3: el acta generada (JSON y MD) cuenta la misma historia ------------------


def test_el_acta_generada_publica_bloqueo_y_la_accion_nombrada(tmp_path):
    audit = _directorio(tmp_path / "v4_audit", PROPUESTA_CON_CITA_OMITIDA)
    _bot4_escrito_en_disco(audit, HonestyReviewer(audit).review(no_evaluable()))

    acta, reports, judge = _acta_con_bot4(audit, tmp_path)
    judge.finalize(acta, reports, blocks=blocks_delivery_zip(acta))
    json_ruta, md_ruta = ActaWriter(tmp_path / "acta").write(acta)

    leido = json.loads(json_ruta.read_text(encoding="utf-8"))
    md = md_ruta.read_text(encoding="utf-8")

    assert leido["verdict"] == VERDICT_BLOCKED
    assert blocks_delivery_zip(leido) is True
    bot4_acta = next(r for r in leido["reviewer_reports"] if r["reviewer"] == "honesty_reviewer")
    assert bot4_acta["status"] == "INPUT_NOT_EVALUABLE"
    assert bot4_acta["critical_count"] == 2
    assert any(a["finding_type"] == FINDING_OVER_PRESENTATION for a in leido["corrective_actions"])
    assert FINDING_OVER_PRESENTATION in md


# --- T3: controles de no-sobre-bloqueo -----------------------------------------


def test_warning_only_bajo_insumo_no_ok_sigue_en_condicional(tmp_path):
    """Un revisor no-OK con solo WARNING no bloquea: la cura no convierte no-OK en castigo.

    El payload se escribe a mano porque el corpus no tiene un insumo real que emita un
    WARNING de Bot 4 sin CRITICAL; aun así lo lee ``collect_reviewer_reports`` desde el
    disco. Su ``verdict_recommendation`` reproduce la regla del propio
    revisor (``HonestyReviewer._compute_verdict``: WARNING sin CRITICAL →
    DEVOLVER-PRUEBAS), así que el control prueba dos cosas a la vez: que AC19 no
    sobre-bloquea y que la fila 3 sigue exigiendo ``is_ok``.
    """
    audit = _directorio(tmp_path / "v4_audit", PROPUESTA_CON_CITA_OMITIDA)
    _bot4_escrito_en_disco(audit, {
        "reviewer": "honesty_reviewer",
        "clause": "P6.5",
        "extraccion": {"estado": "NO-EVALUABLE", "motivo": "proveedor no responde", "via": "extract_checked", "promesas_leidas": 0},
        "findings": [{
            "finding_type": "CG_WARNING_UNDISCLOSED",
            "clause": "P6.5",
            "severity": "WARNING",
            "source_artifact": "02_PROPUESTA_COMERCIAL_20260904_120000.md",
            "description": "CG-WHATSAPP-LEAD no divulgado en la propuesta",
        }],
        "verdict_recommendation": "DEVOLVER-PRUEBAS",
    })

    acta, reports, judge = _acta_con_bot4(audit, tmp_path)
    bot4 = _bot4(reports)
    outcome = judge.finalize(acta, reports, blocks=blocks_delivery_zip(acta))

    assert bot4.status is ReviewerStatus.INPUT_NOT_EVALUABLE
    assert bot4.critical_count == 0
    assert bot4.verified_critical is False
    assert bot4.verified_block is False
    assert bot4.verified_return_for_tests is False, "la fila 3 conserva su exigencia de estado"
    assert acta["verdict"] != VERDICT_BLOCKED
    assert blocks_delivery_zip(acta) is False
    assert [a.finding_type for a in outcome.corrective_actions] == []


def test_insumo_no_ok_real_sin_hallazgos_sigue_en_condicional(tmp_path):
    """La rama real del control: Bot 4 con extraccion no-OK y propuesta sin lenguaje de verificacion.

    El propio revisor deriva ``DEVOLVER-PRUEBAS`` por no poder firmar un insumo que no
    leyó (R2.9), sin ningun CRITICAL: no hay nada que AC19 bloquee.
    """
    audit = _directorio(tmp_path / "v4_audit", PROPUESTA_SIN_LENGUAJE)
    reporte = HonestyReviewer(audit).review(no_evaluable())
    assert all(f["severity"] != "CRITICAL" for f in reporte["findings"])
    _bot4_escrito_en_disco(audit, reporte)

    acta, reports, _ = _acta_con_bot4(audit, tmp_path)
    bot4 = _bot4(reports)

    assert bot4.status is ReviewerStatus.INPUT_NOT_EVALUABLE
    assert bot4.critical_count == 0
    assert acta["verdict"] != VERDICT_BLOCKED
    assert blocks_delivery_zip(acta) is False


@pytest.mark.parametrize(
    "written,esperado",
    [
        ({}, ReviewerStatus.NOT_RUN),
        ({"honesty_reviewer": None}, ReviewerStatus.READER_FAILED),
        ({"honesty_reviewer": Path("sin-escribir.json")}, ReviewerStatus.ARTIFACT_MISSING),
    ],
    ids=["not-run", "reader-failed", "artifact-missing"],
)
def test_los_tres_estados_vacios_leidos_del_disco_no_bloquean(tmp_path, written, esperado):
    """Ninguno de los tres estados vacios bloquea el ZIP por la via de AC19."""
    audit = _directorio(tmp_path / "v4_audit", PROPUESTA_CON_CITA_OMITIDA)

    acta, reports, _ = _acta_con_bot4(audit, tmp_path, written=written)
    bot4 = _bot4(reports)

    assert bot4.status is esperado
    assert bot4.critical_count == 0
    assert bot4.recommendation is None
    assert acta["verdict"] != VERDICT_BLOCKED
    assert blocks_delivery_zip(acta) is False


def test_el_kill_switch_sigue_anulando_el_bloque(tmp_path):
    """GATE_BLOCKING_ENABLED=0 conserva su escape: blocks_publish False con suppressed True."""
    audit = _directorio(tmp_path / "v4_audit", PROPUESTA_CON_CITA_OMITIDA)
    _bot4_escrito_en_disco(audit, HonestyReviewer(audit).review(no_evaluable()))

    acta, reports, judge = _acta_con_bot4(audit, tmp_path)
    assert blocks_delivery_zip(acta) is True
    outcome = judge.finalize(
        acta, reports, blocks=blocks_delivery_zip(acta), gate_blocking_enabled=False
    )

    assert outcome.verdict == VERDICT_BLOCKED
    assert outcome.blocks_publish is False
    assert outcome.enforcement.suppressed_by_operator is True
