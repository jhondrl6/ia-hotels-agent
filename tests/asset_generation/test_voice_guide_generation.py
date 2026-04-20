"""Tests for voice_assistant_guide asset.

Validates that voice_assistant_guide:
- Exists in the catalog as DEPRECATED (FASE-5: sin brecha real)
- Has empty promised_by (no pain point justifica este asset)
- Does not block pipeline on failure
- Generation returns failure for DEPRECATED assets
"""

import pytest
from modules.asset_generation.asset_catalog import ASSET_CATALOG, AssetStatus


class TestVoiceAssistantGuideCatalog:
    """Test voice_assistant_guide catalog entry (DEPRECATED)."""

    def test_voice_guide_exists_in_catalog(self):
        """voice_assistant_guide must exist in the catalog."""
        assert "voice_assistant_guide" in ASSET_CATALOG

    def test_voice_guide_is_deprecated(self):
        """voice_assistant_guide must be DEPRECATED (FASE-5: sin brecha real)."""
        entry = ASSET_CATALOG["voice_assistant_guide"]
        assert entry.status == AssetStatus.DEPRECATED

    def test_voice_guide_promised_by_empty(self):
        """voice_assistant_guide promised_by must be empty (no pain point)."""
        entry = ASSET_CATALOG["voice_assistant_guide"]
        assert len(entry.promised_by) == 0

    def test_voice_guide_not_blocking(self):
        """voice_assistant_guide must not block on failure."""
        entry = ASSET_CATALOG["voice_assistant_guide"]
        assert entry.block_on_failure is False


class TestVoiceAssistantGuideGeneration:
    """Test voice_assistant_guide generation behavior (DEPRECATED)."""

    def test_voice_guide_not_in_generation_strategies(self):
        """DEPRECATED asset must NOT be in GENERATION_STRATEGIES."""
        from modules.asset_generation.conditional_generator import ConditionalGenerator
        gen = ConditionalGenerator()
        assert "voice_assistant_guide" not in gen.GENERATION_STRATEGIES

    def test_voice_guide_generation_skips_deprecated(self, tmp_path):
        """Generating a DEPRECATED asset should return failure or skip."""
        from modules.asset_generation.conditional_generator import ConditionalGenerator
        gen = ConditionalGenerator(output_dir=str(tmp_path))
        hotel_data = {
            "hotel_data": {
                "name": "Hotel Test",
                "city": "Pereira",
            }
        }
        result = gen.generate(
            asset_type="voice_assistant_guide",
            validated_data=hotel_data,
            hotel_name="Hotel Test",
            hotel_id="test_hotel",
        )
        # DEPRECATED assets should not succeed
        assert result.get("success") is not True
