"""Data Validation Module - Fase 2: Motor de Contradicciones."""

# Fase 1 (existente)
from .metadata_validator import MetadataValidator, DEFAULT_WORDPRESS_STRINGS
from .schema_validator_v2 import SchemaValidatorV2

# Fase 2 (nuevo)
from .evidence_ledger import (
    EvidenceLedger,
    Evidence,
    EvidenceType
)
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
    # Fase 1
    'MetadataValidator',
    'DEFAULT_WORDPRESS_STRINGS',
    'SchemaValidatorV2',
    # Fase 2
    'EvidenceLedger',
    'Evidence',
    'EvidenceType',
    'ContradictionEngine',
    'Conflict',
    'ConflictType',
    'Claim',
    'ConsistencyChecker',
    'ConsistencyReport',
    'CanonicalAssessment',
]