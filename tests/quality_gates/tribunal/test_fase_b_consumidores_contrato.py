"""Bateria FASE-B — consumidores del contrato de cuatro estados (AC8/9/10/17/18).

Plan CURA-COSTURA-TRIBUNAL-2026-10-11. Cubre lo que FASE-A dejaba abierto: Bot 2 y
Bot 4 leen `extract_checked` y publican el estado de su insumo, el acta propaga ese
estado a un `ReviewerStatus` que no se puede leer como «sano» (AC17), la detección de
sobre-presentación corre sobre el texto completo (AC9/N5) y el patrón de CRITICAL
tiene su superficie de falso positivo medida y curada (AC10/N7).

L-T4A.5: cada test de estado lleva datos que **alcanzan** la rama que certifica. Ninguno
afirma una ausencia que el propio fixture fabrica: los casos de «sin hallazgos» se
diferencian de los de «no evaluado» comparando las dos variantes del mismo insumo.
"""

import copy
import json
from pathlib import Path

import pytest

from modules.quality_gates.tribunal.acta_writer import ActaWriter
from modules.quality_gates.tribunal.alignment_reviewer import AlignmentReviewer
from modules.quality_gates.tribunal.honesty_reviewer import (
    FINDING_CG_WARNING_UNDISCLOSED,
    FINDING_OVER_PRESENTATION,
    FINDING_TIER_MISMATCH,
    HonestyReviewer,
    VERIFICATION_GROUP_CUANTIFICADOR,
    VERIFICATION_GROUP_LENGUAJE,
    coincidencias_lenguaje_de_verificacion,
)
from modules.quality_gates.tribunal.judge import (
    STATUS_PASS,
    T1_CERTIFIABLE_CLAUSES,
    VERDICT_APPROVED,
    TribunalJudge,
    blocks_delivery_zip,
)
from modules.quality_gates.tribunal.llm_extractor import (
    ExtractionOutcome,
    ExtractionState,
    LLMPromiseExtractor,
    MockPromiseExtractor,
    VerbalPromise,
)
from modules.quality_gates.tribunal.outcome import (
    ReviewerStatus,
    collect_reviewer_reports,
)

# --- insumos -----------------------------------------------------------------

PROPUESTA_LIMPIA = """# Propuesta Comercial

## Introduccion
Le proponemos un boton de WhatsApp para reservas directas.

## Alcance
Pagina de FAQ y Schema Hotel con soporte editorial.
"""

PROPUESTA_CON_CITAS = """# Propuesta Comercial

## Introduccion
Ofrecemos soluciones verificadas para su hotel.
"""

PROPUESTA_CON_CITA_OMITIDA = """# Propuesta Comercial

## Introduccion
Ofrecemos soluciones verificadas para su hotel.

## Alcance
Publicamos datos confirmados del mercado en su ficha.
"""

BASELINE_REAL = Path("evidence/FASE-I/corrida/hotelsalentoreal/v4_audit")
BASELINE_PROPUESTA = Path("evidence/FASE-I/corrida/02_PROPUESTA_COMERCIAL_20260904_120413.md")


class ExtractoraConEstado:
    """Extractor que devuelve el ExtractionOutcome que el test pida, sin LLM."""

    def __init__(self, outcome):
        self.outcome = outcome
        self.llamadas = 0

    def extract_checked(self, proposal_text: str) -> ExtractionOutcome:
        self.llamadas += 1
        return self.outcome


def no_evaluable(motivo="respuesta ilegible: el texto no decodifica como JSON"):
    return ExtractoraConEstado(
        ExtractionOutcome(state=ExtractionState.NO_EVALUABLE, reason=motivo)
    )


def fallido(motivo="proveedor falló: ConnectionError: sin salida"):
    return ExtractoraConEstado(
        ExtractionOutcome(state=ExtractionState.FALLIDO, reason=motivo)
    )


def _directorio(base: Path, propuesta: str, tier: str = "B") -> Path:
    """v4_audit con los insumos minimos que leen Bot 2 y Bot 4."""
    base.mkdir(parents=True, exist_ok=True)
    (base / "02_PROPUESTA_COMERCIAL_20260904_120000.md").write_text(propuesta, encoding="utf-8")
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
        json.dumps(
            {
                "entries": [
                    {"service_name": "Boton de WhatsApp", "pain_ids": [], "status": "LINKED"},
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return base


@pytest.fixture
def audit_dir(tmp_path):
    return _directorio(tmp_path / "v4_audit", PROPUESTA_CON_CITAS)


def _hallazgos(report, tipo):
    return [f for f in report["findings"] if f.get("finding_type") == tipo]


def _escribir_report(audit: Path, nombre: str, report: dict) -> Path:
    ruta = audit / nombre
    ruta.write_text(json.dumps(report, ensure_ascii=False), encoding="utf-8")
    return ruta


# --- AC9: Bot 4 consume el estado ---------------------------------------------


def test_bot4_no_evaluable_publica_estado_y_no_aprueba(audit_dir):
    report = HonestyReviewer(audit_dir).review(no_evaluable())

    assert report["extraccion"]["estado"] == "NO-EVALUABLE"
    assert report["extraccion"]["motivo"].startswith("respuesta ilegible")
    assert report["extraccion"]["via"] == "extract_checked"
    assert report["verdict_recommendation"] != "APROBADO"


def test_bot4_fallido_publica_estado_con_su_motivo(audit_dir):
    """Texto limpio: el unico motivo de no aprobar es el insumo que fallo."""
    audit = _directorio(audit_dir.parent / "fallido", PROPUESTA_LIMPIA)

    report = HonestyReviewer(audit).review(fallido())

    assert report["extraccion"]["estado"] == "FALLIDO"
    assert "proveedor falló" in report["extraccion"]["motivo"]
    assert report["extraccion"]["promesas_leidas"] == 0
    assert report["findings"] == []
    assert report["verdict_recommendation"] == "DEVOLVER-PRUEBAS"


def test_bot4_ok_sin_promesas_es_sin_hallazgos_legitimo(audit_dir):
    """Control verde del tri-estado: texto limpio y extraccion OK -> sin hallazgos."""
    audit = _directorio(audit_dir.parent / "limpia", PROPUESTA_LIMPIA)

    report = HonestyReviewer(audit).review(MockPromiseExtractor([]))

    assert report["extraccion"]["estado"] == "OK_SIN_PROMESAS"
    assert report["findings"] == []
    assert report["verdict_recommendation"] == "APROBADO"


def test_bajo_no_evaluable_la_ausencia_de_claims_se_lee_en_el_estado(audit_dir):
    """TIER_MISMATCH depende de las promesas: no se emite, y el acta no lo lee como limpio.

    Lo que cura la AC9 no es inventar el hallazgo que el LLM no pudo proponer, sino que
    la ausencia viaje acompañada del estado que la explica (R2.9).
    """
    extractora = ExtractoraConEstado(
        ExtractionOutcome(
            state=ExtractionState.OK_CON_PROMESAS,
            promises=[VerbalPromise("datos con tier A de evidencia", "general", "Intro")],
        )
    )
    con_promesas = HonestyReviewer(audit_dir).review(extractora)
    sin_promesas = HonestyReviewer(audit_dir).review(no_evaluable())

    assert len(_hallazgos(con_promesas, FINDING_TIER_MISMATCH)) == 1
    assert _hallazgos(sin_promesas, FINDING_TIER_MISMATCH) == []
    assert sin_promesas["extraccion"]["estado"] == "NO-EVALUABLE"


# --- AC9/N5: el regex corre sobre el texto completo ---------------------------


def test_cita_omitida_por_el_extractor_sigue_detectada_en_texto_completo(audit_dir):
    """Con promesas=[] la sobre-presentacion se emite igual: ya no depende de la cita."""
    audit = _directorio(audit_dir.parent / "omitida", PROPUESTA_CON_CITA_OMITIDA)

    report = HonestyReviewer(audit).review(MockPromiseExtractor([]))

    literales = {f["claim_text"] for f in _hallazgos(report, FINDING_OVER_PRESENTATION)}
    assert {"verificadas", "confirmados"} <= literales


def test_el_hallazgo_de_texto_no_se_silencia_con_extraccion_no_evaluable(audit_dir):
    """El camino determinista sigue emitiendo bajo NO-EVALUABLE (no-OK != sin nada)."""
    audit = _directorio(audit_dir.parent / "noevaluable", PROPUESTA_CON_CITA_OMITIDA)

    report = HonestyReviewer(audit).review(no_evaluable())

    assert len(_hallazgos(report, FINDING_OVER_PRESENTATION)) == 2
    assert report["extraccion"]["estado"] == "NO-EVALUABLE"
    assert report["verdict_recommendation"] == "BLOQUEAR"


def test_tier_a_no_emite_sobre_presentacion(audit_dir):
    """El guard del tier sigue vigente: con evidencia A el lenguaje no es hallazgo."""
    audit = _directorio(audit_dir.parent / "tierA", PROPUESTA_CON_CITA_OMITIDA, tier="A")

    report = HonestyReviewer(audit).review(MockPromiseExtractor([]))

    assert _hallazgos(report, FINDING_OVER_PRESENTATION) == []


# --- AC10: superficie de falso positivo medida y curada -----------------------


def test_frontera_curada_el_cien_por_ciento_de_garantia_vuelve_a_ser_detectable():
    """`\b` despues de `%` pedia un caracter de palabra: ningun `100%` matcheaba."""
    texto = "Le garantizamos una ocupacion del 100% de las habitaciones reservadas."

    assert coincidencias_lenguaje_de_verificacion(texto)


def test_total_de_tabla_deja_de_ser_hallazgo():
    """Par del anterior: la fila de tabla que el patron viejo contaba como CRITICAL."""
    texto = "| **Total CAPEX** | **$2.500.000 COP** | Única vez |\n"

    assert coincidencias_lenguaje_de_verificacion(texto) == []


def test_total_de_una_linea_con_monto_deja_de_ser_hallazgo():
    """El segundo falso positivo medido: el cuantificador dentro de una cifra."""
    texto = "> **Trazabilidad financiera**: La fuga total estimada es de $21.067.200 COP.\n"

    assert coincidencias_lenguaje_de_verificacion(texto) == []


def test_el_absoluto_de_prosa_de_garantia_sigue_siendo_hallazgo():
    """La cura recorta el falso positivo, no el diente."""
    texto = "## GARANTIAS: Proteccion total para usted\n"

    halladas = coincidencias_lenguaje_de_verificacion(texto)
    assert [h["grupo"] for h in halladas] == ["CUANTIFICADOR_ABSOLUTO"]


def test_el_lenguaje_de_verificacion_no_lo_filtra_la_tabla():
    """Asimetria declarada: una celda que dice «Verificado» con tier B si es hallazgo."""
    texto = "| Perfil de Empresa en Google | ✅ Dia 1 (Verificado) | Ya existe en su web |\n"

    assert [h["grupo"] for h in coincidencias_lenguaje_de_verificacion(texto)] == [
        "LENGUAJE_VERIFICACION"
    ]


def test_la_medicion_importa_el_patron_del_codigo():
    """AC10: la medicion invoca VERIFICATION_PATTERNS, no un regex equivalente.

    Sobre un texto sin tablas ni montos, aplicar los dos patrones del modulo y recorrer
    la funcion del revisor tienen que dar el mismo conjunto de literales. Si la cura
    viviera en un patron re-escrito a mano, aqui se separarian.
    """
    import re

    texto = (
        "Ofrecemos soluciones verificadas con proteccion total\n"
        "y una garantia del 100% sobre la entrega.\n"
    )
    desde_patrones = sorted(
        m.group(0).lower()
        for patron in (VERIFICATION_GROUP_LENGUAJE, VERIFICATION_GROUP_CUANTIFICADOR)
        for m in re.finditer(patron, texto, re.IGNORECASE)
    )
    del_modulo = sorted(h["literal"].lower() for h in coincidencias_lenguaje_de_verificacion(texto))

    assert desde_patrones == del_modulo
    assert desde_patrones == ["100%", "total", "verificadas"]


# --- AC18: el contrato de claves del finding ----------------------------------


def test_findings_de_bot4_escriben_el_contrato_de_claves(audit_dir):
    report = HonestyReviewer(audit_dir).review(MockPromiseExtractor([]))

    assert report["findings"]
    for finding in report["findings"]:
        assert "type" not in finding
        assert finding["finding_type"]
        assert finding["clause"] == "P6.5"
        assert finding["source_artifact"]


def test_el_acta_proyecta_el_hallazgo_de_bot4_nombrado(audit_dir, tmp_path):
    """AC18 se certifica en un acta generada: finding_type != None, como en 2026-10-07."""
    report = HonestyReviewer(audit_dir).review(MockPromiseExtractor([]))
    _escribir_report(audit_dir, "revision_honestidad.json", report)
    reports = collect_reviewer_reports(
        audit_dir,
        written={"honesty_reviewer": audit_dir / "revision_honestidad.json"},
    )
    judge_acta = TribunalJudge(audit_dir, tmp_path / "deliveries", "hotelx").evaluate()
    acta = TribunalJudge(audit_dir, tmp_path / "deliveries", "hotelx").enrich(
        judge_acta, reports
    )

    proyectados = [
        f
        for r in acta["reviewer_reports"]
        if r["reviewer"] == "honesty_reviewer"
        for f in r["findings"]
    ]
    assert proyectados
    assert all(f.get("finding_type") for f in proyectados)


# --- AC8: Bot 2 consume el estado ---------------------------------------------


def test_bot2_no_evaluable_publica_estado_y_nunca_ok_no_findings(audit_dir):
    report = AlignmentReviewer(audit_dir).review(no_evaluable())

    assert report["extraccion"]["estado"] == "NO-EVALUABLE"
    assert report["extraccion"]["motivo"]
    assert report["verdict_recommendation"] == "DEVOLVER-PRUEBAS"


def test_bot2_fallido_publica_estado_y_el_motivo_del_proveedor(audit_dir):
    report = AlignmentReviewer(audit_dir).review(fallido())

    assert report["extraccion"]["estado"] == "FALLIDO"
    assert "proveedor falló" in report["extraccion"]["motivo"]


def test_bot2_ok_sin_promesas_es_un_sin_hallazgos_legitimo(audit_dir):
    """Control: con matriz LINKED+pain_id y extraccion OK vacia, si es sin hallazgos."""
    (audit_dir / "proposal_asset_matrix.json").write_text(
        json.dumps(
            {"entries": [{"service_name": "Boton de WhatsApp", "pain_ids": ["sin_whatsapp"], "status": "LINKED"}]},
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    report = AlignmentReviewer(audit_dir).review(MockPromiseExtractor([]))

    assert report["extraccion"]["estado"] == "OK_SIN_PROMESAS"
    assert report["findings"] == []
    assert report["verdict_recommendation"] == "APROBADO"


def test_bot2_el_cruce_matriz_promesa_sigue_disparando_bajo_no_ok(audit_dir):
    """El no-OK no apaga la mitad determinista del revisor (SIN_BRECHA_ASOCIADA)."""
    report = AlignmentReviewer(audit_dir).review(no_evaluable())

    tipos = {f["finding_type"] for f in report["findings"]}
    assert "SIN_BRECHA_ASOCIADA" in tipos
    assert report["summary"]["no_breach"] >= 1


def test_bot2_exige_extractor_y_no_instancia_el_llm_real(audit_dir):
    """Sin default, un llamador offline no puede disparar una llamada al proveedor."""
    with pytest.raises(TypeError):
        AlignmentReviewer(audit_dir).review()

    fuente = Path("modules/quality_gates/tribunal/alignment_reviewer.py").read_text(encoding="utf-8")
    assert "LLMPromiseExtractor" not in fuente
    assert not hasattr(LLMPromiseExtractor, "extract_verbal_promises")


# --- AC17: el estado no-OK llega al acta y al veredicto ------------------------


def _acta_con_extraccion(audit: Path, reporte: dict, tmp_path: Path) -> dict:
    """Atraviesa collect_reviewer_reports + _compute_verdict con el acta certificable.

    Los otros tres Bots se escriben sanos y sin hallazgos: si quedaran NOT_RUN, el
    veredicto nunca seria APROBADO-PARA-ENTREGA ni en el control, y la comparacion
    estaria ganando por vacio (L-T4A.5).
    """
    _escribir_report(audit, "revision_alineacion.json", reporte)
    for nombre, revisor in (
        ("revision_diagnostico.json", "diagnosis_reviewer"),
        ("revision_assets.json", "asset_reviewer"),
        ("revision_honestidad.json", "honesty_reviewer"),
    ):
        _escribir_report(
            audit,
            nombre,
            {"reviewer": revisor, "clause": "P6", "findings": [], "verdict_recommendation": "APROBADO"},
        )
    reports = collect_reviewer_reports(audit)
    judge = TribunalJudge(audit, tmp_path / "deliveries", "hotelx")
    acta = judge.evaluate()
    acta["evidence_tier"] = "A"
    acta["first_floor_rule"] = {"applied": False}
    for clause in T1_CERTIFIABLE_CLAUSES:
        acta["clauses"][clause]["status"] = STATUS_PASS
    return judge.enrich(copy.deepcopy(acta), reports), reports


def test_no_evaluable_no_produce_ok_no_findings_en_el_acta(audit_dir, tmp_path):
    (audit_dir / "proposal_asset_matrix.json").write_text(
        json.dumps({"entries": []}, ensure_ascii=False), encoding="utf-8"
    )
    reporte = AlignmentReviewer(audit_dir).review(no_evaluable())
    assert reporte["findings"] == []

    acta, reports = _acta_con_extraccion(audit_dir, reporte, tmp_path)

    bot2 = next(r for r in reports if r.reviewer == "alignment_reviewer")
    proyectado = next(r for r in acta["reviewer_reports"] if r["reviewer"] == "alignment_reviewer")
    assert bot2.findings_count == 0
    assert bot2.status is ReviewerStatus.INPUT_NOT_EVALUABLE
    assert proyectado["status"] == "INPUT_NOT_EVALUABLE"
    assert proyectado["extraccion"]["estado"] == "NO-EVALUABLE"
    assert acta["verdict"] != VERDICT_APPROVED


def test_el_mismo_insumo_ok_si_es_aprobable(audit_dir, tmp_path):
    """Control verde del par: unico cambio, la extraccion paso a OK_SIN_PROMESAS."""
    (audit_dir / "proposal_asset_matrix.json").write_text(
        json.dumps({"entries": []}, ensure_ascii=False), encoding="utf-8"
    )
    reporte = AlignmentReviewer(audit_dir).review(MockPromiseExtractor([]))

    acta, reports = _acta_con_extraccion(audit_dir, reporte, tmp_path)

    bot2 = next(r for r in reports if r.reviewer == "alignment_reviewer")
    proyectado = next(r for r in acta["reviewer_reports"] if r["reviewer"] == "alignment_reviewer")
    assert bot2.status is ReviewerStatus.OK_NO_FINDINGS
    assert proyectado["status"] == "OK_NO_FINDINGS"
    assert acta["verdict"] == VERDICT_APPROVED


def test_bloquear_con_critical_verificado_sigue_suprimiendo_el_zip(audit_dir, tmp_path):
    """La rama real del enforcement: CRITICAL verificado -> BLOQUEADO -> ZIP suprimido."""
    reporte = HonestyReviewer(audit_dir).review(MockPromiseExtractor([]))
    assert reporte["verdict_recommendation"] == "BLOQUEAR"
    _escribir_report(audit_dir, "revision_honestidad.json", reporte)
    reports = collect_reviewer_reports(
        audit_dir, written={"honesty_reviewer": audit_dir / "revision_honestidad.json"}
    )
    judge = TribunalJudge(audit_dir, tmp_path / "deliveries", "hotelx")
    acta = judge.enrich(judge.evaluate(), reports)

    bot4 = next(r for r in reports if r.reviewer == "honesty_reviewer")
    assert bot4.status is ReviewerStatus.OK_WITH_FINDINGS
    assert bot4.verified_critical
    assert acta["verdict"] == "BLOQUEADO"
    assert blocks_delivery_zip(acta)


def test_el_acta_md_mostra_la_etiqueta_del_estado_nuevo(audit_dir, tmp_path):
    """AC17: sin etiqueta en _STATUS_LABELS el MD imprimia el simbolo crudo."""
    reporte = AlignmentReviewer(audit_dir).review(no_evaluable())
    acta, _ = _acta_con_extraccion(audit_dir, reporte, tmp_path)

    json_ruta, md_ruta = ActaWriter(tmp_path / "acta").write(acta)
    md = md_ruta.read_text(encoding="utf-8")
    leido = json.loads(json_ruta.read_text(encoding="utf-8"))

    assert "⬜ insumo no evaluable" in md
    assert "INPUT_NOT_EVALUABLE" not in md.split("## Reportes de Revisores")[1].split("##")[0]
    assert leido["reviewer_reports"][2]["status"] == "INPUT_NOT_EVALUABLE"


# --- R2.6: baseline real (artefactos versionados del repo) --------------------

pytestmark_baseline = pytest.mark.skipif(
    not (BASELINE_REAL.is_dir() and BASELINE_PROPUESTA.is_file()),
    reason="baseline real FASE-I (hotelsalentoreal 2026-09-04) no disponible",
)


@pytestmark_baseline
def test_bot4_sobre_baseline_real_y_state_del_acta():
    """Bot 4 sobre la propuesta real: tres coincidencias medidas, ninguna de tabla."""
    report = HonestyReviewer(BASELINE_REAL).review(MockPromiseExtractor([]))

    sobre = _hallazgos(report, FINDING_OVER_PRESENTATION)
    assert report["extraccion"]["estado"] == "OK_SIN_PROMESAS"
    assert len(sobre) == 3
    assert {f["verification_group"] for f in sobre} == {
        "LENGUAJE_VERIFICACION",
        "CUANTIFICADOR_ABSOLUTO",
    }
    assert report["verdict_recommendation"] == "BLOQUEAR"


@pytestmark_baseline
def test_bot2_sobre_baseline_real_con_extraccion_no_evaluable():
    """El acta del run real bajo NO-EVALUABLE: estado publicado, no «sin promesas»."""
    report = AlignmentReviewer(BASELINE_REAL).review(no_evaluable("respuesta truncada"))

    assert report["extraccion"]["estado"] == "NO-EVALUABLE"
    assert report["service_matrix"], "el cruce matriz→promesa no se apaga"
    assert report["verdict_recommendation"] != "APROBADO"
