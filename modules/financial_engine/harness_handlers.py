"""Financial Engine Handlers for Agent Harness.

This module provides handler functions that integrate the financial engine
with the Agent Harness, enabling scenario calculations and regional ADR resolution
through the harness task execution system.
"""

from typing import Any, Dict, Optional
from agent_harness.types import TaskContext


def financial_calculation_handler(payload: Dict[str, Any], context: TaskContext) -> Dict[str, Any]:
    """Execute complete financial calculations including ADR resolution and pricing.

    This handler performs:
    1. ADR resolution with shadow mode support
    2. Pricing calculation with shadow mode support
    3. Scenario generation for conservative, realistic, and optimistic cases

    Args:
        payload: Dictionary containing:
            - rooms (int): Number of hotel rooms (default: 10)
            - region (str): Hotel region code (default: "default")
            - user_provided_adr (float, optional): User-provided ADR in COP
            - segment (str, optional): Hotel segment (boutique/standard/large)
            - hotel_id (str, optional): Hotel identifier for logging
            - hotel_name (str, optional): Hotel name for logging
            - expected_loss_cop (float, optional): Expected monthly loss in COP
        context: TaskContext with execution history and suggestions

    Returns:
        Dictionary with:
            - adr_resolution: ADR resolution results
            - pricing: Pricing calculation results
            - scenarios: Generated financial scenarios
            - success: Boolean indicating overall success
    """
    from modules.financial_engine import (
        resolve_adr_with_shadow,
        calculate_price_with_shadow,
        ScenarioCalculator,
        HotelFinancialData,
    )

    try:
        # Extract parameters from payload with defaults
        rooms = payload.get("rooms", 10)
        region = payload.get("region", "default")
        user_provided_adr = payload.get("user_provided_adr")
        segment = payload.get("segment")
        hotel_id = payload.get("hotel_id")
        hotel_name = payload.get("hotel_name")
        expected_loss_cop = payload.get("expected_loss_cop")

        # Validate minimum required parameters
        if rooms <= 0:
            return {
                "success": False,
                "error": "Invalid rooms count",
                "error_type": "ValidationError",
                "message": "Rooms must be a positive integer",
            }

        # Step 1: Resolve ADR with shadow mode
        adr_result = resolve_adr_with_shadow(
            region=region,
            rooms=rooms,
            user_provided_adr=user_provided_adr,
            hotel_id=hotel_id,
            hotel_name=hotel_name,
        )

        # Step 2: Calculate expected loss if not provided
        # Use ADR-based estimation: ADR * rooms * 0.7 (realistic occupancy)
        if expected_loss_cop is None:
            expected_loss_cop = adr_result.adr_cop * rooms * 0.7

        # Step 3: Calculate pricing with shadow mode
        pricing_result = calculate_price_with_shadow(
            rooms=rooms,
            expected_loss_cop=expected_loss_cop,
            segment=segment,
            hotel_id=hotel_id,
            hotel_name=hotel_name,
        )

        # Extract occupancy and channel data from payload
        occupancy_rate = payload.get("occupancy_rate", 0.50)
        direct_channel_percentage = payload.get("direct_channel_percentage", 0.20)

        # Step 4: Generate financial scenarios
        calculator = ScenarioCalculator()
        hotel_data = HotelFinancialData(
            rooms=rooms,
            adr_cop=adr_result.adr_cop,
            occupancy_rate=occupancy_rate,
            direct_channel_percentage=direct_channel_percentage,
        )
        scenarios = calculator.calculate_scenarios(hotel_data)

        # Access scenarios using ScenarioType enum keys
        from modules.financial_engine.scenario_calculator import ScenarioType
        conservative = scenarios[ScenarioType.CONSERVATIVE]
        realistic = scenarios[ScenarioType.REALISTIC]
        optimistic = scenarios[ScenarioType.OPTIMISTIC]

        # Build comprehensive result
        return {
            "success": True,
            "adr_cop": adr_result.adr_cop,
            "adr_resolution": {
                "adr_cop": adr_result.adr_cop,
                "source": adr_result.source,
                "confidence": adr_result.confidence,
                "used_new_calculation": adr_result.used_new_calculation,
                "region": region,
                "segment": segment,
                "metadata": adr_result.metadata,
            },
            "pricing": {
                "monthly_price_cop": pricing_result.monthly_price_cop,
                "tier": pricing_result.tier,
                "pain_ratio": pricing_result.pain_ratio,
                "is_compliant": pricing_result.is_compliant,
                "expected_loss_cop": pricing_result.expected_loss_cop,
                "source": pricing_result.source,
                "used_new_calculation": pricing_result.used_new_calculation,
                "metadata": pricing_result.metadata,
            },
            "scenarios": {
                "conservative": {
                    "monthly_loss_cop": conservative.monthly_loss_cop,
                    "annual_loss_cop": conservative.monthly_loss_cop * 12,
                    "occupancy_rate": occupancy_rate,
                    "probability": conservative.probability,
                },
                "realistic": {
                    "monthly_loss_cop": realistic.monthly_loss_cop,
                    "annual_loss_cop": realistic.monthly_loss_cop * 12,
                    "occupancy_rate": occupancy_rate,
                    "probability": realistic.probability,
                },
                "optimistic": {
                    "monthly_loss_cop": optimistic.monthly_loss_cop,
                    "annual_loss_cop": optimistic.monthly_loss_cop * 12,
                    "occupancy_rate": occupancy_rate,
                    "probability": optimistic.probability,
                },
                },
                "expected_monthly": realistic.monthly_loss_cop,
                "summary": {
                "rooms": rooms,
                "region": region,
                "hotel_id": hotel_id,
                "hotel_name": hotel_name,
                "total_annual_potential_cop": optimistic.monthly_loss_cop * 12,
            },
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "message": "Financial calculation failed",
            "adr_resolution": None,
            "pricing": None,
            "scenarios": None,
        }


def regional_resolver_handler(payload: Dict[str, Any], context: TaskContext) -> Dict[str, Any]:
    """Resolve ADR (Average Daily Rate) for a specific region and hotel size.

    This handler uses the RegionalADRResolver to determine the appropriate
    ADR based on regional benchmarks and hotel segment.

    Args:
        payload: Dictionary containing:
            - region (str): Hotel region code (default: "default")
            - rooms (int): Number of hotel rooms (default: 10)
            - user_provided_adr (float, optional): User-provided ADR for validation
            - plan_maestro_path (str, optional): Path to plan maestro data file
        context: TaskContext with execution history and suggestions

    Returns:
        Dictionary with:
            - adr_cop: Resolved ADR in COP
            - region: Region code used
            - segment: Hotel segment (boutique/standard/large)
            - confidence: Confidence level (VERIFIED/ESTIMATED/CONFLICT)
            - source: Data source used
            - is_default: Whether default values were used
            - metadata: Additional resolution metadata
            - success: Boolean indicating success
    """
    from modules.financial_engine import resolve_regional_adr, RegionalADRResolver

    try:
        # Extract parameters from payload with defaults
        region = payload.get("region", "default")
        rooms = payload.get("rooms", 10)
        user_provided_adr = payload.get("user_provided_adr")
        plan_maestro_path = payload.get("plan_maestro_path")

        # Validate parameters
        if rooms <= 0:
            return {
                "success": False,
                "error": "Invalid rooms count",
                "error_type": "ValidationError",
                "message": "Rooms must be a positive integer",
                "adr_cop": None,
            }

        # Resolve regional ADR
        result = resolve_regional_adr(
            region=region,
            rooms=rooms,
            user_provided_adr=user_provided_adr,
            plan_maestro_path=plan_maestro_path,
        )

        # Build result dictionary
        return {
            "success": True,
            "adr_cop": result.adr_cop,
            "region": result.region,
            "segment": result.segment,
            "confidence": result.confidence,
            "source": result.source,
            "is_default": result.is_default,
            "metadata": result.metadata,
            "validation": {
                "user_provided_adr": user_provided_adr,
                "deviation_pct": result.metadata.get("deviation_pct") if result.metadata else None,
                "matches_benchmark": result.confidence == "VERIFIED",
            },
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "message": "Regional ADR resolution failed",
            "adr_cop": None,
            "region": payload.get("region", "default"),
            "segment": None,
            "confidence": None,
        }


def register_financial_handlers(harness) -> None:
    """Register financial engine handlers with the Agent Harness.

    This function registers both handlers:
    - v4_financial_calculation: Complete financial scenario calculations
    - v4_regional_resolver: Regional ADR resolution

    Args:
        harness: AgentHarness instance to register handlers with

    Example:
        >>> from agent_harness.core import AgentHarness
        >>> from modules.financial_engine.harness_handlers import register_financial_handlers
        >>> harness = AgentHarness()
        >>> register_financial_handlers(harness)
    """
    harness.register_handler("v4_financial_calculation", financial_calculation_handler)
    harness.register_handler("v4_regional_resolver", regional_resolver_handler)
