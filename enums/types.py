"""
Enums para tipos de datos del sistema de validación.
"""
from enum import Enum, auto


class Severity(Enum):
    """Niveles de severidad para issues y claims."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ConfidenceLevel(Enum):
    """Niveles de confianza para datos y validaciones."""
    VERIFIED = 0.9
    ESTIMATED = 0.6
    CONFLICT = 0.3
    UNVERIFIED = 0.0
