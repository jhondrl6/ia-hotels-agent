"""
Coherence Configuration Module v4.2.0

Valores canonicos de coherencia y validacion de precio.
Anteriormente se leian desde .conductor/guidelines.yaml (eliminado).
Ahora los defaults son la unica fuente de verdad.
Si necesitas cambiar umbrales en caliente, vuelve a externalizarlos a un YAML.
"""
from __future__ import annotations
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass


@dataclass
class CoherenceRule:
    """Regla de coherencia individual."""
    name: str
    confidence_threshold: float
    blocking: bool
    description: str


@dataclass
class PriceValidationRule:
    """
    Reglas de validacion de precio vs dolor.

    Unidades: decimal (0.03 = 3%, 0.06 = 6%)
    Notacion x para legibilidad: 3.0x = 0.03 decimal
    """
    min_ratio: float  # Decimal: 0.03 = 3%
    max_ratio: float  # Decimal: 0.06 = 6%
    ideal_ratio: float  # Decimal: 0.045 = 4.5%

    @classmethod
    def from_x_notation(cls, min_x: float, max_x: float, ideal_x: float) -> "PriceValidationRule":
        """Crea regla desde notacion x (ej: 3.0x) a decimal (0.03)."""
        return cls(
            min_ratio=min_x / 100,
            max_ratio=max_x / 100,
            ideal_ratio=ideal_x / 100
        )

    def to_x_notation(self, decimal_ratio: float) -> float:
        """Convierte ratio decimal a notacion x para legibilidad."""
        return decimal_ratio * 100

    def format_ratio_x(self, decimal_ratio: float) -> str:
        """Formatea ratio decimal como string en notacion x (ej: '3.0x')."""
        return f"{self.to_x_notation(decimal_ratio):.1f}x"


class CoherenceConfig:
    """
    Configuracion centralizada de controles de coherencia.
    Fuente de verdad: umbrales hardcodeados como defaults canonicos.
    """

    DEFAULT_RULES = {
        "whatsapp_verified": CoherenceRule(
            name="whatsapp_verified",
            confidence_threshold=0.9,
            blocking=True,
            description="WhatsApp debe estar verificado cruzando 2+ fuentes"
        ),
        "financial_data_validated": CoherenceRule(
            name="financial_data_validated",
            confidence_threshold=0.7,
            blocking=False,
            description="Datos financieros deben tener confianza >= 0.7"
        ),
        "problems_have_solutions": CoherenceRule(
            name="problems_have_solutions",
            confidence_threshold=0.5,
            blocking=True,
            description="Al menos 50% de problemas deben tener solucion"
        ),
        "assets_are_justified": CoherenceRule(
            name="assets_are_justified",
            confidence_threshold=0.8,
            blocking=False,
            description="Assets deben estar justificados por problemas"
        ),
        "overall_coherence": CoherenceRule(
            name="overall_coherence",
            confidence_threshold=0.8,
            blocking=False,
            description="Score de coherencia global debe ser >= 0.8"
        )
    }

    # Valores por defecto en DECIMAL (0.03 = 3%, no 3.0x)
    DEFAULT_PRICE_RULE = PriceValidationRule(
        min_ratio=0.03,
        max_ratio=0.06,
        ideal_ratio=0.045
    )

    def __init__(self):
        self._rules: Dict[str, CoherenceRule] = dict(self.DEFAULT_RULES)
        self._price_rule: PriceValidationRule = self.DEFAULT_PRICE_RULE

    def get_rule(self, rule_name: str) -> CoherenceRule:
        """Obtiene una regla por nombre."""
        return self._rules.get(rule_name, self.DEFAULT_RULES.get(rule_name))

    def get_threshold(self, rule_name: str) -> float:
        """Obtiene el umbral de confianza para una regla."""
        return self.get_rule(rule_name).confidence_threshold

    def is_blocking(self, rule_name: str) -> bool:
        """Determina si una regla es bloqueante."""
        return self.get_rule(rule_name).blocking

    def get_price_rule(self) -> PriceValidationRule:
        """Obtiene reglas de validacion de precio."""
        return self._price_rule

    def validate_price_ratio(self, price_monthly: float, pain_monthly: float) -> tuple:
        """
        Valida que el precio este en rango coherente con el dolor.

        Args:
            price_monthly: Precio mensual en COP
            pain_monthly: Dolor financiero mensual en COP

        Returns:
            (is_valid: bool, score: float, message: str)
            El mensaje usa notacion x para legibilidad (ej: "3.0x")
        """
        if pain_monthly <= 0:
            return True, 1.0, "Sin dolor financiero medible"

        ratio = price_monthly / pain_monthly

        ratio_x = self._price_rule.to_x_notation(ratio)
        min_x = self._price_rule.to_x_notation(self._price_rule.min_ratio)
        max_x = self._price_rule.to_x_notation(self._price_rule.max_ratio)

        if ratio < self._price_rule.min_ratio:
            return False, ratio / self._price_rule.min_ratio,                    f"Precio muy bajo ({ratio_x:.1f}x vs minimo {min_x:.1f}x)"

        if ratio > self._price_rule.max_ratio:
            return False, self._price_rule.max_ratio / ratio,                    f"Precio muy alto ({ratio_x:.1f}x vs maximo {max_x:.1f}x)"

        ideal_distance = abs(ratio - self._price_rule.ideal_ratio)
        max_distance = max(
            self._price_rule.max_ratio - self._price_rule.ideal_ratio,
            self._price_rule.ideal_ratio - self._price_rule.min_ratio
        )
        score = 1.0 - (ideal_distance / max_distance)

        return True, score, f"Precio en rango optimo ({ratio_x:.1f}x)"

    def list_rules(self) -> Dict[str, CoherenceRule]:
        """Lista todas las reglas configuradas."""
        return dict(self._rules)


# Singleton para uso global
_config_instance: Optional[CoherenceConfig] = None


def get_coherence_config() -> CoherenceConfig:
    """Obtiene instancia singleton de configuracion."""
    global _config_instance
    if _config_instance is None:
        _config_instance = CoherenceConfig()
    return _config_instance
