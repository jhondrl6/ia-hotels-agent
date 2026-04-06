"""Observability - Dashboard de Calidad y Calibración de Confianza.

Este módulo implementa la Fase 6 del sistema: Observabilidad, Regresión y Calibración.

Componentes principales:
- QualityDashboard: Métricas por corrida y tendencias históricas
- ConfidenceCalibrator: Ajuste de umbrales basado en histórico
- AlertManager: Detección de degradación automática

Ejemplo de uso:
    >>> from observability.dashboard import QualityDashboard
    >>> dashboard = QualityDashboard()
    >>> dashboard.record_run(metrics)
    >>> alerts = dashboard.check_alerts()
"""

from .dashboard import QualityDashboard, RunMetrics, TrendReport, Alert
from .calibration import ConfidenceCalibrator, CalibrationResult

__version__ = "1.0.0"
__all__ = [
    "QualityDashboard",
    "RunMetrics",
    "TrendReport",
    "Alert",
    "ConfidenceCalibrator",
    "CalibrationResult",
]
