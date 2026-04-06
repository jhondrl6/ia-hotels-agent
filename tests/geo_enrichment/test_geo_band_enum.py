"""Tests for GEOBand enum classification.

Tests that the 4 GEO bands are correctly defined and
that from_score() method properly classifies scores.
"""

import pytest
from modules.geo_enrichment import GEOBand


class TestGEOBandEnum:
    """Test GEOBand enum values and classification."""

    def test_excellent_band_value(self):
        """Test EXCELLENT band exists with correct value."""
        assert GEOBand.EXCELLENT.value == "excellent"

    def test_good_band_value(self):
        """Test GOOD band exists with correct value."""
        assert GEOBand.GOOD.value == "good"

    def test_foundation_band_value(self):
        """Test FOUNDATION band exists with correct value."""
        assert GEOBand.FOUNDATION.value == "foundation"

    def test_critical_band_value(self):
        """Test CRITICAL band exists with correct value."""
        assert GEOBand.CRITICAL.value == "critical"

    def test_excellent_from_score_86(self):
        """Test EXCELLENT classification for score 86."""
        assert GEOBand.from_score(86) == GEOBand.EXCELLENT

    def test_excellent_from_score_100(self):
        """Test EXCELLENT classification for score 100."""
        assert GEOBand.from_score(100) == GEOBand.EXCELLENT

    def test_good_from_score_68(self):
        """Test GOOD classification for score 68."""
        assert GEOBand.from_score(68) == GEOBand.GOOD

    def test_good_from_score_85(self):
        """Test GOOD classification for score 85."""
        assert GEOBand.from_score(85) == GEOBand.GOOD

    def test_foundation_from_score_36(self):
        """Test FOUNDATION classification for score 36."""
        assert GEOBand.from_score(36) == GEOBand.FOUNDATION

    def test_foundation_from_score_67(self):
        """Test FOUNDATION classification for score 67."""
        assert GEOBand.from_score(67) == GEOBand.FOUNDATION

    def test_critical_from_score_0(self):
        """Test CRITICAL classification for score 0."""
        assert GEOBand.from_score(0) == GEOBand.CRITICAL

    def test_critical_from_score_35(self):
        """Test CRITICAL classification for score 35."""
        assert GEOBand.from_score(35) == GEOBand.CRITICAL

    def test_boundary_85_to_86(self):
        """Test boundary between GOOD and EXCELLENT."""
        assert GEOBand.from_score(85) == GEOBand.GOOD
        assert GEOBand.from_score(86) == GEOBand.EXCELLENT

    def test_boundary_67_to_68(self):
        """Test boundary between FOUNDATION and GOOD."""
        assert GEOBand.from_score(67) == GEOBand.FOUNDATION
        assert GEOBand.from_score(68) == GEOBand.GOOD

    def test_boundary_35_to_36(self):
        """Test boundary between CRITICAL and FOUNDATION."""
        assert GEOBand.from_score(35) == GEOBand.CRITICAL
        assert GEOBand.from_score(36) == GEOBand.FOUNDATION
