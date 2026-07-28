"""DT4-R1 Integration test: reconciler → builder → assessment → coverage gate.

FASE-1: Verifies end-to-end flow where pain_ledger_resolved is injected
into AssessmentPayload and consumed by _coverage_gate().
"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from modules.orchestration.post_orchestrator_reconciler import (
    PostOrchestratorReconciler,
    PainResolutionStatus,
)
from modules.assessment_builder import AssessmentBuilder
from modules.quality_gates.publication_gates import (
    PublicationGatesOrchestrator,
    PublicationGateConfig,
    GateStatus,
)


def test_resolved_pain_ledger_coverage_gate():
    """Integration: reconciler resolves no_whatsapp_visible → coverage gate PASS."""
    tmp = Path(tempfile.mkdtemp())

    # 1. Mock pain_ledger.json with no_whatsapp_visible as DETECTED
    pain_ledger = {
        "entries": [
            {"pain_id": "no_whatsapp_visible", "status": "DETECTED"},
            {"pain_id": "no_hotel_schema", "status": "DETECTED"},
        ]
    }
    (tmp / "pain_ledger.json").write_text(json.dumps(pain_ledger))

    # 2. Mock asset_generation_report.json with whatsapp_button as skipped (exists)
    asset_report = {
        "generated_assets": [
            {"pain_ids_resolved": ["no_hotel_schema"]},
        ],
        "skipped_assets": [
            {
                "pain_ids_affected": ["no_whatsapp_visible"],
                "presence_status": "exists",
                "asset_name": "whatsapp_button",
                "site_verified": True,
            }
        ],
    }
    (tmp / "asset_generation_report.json").write_text(json.dumps(asset_report))

    # 3. Run reconciler
    reconciler = PostOrchestratorReconciler()
    output_path = tmp / "pain_ledger_resolved.json"
    result = reconciler.reconcile(
        asset_generation_report_path=tmp / "asset_generation_report.json",
        pain_ledger_path=tmp / "pain_ledger.json",
        output_path=output_path,
    )

    assert output_path.exists(), "Reconciler output file must exist"

    # Verify reconciler output: no_whatsapp_visible → MAPPED_TO_SERVICE
    entries = result["entries"]
    whatsapp_entry = next(e for e in entries if e["pain_id"] == "no_whatsapp_visible")
    assert whatsapp_entry["status"] == PainResolutionStatus.MAPPED_TO_SERVICE, (
        f"no_whatsapp_visible should be MAPPED_TO_SERVICE, got {whatsapp_entry['status']}"
    )
    assert result["summary"]["mapped_to_service"] >= 1

    # 4. Build AssessmentPayload via builder with pain_ledger_resolved
    builder = AssessmentBuilder()
    builder.with_core("https://zione.co/", "Zi One Luxury")

    # Set pain_ledger (original entries — for fallback verification)
    builder._payload.pain_ledger = [
        {"pain_id": "no_whatsapp_visible", "status": "DETECTED"},
        {"pain_id": "no_hotel_schema", "status": "DETECTED"},
    ]
    builder._payload.diagnostic_pain_ids = []
    builder._payload.proposal_pain_ids = []

    # Set pain_ledger_resolved (reconciled — the resolved entries list)
    builder._payload.pain_ledger_resolved = result["entries"]

    assessment = builder.build()

    # Verify resolved entries are in the assessment
    assert assessment["pain_ledger_resolved"] is not None
    assert len(assessment["pain_ledger_resolved"]) == 2
    # no_whatsapp_visible → MAPPED_TO_SERVICE (first entry in input)
    assert assessment["pain_ledger_resolved"][0]["status"] == PainResolutionStatus.MAPPED_TO_SERVICE

    # 5. Run coverage gate with resolved assessment
    orchestrator = PublicationGatesOrchestrator(PublicationGateConfig())
    gate_result = orchestrator._coverage_gate(assessment)

    # 6. Verify: PASS, justified >= 1, no_whatsapp_visible NOT in uncovered
    assert gate_result.passed is True, (
        f"Coverage gate should PASS with resolved ledger, got {gate_result.message}"
    )
    assert gate_result.status == GateStatus.PASSED
    assert gate_result.details["justified"] >= 1, (
        f"Expected at least 1 justified pain, got {gate_result.details}"
    )
    assert "no_whatsapp_visible" not in gate_result.details.get("uncovered", []), (
        "no_whatsapp_visible should NOT be in uncovered (resolved to MAPPED_TO_SERVICE)"
    )
    assert gate_result.gate_name == "coverage_no_silent_drop"

    print("test_resolved_pain_ledger_coverage_gate: PASSED")
    print(f"  Details: {gate_result.details}")


def test_resolved_ledger_without_reconciler_falls_back():
    """When pain_ledger_resolved is None (reconciler never ran), coverage gate
    should fallback to pain_ledger and work correctly."""
    builder = AssessmentBuilder()
    builder.with_core("https://example.com", "Test Hotel")
    builder._payload.pain_ledger = [
        {"pain_id": "no_whatsapp_visible", "status": "DETECTED"},
    ]
    builder._payload.diagnostic_pain_ids = ["no_whatsapp_visible"]
    builder._payload.proposal_pain_ids = []
    # pain_ledger_resolved is None (default — reconciler never ran)

    assessment = builder.build()
    assert assessment["pain_ledger_resolved"] is None

    orchestrator = PublicationGatesOrchestrator(PublicationGateConfig())
    gate_result = orchestrator._coverage_gate(assessment)

    # Should fallback to pain_ledger and PASS (pain is in diagnostic)
    assert gate_result.passed is True
    assert gate_result.status == GateStatus.PASSED

    print("test_resolved_ledger_without_reconciler_falls_back: PASSED")


def test_empty_resolved_ledger_blocked():
    """When pain_ledger_resolved is an empty list (reconciler ran but produced
    nothing), coverage gate should BLOCK."""
    builder = AssessmentBuilder()
    builder.with_core("https://example.com", "Test Hotel")
    builder._payload.pain_ledger = [
        {"pain_id": "no_whatsapp_visible", "status": "DETECTED"},
    ]
    builder._payload.diagnostic_pain_ids = []
    builder._payload.proposal_pain_ids = []
    builder._payload.pain_ledger_resolved = []  # Reconciler ran, produced nothing

    assessment = builder.build()

    orchestrator = PublicationGatesOrchestrator(PublicationGateConfig())
    gate_result = orchestrator._coverage_gate(assessment)

    assert gate_result.passed is False
    assert gate_result.status == GateStatus.BLOCKED
    assert "empty after reconciliation" in gate_result.message

    print("test_empty_resolved_ledger_blocked: PASSED")
