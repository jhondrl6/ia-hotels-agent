"""
Tests for GBP Activity Score calculation (v2.6.2).

Validates the _calcular_activity_score method in gbp_auditor.py.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
from unittest.mock import MagicMock, patch


class TestGBPActivityScore:
    """Test cases for GBP Activity Score calculation."""

    def _create_mock_auditor(self, pesos=None):
        """Create a mock GBPAuditor with configurable weights."""
        from modules.scrapers.gbp_auditor import GBPAuditor
        
        auditor = GBPAuditor.__new__(GBPAuditor)
        auditor.benchmark_loader = MagicMock()
        
        default_pesos = {
            'posts_90d_peso': 0.35,
            'posts_90d_max': 5,
            'fotos_mes_peso': 0.25,
            'fotos_meta': 15,
            'reviews_response_peso': 0.40,
        }
        auditor.benchmark_loader.get_activity_weights.return_value = pesos or default_pesos
        return auditor

    def test_hotel_visperas_case(self):
        """Hotel Vísperas: 0 posts, 9 fotos, no response data -> should be ~15/100."""
        auditor = self._create_mock_auditor()
        
        profile_data = {
            'posts': 0,
            'fotos': 9,
            'reviews': 29,
            'meta': {}  # No response data
        }
        
        score = auditor._calcular_activity_score(profile_data)
        
        # Expected: 0% posts (0/5) + 60% fotos (9/15) + 0% reviews = 0*0.35 + 0.6*0.25 + 0 = 0.15 = 15
        assert score == 15, f"Expected 15, got {score}"

    def test_active_hotel(self):
        """Hotel with good activity: 5 posts, 20 fotos, 50% response rate."""
        auditor = self._create_mock_auditor()
        
        profile_data = {
            'posts': 5,
            'fotos': 20,
            'reviews': 10,
            'meta': {
                'reviews': {
                    'responded': 5,
                    'total': 10
                }
            }
        }
        
        score = auditor._calcular_activity_score(profile_data)
        
        # Expected: 100% posts + 100% fotos (20/15 capped to 1) + 50% reviews
        # = 1*0.35 + 1*0.25 + 0.5*0.40 = 0.35 + 0.25 + 0.20 = 0.80 = 80
        assert score == 80, f"Expected 80, got {score}"

    def test_perfect_activity(self):
        """Hotel with perfect activity: max posts, max fotos, 100% responses."""
        auditor = self._create_mock_auditor()
        
        profile_data = {
            'posts': 5,
            'fotos': 15,
            'reviews': 10,
            'meta': {
                'reviews': {
                    'responded': 10,
                    'total': 10
                }
            }
        }
        
        score = auditor._calcular_activity_score(profile_data)
        
        # Expected: 100% all = 1*0.35 + 1*0.25 + 1*0.40 = 1.0 = 100
        assert score == 100, f"Expected 100, got {score}"

    def test_zero_fotos_still_contributes_posts(self):
        """Hotel with 0 fotos but 3 posts should still get partial score."""
        auditor = self._create_mock_auditor()
        
        profile_data = {
            'posts': 3,
            'fotos': 0,
            'reviews': 0,
            'meta': {}
        }
        
        score = auditor._calcular_activity_score(profile_data)
        
        # Expected: 60% posts (3/5) + 0% fotos + 0% reviews = 0.6*0.35 = 0.21 = 21
        assert score == 21, f"Expected 21, got {score}"

    def test_fallback_when_no_weights(self):
        """Should return 100 when benchmark weights are not available."""
        auditor = self._create_mock_auditor(pesos=None)
        auditor.benchmark_loader.get_activity_weights.return_value = None
        
        profile_data = {'posts': 0, 'fotos': 0}
        
        score = auditor._calcular_activity_score(profile_data)
        
        assert score == 100, f"Expected fallback 100, got {score}"

    def test_fotos_above_meta_caps_at_100_percent(self):
        """Fotos > fotos_meta should cap contribution at 100%."""
        auditor = self._create_mock_auditor()
        
        profile_data = {
            'posts': 0,
            'fotos': 30,  # 200% of meta
            'reviews': 0,
            'meta': {}
        }
        
        score = auditor._calcular_activity_score(profile_data)
        
        # Expected: 0% posts + 100% fotos (capped) + 0% reviews = 0.25 = 25
        assert score == 25, f"Expected 25, got {score}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
