"""Tests para calibracion de confianza."""

import pytest
from observability.calibration import ConfidenceCalibrator, CalibrationResult


class TestConfidenceCalibrator:
    """Tests para ConfidenceCalibrator."""
    
    @pytest.fixture
    def calibrator(self):
        return ConfidenceCalibrator()
    
    def test_calculate_precision_recall(self, calibrator):
        # Crear datos de prueba
        class MockRun:
            def __init__(self, level):
                self.confidence_level = level
        
        runs = [
            MockRun("VERIFIED"),
            MockRun("VERIFIED"),
            MockRun("ESTIMATED"),
            MockRun("CONFLICT")
        ]
        
        result = calibrator.calculate_metrics(runs)
        
        assert isinstance(result, CalibrationResult)
        assert result.precision_verified > 0
        assert result.recall_verified > 0
    
    def test_recommend_threshold_adjustments(self, calibrator):
        # Caso con precision baja en VERIFIED
        result = CalibrationResult(
            precision_verified=0.85,  # Bajo, deberia ser >0.9
            precision_estimated=0.75,
            precision_conflict=0.3,
            recall_verified=0.9,
            recall_estimated=0.1,
            recall_conflict=0.05,
            recommended_thresholds={},
            confidence=0.8
        )
        
        recommendations = calibrator.recommend_adjustments(result)
        
        # Debe sugerir ajuste
        assert len(recommendations) > 0
        assert any("VERIFIED" in r for r in recommendations)
    
    def test_apply_calibration_updates_thresholds(self, calibrator):
        new_thresholds = {
            "verified_threshold": 0.95,
            "estimated_min": 0.6,
            "estimated_max": 0.9
        }
        
        result = calibrator.apply_calibration(new_thresholds)
        assert result is True
