"""Functional test for PostOrchestratorReconciler — FASE-0 DT-4."""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from modules.orchestration.post_orchestrator_reconciler import (
    PostOrchestratorReconciler,
    PainResolutionStatus,
)


def test_reconciler_basic():
    """Test basic reconciliation: generated → ASSET_GENERATED, skipped(exists) → MAPPED_TO_SERVICE."""
    tmp = Path(tempfile.mkdtemp())

    # Mock pain_ledger.json
    pain_ledger = {
        "entries": [
            {"pain_id": "P001", "status": "DETECTED"},
            {"pain_id": "P002", "status": "DIAGNOSED"},
            {"pain_id": "P003", "status": "MAPPED_TO_SERVICE"},
        ]
    }
    (tmp / "pain_ledger.json").write_text(json.dumps(pain_ledger))

    # Mock asset_generation_report.json
    asset_report = {
        "generated_assets": [
            {"pain_ids_resolved": ["P001"]},
        ],
        "skipped_assets": [
            {
                "pain_ids_affected": ["P002"],
                "presence_status": "exists",
                "asset_name": "wa_button",
                "site_verified": True,
            }
        ],
    }
    (tmp / "asset_generation_report.json").write_text(json.dumps(asset_report))

    # Run reconciler
    reconciler = PostOrchestratorReconciler()
    output_path = tmp / "pain_ledger_resolved.json"
    result = reconciler.reconcile(
        asset_generation_report_path=tmp / "asset_generation_report.json",
        pain_ledger_path=tmp / "pain_ledger.json",
        output_path=output_path,
    )

    # Verify
    entries = result["entries"]
    assert entries[0]["status"] == PainResolutionStatus.ASSET_GENERATED, (
        f"P001 should be ASSET_GENERATED, got {entries[0]['status']}"
    )
    assert entries[1]["status"] == PainResolutionStatus.MAPPED_TO_SERVICE, (
        f"P002 should be MAPPED_TO_SERVICE, got {entries[1]['status']}"
    )
    assert entries[2]["status"] == "MAPPED_TO_SERVICE", (
        f"P003 should stay MAPPED_TO_SERVICE, got {entries[2]['status']}"
    )
    assert result["summary"]["asset_generated"] == 1
    assert result["summary"]["mapped_to_service"] == 2  # P002 (resolved) + P003 (preexisting)
    assert result["summary"]["justified_skip"] == 0

    # Verify output file
    assert output_path.exists()
    loaded = json.loads(output_path.read_text())
    assert loaded == result

    print("test_reconciler_basic: PASSED")
    print(f"  Summary: {result['summary']}")


def test_reconciler_redundant():
    """Test skipped with presence=redundant → JUSTIFIED_SKIP."""
    tmp = Path(tempfile.mkdtemp())

    pain_ledger = {
        "entries": [
            {"pain_id": "P004", "status": "DETECTED"},
        ]
    }
    (tmp / "pain_ledger.json").write_text(json.dumps(pain_ledger))

    asset_report = {
        "generated_assets": [],
        "skipped_assets": [
            {
                "pain_ids_affected": ["P004"],
                "presence_status": "redundant",
                "asset_name": "booking_engine",
                "site_verified": True,
            }
        ],
    }
    (tmp / "asset_generation_report.json").write_text(json.dumps(asset_report))

    reconciler = PostOrchestratorReconciler()
    output_path = tmp / "pain_ledger_resolved.json"
    result = reconciler.reconcile(
        asset_generation_report_path=tmp / "asset_generation_report.json",
        pain_ledger_path=tmp / "pain_ledger.json",
        output_path=output_path,
    )

    entries = result["entries"]
    assert entries[0]["status"] == PainResolutionStatus.JUSTIFIED_SKIP, (
        f"P004 should be JUSTIFIED_SKIP, got {entries[0]['status']}"
    )
    assert result["summary"]["justified_skip"] == 1
    print("test_reconciler_redundant: PASSED")


def test_reconciler_missing_files():
    """Test graceful handling of missing input files."""
    tmp = Path(tempfile.mkdtemp())

    reconciler = PostOrchestratorReconciler()
    output_path = tmp / "pain_ledger_resolved.json"
    result = reconciler.reconcile(
        asset_generation_report_path=tmp / "nonexistent.json",
        pain_ledger_path=tmp / "also_nonexistent.json",
        output_path=output_path,
    )

    # Should return empty result
    assert result["entries"] == []
    assert result["summary"]["total"] == 0
    assert output_path.exists()
    print("test_reconciler_missing_files: PASSED")


if __name__ == "__main__":
    test_reconciler_basic()
    test_reconciler_redundant()
    test_reconciler_missing_files()
    print("\nALL TESTS PASSED")
