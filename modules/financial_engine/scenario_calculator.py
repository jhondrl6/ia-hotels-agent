"""
Scenario-based financial calculations for hotel revenue analysis.

This module implements scenario-based financial calculations instead of exact figures,
providing conservative, realistic, and optimistic projections for hotel financial impact.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

from modules.commercial_documents.data_structures import FinancialBreakdown, EvidenceTier


class ScenarioType(Enum):
    """Types of financial scenarios for hotel revenue projections."""

    CONSERVATIVE = "conservador"
    REALISTIC = "realista"
    OPTIMISTIC = "optimista"


@dataclass
class FinancialScenario:
    """
    Represents a financial scenario with calculated projections.

    Attributes:
        scenario_type: The type of scenario (conservative, realistic, optimistic)
        monthly_loss_cop: Estimated monthly loss in Colombian Pesos
        probability: Probability of this scenario occurring (0.0 - 1.0)
        calculation_basis: Description of the basis for calculations
        confidence_score: Confidence level in this scenario (0.0 - 1.0)
        assumptions: List of assumptions made for this scenario
        disclaimer: Optional disclaimer about the scenario
    """

    scenario_type: ScenarioType
    monthly_loss_cop: float
    probability: float  # 0.0 - 1.0
    calculation_basis: str
    confidence_score: float  # 0.0 - 1.0
    assumptions: List[str] = field(default_factory=list)
    disclaimer: Optional[str] = None

    @property
    def monthly_impact_cop(self) -> float:
        """Impacto mensual en COP. Negativo = ganancia neta."""
        return self.monthly_loss_cop

    @property
    def is_net_gain(self) -> bool:
        """True si el escenario representa ganancia neta (no perdida)."""
        return self.monthly_loss_cop < 0

    @property
    def display_label(self) -> str:
        """Label legible para UI (notación colombiana)."""
        if self.is_net_gain:
            formatted = f"{abs(self.monthly_loss_cop):,.0f}".replace(",", ".")
            return f"Ganancia neta: ${formatted} COP/mes"
        formatted = f"{self.monthly_loss_cop:,.0f}".replace(",", ".")
        return f"Perdida estimada: ${formatted} COP/mes"


@dataclass
class HotelFinancialData:
    """
    Financial data for a hotel used in scenario calculations.

    Attributes:
        rooms: Number of rooms in the hotel
        adr_cop: Average Daily Rate in Colombian Pesos
        occupancy_rate: Current occupancy rate (0.0 - 1.0)
        ota_commission_rate: Average OTA commission rate (0.0 - 1.0, default 0.15)
        direct_channel_percentage: Percentage of direct bookings (0.0 - 1.0)
        ota_presence: List of OTAs where the hotel is present
        adr_source: Source of ADR data (for traceability)
        occupancy_source: Source of occupancy data (for traceability)
        channel_source: Source of direct channel percentage (for traceability)
    """

    rooms: int
    adr_cop: float  # Average Daily Rate
    occupancy_rate: float  # 0.0 - 1.0
    ota_commission_rate: float = 0.15  # 0.0 - 1.0 (default 0.15)
    direct_channel_percentage: float = 0.0  # 0.0 - 1.0
    ota_presence: List[str] = field(default_factory=lambda: ["booking", "expedia"])
    # NUEVOS — trazabilidad de fuente
    adr_source: str = "unknown"
    occupancy_source: str = "unknown"
    channel_source: str = "unknown"


class ScenarioCalculator:
    """
    Calculator for scenario-based financial projections.

    This class provides methods to calculate different financial scenarios
    based on hotel data, helping hoteliers understand potential revenue impacts.
    """

    def __init__(self):
        """Initialize the calculator with default OTA commission rate."""
        self.default_ota_commission = 0.15

    def calculate_monthly_revenue(self, hotel_data: HotelFinancialData) -> Dict[str, float]:
        """
        Calculate monthly revenue metrics for a hotel.

        Args:
            hotel_data: Financial data for the hotel

        Returns:
            Dictionary containing monthly revenue calculations
        """
        # Calculate total monthly reservations (30 days)
        days_in_month = 30
        total_room_nights = hotel_data.rooms * days_in_month
        occupied_room_nights = total_room_nights * hotel_data.occupancy_rate

        # Calculate total monthly revenue
        total_monthly_revenue = occupied_room_nights * hotel_data.adr_cop

        # Calculate revenue by channel
        ota_percentage = 1.0 - hotel_data.direct_channel_percentage
        ota_revenue = total_monthly_revenue * ota_percentage
        direct_revenue = total_monthly_revenue * hotel_data.direct_channel_percentage

        return {
            "total_reservations": round(occupied_room_nights, 0),
            "total_revenue_cop": round(total_monthly_revenue, 2),
            "ota_revenue_cop": round(ota_revenue, 2),
            "direct_revenue_cop": round(direct_revenue, 2),
            "ota_percentage": ota_percentage,
            "direct_percentage": hotel_data.direct_channel_percentage,
        }

    def calculate_scenarios(
        self, hotel_data: HotelFinancialData
    ) -> Dict[ScenarioType, FinancialScenario]:
        """
        Calculate all three financial scenarios for a hotel.

        Args:
            hotel_data: Financial data for the hotel

        Returns:
            Dictionary mapping scenario types to their calculated scenarios
        """
        return {
            ScenarioType.CONSERVATIVE: self._calculate_conservative_scenario(hotel_data),
            ScenarioType.REALISTIC: self._calculate_realistic_scenario(hotel_data),
            ScenarioType.OPTIMISTIC: self._calculate_optimistic_scenario(hotel_data),
        }

    def _calculate_conservative_scenario(
        self, hotel_data: HotelFinancialData
    ) -> FinancialScenario:
        """
        Calculate conservative scenario with minimal assumptions.

        Conservative assumptions:
        - Use 90% of provided occupancy
        - Maximum OTA commissions (18%)
        - Minimal direct channel improvement (5%)

        Args:
            hotel_data: Financial data for the hotel

        Returns:
            FinancialScenario with conservative projections
        """
        # Conservative adjustments
        conservative_occupancy = hotel_data.occupancy_rate * 0.90
        max_ota_commission = 0.18
        minimal_improvement = 0.05

        # Calculate current OTA loss
        days_in_month = 30
        occupied_room_nights = (
            hotel_data.rooms * days_in_month * hotel_data.occupancy_rate
        )
        ota_percentage = 1.0 - hotel_data.direct_channel_percentage
        ota_bookings = occupied_room_nights * ota_percentage

        current_ota_commission_loss = (
            ota_bookings * hotel_data.adr_cop * hotel_data.ota_commission_rate
        )

        # Calculate potential savings with minimal improvement
        potential_shift = ota_bookings * minimal_improvement
        savings = potential_shift * hotel_data.adr_cop * max_ota_commission

        monthly_loss = current_ota_commission_loss - savings

        return FinancialScenario(
            scenario_type=ScenarioType.CONSERVATIVE,
            monthly_loss_cop=round(monthly_loss, 2),
            probability=0.70,
            calculation_basis="90% occupancy, 18% OTA commission, 5% shift potential",
            confidence_score=0.85,
            assumptions=[
                "Occupancy rate reduced by 10% for conservative estimate",
                "Maximum OTA commission rate of 18% applied",
                "Only 5% of OTA bookings can shift to direct channel",
                "No additional bookings from IA visibility",
            ],
            disclaimer="Conservative estimates assume minimal improvement in direct bookings",
        )

    def _calculate_realistic_scenario(
        self, hotel_data: HotelFinancialData
    ) -> FinancialScenario:
        """
        Calculate realistic scenario based on provided data.

        Realistic assumptions:
        - Use provided data as-is
        - Moderate improvement potential (10% shift from OTA to direct)
        - Calculate savings

        Args:
            hotel_data: Financial data for the hotel

        Returns:
            FinancialScenario with realistic projections
        """
        # Calculate current OTA loss
        days_in_month = 30
        occupied_room_nights = (
            hotel_data.rooms * days_in_month * hotel_data.occupancy_rate
        )
        ota_percentage = 1.0 - hotel_data.direct_channel_percentage
        ota_bookings = occupied_room_nights * ota_percentage

        current_ota_commission_loss = (
            ota_bookings * hotel_data.adr_cop * hotel_data.ota_commission_rate
        )

        # Calculate potential savings with moderate improvement
        moderate_shift = 0.10  # 10% shift from OTA to direct
        potential_shift = ota_bookings * moderate_shift
        savings = potential_shift * hotel_data.adr_cop * hotel_data.ota_commission_rate

        # Additional revenue from IA visibility (5% increase in direct bookings)
        ia_visibility_boost = occupied_room_nights * 0.05 * hotel_data.adr_cop

        monthly_loss = current_ota_commission_loss - savings - ia_visibility_boost

        return FinancialScenario(
            scenario_type=ScenarioType.REALISTIC,
            monthly_loss_cop=round(monthly_loss, 2),
            probability=0.20,
            calculation_basis="Current data with 10% OTA-to-direct shift, 5% IA visibility boost",
            confidence_score=0.70,
            assumptions=[
                "Occupancy and rates based on provided hotel data",
                "10% of OTA bookings can shift to direct channel",
                "IA visibility generates 5% additional direct bookings",
                "Current OTA commission rates maintained",
            ],
            disclaimer="Realistic estimates assume moderate success in direct booking strategy",
        )

    def _calculate_optimistic_scenario(
        self, hotel_data: HotelFinancialData
    ) -> FinancialScenario:
        """
        Calculate optimistic scenario with best-case assumptions.

        Optimistic assumptions:
        - 20% shift from OTA to direct
        - Additional bookings from IA visibility (10% increase)
        - Higher conversion rates on direct channel

        Args:
            hotel_data: Financial data for the hotel

        Returns:
            FinancialScenario with optimistic projections
        """
        # Optimistic adjustments
        optimistic_occupancy = min(hotel_data.occupancy_rate * 1.05, 1.0)  # Cap at 100%
        optimistic_shift = 0.20  # 20% shift from OTA to direct
        ia_visibility_boost = 0.10  # 10% additional bookings from IA

        # Calculate current OTA loss with optimistic occupancy
        days_in_month = 30
        optimistic_room_nights = hotel_data.rooms * days_in_month * optimistic_occupancy
        ota_percentage = 1.0 - hotel_data.direct_channel_percentage
        ota_bookings = optimistic_room_nights * ota_percentage

        current_ota_commission_loss = (
            ota_bookings * hotel_data.adr_cop * hotel_data.ota_commission_rate
        )

        # Calculate savings with optimistic shift
        potential_shift = ota_bookings * optimistic_shift
        savings = potential_shift * hotel_data.adr_cop * hotel_data.ota_commission_rate

        # Additional revenue from IA visibility
        additional_bookings = optimistic_room_nights * ia_visibility_boost
        ia_revenue = additional_bookings * hotel_data.adr_cop

        monthly_loss = current_ota_commission_loss - savings - ia_revenue

        return FinancialScenario(
            scenario_type=ScenarioType.OPTIMISTIC,
            monthly_loss_cop=round(monthly_loss, 2),
            probability=0.10,
            calculation_basis="105% occupancy, 20% OTA-to-direct shift, 10% IA visibility boost",
            confidence_score=0.50,
            assumptions=[
                "Occupancy rate increased by 5% due to IA visibility",
                "20% of OTA bookings shift to direct channel",
                "IA visibility generates 10% additional direct bookings",
                "Direct channel conversion rates improve significantly",
                "Marketing automation increases repeat bookings",
            ],
            disclaimer="Optimistic estimates assume best-case scenario with strong IA adoption",
        )

    def get_hook_range(
        self, scenarios: Dict[ScenarioType, FinancialScenario]
    ) -> str:
        """
        Generate a formatted range string for initial hook presentation.

        Args:
            scenarios: Dictionary of calculated scenarios

        Returns:
            Formatted range string (e.g., "$800.000 - $3.200.000 COP/mes")
        """
        conservative = scenarios[ScenarioType.CONSERVATIVE].monthly_loss_cop
        optimistic = scenarios[ScenarioType.OPTIMISTIC].monthly_loss_cop

        # Hook range siempre muestra como perdida potencial
        # Si optimista es ganancia, mostrar como "ahorro"
        if optimistic < 0:
            optimistic = abs(optimistic)  # Mostrar como monto positivo de ahorro

        # Format with Colombian notation (dots for thousands)
        conservative_formatted = f"{conservative:,.0f}".replace(",", ".")
        optimistic_formatted = f"{optimistic:,.0f}".replace(",", ".")

        return f"${conservative_formatted} - ${optimistic_formatted} COP/mes"

    @staticmethod
    def interpret_scenario_for_hotelier(scenario: FinancialScenario) -> str:
        """
        Generate a human-readable explanation of a financial scenario.

        Args:
            scenario: The financial scenario to interpret

        Returns:
            Human-readable explanation of the scenario
        """
        scenario_names = {
            ScenarioType.CONSERVATIVE: "Conservador",
            ScenarioType.REALISTIC: "Realista",
            ScenarioType.OPTIMISTIC: "Optimista",
        }

        probability_pct = int(scenario.probability * 100)

        interpretation = (
            f"\n{'=' * 50}\n"
            f"ESCENARIO: {scenario_names.get(scenario.scenario_type, 'Desconocido')}\n"
            f"{'=' * 50}\n"
            f"\n"
            f"{scenario.display_label}\n"
            f"Probabilidad: {probability_pct}%\n"
            f"Confianza en el calculo: {int(scenario.confidence_score * 100)}%\n"
            f"\n"
            f"Base de calculo:\n"
            f"  {scenario.calculation_basis}\n"
            f"\n"
            f"Supuestos principales:\n"
        )

        for assumption in scenario.assumptions:
            interpretation += f"  • {assumption}\n"

        if scenario.disclaimer:
            interpretation += f"\nNota importante: {scenario.disclaimer}\n"

        interpretation += f"\n{'=' * 50}\n"

        return interpretation

    def calculate_breakdown(self, hotel_data: HotelFinancialData) -> FinancialBreakdown:
        """
        Calcula desglose financiero por capas.

        CAPA 1: Comisión OTA verificable (hechos)
        CAPA 2A: Ahorro por migración OTA→directo (hipótesis con fuente)
        CAPA 2B: Ingresos por visibilidad IA (hipótesis con fuente)
        """
        # Capa 1: Comisión OTA = noches_OTA × ADR × comisión_rate
        nights_per_month = hotel_data.rooms * hotel_data.occupancy_rate * 30
        ota_nights = nights_per_month * (1 - hotel_data.direct_channel_percentage)
        monthly_ota_commission = ota_nights * hotel_data.adr_cop * hotel_data.ota_commission_rate

        # Capa 2A: Shift OTA→directo
        shift_percentage = self._get_shift_percentage(hotel_data)
        shift_savings = monthly_ota_commission * shift_percentage

        # Capa 2B: IA revenue boost
        ia_boost_percentage = self._get_ia_boost_percentage(hotel_data)
        ia_revenue = nights_per_month * hotel_data.adr_cop * ia_boost_percentage

        # Evidence tier
        tier = self._determine_evidence_tier(hotel_data)

        # Fuentes de datos
        sources = self._trace_data_sources(hotel_data)

        return FinancialBreakdown(
            monthly_ota_commission_cop=monthly_ota_commission,
            ota_commission_basis=f"{int(ota_nights)} noches OTA × ${int(hotel_data.adr_cop):,} ADR × {hotel_data.ota_commission_rate*100:.0f}% comisión",
            ota_commission_source=sources.get('ota_commission', 'unknown'),
            shift_savings_cop=shift_savings,
            shift_percentage=shift_percentage,
            shift_source=sources.get('shift', 'hardcoded: sin GA4'),
            ia_revenue_cop=ia_revenue,
            ia_boost_percentage=ia_boost_percentage,
            ia_source=sources.get('ia_boost', 'estimado: sin datos GA4'),
            evidence_tier=tier.value,
            disclaimer=tier.disclaimer,
            hotel_data_sources=sources
        )

    def _determine_evidence_tier(self, hotel_data: HotelFinancialData) -> EvidenceTier:
        """Determina tier basado en disponibilidad de datos."""
        # Si tiene GA4+GSC → A
        # Si tiene benchmarks regionales → B
        # Si solo tiene scraping → C
        # Lógica: por ahora siempre C hasta que GA4 se integre
        return EvidenceTier.C

    def _get_shift_percentage(self, hotel_data: HotelFinancialData) -> float:
        """Porcentaje de migración OTA→directo. Documentar fuente."""
        # TODO: Reemplazar con dato de GA4 cuando esté disponible
        return 0.10  # Benchmark: hoteles con mejora digital

    def _get_ia_boost_percentage(self, hotel_data: HotelFinancialData) -> float:
        """Porcentaje de boost por visibilidad IA. Documentar fuente."""
        # TODO: Reemplazar con dato de GA4 cuando esté disponible
        return 0.05  # Estimado: sin datos GA4

    def _trace_data_sources(self, hotel_data: HotelFinancialData) -> Dict[str, str]:
        """Trazabilidad: mapea cada input a su fuente."""
        return {
            'adr': getattr(hotel_data, 'adr_source', 'unknown'),
            'rooms': 'hotel_data',
            'occupancy': getattr(hotel_data, 'occupancy_source', 'unknown'),
            'ota_commission': 'industry_standard_15pct',
            'direct_channel': getattr(hotel_data, 'channel_source', 'unknown'),
            'shift': 'hardcoded: sin GA4',
            'ia_boost': 'estimado: sin datos GA4'
        }
