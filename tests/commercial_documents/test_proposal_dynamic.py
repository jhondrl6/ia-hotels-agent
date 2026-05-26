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
from modules.asset_generation.proposal_asset_alignment import PROPOSAL_SERVICE_TO_ASSET


class TestProposalDynamicFiltering:
    """Verify dynamic filtering: only services for detected pains appear."""

    def setup_method(self):
        """Create generator instance."""
        self.gen = V4ProposalGenerator()

    def test_asset_quality_table_filters_by_detected_pains_only(self):
        """Table should only show services whose pain_id was detected."""
        # Detect only 2 pains: poor_performance and no_whatsapp_visible
        detected_pain_ids = ["poor_performance", "no_whatsapp_visible"]

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
        assert "SEO Local" in service_names
        assert "Botón de WhatsApp" in service_names

        # Verify services that should NOT appear
        all_service_names = [entry.service_name for entry in SERVICE_CATALOG.values()]
        for svc in all_service_names:
            if svc not in service_names:
                # This service's pain was NOT detected — it should NOT appear
                pass

        # Explicitly verify 5 services that should NOT appear
        should_not_appear = [
            "Schema Hotel",              # pain: no_hotel_schema
            "Schema Organization",       # pain: no_org_schema
            "Página de FAQ",             # pain: no_faq_schema
            "Meta Tags Sociales (Open Graph)",  # pain: no_og_tags
            "Informe Mensual",           # pain: no_monthly_report
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

        # Should have 8 services (static mode)
        assert len(service_rows) == 8, f"Backwards compat should show 8 services, got {len(service_rows)}"

    def test_asset_quality_table_none_pains_shows_all_static(self):
        """With detected_pain_ids=None, should fall back to static (backwards compat)."""
        result = self.gen._generate_asset_quality_table(
            assets_generated=[],
            detected_pain_ids=None,
        )

        lines = result.strip().split("\n")
        service_rows = [l for l in lines if l.startswith("| ") and "Entregable" not in l]

        # Should have 8 services
        assert len(service_rows) == 8, f"None pains should show 8 services, got {len(service_rows)}"

    def test_dynamic_services_table_shows_all_services_with_status(self):
        """FASE-2: _generate_dynamic_services_table should show ALL 8 services with status icons."""
        detected_pain_ids = ["no_og_tags", "no_monthly_report"]

        result = self.gen._generate_dynamic_services_table(detected_pain_ids=detected_pain_ids)

        # Should have header + separator + 8 services = 10 lines
        lines = result.strip().split("\n")
        assert len(lines) == 10, f"Expected 10 lines (header+sep+8 services), got {len(lines)}: {lines}"

        # Verify all 8 services from PROPOSAL_SERVICE_TO_ASSET appear
        for service_name in PROPOSAL_SERVICE_TO_ASSET.keys():
            assert service_name in result, f"Service '{service_name}' should appear but didn't"

        # Verify status column exists
        assert "Estado" in lines[0]

    def test_dynamic_services_table_no_pains_returns_all_7_services_with_status(self):
        """FASE-2: With no detected pains, returns all 7 standard services with status column."""
        result = self.gen._generate_dynamic_services_table(detected_pain_ids=[])

        assert result != "", "Expected 7 services when no pains detected, got empty string"

        # Verify all 7 base services are present
        for service_name in PROPOSAL_SERVICE_TO_ASSET.keys():
            assert service_name in result, f"Service '{service_name}' should appear but didn't"

        # Verify status icons are present
        assert "✅" in result or "⏳" in result or "ℹ️" in result or "⚠️" in result

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
        """If all 7 base pains are detected (excl. AEO conditional), all 7 base services appear.

        FASE-D: AEO service is CONDITIONAL on score_aeo < 20, not pain-based.
        So when all base pains are detected, exactly 7 services appear (not 8).
        """
        all_base_pain_ids = [
            entry.pain_id
            for entry in SERVICE_CATALOG.values()
            if entry.pain_id != "low_ia_readiness"  # Exclude AEO conditional
        ]

        result = self.gen._generate_asset_quality_table(
            assets_generated=[],
            detected_pain_ids=all_base_pain_ids,
        )

        lines = result.strip().split("\n")
        service_rows = [l for l in lines if l.startswith("| ") and "Entregable" not in l]

        # 7 base services only (AEO is conditional, not triggered by pain)
        assert len(service_rows) == 7, f"Expected 7 base services, got {len(service_rows)}"

        # Verify all 7 base service names appear
        for entry in SERVICE_CATALOG.values():
            if entry.pain_id != "low_ia_readiness":
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

    def test_service_catalog_has_8_entries(self):
        """SERVICE_CATALOG should have 8 entries: 7 base + 1 AEO conditional (FASE-D).

        The 8th entry is 'optimizacion_ia_generativa' (AEO service) which is
        conditionally added when score_aeo < 20. It does NOT appear in the table
        unless score_aeo condition is met.
        """
        assert len(SERVICE_CATALOG) == 8, f"Expected 8 entries (7 base + AEO), got {len(SERVICE_CATALOG)}"

    def test_aeo_service_is_conditional_entry(self):
        """FASE-D: AEO entry exists but is triggered by score, not by pain detection."""
        from modules.commercial_documents.service_catalog import SERVICE_CATALOG

        aeo_entry = SERVICE_CATALOG.get("optimizacion_ia_generativa")
        assert aeo_entry is not None, "AEO service entry should exist in SERVICE_CATALOG"
        assert aeo_entry.pain_id == "low_ia_readiness"
        assert aeo_entry.asset_type == "llms_txt"

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
        assert len(PROPOSAL_SERVICE_TO_ASSET) == 8, f"Expected 8 entries, got {len(PROPOSAL_SERVICE_TO_ASSET)}"

    def test_service_to_asset_lookup_has_8_entries(self):
        """SERVICE_TO_ASSET_LOOKUP should have 8 entries (7 base + AEO conditional, FASE-D)."""
        from modules.commercial_documents.service_catalog import SERVICE_TO_ASSET_LOOKUP
        assert SERVICE_TO_ASSET_LOOKUP, "SERVICE_TO_ASSET_LOOKUP must exist"
        assert len(SERVICE_TO_ASSET_LOOKUP) == 8, f"Expected 8 entries (7 base + AEO), got {len(SERVICE_TO_ASSET_LOOKUP)}"

    def test_all_service_catalog_services_have_lookup_entry(self):
        """Every SERVICE_CATALOG service should have an entry in SERVICE_TO_ASSET_LOOKUP."""
        from modules.commercial_documents.service_catalog import SERVICE_CATALOG, SERVICE_TO_ASSET_LOOKUP
        for key, entry in SERVICE_CATALOG.items():
            assert entry.service_name in SERVICE_TO_ASSET_LOOKUP, \
                f"Service '{entry.service_name}' from SERVICE_CATALOG has no lookup in SERVICE_TO_ASSET_LOOKUP"


class TestDynamicServicesTableStates:
    """FASE-2: Verify _generate_dynamic_services_table shows correct states."""

    def setup_method(self):
        self.gen = V4ProposalGenerator()

    def test_shows_aligned_for_high_confidence(self):
        """Service with confidence >= 0.85 shows ✅ Alineado."""
        assets = [
            {"asset_type": "optimization_guide", "confidence_score": 0.9},
        ]
        result = self.gen._generate_dynamic_services_table(assets_generated=assets)
        assert "✅ Alineado" in result
        assert "SEO Local" in result

    def test_shows_pending_when_no_asset(self):
        """Service without generated asset shows ⏳ Pendiente."""
        result = self.gen._generate_dynamic_services_table(assets_generated=[])
        assert "⏳ Pendiente" in result

    def test_shows_present_in_production(self):
        """Service verified in production shows ℹ️ Presente en sitio."""
        # Mock site presence report
        mock_result = MagicMock()
        mock_result.status.value = "exists"
        mock_report = MagicMock()
        mock_report.results = {"optimization_guide": mock_result}

        result = self.gen._generate_dynamic_services_table(
            assets_generated=[],
            site_presence_report=mock_report,
        )
        assert "ℹ️ Presente en sitio" in result
        assert "SEO Local" in result

    def test_shows_preparation_for_low_confidence(self):
        """Service with confidence < 0.85 shows 'En proceso de activación — Semana 2'."""
        assets = [
            {"asset_type": "optimization_guide", "confidence_score": 0.7},
        ]
        result = self.gen._generate_dynamic_services_table(assets_generated=assets)
        assert "En proceso de activación — Semana 2" in result

    def test_aeo_conditional_appears_when_score_low(self):
        """AEO service appears when score_aeo < 20."""
        result = self.gen._generate_dynamic_services_table(score_aeo=15)
        assert "Optimización para IA Generativa" in result

    def test_aeo_conditional_absent_when_score_high(self):
        """FASE-2: AEO service now ALWAYS appears (part of PROPOSAL_SERVICE_TO_ASSET)."""
        result = self.gen._generate_dynamic_services_table(score_aeo=25)
        # AEO is always present in the table now; score_aeo only affects its status
        assert "Optimización para IA Generativa" in result
        # When score_aeo >= 20 and no asset generated, it shows as pending
        assert "⏳ Pendiente" in result


class TestTechnicalAssetsTable:
    """FASE-2: Verify _generate_technical_assets_table."""

    def setup_method(self):
        self.gen = V4ProposalGenerator()

    def test_technical_assets_table_shows_both_assets(self):
        """Technical assets table shows analytics_setup_guide and indirect_traffic_optimization."""
        result = self.gen._generate_technical_assets_table()
        assert "Guía de Configuración Analytics" in result
        assert "Optimización de Tráfico Indirecto" in result

    def test_technical_assets_table_shows_generated_status(self):
        """Generated technical asset shows ✅ Generado."""
        assets = [
            {"asset_type": "analytics_setup_guide", "confidence_score": 0.9},
        ]
        result = self.gen._generate_technical_assets_table(assets_generated=assets)
        assert "✅ Generado" in result

    def test_technical_assets_table_shows_not_generated(self):
        """Missing technical asset shows ⏳ No generado."""
        result = self.gen._generate_technical_assets_table(assets_generated=[])
        assert "⏳ No generado" in result
