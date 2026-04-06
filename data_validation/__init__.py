"""Data Validation Module - Motor de Contradicciones y Consistencia."""

# Validadores operativos
from .metadata_validator import MetadataValidator, DEFAULT_WORDPRESS_STRINGS

# Motor de contradicciones
from .contradiction_engine import (
    ContradictionEngine,
    Conflict,
    ConflictType,
    Claim
)
from .consistency_checker import (
    ConsistencyChecker,
    ConsistencyReport,
    CanonicalAssessment
)

__all__ = [
    # Validadores
    'MetadataValidator',
    'DEFAULT_WORDPRESS_STRINGS',
    # Contradicciones
    'ContradictionEngine',
    'Conflict',
    'ConflictType',
    'Claim',
    'ConsistencyChecker',
    'ConsistencyReport',
    'CanonicalAssessment',
]
