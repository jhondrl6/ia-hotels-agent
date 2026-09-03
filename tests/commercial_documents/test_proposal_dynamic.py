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
from modules.commercial_documents.data_structures import AssetSpec
from modules.asset_generation.proposal_asset_alignment import PROPOSAL_SERVICE_TO_ASSET
from modules.common.service_identity import SERVICE_IDENTITIES

# FASE-A: el esperado se CALCULA desde el registro canónico (anti-lección L-NC10).
# Sustituir un literal equivocado por uno correcto sólo re-fosiliza el drift «8 vs 7».
SERVICIOS_ALINEABLES = {i.service_name for i in SERVICE_IDENTITIES if i.counts_in_alignment}
COMPLEMENTO_SIEMPRE_ACTIVO = {
    i.service_name for i in SERVICE_IDENTITIES if not i.counts_in_alignment
}


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

        # Una fila por servicio prometido: el conteo lo fija el registro, no este test
        assert len(service_rows) == len(PROPOSAL_SERVICE_TO_ASSET), (
            f"Backwards compat should show one row per promised service "
            f"({len(PROPOSAL_SERVICE_TO_ASSET)}), got {len(service_rows)}"
        )

    def test_asset_quality_table_none_pains_shows_all_static(self):
        """With detected_pain_ids=None, should fall back to static (backwards compat)."""
        result = self.gen._generate_asset_quality_table(
            assets_generated=[],
            detected_pain_ids=None,
        )

        lines = result.strip().split("\n")
        service_rows = [l for l in lines if l.startswith("| ") and "Entregable" not in l]

        assert len(service_rows) == len(PROPOSAL_SERVICE_TO_ASSET), (
            f"None pains should show one row per promised service "
            f"({len(PROPOSAL_SERVICE_TO_ASSET)}), got {len(service_rows)}"
        )

    def test_dynamic_services_table_shows_all_services_with_status(self):
        """FASE-2: _generate_dynamic_services_table muestra los servicios prometidos con
        iconos de estado. FASE-3: los servicios sin asset quedan excluidos → se pasan
        todos los assets. FASE-A: el conteo sale de PROPOSAL_SERVICE_TO_ASSET."""
        detected_pain_ids = ["no_og_tags", "no_monthly_report"]
        all_assets = [
            {"asset_type": "optimization_guide", "confidence_score": 0.9},
            {"asset_type": "whatsapp_button", "confidence_score": 0.85},
            {"asset_type": "hotel_schema", "confidence_score": 0.8},
            {"asset_type": "org_schema", "confidence_score": 0.9},
            {"asset_type": "monthly_report", "confidence_score": 0.75},
            {"asset_type": "faq_page", "confidence_score": 0.95},
            {"asset_type": "open_graph", "confidence_score": 0.7},
            {"asset_type": "llms_txt", "confidence_score": 0.85},
        ]

        result = self.gen._generate_dynamic_services_table(
            detected_pain_ids=detected_pain_ids,
            assets_generated=all_assets,
        )

        # Should have header + separator + 7 services = 9 lines
        # (monthly_report / "Informe Mensual" blocked by semantic validation)
        lines = result.strip().split("\n")
        assert len(lines) == 9, f"Expected 9 lines (header+sep+7 services), got {len(lines)}: {lines}"

        # Verify all 8 services from PROPOSAL_SERVICE_TO_ASSET appear (except "Informe Mensual")
        for service_name in PROPOSAL_SERVICE_TO_ASSET.keys():
            if service_name == "Informe Mensual":
                continue  # blocked by semantic validation
            assert service_name in result, f"Service '{service_name}' should appear but didn't"

        # Verify status column exists
        assert "Estado" in lines[0]

    def test_dynamic_services_table_no_pains_returns_all_7_services_with_status(self):
        """FASE-2: With no detected pains, returns all 7 standard services with status column.
        FASE-3: Services without assets are excluded → provide all 7 base assets."""
        all_assets = [
            {"asset_type": "optimization_guide", "confidence_score": 0.9},
            {"asset_type": "whatsapp_button", "confidence_score": 0.85},
            {"asset_type": "hotel_schema", "confidence_score": 0.8},
            {"asset_type": "org_schema", "confidence_score": 0.9},
            {"asset_type": "monthly_report", "confidence_score": 0.75},
            {"asset_type": "faq_page", "confidence_score": 0.95},
            {"asset_type": "open_graph", "confidence_score": 0.7},
        ]

        result = self.gen._generate_dynamic_services_table(
            detected_pain_ids=[],
            assets_generated=all_assets,
        )

        assert result != "", "Expected 7 services when no pains detected, got empty string"

        # Verify all 7 base services are present (8 total, "Informe Mensual" blocked by semantic validation)
        for service_name in PROPOSAL_SERVICE_TO_ASSET.keys():
            if service_name == "Informe Mensual":
                continue  # blocked by semantic validation
            if service_name == "Optimización para IA Generativa":
                continue  # no llms_txt asset provided, excluded by conditional filtering
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
        # FASE-A (V14): el esperado sale del registro canónico, no de un literal
        assert set(PROPOSAL_SERVICE_TO_ASSET) == SERVICIOS_ALINEABLES, (
            f"PROPOSAL_SERVICE_TO_ASSET debe proyectar las identidades alineables del "
            f"canónico. Sobran {sorted(set(PROPOSAL_SERVICE_TO_ASSET) - SERVICIOS_ALINEABLES)}, "
            f"faltan {sorted(SERVICIOS_ALINEABLES - set(PROPOSAL_SERVICE_TO_ASSET))}"
        )

    def test_service_to_asset_lookup_refleja_alignment(self):
        """SERVICE_TO_ASSET_LOOKUP es retro-compatibilidad: calca PROPOSAL_SERVICE_TO_ASSET."""
        from modules.commercial_documents.service_catalog import SERVICE_TO_ASSET_LOOKUP
        assert SERVICE_TO_ASSET_LOOKUP, "SERVICE_TO_ASSET_LOOKUP must exist"
        assert SERVICE_TO_ASSET_LOOKUP == PROPOSAL_SERVICE_TO_ASSET, (
            "SERVICE_TO_ASSET_LOOKUP se deriva de PROPOSAL_SERVICE_TO_ASSET; si difieren, "
            "alguien volvió a mantener una copia a mano"
        )

    def test_solo_servicios_alineables_tienen_lookup_entry(self):
        """El complemento siempre-activo está en SERVICE_CATALOG (sí se genera) pero NO
        en SERVICE_TO_ASSET_LOOKUP (no se promete por pain — BUG-10 / FASE-3).

        La versión anterior de este test exigía que TODO SERVICE_CATALOG tuviera entrada
        en el lookup: esa exigencia ES el drift «8 vs 7» de V14 (dos registros que
        responden preguntas distintas forzados a tener el mismo tamaño).
        """
        from modules.commercial_documents.service_catalog import SERVICE_TO_ASSET_LOOKUP
        for key, entry in SERVICE_CATALOG.items():
            debe_estar = entry.service_name not in COMPLEMENTO_SIEMPRE_ACTIVO
            assert (entry.service_name in SERVICE_TO_ASSET_LOOKUP) is debe_estar, (
                f"Service '{entry.service_name}' (key={key}): su presencia en "
                f"SERVICE_TO_ASSET_LOOKUP debería ser {debe_estar}"
            )


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
        """FASE-3: Service without generated asset is excluded (not shown as ⏳ Pendiente).
        Footnote lists excluded services instead."""
        result = self.gen._generate_dynamic_services_table(assets_generated=[])
        # Services without assets are excluded → footnote, not "⏳ Pendiente" in table
        assert "> **Servicios adicionales disponibles:**" in result

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
        """FASE-3: AEO service without asset is excluded (footnote), not shown as pending."""
        result = self.gen._generate_dynamic_services_table(score_aeo=25)
        # AEO without asset is excluded → footnote
        assert "Optimización para IA Generativa" in result
        assert "> **Servicios adicionales disponibles:**" in result


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


class TestFase3ConditionalServicesFiltering:
    """FASE-3 ASSET-ALIGNMENT-ZIONE: Verify conditional service filtering."""

    def setup_method(self):
        self.gen = V4ProposalGenerator()

    def test_conditional_services_filtering(self):
        """Only services with asset or present_in_production appear in main table.
        Excluded services appear in footnote."""
        # 4 services with asset (confidence not None), 4 without (confidence None)
        assets = [
            {"asset_type": "optimization_guide", "confidence_score": 0.9},
            {"asset_type": "whatsapp_button", "confidence_score": 0.85},
            {"asset_type": "hotel_schema", "confidence_score": 0.75},
            {"asset_type": "faq_page", "confidence_score": 0.95},
        ]
        # Remaining 4 have no asset: org_schema, monthly_report, open_graph, llms_txt

        result = self.gen._generate_dynamic_services_table(assets_generated=assets)

        # The 4 services with assets should appear
        assert "SEO Local" in result
        assert "Botón de WhatsApp" in result
        assert "Schema Hotel" in result
        assert "Página de FAQ" in result

        # The 4 services without assets should NOT appear in table rows
        # but should appear in the footnote
        assert "> **Servicios adicionales disponibles:**" in result

        # Verify excluded services are in the footnote
        # NOTE: "Informe Mensual" (monthly_report) is blocked by semantic validation
        # (validar_semantica_comercial), not by conditional filtering — it's skipped entirely.
        excluded = [
            "Schema Organization",
            "Meta Tags Sociales (Open Graph)",
            "Optimización para IA Generativa",
        ]
        for svc in excluded:
            assert svc in result, f"Excluded service '{svc}' should appear in footnote"

        # Verify excluded services do NOT show "⏳ Pendiente" in the table
        lines = result.strip().split("\n")
        table_lines = [l for l in lines if l.startswith("|") and "⏳ Pendiente" in l]
        for line in table_lines:
            for svc in excluded:
                assert svc not in line, f"Excluded service '{svc}' should NOT show '⏳ Pendiente' in table"

    def test_all_services_with_assets_none_excluded(self):
        """When all 8 services have assets, none are excluded and no footnote."""
        assets = [
            {"asset_type": "optimization_guide", "confidence_score": 0.9},
            {"asset_type": "whatsapp_button", "confidence_score": 0.85},
            {"asset_type": "hotel_schema", "confidence_score": 0.8},
            {"asset_type": "org_schema", "confidence_score": 0.9},
            {"asset_type": "monthly_report", "confidence_score": 0.75},
            {"asset_type": "faq_page", "confidence_score": 0.95},
            {"asset_type": "open_graph", "confidence_score": 0.7},
            {"asset_type": "llms_txt", "confidence_score": 0.85},
        ]

        result = self.gen._generate_dynamic_services_table(assets_generated=assets)

        # No footnote should appear
        assert "Servicios adicionales disponibles" not in result

        # All services should appear, except "Informe Mensual" which is blocked
        # by semantic validation (validar_semantica_comercial blocks monthly_report → no_faq_schema)
        for service_name in PROPOSAL_SERVICE_TO_ASSET.keys():
            if service_name == "Informe Mensual":
                continue  # blocked by semantic validation, not by conditional filtering
            assert service_name in result, f"Service '{service_name}' should appear"

    def test_present_in_production_includes_service(self):
        """Service without asset but present_in_production should still appear."""
        mock_result = MagicMock()
        mock_result.status.value = "exists"
        mock_report = MagicMock()
        mock_report.results = {"org_schema": mock_result}

        # No assets generated at all
        result = self.gen._generate_dynamic_services_table(
            assets_generated=[],
            site_presence_report=mock_report,
        )

        # Schema Organization should appear (present_in_production)
        assert "Schema Organization" in result
        assert "ℹ️ Presente en sitio" in result

        # Other services without asset should be excluded → footnote
        assert "> **Servicios adicionales disponibles:**" in result

    def test_no_assets_no_presence_all_excluded(self):
        """When no assets and no presence, footnote lists all 8 services."""
        result = self.gen._generate_dynamic_services_table(assets_generated=[])

        # All 8 should be in the footnote (except "Informe Mensual" blocked by semantic validation)
        assert "> **Servicios adicionales disponibles:**" in result
        for service_name in PROPOSAL_SERVICE_TO_ASSET.keys():
            if service_name == "Informe Mensual":
                continue  # blocked by semantic validation
            assert service_name in result, f"Service '{service_name}' should appear in footnote"

        # Table should be empty (only header + separator)
        lines = result.strip().split("\n")
        table_lines = [l for l in lines if l.startswith("|")]
        # header + separator = 2 lines, no data rows
        data_rows = [l for l in table_lines if "---" not in l and "Servicio" not in l]
        assert len(data_rows) == 0, f"Expected 0 data rows, got {len(data_rows)}: {data_rows}"


class TestFase3LookupUnification:
    """FASE-3 ASSET-ALIGNMENT-ZIONE: Verify SERVICE_TO_ASSET_LOOKUP = PROPOSAL_SERVICE_TO_ASSET."""

    def test_service_to_asset_lookup_matches_proposal(self):
        """SERVICE_TO_ASSET_LOOKUP must be identical to PROPOSAL_SERVICE_TO_ASSET."""
        from modules.commercial_documents.service_catalog import SERVICE_TO_ASSET_LOOKUP
        from modules.asset_generation.proposal_asset_alignment import PROPOSAL_SERVICE_TO_ASSET

        assert set(SERVICE_TO_ASSET_LOOKUP.keys()) == set(PROPOSAL_SERVICE_TO_ASSET.keys()), \
            "SERVICE_TO_ASSET_LOOKUP keys must match PROPOSAL_SERVICE_TO_ASSET keys"
        assert SERVICE_TO_ASSET_LOOKUP == PROPOSAL_SERVICE_TO_ASSET, \
            "SERVICE_TO_ASSET_LOOKUP must be identical to PROPOSAL_SERVICE_TO_ASSET"

    def test_service_to_asset_lookup_cubre_identidades_alineables(self):
        """SERVICE_TO_ASSET_LOOKUP must cover exactly the alignment-counted identities."""
        from modules.commercial_documents.service_catalog import SERVICE_TO_ASSET_LOOKUP

        assert set(SERVICE_TO_ASSET_LOOKUP) == SERVICIOS_ALINEABLES, (
            f"SERVICE_TO_ASSET_LOOKUP debe cubrir las identidades alineables del canónico. "
            f"Sobran {sorted(set(SERVICE_TO_ASSET_LOOKUP) - SERVICIOS_ALINEABLES)}, "
            f"faltan {sorted(SERVICIOS_ALINEABLES - set(SERVICE_TO_ASSET_LOOKUP))}"
        )


class TestFaseR0DPlan30DaysConditional:
    """FASE-R0-D (B6/AC11): Plan 30 días condicional a whatsapp_conflict."""

    def setup_method(self):
        self.gen = V4ProposalGenerator()

    def test_proposal_plan_sin_whatsapp(self):
        """whatsapp_conflict=False: plan NO contiene 'WhatsApp + datos para IA' (AC11)."""
        p1_assets = [
            AssetSpec(asset_type="hotel_schema", priority=1),
        ]
        result = self.gen._build_30_day_plan(
            asset_plan=p1_assets,
            diagnostic_summary=None,
            whatsapp_conflict=False,
        )
        # NO debe mencionar WhatsApp cuando no hay conflicto
        assert "WhatsApp + datos para IA" not in result, \
            "Plan 30 días NO debe mencionar 'WhatsApp + datos para IA' sin conflicto (AC11)"
        # SÍ debe mencionar 'datos para IA' (la parte no-WhatsApp permanece)
        assert "datos para IA" in result, \
            "Plan 30 días debe contener 'datos para IA' (texto base siempre presente)"
        # El asset dinámico debe aparecer
        assert "Hotel Schema" in result

    def test_proposal_plan_con_whatsapp(self):
        """whatsapp_conflict=True: plan SÍ contiene 'WhatsApp + datos para IA'."""
        p1_assets = [
            AssetSpec(asset_type="hotel_schema", priority=1),
        ]
        result = self.gen._build_30_day_plan(
            asset_plan=p1_assets,
            diagnostic_summary=None,
            whatsapp_conflict=True,
        )
        # SÍ debe mencionar WhatsApp cuando hay conflicto
        assert "WhatsApp + datos para IA" in result, \
            "Plan 30 días debe mencionar 'WhatsApp + datos para IA' con conflicto"


class TestFaseR0DServiciosAdicionalesWhatsApp:
    """FASE-R0-D (B7): Botón WhatsApp fuera de 'Servicios adicionales' sin brecha."""

    def setup_method(self):
        self.gen = V4ProposalGenerator()

    def test_servicios_adicionales_sin_brecha_whatsapp(self):
        """Sin conflicto ni brecha whatsapp: botón NO aparece en footnote (B7).

        Setup: whatsapp_conflict=False, opportunity_scores sin brecha whatsapp,\n        whatsapp_button sin asset → va a excluded_services pero se filtra.
        """
        # Algunos assets (NO whatsapp_button) para que la tabla no esté vacía
        assets = [
            {"asset_type": "optimization_guide", "confidence_score": 0.9},
            {"asset_type": "hotel_schema", "confidence_score": 0.85},
        ]
        result = self.gen._generate_dynamic_services_table(
            detected_pain_ids=[],
            assets_generated=assets,
            whatsapp_conflict=False,
            opportunity_scores=None,  # sin brechas → breach_by_asset vacío
        )
        # Debe existir la footnote (hay servicios excluidos: whatsapp_button, etc.)
        assert "> **Servicios adicionales disponibles:**" in result, \
            "Debe existir footnote de servicios adicionales"
        # Botón de WhatsApp NO debe estar en la footnote
        # Extraer el texto de la footnote
        footnote_line = ""
        for line in result.split("\n"):
            if "Servicios adicionales disponibles" in line:
                footnote_line = line
                break
        assert "Botón de WhatsApp" not in footnote_line, \
            "Botón de WhatsApp NO debe aparecer en 'Servicios adicionales' sin brecha (B7)"

    def test_servicios_adicionales_con_brecha_whatsapp(self):
        """Con brecha whatsapp en opportunity_scores: botón SÍ aparece en footnote (B7).

        Setup: whatsapp_conflict=False, opportunity_scores con brecha no_whatsapp_visible,
        whatsapp_button sin asset → va a excluded_services y NO se filtra.
        """
        assets = [
            {"asset_type": "optimization_guide", "confidence_score": 0.9},
            {"asset_type": "hotel_schema", "confidence_score": 0.85},
        ]
        # Brecha whatsapp en opportunity_scores → breach_by_asset["whatsapp_button"] existe
        opportunity_scores = [
            {
                "brecha_id": "no_whatsapp_visible",
                "rank": 2,
                "estimated_monthly_cop": 5_000_000,
                "brecha_name": "WhatsApp no visible",
            },
        ]
        result = self.gen._generate_dynamic_services_table(
            detected_pain_ids=[],
            assets_generated=assets,
            whatsapp_conflict=False,
            opportunity_scores=opportunity_scores,
        )
        # Debe existir la footnote
        assert "> **Servicios adicionales disponibles:**" in result, \
            "Debe existir footnote de servicios adicionales"
        # Botón de WhatsApp SÍ debe estar en la footnote (hay brecha real)
        footnote_line = ""
        for line in result.split("\n"):
            if "Servicios adicionales disponibles" in line:
                footnote_line = line
                break
        assert "Botón de WhatsApp" in footnote_line, \
            "Botón de WhatsApp SÍ debe aparecer en 'Servicios adicionales' con brecha (B7)"
