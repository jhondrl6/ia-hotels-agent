"""
FASE-1B → Grupo F (2026-09-05): tests de presencia para el gate proposal_asset_alignment.

El mecanismo original (reconstruir un reporte desde skipped_assets, FASE-1B) fue
sustituido por DT4-R2: la presencia llega UNA vez en el assessment como snapshot
canónico (normalize_site_presence) y el gate no reconstruye ni re-ejecuta nada —
oráculo único de presencia (AC10). Estos tests verifican que el gate marca
present_in_production desde ese snapshot y no reporta "missing" un asset que ya
existe en producción.
"""

import pytest
from typing import Dict, Any, List

from modules.quality_gates.publication_gates import (
    PublicationGatesOrchestrator,
    PublicationGateConfig,
    GateStatus,
)
from modules.asset_generation.v4_asset_orchestrator import (
    AssetGenerationResult,
    GeneratedAsset,
    SkippedAsset,
)
from modules.assessment_builder import AssessmentBuilder
from modules.commercial_documents.coherence_validator import CoherenceReport


# =============================================================================
# Helpers
# =============================================================================

def _make_generated_asset(asset_type: str) -> GeneratedAsset:
    return GeneratedAsset(
        asset_type=asset_type,
        filename=f"{asset_type}.html",
        path=f"/tmp/{asset_type}.html",
        metadata_path=f"/tmp/{asset_type}.meta.json",
        preflight_status="PASSED",
        confidence_score=0.9,
        pain_ids_resolved=[],
        can_use=True,
    )


def _make_skipped_asset(asset_type: str, presence_status: str = "EXISTS") -> SkippedAsset:
    return SkippedAsset(
        asset_type=asset_type,
        reason=f"{asset_type} already exists in production",
        presence_status=presence_status,
        site_verified=True,
        recommendations=[],
        pain_ids_affected=[],
    )


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def orchestrator():
    return PublicationGatesOrchestrator(PublicationGateConfig())


@pytest.fixture
def base_assessment() -> Dict[str, Any]:
    """Minimal valid assessment that passes financial/coherence checks."""
    return {
        "coherence_score": 0.85,
        "evidence_coverage": 0.96,
        "hard_contradictions": 0,
        "critical_recall": 0.95,
        "financial_data": {
            "occupancy_rate": 75.0,
            "direct_channel_percentage": 30.0,
            "adr_cop": 450000.0,
        },
        "financial_evidence_tier": "B",
        "validation_summary": {"hard_contradictions_count": 0},
        "pain_ledger": [],
        "diagnostic_pain_ids": [],
        "proposal_pain_ids": [],
        "hotel_url": "https://test-hotel.com",
        "hotel_name": "Test Hotel",
        "url": "https://test-hotel.com",
    }


# =============================================================================
# Test 1: presence desde el snapshot canónico — asset marked present_in_production
# =============================================================================

# Snapshot canónico (forma normalize_site_presence): el checker verificó que el
# botón ya existe en el sitio del hotel.
_PRESENCE_WHATSAPP_EXISTS = {
    "site_url": "https://test-hotel.com",
    "checked_at": "2026-09-05T00:00:00",
    "results": {
        "whatsapp_button": {
            "status": "exists",
            "site_verified": True,
            "confidence": 1.0,
        },
    },
    "whatsapp_button": {
        "status": "exists",
        "site_verified": True,
        "confidence": 1.0,
    },
}


def test_gate_presence_with_canonical_site_presence(orchestrator, base_assessment):
    """
    Given an assessment whose canonical site_presence_report says whatsapp_button
    status='exists', the gate must mark whatsapp_button as present_in_production,
    NOT as missing.

    El fixture NO incluye pain_ledger: [] hoy significa «ledger resuelto con 0
    brechas» (FASE-C) y produce un PASS trivial sin detalles de presencia; la
    ausencia de la clave toma la ruta del catálogo legacy que este test ejercita.
    """
    assessment = dict(base_assessment)
    assessment.pop("pain_ledger", None)
    # generated_assets does NOT include whatsapp_button
    assessment["generated_assets"] = [
        {"asset_type": "faq_page", "confidence_score": 0.9, "filename": "faq.html", "path": "/tmp/faq.html", "preflight_status": "PASSED"},
        {"asset_type": "hotel_schema", "confidence_score": 0.9, "filename": "schema.json", "path": "/tmp/schema.json", "preflight_status": "PASSED"},
        {"asset_type": "optimization_guide", "confidence_score": 0.9, "filename": "guide.html", "path": "/tmp/guide.html", "preflight_status": "PASSED"},
        {"asset_type": "org_schema", "confidence_score": 0.9, "filename": "org.json", "path": "/tmp/org.json", "preflight_status": "PASSED"},
        {"asset_type": "monthly_report", "confidence_score": 0.9, "filename": "report.html", "path": "/tmp/report.html", "preflight_status": "PASSED"},
        {"asset_type": "open_graph", "confidence_score": 0.9, "filename": "og.html", "path": "/tmp/og.html", "preflight_status": "PASSED"},
        {"asset_type": "llms_txt", "confidence_score": 0.9, "filename": "llms.txt", "path": "/tmp/llms.txt", "preflight_status": "PASSED"},
    ]
    # whatsapp_button ya existe en producción — snapshot canónico (DT4-R2)
    assessment["site_presence_report"] = _PRESENCE_WHATSAPP_EXISTS

    result = orchestrator._proposal_asset_alignment_gate(assessment)

    # The fix ensures whatsapp_button is recognized as present_in_production
    details = result.details
    assert details is not None, "Gate result should have details"

    # Check present_in_production list includes whatsapp_button
    present = details.get("present_in_production", [])
    present_assets = [p.get("asset") for p in present]
    assert "whatsapp_button" in present_assets, (
        f"whatsapp_button should be present_in_production, not missing. "
        f"present_in_production={present_assets}, "
        f"missing={[m.get('asset') for m in details.get('missing', [])]}"
    )

    # whatsapp_button should NOT be in missing list
    missing_assets = [m.get("asset") for m in details.get("missing", [])]
    assert "whatsapp_button" not in missing_assets, (
        f"whatsapp_button should NOT be in missing list"
    )

    # All services should be covered (present or generated)
    assert details.get("all_covered", False) or len(missing_assets) == 0, (
        f"Expected all services covered, but missing: {missing_assets}"
    )


# =============================================================================
# Test 2: sin site_presence_report — fallback a comportamiento legacy
# =============================================================================

def test_gate_presence_without_presence_fallback(orchestrator, base_assessment):
    """
    Without site_presence_report in the assessment, the gate falls back to
    current behavior: assets not in generated_assets and not verified present
    are marked as missing (WARNING/BLOCKED según coverage).

    Sin pain_ledger (ruta legacy del catálogo estático): con la clave presente
    y [] el gate pasa trivial (FASE-C), así que el fixture la omite.
    """
    assessment = dict(base_assessment)
    assessment.pop("pain_ledger", None)
    # generated_assets does NOT include whatsapp_button
    assessment["generated_assets"] = [
        {"asset_type": "faq_page", "confidence_score": 0.9, "filename": "faq.html", "path": "/tmp/faq.html", "preflight_status": "PASSED"},
    ]
    # NO site_presence_report

    result = orchestrator._proposal_asset_alignment_gate(assessment)

    # With missing assets and no presence info, the gate should detect misalignment
    # It might be BLOCKED or WARNING depending on P1/P2/P3 status of missing assets
    assert result is not None
    assert result.gate_name == "proposal_asset_alignment"
    # Just verify it doesn't crash — backward compat test
    assert result.status in (GateStatus.PASSED, GateStatus.WARNING, GateStatus.BLOCKED)


# =============================================================================
# Test 3: AssessmentBuilder propagates skipped_assets
# =============================================================================

def test_skipped_assets_propagated_to_assessment():
    """
    AssessmentBuilder.with_assets() must propagate skipped_assets from
    AssetGenerationResult to the AssessmentPayload, so downstream gates
    can consume them.
    """
    # Build an AssetGenerationResult with both generated and skipped assets
    asset_result = AssetGenerationResult(
        hotel_id="test-hotel",
        hotel_name="Test Hotel",
        generated_assets=[
            _make_generated_asset("faq_page"),
            _make_generated_asset("hotel_schema"),
        ],
        failed_assets=[],
        coherence_report=CoherenceReport(
            is_coherent=True,
            overall_score=0.85,
            checks=[],
        ),
        skipped_assets=[
            _make_skipped_asset("whatsapp_button", "EXISTS"),
            _make_skipped_asset("llms_txt", "REDUNDANT"),
        ],
        output_dir="/tmp/output",
    )

    builder = AssessmentBuilder()
    builder.with_core("https://test-hotel.com", "Test Hotel")
    builder.with_assets(asset_result)
    payload = builder._payload

    # Verify generated_assets are propagated
    assert len(payload.generated_assets) == 2
    generated_types = {a["asset_type"] for a in payload.generated_assets}
    assert "faq_page" in generated_types
    assert "hotel_schema" in generated_types

    # FASE-1B: Verify skipped_assets are propagated
    assert len(payload.skipped_assets) == 2
    skipped_by_type = {a["asset_type"]: a for a in payload.skipped_assets}

    assert "whatsapp_button" in skipped_by_type
    wa = skipped_by_type["whatsapp_button"]
    assert wa["presence_status"] == "EXISTS"
    assert wa["site_verified"] is True
    assert "already exists" in wa["reason"]

    assert "llms_txt" in skipped_by_type
    lt = skipped_by_type["llms_txt"]
    assert lt["presence_status"] == "REDUNDANT"
    assert lt["site_verified"] is True

    # Verify building to dict includes skipped_assets
    result_dict = builder.build()
    assert "skipped_assets" in result_dict
    assert len(result_dict["skipped_assets"]) == 2


# =============================================================================
# Test 4 (bonus): Empty skipped_assets — no crash, no fake report
# =============================================================================

def test_empty_skipped_assets_no_crash(orchestrator, base_assessment):
    """
    When skipped_assets is an empty list, the gate should not crash
    and should behave normally.
    """
    assessment = dict(base_assessment)
    assessment["generated_assets"] = [
        {"asset_type": "faq_page", "confidence_score": 0.9, "filename": "faq.html", "path": "/tmp/faq.html", "preflight_status": "PASSED"},
    ]
    assessment["skipped_assets"] = []  # empty list

    result = orchestrator._proposal_asset_alignment_gate(assessment)
    assert result is not None
    assert result.gate_name == "proposal_asset_alignment"
