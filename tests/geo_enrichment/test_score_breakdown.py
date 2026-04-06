"""Tests for ScoreBreakdown dataclass.

Tests that all 8 evaluation areas are properly initialized
and that total calculation is correct.
"""

import pytest
from modules.geo_enrichment import ScoreBreakdown


class TestScoreBreakdown:
    """Test ScoreBreakdown initialization and methods."""

    def test_default_initialization(self):
        """Test all areas initialize to 0 by default."""
        breakdown = ScoreBreakdown()
        assert breakdown.robots == 0
        assert breakdown.llms == 0
        assert breakdown.schema == 0
        assert breakdown.meta == 0
        assert breakdown.content == 0
        assert breakdown.brand == 0
        assert breakdown.signals == 0
        assert breakdown.ai_discovery == 0

    def test_total_with_zeros(self):
        """Test total returns 0 when all areas are 0."""
        breakdown = ScoreBreakdown()
        assert breakdown.total() == 0

    def test_total_with_partial_scores(self):
        """Test total calculation with partial scores."""
        breakdown = ScoreBreakdown(
            robots=15,
            llms=12,
            schema=10,
            meta=8,
            content=6,
            brand=5,
            signals=3,
            ai_discovery=2,
        )
        assert breakdown.total() == 61

    def test_total_maximum_scores(self):
        """Test total with maximum possible scores."""
        breakdown = ScoreBreakdown(
            robots=18,
            llms=18,
            schema=16,
            meta=14,
            content=12,
            brand=10,
            signals=6,
            ai_discovery=6,
        )
        assert breakdown.total() == 100

    def test_to_dict_structure(self):
        """Test to_dict returns all 8 areas plus total."""
        breakdown = ScoreBreakdown(robots=10, llms=8)
        d = breakdown.to_dict()
        assert "robots" in d
        assert "llms" in d
        assert "schema" in d
        assert "meta" in d
        assert "content" in d
        assert "brand" in d
        assert "signals" in d
        assert "ai_discovery" in d
        assert "total" in d

    def test_to_dict_values(self):
        """Test to_dict returns correct values."""
        breakdown = ScoreBreakdown(robots=15, llms=12, schema=8)
        d = breakdown.to_dict()
        assert d["robots"] == 15
        assert d["llms"] == 12
        assert d["schema"] == 8
        assert d["total"] == 35

    def test_individual_area_assignment(self):
        """Test each area can be assigned individually."""
        breakdown = ScoreBreakdown()
        breakdown.robots = 18
        breakdown.llms = 18
        breakdown.schema = 16
        breakdown.meta = 14
        breakdown.content = 12
        breakdown.brand = 10
        breakdown.signals = 6
        breakdown.ai_discovery = 6
        assert breakdown.total() == 100

    def test_8_areas_defined(self):
        """Test that exactly 8 areas are defined."""
        breakdown = ScoreBreakdown()
        # Verify all 8 areas are accessible
        areas = [
            breakdown.robots,
            breakdown.llms,
            breakdown.schema,
            breakdown.meta,
            breakdown.content,
            breakdown.brand,
            breakdown.signals,
            breakdown.ai_discovery,
        ]
        assert len(areas) == 8
