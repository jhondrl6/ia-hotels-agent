"""Fidelidad y contrato de la salida de HonestyReviewer (R6, R8, R9 del dossier).

Cubren los modos de fallo que la suite de la fase no observaba: gates replicados en
ambos archivos, tier degradado a UNKNOWN, nombre reportado que no corresponde al
archivo leído, y divulgación adivinada con palabras sueltas.
"""

import json
import os
import time
from pathlib import Path

from modules.quality_gates.tribunal.honesty_reviewer import (
    DISCLOSURE_PHRASES_BY_GATE,
    FINDING_CG_WARNING_UNDISCLOSED,
    HonestyReviewer,
)
from modules.quality_gates.tribunal.llm_extractor import MockPromiseExtractor


PROPOSAL_WITH_CONTACT_ONLY = "# Propuesta\n\nWhatsApp: 316 6296142\n"
PROPOSAL_DISCLOSING_PROBLEM = (
    "# Propuesta\n\n"
    "Hallazgo: WhatsApp no aparece en la sección inicial del diagnóstico. "
    "Lo abrimos como quick win #1.\n"
)


def gate(gate_id, severity="WARNING", passed=True, message="sin detalle", suggestion=""):
    return {
        "gate_id": gate_id,
        "name": gate_id,
        "passed": passed,
        "severity": severity,
        "message": message,
        "suggestion": suggestion,
    }


def build_dir(root: Path, canonical_results=None, diagnostic_results=None,
              proposal=PROPOSAL_WITH_CONTACT_ONLY, manifest_tier="B",
              breakdown=None, diagnostic_files=None):
    """Crea un v4_audit con su deliveries, como el pipeline."""
    v4_complete = root / "v4_complete"
    v4_audit = v4_complete / "hotelx" / "v4_audit"
    v4_audit.mkdir(parents=True)
    delivery = v4_complete / "deliveries" / "hotelx_20260901"
    delivery.mkdir(parents=True)

    (v4_audit / "commercial_gates_report.json").write_text(
        json.dumps({"results": canonical_results or []}), encoding="utf-8"
    )
    for name, results in (diagnostic_files or {
        "commercial_gates_report_diagnostic_20260901_000000.json": diagnostic_results or []
    }).items():
        (v4_audit / name).write_text(json.dumps({"results": results}), encoding="utf-8")

    scenarios = {"scenarios": {"conservative": 1, "realistic": 2, "optimistic": 3}}
    if breakdown:
        scenarios["breakdown"] = breakdown
    (v4_audit / "financial_scenarios_20260901.json").write_text(
        json.dumps(scenarios), encoding="utf-8"
    )
    (v4_audit / "02_PROPUESTA_COMERCIAL_20260901.md").write_text(proposal, encoding="utf-8")

    if manifest_tier:
        (delivery / "MANIFEST.json").write_text(
            json.dumps({"quality_metadata": {"evidence_tier": manifest_tier}}), encoding="utf-8"
        )
    return v4_audit


def review(v4_audit):
    return HonestyReviewer(v4_audit).review(extractor=MockPromiseExtractor([]))


def undisclosed_findings(report):
    return [f for f in report["findings"] if f["type"] == FINDING_CG_WARNING_UNDISCLOSED]


def test_gate_replicado_y_fallido_emite_un_solo_finding(tmp_path):
    """S1: CG-OTA-NARRATIVE en ambos archivos no puede producir dos hallazgos idénticos."""
    repeated = gate("CG-OTA-NARRATIVE", passed=False, message="sin narrativa OTA")
    v4_audit = build_dir(
        tmp_path, canonical_results=[repeated],
        diagnostic_results=[repeated, gate("CG-TECH-JARGON", passed=True)],
        proposal="# Propuesta sin el problema\n",
    )
    report = review(v4_audit)

    assert len(undisclosed_findings(report)) == 1
    assert report["commercial_gates_read"]["warnings_found"] == ["CG-OTA-NARRATIVE"]
    assert report["summary"]["undisclosed_warnings"] == 1


def test_entradas_y_distintos_se_reportan_por_separado(tmp_path):
    """Q4: `total_cg_count` cuenta entradas y el campo explícito resuelve la ambigüedad."""
    shared = gate("CG-TECH-JARGON")
    v4_audit = build_dir(tmp_path, canonical_results=[shared], diagnostic_results=[shared])
    gates = review(v4_audit)["commercial_gates_read"]

    assert gates["total_cg_count"] == 2
    assert gates["distinct_cg_count"] == 1
    assert gates["duplicate_gate_ids"] == ["CG-TECH-JARGON"]


def test_mencion_legitima_de_contacto_no_divulga_el_problema(tmp_path):
    """D5/AC12 segunda vía: la propuesta real cita el número y aun así el WARNING no está divulgado."""
    v4_audit = build_dir(
        tmp_path,
        diagnostic_results=[gate("CG-WHATSAPP-LEAD", passed=False,
                                 message="WhatsApp no aparece en la sección inicial del diagnóstico.")],
    )
    refs = {f["cg_reference"] for f in undisclosed_findings(review(v4_audit))}

    assert "CG-WHATSAPP-LEAD" in refs


def test_divulgacion_expresa_cierra_el_hallazgo(tmp_path):
    """Con el problema nombrado expresamente, el revisor deja de señalarlo."""
    v4_audit = build_dir(
        tmp_path,
        diagnostic_results=[gate("CG-WHATSAPP-LEAD", passed=False,
                                 message="WhatsApp no aparece en la sección inicial del diagnóstico.")],
        proposal=PROPOSAL_DISCLOSING_PROBLEM,
    )
    report = review(v4_audit)

    assert undisclosed_findings(report) == []
    assert report["verdict_recommendation"] == "APROBADO"


def test_gate_sin_criterio_de_divulgacion_no_se_juzga(tmp_path):
    """Sin entrada en la tabla no se afirma divulgación: se evita el falso positivo."""
    v4_audit = build_dir(
        tmp_path, diagnostic_results=[gate("CG-ALGUNA-NUEVA", passed=False)],
        proposal="# Propuesta que no menciona nada\n",
    )
    assert undisclosed_findings(review(v4_audit)) == []


def test_tier_del_manifest_llega_a_los_hallazgos_cg(tmp_path):
    """S2: el tier ya resuelto se propaga en vez de degradarse a UNKNOWN."""
    v4_audit = build_dir(
        tmp_path,
        diagnostic_results=[gate("CG-WHATSAPP-LEAD", passed=False)],
        manifest_tier="C",
    )
    findings = undisclosed_findings(review(v4_audit))

    assert findings and findings[0]["evidence_tier_declared"] == "C"


def test_nombre_reportado_corresponde_al_archivo_cargado(tmp_path):
    """S3: el más reciente por mtime es el que se lee Y el que se reporta."""
    older = "commercial_gates_report_diagnostic_20260101_000000.json"
    newest = "commercial_gates_report_diagnostic_20260901_000000.json"
    v4_audit = build_dir(
        tmp_path,
        diagnostic_files={
            older: [gate("CG-VIEJO-A"), gate("CG-VIEJO-B"), gate("CG-VIEJO-C")],
            newest: [gate("CG-WHATSAPP-LEAD", passed=False)],
        },
        proposal="# Propuesta que no menciona el problema\n",
    )
    now = time.time()
    os.utime(v4_audit / older, (now - 86400 * 30, now - 86400 * 30))
    os.utime(v4_audit / newest, (now - 86400, now - 86400))

    reviewer = HonestyReviewer(v4_audit)
    report = reviewer.review(extractor=MockPromiseExtractor([]))
    gates = report["commercial_gates_read"]

    assert gates["diagnostic_file"] == newest
    assert gates["total_cg_count"] == 1
    assert os.stat(v4_audit / gates["diagnostic_file"]).st_mtime > os.stat(v4_audit / older).st_mtime


def test_all_gates_no_infla_el_acta(tmp_path):
    """S4/Q: all_gates se reduce a gate_id/severity/passed; el detalle sigue en la fuente."""
    v4_audit = build_dir(tmp_path, canonical_results=[gate("CG-ROI-NEGATIVE", severity="BLOCKING")])
    all_gates = review(v4_audit)["commercial_gates_read"]["all_gates"]

    assert all(set(g.keys()) == {"gate_id", "severity", "passed"} for g in all_gates)


def test_no_rejulga_un_gate_que_paso(tmp_path):
    """NR4: el revisor lee el veredicto del gate, no recalcula su criterio."""
    v4_audit = build_dir(
        tmp_path,
        diagnostic_results=[gate("CG-TIER-CONSISTENCY", passed=True,
                                 message="Tier consistente: 'B' en frontmatter y texto.")],
        proposal="# Propuesta\n\nAquí hay un tier inconsistente y jerga técnica\n",
    )
    assert undisclosed_findings(review(v4_audit)) == []


def test_no_reimplementa_logica_de_publication_gates():
    """NR4: el módulo del revisor no importa internals de los gates que revisa."""
    import modules.quality_gates.tribunal.honesty_reviewer as subject

    forbidden = ("publication_gates", "domain_gates", "coherence_gate", "delivery_quality_report")
    assert subject.__file__ is not None
    source = Path(subject.__file__).read_text(encoding="utf-8")
    assert not any(f"modules.quality_gates.{name}" in source or f"from {name}" in source
                   for name in forbidden)


def test_tabla_de_divulgacion_cubre_los_gates_warning_posibles():
    """La tabla es auditables: cada frase nombra un problema, no una palabra suelta."""
    for gate_id, phrases in DISCLOSURE_PHRASES_BY_GATE.items():
        assert phrases, gate_id
        for phrase in phrases:
            assert " " in phrase or len(phrase) > 9, f"{gate_id}: frase demasiado suelta: {phrase}"
