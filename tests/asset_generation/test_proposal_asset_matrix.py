"""
Tests for ProposalAssetMatrix — FASE-0D-PROPOSAL-ASSET.

Validates that every service sold in a commercial proposal is:
1. Backed by a real breach (pain_id in ledger)
2. Has a corresponding generated asset (or marked MISSING_ASSET)
"""
import pytest
from pathlib import Path
from tempfile import TemporaryDirectory

from modules.asset_generation.proposal_asset_alignment import (
    ProposalAssetMatrixEntry,
    ProposalAssetMatrix,
    PROPOSAL_SERVICE_TO_ASSET,
)
from modules.asset_generation.pain_ledger import PainLedgerEntry
from modules.asset_generation.v4_asset_orchestrator import GeneratedAsset


# ── Fixtures ──────────────────────────────────────────────────────────

@pytest.fixture
def sample_pain_ledger():
    """Pain ledger with WhatsApp, Schema Hotel, and Schema Org breaches."""
    return [
        PainLedgerEntry(
            pain_id="no_whatsapp_visible",
            source_module="pain_solution_mapper",
            source_file="schema_validator_v2.py",
            severity="HIGH",
            confidence=0.95,
            status="DETECTED",
            human_label="No WhatsApp Visible",
            evidence_refs=["web_scrape_wa_button=false"],
        ),
        PainLedgerEntry(
            pain_id="no_hotel_schema",
            source_module="pain_solution_mapper",
            source_file="schema_validator_v2.py",
            severity="CRITICAL",
            confidence=0.90,
            status="DETECTED",
            human_label="Sin Schema Hotel",
            evidence_refs=["schema_hotel_detected=false"],
        ),
        PainLedgerEntry(
            pain_id="no_org_schema",
            source_module="pain_solution_mapper",
            source_file="schema_validator_v2.py",
            severity="MEDIUM",
            confidence=0.85,
            status="DETECTED",
            human_label="Sin Schema Organization",
            evidence_refs=["org_schema_detected=false"],
        ),
    ]


@pytest.fixture
def sample_generated_assets():
    """Generated assets for WhatsApp button and Hotel Schema, but NOT FAQ."""
    return [
        GeneratedAsset(
            asset_type="whatsapp_button",
            filename="whatsapp_button.html",
            path="/tmp/output/whatsapp_button.html",
            metadata_path="/tmp/output/whatsapp_button_metadata.json",
            preflight_status="PASSED",
            confidence_score=0.95,
            pain_ids_resolved=["no_whatsapp_visible"],
            can_use=True,
            delivery_filename="boton_whatsapp.html",
        ),
        GeneratedAsset(
            asset_type="hotel_schema",
            filename="hotel_schema.json",
            path="/tmp/output/hotel_schema.json",
            metadata_path="/tmp/output/hotel_schema_metadata.json",
            preflight_status="PASSED",
            confidence_score=0.90,
            pain_ids_resolved=["no_hotel_schema"],
            can_use=True,
            delivery_filename="hotel_schema.jsonld",
        ),
    ]


@pytest.fixture
def proposal_services():
    """Services sold in the proposal."""
    return [
        "Botón de WhatsApp",
        "Schema Hotel",
        "Schema Organization",
        "Página de FAQ",  # No asset generated, no pain in ledger
    ]


# ── RED Tests ─────────────────────────────────────────────────────────

class TestProposalAssetMatrixServiceWithoutBreach:
    """RED: test_fails_when_service_sold_without_real_breach"""

    def test_fails_when_service_sold_without_real_breach(
        self, proposal_services, sample_pain_ledger, sample_generated_assets
    ):
        """
        A service sold in the proposal MUST have a corresponding pain/breach
        in the pain ledger. Services without a real breach should be flagged.
        """
        matrix = ProposalAssetMatrix()
        entries = matrix.build(proposal_services, sample_pain_ledger, sample_generated_assets)

        # Find entry for "Página de FAQ" — no pain in ledger for this
        faq_entry = next(
            (e for e in entries if e.service_name == "Página de FAQ"), None
        )
        assert faq_entry is not None, "FAQ service should be in matrix"
        # No faq-related pain in the ledger → NO_BREACH
        assert faq_entry.status == "NO_BREACH", (
            f"Expected NO_BREACH for FAQ (no pain in ledger), got {faq_entry.status}"
        )
        assert faq_entry.pain_ids == [], "Should have no pain_ids"
        assert faq_entry.confidence == 0.0, "Confidence should be 0.0 for NO_BREACH"


class TestProposalAssetMatrixServiceWithoutAsset:
    """RED: test_fails_when_service_sold_without_asset"""

    def test_fails_when_service_sold_without_asset(
        self, proposal_services, sample_pain_ledger, sample_generated_assets
    ):
        """
        A service sold with a real breach but no generated asset
        should be marked MISSING_ASSET.
        """
        # Schema Organization has a breach (no_org_schema) but no generated asset
        matrix = ProposalAssetMatrix()
        entries = matrix.build(proposal_services, sample_pain_ledger, sample_generated_assets)

        org_entry = next(
            (e for e in entries if e.service_name == "Schema Organization"), None
        )
        assert org_entry is not None, "Schema Organization should be in matrix"
        assert org_entry.status == "MISSING_ASSET", (
            f"Expected MISSING_ASSET for Schema Org (breach exists, no asset), "
            f"got {org_entry.status}"
        )
        assert "no_org_schema" in org_entry.pain_ids, "Should link to org schema pain"
        assert org_entry.asset_path is None, "No asset → asset_path should be None"


class TestProposalAssetMatrixServiceLinked:
    """GREEN: test_passes_when_service_present_and_justified"""

    def test_passes_when_service_present_and_justified(
        self, proposal_services, sample_pain_ledger, sample_generated_assets
    ):
        """
        A service with both a real breach AND a generated asset
        should be LINKED with correct metadata.
        """
        matrix = ProposalAssetMatrix()
        entries = matrix.build(proposal_services, sample_pain_ledger, sample_generated_assets)

        # Botón de WhatsApp — breach + asset = LINKED
        wa_entry = next(
            (e for e in entries if e.service_name == "Botón de WhatsApp"), None
        )
        assert wa_entry is not None, "WhatsApp service should be in matrix"
        assert wa_entry.status == "LINKED", (
            f"Expected LINKED for WhatsApp, got {wa_entry.status}"
        )
        assert "no_whatsapp_visible" in wa_entry.pain_ids
        assert wa_entry.asset_type == "whatsapp_button"
        assert wa_entry.asset_path is not None
        assert wa_entry.confidence > 0.8

        # Schema Hotel — breach + asset = LINKED
        hotel_entry = next(
            (e for e in entries if e.service_name == "Schema Hotel"), None
        )
        assert hotel_entry is not None, "Hotel Schema service should be in matrix"
        assert hotel_entry.status == "LINKED"
        assert "no_hotel_schema" in hotel_entry.pain_ids


# ── Serialization Tests ────────────────────────────────────────────────

class TestProposalAssetMatrixSave:
    """Tests for save() functionality."""

    def test_save_writes_valid_json(
        self, proposal_services, sample_pain_ledger, sample_generated_assets
    ):
        """save() should write a valid JSON file with all entries."""
        matrix = ProposalAssetMatrix()
        entries = matrix.build(proposal_services, sample_pain_ledger, sample_generated_assets)

        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "proposal_asset_matrix.json"
            matrix.save(entries, path)

            assert path.exists(), "JSON file should be created"
            import json
            data = json.loads(path.read_text(encoding="utf-8"))

            assert "entries" in data
            assert len(data["entries"]) == len(entries)
            # Verify statuses
            statuses = {e["service_name"]: e["status"] for e in data["entries"]}
            assert statuses["Botón de WhatsApp"] == "LINKED"
            assert statuses["Schema Hotel"] == "LINKED"
            assert statuses["Schema Organization"] == "MISSING_ASSET"
            assert statuses["Página de FAQ"] == "NO_BREACH"


# ── Edge Cases ─────────────────────────────────────────────────────────

class TestProposalAssetMatrixEdgeCases:
    """Edge case tests."""

    def test_empty_services_returns_empty(self):
        """Empty proposal services → empty matrix."""
        matrix = ProposalAssetMatrix()
        entries = matrix.build([], [], [])
        assert entries == []

    def test_unknown_service_is_skipped(self, sample_pain_ledger, sample_generated_assets):
        """Service not in PROPOSAL_SERVICE_TO_ASSET skips gracefully."""
        matrix = ProposalAssetMatrix()
        entries = matrix.build(
            ["Servicio Inexistente"], sample_pain_ledger, sample_generated_assets
        )
        assert len(entries) == 0
