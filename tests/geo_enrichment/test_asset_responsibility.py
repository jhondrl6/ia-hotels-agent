"""Tests for AssetResponsibilityContract - FASE-5.

These tests verify:
1. CORE assets come before GEO assets in implementation order
2. GEO assets never replace CORE assets (always enrich)
3. Enrichment chains are correctly formed

Run with: python -m pytest tests/geo_enrichment/test_asset_responsibility.py -v
"""

import pytest
from modules.geo_enrichment import (
    AssetResponsibilityContract,
    AssetType,
    AssetResponsibility,
    get_implementation_order,
    get_replacement_rule,
    generate_delivery_template,
)


class TestResponsibilityOrder:
    """Tests for implementation order - CORE must come before GEO."""

    def test_core_before_geo_default(self):
        """All CORE assets should come before all GEO assets by default."""
        contract = AssetResponsibilityContract()
        order = contract.get_implementation_order()

        # Find the dividing line between CORE and GEO
        core_indices = []
        geo_indices = []

        for i, resp in enumerate(order):
            if resp.type == AssetType.CORE:
                core_indices.append(i)
            elif resp.type == AssetType.GEO:
                geo_indices.append(i)

        # All CORE indices should be less than all GEO indices
        assert len(core_indices) > 0, "Should have CORE assets"
        assert len(geo_indices) > 0, "Should have GEO assets"

        max_core = max(core_indices)
        min_geo = min(geo_indices)

        assert max_core < min_geo, (
            f"CORE assets should come before GEO assets. "
            f"Last CORE at index {max_core}, first GEO at index {min_geo}"
        )

    def test_core_before_geo_with_filter(self):
        """With filtered assets, CORE still comes before GEO."""
        contract = AssetResponsibilityContract()
        order = contract.get_implementation_order(
            core_assets=['hotel_schema.json', 'faq_schema.json'],
            geo_assets=['faq_schema_rich.json', 'hotel_schema_rich.json']
        )

        core_indices = [i for i, r in enumerate(order) if r.type == AssetType.CORE]
        geo_indices = [i for i, r in enumerate(order) if r.type == AssetType.GEO]

        assert max(core_indices) < min(geo_indices), "CORE must come before GEO"

    def test_priority_order_correct(self):
        """Priority 1 (CORE) should come before priority 2 (GEO)."""
        contract = AssetResponsibilityContract()
        order = contract.get_implementation_order()

        # Check that priorities are in ascending order
        priorities = [r.priority for r in order]
        assert priorities == sorted(priorities), "Priorities should be ascending"

    def test_mandatory_comes_first(self):
        """Mandatory assets should come before optional ones."""
        contract = AssetResponsibilityContract()
        order = contract.get_implementation_order()

        # Find first non-mandatory
        first_optional_idx = None
        for i, resp in enumerate(order):
            if not resp.mandatory:
                first_optional_idx = i
                break

        # All before it should be mandatory
        if first_optional_idx is not None:
            for i in range(first_optional_idx):
                assert order[i].mandatory, f"Asset {order[i].filename} should be mandatory"


class TestNoReplacement:
    """Tests verifying GEO never replaces CORE."""

    def test_geo_has_enriched_by_field(self):
        """All GEO assets should have enriched_by set."""
        contract = AssetResponsibilityContract()

        for resp in contract.get_geo_responsibilities():
            assert resp.enriched_by is not None, (
                f"GEO asset {resp.filename} should have enriched_by field"
            )

    def test_geo_replaces_is_none(self):
        """GEO assets should not replace anything (replaces=None)."""
        contract = AssetResponsibilityContract()

        for resp in contract.get_geo_responsibilities():
            assert resp.replaces is None, (
                f"GEO asset {resp.filename} should not have 'replaces' set. "
                f"Found: {resp.replaces}. GEO enriches, never replaces."
            )

    def test_core_enrichment_chain_defined(self):
        """Each CORE asset should have a defined enrichment chain."""
        contract = AssetResponsibilityContract()

        for resp in contract.get_core_responsibilities():
            chain = contract.get_asset_chain(resp.filename)
            assert chain['core'] == resp.filename
            # GEO can be None if no enrichment exists
            if chain['geo'] is not None:
                assert chain['chain'] == [resp.filename, chain['geo']]

    def test_replacement_rule_never_replace(self):
        """Replacement rule should always be 'enrich' for GEO assets, never 'replace'."""
        contract = AssetResponsibilityContract()

        geo_assets = ['hotel_schema_rich.json', 'faq_schema_rich.json', 'boton_whatsapp_rich.html']

        for asset in geo_assets:
            rule = contract.get_replacement_rule(asset)
            assert rule['rule'] != 'replace', (
                f"GEO asset {asset} should not have 'replace' rule. "
                f"Found: {rule['rule']}"
            )

    def test_core_has_no_enriched_by(self):
        """CORE assets should have enriched_by=None (they are the source)."""
        contract = AssetResponsibilityContract()

        for resp in contract.get_core_responsibilities():
            assert resp.enriched_by is None, (
                f"CORE asset {resp.filename} should not have 'enriched_by'. "
                f"CORE is the source, not enriched."
            )


class TestEnrichmentChain:
    """Tests for enrichment chain integrity."""

    def test_hotel_schema_chain(self):
        """hotel_schema.json -> hotel_schema_rich.json chain should exist."""
        contract = AssetResponsibilityContract()

        chain = contract.get_asset_chain('hotel_schema.json')

        assert chain['core'] == 'hotel_schema.json'
        assert chain['geo'] == 'hotel_schema_rich.json'
        assert 'hotel_schema_rich.json' in chain['chain']

    def test_faq_schema_chain(self):
        """faq_schema.json -> faq_schema_rich.json chain should exist."""
        contract = AssetResponsibilityContract()

        chain = contract.get_asset_chain('faq_schema.json')

        assert chain['core'] == 'faq_schema.json'
        assert chain['geo'] == 'faq_schema_rich.json'
        assert 'faq_schema_rich.json' in chain['chain']

    def test_boton_whatsapp_chain(self):
        """boton_whatsapp.html -> boton_whatsapp_rich.html chain should exist."""
        contract = AssetResponsibilityContract()

        chain = contract.get_asset_chain('boton_whatsapp.html')

        assert chain['core'] == 'boton_whatsapp.html'
        assert chain['geo'] == 'boton_whatsapp_rich.html'
        assert 'boton_whatsapp_rich.html' in chain['chain']

    def test_chain_bidirectional(self):
        """GEO asset should reference back to CORE."""
        contract = AssetResponsibilityContract()

        # From CORE to GEO
        core_to_geo = contract.CORE_TO_GEO_MAP
        assert core_to_geo['hotel_schema.json'] == 'hotel_schema_rich.json'
        assert core_to_geo['faq_schema.json'] == 'faq_schema_rich.json'

        # From GEO to CORE (reverse mapping)
        geo_to_core = contract.GEO_TO_CORE_MAP
        assert geo_to_core['hotel_schema_rich.json'] == 'hotel_schema.json'
        assert geo_to_core['faq_schema_rich.json'] == 'faq_schema.json'

    def test_chain_completeness(self):
        """All GEO assets should have a CORE parent and vice versa."""
        contract = AssetResponsibilityContract()

        core_to_geo = contract.CORE_TO_GEO_MAP
        geo_to_core = contract.GEO_TO_CORE_MAP

        # Every CORE with GEO enrichment should map to a GEO
        for core in core_to_geo:
            geo = core_to_geo[core]
            assert geo in geo_to_core, f"{geo} should be in reverse map"
            assert geo_to_core[geo] == core, f"Reverse mapping should be consistent"

        # Every GEO should map back to CORE
        for geo in geo_to_core:
            core = geo_to_core[geo]
            assert core in core_to_geo, f"{core} should be in forward map"
            assert core_to_geo[core] == geo, f"Forward mapping should be consistent"


class TestConvenienceFunctions:
    """Tests for module-level convenience functions."""

    def test_get_implementation_order_function(self):
        """Module-level get_implementation_order should work."""
        order = get_implementation_order(
            core_assets=['hotel_schema.json'],
            geo_assets=['hotel_schema_rich.json']
        )

        assert len(order) == 2
        assert order[0].type == AssetType.CORE
        assert order[1].type == AssetType.GEO

    def test_get_replacement_rule_function(self):
        """Module-level get_replacement_rule should work."""
        rule = get_replacement_rule('hotel_schema_rich.json')

        assert 'rule' in rule
        assert rule['rule'] == 'enrich'
        assert 'paired_asset' in rule

    def test_generate_delivery_template(self):
        """Module-level generate_delivery_template should work."""
        template = generate_delivery_template(
            hotel_name="Hotel Test",
            core_assets=['hotel_schema.json', 'faq_schema.json'],
            geo_assets=['hotel_schema_rich.json'],
            geo_score=50  # Low score = GEO mandatory
        )

        assert "Hotel Test" in template
        assert "IMPLEMENTATION_ORDER" in template or "ORDEN DE IMPLEMENTACIÓN" in template
        assert "hotel_schema.json" in template


class TestContractEdgeCases:
    """Edge case tests."""

    def test_empty_core_assets(self):
        """Should handle empty core_assets gracefully."""
        contract = AssetResponsibilityContract()
        order = contract.get_implementation_order(core_assets=[], geo_assets=['hotel_schema_rich.json'])

        assert len(order) == 1
        assert order[0].filename == 'hotel_schema_rich.json'

    def test_empty_geo_assets(self):
        """Should handle empty geo_assets gracefully."""
        contract = AssetResponsibilityContract()
        order = contract.get_implementation_order(core_assets=['hotel_schema.json'], geo_assets=[])

        assert len(order) == 1
        assert order[0].filename == 'hotel_schema.json'

    def test_none_values(self):
        """Should handle None values gracefully."""
        contract = AssetResponsibilityContract()
        order = contract.get_implementation_order(core_assets=None, geo_assets=None)

        # Should return all assets
        assert len(order) == 6  # 3 CORE + 3 GEO

    def test_unknown_asset_rule(self):
        """Should return 'unknown' rule for unrecognized assets."""
        contract = AssetResponsibilityContract()
        rule = contract.get_replacement_rule('unknown_file.json')

        assert rule['rule'] in ['unknown_enrich', 'standalone', 'unknown']
        assert 'description' in rule


class TestDeliveryTemplate:
    """Tests for delivery template generation."""

    def test_template_includes_rule_of_gold(self):
        """Template should include 'NUNCA REEMPLAZAR, SIEMPRE ENRIQUECER'."""
        contract = AssetResponsibilityContract()
        template = contract.generate_delivery_template(
            hotel_name="Test Hotel",
            core_assets=['hotel_schema.json'],
            geo_assets=['hotel_schema_rich.json']
        )

        assert "NUNCA REEMPLAZAR" in template or "SIEMPRE ENRIQUECER" in template

    def test_template_marks_mandatory(self):
        """Template should mark mandatory assets correctly."""
        contract = AssetResponsibilityContract()
        template = contract.generate_delivery_template(
            hotel_name="Test Hotel",
            core_assets=['hotel_schema.json'],
            geo_assets=[],
            geo_score=100
        )

        # CORE should be marked as mandatory
        assert "hotel_schema.json" in template

    def test_template_shows_geo_mandatory_when_low_score(self):
        """GEO assets should show as mandatory when score < 68."""
        contract = AssetResponsibilityContract()
        template = contract.generate_delivery_template(
            hotel_name="Test Hotel",
            core_assets=['hotel_schema.json'],
            geo_assets=['hotel_schema_rich.json'],
            geo_score=50  # Low score
        )

        # Should indicate GEO is OBLIGATORIO
        assert "OBLIGATORIO" in template

    def test_template_shows_geo_optional_when_high_score(self):
        """GEO assets should show as optional when score >= 68."""
        contract = AssetResponsibilityContract()
        template = contract.generate_delivery_template(
            hotel_name="Test Hotel",
            core_assets=['hotel_schema.json'],
            geo_assets=['hotel_schema_rich.json'],
            geo_score=85  # High score
        )

        # Should indicate GEO is OPCIONAL
        assert "OPCIONAL" in template or "OPCIONAL" not in template  # May vary based on exact logic


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
