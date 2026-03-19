"""
Coherence Configuration Module v4.2.0

Lee configuración de validación de coherencia desde .conductor/guidelines.yaml
"""
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
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
    Reglas de validación de precio vs dolor.

    Unidades: decimal (0.03 = 3%, 0.06 = 6%)
    Notación x para legibilidad: 3.0x = 0.03 decimal
    """
    min_ratio: float  # Decimal: 0.03 = 3%
    max_ratio: float  # Decimal: 0.06 = 6%
    ideal_ratio: float  # Decimal: 0.045 = 4.5%

    @classmethod
    def from_x_notation(cls, min_x: float, max_x: float, ideal_x: float) -> "PriceValidationRule":
        """
        Crea regla desde notación x (ej: 3.0x) a decimal (0.03).

        Args:
            min_x: Ratio mínimo en notación x (ej: 3.0 para 3%)
            max_x: Ratio máximo en notación x (ej: 6.0 para 6%)
            ideal_x: Ratio ideal en notación x (ej: 4.5 para 4.5%)

        Returns:
            PriceValidationRule con valores en decimal
        """
        return cls(
            min_ratio=min_x / 100,
            max_ratio=max_x / 100,
            ideal_ratio=ideal_x / 100
        )

    def to_x_notation(self, decimal_ratio: float) -> float:
        """Convierte ratio decimal a notación x para legibilidad."""
        return decimal_ratio * 100

    def format_ratio_x(self, decimal_ratio: float) -> str:
        """Formatea ratio decimal como string en notación x (ej: '3.0x')."""
        return f"{self.to_x_notation(decimal_ratio):.1f}x"


class CoherenceConfig:
    """
    Configuración centralizada de controles de coherencia.
    Lee desde .conductor/guidelines.yaml con fallback a valores por defecto.
    """

    DEFAULT_RULES = {
        'whatsapp_verified': CoherenceRule(
            name='whatsapp_verified',
            confidence_threshold=0.9,
            blocking=True,
            description='WhatsApp debe estar verificado cruzando 2+ fuentes'
        ),
        'financial_data_validated': CoherenceRule(
            name='financial_data_validated',
            confidence_threshold=0.7,
            blocking=False,
            description='Datos financieros deben tener confianza >= 0.7'
        ),
        'problems_have_solutions': CoherenceRule(
            name='problems_have_solutions',
            confidence_threshold=0.5,
            blocking=True,
            description='Al menos 50% de problemas deben tener solución'
        ),
        'assets_are_justified': CoherenceRule(
            name='assets_are_justified',
            confidence_threshold=0.8,
            blocking=False,
            description='Assets deben estar justificados por problemas'
        ),
        'overall_coherence': CoherenceRule(
            name='overall_coherence',
            confidence_threshold=0.8,
            blocking=False,
            description='Score de coherencia global debe ser >= 0.8'
        )
    }

    # Valores por defecto en DECIMAL (0.03 = 3%, no 3.0x)
    DEFAULT_PRICE_RULE = PriceValidationRule(
        min_ratio=0.03,
        max_ratio=0.06,
        ideal_ratio=0.045
    )

    def __init__(self, config_path: str = ".conductor/guidelines.yaml"):
        self.config_path = Path(config_path)
        self._rules: Dict[str, CoherenceRule] = {}
        self._price_rule: Optional[PriceValidationRule] = None
        self._load_config()

    def _load_config(self) -> None:
        """Carga configuración desde YAML o usa defaults."""
        if not self.config_path.exists():
            print(f"[WARN] Config no encontrado: {self.config_path}")
            print("[INFO] Usando valores por defecto")
            self._rules = self.DEFAULT_RULES.copy()
            self._price_rule = self.DEFAULT_PRICE_RULE
            return

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            # Cargar reglas de coherencia v4
            v4_rules = config.get('v4_coherence_rules', {})

            for rule_name, rule_data in v4_rules.items():
                self._rules[rule_name] = CoherenceRule(
                    name=rule_name,
                    confidence_threshold=rule_data.get('confidence_threshold', 0.5),
                    blocking=rule_data.get('blocking', False),
                    description=rule_data.get('description', '')
                )

            # Completar con defaults si faltan reglas
            for name, default_rule in self.DEFAULT_RULES.items():
                if name not in self._rules:
                    self._rules[name] = default_rule

            # Cargar reglas de precio
            price_config = config.get('price_validation', {})

            # Detectar si el YAML usa notación x (valores > 1.0) o decimal
            min_ratio = price_config.get('min_ratio', 0.03)

            # Si el valor es > 1.0, asumimos notación x y convertimos a decimal
            if min_ratio > 1.0:
                print("[INFO] Detectada notación x en guidelines.yaml, convirtiendo a decimal")
                self._price_rule = PriceValidationRule.from_x_notation(
                    min_x=price_config.get('min_ratio', 3.0),
                    max_x=price_config.get('max_ratio', 6.0),
                    ideal_x=price_config.get('ideal_ratio', 4.5)
                )
            else:
                # Ya está en decimal
                self._price_rule = PriceValidationRule(
                    min_ratio=min_ratio,
                    max_ratio=price_config.get('max_ratio', 0.06),
                    ideal_ratio=price_config.get('ideal_ratio', 0.045)
                )

            print(f"[INFO] Config cargada desde: {self.config_path}")

        except Exception as e:
            print(f"[WARN] Error cargando config: {e}")
            print("[INFO] Usando valores por defecto")
            self._rules = self.DEFAULT_RULES.copy()
            self._price_rule = self.DEFAULT_PRICE_RULE

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
        """Obtiene reglas de validación de precio."""
        return self._price_rule

    def validate_price_ratio(self, price_monthly: float, pain_monthly: float) -> tuple:
        """
        Valida que el precio esté en rango coherente con el dolor.

        Args:
            price_monthly: Precio mensual en COP
            pain_monthly: Dolor financiero mensual en COP

        Returns:
            (is_valid: bool, score: float, message: str)
            El mensaje usa notación x para legibilidad (ej: "3.0x")
        """
        if pain_monthly <= 0:
            return True, 1.0, "Sin dolor financiero medible"

        ratio = price_monthly / pain_monthly

        # Convertir a notación x para mensajes legibles
        ratio_x = self._price_rule.to_x_notation(ratio)
        min_x = self._price_rule.to_x_notation(self._price_rule.min_ratio)
        max_x = self._price_rule.to_x_notation(self._price_rule.max_ratio)

        if ratio < self._price_rule.min_ratio:
            return False, ratio / self._price_rule.min_ratio, \
                   f"Precio muy bajo ({ratio_x:.1f}x vs mínimo {min_x:.1f}x)"

        if ratio > self._price_rule.max_ratio:
            return False, self._price_rule.max_ratio / ratio, \
                   f"Precio muy alto ({ratio_x:.1f}x vs máximo {max_x:.1f}x)"

        # Calcular score basado en qué tan cerca del ideal
        ideal_distance = abs(ratio - self._price_rule.ideal_ratio)
        max_distance = max(
            self._price_rule.max_ratio - self._price_rule.ideal_ratio,
            self._price_rule.ideal_ratio - self._price_rule.min_ratio
        )
        score = 1.0 - (ideal_distance / max_distance)

        return True, score, f"Precio en rango óptimo ({ratio_x:.1f}x)"

    def list_rules(self) -> Dict[str, CoherenceRule]:
        """Lista todas las reglas configuradas."""
        return self._rules.copy()


# Singleton para uso global
_config_instance: Optional[CoherenceConfig] = None


def get_coherence_config() -> CoherenceConfig:
    """Obtiene instancia singleton de configuración."""
    global _config_instance
    if _config_instance is None:
        _config_instance = CoherenceConfig()
    return _config_instance
