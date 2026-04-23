"""
Tests for FASE-CAUSAL: Dynamic proposal generation based on detected pains.

Verifies that V4ProposalGenerator._generate_asset_quality_table() and
_generate_dynamic_services_table() filter services based ONLY on detected pains,
rather than showing all 7 services unconditionally.

Created by FASE-CAUSAL-VALIDATE.
"""

import pytest
from unittest.mock import MagicMock, patch
from modules.commercial_documents.v4_proposal_generator import V4ProposalGenerator
from modules.commercial_documents.service_catalog import SERVICE_CATALOG


class TestProposalDynamicFiltering:
    """Verify dynamic filtering: only services for detected pains appear."""

    def setup_method(self):
        """Create generator instance."""
        self.gen = V4ProposalGenerator()

    def test_asset_quality_table_filters_by_detected_pains_only(self):
        """Table should only show services whose pain_id was detected."""
        # Detect only 2 pains: low_gbp_score and no_whatsapp_visible
        detected_pain_ids = ["low_gbp_score", "no_whatsapp_visible"]

        # Call with empty assets_generated (all would be "Pendiente" if shown)
        result = self.gen._generate_asset_quality_table(
            assets_generated=[],
            detected_pain_ids=detected_pain_ids,
        )

        lines = result.strip().split("\n")

        # Should have header + separator + 2 data rows = 4 lines
        assert len(lines) == 4, f"Expected 4 lines (header+sep+2 rows), got {len(lines)}: {lines}"

        # Extract service names from table rows
        service_rows = [l for l in lines if l.startswith("| ") and "Entregable" not in l and "---" not in l]
        service_names = []
        for row in service_rows:
            parts = row.split("|")
            if len(parts) >= 2:
                service_names.append(parts[1].strip())

        # Should only have 2 services
        assert len(service_names) == 2, f"Expected 2 services, got {len(service_names)}: {service_names}"

        # Verify the exact services that SHOULD appear
        assert "Google Maps Optimizado" in service_names
        assert "Botón de WhatsApp" in service_names

        # Verify services that should NOT appear
        all_service_names = [entry.service_name for entry in SERVICE_CATALOG.values()]
        for svc in all_service_names:
            if svc not in service_names:
                # This service's pain was NOT detected — it should NOT appear
                pass

        # Explicitly verify 5 services that should NOT appear
        should_not_appear = [
            "SEO Local",                  # pain: poor_performance
            "Datos Estructurados",       # pain: no_hotel_schema
            "Página de FAQ",             # pain: no_faq_schema
            "Meta Tags Sociales (Open Graph)",  # pain: no_og_tags
            "Barra de Reserva Móvil",    # pain: no_motor_reservas
        ]
        for svc in should_not_appear:
            assert svc not in service_names, f"Service '{svc}' should NOT appear but did"

    def test_asset_quality_table_empty_pains_shows_all_static(self):
        """With no detected pains, should fall back to PROPOSAL_SERVICE_TO_ASSET (backwards compat)."""
        # Empty list = backwards-compat mode
        result = self.gen._generate_asset_quality_table(
            assets_generated=[],
            detected_pain_ids=[],
        )

        lines = result.strip().split("\n")
        service_rows = [l for l in lines if l.startswith("| ") and "Entregable" not in l]

        # Should have 7 services (static mode)
        assert len(service_rows) == 7, f"Backwards compat should show 7 services, got {len(service_rows)}"

    def test_asset_quality_table_none_pains_shows_all_static(self):
        """With detected_pain_ids=None, should fall back to static (backwards compat)."""
        result = self.gen._generate_asset_quality_table(
            assets_generated=[],
            detected_pain_ids=None,
        )

        lines = result.strip().split("\n")
        service_rows = [l for l in lines if l.startswith("| ") and "Entregable" not in l]

        # Should have 7 services
        assert len(service_rows) == 7, f"None pains should show 7 services, got {len(service_rows)}"

    def test_dynamic_services_table_filters_by_detected_pains(self):
        """_generate_dynamic_services_table should only show services for detected pains."""
        detected_pain_ids = ["no_og_tags", "no_motor_reservas"]

        result = self.gen._generate_dynamic_services_table(detected_pain_ids=detected_pain_ids)

        lines = result.strip().split("\n")

        # Should have header + separator + 2 data rows = 4 lines
        assert len(lines) == 4, f"Expected 4 lines, got {len(lines)}: {lines}"

        # Verify the 2 services that SHOULD appear
        assert "Meta Tags Sociales (Open Graph)" in result
        assert "Barra de Reserva Móvil" in result

        # Verify 5 services that should NOT appear
        should_not_appear = [
            "Google Maps Optimizado",
            "SEO Local",
            "Botón de WhatsApp",
            "Datos Estructurados",
            "Página de FAQ",
        ]
        for svc in should_not_appear:
            assert svc not in result, f"Service '{svc}' should NOT appear but did"

    def test_dynamic_services_table_no_pains_returns_empty(self):
        """With no detected pains, dynamic table returns empty string (awaiting diagnostic)."""
        result = self.gen._generate_dynamic_services_table(detected_pain_ids=[])

        # When no pains detected, function returns empty string
        # (signals "awaiting diagnostic data" downstream)
        assert result == "", f"Expected empty string when no pains, got: {result!r}"

    def test_single_pain_detected_shows_single_service(self):
        """With exactly 1 pain detected, only 1 service should appear."""
        detected_pain_ids = ["no_whatsapp_visible"]

        result = self.gen._generate_asset_quality_table(
            assets_generated=[],
            detected_pain_ids=detected_pain_ids,
        )

        lines = result.strip().split("\n")
        service_rows = [l for l in lines if l.startswith("| ") and "Entregable" not in l]

        assert len(service_rows) == 1, f"Expected 1 service, got {len(service_rows)}"
        assert "Botón de WhatsApp" in result

    def test_all_7_pains_detected_shows_all_7_services(self):
        """If all 7 pains are detected, all 7 services should appear."""
        all_pain_ids = list(set(entry.pain_id for entry in SERVICE_CATALOG.values()))

        result = self.gen._generate_asset_quality_table(
            assets_generated=[],
            detected_pain_ids=all_pain_ids,
        )

        lines = result.strip().split("\n")
        service_rows = [l for l in lines if l.startswith("| ") and "Entregable" not in l]

        assert len(service_rows) == 7, f"Expected 7 services, got {len(service_rows)}"

        # Verify all 7 service names appear
        for entry in SERVICE_CATALOG.values():
            assert entry.service_name in result, f"Service '{entry.service_name}' should appear but didn't"


class TestServiceCatalogConsistency:
    """Verify SERVICE_CATALOG has correct mappings."""

    def test_all_catalog_entries_have_valid_pain_id(self):
        """Every SERVICE_CATALOG entry must have a non-empty pain_id."""
        for key, entry in SERVICE_CATALOG.items():
            assert entry.pain_id, f"Entry '{key}' has empty pain_id"
            assert isinstance(entry.pain_id, str), f"Entry '{key}' pain_id is not string"
            assert entry.pain_id.startswith("no_") or "_" in entry.pain_id, \
                f"Entry '{key}' has suspicious pain_id: {entry.pain_id}"

    def test_all_catalog_entries_have_valid_asset_type(self):
        """Every SERVICE_CATALOG entry must have a non-empty asset_type."""
        for key, entry in SERVICE_CATALOG.items():
            assert entry.asset_type, f"Entry '{key}' has empty asset_type"
            assert isinstance(entry.asset_type, str), f"Entry '{key}' asset_type is not string"

    def test_service_catalog_has_7_entries(self):
        """SERVICE_CATALOG should have exactly 7 entries (one per vendible service)."""
        assert len(SERVICE_CATALOG) == 7, f"Expected 7 entries, got {len(SERVICE_CATALOG)}"

    def test_pain_ids_are_unique_in_catalog(self):
        """Each pain_id should map to exactly one service (no duplicates)."""
        pain_ids = [entry.pain_id for entry in SERVICE_CATALOG.values()]
        unique_pain_ids = set(pain_ids)
        assert len(pain_ids) == len(unique_pain_ids), \
            f"Duplicate pain_ids found: {[p for p in pain_ids if pain_ids.count(p) > 1]}"


class TestBackwardsCompatibility:
    """Verify backwards compatibility with existing gates/assumptions."""

    def test_proposal_service_to_asset_still_present(self):
        """PROPOSAL_SERVICE_TO_ASSET must still exist for gate compatibility."""
        from modules.asset_generation.proposal_asset_alignment import PROPOSAL_SERVICE_TO_ASSET
        assert PROPOSAL_SERVICE_TO_ASSET, "PROPOSAL_SERVICE_TO_ASSET must exist for backwards compat"
        assert len(PROPOSAL_SERVICE_TO_ASSET) == 7, f"Expected 7 entries, got {len(PROPOSAL_SERVICE_TO_ASSET)}"

    def test_service_to_asset_lookup_exists(self):
        """SERVICE_TO_ASSET_LOOKUP should exist and have 7 entries."""
        from modules.commercial_documents.service_catalog import SERVICE_TO_ASSET_LOOKUP
        assert SERVICE_TO_ASSET_LOOKUP, "SERVICE_TO_ASSET_LOOKUP must exist"
        assert len(SERVICE_TO_ASSET_LOOKUP) == 7, f"Expected 7 entries, got {len(SERVICE_TO_ASSET_LOOKUP)}"

    def test_all_service_catalog_services_have_lookup_entry(self):
        """Every SERVICE_CATALOG service should have an entry in SERVICE_TO_ASSET_LOOKUP."""
        from modules.commercial_documents.service_catalog import SERVICE_CATALOG, SERVICE_TO_ASSET_LOOKUP
        for key, entry in SERVICE_CATALOG.items():
            assert entry.service_name in SERVICE_TO_ASSET_LOOKUP, \
                f"Service '{entry.service_name}' from SERVICE_CATALOG has no lookup in SERVICE_TO_ASSET_LOOKUP"
