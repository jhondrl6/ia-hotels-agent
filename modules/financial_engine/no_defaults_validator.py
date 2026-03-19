"""No Defaults in Money - Financial Data Validation.

Bloquea cálculos financieros cuando se detectan valores por defecto
en campos críticos del hotel.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
from enum import Enum


class DefaultValueType(Enum):
    """Tipos de valores por defecto detectados."""
    ZERO = "zero"
    NONE = "none"
    MISSING = "missing"


class BlockReason(Enum):
    """Razones de bloqueo para cálculos financieros."""
    OCCUPANCY_RATE_ZERO = "occupancy_rate_is_zero"
    DIRECT_CHANNEL_ZERO = "direct_channel_is_zero"
    ADR_COP_ZERO = "adr_cop_is_zero"
    OCCUPANCY_RATE_NONE = "occupancy_rate_is_none"
    DIRECT_CHANNEL_NONE = "direct_channel_is_none"
    ADR_COP_NONE = "adr_cop_is_none"
    OCCUPANCY_RATE_MISSING = "occupancy_rate_is_missing"
    DIRECT_CHANNEL_MISSING = "direct_channel_is_missing"
    ADR_COP_MISSING = "adr_cop_is_missing"


@dataclass
class ValidationBlock:
    """Registro de un bloqueo de validación."""
    field: str
    value: Any
    default_type: DefaultValueType
    reason: BlockReason
    message: str
    correction_hint: str


@dataclass
class NoDefaultsValidationResult:
    """Resultado de validación No Defaults."""
    can_calculate: bool
    blocks: List[ValidationBlock] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    @property
    def has_blocks(self) -> bool:
        return len(self.blocks) > 0
    
    def to_user_message(self) -> str:
        """Genera mensaje descriptivo para el usuario."""
        if self.can_calculate:
            return "Datos financieros validados correctamente."
        
        messages = ["⚠️ CÁLCULO FINANCIERO BLOQUEADO", ""]
        messages.append("Se detectaron valores por defecto en campos críticos:")
        messages.append("")
        
        for block in self.blocks:
            messages.append(f"  • {block.field}: {block.message}")
            messages.append(f"    → {block.correction_hint}")
        
        messages.append("")
        messages.append("Por favor, complete los datos en el onboarding para continuar.")
        
        return "\n".join(messages)


class NoDefaultsValidator:
    """Validador que bloquea cálculos con valores por defecto.
    
    Implementa la regla: "No Defaults in Money" - Nunca calcular
    proyecciones financieras usando valores por defecto (0 o None).
    """
    
    # Campos críticos que no pueden tener valores por defecto
    CRITICAL_FIELDS = ["occupancy_rate", "direct_channel_percentage", "adr_cop"]
    
    # Mensajes de error por campo
    ERROR_MESSAGES = {
        "occupancy_rate": "No se puede calcular sin ocupación real. El valor por defecto es 0%.",
        "direct_channel_percentage": "No se puede proyectar sin canal directo. El valor por defecto es 0%.",
        "adr_cop": "No se puede estimar ingresos sin tarifa promedio. El valor por defecto es $0.",
    }
    
    # Hints de corrección por campo
    CORRECTION_HINTS = {
        "occupancy_rate": "Complete el onboarding con el porcentaje real de ocupación del hotel",
        "direct_channel_percentage": "Indique el porcentaje actual de reservas directas (sin OTA)",
        "adr_cop": "Ingrese el ADR (Average Daily Rate) promedio en pesos colombianos",
    }
    
    # Mapeo de campos a razones de bloqueo
    BLOCK_REASONS = {
        "occupancy_rate": {
            DefaultValueType.ZERO: BlockReason.OCCUPANCY_RATE_ZERO,
            DefaultValueType.NONE: BlockReason.OCCUPANCY_RATE_NONE,
            DefaultValueType.MISSING: BlockReason.OCCUPANCY_RATE_MISSING,
        },
        "direct_channel_percentage": {
            DefaultValueType.ZERO: BlockReason.DIRECT_CHANNEL_ZERO,
            DefaultValueType.NONE: BlockReason.DIRECT_CHANNEL_NONE,
            DefaultValueType.MISSING: BlockReason.DIRECT_CHANNEL_MISSING,
        },
        "adr_cop": {
            DefaultValueType.ZERO: BlockReason.ADR_COP_ZERO,
            DefaultValueType.NONE: BlockReason.ADR_COP_NONE,
            DefaultValueType.MISSING: BlockReason.ADR_COP_MISSING,
        },
    }
    
    def __init__(self):
        self.blocks: List[ValidationBlock] = []
    
    def validate(self, data: Dict[str, Any]) -> NoDefaultsValidationResult:
        """Valida que no haya valores por defecto en campos críticos.
        
        Args:
            data: Diccionario con datos financieros del hotel
            
        Returns:
            NoDefaultsValidationResult con resultado de validación
        """
        self.blocks = []
        warnings = []
        
        for field_name in self.CRITICAL_FIELDS:
            if isinstance(data, dict):
                value = data.get(field_name)
            else:
                value = getattr(data, field_name, None)
            block = self._check_field(field_name, value)
            
            if block:
                self.blocks.append(block)
        
        can_calculate = len(self.blocks) == 0
        
        return NoDefaultsValidationResult(
            can_calculate=can_calculate,
            blocks=self.blocks,
            warnings=warnings
        )
    
    def _check_field(self, field_name: str, value: Any) -> Optional[ValidationBlock]:
        """Verifica si un campo tiene valor por defecto.
        
        Args:
            field_name: Nombre del campo
            value: Valor a verificar
            
        Returns:
            ValidationBlock si es valor por defecto, None si es válido
        """
        default_type = self._get_default_type(value)
        
        if default_type is None:
            return None
        
        return ValidationBlock(
            field=field_name,
            value=value,
            default_type=default_type,
            reason=self.BLOCK_REASONS[field_name][default_type],
            message=self.ERROR_MESSAGES[field_name],
            correction_hint=self.CORRECTION_HINTS[field_name]
        )
    
    def _get_default_type(self, value: Any) -> Optional[DefaultValueType]:
        """Determina el tipo de valor por defecto.
        
        Args:
            value: Valor a evaluar
            
        Returns:
            DefaultValueType si es valor por defecto, None si es válido
        """
        if value is None:
            return DefaultValueType.NONE
        
        if isinstance(value, (int, float)) and value == 0:
            return DefaultValueType.ZERO
        
        if isinstance(value, str) and value.strip() == "":
            return DefaultValueType.MISSING
        
        return None
    
    @staticmethod
    def is_default_value(value: Any) -> bool:
        """Determina si un valor es considerado 'por defecto'.
        
        Args:
            value: Valor a evaluar
            
        Returns:
            True si es valor por defecto (0, None, vacío)
        """
        if value is None:
            return True
        
        if isinstance(value, (int, float)) and value == 0:
            return True
        
        if isinstance(value, str) and value.strip() == "":
            return True
        
        return False
