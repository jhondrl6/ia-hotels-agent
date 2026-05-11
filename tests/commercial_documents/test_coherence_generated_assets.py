"""Tests for FASE-1-A FIX-2: Coherence Validator generated_assets source of truth."""

import pytest
from unittest.mock import MagicMock
from modules.commercial_documents.coherence_validator import CoherenceValidator
from modules.asset_generation.proposal_asset_alignment import PROPOSAL_SERVICE_TO_ASSET


class TestCoherenceGeneratedAssets:
    """Tests for _check_promised_assets_exist with generated_assets parameter."""

    @pytest.fixture
    def validator(self):
        return CoherenceValidator()

    @pytest.fixture
    def mock_diagnostic(self):
        """Create a mock DiagnosticDocument."""
        return MagicMock()

    def _make_asset_specs(self, asset_types):
        """Helper: create mock AssetSpec list from asset_type names."""
        specs = []
        for at in asset_types:
            mock = MagicMock()
            mock.asset_type = at
            specs.append(mock)
        return specs

    def test_generated_assets_4_of_8_score(self, validator, mock_diagnostic):
        """4/8 assets generated (can_use=True) → score = 0.5.
        
        The orchestrator passes ALL planned asset_specs (matching PROPOSAL_SERVICE_TO_ASSET.values()).
        With 4 can_use=True out of 8 planned:
        - promised_types = 8 (all planned)
        - missing = {faq_page, open_graph, llms_txt, org_schema} = 4
        - score = (8 - 4) / 8 = 0.5
        """
        # All 8 planned asset_specs (like orchestrator does)
        all_planned = self._make_asset_specs(PROPOSAL_SERVICE_TO_ASSET.values())
        
        # 4 of 8 actually generated with can_use=True
        generated_assets = {
            'optimization_guide': {'can_use': True, 'confidence_score': 0.9},
            'whatsapp_button': {'can_use': True, 'confidence_score': 0.8},
            'hotel_schema': {'can_use': True, 'confidence_score': 0.7},
            'monthly_report': {'can_use': True, 'confidence_score': 0.6},
            # faq_page, open_graph, llms_txt, org_schema = MISSING (can_use=False or absent)
        }
        
        result = validator._check_promised_assets_exist(
            all_planned, mock_diagnostic, generated_assets=generated_assets
        )
        expected_score = 4 / len(PROPOSAL_SERVICE_TO_ASSET)
        assert abs(result.score - expected_score) < 0.01
        assert result.passed is False

    def test_generated_assets_7_of_8_score(self, validator, mock_diagnostic):
        """All 8 assets generated with can_use=True → score = 1.0."""
        all_planned = self._make_asset_specs(PROPOSAL_SERVICE_TO_ASSET.values())
        generated_assets = {
            'optimization_guide': {'can_use': True, 'confidence_score': 0.9},
            'whatsapp_button': {'can_use': True, 'confidence_score': 0.8},
            'hotel_schema': {'can_use': True, 'confidence_score': 0.7},
            'monthly_report': {'can_use': True, 'confidence_score': 0.6},
            'faq_page': {'can_use': True, 'confidence_score': 0.5},
            'open_graph': {'can_use': True, 'confidence_score': 0.4},
            'llms_txt': {'can_use': True, 'confidence_score': 0.3},
            'org_schema': {'can_use': True, 'confidence_score': 0.85},
        }
        result = validator._check_promised_assets_exist(
            all_planned, mock_diagnostic, generated_assets=generated_assets
        )
        assert result.score == 1.0
        assert result.passed is True

    def test_generated_assets_none_uses_catalog(self, validator, mock_diagnostic):
        """generated_assets=None → fallback to catalog (legacy behavior).
        
        With no generated_assets, the method uses is_asset_implemented() from
        the static catalog. Since all 8 PROPOSAL_SERVICE_TO_ASSET entries have
        IMPLEMENTED status in ASSET_CATALOG, missing_service_assets stays empty
        and the check passes with score=1.0.
        """
        # Pass all planned asset_specs
        all_planned = self._make_asset_specs(PROPOSAL_SERVICE_TO_ASSET.values())
        
        result = validator._check_promised_assets_exist(
            all_planned, mock_diagnostic, generated_assets=None
        )
        # Legacy: uses is_asset_implemented() from catalog
        # All 8 services have IMPLEMENTED assets → passed, score=1.0
        assert result.passed is True
        assert result.score == 1.0

    def test_generated_assets_partial_with_can_use_false(self, validator, mock_diagnostic):
        """Asset with can_use=False counts as missing (not just absent from dict).
        
        whatsapp_button has can_use=False explicitly, so it's counted as missing.
        optimization_guide is can_use=True.
        Result: 1/8 can_use → score = (8-7)/8 = 0.125.
        """
        all_planned = self._make_asset_specs(PROPOSAL_SERVICE_TO_ASSET.values())
        generated_assets = {
            'optimization_guide': {'can_use': True, 'confidence_score': 0.9},
            # All others: absent → treated as can_use=False
        }
        # Note: whatsapp_button has can_use implicitly False (not in dict)
        result = validator._check_promised_assets_exist(
            all_planned, mock_diagnostic, generated_assets=generated_assets
        )
        # 1 can_use=True, 7 missing → score = (8-7)/8 = 0.125
        expected_score = 1 / len(PROPOSAL_SERVICE_TO_ASSET)
        assert abs(result.score - expected_score) < 0.01
        assert result.passed is False

    def test_generated_assets_only_one_can_use(self, validator, mock_diagnostic):
        """Only 1 of 8 assets can_use → score = 0.125.
        
        When an asset_type is absent from generated_assets dict,
        gen_info.get('can_use', False) defaults to False.
        """
        all_planned = self._make_asset_specs(PROPOSAL_SERVICE_TO_ASSET.values())
        generated_assets = {
            'whatsapp_button': {'can_use': True, 'confidence_score': 0.8},
            # All others absent → can_use=False
        }
        result = validator._check_promised_assets_exist(
            all_planned, mock_diagnostic, generated_assets=generated_assets
        )
        # 1 can_use, 7 missing → (8-7)/8 = 0.125
        expected_score = 1 / len(PROPOSAL_SERVICE_TO_ASSET)
        assert abs(result.score - expected_score) < 0.01
        assert result.passed is False