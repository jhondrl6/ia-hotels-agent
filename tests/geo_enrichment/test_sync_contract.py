"""Tests for SyncContractAnalyzer.

Reference: FASE-4 prompt - Tests Obligatorios
"""

import pytest
from dataclasses import dataclass
from typing import List

# Import from geo_enrichment module
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from modules.geo_enrichment.sync_contract import (
    SyncContractAnalyzer,
    SyncResult,
    GEOBand,
    LossLevel,
    analyze_sync,
    LOSS_THRESHOLD
)


# =============================================================================
# MOCK GEO ASSESSMENT
# =============================================================================

class MockBreakdown:
    """Mock breakdown for testing."""
    def __init__(self, **scores):
        self.robots = scores.get("robots", 10)
        self.llms = scores.get("llms", 10)
        self.schema = scores.get("schema", 10)
        self.meta = scores.get("meta", 10)
        self.content = scores.get("content", 10)
        self.brand = scores.get("brand", 10)
        self.signals = scores.get("signals", 10)
        self.ai_discovery = scores.get("ai_discovery", 10)
    
    def total(self):
        return (
            self.robots + self.llms + self.schema + self.meta +
            self.content + self.brand + self.signals + self.ai_discovery
        )


class MockGeoAssessment:
    """Mock GEOAssessment for testing."""
    def __init__(
        self,
        total_score: int,
        band: GEOBand,
        gaps_blocking: List[str] = None,
        recommendations: List[str] = None
    ):
        self.total_score = total_score
        self.band = band
        self.gaps_blocking = gaps_blocking or []
        self.recommendations = recommendations or []
        self.site_url = "https://example.com"
        self.breakdown = MockBreakdown()


# =============================================================================
# TEST: EXCELLENT + ALTA = "Problema es comercial, no técnico"
# =============================================================================

class TestSyncExcellentAlta:
    """Test case A1: EXCELLENT band with ALTA loss."""
    
    def test_sync_excellent_alta(self):
        """Tag should be 'Problema es comercial, no técnico'."""
        commercial = {
            "perdida_mensual_total": 8_000_000,  # > 5M threshold
            "paquete_recomendado": "Starter",
            "metricas_clave": {"reservas_perdidas_mes": 20}
        }
        geo = MockGeoAssessment(total_score=92, band=GEOBand.EXCELLENT)
        
        analyzer = SyncContractAnalyzer()
        result = analyzer.analyze(commercial, geo)
        
        assert result.is_consistent is True
        assert result.combination_tag == "Problema es comercial, no técnico"
        assert result.sync_score == 0.95
        assert "comercial" in result.recommendation.lower()
        assert "técnico" in result.recommendation.lower() or "técnica" in result.recommendation.lower()


# =============================================================================
# TEST: EXCELLENT + BAJA = "Hotel en buen estado técnico"
# =============================================================================

class TestSyncExcellentBaja:
    """Test case A2: EXCELLENT band with BAJA loss."""
    
    def test_sync_excellent_baja(self):
        """Tag should be 'Hotel en buen estado técnico'."""
        commercial = {
            "perdida_mensual_total": 2_000_000,  # < 5M threshold
            "paquete_recomendado": "Starter",
            "metricas_clave": {}
        }
        geo = MockGeoAssessment(total_score=88, band=GEOBand.EXCELLENT)
        
        analyzer = SyncContractAnalyzer()
        result = analyzer.analyze(commercial, geo)
        
        assert result.is_consistent is True
        assert result.combination_tag == "Hotel en buen estado técnico"
        assert result.sync_score == 1.0


# =============================================================================
# TEST: GOOD + ALTA = "Brecha técnica contribuye"
# =============================================================================

class TestSyncGoodAlta:
    """Test case B1: GOOD band with ALTA loss."""
    
    def test_sync_good_alta(self):
        """Tag should be 'Brecha técnica contribuye'."""
        commercial = {
            "perdida_mensual_total": 6_900_000,
            "paquete_recomendado": "Pro",
            "metricas_clave": {"reservas_perdidas_mes": 18}
        }
        geo = MockGeoAssessment(
            total_score=78,
            band=GEOBand.GOOD,
            gaps_blocking=["Falta llms.txt"]
        )
        
        analyzer = SyncContractAnalyzer()
        result = analyzer.analyze(commercial, geo)
        
        assert result.is_consistent is True
        assert result.combination_tag == "Brecha técnica contribuye"
        assert result.sync_score == 0.85


# =============================================================================
# TEST: FOUNDATION + ALTA = "Brecha técnica confirma pérdida"
# =============================================================================

class TestSyncFoundationAlta:
    """Test case C1: FOUNDATION band with ALTA loss."""
    
    def test_sync_foundation_alta(self):
        """Tag should be 'Brecha técnica confirma pérdida'."""
        commercial = {
            "perdida_mensual_total": 7_500_000,
            "paquete_recomendado": "Elite",
            "metricas_clave": {"reservas_perdidas_mes": 25}
        }
        geo = MockGeoAssessment(
            total_score=55,
            band=GEOBand.FOUNDATION,
            gaps_blocking=["Sin robots.txt", "Schema incompleto"]
        )
        
        analyzer = SyncContractAnalyzer()
        result = analyzer.analyze(commercial, geo)
        
        assert result.is_consistent is True
        assert result.combination_tag == "Brecha técnica confirma pérdida"
        assert result.sync_score == 0.8
        assert "priorizar" in result.recommendation.lower() or "urgencia" in result.recommendation.lower()


# =============================================================================
# TEST: CRITICAL + ALTA = "Crisis técnica confirma pérdida"
# =============================================================================

class TestSyncCriticalAlta:
    """Test case D1: CRITICAL band with ALTA loss."""
    
    def test_sync_critical_alta(self):
        """Tag should be 'Crisis técnica confirma pérdida'."""
        commercial = {
            "perdida_mensual_total": 9_000_000,
            "paquete_recomendado": "Elite PLUS",
            "metricas_clave": {"reservas_perdidas_mes": 30}
        }
        geo = MockGeoAssessment(
            total_score=28,
            band=GEOBand.CRITICAL,
            gaps_blocking=["Sin llms.txt", "robots.txt bloquea IA", "Schema ausente"]
        )
        
        analyzer = SyncContractAnalyzer()
        result = analyzer.analyze(commercial, geo)
        
        assert result.is_consistent is True
        assert result.combination_tag == "Crisis técnica confirma pérdida"
        assert result.sync_score == 0.75


# =============================================================================
# TEST: FOUNDATION + BAJA = Inconsistencia
# =============================================================================

class TestSyncInconsistency:
    """Test case C2: FOUNDATION band with BAJA loss - inconsistency."""
    
    def test_sync_foundation_baja_inconsistency(self):
        """Should detect inconsistency and report."""
        commercial = {
            "perdida_mensual_total": 1_500_000,  # < 5M
            "paquete_recomendado": "Starter",
            "metricas_clave": {}
        }
        geo = MockGeoAssessment(
            total_score=42,
            band=GEOBand.FOUNDATION,
            gaps_blocking=["Sin llms.txt", "robots.txt bloquea IA"]
        )
        
        analyzer = SyncContractAnalyzer()
        result = analyzer.analyze(commercial, geo)
        
        assert result.is_consistent is False
        assert result.combination_tag == "Inconsistencia - investigar"
        assert result.sync_score == 0.4
        assert result.contradiction_report is not None
        assert result.contradiction_report["type"] == "inconsistency"
        assert result.contradiction_report["action"] == "investigar"


# =============================================================================
# TEST: CRITICAL + BAJA = Error
# =============================================================================

class TestSyncCriticalBajaError:
    """Test case D2: CRITICAL band with BAJA loss - error."""
    
    def test_sync_critical_baja_error(self):
        """Should detect error and report."""
        commercial = {
            "perdida_mensual_total": 800_000,  # < 5M
            "paquete_recomendado": "Starter",
            "metricas_clave": {}
        }
        geo = MockGeoAssessment(
            total_score=22,
            band=GEOBand.CRITICAL,
            gaps_blocking=["Sin llms.txt", "robots.txt bloquea IA", "Schema ausente"]
        )
        
        analyzer = SyncContractAnalyzer()
        result = analyzer.analyze(commercial, geo)
        
        assert result.is_consistent is False
        assert result.combination_tag == "Error - verificar datos"
        assert result.sync_score == 0.2
        assert result.contradiction_report is not None
        assert result.contradiction_report["type"] == "error"
        assert result.contradiction_report["action"] == "verificar_datos"


# =============================================================================
# TEST: All 8 Combinations
# =============================================================================

class TestAllCombinations:
    """Test all 8 combinations of GEO band × Loss level."""
    
    @pytest.mark.parametrize("band,loss_level,expected_tag", [
        (GEOBand.EXCELLENT, LossLevel.ALTA, "Problema es comercial, no técnico"),
        (GEOBand.EXCELLENT, LossLevel.BAJA, "Hotel en buen estado técnico"),
        (GEOBand.GOOD, LossLevel.ALTA, "Brecha técnica contribuye"),
        (GEOBand.GOOD, LossLevel.BAJA, "Hotel en buen estado"),
        (GEOBand.FOUNDATION, LossLevel.ALTA, "Brecha técnica confirma pérdida"),
        (GEOBand.FOUNDATION, LossLevel.BAJA, "Inconsistencia - investigar"),
        (GEOBand.CRITICAL, LossLevel.ALTA, "Crisis técnica confirma pérdida"),
        (GEOBand.CRITICAL, LossLevel.BAJA, "Error - verificar datos"),
    ])
    def test_all_combinations(self, band, loss_level, expected_tag):
        """Test each combination returns correct tag."""
        commercial = {
            "perdida_mensual_total": 10_000_000 if loss_level == LossLevel.ALTA else 1_000_000,
            "paquete_recomendado": "Pro",
            "metricas_clave": {}
        }
        
        scores = {
            GEOBand.EXCELLENT: 92,
            GEOBand.GOOD: 78,
            GEOBand.FOUNDATION: 55,
            GEOBand.CRITICAL: 25,
        }
        geo = MockGeoAssessment(total_score=scores[band], band=band)
        
        analyzer = SyncContractAnalyzer()
        result = analyzer.analyze(commercial, geo)
        
        assert result.combination_tag == expected_tag


# =============================================================================
# TEST: Loss Classification Thresholds
# =============================================================================

class TestLossClassification:
    """Test loss level classification."""
    
    def test_exactly_threshold_is_alta(self):
        """Exactly at threshold should be ALTA."""
        commercial = {"perdida_mensual_total": LOSS_THRESHOLD}
        geo = MockGeoAssessment(total_score=50, band=GEOBand.FOUNDATION)
        
        analyzer = SyncContractAnalyzer()
        result = analyzer.analyze(commercial, geo)
        
        assert result.combination_tag in ["Brecha técnica confirma pérdida", "Crisis técnica confirma pérdida"]
    
    def test_just_below_threshold_is_baja(self):
        """Just below threshold should be BAJA."""
        commercial = {"perdida_mensual_total": LOSS_THRESHOLD - 1}
        geo = MockGeoAssessment(total_score=50, band=GEOBand.FOUNDATION)
        
        analyzer = SyncContractAnalyzer()
        result = analyzer.analyze(commercial, geo)
        
        assert result.combination_tag == "Inconsistencia - investigar"
    
    def test_zero_loss_unknown(self):
        """Zero loss should be handled gracefully."""
        commercial = {"perdida_mensual_total": 0}
        geo = MockGeoAssessment(total_score=50, band=GEOBand.FOUNDATION)
        
        analyzer = SyncContractAnalyzer()
        result = analyzer.analyze(commercial, geo)
        
        # Unknown loss with FOUNDATION = investigate
        assert result.combination_tag == "Inconsistencia - investigar"


# =============================================================================
# TEST: get_sync_summary
# =============================================================================

class TestSyncSummary:
    """Test the get_sync_summary helper method."""
    
    def test_sync_summary_consistent(self):
        """Summary should format consistent result correctly."""
        commercial = {"perdida_mensual_total": 8_000_000, "paquete_recomendado": "Pro", "metricas_clave": {}}
        geo = MockGeoAssessment(total_score=78, band=GEOBand.GOOD)
        
        analyzer = SyncContractAnalyzer()
        result = analyzer.analyze(commercial, geo)
        summary = analyzer.get_sync_summary(result)
        
        assert "Consistente: ✅ Sí" in summary
        assert "Brecha técnica contribuye" in summary
        assert "Sync Score: 0.85" in summary
    
    def test_sync_summary_inconsistent(self):
        """Summary should format inconsistent result correctly."""
        commercial = {"perdida_mensual_total": 1_500_000, "paquete_recomendado": "Starter", "metricas_clave": {}}
        geo = MockGeoAssessment(total_score=42, band=GEOBand.FOUNDATION)
        
        analyzer = SyncContractAnalyzer()
        result = analyzer.analyze(commercial, geo)
        summary = analyzer.get_sync_summary(result)
        
        assert "Consistente: ❌ No" in summary
        assert "Inconsistencia" in summary


# =============================================================================
# TEST: Convenience Function
# =============================================================================

class TestConvenienceFunction:
    """Test the analyze_sync convenience function."""
    
    def test_analyze_sync_convenience(self):
        """analyze_sync should work as convenience function."""
        commercial = {"perdida_mensual_total": 8_000_000, "paquete_recomendado": "Pro", "metricas_clave": {}}
        geo = MockGeoAssessment(total_score=28, band=GEOBand.CRITICAL)
        
        result = analyze_sync(commercial, geo)
        
        assert isinstance(result, SyncResult)
        assert result.combination_tag == "Crisis técnica confirma pérdida"


# =============================================================================
# TEST: GEO Band Extraction
# =============================================================================

class TestGeoBandExtraction:
    """Test extraction of GEO band from various formats."""
    
    def test_band_from_string(self):
        """Should handle band stored as string."""
        commercial = {"perdida_mensual_total": 5_000_000, "paquete_recomendado": "Pro", "metricas_clave": {}}
        
        class StringBandAssessment:
            band = "excellent"
            total_score = 90
        
        analyzer = SyncContractAnalyzer()
        result = analyzer.analyze(commercial, StringBandAssessment())
        
        assert result.combination_tag == "Problema es comercial, no técnico"
    
    def test_band_from_enum_value(self):
        """Should handle band as Enum with value."""
        commercial = {"perdida_mensual_total": 5_000_000, "paquete_recomendado": "Pro", "metricas_clave": {}}
        
        class EnumValueAssessment:
            class band:
                value = "critical"
            total_score = 25
        
        analyzer = SyncContractAnalyzer()
        result = analyzer.analyze(commercial, EnumValueAssessment())
        
        assert result.combination_tag == "Crisis técnica confirma pérdida"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
