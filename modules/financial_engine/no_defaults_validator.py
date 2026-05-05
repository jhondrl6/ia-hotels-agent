"""No Defaults in Money - Financial Data Validation.

Bloquea cálculos financieros cuando se detectan valores por defecto
en campos críticos del hotel.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union, Set
from enum import Enum

from modules.financial_engine.financial_evidence import EpistemicStatus


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
class ValidationWarning:
    """Registro de un warning por fuente sospechosa."""
    field: str
    source: str
    message: str


# Fuentes que no son verificacion real de datos
# LEGACY — usar SOURCE_EPISTEMIC_MAP
SUSPECT_SOURCES: Set[str] = {
    "legacy_hardcode", "default", "unknown", "hardcoded", "estimated",
}


# Reemplaza clasificacion binaria de SUSPECT_SOURCES con mapeo granular
SOURCE_EPISTEMIC_MAP: Dict[str, EpistemicStatus] = {
    "user_provided": EpistemicStatus.MEASURED,
    "web_scraping": EpistemicStatus.OBSERVED,
    "regional_v410": EpistemicStatus.REGIONAL_BENCHMARK,
    "legacy_hardcode": EpistemicStatus.DEFAULTED,
    "default": EpistemicStatus.DEFAULTED,
    "unknown": EpistemicStatus.DEFAULTED,
    "hardcoded": EpistemicStatus.DEFAULTED,
    "estimated": EpistemicStatus.DEFAULTED,
    "simulated": EpistemicStatus.SIMULATED,
}


def classify_source(source: str) -> EpistemicStatus:
    """Clasifica un source string en su estado epistemico."""
    return SOURCE_EPISTEMIC_MAP.get(source.lower(), EpistemicStatus.DEFAULTED)


def determine_precision_tier(
    adr_status: EpistemicStatus,
    occupancy_status: EpistemicStatus,
    channel_status: EpistemicStatus,
) -> str:
    """Determina el tier de precision por peor fuente."""
    statuses = {adr_status, occupancy_status, channel_status}
    if EpistemicStatus.DEFAULTED in statuses or EpistemicStatus.SIMULATED in statuses:
        return "C"
    if EpistemicStatus.REGIONAL_BENCHMARK in statuses:
        return "B"
    if EpistemicStatus.CONFLICT in statuses:
        return "C"
    return "A"


@dataclass
class NoDefaultsValidationResult:
    """Resultado de validacion No Defaults."""
    can_calculate: bool
    blocks: List[ValidationBlock] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    source_warnings: List[ValidationWarning] = field(default_factory=list)
    precision_tier: str = "C"  # Default conservador
    field_epistemic: Dict[str, EpistemicStatus] = field(default_factory=dict)
    can_show_exact_money: bool = False
    
    @property
    def has_blocks(self) -> bool:
        return len(self.blocks) > 0

    @property
    def has_suspect_sources(self) -> bool:
        """True si alguna fuente es sospechosa (no verificacion real)."""
        return len(self.source_warnings) > 0

    @property
    def suspect_fields(self) -> List[str]:
        """Lista de campos con fuentes sospechosas."""
        return [w.field for w in self.source_warnings]

    @property
    def source_reliability(self) -> str:
        """Retorna 'verified' si no hay fuentes sospechosas, 'unverified' si las hay."""
        return "unverified" if self.has_suspect_sources else "verified"

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
    
    def validate(
        self,
        data: Dict[str, Any],
        sources: Optional[Dict[str, str]] = None,
    ) -> NoDefaultsValidationResult:
        """Valida que no haya valores por defecto en campos críticos.

        Args:
            data: Diccionario con datos financieros del hotel
            sources: Diccionario opcional campo -> fuente (ej {"adr_cop": "legacy_hardcode"})
                     Si se pasa, se detectan fuentes sospechosas y se generan warnings.

        Returns:
            NoDefaultsValidationResult con resultado de validación
        """
        self.blocks = []
        general_warnings: List[str] = []
        source_warnings: List[ValidationWarning] = []

        for field_name in self.CRITICAL_FIELDS:
            if isinstance(data, dict):
                value = data.get(field_name)
            else:
                value = getattr(data, field_name, None)
            block = self._check_field(field_name, value)

            if block:
                self.blocks.append(block)

            # FASE-J: detectar fuentes sospechosas (no bloquea, solo advierte)
            if sources and field_name in sources:
                src = sources[field_name]
                if src in SUSPECT_SOURCES:
                    msg = (
                        f"Campo '{field_name}' usa fuente '{src}' "
                        f"(no verificacion real). Los datos podrian ser estimados."
                    )
                    source_warnings.append(ValidationWarning(
                        field=field_name,
                        source=src,
                        message=msg,
                    ))
                    general_warnings.append(msg)

        can_calculate = len(self.blocks) == 0

        # Clasificar fuentes epistemicamente si se proveyeron sources
        field_epistemic: Dict[str, EpistemicStatus] = {}
        if sources:
            field_epistemic = {
                field_name: classify_source(sources[field_name])
                for field_name in self.CRITICAL_FIELDS
                if field_name in sources
            }

        # Determinar precision_tier y can_show_exact_money
        adr_status = field_epistemic.get("adr_cop", EpistemicStatus.DEFAULTED)
        occ_status = field_epistemic.get("occupancy_rate", EpistemicStatus.DEFAULTED)
        ch_status = field_epistemic.get("direct_channel_percentage", EpistemicStatus.DEFAULTED)
        precision_tier = determine_precision_tier(adr_status, occ_status, ch_status)
        can_show_exact = all(
            s in {EpistemicStatus.MEASURED, EpistemicStatus.OBSERVED}
            for s in [adr_status, occ_status, ch_status]
        )

        return NoDefaultsValidationResult(
            can_calculate=can_calculate,
            blocks=self.blocks,
            warnings=general_warnings,
            source_warnings=source_warnings,
            precision_tier=precision_tier,
            field_epistemic=field_epistemic,
            can_show_exact_money=can_show_exact,
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
