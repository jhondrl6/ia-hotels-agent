"""
PrecisionValidator — Valida precision financiera y determina reglas de render.

Usa classify_source() y determine_precision_tier() de no_defaults_validator
para clasificar fuentes con granularidad epistémica y decidir si se puede
mostrar cifra exacta o solo rango.
"""

from modules.financial_engine.no_defaults_validator import (
    NoDefaultsValidator,
    ValidationBlock,
    NoDefaultsValidationResult,
    classify_source,
    determine_precision_tier,
)
from modules.financial_engine.financial_evidence import EpistemicStatus


class PrecisionValidator:
    """Valida precisión financiera y determina reglas de render."""

    @staticmethod
    def validate(
        adr_cop: float,
        adr_source: str,
        occupancy_rate: float,
        occupancy_source: str,
        direct_channel_pct: float,
        channel_source: str,
    ) -> NoDefaultsValidationResult:
        """Valida campos y determina tier + can_show_exact.

        Args:
            adr_cop: Valor del ADR en COP.
            adr_source: Fuente del ADR.
            occupancy_rate: Tasa de ocupacion (0.0-1.0).
            occupancy_source: Fuente de occupancy.
            direct_channel_pct: Porcentaje de canal directo (0.0-1.0).
            channel_source: Fuente del canal directo.

        Returns:
            NoDefaultsValidationResult con precision_tier, field_epistemic y
            can_show_exact_money calculados.
        """
        validator = NoDefaultsValidator()

        data = {
            "adr_cop": adr_cop,
            "occupancy_rate": occupancy_rate,
            "direct_channel_percentage": direct_channel_pct,
        }
        sources = {
            "adr_cop": adr_source,
            "occupancy_rate": occupancy_source,
            "direct_channel_percentage": channel_source,
        }

        return validator.validate(data, sources)
