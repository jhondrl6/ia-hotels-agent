"""
Tests for PainLedger - FASE-0B: Pain Ledger facade.

Tests:
- test_ledger_normalizes_pain_ids
- test_ledger_serializes_reproducibly
- test_ledger_backward_compat_with_pain_ids_resolved
"""

import pytest
import json
import tempfile
from pathlib import Path
from dataclasses import asdict

from modules.commercial_documents.pain_solution_mapper import Pain


class TestPainLedger:
    """Test PainLedger facade."""

    def test_ledger_normalizes_pain_ids(self, tmp_path):
        """Test that pain_ids are normalized to lowercase_underscore."""
        from modules.asset_generation.pain_ledger import PainLedger, PainLedgerEntry

        ledger = PainLedger()

        # Create pains with different id formats
        pains = [
            Pain(
                id="No WhatsApp Visible",  # Title Case
                name="Sin WhatsApp Visible",
                description="No se detecta botón o enlace de WhatsApp",
                severity="high",
                detected_by="validation",
                confidence=0.5
            ),
            Pain(
                id="low_gbp_score",  # Already normalized
                name="Bajo Score GBP",
                description="Google Business Profile con score bajo",
                severity="high",
                detected_by="gbp",
                confidence=0.8
            ),
            Pain(
                id="METADATA_DEFAULTS",  # ALL CAPS
                name="Metadatos por Defecto",
                description="Título y descripción usando valores por defecto del CMS",
                severity="high",
                detected_by="metadata",
                confidence=0.9
            ),
        ]

        entries = ledger.from_pains(pains, source_module="test_module")

        # Verify normalized ids
        assert entries[0].pain_id == "no_whatsapp_visible"
        assert entries[1].pain_id == "low_gbp_score"
        assert entries[2].pain_id == "metadata_defaults"

    def test_ledger_serializes_reproducibly(self, tmp_path):
        """Test that PainLedger serializes to JSON reproducibly."""
        from modules.asset_generation.pain_ledger import PainLedger, PainLedgerEntry

        ledger = PainLedger()

        pains = [
            Pain(
                id="no_whatsapp_visible",
                name="Sin WhatsApp Visible",
                description="No se detecta botón o enlace de WhatsApp",
                severity="high",
                detected_by="validation",
                confidence=0.5
            ),
        ]

        entries = ledger.from_pains(pains, source_module="test_module")

        # Serialize twice
        data1 = ledger.to_dict(entries)
        data2 = ledger.to_dict(entries)

        # Should produce identical JSON strings
        json1 = json.dumps(data1, sort_keys=True, ensure_ascii=False)
        json2 = json.dumps(data2, sort_keys=True, ensure_ascii=False)
        assert json1 == json2

        # Save and reload
        save_path = tmp_path / "pain_ledger.json"
        ledger.save(entries, save_path)

        loaded_entries = ledger.load(save_path)
        assert len(loaded_entries) == 1
        assert loaded_entries[0].pain_id == "no_whatsapp_visible"
        assert loaded_entries[0].source_module == "test_module"

    def test_ledger_backward_compat_with_pain_ids_resolved(self):
        """Test backward compatibility: entries expose pain_ids_resolved list."""
        from modules.asset_generation.pain_ledger import PainLedger, PainLedgerEntry

        ledger = PainLedger()

        pains = [
            Pain(
                id="no_whatsapp_visible",
                name="Sin WhatsApp Visible",
                description="No se detecta botón",
                severity="high",
                detected_by="validation",
                confidence=0.5
            ),
            Pain(
                id="low_gbp_score",
                name="Bajo Score GBP",
                description="Score bajo",
                severity="high",
                detected_by="gbp",
                confidence=0.8
            ),
        ]

        entries = ledger.from_pains(pains, source_module="test_module")

        # Backward compat: each entry should have pain_id (single)
        # and we should be able to extract all pain_ids as a list
        pain_ids_list = [entry.pain_id for entry in entries]

        assert "no_whatsapp_visible" in pain_ids_list
        assert "low_gbp_score" in pain_ids_list

        # Verify entry structure has required fields for backward compat
        for entry in entries:
            assert hasattr(entry, 'pain_id')
            assert hasattr(entry, 'source_module')
            assert hasattr(entry, 'source_file')
            assert hasattr(entry, 'severity')
            assert hasattr(entry, 'confidence')
            assert hasattr(entry, 'status')
            assert hasattr(entry, 'human_label')
            assert hasattr(entry, 'evidence_refs')