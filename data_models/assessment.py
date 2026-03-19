"""
Modelos de datos para el sistema de validación y análisis.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from enums.types import Severity, ConfidenceLevel


@dataclass
class Evidence:
    """Evidencia que respalda o refuta un claim."""
    source: str
    value: Any
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict = field(default_factory=dict)


@dataclass
class Claim:
    """Afirmación sobre un dato del hotel que requiere validación."""
    field: str
    value: Any
    confidence: ConfidenceLevel
    sources: list[str] = field(default_factory=list)
    evidence: list[Evidence] = field(default_factory=list)
    severity: Severity = Severity.INFO


@dataclass
class CanonicalAssessment:
    """Evaluación canónica consolidada de un hotel."""
    hotel_name: str
    url: str
    claims: list[Claim] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.now)
    version: str = "1.0.0"
