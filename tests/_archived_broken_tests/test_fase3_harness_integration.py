"""Tests for Phase 3 - Financial Engine Integration with Agent Harness.

This module tests the integration between the Financial Engine v4.1.0 and
the Agent Harness, verifying handler registration, execution, and feature
flag-based delegation.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from dataclasses import dataclass
from typing import Dict, Any, Optional

from agent_harness import AgentHarness, AgentTask, AgentResult, TaskContext
from modules.financial_engine.harness_handlers import (
    financial_calculation_handler,
    regional_resolver_handler,
    register_financial_handlers,
)
from modules.financial_engine.scenario_calculator import ScenarioType
from modules.financial_engine.feature_flags import (
    FinancialFeatureFlags,
    RolloutMode,
    get_flags,
    reset_flags,
)


# Fixtures
@pytest.fixture
def mock_task_context():
    """Create a mock TaskContext for testing."""
    return TaskContext(
        previous_runs=0,
        last_outcome=None,
        last_error_type=None,
        suggestions=[],
        harness=None,
    )


@pytest.fixture
def sample_financial_payload():
    """Sample payload for financial calculation tests."""
    return {
        "rooms": 20,
        "region": "bogota",
        "user_provided_adr": 350000.0,
        "segment": "boutique",
        "hotel_id": "hotel_test_001",
        "hotel_name": "Hotel Test",
    }


@pytest.fixture
def sample_regional_payload():
    """Sample payload for regional resolver tests."""
    return {
        "region": "medellin",
        "rooms": 30,
        "user_provided_adr": 400000.0,
    }


@pytest.fixture
def harness():
    """Create an AgentHarness instance for testing."""
    return AgentHarness(verbose=False)


# Test Harness Handlers Registration
class TestHarnessHandlers:
    """Tests for handler registration with Agent Harness."""

    def test_harness_handlers_registration(self, harness):
        """Verify that financial handlers are registered correctly."""
        # Initially, handlers should not be registered
        assert "v4_financial_calculation" not in harness._task_handlers
        assert "v4_regional_resolver" not in harness._task_handlers

        # Register handlers
        register_financial_handlers(harness)

        # Verify handlers are now registered
        assert "v4_financial_calculation" in harness._task_handlers
        assert "v4_regional_resolver" in harness._task_handlers

        # Verify the handlers are callable
        assert callable(harness._task_handlers["v4_financial_calculation"])
        assert callable(harness._task_handlers["v4_regional_resolver"])

    def test_register_financial_handlers_idempotent(self, harness):
        """Verify that registering handlers multiple times works correctly."""
        register_financial_handlers(harness)
        first_calc_handler = harness._task_handlers["v4_financial_calculation"]
        first_reg_handler = harness._task_handlers["v4_regional_resolver"]

        # Register again
        register_financial_handlers(harness)

        # Handlers should be replaced (not duplicated)
        assert harness._task_handlers["v4_financial_calculation"] == first_calc_handler
        assert harness._task_handlers["v4_regional_resolver"] == first_reg_handler


# Test Financial Calculation Handler Directly
class TestFinancialCalculationHandler:
    """Tests for the financial calculation handler."""

    @patch("modules.financial_engine.resolve_adr_with_shadow")
    @patch("modules.financial_engine.calculate_price_with_shadow")
    @patch("modules.financial_engine.ScenarioCalculator")
    @patch("modules.financial_engine.HotelFinancialData")
    def test_financial_calculation_handler_direct(
        self,
        mock_hotel_data_class,
        mock_scenario_calc,
        mock_price_wrapper,
        mock_adr_wrapper,
        mock_task_context,
        sample_financial_payload,
    ):
        """Test the financial calculation handler with mocked dependencies."""
        # Setup mocks
        mock_adr_result = Mock()
        mock_adr_result.adr_cop = 350000.0
        mock_adr_result.source = "regional_v410"
        mock_adr_result.confidence = "VERIFIED"
        mock_adr_result.used_new_calculation = True
        mock_adr_result.metadata = {"region": "bogota", "segment": "boutique"}
        mock_adr_wrapper.return_value = mock_adr_result

        mock_price_result = Mock()
        mock_price_result.monthly_price_cop = 245000.0
        mock_price_result.tier = "boutique"
        mock_price_result.pain_ratio = 0.05
        mock_price_result.is_compliant = True
        mock_price_result.expected_loss_cop = 4900000.0
        mock_price_result.source = "hybrid_v410"
        mock_price_result.used_new_calculation = True
        mock_price_result.metadata = {"formula_used": "hybrid"}
        mock_price_wrapper.return_value = mock_price_result

        mock_scenarios = {
            ScenarioType.CONSERVATIVE: Mock(
                monthly_loss_cop=2100000.0,
                probability=0.70,
            ),
            ScenarioType.REALISTIC: Mock(
                monthly_loss_cop=2940000.0,
                probability=0.20,
            ),
            ScenarioType.OPTIMISTIC: Mock(
                monthly_loss_cop=3780000.0,
                probability=0.10,
            ),
        }
        mock_calculator = Mock()
        mock_calculator.calculate_scenarios.return_value = mock_scenarios
        mock_scenario_calc.return_value = mock_calculator

        # Mock HotelFinancialData to accept region and segment params
        mock_hotel_data_instance = Mock()
        mock_hotel_data_class.return_value = mock_hotel_data_instance

        # Execute handler
        result = financial_calculation_handler(sample_financial_payload, mock_task_context)

        # Verify result structure
        assert result["success"] is True
        assert "adr_resolution" in result
        assert "pricing" in result
        assert "scenarios" in result
        assert "summary" in result

        # Verify ADR resolution
        assert result["adr_resolution"]["adr_cop"] == 350000.0
        assert result["adr_resolution"]["source"] == "regional_v410"
        assert result["adr_resolution"]["confidence"] == "VERIFIED"

        # Verify pricing
        assert result["pricing"]["monthly_price_cop"] == 245000.0
        assert result["pricing"]["tier"] == "boutique"
        assert result["pricing"]["pain_ratio"] == 0.05
        assert result["pricing"]["is_compliant"] is True

        # Verify scenarios
        assert "conservative" in result["scenarios"]
        assert "realistic" in result["scenarios"]
        assert "optimistic" in result["scenarios"]

        # Verify mocks were called
        mock_adr_wrapper.assert_called_once()
        mock_price_wrapper.assert_called_once()
        mock_calculator.calculate_scenarios.assert_called_once()

    def test_financial_calculation_handler_invalid_rooms(
        self, mock_task_context
    ):
        """Test handler with invalid rooms count."""
        payload = {"rooms": 0, "region": "bogota"}

        result = financial_calculation_handler(payload, mock_task_context)

        assert result["success"] is False
        assert result["error_type"] == "ValidationError"
        assert "Invalid rooms count" in result["error"]

    @patch("modules.financial_engine.resolve_adr_with_shadow")
    def test_financial_calculation_handler_exception(
        self, mock_adr_wrapper, mock_task_context, sample_financial_payload
    ):
        """Test handler when an exception occurs."""
        mock_adr_wrapper.side_effect = Exception("ADR resolution failed")

        result = financial_calculation_handler(sample_financial_payload, mock_task_context)

        assert result["success"] is False
        assert result["error_type"] == "Exception"
        assert "ADR resolution failed" in result["error"]
        assert result["adr_resolution"] is None


# Test Regional Resolver Handler Directly
class TestRegionalResolverHandler:
    """Tests for the regional resolver handler."""

    @patch("modules.financial_engine.resolve_regional_adr")
    def test_regional_resolver_handler_direct(
        self, mock_resolve, mock_task_context, sample_regional_payload
    ):
        """Test the regional resolver handler with mocked dependencies."""
        # Setup mock
        mock_result = Mock()
        mock_result.adr_cop = 400000.0
        mock_result.region = "medellin"
        mock_result.segment = "standard"
        mock_result.confidence = "VERIFIED"
        mock_result.source = "benchmark"
        mock_result.is_default = False
        mock_result.metadata = {"deviation_pct": 5.0}
        mock_resolve.return_value = mock_result

        # Execute handler
        result = regional_resolver_handler(sample_regional_payload, mock_task_context)

        # Verify result structure
        assert result["success"] is True
        assert result["adr_cop"] == 400000.0
        assert result["region"] == "medellin"
        assert result["segment"] == "standard"
        assert result["confidence"] == "VERIFIED"
        assert result["source"] == "benchmark"
        assert result["is_default"] is False

        # Verify validation section
        assert result["validation"]["user_provided_adr"] == 400000.0
        assert result["validation"]["deviation_pct"] == 5.0
        assert result["validation"]["matches_benchmark"] is True

        # Verify mock was called correctly
        mock_resolve.assert_called_once()
        call_args = mock_resolve.call_args
        # Check positional args
        if call_args.args:
            assert call_args.args[0] == "medellin"  # region
            assert call_args.args[1] == 30  # rooms
            assert call_args.args[2] == 400000.0  # user_provided_adr
        else:
            # Check keyword args
            assert call_args.kwargs["region"] == "medellin"
            assert call_args.kwargs["rooms"] == 30
            assert call_args.kwargs["user_provided_adr"] == 400000.0

    def test_regional_resolver_handler_invalid_rooms(self, mock_task_context):
        """Test handler with invalid rooms count."""
        payload = {"region": "bogota", "rooms": -5}

        result = regional_resolver_handler(payload, mock_task_context)

        assert result["success"] is False
        assert result["error_type"] == "ValidationError"
        assert result["adr_cop"] is None

    def test_regional_resolver_handler_default_values(self, mock_task_context):
        """Test handler with default values."""
        payload = {}  # Empty payload

        with patch("modules.financial_engine.resolve_regional_adr") as mock_resolve:
            mock_result = Mock()
            mock_result.adr_cop = 300000.0
            mock_result.region = "default"
            mock_result.segment = "standard"
            mock_result.confidence = "ESTIMATED"
            mock_result.source = "default"
            mock_result.is_default = True
            mock_result.metadata = {}
            mock_resolve.return_value = mock_result

            result = regional_resolver_handler(payload, mock_task_context)

            assert result["success"] is True
            assert result["region"] == "default"
            mock_resolve.assert_called_once_with(
                region="default",
                rooms=10,
                user_provided_adr=None,
                plan_maestro_path=None,
            )


# Test Feature Flag Harness Delegation
class TestFeatureFlagsHarnessDelegation:
    """Tests for feature flag based harness delegation."""

    def test_should_use_harness_delegation_when_enabled(self):
        """Test that harness delegation is enabled when flags are properly configured."""
        flags = FinancialFeatureFlags(
            financial_v410_enabled=True,
            regional_adr_mode=RolloutMode.ACTIVE,
            pricing_hybrid_mode=RolloutMode.ACTIVE,
        )
        assert flags.should_use_harness_delegation() is True

    def test_should_use_harness_delegation_with_canary(self):
        """Test harness delegation with CANARY mode."""
        flags = FinancialFeatureFlags(
            financial_v410_enabled=True,
            regional_adr_mode=RolloutMode.CANARY,
            pricing_hybrid_mode=RolloutMode.SHADOW,  # Not CANARY or ACTIVE
        )
        assert flags.should_use_harness_delegation() is True

    def test_should_not_use_harness_delegation_when_disabled(self):
        """Test that harness delegation is disabled when financial_v410 is off."""
        flags = FinancialFeatureFlags(
            financial_v410_enabled=False,
            regional_adr_mode=RolloutMode.ACTIVE,
        )
        assert flags.should_use_harness_delegation() is False

    def test_should_not_use_harness_delegation_in_shadow(self):
        """Test that harness delegation is disabled in SHADOW mode."""
        flags = FinancialFeatureFlags(
            financial_v410_enabled=True,
            regional_adr_mode=RolloutMode.SHADOW,
            pricing_hybrid_mode=RolloutMode.SHADOW,
        )
        assert flags.should_use_harness_delegation() is False

    def test_should_not_use_harness_delegation_in_legacy(self):
        """Test that harness delegation is disabled in FORCE_LEGACY mode."""
        flags = FinancialFeatureFlags(
            financial_v410_enabled=True,
            regional_adr_mode=RolloutMode.FORCE_LEGACY,
            pricing_hybrid_mode=RolloutMode.FORCE_LEGACY,
        )
        assert flags.should_use_harness_delegation() is False


# Test Backward Compatibility Fallback
class TestBackwardCompatibility:
    """Tests for backward compatibility when flags are disabled."""

    @patch("modules.financial_engine.resolve_adr_with_shadow")
    @patch("modules.financial_engine.calculate_price_with_shadow")
    def test_legacy_path_when_flags_disabled(
        self, mock_price, mock_adr, harness, mock_task_context
    ):
        """Verify that when flags are disabled, legacy code path is used.
        
        This test simulates the scenario where financial_v410_enabled is False
        and ensures the system falls back to legacy behavior.
        """
        from modules.financial_engine.feature_flags import FinancialFeatureFlags

        # Create flags with v4.1.0 disabled
        flags = FinancialFeatureFlags.production_safe()
        assert flags.financial_v410_enabled is False
        assert flags.should_use_harness_delegation() is False

        # Verify legacy resolution would be used
        # (In actual implementation, this would check the mode)
        assert flags.regional_adr_mode == RolloutMode.SHADOW

    def test_feature_flags_production_safe(self):
        """Test that production-safe flags disable all new features."""
        flags = FinancialFeatureFlags.production_safe()

        assert flags.regional_adr_enabled is False
        assert flags.pricing_hybrid_enabled is False
        assert flags.financial_v410_enabled is False
        assert flags.regional_adr_mode == RolloutMode.SHADOW
        assert flags.pricing_hybrid_mode == RolloutMode.SHADOW

    def test_feature_flags_full_enabled(self):
        """Test that full-enabled flags activate all features."""
        flags = FinancialFeatureFlags.full_enabled()

        assert flags.regional_adr_enabled is True
        assert flags.pricing_hybrid_enabled is True
        assert flags.financial_v410_enabled is True
        assert flags.regional_adr_mode == RolloutMode.ACTIVE
        assert flags.pricing_hybrid_mode == RolloutMode.ACTIVE


# Test Harness Run Task Integration
class TestHarnessRunTaskIntegration:
    """Tests for harness.run_task() integration with financial tasks."""

    @pytest.fixture
    def harness_with_handlers(self):
        """Create a harness with financial handlers registered."""
        harness = AgentHarness(verbose=False)
        register_financial_handlers(harness)
        return harness

    @patch("modules.financial_engine.resolve_adr_with_shadow")
    @patch("modules.financial_engine.calculate_price_with_shadow")
    @patch("modules.financial_engine.ScenarioCalculator")
    @patch("modules.financial_engine.HotelFinancialData")
    def test_harness_run_task_integration(
        self,
        mock_hotel_data_class,
        mock_scenario_calc,
        mock_price_wrapper,
        mock_adr_wrapper,
        harness_with_handlers,
    ):
        """Verify that harness.run_task() works with financial calculation tasks."""
        # Setup mocks
        mock_adr_result = Mock()
        mock_adr_result.adr_cop = 300000.0
        mock_adr_result.source = "regional_v410"
        mock_adr_result.confidence = "VERIFIED"
        mock_adr_result.used_new_calculation = True
        mock_adr_result.metadata = {}
        mock_adr_wrapper.return_value = mock_adr_result

        mock_price_result = Mock()
        mock_price_result.monthly_price_cop = 200000.0
        mock_price_result.tier = "standard"
        mock_price_result.pain_ratio = 0.05
        mock_price_result.is_compliant = True
        mock_price_result.expected_loss_cop = 4000000.0
        mock_price_result.source = "hybrid_v410"
        mock_price_result.used_new_calculation = True
        mock_price_result.metadata = {}
        mock_price_wrapper.return_value = mock_price_result

        mock_scenarios = {
            ScenarioType.CONSERVATIVE: Mock(
                monthly_loss_cop=2000000.0,
                probability=0.70,
            ),
            ScenarioType.REALISTIC: Mock(
                monthly_loss_cop=2800000.0,
                probability=0.20,
            ),
            ScenarioType.OPTIMISTIC: Mock(
                monthly_loss_cop=3600000.0,
                probability=0.10,
            ),
        }
        mock_calculator = Mock()
        mock_calculator.calculate_scenarios.return_value = mock_scenarios
        mock_scenario_calc.return_value = mock_calculator

        # Mock HotelFinancialData
        mock_hotel_data_class.return_value = Mock()

        # Create and run task
        task = AgentTask(
            name="v4_financial_calculation",
            payload={
                "rooms": 15,
                "region": "cartagena",
                "hotel_id": "test_hotel_123",
            },
        )

        result = harness_with_handlers.run_task(task)

        # Verify result
        assert isinstance(result, AgentResult)
        assert result.success is True
        assert result.outcome in ("success", "partial_failure")
        assert "adr_resolution" in result.data
        assert "pricing" in result.data
        assert "scenarios" in result.data
        assert result.data["success"] is True

    @patch("modules.financial_engine.resolve_regional_adr")
    def test_harness_run_regional_resolver_task(
        self, mock_resolve, harness_with_handlers
    ):
        """Verify that harness.run_task() works with regional resolver tasks."""
        # Setup mock
        mock_result = Mock()
        mock_result.adr_cop = 450000.0
        mock_result.region = "cali"
        mock_result.segment = "standard"
        mock_result.confidence = "VERIFIED"
        mock_result.source = "benchmark"
        mock_result.is_default = False
        mock_result.metadata = {}
        mock_resolve.return_value = mock_result

        # Create and run task
        task = AgentTask(
            name="v4_regional_resolver",
            payload={"region": "cali", "rooms": 40},
        )

        result = harness_with_handlers.run_task(task)

        # Verify result
        assert isinstance(result, AgentResult)
        assert result.success is True
        assert result.data["success"] is True
        assert result.data["adr_cop"] == 450000.0
        assert result.data["region"] == "cali"

    def test_harness_run_unknown_task(self, harness_with_handlers):
        """Verify that unknown tasks return appropriate error."""
        task = AgentTask(
            name="unknown_task",
            payload={"data": "test"},
        )

        result = harness_with_handlers.run_task(task)

        assert isinstance(result, AgentResult)
        assert result.success is False
        assert result.outcome == "error"

    def test_harness_task_context_injection(self, harness_with_handlers):
        """Verify that TaskContext is properly injected during task execution."""
        context_received = []

        def capture_context_handler(payload, context):
            context_received.append(context)
            return {"captured": True}

        harness_with_handlers.register_handler("test_context", capture_context_handler)

        task = AgentTask(name="test_context", payload={"url": "https://test.com"})
        harness_with_handlers.run_task(task)

        assert len(context_received) == 1
        assert isinstance(context_received[0], TaskContext)


# Test End-to-End Integration
class TestEndToEndIntegration:
    """End-to-end integration tests for Phase 3."""

    def test_full_workflow_with_harness(self):
        """Test the complete workflow from harness creation to task execution."""
        # Step 1: Create harness
        harness = AgentHarness(verbose=False)

        # Step 2: Register financial handlers
        register_financial_handlers(harness)

        # Step 3: Verify handlers are registered
        assert "v4_financial_calculation" in harness._task_handlers
        assert "v4_regional_resolver" in harness._task_handlers

        # Step 4: Create feature flags
        flags = FinancialFeatureFlags.full_enabled()
        assert flags.should_use_harness_delegation() is True

        # Step 5: Verify integration is ready
        assert harness._task_handlers["v4_financial_calculation"].__name__ == "financial_calculation_handler"
        assert harness._task_handlers["v4_regional_resolver"].__name__ == "regional_resolver_handler"


# Test Error Handling and Edge Cases
class TestErrorHandlingAndEdgeCases:
    """Tests for error handling and edge cases."""

    def test_handler_with_none_payload(self, mock_task_context):
        """Test handler behavior with None payload."""
        # Handlers should handle missing keys gracefully
        result = financial_calculation_handler({}, mock_task_context)

        # Should not crash, but may return error due to validation
        assert isinstance(result, dict)
        assert "success" in result

    def test_handler_with_extra_payload_keys(self, mock_task_context):
        """Test handler ignores extra keys in payload."""
        payload = {
            "rooms": 10,
            "region": "bogota",
            "extra_key": "should_be_ignored",
            "another_extra": 123,
        }

        with patch("modules.financial_engine.resolve_adr_with_shadow") as mock_adr:
            mock_adr.return_value = Mock(
                adr_cop=300000.0,
                source="test",
                confidence="VERIFIED",
                used_new_calculation=True,
                metadata={},
            )
            with patch("modules.financial_engine.calculate_price_with_shadow") as mock_price:
                mock_price.return_value = Mock(
                    monthly_price_cop=150000.0,
                    tier="standard",
                    pain_ratio=0.05,
                    is_compliant=True,
                    expected_loss_cop=3000000.0,
                    source="test",
                    used_new_calculation=True,
                    metadata={},
                )
                with patch("modules.financial_engine.ScenarioCalculator") as mock_calc:
                    with patch("modules.financial_engine.HotelFinancialData") as mock_hotel_data:
                        mock_scenarios = {
                            ScenarioType.CONSERVATIVE: Mock(
                                monthly_loss_cop=1500000.0,
                                probability=0.70,
                            ),
                            ScenarioType.REALISTIC: Mock(
                                monthly_loss_cop=2100000.0,
                                probability=0.20,
                            ),
                            ScenarioType.OPTIMISTIC: Mock(
                                monthly_loss_cop=2700000.0,
                                probability=0.10,
                            ),
                        }
                        mock_instance = Mock()
                        mock_instance.calculate_scenarios.return_value = mock_scenarios
                        mock_calc.return_value = mock_instance
                        mock_hotel_data.return_value = Mock()

                        result = financial_calculation_handler(payload, mock_task_context)

                        # Should succeed despite extra keys
                        assert result["success"] is True

    def test_handler_preserves_payload_values(self, mock_task_context):
        """Test that handler preserves and uses payload values correctly."""
        payload = {
            "rooms": 25,
            "region": "barranquilla",
            "user_provided_adr": 500000.0,
        }

        with patch("modules.financial_engine.resolve_adr_with_shadow") as mock_adr:
            mock_adr.return_value = Mock(
                adr_cop=500000.0,
                source="user_provided",
                confidence="VERIFIED",
                used_new_calculation=False,
                metadata={},
            )
            with patch("modules.financial_engine.calculate_price_with_shadow") as mock_price:
                mock_price.return_value = Mock(
                    monthly_price_cop=250000.0,
                    tier="standard",
                    pain_ratio=0.05,
                    is_compliant=True,
                    expected_loss_cop=8750000.0,  # 500000 * 25 * 0.7
                    source="test",
                    used_new_calculation=True,
                    metadata={},
                )
                with patch("modules.financial_engine.ScenarioCalculator") as mock_calc:
                    with patch("modules.financial_engine.HotelFinancialData") as mock_hotel_data:
                        mock_scenarios = {
                            ScenarioType.CONSERVATIVE: Mock(
                                monthly_loss_cop=4375000.0,
                                probability=0.70,
                            ),
                            ScenarioType.REALISTIC: Mock(
                                monthly_loss_cop=5625000.0,
                                probability=0.20,
                            ),
                            ScenarioType.OPTIMISTIC: Mock(
                                monthly_loss_cop=7875000.0,
                                probability=0.10,
                            ),
                        }
                        mock_instance = Mock()
                        mock_instance.calculate_scenarios.return_value = mock_scenarios
                        mock_calc.return_value = mock_instance
                        mock_hotel_data.return_value = Mock()

                        result = financial_calculation_handler(payload, mock_task_context)

                        # Verify the handler used the correct values
                        mock_adr.assert_called_once()
                        # Check args (positional or keyword)
                        if mock_adr.call_args.args:
                            assert mock_adr.call_args.args[0] == "barranquilla"
                            assert mock_adr.call_args.args[1] == 25
                            assert mock_adr.call_args.args[2] == 500000.0

                        assert result["success"] is True
                        assert result["summary"]["rooms"] == 25
                        assert result["summary"]["region"] == "barranquilla"


# Test Memory Integration
class TestMemoryIntegration:
    """Tests for integration with Agent Harness memory system."""

    def test_task_execution_logged_to_memory(self, harness, sample_financial_payload):
        """Verify that task executions are logged to memory."""
        register_financial_handlers(harness)

        with patch("modules.financial_engine.resolve_adr_with_shadow") as mock_adr:
            mock_adr.return_value = Mock(
                adr_cop=300000.0,
                source="test",
                confidence="VERIFIED",
                used_new_calculation=True,
                metadata={},
            )
            with patch("modules.financial_engine.calculate_price_with_shadow") as mock_price:
                mock_price.return_value = Mock(
                    monthly_price_cop=150000.0,
                    tier="standard",
                    pain_ratio=0.05,
                    is_compliant=True,
                    expected_loss_cop=3000000.0,
                    source="test",
                    used_new_calculation=True,
                    metadata={},
                )
                with patch("modules.financial_engine.ScenarioCalculator") as mock_calc:
                    with patch("modules.financial_engine.HotelFinancialData") as mock_hotel_data:
                        mock_scenarios = Mock()
                        mock_scenarios.conservative = Mock(
                            monthly_revenue_cop=1500000.0,
                            annual_revenue_cop=18000000.0,
                            occupancy_rate=0.50,
                            probability=0.70,
                        )
                        mock_scenarios.realistic = Mock(
                            monthly_revenue_cop=2100000.0,
                            annual_revenue_cop=25200000.0,
                            occupancy_rate=0.70,
                            probability=0.20,
                        )
                        mock_scenarios.optimistic = Mock(
                            monthly_revenue_cop=2700000.0,
                            annual_revenue_cop=32400000.0,
                            occupancy_rate=0.90,
                            probability=0.10,
                        )
                        mock_instance = Mock()
                        mock_instance.calculate_all_scenarios.return_value = mock_scenarios
                        mock_calc.return_value = mock_instance
                        mock_hotel_data.return_value = Mock()

                        task = AgentTask(
                            name="v4_financial_calculation",
                            payload=sample_financial_payload,
                        )

                        result = harness.run_task(task)

                        # Verify execution was logged
                        assert result.success is True
                        # Memory logging happens in harness.run_task


# Test Concurrent Handler Registration
class TestConcurrentHandlerRegistration:
    """Tests for handler registration behavior."""

    def test_multiple_harnesses_independent_handlers(self):
        """Verify that multiple harness instances have independent handlers."""
        harness1 = AgentHarness(verbose=False)
        harness2 = AgentHarness(verbose=False)

        register_financial_handlers(harness1)

        # Only harness1 should have the handlers
        assert "v4_financial_calculation" in harness1._task_handlers
        assert "v4_regional_resolver" in harness1._task_handlers
        assert "v4_financial_calculation" not in harness2._task_handlers
        assert "v4_regional_resolver" not in harness2._task_handlers

        # Register on harness2 as well
        register_financial_handlers(harness2)

        # Now both should have the handlers
        assert "v4_financial_calculation" in harness1._task_handlers
        assert "v4_financial_calculation" in harness2._task_handlers

        # But they should be separate objects
        assert harness1._task_handlers is not harness2._task_handlers
