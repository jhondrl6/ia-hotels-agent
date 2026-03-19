"""Enum de severidad para clasificación de claims.

Define los niveles de severidad que determinan la prioridad y el tiempo
de resolución para cada claim identificado durante el análisis.
"""

from enum import Enum


class Severity(Enum):
    """Niveles de severidad para claims de validación.

    Cada nivel tiene un SLA asociado que determina el tiempo máximo
    para resolver o mitigar el claim.

    Attributes:
        CRITICAL: Bloquea publicación. Requiere atención inmediata.
        HIGH: Debe resolverse en 7 días.
        MEDIUM: Debe resolverse en 30 días.
        LOW: Quick win, mejora incremental.
    """

    CRITICAL = "critical"
    """Bloquea publicación. Requiere atención inmediata."""

    HIGH = "high"
    """Debe resolverse en 7 días."""

    MEDIUM = "medium"
    """Debe resolverse en 30 días."""

    LOW = "low"
    """Quick win, mejora incremental."""

    @property
    def sla_days(self) -> int:
        """Retorna el SLA en días para este nivel de severidad.

        Returns:
            int: Número de días para resolver el claim.
        """
        sla_map = {
            Severity.CRITICAL: 0,  # Inmediato
            Severity.HIGH: 7,
            Severity.MEDIUM: 30,
            Severity.LOW: 90,
        }
        return sla_map[self]

    @property
    def description(self) -> str:
        """Retorna la descripción legible del nivel de severidad.

        Returns:
            str: Descripción del nivel de severidad.
        """
        descriptions = {
            Severity.CRITICAL: "Bloquea publicación",
            Severity.HIGH: "7 días",
            Severity.MEDIUM: "30 días",
            Severity.LOW: "Quick win",
        }
        return descriptions[self]

    @property
    def blocks_deployment(self) -> bool:
        """Indica si este nivel de severidad bloquea publicación.

        Returns:
            bool: True si bloquea publicación.
        """
        return self == Severity.CRITICAL

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
            "sla_days": self.sla_days,
            "blocks_deployment": self.blocks_deployment,
        }
