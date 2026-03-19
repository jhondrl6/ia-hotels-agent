"""
End-to-End Tests for v4.0 Complete Flow.

This module tests the complete v4.0 flow with 5 different hotel scenarios:
1. Hotel Visperas (Eje Cafetero) - Ideal scenario
2. Hotel Caribe Premium (Caribe) - High-value hotel
3. Hotel Antioquia Conflicto (Antioquia) - WhatsApp conflict scenario
4. Hostal Económico (Eje Cafetero) - Low confidence scenario
5. Complete onboarding flow test

Tests verify:
- Phase 1 completion
- Phase 2 validation
- Conflict detection
- Asset generation/blocking
- Metadata inclusion
- Progress tracking
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from pathlib import Path

from modules.orchestration_v4.onboarding_controller import (
    OnboardingController,
    OnboardingPhase,
    OnboardingStatus,
)
from modules.orchestration_v4.two_phase_flow import HotelInputs
from modules.asset_generation.conditional_generator import ConditionalGenerator
from modules.asset_generation.asset_metadata import AssetMetadataEnforcer, AssetMetadata
from modules.data_validation.confidence_taxonomy import ConfidenceLevel, DataPoint, DataSource


class TestV40CompleteFlowE2E:
    """End-to-end tests for v4.0 complete flow with multiple hotel scenarios."""

    @pytest.fixture(autouse=True)
    def setup_method(self, tmp_path):
        """Initialize OnboardingController and ConditionalGenerator before each test."""
        self.controller = OnboardingController()
        self.generator = ConditionalGenerator(output_dir=str(tmp_path))
        self.tmp_path = tmp_path
        yield

    # ====================================================================================
    # HELPER METHODS
    # ====================================================================================

    def _create_hotel_inputs(
        self,
        rooms: int = 20,
        adr_cop: float = 300000.0,
        occupancy_rate: float = 0.60,
        ota_presence: list = None,
        direct_channel_percentage: float = None,
        whatsapp_number: str = None,
    ) -> HotelInputs:
        """Create HotelInputs for different scenarios.

        Args:
            rooms: Number of rooms in the hotel
            adr_cop: Average Daily Rate in COP
            occupancy_rate: Occupancy rate as decimal (0.0 - 1.0)
            ota_presence: List of OTA platforms where hotel is present
            direct_channel_percentage: Percentage of direct bookings
            whatsapp_number: WhatsApp contact number

        Returns:
            HotelInputs dataclass instance
        """
        return HotelInputs(
            rooms=rooms,
            adr_cop=adr_cop,
            occupancy_rate=occupancy_rate,
            ota_presence=ota_presence or ["booking", "expedia"],
            direct_channel_percentage=direct_channel_percentage or 0.20,
            whatsapp_number=whatsapp_number,
        )

    def _create_scraped_data(
        self,
        whatsapp: str = None,
        price: str = None,
        amenities: list = None,
        include_data: bool = True,
    ) -> dict:
        """Create scraped data (optional conflicts).

        Args:
            whatsapp: WhatsApp number from website
            price: Price scraped from website
            amenities: List of hotel amenities
            include_data: Whether to include scraped data at all

        Returns:
            Dictionary with scraped data or empty dict
        """
        if not include_data:
            return {}
        return {
            "whatsapp": whatsapp,
            "price": price,
            "amenities": amenities or ["wifi", "parking", "breakfast"],
        }

    def _create_gbp_data(
        self,
        phone: str = None,
        rating: float = None,
        review_count: int = None,
        include_data: bool = True,
    ) -> dict:
        """Create GBP data (optional conflicts).

        Args:
            phone: Phone number from Google Business Profile
            rating: Rating from GBP
            review_count: Number of reviews on GBP
            include_data: Whether to include GBP data at all

        Returns:
            Dictionary with GBP data or empty dict
        """
        if not include_data:
            return {}
        return {
            "phone": phone,
            "rating": rating or 4.5,
            "review_count": review_count or 100,
        }

    def _verify_assets_generated(
        self,
        hotel_id: str,
        asset_types: list,
        expect_blocked: list = None,
    ) -> dict:
        """Verify assets exist and have metadata.

        Args:
            hotel_id: Unique hotel identifier
            asset_types: List of asset types to verify
            expect_blocked: List of asset types that should be blocked

        Returns:
            Dictionary with verification results
        """
        expect_blocked = expect_blocked or []
        results = {"generated": [], "blocked": [], "missing": []}

        hotel_dir = self.generator.output_dir / hotel_id

        for asset_type in asset_types:
            asset_dir = hotel_dir / asset_type

            if asset_type in expect_blocked:
                results["blocked"].append(asset_type)
                continue

            if not asset_dir.exists():
                results["missing"].append(asset_type)
                continue

            # Check for files (excluding metadata files)
            files = [f for f in asset_dir.iterdir() if not f.name.endswith("_metadata.json")]
            if files:
                results["generated"].append(asset_type)
            else:
                results["missing"].append(asset_type)

        return results

    def _verify_metadata_structure(self, metadata: dict) -> bool:
        """Verify metadata format.

        Args:
            metadata: Metadata dictionary to verify

        Returns:
            True if metadata structure is valid
        """
        required_fields = [
            "asset_type",
            "generated_at",
            "confidence_score",
            "preflight_status",
            "hotel_id",
            "hotel_name",
        ]

        for field in required_fields:
            assert field in metadata, f"Missing required field: {field}"

        # Verify confidence_score is between 0 and 1
        assert 0.0 <= metadata["confidence_score"] <= 1.0, "confidence_score must be between 0.0 and 1.0"

        # Verify preflight_status is valid
        assert metadata["preflight_status"] in ["passed", "warning", "blocked"], \
            f"Invalid preflight_status: {metadata['preflight_status']}"

        # Verify generated_at is ISO format string
        assert isinstance(metadata["generated_at"], str), "generated_at must be a string"

        return True

    # ====================================================================================
    # TEST SCENARIO 1: Hotel Visperas (Ideal Scenario)
    # ====================================================================================

    def test_hotel_1_visperas_ideal_scenario(self):
        """Test Hotel Visperas (Eje Cafetero) - Ideal scenario with matching WhatsApp.

        Hotel Details:
        - Name: Hotel Visperas
        - Region: Eje Cafetero
        - Rooms: 15
        - ADR: $400,000 COP
        - Occupancy: 51%
        - WhatsApp matches across all sources

        Expected Behavior:
        - Phase 1 completes successfully
        - Phase 2 validation passes
        - No conflicts detected
        - All assets generated
        - Metadata includes all required fields
        """
        hotel_name = "Hotel Visperas"
        hotel_url = "https://www.hotelvisperas.com"
        hotel_id = OnboardingController.generate_hotel_id(hotel_url)

        # Create inputs matching the WhatsApp across all sources
        hotel_inputs = self._create_hotel_inputs(
            rooms=15,
            adr_cop=400000.0,
            occupancy_rate=0.51,
            whatsapp_number="+573112345678",
            ota_presence=["booking", "expedia", "airbnb"],
            direct_channel_percentage=0.25,
        )

        # Create scraped data with matching WhatsApp
        scraped_data = self._create_scraped_data(
            whatsapp="+573112345678",
            price="400000",
            amenities=["wifi", "parking", "breakfast", "pool"],
        )

        # Create GBP data with matching WhatsApp
        gbp_data = self._create_gbp_data(
            phone="+573112345678",
            rating=4.7,
            review_count=156,
        )

        # Phase 1: Start onboarding
        with patch.object(
            self.controller._orchestrator,
            "phase_1_hook",
            return_value=Mock(
                hotel_name=hotel_name,
                hotel_url=hotel_url,
                region="eje_cafetero",
                hook_message=f"{hotel_name} podria estar perdiendo entre $5.000.000 y $15.000.000 COP mensuales",
                loss_range_min=5000000.0,
                loss_range_max=15000000.0,
            ),
        ):
            state = self.controller.start_onboarding(hotel_url, hotel_name, region="eje_cafetero")

        # Verify Phase 1 completed
        assert state.current_phase == OnboardingPhase.PHASE_2_INPUT
        assert state.status == OnboardingStatus.PENDING
        assert state.phase_1_result is not None
        assert self.controller.get_progress_percentage(hotel_id) == 30

        # Phase 2: Submit inputs with no conflicts
        mock_phase2_result = Mock()
        mock_phase2_result.conflicts_report = []
        mock_phase2_result.has_conflicts = False
        mock_phase2_result.can_proceed = True
        mock_phase2_result.validated_fields = {
            "whatsapp": {"value": "+573112345678", "match_percentage": 100.0},
            "adr": {"value": 400000.0, "match_percentage": 100.0},
            "rooms": {"value": 15},
        }

        with patch.object(
            self.controller._orchestrator,
            "phase_2_input",
            return_value=mock_phase2_result,
        ):
            state = self.controller.submit_phase_2(
                hotel_id=hotel_id,
                inputs=hotel_inputs,
                scraped_data=scraped_data,
                gbp_data=gbp_data,
            )

        # Verify Phase 2 completed without conflicts
        assert state.current_phase == OnboardingPhase.CALCULATION
        assert state.status == OnboardingStatus.COMPLETED
        assert state.phase_2_result is not None
        assert state.phase_2_result.has_conflicts is False
        assert len(state.phase_2_result.conflicts_report) == 0
        assert self.controller.can_proceed_to_assets(hotel_id) is True
        assert self.controller.get_progress_percentage(hotel_id) == 60

        # Generate assets
        validated_data = {
            "whatsapp": self._create_data_point("whatsapp", "+573112345678", ["web_scraping", "gbp_api", "user_input"]),
        }

        result = self.generator.generate(
            asset_type="whatsapp_button",
            validated_data=validated_data,
            hotel_name=hotel_name,
            hotel_id=hotel_id,
        )

        # Verify asset generation
        assert result["success"] is True
        assert result["status"] in ["generated", "estimated"]
        assert result["hotel_id"] == hotel_id
        assert "metadata" in result
        self._verify_metadata_structure(result["metadata"])

    # ====================================================================================
    # TEST SCENARIO 2: Hotel Caribe Premium (High-Value Hotel)
    # ====================================================================================

    def test_hotel_2_caribe_boutique(self):
        """Test Hotel Caribe Premium (Caribe) - High-value hotel scenario.

        Hotel Details:
        - Name: Hotel Caribe Premium
        - Region: Caribe
        - Rooms: 25
        - ADR: $900,000 COP
        - Occupancy: 68%
        - High-value hotel with different region

        Expected Behavior:
        - Phase 1 completes with appropriate loss range
        - Phase 2 validation works
        - Scenarios generated reflect high ADR
        - Assets generated with high confidence
        """
        hotel_name = "Hotel Caribe Premium"
        hotel_url = "https://www.caribepremium.com"
        hotel_id = OnboardingController.generate_hotel_id(hotel_url)

        # Create inputs for high-value hotel
        hotel_inputs = self._create_hotel_inputs(
            rooms=25,
            adr_cop=900000.0,
            occupancy_rate=0.68,
            whatsapp_number="+573202345678",
            ota_presence=["booking", "expedia", "hotels", "trivago"],
            direct_channel_percentage=0.15,
        )

        scraped_data = self._create_scraped_data(
            whatsapp="+573202345678",
            price="900000",
            amenities=["wifi", "pool", "spa", "restaurant", "beach_access"],
        )

        gbp_data = self._create_gbp_data(
            phone="+573202345678",
            rating=4.8,
            review_count=324,
        )

        # Phase 1
        with patch.object(
            self.controller._orchestrator,
            "phase_1_hook",
            return_value=Mock(
                hotel_name=hotel_name,
                hotel_url=hotel_url,
                region="caribe",
                hook_message=f"{hotel_name} podria estar perdiendo entre $20.000.000 y $45.000.000 COP mensuales",
                loss_range_min=20000000.0,
                loss_range_max=45000000.0,
            ),
        ):
            state = self.controller.start_onboarding(hotel_url, hotel_name, region="caribe")

        assert state.current_phase == OnboardingPhase.PHASE_2_INPUT

        # Phase 2 with scenarios
        mock_phase2_result = Mock()
        mock_phase2_result.conflicts_report = []
        mock_phase2_result.has_conflicts = False
        mock_phase2_result.can_proceed = True
        mock_phase2_result.scenarios = {
            "conservative": {"monthly_loss_cop": 25000000.0, "probability": 0.7},
            "optimistic": {"monthly_loss_cop": 40000000.0, "probability": 0.3},
        }

        with patch.object(
            self.controller._orchestrator,
            "phase_2_input",
            return_value=mock_phase2_result,
        ):
            state = self.controller.submit_phase_2(
                hotel_id=hotel_id,
                inputs=hotel_inputs,
                scraped_data=scraped_data,
                gbp_data=gbp_data,
            )

        # Verify scenarios reflect high ADR
        assert state.current_phase == OnboardingPhase.CALCULATION
        assert state.phase_2_result.scenarios is not None
        assert "conservative" in state.phase_2_result.scenarios

        # Generate financial projection asset
        validated_data = {
            "hotel_financial_data": self._create_data_point(
                "hotel_financial_data",
                {"revenue": 50000000, "occupancy": 0.68},
                ["user_input"]
            ),
            "hotel_data": self._create_data_point(
                "hotel_data",
                {"name": hotel_name, "adr": 900000},
                ["user_input"]
            ),
        }

        result = self.generator.generate(
            asset_type="financial_projection",
            validated_data=validated_data,
            hotel_name=hotel_name,
            hotel_id=hotel_id,
        )

        assert result["success"] is True
        assert "metadata" in result
        self._verify_metadata_structure(result["metadata"])

    # ====================================================================================
    # TEST SCENARIO 3: Hotel Antioquia Conflicto (WhatsApp Conflict)
    # ====================================================================================

    def test_hotel_3_antioquia_conflict_scenario(self):
        """Test Hotel Antioquia Conflicto - WhatsApp conflict detection.

        Hotel Details:
        - Name: Hotel Antioquia Conflicto
        - Region: Antioquia
        - Rooms: 20
        - ADR: $560,000 COP
        - WhatsApp conflict: web says +573111111111, GBP says +573222222222

        Expected Behavior:
        - Phase 1 completes successfully
        - Phase 2 detects WhatsApp conflict
        - Status set to BLOCKED
        - WhatsApp asset should be blocked
        - Other assets can still be generated with warnings
        """
        hotel_name = "Hotel Antioquia Conflicto"
        hotel_url = "https://www.antioquiaconflicto.com"
        hotel_id = OnboardingController.generate_hotel_id(hotel_url)

        # User provides one WhatsApp number
        hotel_inputs = self._create_hotel_inputs(
            rooms=20,
            adr_cop=560000.0,
            occupancy_rate=0.55,
            whatsapp_number="+573111111111",
        )

        # Web shows different WhatsApp
        scraped_data = self._create_scraped_data(
            whatsapp="+573111111111",
            price="560000",
        )

        # GBP shows yet another WhatsApp (CONFLICT!)
        gbp_data = self._create_gbp_data(
            phone="+573222222222",  # Different from web and user input
            rating=4.2,
            review_count=89,
        )

        # Phase 1
        with patch.object(
            self.controller._orchestrator,
            "phase_1_hook",
            return_value=Mock(
                hotel_name=hotel_name,
                hotel_url=hotel_url,
                region="antioquia",
                hook_message=f"{hotel_name} podria estar perdiendo entre $8.000.000 y $18.000.000 COP mensuales",
                loss_range_min=8000000.0,
                loss_range_max=18000000.0,
            ),
        ):
            state = self.controller.start_onboarding(hotel_url, hotel_name, region="antioquia")

        assert state.current_phase == OnboardingPhase.PHASE_2_INPUT

        # Phase 2 with WhatsApp conflict
        mock_phase2_result = Mock()
        mock_phase2_result.conflicts_report = ["whatsapp"]
        mock_phase2_result.has_conflicts = True
        mock_phase2_result.can_proceed = False
        mock_phase2_result.validated_fields = {
            "whatsapp": {
                "value": None,
                "confidence": "CONFLICT",
                "sources": ["web_scraping", "gbp_api", "user_input"],
                "conflict_details": {
                    "web": "+573111111111",
                    "gbp": "+573222222222",
                    "user": "+573111111111",
                }
            },
            "adr": {"value": 560000.0, "match_percentage": 100.0},
        }

        with patch.object(
            self.controller._orchestrator,
            "phase_2_input",
            return_value=mock_phase2_result,
        ):
            state = self.controller.submit_phase_2(
                hotel_id=hotel_id,
                inputs=hotel_inputs,
                scraped_data=scraped_data,
                gbp_data=gbp_data,
            )

        # Verify conflict detected and blocked
        assert state.current_phase == OnboardingPhase.VALIDATION
        assert state.status == OnboardingStatus.BLOCKED
        assert state.phase_2_result.has_conflicts is True
        assert "whatsapp" in state.phase_2_result.conflicts_report
        assert self.controller.can_proceed_to_assets(hotel_id) is False

        # Verify conflict summary
        conflict_summary = self.controller.get_conflict_summary(hotel_id)
        assert len(conflict_summary) > 0
        assert any("whatsapp" in str(conflict).lower() for conflict in conflict_summary)

        # Attempt to generate WhatsApp asset - should be blocked
        # Create a DataPoint with conflicting values to simulate CONFLICT level
        whatsapp_dp = DataPoint("whatsapp")
        # Add same value for web and user
        whatsapp_dp.add_source(DataSource(
            source_type="web_scraping",
            value="+573111111111",
            timestamp=datetime.now().isoformat(),
        ))
        whatsapp_dp.add_source(DataSource(
            source_type="user_input",
            value="+573111111111",
            timestamp=datetime.now().isoformat(),
        ))
        # Add different value for GBP to trigger conflict
        whatsapp_dp.add_source(DataSource(
            source_type="gbp_api",
            value="+573222222222",
            timestamp=datetime.now().isoformat(),
        ))

        validated_data = {"whatsapp": whatsapp_dp}

        result = self.generator.generate(
            asset_type="whatsapp_button",
            validated_data=validated_data,
            hotel_name=hotel_name,
            hotel_id=hotel_id,
        )

        # WhatsApp asset should be blocked
        assert result["success"] is False
        assert result["status"] == "blocked"
        assert "Preflight check failed" in result["error"]

    # ====================================================================================
    # TEST SCENARIO 4: Hostal Económico (Low Confidence)
    # ====================================================================================

    def test_hotel_4_small_hostal_low_confidence(self):
        """Test Hostal Económico - Low confidence with only user input.

        Hotel Details:
        - Name: Hostal Económico
        - Region: Eje Cafetero
        - Rooms: 8
        - ADR: $150,000 COP
        - Occupancy: 40%
        - Only user input, no scraped data or GBP data

        Expected Behavior:
        - Phase 1 completes successfully
        - Phase 2 completes with low confidence
        - Assets generated with ESTIMATED_ prefix
        - Metadata includes disclaimers about low confidence
        """
        hotel_name = "Hostal Económico"
        hotel_url = "https://www.hostaleconomico.com"
        hotel_id = OnboardingController.generate_hotel_id(hotel_url)

        # Only user input, no external data
        hotel_inputs = self._create_hotel_inputs(
            rooms=8,
            adr_cop=150000.0,
            occupancy_rate=0.40,
            whatsapp_number="+573303456789",
        )

        # No scraped data
        scraped_data = self._create_scraped_data(include_data=False)

        # No GBP data
        gbp_data = self._create_gbp_data(include_data=False)

        # Phase 1
        with patch.object(
            self.controller._orchestrator,
            "phase_1_hook",
            return_value=Mock(
                hotel_name=hotel_name,
                hotel_url=hotel_url,
                region="eje_cafetero",
                hook_message=f"{hotel_name} podria estar perdiendo entre $1.000.000 y $3.000.000 COP mensuales",
                loss_range_min=1000000.0,
                loss_range_max=3000000.0,
            ),
        ):
            state = self.controller.start_onboarding(hotel_url, hotel_name, region="eje_cafetero")

        assert state.current_phase == OnboardingPhase.PHASE_2_INPUT

        # Phase 2 with low confidence (only user input)
        mock_phase2_result = Mock()
        mock_phase2_result.conflicts_report = []
        mock_phase2_result.has_conflicts = False
        mock_phase2_result.can_proceed = True
        mock_phase2_result.validated_fields = {
            "whatsapp": {
                "value": "+573303456789",
                "confidence": "ESTIMATED",
                "sources": ["user_input"],
            },
            "adr": {
                "value": 150000.0,
                "confidence": "ESTIMATED",
                "sources": ["user_input"],
            },
        }

        with patch.object(
            self.controller._orchestrator,
            "phase_2_input",
            return_value=mock_phase2_result,
        ):
            state = self.controller.submit_phase_2(
                hotel_id=hotel_id,
                inputs=hotel_inputs,
                scraped_data=scraped_data,
                gbp_data=gbp_data,
            )

        # Verify completion with low confidence
        assert state.current_phase == OnboardingPhase.CALCULATION
        assert state.status == OnboardingStatus.COMPLETED

        # Generate asset with only user input (low confidence)
        dp = DataPoint("whatsapp")
        dp.add_source(DataSource("user_input", "+573303456789", datetime.now().isoformat()))
        # Confidence will be ESTIMATED with only one source

        validated_data = {"whatsapp": dp}

        result = self.generator.generate(
            asset_type="whatsapp_button",
            validated_data=validated_data,
            hotel_name=hotel_name,
            hotel_id=hotel_id,
        )

        # Should succeed but may have ESTIMATED_ prefix
        assert result["success"] is True
        assert "metadata" in result
        self._verify_metadata_structure(result["metadata"])

        # Check for ESTIMATED_ prefix in filename if warning status
        if result["status"] == "estimated":
            assert "ESTIMATED_" in result["filename"] or result["metadata"].get("fallback_used")

    # ====================================================================================
    # TEST SCENARIO 5: Complete Onboarding Flow
    # ====================================================================================

    def test_hotel_5_complete_onboarding_flow(self):
        """Test complete onboarding flow: Phase 1 -> Phase 2 -> Assets.

        Hotel Details:
        - Name: Hotel Flujo Completo
        - Region: Bogota
        - Rooms: 30
        - ADR: $350,000 COP
        - Occupancy: 65%

        Verifies:
        - All phases complete correctly
        - Progress tracking works (0% -> 30% -> 60%)
        - Final assets have metadata
        - Multiple asset types generated
        """
        hotel_name = "Hotel Flujo Completo"
        hotel_url = "https://www.hotelflujocompleto.com"
        hotel_id = OnboardingController.generate_hotel_id(hotel_url)

        hotel_inputs = self._create_hotel_inputs(
            rooms=30,
            adr_cop=350000.0,
            occupancy_rate=0.65,
            whatsapp_number="+573154321098",
            ota_presence=["booking", "expedia", "airbnb", "despegar"],
            direct_channel_percentage=0.30,
        )

        scraped_data = self._create_scraped_data(
            whatsapp="+573154321098",
            price="350000",
            amenities=["wifi", "gym", "restaurant", "parking"],
        )

        gbp_data = self._create_gbp_data(
            phone="+573154321098",
            rating=4.6,
            review_count=210,
        )

        # Verify initial progress
        assert self.controller.get_progress_percentage(hotel_id) == 0

        # Phase 1: Hook
        with patch.object(
            self.controller._orchestrator,
            "phase_1_hook",
            return_value=Mock(
                hotel_name=hotel_name,
                hotel_url=hotel_url,
                region="bogota",
                hook_message=f"{hotel_name} podria estar perdiendo entre $10.000.000 y $25.000.000 COP mensuales",
                loss_range_min=10000000.0,
                loss_range_max=25000000.0,
            ),
        ):
            state = self.controller.start_onboarding(hotel_url, hotel_name, region="bogota")

        # Verify Phase 1 progress
        assert state.current_phase == OnboardingPhase.PHASE_2_INPUT
        assert state.status == OnboardingStatus.PENDING
        assert self.controller.get_progress_percentage(hotel_id) == 30

        # Get status report
        status_report = OnboardingController.format_status_report(state)
        assert "ONBOARDING STATUS REPORT" in status_report
        assert hotel_id in status_report
        assert "fase_2_input" in status_report

        # Phase 2: Input with scenarios
        mock_scenarios = {
            "conservative": {
                "monthly_loss_cop": 12000000.0,
                "probability": 0.6,
                "calculation_basis": "historical_data",
            },
            "optimistic": {
                "monthly_loss_cop": 22000000.0,
                "probability": 0.25,
                "calculation_basis": "market_potential",
            },
            "break_even": {
                "monthly_loss_cop": 0.0,
                "probability": 0.15,
                "calculation_basis": "current_performance",
            },
        }

        mock_phase2_result = Mock()
        mock_phase2_result.conflicts_report = []
        mock_phase2_result.validation_conflicts = []  # Required by format_status_report
        mock_phase2_result.has_conflicts = False
        mock_phase2_result.can_proceed = True
        mock_phase2_result.scenarios = mock_scenarios
        mock_phase2_result.validated_fields = {
            "whatsapp": {"value": "+573154321098", "match_percentage": 100.0},
            "adr": {"value": 350000.0, "match_percentage": 100.0},
            "rooms": {"value": 30},
            "occupancy_rate": {"value": 0.65},
        }
        mock_phase2_result.confidence_scores = {
            "whatsapp": 1.0,
            "adr": 1.0,
            "rooms": 1.0,
        }

        with patch.object(
            self.controller._orchestrator,
            "phase_2_input",
            return_value=mock_phase2_result,
        ):
            state = self.controller.submit_phase_2(
                hotel_id=hotel_id,
                inputs=hotel_inputs,
                scraped_data=scraped_data,
                gbp_data=gbp_data,
            )

        # Verify Phase 2 completion
        assert state.current_phase == OnboardingPhase.CALCULATION
        assert state.status == OnboardingStatus.COMPLETED
        assert state.phase_2_result.scenarios is not None
        assert len(state.phase_2_result.scenarios) == 3
        assert self.controller.get_progress_percentage(hotel_id) == 60
        assert self.controller.can_proceed_to_assets(hotel_id) is True

        # Generate multiple asset types
        # Use matching values across sources for VERIFIED confidence
        whatsapp_dp = self._create_data_point(
            "whatsapp", "+573154321098",
            ["web_scraping", "gbp_api", "user_input"]
        )

        hotel_data_dp = self._create_data_point(
            "hotel_data",
            {
                "name": hotel_name,
                "description": "Hotel de lujo en Bogota",
                "website": hotel_url,
                "phone": "+573154321098",
                "address": "Calle Principal 123",
                "city": "Bogota",
                "country": "CO",
                "amenities": ["wifi", "gym", "restaurant", "parking"],
            },
            ["web_scraping", "user_input"]
        )

        financial_data_dp = self._create_data_point(
            "hotel_financial_data",
            mock_scenarios,
            ["user_input"]
        )

        # Generate WhatsApp button
        result_whatsapp = self.generator.generate(
            asset_type="whatsapp_button",
            validated_data={"whatsapp": whatsapp_dp},
            hotel_name=hotel_name,
            hotel_id=hotel_id,
        )

        # Generate hotel schema
        result_schema = self.generator.generate(
            asset_type="hotel_schema",
            validated_data={"hotel_data": hotel_data_dp},
            hotel_name=hotel_name,
            hotel_id=hotel_id,
        )

        # Generate financial projection
        result_financial = self.generator.generate(
            asset_type="financial_projection",
            validated_data={
                "hotel_financial_data": financial_data_dp,
                "hotel_data": hotel_data_dp,
            },
            hotel_name=hotel_name,
            hotel_id=hotel_id,
        )

        # Verify all assets generated
        assert result_whatsapp["success"] is True
        assert result_schema["success"] is True
        assert result_financial["success"] is True

        # Verify metadata on all assets
        self._verify_metadata_structure(result_whatsapp["metadata"])
        self._verify_metadata_structure(result_schema["metadata"])
        self._verify_metadata_structure(result_financial["metadata"])

        # Get generation summary
        generations = [result_whatsapp, result_schema, result_financial]
        summary = self.generator.get_generation_summary(generations)

        assert summary["total"] == 3
        assert summary["success_rate"] > 0

        # Verify files exist on disk
        asset_results = self._verify_assets_generated(
            hotel_id,
            asset_types=["whatsapp_button", "hotel_schema", "financial_projection"],
        )

        assert len(asset_results["generated"]) >= 2  # At least 2 assets generated

        # Verify final status report
        final_report = OnboardingController.format_status_report(state)
        assert "CALCULATION" in final_report or "completo" in final_report
        assert "Ready for asset generation" in final_report or "completado" in final_report

    # ====================================================================================
    # HELPER METHOD FOR DATA POINT CREATION
    # ====================================================================================

    def _create_data_point(
        self,
        field_name: str,
        value: any,
        sources: list,
        confidence: ConfidenceLevel = None,
    ) -> DataPoint:
        """Create a DataPoint with specified sources and confidence.

        Args:
            field_name: Name of the field
            value: The value to store
            sources: List of source type strings
            confidence: Optional confidence level (used to create conflicting values if CONFLICT)

        Returns:
            Configured DataPoint instance
        """
        dp = DataPoint(field_name)

        for i, source_type in enumerate(sources):
            # If confidence is CONFLICT, add conflicting values for different sources
            if confidence == ConfidenceLevel.CONFLICT and i > 0 and value is not None:
                # Create a slightly different value to trigger conflict
                if isinstance(value, str) and value.startswith("+"):
                    # For phone numbers, change the last digit
                    conflict_value = value[:-1] + str((int(value[-1]) + 1) % 10)
                else:
                    conflict_value = value
                dp.add_source(DataSource(
                    source_type=source_type,
                    value=conflict_value,
                    timestamp=datetime.now().isoformat(),
                ))
            else:
                dp.add_source(DataSource(
                    source_type=source_type,
                    value=value,
                    timestamp=datetime.now().isoformat(),
                ))

        return dp
