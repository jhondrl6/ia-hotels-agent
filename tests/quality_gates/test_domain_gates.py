"""Tests for Domain Gates.

Valida los gates por dominio: Técnico, Comercial y Financiero.
"""

import pytest
from modules.quality_gates.domain_gates import (
    TechnicalGate,
    CommercialGate,
    FinancialGate,
    DomainGatesOrchestrator,
    GateType,
    GateStatus,
    GateCheck,
    DomainGateResult,
)


class TestTechnicalGate:
    """Test cases for Technical Gate."""

    def test_technical_gate_initialization(self):
        """Test TechnicalGate initializes with correct config."""
        gate = TechnicalGate()
        assert gate.min_schema_coverage == 0.5
        assert gate.max_performance_score == 50

    def test_technical_gate_with_config(self):
        """Test TechnicalGate accepts custom config."""
        gate = TechnicalGate(config={
            "min_schema_coverage": 0.7,
            "max_performance_score": 60
        })
        assert gate.min_schema_coverage == 0.7
        assert gate.max_performance_score == 60

    def test_schema_valid_passes(self):
        """Test schema validation passes with good coverage."""
        gate = TechnicalGate()

        assessment = {
            "schema": {
                "coverage": 0.8,
                "errors": [],
            }
        }

        check = gate._check_schema_valid(assessment)
        assert check.passed is True

    def test_schema_low_coverage_fails(self):
        """Test schema validation fails with low coverage."""
        gate = TechnicalGate()

        assessment = {
            "schema": {
                "coverage": 0.3,
                "errors": [],
            }
        }

        check = gate._check_schema_valid(assessment)
        assert check.passed is False

    def test_performance_measured_passes(self):
        """Test performance check passes when measured."""
        gate = TechnicalGate()

        assessment = {
            "performance": {
                "data_source": "pagespeed_api",
                "lighthouse_score": 75,
                "first_contentful_paint": 1.5,
                "largest_contentful_paint": 2.0,
            }
        }

        check = gate._check_performance_measured(assessment)
        assert check.passed is True

    def test_performance_not_measured_fails(self):
        """Test performance check fails when not measured."""
        gate = TechnicalGate()

        assessment = {
            "performance": {}
        }

        check = gate._check_performance_measured(assessment)
        assert check.passed is False


class TestCommercialGate:
    """Test cases for Commercial Gate."""

    def test_commercial_gate_initialization(self):
        """Test CommercialGate initializes correctly."""
        gate = CommercialGate()
        assert gate.whatsapp_confidence_threshold == 0.9

    def test_whatsapp_verified_passes(self):
        """Test WhatsApp check passes when verified."""
        gate = CommercialGate()

        assessment = {
            "contact": {
                "whatsapp": {
                    "number": "+573113973744",
                    "confidence": 0.95,
                    "source": "user_input",
                }
            }
        }

        check = gate._check_whatsapp_verified(assessment)
        assert check.passed is True

    def test_whatsapp_not_verified_fails(self):
        """Test WhatsApp check fails when not verified."""
        gate = CommercialGate()

        assessment = {
            "contact": {
                "whatsapp": {
                    "number": "+573113973744",
                    "confidence": 0.3,
                    "source": "unknown",
                }
            }
        }

        check = gate._check_whatsapp_verified(assessment)
        assert check.passed is False

    def test_gbp_status_known_passes(self):
        """Test GBP check passes when status known."""
        gate = CommercialGate()

        assessment = {
            "google_business_profile": {
                "status": "active",
                "rating": 4.5,
            }
        }

        check = gate._check_gbp_status_known(assessment)
        assert check.passed is True


class TestFinancialGate:
    """Test cases for Financial Gate."""

    def test_financial_gate_initialization(self):
        """Test FinancialGate initializes correctly."""
        gate = FinancialGate()
        assert gate.require_whatsapp is True

    def test_no_defaults_check_passes(self):
        """Test no defaults check passes with valid data."""
        gate = FinancialGate()

        financial_data = {
            "inputs": {
                "rooms": 50,
                "adr": 180000.0,
                "occupancy": 0.70,
                "direct_percentage": 0.20,
            }
        }

        check = gate._check_no_defaults(financial_data)
        assert check.passed is True

    def test_no_defaults_check_fails(self):
        """Test no defaults check fails with defaults."""
        gate = FinancialGate()

        financial_data = {
            "inputs": {
                "rooms": 0,
                "adr": 0,
                "occupancy": 0,
            }
        }

        check = gate._check_no_defaults(financial_data)
        assert check.passed is False

    def test_inputs_validated_passes(self):
        """Test inputs validated check passes."""
        gate = FinancialGate()

        financial_data = {
            "inputs": {
                "rooms": 50,
                "adr": 180000.0,
                "occupancy": 0.70,
            },
            "validation": {
                "validated": True,
            }
        }

        check = gate._check_inputs_validated(financial_data)
        assert check.passed is True


class TestDomainGatesOrchestrator:
    """Test cases for Domain Gates Orchestrator."""

    def test_orchestrator_initialization(self):
        """Test orchestrator initializes all gates."""
        orchestrator = DomainGatesOrchestrator()
        assert orchestrator.technical_gate is not None
        assert orchestrator.commercial_gate is not None
        assert orchestrator.financial_gate is not None

    def test_execute_all_returns_all_gates(self):
        """Test execute_all runs all gates."""
        orchestrator = DomainGatesOrchestrator()

        assessment = {
            "schema": {"coverage": 0.8, "errors": []},
            "performance": {
                "data_source": "pagespeed_api",
                "lighthouse_score": 75,
                "first_contentful_paint": 1.5,
                "largest_contentful_paint": 2.0,
            },
            "contact": {
                "whatsapp": {
                    "number": "+573113973744",
                    "confidence": 0.95,
                    "source": "user_input",
                }
            },
            "google_business_profile": {"status": "active"},
            "hotel_info": {"name": "Test Hotel", "address": "Test Address"},
        }

        financial_data = {
            "inputs": {
                "rooms": 50,
                "adr": 180000.0,
                "occupancy": 0.70,
            },
            "validation": {"validated": True},
            "data_source": {"type": "user_input", "confidence": 0.8},
        }

        results = orchestrator.execute_all(assessment, financial_data)

        assert "gates" in results
        assert "technical" in results["gates"]
        assert "commercial" in results["gates"]
        assert "financial" in results["gates"]
        assert "can_proceed" in results

    def test_can_generate_documents_all_passed(self):
        """Test can_generate_documents when all gates pass."""
        orchestrator = DomainGatesOrchestrator()

        results = {
            "overall_status": "ready",
            "can_proceed": True,
            "gates": {
                "technical": {"passed": True, "status": "passed"},
                "commercial": {"passed": True, "status": "passed"},
                "financial": {"passed": True, "status": "passed"},
            },
        }

        assert orchestrator.can_generate_documents(results) is True

    def test_can_generate_documents_one_failed(self):
        """Test can_generate_documents when one gate fails."""
        orchestrator = DomainGatesOrchestrator()

        results = {
            "overall_status": "blocked",
            "can_proceed": False,
            "gates": {
                "technical": {"passed": True, "status": "passed"},
                "commercial": {"passed": False, "status": "failed"},
                "financial": {"passed": True, "status": "passed"},
            },
        }

        assert orchestrator.can_generate_documents(results) is False

    def test_get_blocking_issues_returns_issues(self):
        """Test get_blocking_issues returns blocking issues."""
        orchestrator = DomainGatesOrchestrator()

        results = {
            "overall_status": "blocked",
            "can_proceed": False,
            "blocking_issues": [
                "[technical] ERROR: Schema invalid",
                "[financial] ERROR: Has defaults",
            ],
            "gates": {
                "technical": {
                    "passed": False,
                    "status": "failed",
                    "checks": [
                        {"name": "schema", "passed": False, "message": "Schema invalid", "severity": "error"},
                        {"name": "performance", "passed": True, "message": "OK", "severity": "info"},
                    ]
                },
                "commercial": {"passed": True, "status": "passed", "checks": []},
                "financial": {
                    "passed": False,
                    "status": "failed",
                    "checks": [
                        {"name": "no_defaults", "passed": False, "message": "Has defaults", "severity": "error"},
                    ]
                },
            },
        }

        issues = orchestrator.get_blocking_issues(results)

        assert len(issues) > 0
        assert any("Schema invalid" in issue for issue in issues)
        assert any("Has defaults" in issue for issue in issues)


class TestGateResult:
    """Test cases for DomainGateResult."""

    def test_gate_result_properties(self):
        """Test DomainGateResult properties."""
        result = DomainGateResult(
            gate_type=GateType.TECHNICAL,
            status=GateStatus.PASSED,
            checks=[
                GateCheck(name="test", passed=True, message="OK"),
            ]
        )
        
        assert result.passed is True
        assert result.failed is False
        assert len(result.critical_failures) == 0

    def test_gate_result_failed(self):
        """Test DomainGateResult when failed."""
        result = DomainGateResult(
            gate_type=GateType.FINANCIAL,
            status=GateStatus.FAILED,
            checks=[
                GateCheck(name="test", passed=False, message="Failed", severity="critical"),
            ]
        )
        
        assert result.passed is False
        assert result.failed is True
        assert len(result.critical_failures) == 1

    def test_gate_result_to_dict(self):
        """Test DomainGateResult serialization."""
        result = DomainGateResult(
            gate_type=GateType.COMMERCIAL,
            status=GateStatus.PASSED,
            checks=[
                GateCheck(name="whatsapp", passed=True, message="Verified"),
            ]
        )
        
        data = result.to_dict()
        
        assert data["gate_type"] == "commercial"
        assert data["status"] == "passed"
        assert data["passed"] is True
        assert len(data["checks"]) == 1
