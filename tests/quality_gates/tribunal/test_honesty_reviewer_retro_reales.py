"""Tests retro de HonestyReviewer sobre los artefactos REALES del baseline.

Los 7 tests de la fase FASE-T4-B eran verdes contra un fixture que clonaba el
*contenido* de los artefactos pero no su *estructura de ubicación*, y la ubicación
era el requisito marcado ⚠️ CRÍTICO por el plan. Este archivo corre el revisor sobre
`output/FASE-D_salentoreal_post_guard/` para cerrar ese ángulo (R1.2 del dossier de
auditoría). Se omite en máquinas sin el baseline para no romper CI.
"""

import json
from pathlib import Path

import pytest

from modules.quality_gates.tribunal.honesty_reviewer import (
    FINDING_CG_WARNING_UNDISCLOSED,
    FINDING_MISSING_ARTIFACT,
    HonestyReviewer,
)
from modules.quality_gates.tribunal.llm_extractor import MockPromiseExtractor


BASELINE = Path("output/FASE-D_salentoreal_post_guard/v4_complete/hotelsalentoreal/v4_audit")

pytestmark = pytest.mark.skipif(
    not BASELINE.is_dir(), reason="baseline SalentoReal no disponible"
)

# Composición medida sobre los artefactos reales de la corrida 2026-08-31 12:28 (Tier B).
EXPECTED_TOTAL_CG = 12
EXPECTED_DISTINCT_CG = 10
EXPECTED_DUPLICATES = ["CG-OTA-NARRATIVE", "CG-TECH-JARGON"]
EXPECTED_UNDISCLOSED_GATE = "CG-WHATSAPP-LEAD"
EXPECTED_EVIDENCE_TIER = "B"


@pytest.fixture
def real_reviewer():
    return HonestyReviewer(BASELINE)


@pytest.fixture
def real_report(real_reviewer):
    return real_reviewer.review(extractor=MockPromiseExtractor([]))


def test_propuesta_real_resuelta_y_sin_missing_artifact(real_report):
    """D1: la propuesta vive en v4_complete/, no en v4_audit_dir."""
    assert real_report["findings"], "esperaba hallazgos de datos reales"
    missing = [f for f in real_report["findings"] if f["type"] == FINDING_MISSING_ARTIFACT]
    assert missing == [], f"MISSING_ARTIFACT espurio: {missing}"


def test_lee_los_cg_de_ambos_archivos_reales(real_report):
    """D1/S1: conteo no-cero, y entradas vs distintos quedan explícitos."""
    gates = real_report["commercial_gates_read"]
    assert gates["total_cg_count"] > 0
    assert gates["total_cg_count"] == EXPECTED_TOTAL_CG
    assert gates["distinct_cg_count"] == EXPECTED_DISTINCT_CG
    assert gates["duplicate_gate_ids"] == EXPECTED_DUPLICATES
    assert gates["warnings_found"] == [EXPECTED_UNDISCLOSED_GATE]


def test_nombre_reportado_es_el_archivo_realmente_leido(real_reviewer, real_report):
    """S3: el acta atribuye su conteo al Path que el revisor abrió."""
    resolved = real_reviewer._resolve_artifact_paths()
    gates = real_report["commercial_gates_read"]

    assert gates["canonical_file"] == resolved["cg_canonical"].name
    assert gates["diagnostic_file"] == resolved["cg_diagnostic"].name
    assert Path(BASELINE / gates["diagnostic_file"]).is_file()


def test_cg_whatsapp_lead_no_divulgado_en_propuesta_real(real_report):
    """AC12 por la segunda vía (D5): la propuesta real menciona el número de contacto
    pero no divulga el problema que el WARNING detectó."""
    referenced = {
        f.get("cg_reference")
        for f in real_report["findings"]
        if f["type"] == FINDING_CG_WARNING_UNDISCLOSED
    }
    assert EXPECTED_UNDISCLOSED_GATE in referenced


def test_evidence_tier_no_degradado_a_unknown(real_report):
    """S2: el tier del MANIFEST se propaga a todas las familias de hallazgo."""
    for finding in real_report["findings"]:
        assert finding["evidence_tier_declared"] == EXPECTED_EVIDENCE_TIER


def test_veredicto_determinado_por_hallazgos_reales(real_report):
    """D1: el veredicto sale de los CG-* reales, no de un artefacto ausente."""
    assert real_report["verdict_recommendation"] == "DEVOLVER-PRUEBAS"
    assert real_report["summary"]["total_findings"] == len(real_report["findings"])
    assert real_report["summary"]["undisclosed_warnings"] == len(
        [f for f in real_report["findings"] if f["type"] == FINDING_CG_WARNING_UNDISCLOSED]
    )


def test_serializacion_del_acta_real_es_releible(real_reviewer, tmp_path):
    """El acta de la corrida real se escribe y se re-leé intacta (en tmp, nunca en el
    baseline de sola lectura)."""
    output_path = real_reviewer.write_report(
        extractor=MockPromiseExtractor([]), output_path=tmp_path / "revision_honestidad.json"
    )
    loaded = json.loads(output_path.read_text(encoding="utf-8"))

    assert loaded["reviewer"] == "honesty_reviewer"
    assert loaded["clause"] == "P6.5"
    assert loaded["commercial_gates_read"]["total_cg_count"] == EXPECTED_TOTAL_CG
    assert loaded["findings"] == real_reviewer.review(extractor=MockPromiseExtractor([]))["findings"]
