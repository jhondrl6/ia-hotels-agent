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
    def mock_asset_seo(self):
        """Create a mock AssetSpec for SEO Local."""
        asset = MagicMock()
        asset.asset_type = 'optimization_guide'
        return asset

    @pytest.fixture
    def mock_diagnostic(self):
        """Create a mock DiagnosticDocument."""
        return MagicMock()

    def test_generated_assets_4_of_7_score(self, validator, mock_asset_seo, mock_diagnostic):
        """4/7 assets can_use → score ~0.57.
        
        Uses exact asset types from PROPOSAL_SERVICE_TO_ASSET:
        - optimization_guide, whatsapp_button, hotel_schema, monthly_report = 4
        - faq_page, open_graph, llms_txt = 3 missing
        """
        generated_assets = {
            'optimization_guide': {'can_use': True, 'confidence_score': 0.9},
            'whatsapp_button': {'can_use': True, 'confidence_score': 0.8},
            'hotel_schema': {'can_use': True, 'confidence_score': 0.7},
            'monthly_report': {'can_use': True, 'confidence_score': 0.6},
            # faq_page, open_graph, llms_txt missing → 3/7 missing
        }
        result = validator._check_promised_assets_exist(
            [mock_asset_seo], mock_diagnostic, generated_assets=generated_assets
        )
        # With 4/7 can_use=True: score should be 4/7 ≈ 0.57
        expected_score = 4 / len(PROPOSAL_SERVICE_TO_ASSET)
        assert abs(result.score - expected_score) < 0.01

    def test_generated_assets_7_of_7_score(self, validator, mock_asset_seo, mock_diagnostic):
        """All 7 assets can_use → score = 1.0."""
        generated_assets = {
            'optimization_guide': {'can_use': True, 'confidence_score': 0.9},
            'whatsapp_button': {'can_use': True, 'confidence_score': 0.8},
            'hotel_schema': {'can_use': True, 'confidence_score': 0.7},
            'monthly_report': {'can_use': True, 'confidence_score': 0.6},
            'faq_page': {'can_use': True, 'confidence_score': 0.5},
            'open_graph': {'can_use': True, 'confidence_score': 0.4},
            'llms_txt': {'can_use': True, 'confidence_score': 0.3},
        }
        result = validator._check_promised_assets_exist(
            [mock_asset_seo], mock_diagnostic, generated_assets=generated_assets
        )
        assert result.score == 1.0
        assert result.passed is True

    def test_generated_assets_none_uses_catalog(self, validator, mock_asset_seo, mock_diagnostic):
        """generated_assets=None → fallback to catalog (legacy behavior)."""
        result = validator._check_promised_assets_exist(
            [mock_asset_seo], mock_diagnostic, generated_assets=None
        )
        # Legacy: uses is_asset_implemented() from catalog
        assert result is not None
        assert hasattr(result, 'score')

    def test_generated_assets_partial_false(self, validator, mock_asset_seo, mock_diagnostic):
        """Asset with can_use=False counts as missing."""
        generated_assets = {
            'optimization_guide': {'can_use': True, 'confidence_score': 0.9},
            'whatsapp_button': {'can_use': False, 'confidence_score': 0.2},
        }
        result = validator._check_promised_assets_exist(
            [mock_asset_seo], mock_diagnostic, generated_assets=generated_assets
        )
        # whatsapp_button has can_use=False → should be counted as missing
        assert result.passed is False
        assert result.score < 1.0

    def test_generated_assets_missing_type_defaults_to_false(self, validator, mock_asset_seo, mock_diagnostic):
        """Asset type not in generated_assets → treated as can_use=False."""
        generated_assets = {
            'optimization_guide': {'can_use': True},
            # All others NOT present → defaults to False
        }
        result = validator._check_promised_assets_exist(
            [mock_asset_seo], mock_diagnostic, generated_assets=generated_assets
        )
        # Only 1/7 can_use=True → score = 1/7 ≈ 0.14
        expected_score = 1 / len(PROPOSAL_SERVICE_TO_ASSET)
        assert abs(result.score - expected_score) < 0.01
        assert result.passed is False