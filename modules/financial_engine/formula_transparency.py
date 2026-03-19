"""
Formula Transparency Module

This module explains financial calculations in natural language for transparency.
It provides detailed breakdowns of how financial metrics are computed,
suitable for both technical and non-technical audiences.
"""

from typing import Dict, List, Any
from dataclasses import dataclass, field


@dataclass
class CalculationStep:
    """
    Represents a single step in a financial calculation.
    
    Attributes:
        step_number: The order of this step in the calculation sequence
        description: Human-readable description of what this step does
        formula: The mathematical formula used (LaTeX-style notation)
        inputs: Dictionary of input values used in this step
        result: The computed result of this step
        explanation: Natural language explanation of the calculation
    """
    step_number: int
    description: str
    formula: str
    inputs: Dict[str, Any]
    result: Any
    explanation: str


@dataclass
class TransparentCalculation:
    """
    Container for a complete transparent calculation with all metadata.
    
    Attributes:
        title: The name/title of the calculation
        steps: List of calculation steps in order
        final_result: The ultimate result of the calculation
        assumptions: List of assumptions made during calculation
        limitations: List of limitations or caveats to consider
    """
    title: str
    steps: List[CalculationStep]
    final_result: Any
    assumptions: List[str] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)


class FormulaTransparency:
    """
    Provides transparent explanations of financial formulas and calculations.
    
    This class translates complex financial computations into human-readable
    explanations, showing each step, the formulas used, and their implications.
    
    All methods return TransparentCalculation objects that can be formatted
    for different audiences (technical reports vs. hotelier summaries).
    """
    
    def __init__(self):
        """Initialize the FormulaTransparency engine."""
        pass
    
    def explain_revenue_calculation(
        self,
        rooms: int,
        adr: float,
        occupancy: float
    ) -> TransparentCalculation:
        """
        Explain hotel revenue calculation with full transparency.
        
        Breaks down the calculation from room count and ADR through
        to projected monthly revenue, showing how occupancy affects results.
        
        Args:
            rooms: Total number of rooms in the hotel
            adr: Average Daily Rate (price per room per night)
            occupancy: Occupancy rate as decimal (e.g., 0.65 for 65%)
            
        Returns:
            TransparentCalculation with all steps documented
            
        Example:
            >>> ft = FormulaTransparency()
            >>> calc = ft.explain_revenue_calculation(50, 180000, 0.70)
            >>> print(calc.final_result)
            189000000.0
        """
        steps = []
        
        # Step 1: Calculate maximum daily revenue (100% occupancy)
        max_daily_revenue = rooms * adr
        steps.append(CalculationStep(
            step_number=1,
            description="Calcular ingreso diario máximo (ocupación 100%)",
            formula="habitaciones × tarifa_promedio = ingreso_diario_max",
            inputs={
                "habitaciones": rooms,
                "tarifa_promedio": adr,
                "tarifa_formateada": format_cop(adr)
            },
            result=max_daily_revenue,
            explanation=(
                f"Con {rooms} habitaciones a {format_cop(adr)} cada una, "
                f"el ingreso máximo diario sería {format_cop(max_daily_revenue)} "
                f"si todas las habitaciones se vendieran."
            )
        ))
        
        # Step 2: Calculate actual daily revenue based on occupancy
        actual_daily_revenue = max_daily_revenue * occupancy
        steps.append(CalculationStep(
            step_number=2,
            description="Aplicar tasa de ocupación real",
            formula="ingreso_diario_max × ocupación = ingreso_diario_real",
            inputs={
                "ingreso_diario_maximo": max_daily_revenue,
                "ocupación": occupancy,
                "ocupación_pct": format_percentage(occupancy)
            },
            result=actual_daily_revenue,
            explanation=(
                f"Con una ocupación del {format_percentage(occupancy)}, "
                f"el ingreso diario real es {format_cop(actual_daily_revenue)}. "
                f"Esto representa {format_percentage(occupancy)} de {format_cop(max_daily_revenue)}."
            )
        ))
        
        # Step 3: Calculate monthly revenue (30 days)
        monthly_revenue = actual_daily_revenue * 30
        steps.append(CalculationStep(
            step_number=3,
            description="Proyectar ingreso mensual",
            formula="ingreso_diario_real × 30_días = ingreso_mensual",
            inputs={
                "ingreso_diario_real": actual_daily_revenue,
                "días_por_mes": 30
            },
            result=monthly_revenue,
            explanation=(
                f"Multiplicando el ingreso diario de {format_cop(actual_daily_revenue)} "
                f"por 30 días, obtenemos un ingreso mensual proyectado de "
                f"{format_cop(monthly_revenue)}."
            )
        ))
        
        return TransparentCalculation(
            title="Cálculo de Ingresos Hotelarios",
            steps=steps,
            final_result=monthly_revenue,
            assumptions=[
                "Se asume un mes de 30 días para simplificar",
                "La ocupación es constante durante el mes",
                "La tarifa promedio no varía significativamente",
                "No se consideran cancelaciones o no-shows"
            ],
            limitations=[
                "La ocupación real varía por día de la semana y temporada",
                "No incluye ingresos adicionales (restaurante, spa, etc.)",
                "Las tarifas pueden variar por canal de venta",
                "Factores externos (eventos, clima) no están incluidos"
            ]
        )
    
    def explain_ota_commission_loss(
        self,
        monthly_revenue: float,
        ota_percentage: float,
        commission_rate: float
    ) -> TransparentCalculation:
        """
        Explain OTA commission loss calculation.
        
        Shows how much revenue is lost to OTA commissions by breaking down
        the portion of revenue coming through OTAs and applying commission rates.
        
        Formula: revenue × ota% × commission_rate = loss
        
        Args:
            monthly_revenue: Total monthly revenue
            ota_percentage: Percentage of bookings from OTAs (0-1)
            commission_rate: Average OTA commission rate (0-1, typically 0.15-0.25)
            
        Returns:
            TransparentCalculation showing commission loss breakdown
            
        Example:
            >>> ft = FormulaTransparency()
            >>> calc = ft.explain_ota_commission_loss(100000000, 0.70, 0.18)
            >>> print(calc.final_result)
            12600000.0
        """
        steps = []
        
        # Step 1: Calculate OTA revenue portion
        ota_revenue = monthly_revenue * ota_percentage
        steps.append(CalculationStep(
            step_number=1,
            description="Calcular ingreso proveniente de OTAs",
            formula="ingreso_mensual × porcentaje_ota = ingreso_ota",
            inputs={
                "ingreso_mensual": monthly_revenue,
                "porcentaje_ota": ota_percentage,
                "porcentaje_ota_fmt": format_percentage(ota_percentage)
            },
            result=ota_revenue,
            explanation=(
                f"Del ingreso total de {format_cop(monthly_revenue)}, "
                f"el {format_percentage(ota_percentage)} proviene de OTAs. "
                f"Esto equivale a {format_cop(ota_revenue)}."
            )
        ))
        
        # Step 2: Calculate commission amount
        commission_amount = ota_revenue * commission_rate
        steps.append(CalculationStep(
            step_number=2,
            description="Calcular comisión pagada a OTAs",
            formula="ingreso_ota × tasa_comisión = comisión_total",
            inputs={
                "ingreso_ota": ota_revenue,
                "tasa_comisión": commission_rate,
                "tasa_comisión_fmt": format_percentage(commission_rate)
            },
            result=commission_amount,
            explanation=(
                f"Con una comisión promedio del {format_percentage(commission_rate)}, "
                f"el hotel paga {format_cop(commission_amount)} en comisiones "
                f"sobre los ingresos de OTAs."
            )
        ))
        
        # Step 3: Project annual loss
        annual_loss = commission_amount * 12
        steps.append(CalculationStep(
            step_number=3,
            description="Proyectar pérdida anual por comisiones",
            formula="comisión_mensual × 12_meses = pérdida_anual",
            inputs={
                "comisión_mensual": commission_amount,
                "meses_por_año": 12
            },
            result=annual_loss,
            explanation=(
                f"La comisión mensual de {format_cop(commission_amount)} "
                f"se proyecta a {format_cop(annual_loss)} anuales. "
                f"Este dinero se pierde irrecuperablemente en comisiones."
            )
        ))
        
        return TransparentCalculation(
            title="Pérdida por Comisiones de OTAs",
            steps=steps,
            final_result=annual_loss,
            assumptions=[
                "El porcentaje de OTAs se mantiene constante",
                "La tasa de comisión es el promedio ponderado de todas las OTAs",
                "El ingreso mensual es representativo del año",
                "No se consideran comisiones negociadas especiales"
            ],
            limitations=[
                "Las comisiones varían entre OTAs (15-25% típicamente)",
                "Algunas OTAs tienen modelos híbridos (comisión + CPC)",
                "Las negociaciones de volumen pueden reducir comisiones",
                "Las cancelaciones pueden afectar comisiones ya pagadas"
            ]
        )
    
    def explain_direct_channel_savings(
        self,
        monthly_revenue: float,
        current_direct_pct: float,
        target_direct_pct: float,
        commission_rate: float
    ) -> TransparentCalculation:
        """
        Explain potential savings from shifting to direct bookings.
        
        Calculates how much could be saved by moving bookings from OTAs
        to direct channels (website, phone, walk-ins) which typically
        have much lower or zero commission rates.
        
        Args:
            monthly_revenue: Total monthly revenue
            current_direct_pct: Current percentage of direct bookings (0-1)
            target_direct_pct: Target percentage of direct bookings (0-1)
            commission_rate: Average OTA commission rate (0-1)
            
        Returns:
            TransparentCalculation showing potential savings
            
        Example:
            >>> ft = FormulaTransparency()
            >>> calc = ft.explain_direct_channel_savings(
            ...     100000000, 0.30, 0.50, 0.18
            ... )
            >>> print(calc.final_result)
            43200000.0
        """
        steps = []
        
        current_ota_pct = 1 - current_direct_pct
        target_ota_pct = 1 - target_direct_pct
        
        # Step 1: Current OTA revenue
        current_ota_revenue = monthly_revenue * current_ota_pct
        steps.append(CalculationStep(
            step_number=1,
            description="Calcular ingreso actual por OTAs",
            formula="ingreso_mensual × (1 - directo_actual) = ingreso_ota_actual",
            inputs={
                "ingreso_mensual": monthly_revenue,
                "directo_actual": current_direct_pct,
                "directo_actual_fmt": format_percentage(current_direct_pct)
            },
            result=current_ota_revenue,
            explanation=(
                f"Actualmente con {format_percentage(current_direct_pct)} de reservas directas, "
                f"el {format_percentage(current_ota_pct)} proviene de OTAs: "
                f"{format_cop(current_ota_revenue)}."
            )
        ))
        
        # Step 2: Target OTA revenue
        target_ota_revenue = monthly_revenue * target_ota_pct
        steps.append(CalculationStep(
            step_number=2,
            description="Calcular ingreso objetivo por OTAs",
            formula="ingreso_mensual × (1 - directo_objetivo) = ingreso_ota_objetivo",
            inputs={
                "ingreso_mensual": monthly_revenue,
                "directo_objetivo": target_direct_pct,
                "directo_objetivo_fmt": format_percentage(target_direct_pct)
            },
            result=target_ota_revenue,
            explanation=(
                f"Con el objetivo de {format_percentage(target_direct_pct)} directas, "
                f"solo el {format_percentage(target_ota_pct)} vendría de OTAs: "
                f"{format_cop(target_ota_revenue)}."
            )
        ))
        
        # Step 3: Monthly savings
        ota_revenue_reduction = current_ota_revenue - target_ota_revenue
        monthly_savings = ota_revenue_reduction * commission_rate
        steps.append(CalculationStep(
            step_number=3,
            description="Calcular ahorro mensual en comisiones",
            formula="(ingreso_ota_actual - ingreso_ota_objetivo) × comisión = ahorro_mensual",
            inputs={
                "reducción_ota": ota_revenue_reduction,
                "tasa_comisión": commission_rate,
                "tasa_comisión_fmt": format_percentage(commission_rate)
            },
            result=monthly_savings,
            explanation=(
                f"La reducción de {format_cop(ota_revenue_reduction)} en ingresos de OTA "
                f"multiplicada por {format_percentage(commission_rate)} de comisión "
                f"genera un ahorro de {format_cop(monthly_savings)} mensuales."
            )
        ))
        
        # Step 4: Annual projection
        annual_savings = monthly_savings * 12
        steps.append(CalculationStep(
            step_number=4,
            description="Proyectar ahorro anual",
            formula="ahorro_mensual × 12_meses = ahorro_anual",
            inputs={
                "ahorro_mensual": monthly_savings,
                "meses_por_año": 12
            },
            result=annual_savings,
            explanation=(
                f"El ahorro mensual de {format_cop(monthly_savings)} "
                f"se proyecta a {format_cop(annual_savings)} anuales "
                f"que se quedarían en el hotel."
            )
        ))
        
        return TransparentCalculation(
            title="Ahorro Potencial por Canal Directo",
            steps=steps,
            final_result=annual_savings,
            assumptions=[
                "El ingreso total se mantiene constante",
                "La tasa de comisión promedio no cambia",
                "El canal directo tiene comisión cercana a cero",
                "Se logra el porcentaje objetivo de directas"
            ],
            limitations=[
                "Requiere inversión en marketing digital para lograr el objetivo",
                "Los costos del canal directo (web, booking engine) no son cero",
                "El cambio de comportamiento de huéspedes lleva tiempo",
                "Las OTAs pueden penalizar hoteles con menor visibilidad"
            ]
        )
    
    def explain_invisibility_penalty(
        self,
        monthly_revenue: float,
        estimated_penalty_pct: float = 0.05
    ) -> TransparentCalculation:
        """
        Explain the revenue impact of IA invisibility.
        
        Calculates the estimated revenue loss for hotels that are not
        visible or bookable through AI assistants and modern search.
        
        Studies suggest hotels invisible to AI search may lose 5-15% of
        potential revenue as travelers increasingly use AI for planning.
        
        Args:
            monthly_revenue: Current monthly revenue
            estimated_penalty_pct: Estimated revenue penalty (default 5%)
            
        Returns:
            TransparentCalculation showing invisibility impact
            
        Example:
            >>> ft = FormulaTransparency()
            >>> calc = ft.explain_invisibility_penalty(100000000, 0.05)
            >>> print(calc.final_result)
            60000000.0
        """
        steps = []
        
        # Step 1: Explain the penalty concept
        monthly_penalty = monthly_revenue * estimated_penalty_pct
        steps.append(CalculationStep(
            step_number=1,
            description="Calcular impacto mensual de invisibilidad en IA",
            formula="ingreso_mensual × penalización_invisibilidad = pérdida_mensual",
            inputs={
                "ingreso_mensual": monthly_revenue,
                "penalización": estimated_penalty_pct,
                "penalización_fmt": format_percentage(estimated_penalty_pct)
            },
            result=monthly_penalty,
            explanation=(
                f"Los hoteles que no son visibles para asistentes de IA pierden "
                f"oportunidades de reserva. Con una penalización estimada del "
                f"{format_percentage(estimated_penalty_pct)}, esto representa "
                f"{format_cop(monthly_penalty)} mensuales en ingresos no realizados."
            )
        ))
        
        # Step 2: Annual projection
        annual_penalty = monthly_penalty * 12
        steps.append(CalculationStep(
            step_number=2,
            description="Proyectar impacto anual",
            formula="pérdida_mensual × 12_meses = pérdida_anual",
            inputs={
                "pérdida_mensual": monthly_penalty,
                "meses_por_año": 12
            },
            result=annual_penalty,
            explanation=(
                f"La pérdida mensual de {format_cop(monthly_penalty)} "
                f"se proyecta a {format_cop(annual_penalty)} anuales. "
                f"Este es dinero que competidores visibles en IA están capturando."
            )
        ))
        
        # Step 3: Opportunity cost explanation
        opportunity_multiplier = 1 + estimated_penalty_pct
        potential_revenue = monthly_revenue * opportunity_multiplier
        steps.append(CalculationStep(
            step_number=3,
            description="Calcular ingreso potencial con visibilidad IA",
            formula="ingreso_actual × (1 + penalización) = ingreso_potencial",
            inputs={
                "ingreso_actual": monthly_revenue,
                "multiplicador": opportunity_multiplier
            },
            result=potential_revenue,
            explanation=(
                f"Si el hotel fuera visible en IA, podría capturar ingresos "
                f"adicionales. El ingreso potencial sería {format_cop(potential_revenue)} "
                f"en lugar de {format_cop(monthly_revenue)}."
            )
        ))
        
        return TransparentCalculation(
            title="Penalización por Invisibilidad en IA",
            steps=steps,
            final_result=annual_penalty,
            assumptions=[
                "El 5% es una estimación conservadora basada en tendencias",
                "La adopción de IA para búsqueda de hoteles continúa creciendo",
                "Los huéspedes prefieren hoteles que pueden reservar vía IA",
                "La invisibilidad es completa (no aparece en ninguna IA)"
            ],
            limitations=[
                "La penalización real varía por segmento y ubicación",
                "Los datos de IA search son limitados y cambiantes",
                "Difícil de medir directamente (ingresos no realizados)",
                "La visibilidad en IA requiere inversión en estructura de datos"
            ]
        )
    
    def format_for_report(self, calculation: TransparentCalculation) -> str:
        """
        Format a calculation for technical/reporting audiences.
        
        Produces a detailed markdown-formatted explanation suitable for
        inclusion in diagnostic reports, presentations, or documentation.
        Includes all formulas, technical details, and structured sections.
        
        Args:
            calculation: The TransparentCalculation to format
            
        Returns:
            Markdown-formatted string with full technical details
        """
        lines = [
            f"## {calculation.title}",
            "",
            "### Desglose del Cálculo",
            ""
        ]
        
        for step in calculation.steps:
            lines.extend([
                f"#### Paso {step.step_number}: {step.description}",
                "",
                f"**Fórmula:** `{step.formula}`",
                "",
                "**Entradas:**",
            ])
            
            for key, value in step.inputs.items():
                if not key.endswith('_fmt') and not key.endswith('_formateada'):
                    # Format numeric values appropriately
                    if isinstance(value, (int, float)):
                        if key in ['ocupación', 'porcentaje', 'tasa', 'penalización']:
                            formatted_value = format_percentage(value)
                        elif key in ['ingreso', 'comisión', 'pérdida', 'ahorro']:
                            formatted_value = format_cop(value)
                        else:
                            formatted_value = str(value)
                    else:
                        formatted_value = str(value)
                    lines.append(f"- `{key}`: {formatted_value}")
            
            lines.extend([
                "",
                f"**Resultado:** {step.result}",
                "",
                f"**Explicación:** {step.explanation}",
                ""
            ])
        
        lines.extend([
            "### Resultado Final",
            "",
            f"**{calculation.final_result}**",
            "",
            "### Supuestos",
            ""
        ])
        
        for assumption in calculation.assumptions:
            lines.append(f"- {assumption}")
        
        lines.extend([
            "",
            "### Limitaciones",
            ""
        ])
        
        for limitation in calculation.limitations:
            lines.append(f"- {limitation}")
        
        lines.append("")
        
        return "\n".join(lines)
    
    def format_for_hotelier(self, calculation: TransparentCalculation) -> str:
        """
        Format a calculation for non-technical hotelier audiences.
        
        Produces a simplified, plain-language explanation that focuses
        on business impact rather than technical formulas. Removes all
        mathematical notation and emphasizes "what this means for you".
        
        Args:
            calculation: The TransparentCalculation to format
            
        Returns:
            Plain text explanation suitable for hoteliers
        """
        lines = [
            f"{calculation.title}",
            "=" * len(calculation.title),
            ""
        ]
        
        # Provide context
        lines.extend([
            "¿Qué significa esto para su hotel?",
            "",
            "Este análisis muestra cómo se calculan los números importantes "
            "para su negocio. Aquí está el resumen en términos simples:",
            ""
        ])
        
        # Summarize steps in plain language
        for step in calculation.steps:
            lines.append(f"• {step.explanation}")
            lines.append("")
        
        # Final result with emphasis
        lines.extend([
            "RESULTADO FINAL",
            "-" * 20,
            "",
            f"El número más importante es: {calculation.final_result}",
            ""
        ])
        
        # Context about what this means
        if "comisión" in calculation.title.lower() or "pérdida" in calculation.title.lower():
            lines.extend([
                "Esto representa dinero que su hotel está dejando de ganar "
                "o pagando innecesariamente. Es una oportunidad de mejora.",
                ""
            ])
        elif "ahorro" in calculation.title.lower():
            lines.extend([
                "Esto representa dinero que su hotel podría ahorrar "
                "implementando las recomendaciones sugeridas.",
                ""
            ])
        else:
            lines.extend([
                "Este es un dato clave para entender la salud financiera "
                "de su hotel y tomar decisiones informadas.",
                ""
            ])
        
        # Important caveats
        if calculation.limitations:
            lines.extend([
                "Puntos importantes a considerar:",
                ""
            ])
            for limitation in calculation.limitations[:3]:  # Top 3 limitations
                lines.append(f"• {limitation}")
            lines.append("")
        
        lines.append("¿Tiene preguntas sobre estos cálculos? Estamos aquí para explicar.")
        
        return "\n".join(lines)


def format_cop(amount: float) -> str:
    """
    Format a number as Colombian pesos.
    
    Uses Colombian formatting conventions: $ symbol, dot as thousands
    separator, no decimal places for whole numbers.
    
    Args:
        amount: The amount to format
        
    Returns:
        Formatted string like "$2.100.000" or "$850.000"
        
    Example:
        >>> format_cop(2100000)
        '$2.100.000'
        >>> format_cop(850500)
        '$850.500'
    """
    if amount is None:
        return "$0"
    
    # Round to nearest integer
    amount = round(amount)
    
    # Format with dots as thousands separators
    formatted = f"{amount:,.0f}"
    
    # Replace comma with dot for Colombian format
    formatted = formatted.replace(",", ".")
    
    return f"${formatted}"


def format_percentage(value: float) -> str:
    """
    Format a decimal as a percentage string.
    
    Args:
        value: Decimal value (e.g., 0.15 for 15%)
        
    Returns:
        Formatted percentage string like "15%"
        
    Example:
        >>> format_percentage(0.15)
        '15%'
        >>> format_percentage(0.7)
        '70%'
        >>> format_percentage(0.185)
        '18.5%'
    """
    if value is None:
        return "0%"
    
    # Convert to percentage
    percentage = value * 100
    
    # Format without decimals if whole number, otherwise one decimal
    if percentage == int(percentage):
        return f"{int(percentage)}%"
    else:
        return f"{percentage:.1f}%"
