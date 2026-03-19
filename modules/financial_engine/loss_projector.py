"""
Loss Projector Module

Projects financial losses and opportunities with confidence intervals.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from .scenario_calculator import ScenarioType, FinancialScenario


@dataclass
class ProjectionInterval:
    """Represents a confidence interval for projections."""
    lower_bound: float
    upper_bound: float
    confidence_level: float  # 0.0 - 1.0
    basis: str


@dataclass
class MonthlyProjection:
    """Represents a single month's financial projection."""
    month: int
    month_name: str
    conservative: float
    realistic: float
    optimistic: float
    interval: ProjectionInterval


@dataclass
class LossProjection:
    """Complete loss projection for a hotel over multiple months."""
    hotel_name: str
    projection_date: datetime
    months: int
    monthly_projections: List[MonthlyProjection]
    total_conservative: float
    total_realistic: float
    total_optimistic: float
    recommended_target: float  # Usually realistic
    assumptions: List[str]


class LossProjector:
    """
    Projects financial losses and opportunities with confidence intervals.
    
    Uses scenario-based calculations to project potential losses over time
    and calculates ROI for intervention strategies.
    """
    
    def __init__(self, hotel_name: str, projection_months: int = 12):
        """
        Initialize the loss projector.
        
        Args:
            hotel_name: Name of the hotel
            projection_months: Number of months to project (default: 12)
        """
        self.hotel_name = hotel_name
        self.projection_months = projection_months
        self._degradation_rate = 0.02  # 2% monthly degradation
        
    def project_from_scenarios(
        self, 
        scenarios: Dict[ScenarioType, FinancialScenario]
    ) -> LossProjection:
        """
        Create monthly projections based on scenario calculations.
        
        Each month applies a slight degradation factor to simulate
        increasing opportunity costs over time.
        
        Args:
            scenarios: Dictionary mapping ScenarioType to FinancialScenario
            
        Returns:
            LossProjection with monthly breakdown and totals
        """
        monthly_projections = []
        total_conservative = 0.0
        total_realistic = 0.0
        total_optimistic = 0.0
        
        for month in range(1, self.projection_months + 1):
            projection = self._calculate_monthly_projection(month, scenarios)
            monthly_projections.append(projection)
            
            total_conservative += projection.conservative
            total_realistic += projection.realistic
            total_optimistic += projection.optimistic
        
        assumptions = [
            f"Proyeccion basada en {self.projection_months} meses",
            "Degradacion mensual aplicada: 2% (costo de oportunidad creciente)",
            "Valores en COP (Pesos Colombianos)",
            "Intervalos de confianza calculados sobre datos historicos"
        ]
        
        return LossProjection(
            hotel_name=self.hotel_name,
            projection_date=datetime.now(),
            months=self.projection_months,
            monthly_projections=monthly_projections,
            total_conservative=round(total_conservative, 2),
            total_realistic=round(total_realistic, 2),
            total_optimistic=round(total_optimistic, 2),
            recommended_target=round(total_realistic, 2),
            assumptions=assumptions
        )
    
    def _calculate_monthly_projection(
        self, 
        month: int, 
        scenarios: Dict[ScenarioType, FinancialScenario]
    ) -> MonthlyProjection:
        """
        Calculate projection for a specific month.
        
        Applies degradation factor based on month number to simulate
        increasing opportunity costs over time.
        
        Args:
            month: Month number (1-indexed)
            scenarios: Dictionary of scenarios
            
        Returns:
            MonthlyProjection for the specified month
        """
        # Get base values from scenarios
        conservative_scenario = scenarios.get(ScenarioType.CONSERVATIVE)
        if not conservative_scenario:
            raise ValueError("Conservative scenario required")
        conservative_value = conservative_scenario.monthly_loss_cop
        realistic_scenario = scenarios.get(ScenarioType.REALISTIC)
        if not realistic_scenario:
            raise ValueError("Realistic scenario required")
        realistic_value = realistic_scenario.monthly_loss_cop
        optimistic_scenario = scenarios.get(ScenarioType.OPTIMISTIC)
        if not optimistic_scenario:
            raise ValueError("Optimistic scenario required")
        optimistic_value = optimistic_scenario.monthly_loss_cop
        
        # Normalize to monthly values
        monthly_conservative = conservative_value / 12
        monthly_realistic = realistic_value / 12
        monthly_optimistic = optimistic_value / 12
        
        # Apply degradation factor (opportunity cost increases over time)
        degradation = 1 + (self._degradation_rate * (month - 1))
        
        adjusted_conservative = monthly_conservative * degradation
        adjusted_realistic = monthly_realistic * degradation
        adjusted_optimistic = monthly_optimistic * degradation
        
        # Calculate confidence interval
        interval = self._calculate_interval(adjusted_conservative, adjusted_optimistic)
        
        month_names = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]
        
        current_month_idx = (datetime.now().month - 1 + month - 1) % 12
        month_name = f"Mes {month} ({month_names[current_month_idx]})"
        
        return MonthlyProjection(
            month=month,
            month_name=month_name,
            conservative=round(adjusted_conservative, 2),
            realistic=round(adjusted_realistic, 2),
            optimistic=round(adjusted_optimistic, 2),
            interval=interval
        )
    
    def _calculate_interval(
        self, 
        conservative: float, 
        optimistic: float
    ) -> ProjectionInterval:
        """
        Calculate confidence interval between conservative and optimistic scenarios.
        
        Args:
            conservative: Conservative scenario value (lower bound)
            optimistic: Optimistic scenario value (upper bound)
            
        Returns:
            ProjectionInterval with bounds and confidence level
        """
        # Confidence level based on data quality assumptions
        # Wider intervals get lower confidence
        range_width = abs(optimistic - conservative)
        avg_value = (conservative + optimistic) / 2
        
        if avg_value > 0:
            relative_range = range_width / avg_value
            if relative_range < 0.2:
                confidence_level = 0.85
                basis = "Datos historicos solidos, baja variabilidad"
            elif relative_range < 0.4:
                confidence_level = 0.70
                basis = "Datos historicos moderados"
            else:
                confidence_level = 0.55
                basis = "Alta incertidumbre, datos limitados"
        else:
            confidence_level = 0.50
            basis = "Datos insuficientes para intervalo confiable"
        
        return ProjectionInterval(
            lower_bound=round(min(conservative, optimistic), 2),
            upper_bound=round(max(conservative, optimistic), 2),
            confidence_level=confidence_level,
            basis=basis
        )
    
    def get_summary_table(self, projection: LossProjection) -> List[Dict]:
        """
        Convert projection to table-friendly format.
        
        Args:
            projection: LossProjection to format
            
        Returns:
            List of dictionaries, each representing a month's data
        """
        table = []
        for monthly in projection.monthly_projections:
            row = {
                "month": monthly.month,
                "month_name": monthly.month_name,
                "conservative": monthly.conservative,
                "realistic": monthly.realistic,
                "optimistic": monthly.optimistic,
                "confidence": monthly.interval.confidence_level
            }
            table.append(row)
        return table
    
    def get_roi_projection(
        self, 
        projection: LossProjection, 
        package_cost_monthly: float
    ) -> Dict[str, float]:
        """
        Calculate ROI projection for each scenario.
        
        ROI = (savings - cost) / cost
        
        Args:
            projection: LossProjection with savings estimates
            package_cost_monthly: Monthly cost of the solution package
            
        Returns:
            Dictionary with ROI for each scenario
        """
        total_cost = package_cost_monthly * projection.months
        
        def calculate_roi(savings: float) -> float:
            if total_cost == 0:
                return 0.0
            return (savings - total_cost) / total_cost
        
        return {
            "roi_conservative": round(calculate_roi(projection.total_conservative), 4),
            "roi_realistic": round(calculate_roi(projection.total_realistic), 4),
            "roi_optimistic": round(calculate_roi(projection.total_optimistic), 4),
            "total_investment": round(total_cost, 2),
            "projected_savings_conservative": projection.total_conservative,
            "projected_savings_realistic": projection.total_realistic,
            "projected_savings_optimistic": projection.total_optimistic
        }
    
    @staticmethod
    def format_projection_for_client(projection: LossProjection) -> str:
        """
        Format projection as readable text for client presentation.
        
        Args:
            projection: LossProjection to format
            
        Returns:
            Formatted string with highlighted key numbers
        """
        lines = [
            "=" * 60,
            f"PROYECCION FINANCIERA: {projection.hotel_name.upper()}",
            f"Fecha de proyeccion: {projection.projection_date.strftime('%d/%m/%Y')}",
            "=" * 60,
            "",
            f"Periodo: {projection.months} meses",
            "",
            "RESUMEN DE PERDIDAS PROYECTADAS:",
            "-" * 40,
            f"  Escenario Conservador:  ${projection.total_conservative:,.0f} COP",
            f"  Escenario Realista:     ${projection.total_realistic:,.0f} COP",
            f"  Escenario Optimista:    ${projection.total_optimistic:,.0f} COP",
            "",
            f"META RECOMENDADA: ${projection.recommended_target:,.0f} COP",
            "",
            "DETALLE MENSUAL:",
            "-" * 40,
        ]
        
        for monthly in projection.monthly_projections[:6]:  # Show first 6 months
            lines.append(
                f"  {monthly.month_name:<20} "
                f"Realista: ${monthly.realistic:>12,.0f}"
            )
        
        if len(projection.monthly_projections) > 6:
            lines.append(f"  ... y {len(projection.monthly_projections) - 6} meses adicionales")
        
        lines.extend([
            "",
            "SUPUESTOS:",
            "-" * 40,
        ])
        for assumption in projection.assumptions:
            lines.append(f"  - {assumption}")
        
        lines.extend([
            "",
            "=" * 60,
            "NOTA IMPORTANTE:",
            "-" * 40,
            "Estas proyecciones son estimaciones basadas en datos",
            "disponibles y modelos estadisticos. Los resultados reales",
            "pueden variar segun condiciones del mercado y ejecucion",
            "de las estrategias recomendadas.",
            "=" * 60,
        ])
        
        return "\n".join(lines)
    
    @staticmethod
    def compare_to_benchmark(
        projection: LossProjection, 
        benchmark_regional: float
    ) -> Dict[str, Any]:
        """
        Compare projection to regional benchmark.
        
        Args:
            projection: LossProjection to compare
            benchmark_regional: Regional benchmark value (annual)
            
        Returns:
            Dictionary with comparison analysis
        """
        monthly_benchmark = benchmark_regional / 12
        avg_monthly_loss = projection.total_realistic / projection.months
        
        difference = avg_monthly_loss - monthly_benchmark
        percentage_diff = (difference / monthly_benchmark * 100) if monthly_benchmark > 0 else 0
        
        if percentage_diff > 20:
            status = "CRITICO"
            recommendation = "Perdidas significativamente por encima del benchmark. Intervencion urgente recomendada."
        elif percentage_diff > 5:
            status = "ELEVADO"
            recommendation = "Perdidas sobre el promedio regional. Mejoras operativas necesarias."
        elif percentage_diff > -5:
            status = "ALINEADO"
            recommendation = "En linea con el benchmark regional. Mantener y optimizar."
        else:
            status = "OPTIMO"
            recommendation = "Por debajo del benchmark. Caso de exito potencial."
        
        return {
            "hotel_name": projection.hotel_name,
            "avg_monthly_loss": round(avg_monthly_loss, 2),
            "regional_benchmark_monthly": round(monthly_benchmark, 2),
            "difference": round(difference, 2),
            "percentage_difference": round(percentage_diff, 2),
            "status": status,
            "recommendation": recommendation,
            "annual_projection_vs_benchmark": round(
                projection.total_realistic - benchmark_regional, 2
            )
        }
