"""FASE-E (A2) — Persistencia del snapshot canónico de SitePresence.

Desde DT4-R2 el snapshot se calcula una vez por corrida (main.py,
``normalize_site_presence``) y se propaga en memoria; esta fase añade la
mitad que faltaba: disco (``v4_audit/site_presence_snapshot.json``). El
oráculo que decide ``present_in_production`` — y con ello ``no_breach``,
``unresolved``, ``coverage_ratio`` y G9 — pasa a ser auditable post-hoc.

Contratos fijados (anti-regresión DT4-N2: "los gates validan, no descubren
ni reconstruyen la evidencia primaria"):

* El writer serializa el objeto propagado TAL CUAL: si algún día se cuela
  un ``normalize_site_presence`` dentro del writer, los campos extra que
  hoy sobreviven desaparecerían y estos tests se ponen rojos.
* UTF-8 explícito con acentos/ñ (precedente FASE-P0-C / v4.46.1 ENCODING-SAFETY).
* El snapshot persistido alimenta los MISMOS oráculos que la versión en
  memoria (retro-testeable: una corrida pasada puede re-evaluarse).
"""

import json

from modules.asset_generation.proposal_asset_alignment import (
    ProposalAssetMatrixEntry,
    _presence_exists,
    committed_services_from_entries,
)
from modules.asset_generation.site_presence_adapter import (
    SNAPSHOT_VERSION,
    normalize_site_presence,
    save_site_presence_snapshot,
)
from modules.quality_gates.alignment_result import _presence_resolved


def _canonical_snapshot() -> dict:
    results = {
        "llms_txt": {
            "status": "exists_with_issues",
            "site_verified": True,
            "confidence": 0.95,
        },
        "whatsapp_button": {
            "status": "not_exists",
            "site_verified": False,
            "confidence": 0.7,
        },
    }
    # normalize_site_presence publica cada asset además como clave top-level
    # (contrato que consume AlignmentResult._presence_resolved).
    return {
        "site_url": "https://hotel-vísperas-ñ.example.com",
        "checked_at": "2026-09-03T12:00:00",
        "results": results,
        **results,
    }


def test_writer_escribe_el_archivo(tmp_path):
    path = tmp_path / "v4_audit" / "site_presence_snapshot.json"
    snapshot = _canonical_snapshot()

    save_site_presence_snapshot(snapshot, path)

    assert path.exists(), "el writer dejó de escribir site_presence_snapshot.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["snapshot_version"] == SNAPSHOT_VERSION
    assert payload["snapshot"] == snapshot


def test_no_reconstruccion_campos_extra_sobreviven(tmp_path):
    path = tmp_path / "site_presence_snapshot.json"
    snapshot = _canonical_snapshot()
    snapshot["probe_top_level"] = {"notas": "debe-sobrevivir"}
    snapshot["results"]["llms_txt"]["probe_entry"] = "debe-sobrevivir"
    snapshot["llms_txt"]["probe_entry"] = "debe-sobrevivir"

    save_site_presence_snapshot(snapshot, path)

    persisted = json.loads(path.read_text(encoding="utf-8"))["snapshot"]
    assert persisted == snapshot, (
        "el writer alteró el snapshot: ¿se coló una normalización o "
        "reconstrucción? DT4-N2 prohíbe reconstruir la evidencia primaria"
    )


def test_utf8_acentos_enie_sin_escape_ascii(tmp_path):
    path = tmp_path / "site_presence_snapshot.json"
    snapshot = _canonical_snapshot()  # site_url con í y ñ

    save_site_presence_snapshot(snapshot, path)

    raw = path.read_text(encoding="utf-8")
    assert "vísperas-ñ" in raw
    assert "\\u00ed" not in raw and "\\u00f1" not in raw  # ensure_ascii=False


def test_ruta_fallo_checker_snapshot_vacio_canonico(tmp_path):
    path = tmp_path / "site_presence_snapshot.json"
    snapshot = normalize_site_presence(None)  # {"results": {}} — ruta de fallo en main.py

    save_site_presence_snapshot(snapshot, path)

    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["snapshot"] == {"results": {}}


def test_snapshot_persistido_alimenta_los_oraculos(tmp_path):
    path = tmp_path / "v4_audit" / "site_presence_snapshot.json"
    save_site_presence_snapshot(_canonical_snapshot(), path)

    snapshot = json.loads(path.read_text(encoding="utf-8"))["snapshot"]

    # Los mismos oráculos que en memoria, ahora leyendo de disco:
    assert _presence_exists(snapshot, "llms_txt")  # exists_with_issues cuenta (H7/L-SR3)
    assert not _presence_exists(snapshot, "whatsapp_button")
    assert _presence_resolved(snapshot, "llms_txt")

    comprometidos = committed_services_from_entries(
        [
            ProposalAssetMatrixEntry(
                service_name="Optimización para IA Generativa",
                pain_ids=[],
                asset_type="llms_txt",
                status="PRESENT_IN_PRODUCTION",
            ),
            ProposalAssetMatrixEntry(
                service_name="Botón de WhatsApp",
                pain_ids=[],
                asset_type="whatsapp_button",
                status="MISSING_ASSET",
            ),
        ],
        snapshot,
    )
    assert comprometidos == ["Optimización para IA Generativa"]
