"""FASE-E (A6) — asset_path deja de ser null para assets generados.

Evidencia del dossier: ``proposal_asset_matrix.json`` v2.0 traía
``{"alignment": "linked", "asset_path": null, "asset_type": "llms_txt", ...}``
— la trazabilidad P6.3 (recomendación vendida → asset específico) no era
verificable desde el artefacto.

Causa raíz: el caller (main.py, ``assets_for_quality``) construía los dicts
de ``generated_assets`` sin la clave ``path``; el builder
``classify_promised_services`` lee ``gen_asset.get("path")`` para LINKED.
Estos tests fijan la cadena con la forma EXACTA que main.py alimenta hoy
(FASE-E añadió ``"path": a.path or None``) y el consumo por el delivery
report (G9) del JSON persistido.
"""

import json
from types import SimpleNamespace

from modules.asset_generation.proposal_asset_alignment import AssetAlignmentMatrix
from modules.quality_gates.delivery_quality_report import DeliveryQualityReportGenerator

_LEDGER_AI_CRAWLER = [{"pain_id": "ai_crawler_blocked", "confidence": 0.9}]


def _generated_llms(path="output/v4_complete/hotelsalentoreal/ASSETS/llms_txt/llms.txt"):
    # Forma EXACTA de los dicts que main.py alimenta como assets_generated
    # desde FASE-E (antes de E solo traía asset_type + confidence_score).
    return [
        {
            "asset_type": "llms_txt",
            "confidence_score": 0.92,
            "path": path,
        }
    ]


def _build(pain_ledger, generated):
    return AssetAlignmentMatrix.build(
        delivery_context=SimpleNamespace(),
        pain_ledger=pain_ledger,
        generated_assets=generated,
        site_presence_report=None,
    )


def test_linked_con_path_poblado():
    matrix = _build(_LEDGER_AI_CRAWLER, _generated_llms())

    entry = next(e for e in matrix.entries if e.asset_type == "llms_txt")
    assert entry.status == "LINKED"
    assert entry.asset_path == _generated_llms()[0]["path"]

    # Lo que se serializa a proposal_asset_matrix.json — el artefacto que
    # audita el Bot 3 del tribunal para verificar P6.3:
    serialized = {e["asset_type"]: e for e in matrix.to_dict()["entries"]}
    assert serialized["llms_txt"]["asset_path"] == entry.asset_path


def test_linked_sin_archivoqueda_null_y_no_inventa():
    matrix = _build(_LEDGER_AI_CRAWLER, _generated_llms(path=None))

    entry = next(e for e in matrix.entries if e.asset_type == "llms_txt")
    assert entry.status == "LINKED"
    assert entry.asset_path is None


def test_missing_asset_ruta_null():
    matrix = _build(_LEDGER_AI_CRAWLER, [])  # brecha mapeada, asset no generado

    entry = next(e for e in matrix.entries if e.asset_type == "llms_txt")
    assert entry.status == "MISSING_ASSET"
    assert entry.asset_path is None


def test_dict_sin_clave_path_no_inventa_ruta():
    generated = [{"asset_type": "llms_txt", "confidence_score": 0.9}]  # forma pre-E
    matrix = _build(_LEDGER_AI_CRAWLER, generated)

    entry = next(e for e in matrix.entries if e.asset_type == "llms_txt")
    assert entry.asset_path is None


def test_delivery_report_consumer_lee_asset_path(tmp_path):
    asset_file = tmp_path / "llms.txt"
    asset_file.write_text("# llms.txt", encoding="utf-8")
    v4_audit = tmp_path / "hotelsalentoreal" / "v4_audit"
    v4_audit.mkdir(parents=True)

    matrix = _build(_LEDGER_AI_CRAWLER, _generated_llms(path=str(asset_file)))
    matrix.save(v4_audit / "proposal_asset_matrix.json")

    report = DeliveryQualityReportGenerator().generate(
        "hotelsalentoreal", v4_audit, site_presence_report=None
    )

    g9 = report.proposal_asset_gate
    assert g9["passed"] is True
    assert g9["total"] == 1 and g9["aligned"] == 1

    persisted = json.loads(
        (v4_audit / "proposal_asset_matrix.json").read_text(encoding="utf-8")
    )
    assert persisted["entries"][0]["asset_path"] == str(asset_file)
