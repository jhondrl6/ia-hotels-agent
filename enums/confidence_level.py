"""Enum de niveles de confianza para validación de datos.

Define los niveles de confianza basados en el score numérico
y la cantidad de fuentes de evidencia que respaldan un claim.
"""

from enum import Enum
from typing import Optional


class ConfidenceLevel(Enum):
    """Niveles de confianza para validación de claims.

    Los niveles se determinan por el score de confianza (0.0-1.0)
    y la consistencia entre múltiples fuentes de evidencia.

    Attributes:
        VERIFIED: Score ≥ 0.9, 2+ fuentes coinciden.
        ESTIMATED: Score 0.5-0.9, 1 fuente o benchmark.
        CONFLICT: Score < 0.5, fuentes contradicen.
        INSUFFICIENT: No hay evidencia disponible.
    """

    VERIFIED = "verified"
    """Score ≥ 0.9. 2+ fuentes independientes coinciden."""

    ESTIMATED = "estimated"
    """Score 0.5-0.9. 1 fuente o benchmark regional."""

    CONFLICT = "conflict"
    """Score < 0.5. Fuentes se contradicen."""

    INSUFFICIENT = "insufficient"
    """Sin datos o evidencia inadecuada."""

    @classmethod
    def from_score(cls, score: Optional[float]) -> "ConfidenceLevel":
        """Determina el nivel de confianza basado en un score numérico.

        Args:
            score: Score de confianza entre 0.0 y 1.0, o None.

        Returns:
            ConfidenceLevel: Nivel de confianza correspondiente.
        """
        if score is None:
            return cls.INSUFFICIENT
        if score >= 0.9:
            return cls.VERIFIED
        if score >= 0.5:
            return cls.ESTIMATED
        if score > 0.0:
            return cls.CONFLICT
        return cls.INSUFFICIENT

    @property
    def min_score(self) -> float:
        """Retorna el score mínimo para este nivel de confianza.

        Returns:
            float: Score mínimo (0.0-1.0).
        """
        min_scores = {
            ConfidenceLevel.VERIFIED: 0.9,
            ConfidenceLevel.ESTIMATED: 0.5,
            ConfidenceLevel.CONFLICT: 0.0,
            ConfidenceLevel.INSUFFICIENT: 0.0,
        }
        return min_scores[self]

    @property
    def max_score(self) -> float:
        """Retorna el score máximo para este nivel de confianza.

        Returns:
            float: Score máximo (0.0-1.0).
        """
        max_scores = {
            ConfidenceLevel.VERIFIED: 1.0,
            ConfidenceLevel.ESTIMATED: 0.8999,
            ConfidenceLevel.CONFLICT: 0.4999,
            ConfidenceLevel.INSUFFICIENT: 0.0,
        }
        return max_scores[self]

    @property
    def description(self) -> str:
        """Retorna la descripción legible del nivel de confianza.

        Returns:
            str: Descripción del nivel.
        """
        descriptions = {
            ConfidenceLevel.VERIFIED: "≥0.9 - 2+ fuentes coinciden",
            ConfidenceLevel.ESTIMATED: "0.5-0.9 - 1 fuente o benchmark",
            ConfidenceLevel.CONFLICT: "<0.5 - Fuentes contradicen",
            ConfidenceLevel.INSUFFICIENT: "Sin evidencia disponible",
        }
        return descriptions[self]

    @property
    def requires_disclaimer(self) -> bool:
        """Indica si este nivel requiere disclaimer en assets.

        Returns:
            bool: True si requiere disclaimer.
        """
        return self in (ConfidenceLevel.ESTIMATED, ConfidenceLevel.CONFLICT)

    def __str__(self) -> str:
        """Representación string del enum.

        Returns:
            str: Valor del enum como string.
        """
        return self.value

    def to_dict(self) -> dict:
        """Serializa el enum a diccionario.

        Returns:
            dict: Representación del enum como diccionario.
        """
        return {
            "level": self.value,
            "description": self.description,
            "min_score": self.min_score,
            "max_score": self.max_score,
            "requires_disclaimer": self.requires_disclaimer,
        }
