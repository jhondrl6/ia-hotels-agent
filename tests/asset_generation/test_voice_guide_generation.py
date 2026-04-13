"""Tests for voice_assistant_guide asset generation.

Validates that voice_assistant_guide:
- Is in the catalog as IMPLEMENTED
- Has promised_by entries (not empty)
- Generates content even without specific pain detection
"""

import pytest
from modules.asset_generation.asset_catalog import ASSET_CATALOG, AssetStatus
from modules.asset_generation.conditional_generator import ConditionalGenerator


class TestVoiceAssistantGuideCatalog:
    """Test voice_assistant_guide catalog entry."""

    def test_voice_guide_exists_in_catalog(self):
        """voice_assistant_guide must exist in the catalog."""
        assert "voice_assistant_guide" in ASSET_CATALOG

    def test_voice_guide_is_implemented(self):
        """voice_assistant_guide must be IMPLEMENTED."""
        entry = ASSET_CATALOG["voice_assistant_guide"]
        assert entry.status == AssetStatus.IMPLEMENTED

    def test_voice_guide_has_promised_by(self):
        """voice_assistant_guide promised_by must NOT be empty."""
        entry = ASSET_CATALOG["voice_assistant_guide"]
        assert len(entry.promised_by) > 0

    def test_voice_guide_promised_by_aeo(self):
        """voice_assistant_guide promised_by should include 'always_aeo' for AEO coverage."""
        entry = ASSET_CATALOG["voice_assistant_guide"]
        assert "always_aeo" in entry.promised_by

    def test_voice_guide_not_blocking(self):
        """voice_assistant_guide must not block on failure."""
        entry = ASSET_CATALOG["voice_assistant_guide"]
        assert entry.block_on_failure is False


class TestVoiceAssistantGuideGeneration:
    """Test voice_assistant_guide content generation."""

    def test_voice_guide_generates_content(self, tmp_path):
        """voice_assistant_guide should generate valid content."""
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
        assert result["success"] is True
        assert result["status"] in ("success", "warning")

    def test_voice_guide_generates_without_specific_pain(self, tmp_path):
        """voice_assistant_guide should generate even without pain detection trigger."""
        gen = ConditionalGenerator(output_dir=str(tmp_path))
        # Minimal data — no specific voice readiness pain
        result = gen.generate(
            asset_type="voice_assistant_guide",
            validated_data={},
            hotel_name="Basic Hotel",
            hotel_id="basic_hotel",
        )
        assert result["success"] is True

    def test_voice_guide_in_generation_strategies(self):
        """voice_assistant_guide must be in GENERATION_STRATEGIES."""
        gen = ConditionalGenerator()
        assert "voice_assistant_guide" in gen.GENERATION_STRATEGIES
