"""
Financial Coherence Validator — Arbitraje Ético Gate (ROICR FASE-4A).

Impide que se generen propuestas donde el fee mensual supera el 60% del
recovery mensual esperado. Este gate protege al cliente de contratos
comercialmente inviables.

El threshold es 0.60 (60%), DIFERENTE del Value-Capture Cap en pricing (0.50).
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class ValidationReport:
    """
    Reporte de validación para arbitraje ético.
    
    Attributes:
        is_valid: True si pasa el gate, False si es bloqueado
        errors: Lista de errores/mensajes de bloqueo
        fee_ratio: ratio real fee/recovery (None si no aplica)
        threshold: threshold usado para la validación
    """
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    fee_ratio: Optional[float] = None
    threshold: float = 0.60
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "fee_ratio": self.fee_ratio,
            "threshold": self.threshold,
        }


def validar_arbitraje_etico(proposal_data: Dict[str, Any]) -> ValidationReport:
    """
    Valida que el fee mensual no supere el 60% del recovery mensual esperado.
    
    Este gate implementa el "Arbitraje Ético" — impide propuestas donde el
    cliente pagaría más de lo que recuperaría mensualmente.
    
    Args:
        proposal_data: Diccionario con datos de la propuesta.
            Debe contener:
                - monthly_fee: float (COP mensuales)
                - expected_monthly_recovery: float (COP mensuales recuperados)
            
            También acepta keys alternativas:
                - fee / recovery
                - monthly_fee_cop / expected_monthly_recovery_cop
    
    Returns:
        ValidationReport con:
            - is_valid: True si fee <= 60% del recovery
            - errors: Lista con mensaje de bloqueo si is_valid=False
            - fee_ratio: ratio real fee/recovery
            - threshold: 0.60
    
    Ejemplo:
        >>> data = {
        ...     "monthly_fee": 1500000,
        ...     "expected_monthly_recovery": 3000000
        ... }
        >>> result = validar_arbitraje_etico(data)
        >>> result.is_valid
        False
        >>> result.fee_ratio
        0.5
    """
    # Extraer fee y recovery de proposal_data
    monthly_fee = (
        proposal_data.get("monthly_fee") 
        or proposal_data.get("fee")
        or proposal_data.get("monthly_fee_cop")
        or 0
    )
    
    expected_recovery = (
        proposal_data.get("expected_monthly_recovery")
        or proposal_data.get("recovery")
        or proposal_data.get("expected_monthly_recovery_cop")
        or 0
    )
    
    # Si no hay datos, no podemos validar — retornamos inválido con error
    if monthly_fee <= 0 or expected_recovery <= 0:
        return ValidationReport(
            is_valid=False,
            errors=["No se puede validar arbitraje: monthly_fee o expected_monthly_recovery son 0 o ausentes"],
            fee_ratio=None,
            threshold=0.60,
        )
    
    fee_ratio = monthly_fee / expected_recovery
    threshold = 0.60
    
    # Gate: fee NO puede superar 60% del recovery
    if fee_ratio > threshold:
        errors = [
            f"ETHICS GATE: fee ({monthly_fee:,.0f} COP) supera el {threshold:.0%} "
            f"del recovery esperado ({expected_recovery:,.0f} COP)",
            f"Ratio actual: {fee_ratio:.1%} (threshold: {threshold:.0%})",
            "Propuesta bloqueada por arbitraje ético — el fee sería mayor que "
            "lo que el cliente recupera mensualmente.",
        ]
        return ValidationReport(
            is_valid=False,
            errors=errors,
            fee_ratio=fee_ratio,
            threshold=threshold,
        )
    
    # Pasó el gate
    return ValidationReport(
        is_valid=True,
        errors=[],
        fee_ratio=fee_ratio,
        threshold=threshold,
    )


# Alias para compatibilidad con código que use el nombre en español
ValidationResult = ValidationReport