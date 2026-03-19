"""
Two-Phase User Flow Module for IA Hoteles Agent v4.0

This module implements the two-phase user flow: Hook (Phase 1) -> Input (Phase 2)

Phase 1 (Hook): Capture user attention with estimated loss range based on benchmarks
Phase 2 (Input): Collect detailed hotel data and calculate precise scenarios
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from ..data_validation.cross_validator import CrossValidator
from ..data_validation.confidence_taxonomy import ConfidenceLevel
from ..financial_engine.scenario_calculator import ScenarioCalculator, HotelFinancialData


@dataclass
class Phase1Result:
    """
    Result from Phase 1 (Hook) of the two-phase flow.

    Contains the initial hook message with estimated loss range based on
    regional benchmarks. This is designed to capture user attention and
    encourage them to proceed to Phase 2.
    """

    hotel_name: str
    hotel_url: str
    region: str
    hook_message: str
    loss_range_min: float
    loss_range_max: float
    next_step: str
    confidence_level: str  # "low" for phase 1
    disclaimer: str
    requires_user_input: bool = True


@dataclass
class Phase2Result:
    """
    Result from Phase 2 (Input) of the two-phase flow.

    Contains validated hotel data, confidence scores, conflict reports,
    and calculated financial scenarios based on user-provided inputs.
    """

    hotel_data: HotelFinancialData
    validated_fields: Dict[str, Any]
    confidence_scores: Dict[str, float]
    has_conflicts: bool
    conflicts_report: List[str]
    can_proceed: bool
    scenarios: Optional[Dict] = None


@dataclass
class HotelInputs:
    """
    User-provided hotel data inputs for Phase 2.

    All fields are optional to allow gradual data collection.
    None values indicate fields that still need to be collected.
    """

    rooms: Optional[int] = None
    adr_cop: Optional[float] = None
    occupancy_rate: Optional[float] = None
    ota_presence: List[str] = field(default_factory=list)
    direct_channel_percentage: Optional[float] = None
    whatsapp_number: Optional[str] = None


class TwoPhaseOrchestrator:
    """
    Orchestrates the two-phase user flow for hotel financial analysis.

    Phase 1: Generates an attention-grabbing hook based on regional benchmarks
    Phase 2: Validates user inputs and calculates precise financial scenarios

    This approach minimizes friction by showing value before asking for detailed data.
    """

    def __init__(self, plan_maestro_data: Dict = None):
        """
        Initialize the two-phase orchestrator.

        Args:
            plan_maestro_data: Optional benchmark data for regional calculations.
                              If not provided, default conservative estimates are used.
        """
        self.plan_maestro_data = plan_maestro_data or {}
        self.scenario_calculator = ScenarioCalculator()
        self.cross_validator = CrossValidator()

    def phase_1_hook(self, hotel_url: str, hotel_name: str = None, region: str = "default") -> Phase1Result:
        """
        Execute Phase 1: Generate hook message with estimated loss range.

        Uses regional benchmarks to calculate a conservative-to-optimistic range
        of potential monthly losses due to OTA commissions and poor IA visibility.

        Args:
            hotel_url: URL of the hotel website (primary input for Phase 1)
            hotel_name: Optional hotel name (extracted from URL if not provided)
            region: Geographic region for benchmark data (default: "default")

        Returns:
            Phase1Result containing hook message, loss range, and next step instructions
        """
        # Extract hotel name from URL if not provided
        if not hotel_name:
            hotel_name = self._extract_name_from_url(hotel_url)

        # Calculate hook range based on regional benchmarks
        loss_min, loss_max = self._calculate_hook_range(region)

        # Format the hook message
        hook_message = self._format_hook_message(hotel_name, loss_min, loss_max)

        # Format disclaimer
        disclaimer = (
            "Esta estimacion inicial se basa en benchmarks regionales promedio. "
            "Para obtener un calculo preciso personalizado para su hotel, "
            "necesitamos algunos datos adicionales. Su informacion se mantiene "
            "confidencial y se utiliza unicamente para generar el analisis."
        )

        return Phase1Result(
            hotel_name=hotel_name,
            hotel_url=hotel_url,
            region=region,
            hook_message=hook_message,
            loss_range_min=loss_min,
            loss_range_max=loss_max,
            next_step="complete_phase_2",
            confidence_level="low",
            disclaimer=disclaimer,
            requires_user_input=True
        )

    def _extract_name_from_url(self, url: str) -> str:
        """Extract a readable hotel name from a URL."""
        # Remove protocol and www
        clean = url.replace("https://", "").replace("http://", "").replace("www.", "")
        # Remove TLD and path
        clean = clean.split("/")[0].split(".")[0]
        # Capitalize and replace hyphens/underscores with spaces
        clean = clean.replace("-", " ").replace("_", " ").title()
        return clean or "Su Hotel"

    def _calculate_hook_range(self, region: str) -> tuple:
        """
        Calculate the hook loss range for a given region.

        Uses regional benchmarks from plan maestro data to establish
        conservative (minimum) and optimistic (maximum) loss estimates.

        Args:
            region: Geographic region code

        Returns:
            Tuple of (min_loss, max_loss) in COP
        """
        # Get regional benchmarks
        benchmarks = self._get_regional_benchmarks(region)

        # Conservative estimate: smaller hotels, lower ADR, minimal impact
        conservative_rooms = benchmarks.get("min_rooms", 15)
        conservative_adr = benchmarks.get("min_adr", 120000)
        conservative_occupancy = benchmarks.get("min_occupancy", 0.40)

        # Optimistic estimate: larger hotels, higher ADR, significant impact
        optimistic_rooms = benchmarks.get("max_rooms", 50)
        optimistic_adr = benchmarks.get("max_adr", 450000)
        optimistic_occupancy = benchmarks.get("max_occupancy", 0.75)

        # Calculate conservative monthly loss (minimum)
        min_loss = self._estimate_monthly_loss(
            conservative_rooms, conservative_adr, conservative_occupancy
        )

        # Calculate optimistic monthly loss (maximum)
        max_loss = self._estimate_monthly_loss(
            optimistic_rooms, optimistic_adr, optimistic_occupancy
        )

        return (min_loss, max_loss)

    def _get_regional_benchmarks(self, region: str) -> Dict[str, float]:
        """Get benchmark data for a specific region."""
        default_benchmarks = {
            "min_rooms": 15,
            "max_rooms": 50,
            "min_adr": 120000,
            "max_adr": 450000,
            "min_occupancy": 0.40,
            "max_occupancy": 0.75,
        }

        if not self.plan_maestro_data:
            return default_benchmarks

        regions = self.plan_maestro_data.get("regions", {})
        return regions.get(region, default_benchmarks)

    def _estimate_monthly_loss(self, rooms: int, adr: float, occupancy: float) -> float:
        """
        Estimate monthly loss based on hotel characteristics.

        Uses simplified assumptions:
        - 30 days in month
        - 70% of bookings through OTAs (typical for hotels without direct channel focus)
        - 15% average OTA commission
        - 20% potential shift to direct with proper IA visibility
        """
        days_in_month = 30
        room_nights = rooms * days_in_month * occupancy
        ota_bookings = room_nights * 0.70  # 70% through OTAs
        commission_loss = ota_bookings * adr * 0.15  # 15% commission
        potential_savings = commission_loss * 0.20  # 20% can shift to direct
        return round(potential_savings, 2)

    def _format_hook_message(self, hotel_name: str, loss_min: float, loss_max: float) -> str:
        """Format the hook message with proper Colombian number notation."""
        min_formatted = f"{loss_min:,.0f}".replace(",", ".")
        max_formatted = f"{loss_max:,.0f}".replace(",", ".")

        return (
            f"{hotel_name} podria estar perdiendo entre **${min_formatted} y ${max_formatted} COP "
            f"mensuales** en comisiones de OTAs y reservas no capturadas por baja visibilidad "
            f"en Inteligencia Artificial."
        )

    def phase_2_input(
        self,
        phase_1_result: Phase1Result,
        user_inputs: HotelInputs,
        scraped_data: Dict = None,
        gbp_data: Dict = None
    ) -> Phase2Result:
        """
        Execute Phase 2: Validate inputs and calculate scenarios.

        Takes the Phase 1 result and user-provided inputs, validates them
        against scraped data and GBP API data, and calculates precise
        financial scenarios.

        Args:
            phase_1_result: Result from Phase 1 containing hotel URL and basic info
            user_inputs: User-provided hotel data via form inputs
            scraped_data: Optional data scraped from hotel website
            gbp_data: Optional data from Google Business Profile API

        Returns:
            Phase2Result containing validated data, confidence scores, and scenarios
        """
        scraped_data = scraped_data or {}
        gbp_data = gbp_data or {}

        # Validate all inputs using CrossValidator
        validated_fields = self._validate_all_inputs(user_inputs, scraped_data, gbp_data)

        # Check for conflicts
        conflicts = self.cross_validator.get_conflict_report()
        has_conflicts = len(conflicts) > 0
        conflicts_report = [c.get("field_name", "unknown") for c in conflicts]

        # Extract confidence scores
        confidence_scores = {}
        for field_name, field_data in validated_fields.items():
            if isinstance(field_data, dict):
                # Get match percentage or default to 0
                score = field_data.get("match_percentage", 0.0)
                confidence_scores[field_name] = score

        # Determine if we can proceed (need at least rooms and ADR)
        can_proceed = (
            user_inputs.rooms is not None and
            user_inputs.adr_cop is not None and
            not has_conflicts
        )

        scenarios = None
        hotel_data = None

        if can_proceed:
            # Create HotelFinancialData from validated inputs
            hotel_data = HotelFinancialData(
                rooms=user_inputs.rooms,
                adr_cop=user_inputs.adr_cop,
                occupancy_rate=user_inputs.occupancy_rate or 0.50,
                ota_commission_rate=0.15,
                direct_channel_percentage=user_inputs.direct_channel_percentage or 0.0,
                ota_presence=user_inputs.ota_presence or ["booking", "expedia"]
            )

            # Calculate scenarios
            calculated_scenarios = self.scenario_calculator.calculate_scenarios(hotel_data)

            # Convert to serializable dict
            scenarios = {}
            for scenario_type, scenario in calculated_scenarios.items():
                scenarios[scenario_type.value] = {
                    "monthly_loss_cop": scenario.monthly_loss_cop,
                    "probability": scenario.probability,
                    "calculation_basis": scenario.calculation_basis,
                    "confidence_score": scenario.confidence_score,
                    "assumptions": scenario.assumptions,
                    "disclaimer": scenario.disclaimer,
                }

        return Phase2Result(
            hotel_data=hotel_data,
            validated_fields=validated_fields,
            confidence_scores=confidence_scores,
            has_conflicts=has_conflicts,
            conflicts_report=conflicts_report,
            can_proceed=can_proceed,
            scenarios=scenarios
        )

    def _validate_all_inputs(
        self,
        user_inputs: HotelInputs,
        scraped_data: Dict,
        gbp_data: Dict
    ) -> Dict[str, Any]:
        """
        Validate all hotel inputs across multiple sources.

        Cross-validates user inputs with scraped data and GBP API data
        to ensure accuracy and detect conflicts.

        Args:
            user_inputs: User-provided hotel data
            scraped_data: Data scraped from hotel website
            gbp_data: Data from Google Business Profile API

        Returns:
            Dictionary of validated fields with confidence information
        """
        validated = {}

        # Validate WhatsApp across sources
        whatsapp_dp = self.cross_validator.validate_whatsapp(
            web_value=scraped_data.get("whatsapp"),
            gbp_value=gbp_data.get("phone"),
            user_value=user_inputs.whatsapp_number
        )
        if whatsapp_dp:
            validated["whatsapp"] = whatsapp_dp.to_dict()

        # Validate ADR across sources (scraped price vs user input vs benchmark)
        benchmark_adr = self._get_regional_adr_benchmark()
        adr_dp = self.cross_validator.validate_adr(
            scraped_price=scraped_data.get("price"),
            user_input=user_inputs.adr_cop,
            benchmark_region=benchmark_adr
        )
        if adr_dp:
            validated["adr"] = adr_dp.to_dict()

        # Validate rooms (user input only, no external source typically)
        if user_inputs.rooms is not None:
            self.cross_validator.add_user_input("rooms", user_inputs.rooms)
            rooms_dp = self.cross_validator.get_validated_field("rooms")
            if rooms_dp:
                validated["rooms"] = rooms_dp.to_dict()

        # Validate occupancy rate (user input)
        if user_inputs.occupancy_rate is not None:
            self.cross_validator.add_user_input(
                "occupancy_rate", user_inputs.occupancy_rate
            )
            occ_dp = self.cross_validator.get_validated_field("occupancy_rate")
            if occ_dp:
                validated["occupancy_rate"] = occ_dp.to_dict()

        # Validate direct channel percentage (user input)
        if user_inputs.direct_channel_percentage is not None:
            self.cross_validator.add_user_input(
                "direct_channel_percentage", user_inputs.direct_channel_percentage
            )
            dcp_dp = self.cross_validator.get_validated_field("direct_channel_percentage")
            if dcp_dp:
                validated["direct_channel_percentage"] = dcp_dp.to_dict()

        return validated

    def _get_regional_adr_benchmark(self) -> Optional[float]:
        """Get average ADR benchmark for default region."""
        if not self.plan_maestro_data:
            return None

        regions = self.plan_maestro_data.get("regions", {})
        default_region = regions.get("default", {})
        avg_adr = default_region.get("avg_adr")

        return avg_adr

    def get_phase_1_form(self) -> Dict[str, Any]:
        """
        Get the form schema for Phase 1 (Hook).

        Phase 1 only requires the hotel URL to generate the initial hook.

        Returns:
            Dictionary containing form field definitions for Phase 1
        """
        return {
            "form_id": "phase_1_hook",
            "title": "Descubra cuanto esta perdiendo su hotel",
            "description": "Ingrese la URL de su hotel para recibir una estimacion inicial.",
            "fields": [
                {
                    "name": "hotel_url",
                    "type": "url",
                    "label": "URL del Hotel",
                    "placeholder": "https://www.suhotel.com",
                    "required": True,
                    "validation": {
                        "pattern": "https?://.+\\..+",
                        "message": "Por favor ingrese una URL valida (ej: https://www.suhotel.com)"
                    },
                    "help_text": "La direccion web de su hotel (la pagina principal)"
                }
            ],
            "submit_label": "Descubrir mi perdida estimada",
            "privacy_note": "Solo usamos su URL para analisis. No almacenamos datos personales."
        }

    def get_phase_2_form(self) -> Dict[str, Any]:
        """
        Get the form schema for Phase 2 (Input).

        Phase 2 collects detailed hotel data needed for precise calculations.

        Returns:
            Dictionary containing form field definitions for Phase 2
        """
        return {
            "form_id": "phase_2_input",
            "title": "Complete los datos de su hotel",
            "description": (
                "Estos datos nos permiten calcular con precision su perdida mensual "
                "y generar recomendaciones personalizadas."
            ),
            "fields": [
                {
                    "name": "rooms",
                    "type": "number",
                    "label": "Numero de habitaciones",
                    "placeholder": "25",
                    "required": True,
                    "validation": {
                        "min": 1,
                        "max": 500,
                        "integer": True,
                        "message": "Ingrese un numero valido de habitaciones (1-500)"
                    },
                    "help_text": "Cantidad total de habitaciones disponibles en su hotel"
                },
                {
                    "name": "adr_cop",
                    "type": "currency",
                    "label": "Tarifa Promedio Diaria (ADR)",
                    "placeholder": "250000",
                    "required": True,
                    "currency": "COP",
                    "validation": {
                        "min": 50000,
                        "max": 2000000,
                        "message": "Ingrese un valor entre $50.000 y $2.000.000 COP"
                    },
                    "help_text": "Precio promedio por noche de sus habitaciones en pesos colombianos"
                },
                {
                    "name": "occupancy_rate",
                    "type": "percentage",
                    "label": "Ocupacion promedio",
                    "placeholder": "65",
                    "required": True,
                    "validation": {
                        "min": 0,
                        "max": 100,
                        "message": "Ingrese un porcentaje entre 0% y 100%"
                    },
                    "help_text": "Porcentaje promedio de habitaciones ocupadas mensualmente"
                },
                {
                    "name": "ota_presence",
                    "type": "multiselect",
                    "label": "OTAs donde aparece su hotel",
                    "required": False,
                    "options": [
                        {"value": "booking", "label": "Booking.com"},
                        {"value": "expedia", "label": "Expedia"},
                        {"value": "hotels", "label": "Hotels.com"},
                        {"value": "airbnb", "label": "Airbnb"},
                        {"value": "despegar", "label": "Despegar"},
                        {"value": "trivago", "label": "Trivago"},
                        {"value": "tripadvisor", "label": "TripAdvisor"},
                        {"value": "otros", "label": "Otros"}
                    ],
                    "help_text": "Seleccione todos los sitios de reserva donde esta presente su hotel"
                },
                {
                    "name": "direct_channel_percentage",
                    "type": "percentage",
                    "label": "Reservas directas (%)",
                    "placeholder": "20",
                    "required": False,
                    "validation": {
                        "min": 0,
                        "max": 100,
                        "message": "Ingrese un porcentaje entre 0% y 100%"
                    },
                    "help_text": (
                        "Porcentaje de reservas que llegan directamente "
                        "(sin pasar por OTAs) via web, telefono o walk-in"
                    )
                },
                {
                    "name": "whatsapp_number",
                    "type": "tel",
                    "label": "Numero de WhatsApp",
                    "placeholder": "+57 300 123 4567",
                    "required": False,
                    "validation": {
                        "pattern": "^(\\+?57)?[\\s\\-]?[0-9]{10}$",
                        "message": "Ingrese un numero valido de Colombia (10 digitos)"
                    },
                    "help_text": (
                        "Numero de WhatsApp para contacto directo con huespedes "
                        "(se validara contra su web y Google Business)"
                    )
                }
            ],
            "submit_label": "Calcular mi analisis personalizado",
            "privacy_note": (
                "Sus datos se mantienen confidenciales y solo se usan para "
                "generar el analisis financiero. No compartimos informacion con terceros."
            ),
            "disclaimer": (
                "Los calculos se basan en los datos proporcionados y benchmarks "
                "de la industria hotelera. Los resultados son estimaciones orientativas."
            )
        }

    @staticmethod
    def format_hook_for_display(result: Phase1Result) -> str:
        """
        Format a Phase1Result as readable markdown for display.

        Creates a formatted markdown string suitable for displaying in
        web interfaces, reports, or chat messages.

        Args:
            result: The Phase1Result to format

        Returns:
            Formatted markdown string with hook message and CTA
        """
        min_formatted = f"{result.loss_range_min:,.0f}".replace(",", ".")
        max_formatted = f"{result.loss_range_max:,.0f}".replace(",", ".")

        markdown = f"""## {result.hotel_name}

{result.hook_message}

---

### Rango estimado de perdida mensual

- **Minimo (conservador)**: ${min_formatted} COP
- **Maximo (optimista)**: ${max_formatted} COP

---

### {result.disclaimer}

**Siguiente paso**: {result.next_step}

Para obtener un calculo preciso personalizado para su hotel, complete el formulario con los datos de sus habitaciones, tarifas y ocupacion.

---

*Esta estimacion se basa en benchmarks regionales y puede variar segun las caracteristicas especificas de su establecimiento.*
"""
        return markdown
