"""AC11 (cura N6): una sola precedencia de evidence_tier, compartida por Juez y Bot 4.

La situación que curó esta fase: el Juez leía escenarios→MANIFEST→"C" y Bot 4 leía
MANIFEST→escenarios→"UNKNOWN". Con dos consumidores y dos reglas, el acta aplicaba el
primer piso mientras el check de sobre-presentación del revisor se silenciaba (UNKNOWN
estaba en la lista que devolvía la lista vacía antes de evaluar).

Rama **no certificada**, declarada: «MANIFEST y escenarios en desacuerdo». No la produce
el régimen ZIP-only (L-E2E.1: nunca se descomprime `deliveries/<hotel>/MANIFEST.json`) y
no la produce ningún arnés de la casa (medido: `build_dir` de
`test_honesty_reviewer_fidelidad_salida.py` jamás pasa `breakdown=`). Forzarla con un
fixture sintético certificaría una rama que producción no genera; la AC lo prohíbe.
"""

import json
from pathlib import Path

from modules.quality_gates.tribunal import evidence_tier as evidence_tier_module
from modules.quality_gates.tribunal import honesty_reviewer as honesty_reviewer_module
from modules.quality_gates.tribunal import judge as judge_module
from modules.quality_gates.tribunal.evidence_tier import (
    FUENTE_ESCENARIOS,
    FUENTE_MANIFEST,
    FUENTE_SIN_DECLARACION,
    TIER_FALLBACK,
    resolve_evidence_tier,
)
from modules.quality_gates.tribunal.honesty_reviewer import (
    FINDING_OVER_PRESENTATION,
    FINDING_OVER_PRESENTATION_NO_EVALUABLE,
    HonestyReviewer,
)
from modules.quality_gates.tribunal.judge import TribunalJudge
from modules.quality_gates.tribunal.llm_extractor import MockPromiseExtractor


PROYECTOS = {"conservative": 1, "realistic": 2, "optimistic": 3}

PROSA_CON_LENGUAJE_DE_VERIFICACION = (
    "# Propuesta Comercial\n\nTransparencia total en cada cifra que le entregamos.\n"
)
PROSA_SIN_LENGUAJE_DE_VERIFICACION = (
    "# Propuesta Comercial\n\nLe mostramos el alcance del trabajo.\n"
)


def construir_run(
    tmp_path: Path,
    *,
    tier_escenarios=None,
    tier_manifest=None,
    proposal=PROSA_SIN_LENGUAJE_DE_VERIFICACION,
) -> tuple[Path, Path]:
    """Monta `v4_audit` + `deliveries` como los deja el pipeline y retorna ambas rutas.

    `tier_escenarios=None` escribe el scenarios **sin** `breakdown`: es la vía con la que
    un test deja el tier sin declarar, que es el estado que curó AC11.
    """
    v4_audit = tmp_path / "v4_complete" / "hotelx" / "v4_audit"
    v4_audit.mkdir(parents=True)
    deliveries = tmp_path / "v4_complete" / "deliveries"
    paquete = deliveries / "hotelx_20261012"
    paquete.mkdir(parents=True)

    escenarios = {"scenarios": dict(PROYECTOS)}
    if tier_escenarios is not None:
        escenarios["breakdown"] = {"evidence_tier": tier_escenarios}
    (v4_audit / "financial_scenarios_20261012.json").write_text(
        json.dumps(escenarios), encoding="utf-8"
    )
    (v4_audit / "02_PROPUESTA_COMERCIAL_20261012.md").write_text(proposal, encoding="utf-8")
    (v4_audit / "commercial_gates_report.json").write_text(
        json.dumps({"results": []}), encoding="utf-8"
    )

    if tier_manifest is not None:
        (paquete / "MANIFEST.json").write_text(
            json.dumps({"quality_metadata": {"evidence_tier": tier_manifest}}),
            encoding="utf-8",
        )
    return v4_audit, deliveries


def revisar(v4_audit: Path, deliveries: Path) -> dict:
    return HonestyReviewer(v4_audit, deliveries).review(
        extractor=MockPromiseExtractor([])
    )


def enjuiciar(v4_audit: Path, deliveries: Path) -> dict:
    return TribunalJudge(
        v4_audit_dir=v4_audit, deliveries_dir=deliveries, hotel_id="hotelx"
    ).evaluate()


# ── el símbolo: precedencia y fallback únicos ────────────────────────────


def test_el_mismo_dato_bajo_las_dos_vias_coincidentes_aporta_el_mismo_tier():
    """Coinciden: escenarios y MANIFEST declaran "B" → gana escenarios, declarado."""
    resolucion = resolve_evidence_tier(
        {"breakdown": {"evidence_tier": "B"}},
        {"quality_metadata": {"evidence_tier": "B"}},
        scenarios_name="financial_scenarios_20261012.json",
    )

    assert resolucion.tier == "B"
    assert resolucion.fuente == FUENTE_ESCENARIOS
    assert resolucion.declarado is True
    assert resolucion.descripcion_fuente == (
        "financial_scenarios_20261012.json → breakdown.evidence_tier"
    )


def test_falta_la_fuente_de_escenarios_y_aporta_el_manifest():
    """Falta una fuente: sin `breakdown`, el MANIFEST declara el tier y se nombra a sí mismo."""
    resolucion = resolve_evidence_tier(
        {"scenarios": dict(PROYECTOS)}, {"quality_metadata": {"evidence_tier": "C"}}
    )

    assert (resolucion.tier, resolucion.fuente, resolucion.declarado) == (
        "C",
        FUENTE_MANIFEST,
        True,
    )
    assert resolucion.descripcion_fuente == "MANIFEST.json → quality_metadata.evidence_tier"


def test_sin_ninguna_fuente_el_fallback_es_el_mismo_simbolo_para_ambos():
    """El fallback vive en el símbolo compartido: un solo literal para las dos bocas."""
    resolucion = resolve_evidence_tier(None, None)

    assert resolucion.tier == TIER_FALLBACK
    assert resolucion.fuente == FUENTE_SIN_DECLARACION
    assert resolucion.declarado is False
    assert TIER_FALLBACK in resolucion.descripcion_fuente


def test_un_manifest_de_forma_inesperada_no_se_lea_como_tier_declarado():
    """`quality_metadata` sin clave, o un tier vacío: no es declaración, es fallback."""
    for manifest in ({"quality_metadata": {}}, {"quality_metadata": {"evidence_tier": ""}}, {}):
        resolucion = resolve_evidence_tier(None, manifest)
        assert (resolucion.tier, resolucion.declarado) == (TIER_FALLBACK, False)


def test_los_dos_consumidores_importan_el_simbolo_compartido():
    """Un símbolo, dos consumidores: la precedencia ya no vive re-escrita en cada módulo."""
    raiz = Path(__file__).resolve().parents[3]
    fuente_judge = (raiz / "modules/quality_gates/tribunal/judge.py").read_text(
        encoding="utf-8"
    )
    fuente_bot4 = (
        raiz / "modules/quality_gates/tribunal/honesty_reviewer.py"
    ).read_text(encoding="utf-8")

    assert "resolve_evidence_tier" in fuente_judge
    assert "resolve_evidence_tier" in fuente_bot4
    assert not hasattr(HonestyReviewer, "_extract_evidence_tier")
    # La cadena que invertía el orden en Bot 4 (MANIFEST primero) no sigue escrita a mano.
    assert 'manifest["quality_metadata"].get("evidence_tier")' not in fuente_bot4


def test_la_precedencia_vive_en_un_unico_objeto():
    """Las dos bocas están atadas al mismo objeto: nadie puede cambiar el orden a solas."""
    assert judge_module.resolve_evidence_tier is resolve_evidence_tier
    assert honesty_reviewer_module.resolve_evidence_tier is resolve_evidence_tier


# ── los dos consumidores resuelven igual ─────────────────────────────────


def test_juez_y_bot4_coinciden_cuando_ambas_fuentes_declaran_lo_mismo(tmp_path):
    """Certificación cruzada por comportamiento: mismo insumo → mismo tier en las dos bocas."""
    v4_audit, deliveries = construir_run(tmp_path, tier_escenarios="B", tier_manifest="B")

    acta = enjuiciar(v4_audit, deliveries)
    report = revisar(v4_audit, deliveries)

    assert acta["evidence_tier"] == "B"
    assert report["tier_resuelto"]["evidence_tier"] == "B"
    assert report["tier_resuelto"]["fuente"] == FUENTE_ESCENARIOS
    assert (
        acta["first_floor_rule"]["source_artifact"]
        == report["tier_resuelto"]["motivo_fuente"]
    )


def test_juez_y_bot4_coinciden_en_el_fallback_cuando_nadie_declara(tmp_path):
    """Sin ninguna declaración, los dos leen TIER_FALLBACK y Bot 4 además lo marca no-declarado."""
    v4_audit, deliveries = construir_run(tmp_path)

    acta = enjuiciar(v4_audit, deliveries)
    report = revisar(v4_audit, deliveries)

    assert acta["evidence_tier"] == TIER_FALLBACK
    assert report["tier_resuelto"]["evidence_tier"] == TIER_FALLBACK
    assert report["tier_resuelto"]["declarado"] is False


def test_el_manifest_puede_declarar_solo_y_ambos_lo_leen(tmp_path):
    """Rama del MANIFEST (fallback del Juez, segunda de la precedencia): la regla sigue siendo una."""
    v4_audit, deliveries = construir_run(tmp_path, tier_manifest="B+")

    acta = enjuiciar(v4_audit, deliveries)
    report = revisar(v4_audit, deliveries)

    assert acta["evidence_tier"] == "B+"
    assert report["tier_resuelto"]["evidence_tier"] == "B+"
    assert report["tier_resuelto"]["fuente"] == FUENTE_MANIFEST
    assert acta["first_floor_rule"]["applied"] is True


# ── UNKNOWN dejó de silenciar el check de Bot 4 ──────────────────────────


def test_tier_no_declarado_publica_estado_no_evaluable_en_vez_de_silencio(tmp_path):
    """El caso N6: antes devolvía [] y el check no corría; ahora publica su no-evaluable."""
    v4_audit, deliveries = construir_run(
        tmp_path, proposal=PROSA_CON_LENGUAJE_DE_VERIFICACION
    )

    report = revisar(v4_audit, deliveries)
    hallazgos = report["findings"]
    no_evaluables = [
        f for f in hallazgos if f["finding_type"] == FINDING_OVER_PRESENTATION_NO_EVALUABLE
    ]

    assert len(no_evaluables) == 1
    assert no_evaluables[0]["severity"] == "WARNING"
    assert no_evaluables[0]["evidence_tier_declarado"] is False
    # Contrato de claves del acta (AC18): nombrado, no anónimo.
    assert no_evaluables[0]["clause"] == "P6.5"
    assert no_evaluables[0]["source_artifact"]
    # Con tier no declarado no se inventa un CRITICAL: el ZIP no se suprime por falta de dato.
    assert [f for f in hallazgos if f["finding_type"] == FINDING_OVER_PRESENTATION] == []
    assert report["summary"]["over_presentaciones_no_evaluables"] == 1
    assert report["verdict_recommendation"] == "DEVOLVER-PRUEBAS"


def test_tier_declarado_no_degradado_sigue_emitiendo_el_critical(tmp_path):
    """Contraste que evita el verde vacuo: con tier declarado el mismo texto sí CRITICA."""
    v4_audit, deliveries = construir_run(
        tmp_path, tier_escenarios="B", proposal=PROSA_CON_LENGUAJE_DE_VERIFICACION
    )

    report = revisar(v4_audit, deliveries)
    criticos = [f for f in report["findings"] if f["finding_type"] == FINDING_OVER_PRESENTATION]

    assert len(criticos) == 1
    assert report["findings"] == criticos
    assert report["verdict_recommendation"] == "BLOQUEAR"


def test_tier_a_declarado_no_emite_sobre_presentacion_ni_estado_no_evaluable(tmp_path):
    """El salto legítimo sigue siendo legítimo: A declarado = check evaluado, sin hallazgo."""
    v4_audit, deliveries = construir_run(
        tmp_path, tier_escenarios="A", proposal=PROSA_CON_LENGUAJE_DE_VERIFICACION
    )

    report = revisar(v4_audit, deliveries)

    assert report["findings"] == []
    assert report["tier_resuelto"]["declarado"] is True
