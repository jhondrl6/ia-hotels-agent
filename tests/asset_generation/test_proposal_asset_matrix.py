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
        in the pain ledger.

        FASE-C (Punto 8): sin brecha no hay promesa. El servicio ya no se emite
        como entrada NO_BREACH — se excluye y queda DECLARADO en not_promised,
        que es la forma auditable de no prometerlo.
        """
        matrix = ProposalAssetMatrix()
        entries = matrix.build(proposal_services, sample_pain_ledger, sample_generated_assets)

        faq_entry = next(
            (e for e in entries if e.service_name == "Página de FAQ"), None
        )
        assert faq_entry is None, "Sin brecha en el ledger, FAQ no se promete"
        assert "Página de FAQ" in matrix.not_promised, (
            "Lo no prometido debe declararse, no descartarse en silencio"
        )
        # Los que sí tienen brecha siguen en la matriz
        assert {e.service_name for e in entries} == {
            "Botón de WhatsApp", "Schema Hotel", "Schema Organization"
        }


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
            # FASE-C (Punto 8): sin brecha no se promete ⟹ no hay entrada que
            # serializar.
            assert "Página de FAQ" not in statuses


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


# ═══════════════════════════════════════════════════════════════════════════
# FASE-DT-3 FASE-2: Tests para el contrato canónico unificado
# ═══════════════════════════════════════════════════════════════════════════

from modules.asset_generation.proposal_asset_alignment import (
    AssetAlignmentMatrix,
    AlignmentStatus,
)


class TestAssetAlignmentMatrixBuild:
    """Tests para AssetAlignmentMatrix.build() con DeliveryContext."""

    def test_legacy_build_matches_proposal_asset_matrix(
        self, proposal_services, sample_pain_ledger, sample_generated_assets
    ):
        """AssetAlignmentMatrix.build() con generated_assets override produce
        los mismos resultados que ProposalAssetMatrix.build() legacy."""
        from modules.delivery.delivery_context import DeliveryContext
        ctx = DeliveryContext()

        aam = AssetAlignmentMatrix.build(
            delivery_context=ctx,
            pain_ledger=sample_pain_ledger,
            generated_assets=sample_generated_assets,
        )

        # Debe coincidir con el comportamiento legacy
        assert aam.total_services > 0
        wa = aam.get_alignment("Botón de WhatsApp")
        assert wa == AlignmentStatus.LINKED, f"Expected LINKED, got {wa}"
        hotel = aam.get_alignment("Schema Hotel")
        assert hotel == AlignmentStatus.LINKED, f"Expected LINKED, got {hotel}"
        # FASE-C (Punto 8): sin brecha no se promete ⟹ no hay entrada y el
        # lookup no puede inventar un estado.
        faq = aam.get_alignment("Página de FAQ")
        assert faq == AlignmentStatus.INDETERMINATE, f"Expected INDETERMINATE, got {faq}"
        assert "Página de FAQ" in aam.not_promised

        # anti-A5: los DOS builders comparten la partición canónica, así que
        # deben dar exactamente los mismos pares (servicio, estado).
        legacy = ProposalAssetMatrix()
        legacy_entries = legacy.build(
            list(proposal_services), sample_pain_ledger, sample_generated_assets
        )
        assert sorted((e.service_name, e.status) for e in legacy_entries) == \
            sorted((e.service_name, e.status) for e in aam.entries
                   if e.service_name in proposal_services)
        assert sorted(legacy.not_promised) == sorted(
            n for n in aam.not_promised if n in proposal_services
        )

    def test_build_empty_ledger_promises_nothing(
        self, sample_generated_assets
    ):
        """FASE-C: ledger VACÍO = resuelto sin brechas → 0 servicios prometidos.

        Antes este test era vacuamente verde: recorría entradas que ya no
        existen. Ahora fija el contrato (vacío ≠ ausente).
        """
        from modules.delivery.delivery_context import DeliveryContext
        from modules.asset_generation.proposal_asset_alignment import (
            ALL_PROMISED_SERVICES,
        )
        ctx = DeliveryContext()
        aam = AssetAlignmentMatrix.build(
            delivery_context=ctx,
            pain_ledger=[],
            generated_assets=sample_generated_assets,
        )
        assert aam.entries == []
        assert sorted(aam.not_promised) == sorted(ALL_PROMISED_SERVICES)

    def test_build_absent_ledger_keeps_static_catalog(
        self, sample_generated_assets
    ):
        """FASE-C: ledger AUSENTE (None) → modo legacy, catálogo estático con
        NO_BREACH donde no haya pain. No se colapsa con el caso anterior."""
        from modules.delivery.delivery_context import DeliveryContext
        from modules.asset_generation.proposal_asset_alignment import (
            ALL_PROMISED_SERVICES,
        )
        ctx = DeliveryContext()
        aam = AssetAlignmentMatrix.build(
            delivery_context=ctx,
            pain_ledger=None,
            generated_assets=sample_generated_assets,
        )
        assert len(aam.entries) == len(ALL_PROMISED_SERVICES)
        assert aam.not_promised == []
        for entry in aam.entries:
            assert entry.status in ("LINKED", "MISSING_ASSET", "NO_BREACH"), \
                f"{entry.service_name}: estado inesperado {entry.status}"


class TestAssetAlignmentMatrixDeliveryReady:
    """Tests para is_delivery_ready()."""

    def test_empty_matrix_is_ready(self):
        """Matriz vacía → delivery ready (sin servicios accionables)."""
        aam = AssetAlignmentMatrix()
        assert aam.is_delivery_ready() is True

    def test_all_linked_is_ready(self):
        """Todos LINKED → delivery ready."""
        entries = [
            ProposalAssetMatrixEntry("S1", ["p1"], "a1", "/tmp/a1", 0.9, "LINKED"),
            ProposalAssetMatrixEntry("S2", ["p2"], "a2", "/tmp/a2", 0.85, "LINKED"),
        ]
        aam = AssetAlignmentMatrix(entries=entries)
        assert aam.is_delivery_ready() is True

    def test_all_no_breach_is_ready(self):
        """Todos NO_BREACH → delivery ready (ningún servicio accionable)."""
        entries = [
            ProposalAssetMatrixEntry("S1", [], "a1", None, 0.0, "NO_BREACH"),
            ProposalAssetMatrixEntry("S2", [], "a2", None, 0.0, "NO_BREACH"),
        ]
        aam = AssetAlignmentMatrix(entries=entries)
        assert aam.is_delivery_ready() is True

    def test_missing_asset_blocks_delivery(self):
        """MISSING_ASSET presente → NO delivery ready."""
        entries = [
            ProposalAssetMatrixEntry("S1", ["p1"], "a1", "/tmp/a1", 0.9, "LINKED"),
            ProposalAssetMatrixEntry("S2", ["p2"], "a2", None, 0.0, "MISSING_ASSET"),
        ]
        aam = AssetAlignmentMatrix(entries=entries)
        assert aam.is_delivery_ready() is False

    def test_generic_draft_blocks_delivery(self):
        """GENERIC_DRAFT presente → NO delivery ready."""
        entries = [
            ProposalAssetMatrixEntry("S1", ["p1"], "a1", "/tmp/a1", 0.9, "LINKED"),
            ProposalAssetMatrixEntry("S2", ["p2"], "a2", None, 0.0, "GENERIC_DRAFT"),
        ]
        aam = AssetAlignmentMatrix(entries=entries)
        assert aam.is_delivery_ready() is False

    def test_mixed_linked_no_breach_is_ready(self):
        """LINKED + NO_BREACH → delivery ready (NO_BREACH no cuenta)."""
        entries = [
            ProposalAssetMatrixEntry("S1", ["p1"], "a1", "/tmp/a1", 0.9, "LINKED"),
            ProposalAssetMatrixEntry("S2", [], "a2", None, 0.0, "NO_BREACH"),
        ]
        aam = AssetAlignmentMatrix(entries=entries)
        assert aam.is_delivery_ready() is True


class TestAssetAlignmentMatrixGetAlignment:
    """Tests para get_alignment()."""

    def test_known_service_returns_correct_status(self):
        entries = [
            ProposalAssetMatrixEntry("S1", ["p1"], "a1", "/tmp/a1", 0.9, "LINKED"),
        ]
        aam = AssetAlignmentMatrix(entries=entries)
        assert aam.get_alignment("S1") == AlignmentStatus.LINKED

    def test_unknown_service_returns_indeterminate(self):
        aam = AssetAlignmentMatrix()
        assert aam.get_alignment("No Existe") == AlignmentStatus.INDETERMINATE

    def test_all_statuses_map_correctly(self):
        entries = [
            ProposalAssetMatrixEntry("linked", ["p1"], "a1", "/tmp", 0.9, "LINKED"),
            ProposalAssetMatrixEntry("missing", ["p2"], "a2", None, 0.0, "MISSING_ASSET"),
            ProposalAssetMatrixEntry("nobre", [], "a3", None, 0.0, "NO_BREACH"),
            ProposalAssetMatrixEntry("draft", ["p4"], "a4", None, 0.0, "GENERIC_DRAFT"),
        ]
        aam = AssetAlignmentMatrix(entries=entries)
        assert aam.get_alignment("linked") == AlignmentStatus.LINKED
        assert aam.get_alignment("missing") == AlignmentStatus.MISSING_ASSET
        assert aam.get_alignment("nobre") == AlignmentStatus.NO_BREACH
        assert aam.get_alignment("draft") == AlignmentStatus.GENERIC_DRAFT


class TestAssetAlignmentMatrixToDict:
    """Tests para to_dict() y backward compat."""

    def test_empty_matrix_to_dict(self):
        aam = AssetAlignmentMatrix()
        d = aam.to_dict()
        assert d["proposal_asset_matrix_version"] == "2.0"
        assert d["delivery_ready"] is True
        assert d["entries"] == []

    def test_populated_matrix_to_dict_format(self):
        entries = [
            ProposalAssetMatrixEntry("S1", ["p1"], "a1", "/tmp/a1", 0.9, "LINKED"),
        ]
        aam = AssetAlignmentMatrix(entries=entries)
        d = aam.to_dict()
        assert "entries" in d
        assert len(d["entries"]) == 1
        e = d["entries"][0]
        assert e["service_name"] == "S1"
        assert e["status"] == "LINKED"
        assert e["alignment"] == "linked"
        assert "delivery_ready" in d

    def test_to_dict_includes_backward_compat_fields(self):
        """to_dict() debe mantener compatibilidad con consumidores legacy."""
        entries = [
            ProposalAssetMatrixEntry("S1", ["p1"], "a1", "/tmp/a1", 0.9, "LINKED"),
        ]
        aam = AssetAlignmentMatrix(entries=entries)
        d = aam.to_dict()
        # Campos que existían en el formato legacy
        assert "proposal_asset_matrix_version" in d
        assert "entries" in d
        # Cada entry mantiene los campos legacy
        e = d["entries"][0]
        for field in ("service_name", "pain_ids", "asset_type", "asset_path", "confidence", "status"):
            assert field in e, f"Missing legacy field: {field}"
