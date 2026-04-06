"""Calibracion de Confianza - Ajuste de Umbrales.

Este modulo implementa la calibracion de confianza basada en
performance historico para ajustar umbrales de confianza.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime


@dataclass
class CalibrationResult:
    """Resultado de calibracion de confianza."""
    precision_verified: float
    precision_estimated: float
    precision_conflict: float
    recall_verified: float
    recall_estimated: float
    recall_conflict: float
    recommended_thresholds: Dict[str, float]
    confidence: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "precision_verified": self.precision_verified,
            "precision_estimated": self.precision_estimated,
            "precision_conflict": self.precision_conflict,
            "recall_verified": self.recall_verified,
            "recall_estimated": self.recall_estimated,
            "recall_conflict": self.recall_conflict,
            "recommended_thresholds": self.recommended_thresholds,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat()
        }


class ConfidenceCalibrator:
    """Calibrador de confianza para ajuste de umbrales."""
    
    def __init__(self):
        self._historical_data: List[Dict] = []
    
    def add_historical_result(self, predicted_level: str, actual_accuracy: float) -> None:
        """Agrega un resultado historico."""
        self._historical_data.append({
            "predicted_level": predicted_level,
            "actual_accuracy": actual_accuracy,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def calculate_metrics(self, runs: List[Any]) -> CalibrationResult:
        """Calcula metricas de precision/recall por nivel."""
        # Contar por nivel
        verified_total = sum(1 for r in runs if getattr(r, "confidence_level", "") == "VERIFIED")
        estimated_total = sum(1 for r in runs if getattr(r, "confidence_level", "") == "ESTIMATED")
        conflict_total = sum(1 for r in runs if getattr(r, "confidence_level", "") == "CONFLICT")
        
        total = len(runs) if runs else 1
        
        # Calcular precision (simulado - en produccion usaria ground truth)
        precision_verified = 0.95 if verified_total > 0 else 0.0
        precision_estimated = 0.75 if estimated_total > 0 else 0.0
        precision_conflict = 0.30 if conflict_total > 0 else 0.0
        
        # Calcular recall
        recall_verified = verified_total / total
        recall_estimated = estimated_total / total
        recall_conflict = conflict_total / total
        
        # Umbral de confianza general
        confidence = (precision_verified * 0.5 + precision_estimated * 0.3 + precision_conflict * 0.2)
        
        # Recomendaciones
        recommended = {
            "verified_threshold": 0.9,
            "estimated_min": 0.5,
            "estimated_max": 0.9,
            "conflict_threshold": 0.5
        }
        
        return CalibrationResult(
            precision_verified=precision_verified,
            precision_estimated=precision_estimated,
            precision_conflict=precision_conflict,
            recall_verified=recall_verified,
            recall_estimated=recall_estimated,
            recall_conflict=recall_conflict,
            recommended_thresholds=recommended,
            confidence=confidence
        )
    
    def recommend_adjustments(self, current_metrics: CalibrationResult) -> List[str]:
        """Genera recomendaciones de ajuste."""
        recommendations = []
        
        if current_metrics.precision_verified < 0.9:
            recommendations.append("Aumentar umbral VERIFIED a >0.95")
        
        if current_metrics.precision_estimated < 0.7:
            recommendations.append("Revisar rangos ESTIMATED (0.5-0.9)")
        
        if current_metrics.recall_conflict > 0.1:
            recommendations.append("Demasiados CONFLICT - revisar validadores")
        
        if not recommendations:
            recommendations.append("Umbrales actuales son adecuados")
        
        return recommendations
    
    def apply_calibration(self, new_thresholds: Dict[str, float]) -> bool:
        """Aplica nuevos umbrales de calibracion."""
        # En implementacion real, guardaria en configuracion
        return True