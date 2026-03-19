"""Modelo de datos para claims de validación.

Define la estructura de un claim, que representa una afirmación
sobre un dato específico del hotel con su evidencia y nivel de confianza.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional, Any
from uuid import UUID, uuid4
import json

from enums.severity import Severity
from enums.confidence_level import ConfidenceLevel


@dataclass
class Claim:
    """Representa un claim de validación con evidencia y metadata.

    Un claim es una afirmación verificable sobre un aspecto específico
    del hotel (metadata, schema, performance, etc.) con su nivel de
    confianza y evidencia asociada.

    Attributes:
        claim_id: UUID único del claim.
        source_id: Fuente de evidencia (string identificador).
        timestamp: Fecha/hora de creación en formato ISO 8601.
        confidence: Score de confianza entre 0.0 y 1.0.
        evidence_excerpt: Extracto verificable de la evidencia.
        severity: Nivel de severidad del claim.
        category: Categoría del claim (ej: "metadata", "schema").
        message: Descripción legible del claim.
        field_path: Ruta del campo afectado (opcional).
        raw_evidence: Datos crudos de la evidencia (opcional).
    """

    # Campos obligatorios
    source_id: str
    evidence_excerpt: str
    severity: Severity
    category: str
    message: str

    # Campos con defaults
    claim_id: UUID = field(default_factory=uuid4)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    confidence: float = 0.0

    # Campos opcionales
    field_path: Optional[str] = None
    raw_evidence: Optional[dict[str, Any]] = None

    def __post_init__(self):
        """Validaciones post-inicialización."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                f"Confidence must be between 0.0 and 1.0, got {self.confidence}"
            )
        if not self.source_id:
            raise ValueError("source_id is required")
        if not self.evidence_excerpt:
            raise ValueError("evidence_excerpt is required")
        if not self.message:
            raise ValueError("message is required")
        if not self.category:
            raise ValueError("category is required")

    @property
    def confidence_level(self) -> ConfidenceLevel:
        """Determina el nivel de confianza basado en el score.

        Returns:
            ConfidenceLevel: Nivel de confianza correspondiente.
        """
        return ConfidenceLevel.from_score(self.confidence)

    @property
    def is_actionable(self) -> bool:
        """Indica si el claim requiere acción.

        Returns:
            bool: True si el claim requiere acción.
        """
        return self.severity in (Severity.CRITICAL, Severity.HIGH)

    @property
    def is_verified(self) -> bool:
        """Indica si el claim está verificado (confianza ≥ 0.9).

        Returns:
            bool: True si está verificado.
        """
        return self.confidence >= 0.9

    @property
    def blocks_deployment(self) -> bool:
        """Indica si el claim bloquea publicación.

        Returns:
            bool: True si es severidad CRITICAL.
        """
        return self.severity == Severity.CRITICAL

    def to_dict(self) -> dict[str, Any]:
        """Serializa el claim a diccionario.

        Returns:
            dict: Representación del claim como diccionario.
        """
        data = asdict(self)
        # Convertir tipos no serializables
        data["claim_id"] = str(self.claim_id)
        data["timestamp"] = self.timestamp.isoformat()
        data["severity"] = self.severity.value
        data["confidence_level"] = self.confidence_level.value
        data["is_actionable"] = self.is_actionable
        data["is_verified"] = self.is_verified
        data["blocks_deployment"] = self.blocks_deployment
        return data

    def to_json(self) -> str:
        """Serializa el claim a JSON.

        Returns:
            str: Representación JSON del claim.
        """
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Claim":
        """Crea un Claim desde un diccionario.

        Args:
            data: Diccionario con los datos del claim.

        Returns:
            Claim: Instancia de Claim.
        """
        claim_data = data.copy()

        if isinstance(claim_data.get("claim_id"), str):
            claim_data["claim_id"] = UUID(claim_data["claim_id"])

        if isinstance(claim_data.get("timestamp"), str):
            claim_data["timestamp"] = datetime.fromisoformat(claim_data["timestamp"])

        if isinstance(claim_data.get("severity"), str):
            claim_data["severity"] = Severity(claim_data["severity"])

        # Remover campos calculados si existen
        claim_data.pop("confidence_level", None)
        claim_data.pop("is_actionable", None)
        claim_data.pop("is_verified", None)
        claim_data.pop("blocks_deployment", None)

        return cls(**claim_data)

    @classmethod
    def from_json(cls, json_str: str) -> "Claim":
        """Crea un Claim desde un string JSON.

        Args:
            json_str: String JSON con los datos del claim.

        Returns:
            Claim: Instancia de Claim.
        """
        data = json.loads(json_str)
        return cls.from_dict(data)

    def __str__(self) -> str:
        """Representación string del claim.

        Returns:
            str: Representación legible del claim.
        """
        return f"Claim({self.category}:{self.severity.value}) {self.message[:50]}..."

    def __hash__(self) -> int:
        """Hash basado en claim_id para uso en sets/dicts.

        Returns:
            int: Hash del claim_id.
        """
        return hash(self.claim_id)

    def __eq__(self, other: object) -> bool:
        """Comparación de igualdad basada en claim_id.

        Args:
            other: Otro objeto a comparar.

        Returns:
            bool: True si son iguales.
        """
        if not isinstance(other, Claim):
            return NotImplemented
        return self.claim_id == other.claim_id
