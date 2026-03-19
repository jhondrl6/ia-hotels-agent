"""Financial Calculator v2 - Calculos con validacion estricta.

Calculador financiero que integra validacion de datos antes
de generar proyecciones. Implementa "No Defaults in Money".
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
from datetime import datetime, timezone

# Importar scenario_calculator existente
from modules.financial_engine.scenario_calculator import (
    ScenarioCalculator,
    HotelFinancialData,
    ScenarioType,
    FinancialScenario,
)
from modules.financial_engine.no_defaults_validator import (
    NoDefaultsValidator,
    NoDefaultsValidationResult,
)


class CalculationStatus(Enum):
    """Estados posibles del calculo."""

    SUCCESS = "success"
    BLOCKED_BY_DEFAULTS = "blocked_by_defaults"
    BLOCKED_BY_VALIDATION = "blocked_by_validation"
    INSUFFICIENT_DATA = "insufficient_data"
    ERROR = "error"


@dataclass
class FinancialCalculationResult:
    """Resultado de calculo financiero."""

    status: CalculationStatus
    scenarios: Optional[Dict[ScenarioType, FinancialScenario]] = None
    hook_range: Optional[str] = None
    validation_result: Optional[NoDefaultsValidationResult] = None
    error_message: Optional[str] = None
    calculation_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def success(self) -> bool:
        """True si el calculo fue exitoso."""
        return self.status == CalculationStatus.SUCCESS

    @property
    def blocked(self) -> bool:
        """True si el calculo fue bloqueado."""
        return self.status in (
            CalculationStatus.BLOCKED_BY_DEFAULTS,
            CalculationStatus.BLOCKED_BY_VALIDATION,
            CalculationStatus.INSUFFICIENT_DATA,
        )

    def get_conservative_loss(self) -> Optional[float]:
        """Obtiene perdida del escenario conservador."""
        if self.scenarios and ScenarioType.CONSERVATIVE in self.scenarios:
            return self.scenarios[ScenarioType.CONSERVATIVE].monthly_loss_cop
        return None

    def get_realistic_loss(self) -> Optional[float]:
        """Obtiene perdida del escenario realista."""
        if self.scenarios and ScenarioType.REALISTIC in self.scenarios:
            return self.scenarios[ScenarioType.REALISTIC].monthly_loss_cop
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Serializa resultado a diccionario."""
        result = {
            "status": self.status.value,
            "success": self.success,
            "blocked": self.blocked,
            "timestamp": self.calculation_timestamp.isoformat(),
            "hook_range": self.hook_range,
        }

        if self.scenarios:
            result["scenarios"] = {
                k.value: {
                    "monthly_loss_cop": v.monthly_loss_cop,
                    "probability": v.probability,
                    "confidence_score": v.confidence_score,
                    "calculation_basis": v.calculation_basis,
                }
                for k, v in self.scenarios.items()
            }

        if self.validation_result:
            result["validation"] = {
                "can_calculate": self.validation_result.can_calculate,
                "block_count": len(self.validation_result.blocks),
                "blocks": [
                    {
                        "field": b.field,
                        "reason": b.reason.value,
                        "message": b.message,
                    }
                    for b in self.validation_result.blocks
                ],
            }

        if self.error_message:
            result["error"] = self.error_message

        return result


class FinancialCalculatorV2:
    """Calculador financiero v2 con validacion estricta.

    Este calculador:
    1. Valida que no haya valores por defecto (No Defaults in Money)
    2. Solo calcula escenarios si la validacion pasa
    3. Genera mensajes explicativos cuando bloquea
    4. Mantiene trazabilidad de todas las decisiones
    """

    def __init__(self):
        self.validator = NoDefaultsValidator()
        self.scenario_calculator = ScenarioCalculator()

    def calculate(self, financial_data: Dict[str, Any]) -> FinancialCalculationResult:
        """Calcula escenarios financieros con validacion previa.

        Args:
            financial_data: Datos financieros del hotel
                - rooms: int
                - adr_cop: float
                - occupancy_rate: float
                - direct_channel_percentage: float (optional)
                - ota_commission_rate: float (optional)

        Returns:
            FinancialCalculationResult con escenarios o bloqueo
        """
        # Paso 1: Validar No Defaults
        validation_result = self.validator.validate(financial_data)

        # Paso 2: Si falla, retornar bloqueo con mensaje
        if not validation_result.can_calculate:
            return FinancialCalculationResult(
                status=CalculationStatus.BLOCKED_BY_DEFAULTS,
                validation_result=validation_result,
                error_message=validation_result.to_user_message(),
                metadata={"reason": "validation_failed", "blocks": len(validation_result.blocks)},
            )

        try:
            # Paso 3: Si pasa, convertir a HotelFinancialData
            hotel_data = self._to_hotel_financial_data(financial_data)

            # Paso 4: Calcular escenarios con ScenarioCalculator
            scenarios = self.scenario_calculator.calculate_scenarios(hotel_data)

            # Generar hook range
            hook_range = self.scenario_calculator.get_hook_range(scenarios)

            # Paso 5: Retornar resultado exitoso
            return FinancialCalculationResult(
                status=CalculationStatus.SUCCESS,
                scenarios=scenarios,
                hook_range=hook_range,
                validation_result=validation_result,
                metadata={
                    "rooms": hotel_data.rooms,
                    "adr_cop": hotel_data.adr_cop,
                    "occupancy_rate": hotel_data.occupancy_rate,
                    "direct_channel_percentage": hotel_data.direct_channel_percentage,
                },
            )

        except Exception as e:
            return FinancialCalculationResult(
                status=CalculationStatus.ERROR,
                validation_result=validation_result,
                error_message=f"Error en calculo financiero: {str(e)}",
                metadata={"exception": str(e)},
            )

    def calculate_conditional(
        self,
        financial_data: Dict[str, Any],
        coherence_score: float = 0.0,
        min_coherence: float = 0.8,
    ) -> FinancialCalculationResult:
        """Calcula escenarios solo si coherencia es suficiente.

        Args:
            financial_data: Datos financieros del hotel
            coherence_score: Score de coherencia actual
            min_coherence: Minimo de coherencia requerido

        Returns:
            FinancialCalculationResult con escenarios o bloqueo
        """
        # Bloquear si coherence_score < min_coherence
        if coherence_score < min_coherence:
            return FinancialCalculationResult(
                status=CalculationStatus.BLOCKED_BY_VALIDATION,
                error_message=(
                    f"Coherencia insuficiente ({coherence_score:.2f} < {min_coherence:.2f}). "
                    "Se requiere mayor consistencia entre los datos del hotel para generar "
                    "proyecciones financieras confiables."
                ),
                metadata={
                    "coherence_score": coherence_score,
                    "min_coherence": min_coherence,
                    "gap": min_coherence - coherence_score,
                },
            )

        # Si pasa la validacion de coherencia, proceder con calculo normal
        result = self.calculate(financial_data)

        # Agregar metadata de coherencia
        result.metadata["coherence_score"] = coherence_score
        result.metadata["min_coherence"] = min_coherence

        return result

    def get_calculation_explanation(self, result: FinancialCalculationResult) -> str:
        """Genera explicacion legible del calculo.

        Args:
            result: Resultado de calculo

        Returns:
            Texto explicativo para incluir en documentos
        """
        if result.blocked:
            return self._get_blocked_explanation(result)

        if not result.scenarios:
            return "No hay escenarios calculados para explicar."

        lines = [
            "=" * 60,
            "EXPLICACION DEL CALCULO FINANCIERO",
            "=" * 60,
            "",
            f"Fecha de calculo: {result.calculation_timestamp.strftime('%Y-%m-%d %H:%M UTC')}",
            "",
            "RANGO ESTIMADO (HOOK):",
            f"  {result.hook_range}",
            "",
            "ESCENARIOS CALCULADOS:",
            "",
        ]

        scenario_names = {
            ScenarioType.CONSERVATIVE: "CONSERVADOR (70% probabilidad)",
            ScenarioType.REALISTIC: "REALISTA (20% probabilidad)",
            ScenarioType.OPTIMISTIC: "OPTIMISTA (10% probabilidad)",
        }

        for scenario_type, scenario in result.scenarios.items():
            loss_formatted = f"{scenario.monthly_loss_cop:,.0f}".replace(",", ".")
            confidence_pct = int(scenario.confidence_score * 100)

            lines.extend(
                [
                    f"  {scenario_names.get(scenario_type, 'Desconocido')}:",
                    f"    Perdida mensual: ${loss_formatted} COP",
                    f"    Confianza: {confidence_pct}%",
                    f"    Base: {scenario.calculation_basis}",
                    "",
                ]
            )

        lines.extend(
            [
                "METODOLOGIA:",
                "  Los calculos se basan en:",
                "  • Datos validados del hotel (sin valores por defecto)",
                "  • Escenarios con diferentes niveles de optimismo",
                "  • Probabilidades asignadas segun realismo de cada escenario",
                "  • Perdida mensual = Comisiones OTA - Ahorros potenciales",
                "",
                "=" * 60,
            ]
        )

        return "\n".join(lines)

    def _get_blocked_explanation(self, result: FinancialCalculationResult) -> str:
        """Genera explicacion cuando el calculo fue bloqueado."""
        lines = [
            "=" * 60,
            "CALCULO FINANCIERO BLOQUEADO",
            "=" * 60,
            "",
        ]

        if result.status == CalculationStatus.BLOCKED_BY_DEFAULTS:
            lines.extend(
                [
                    "Razon: Se detectaron valores por defecto en campos criticos.",
                    "",
                    "Campos bloqueados:",
                ]
            )
            if result.validation_result:
                for block in result.validation_result.blocks:
                    lines.extend(
                        [
                            f"  • {block.field}",
                            f"    {block.message}",
                            f"    Solucion: {block.correction_hint}",
                            "",
                        ]
                    )

        elif result.status == CalculationStatus.BLOCKED_BY_VALIDATION:
            lines.extend(
                [
                    "Razon: No cumple con los criterios de validacion.",
                    "",
                    f"{result.error_message}",
                ]
            )

        elif result.status == CalculationStatus.INSUFFICIENT_DATA:
            lines.extend(
                [
                    "Razon: Datos insuficientes para el calculo.",
                    "",
                    f"{result.error_message}",
                ]
            )

        lines.extend(
            [
                "",
                "POLITICA 'NO DEFAULTS IN MONEY':",
                "  No se generan proyecciones financieras con datos incompletos",
                "  o valores por defecto para proteger la integridad de los calculos.",
                "",
                "=" * 60,
            ]
        )

        return "\n".join(lines)

    def _to_hotel_financial_data(self, data: Dict[str, Any]) -> HotelFinancialData:
        """Convierte dict a HotelFinancialData."""
        # Extraer valores con defaults seguros
        rooms = int(data.get("rooms", 0))
        adr_cop = float(data.get("adr_cop", 0))
        occupancy_rate = float(data.get("occupancy_rate", 0))
        direct_channel_percentage = float(data.get("direct_channel_percentage", 0))
        ota_commission_rate = float(data.get("ota_commission_rate", 0.15))

        # Validar que los valores criticos no sean cero (ya deberian estar validados)
        if rooms <= 0:
            raise ValueError(f"Numero de habitaciones invalido: {rooms}")
        if adr_cop <= 0:
            raise ValueError(f"ADR invalido: {adr_cop}")
        if occupancy_rate <= 0:
            raise ValueError(f"Tasa de ocupacion invalida: {occupancy_rate}")

        return HotelFinancialData(
            rooms=rooms,
            adr_cop=adr_cop,
            occupancy_rate=occupancy_rate,
            direct_channel_percentage=direct_channel_percentage,
            ota_commission_rate=ota_commission_rate,
        )


def calculate_financial_scenarios(
    rooms: int,
    adr_cop: float,
    occupancy_rate: float,
    direct_channel_percentage: float = 0.0,
    ota_commission_rate: float = 0.15,
    coherence_score: float = 0.0,
    min_coherence: float = 0.8,
) -> FinancialCalculationResult:
    """Funcion helper para calcular escenarios facilmente.

    Args:
        rooms: Numero de habitaciones
        adr_cop: Tarifa promedio en COP
        occupancy_rate: Tasa de ocupacion (0-1)
        direct_channel_percentage: Porcentaje canal directo (0-1)
        ota_commission_rate: Comision OTA promedio (0-1)
        coherence_score: Score de coherencia actual
        min_coherence: Minimo de coherencia requerido

    Returns:
        FinancialCalculationResult con escenarios o bloqueo
    """
    calculator = FinancialCalculatorV2()

    financial_data = {
        "rooms": rooms,
        "adr_cop": adr_cop,
        "occupancy_rate": occupancy_rate,
        "direct_channel_percentage": direct_channel_percentage,
        "ota_commission_rate": ota_commission_rate,
    }

    return calculator.calculate_conditional(
        financial_data, coherence_score=coherence_score, min_coherence=min_coherence
    )
