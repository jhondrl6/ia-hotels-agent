"""Tests de contrato F13 — Propagación de site_verification (FASE-P1-D).

La verificación del sitio vivo ya existía y la consumían el asset layer
(skip) y el gate ("verified in production"), pero NO el pain_ledger ni el
diagnóstico. Estos contratos verifican la propagación completa:

- C1: site_verification confirma el asset → entrada del ledger pasa de
      DETECTED (HIGH) a VERIFIED_IN_SITE (LOW).
- C2: El reconciler preserva VERIFIED_IN_SITE (no lo degrada).
- C3: El coverage gate cuenta VERIFIED_IN_SITE como justificado
      (cubiertas + justificadas == detectadas sigue cuadrando).
- C4: El diagnóstico no reporta como brecha abierta un pain verificado
      en producción.
"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from modules.asset_generation.pain_ledger import PainLedger, PainLedgerEntry
from modules.orchestration.post_orchestrator_reconciler import (
    PostOrchestratorReconciler,
)
from modules.quality_gates.publication_gates import (
    PublicationGatesOrchestrator,
    PublicationGateConfig,
)


def _entry(pain_id: str, status: str = "DETECTED", severity: str = "HIGH"):
    return PainLedgerEntry(
        pain_id=pain_id,
        source_module="pain_solution_mapper",
        source_file="validation",
        severity=severity,
        confidence=0.3,
        status=status,
        human_label="Test",
    )


def _presence(status: str, site_verified: bool = True):
    """Dict canónico en la forma que produce normalize_site_presence()."""
    return {
        "results": {
            "whatsapp_button": {
                "status": status,
                "site_verified": site_verified,
                "confidence": 0.85,
            }
        }
    }


# ─── C1: PainLedger.apply_site_verification ─────────────────────────────────

def test_verified_asset_moves_pain_to_verified_in_site():
    """no_whatsapp_visible DETECTED HIGH + botón existente → VERIFIED_IN_SITE LOW."""
    ledger = PainLedger()
    entries = [_entry("no_whatsapp_visible")]
    result = ledger.apply_site_verification(entries, _presence("exists"))
    assert result[0].status == "VERIFIED_IN_SITE"
    assert result[0].severity == "LOW", "La brecha verificada no sigue siendo HIGH"
    assert any("site_verification" in ref for ref in result[0].evidence_refs)


def test_not_exists_keeps_detected():
    ledger = PainLedger()
    entries = [_entry("no_whatsapp_visible")]
    result = ledger.apply_site_verification(entries, _presence("not_exists", False))
    assert result[0].status == "DETECTED"
    assert result[0].severity == "HIGH"


def test_exists_with_issues_keeps_detected():
    """Existe pero con problemas → el pain sigue abierto (los problemas son reales)."""
    ledger = PainLedger()
    entries = [_entry("no_whatsapp_visible")]
    result = ledger.apply_site_verification(
        entries, _presence("exists_with_issues", True)
    )
    assert result[0].status == "DETECTED"


def test_redundant_delivery_also_verified():
    ledger = PainLedger()
    entries = [_entry("no_whatsapp_visible")]
    result = ledger.apply_site_verification(entries, _presence("redundant"))
    assert result[0].status == "VERIFIED_IN_SITE"


def test_unmapped_pain_not_touched():
    """Pains sin asset de presencia mapeable (ej: low_gbp_score) no cambian."""
    ledger = PainLedger()
    entries = [_entry("low_gbp_score")]
    result = ledger.apply_site_verification(entries, _presence("exists"))
    assert result[0].status == "DETECTED"


def test_empty_presence_report_is_noop():
    ledger = PainLedger()
    entries = [_entry("no_whatsapp_visible")]
    assert ledger.apply_site_verification(entries, None)[0].status == "DETECTED"
    assert ledger.apply_site_verification(entries, {})[0].status == "DETECTED"


# ─── C2: Reconciler preserva VERIFIED_IN_SITE ───────────────────────────────

def test_reconciler_preserves_verified_in_site():
    tmp = Path(tempfile.mkdtemp())
    pain_ledger = {
        "entries": [
            {"pain_id": "no_whatsapp_visible", "status": "VERIFIED_IN_SITE"},
        ]
    }
    (tmp / "pain_ledger.json").write_text(json.dumps(pain_ledger), encoding="utf-8")
    asset_report = {
        "generated_assets": [],
        "skipped_assets": [
            {
                "pain_ids_affected": ["no_whatsapp_visible"],
                "presence_status": "exists",
                "asset_name": "whatsapp_button",
                "site_verified": True,
            }
        ],
    }
    (tmp / "asset_generation_report.json").write_text(
        json.dumps(asset_report), encoding="utf-8"
    )

    reconciler = PostOrchestratorReconciler()
    result = reconciler.reconcile(
        asset_generation_report_path=tmp / "asset_generation_report.json",
        pain_ledger_path=tmp / "pain_ledger.json",
        output_path=tmp / "pain_ledger_resolved.json",
    )
    assert result["entries"][0]["status"] == "VERIFIED_IN_SITE", (
        "El reconciler no debe degradar VERIFIED_IN_SITE a MAPPED_TO_SERVICE"
    )


# ─── C3: Coverage gate — VERIFIED_IN_SITE justifica el pain ─────────────────

def test_coverage_gate_counts_verified_in_site_as_justified():
    orchestrator = PublicationGatesOrchestrator(PublicationGateConfig())
    assessment = {
        "pain_ledger": [
            {"pain_id": "no_whatsapp_visible", "status": "VERIFIED_IN_SITE"},
        ],
        # El diagnóstico YA NO lo reporta (F13) — no está en los documentos
        "diagnostic_pain_ids": [],
        "proposal_pain_ids": [],
    }
    gate = orchestrator._coverage_gate(assessment)
    assert gate.passed is True, f"Gate debe pasar: {gate.message}"
    assert "no_whatsapp_visible" not in gate.details.get("uncovered", []), (
        "VERIFIED_IN_SITE no puede caer en uncovered (cobradas+justificadas==detectadas)"
    )
    assert gate.details["justified"] >= 1


# ─── C4: Diagnóstico filtra brechas verificadas en producción ───────────────

def test_diagnostic_loads_verified_pain_ids_from_ledger():
    from modules.commercial_documents.v4_diagnostic_generator import (
        V4DiagnosticGenerator,
    )

    tmp = Path(tempfile.mkdtemp())
    v4_audit = tmp / "v4_audit"
    v4_audit.mkdir()
    ledger_data = {
        "entries": [
            {"pain_id": "no_whatsapp_visible", "status": "VERIFIED_IN_SITE"},
            {"pain_id": "no_hotel_schema", "status": "DETECTED"},
        ]
    }
    (v4_audit / "pain_ledger.json").write_text(
        json.dumps(ledger_data), encoding="utf-8"
    )

    gen = V4DiagnosticGenerator()
    verified = gen._load_verified_in_site_pain_ids(str(tmp))
    assert verified == frozenset({"no_whatsapp_visible"})


def test_diagnostic_load_verified_empty_when_no_files():
    from modules.commercial_documents.v4_diagnostic_generator import (
        V4DiagnosticGenerator,
    )

    tmp = Path(tempfile.mkdtemp())
    gen = V4DiagnosticGenerator()
    assert gen._load_verified_in_site_pain_ids(str(tmp)) == frozenset()


def test_identify_brechas_excludes_verified_in_site_pains():
    """_identify_brechas excluye pains VERIFIED_IN_SITE (F13)."""
    from modules.commercial_documents.v4_diagnostic_generator import (
        V4DiagnosticGenerator,
    )
    from modules.commercial_documents.pain_solution_mapper import Pain

    gen = V4DiagnosticGenerator()
    gen._region = "eje_cafetero"
    gen._verified_in_site_pain_ids = frozenset({"no_whatsapp_visible"})

    detected = [
        Pain(id="no_whatsapp_visible", name="Sin WhatsApp Visible",
             description="d", severity="high", detected_by="validation",
             confidence=0.3),
        Pain(id="no_hotel_schema", name="Sin Schema Hotel",
             description="d", severity="high", detected_by="schema",
             confidence=1.0),
    ]

    class _FakeMapper:
        def detect_pains(self, **kwargs):
            return detected

    import modules.commercial_documents.v4_diagnostic_generator as gen_mod
    original_mapper = gen_mod.PainSolutionMapper
    gen_mod.PainSolutionMapper = _FakeMapper
    try:
        brechas = gen._identify_brechas(
            audit_result=object(),  # no-None para pasar el guard
            validation_summary=object(),
            analytics_data=None,
            whatsapp_html_detected=False,
        )
    finally:
        gen_mod.PainSolutionMapper = original_mapper

    pain_ids = [b["pain_id"] for b in brechas]
    assert "no_whatsapp_visible" not in pain_ids, (
        "Brecha verificada en producción no puede aparecer como abierta"
    )
    assert "no_hotel_schema" in pain_ids
