"""Integration Test for Phase 3: Guardrails Financieros.

Valida que todos los componentes de la Fase 3 funcionan juntos:
- No Defaults Validator
- Domain Gates
- Financial Calculator v2
- Coherence Gate

Caso de prueba: Hotel Vísperas (debe ser bloqueado)
"""

import pytest
from modules.financial_engine.no_defaults_validator import NoDefaultsValidator
from modules.financial_engine.calculator_v2 import (
    FinancialCalculatorV2,
    CalculationStatus,
    calculate_financial_scenarios,
)
from modules.quality_gates.coherence_gate import (
    CoherenceGate,
    CoherenceStatus,
    PublicationStatus,
)
from modules.quality_gates.domain_gates import (
    DomainGatesOrchestrator,
)


class TestPhase3Integration:
    """Integration tests for Phase 3 components."""

    def test_end_to_end_valid_data(self):
        """Test complete flow with valid data."""
        # Datos válidos - estructura esperada por domain gates
        assessment = {
            "coherence_score": 0.85,
            "schema": {"coverage": 0.8, "errors": []},
            "performance": {
                "data_source": "pagespeed_api",
                "lighthouse_score": 75,
                "first_contentful_paint": 1.5,
                "largest_contentful_paint": 2.0,
            },
            "contact": {
                "whatsapp": {"number": "+573001234567", "confidence": 0.95, "source": "user_input"}
            },
            "google_business_profile": {"status": "active"},
            "hotel_info": {"name": "Test Hotel", "address": "Test Address"},
        }

        # Para FinancialCalculatorV2 (formato plano)
        financial_data_flat = {
            "rooms": 50,
            "adr_cop": 180000.0,
            "occupancy_rate": 0.70,
            "direct_channel_percentage": 0.20,
        }

        # Para DomainGatesOrchestrator (formato anidado)
        financial_data_nested = {
            "inputs": {
                "rooms": 50,
                "adr": 180000.0,
                "occupancy": 0.70,
                "direct_percentage": 0.20,
            },
            "validation": {"validated": True},
            "data_source": {"type": "user_input", "confidence": 0.8},
        }
        
        # 1. Validar coherencia
        coherence_gate = CoherenceGate()
        coherence_result = coherence_gate.check(assessment)
        assert coherence_result.passed is True
        
        # 2. Calcular escenarios (usa formato plano)
        calculator = FinancialCalculatorV2()
        calc_result = calculator.calculate_conditional(
            financial_data_flat,
            coherence_score=assessment["coherence_score"],
            min_coherence=0.8
        )
        assert calc_result.status == CalculationStatus.SUCCESS
        assert calc_result.scenarios is not None
        
        # 3. Ejecutar domain gates (usa formato anidado)
        orchestrator = DomainGatesOrchestrator()
        gate_results = orchestrator.execute_all(assessment, financial_data_nested)
        assert gate_results["can_proceed"] is True
        # all_passed es False porque hay warnings, pero se puede proceder

    def test_end_to_end_blocked_by_defaults(self):
        """Test complete flow blocked by default values."""
        assessment = {
            "coherence_score": 0.85,
        }
        
        # Datos con valores por defecto
        financial_data = {
            "rooms": 50,
            "adr_cop": 0,  # Default
            "occupancy_rate": 0,  # Default
            "direct_channel_percentage": 0,
        }
        
        # Calcular escenarios
        calculator = FinancialCalculatorV2()
        calc_result = calculator.calculate(financial_data)
        
        assert calc_result.status == CalculationStatus.BLOCKED_BY_DEFAULTS
        assert calc_result.blocked is True
        assert calc_result.scenarios is None

    def test_end_to_end_blocked_by_coherence(self):
        """Test complete flow blocked by low coherence."""
        assessment = {
            "coherence_score": 0.4,  # Low coherence
        }
        
        financial_data = {
            "rooms": 50,
            "adr_cop": 180000.0,
            "occupancy_rate": 0.70,
            "direct_channel_percentage": 0.20,
        }
        
        # Validar coherencia
        coherence_gate = CoherenceGate()
        coherence_result = coherence_gate.check(assessment)
        
        assert coherence_result.passed is False
        assert coherence_result.status == CoherenceStatus.DRAFT_INTERNAL
        
        # Calcular con coherencia condicional
        calculator = FinancialCalculatorV2()
        calc_result = calculator.calculate_conditional(
            financial_data,
            coherence_score=assessment["coherence_score"],
            min_coherence=0.8
        )
        
        assert calc_result.status == CalculationStatus.BLOCKED_BY_VALIDATION


class TestHotelVisperasRegression:
    """Regression test for Hotel Vísperas case.
    
    Hotel Vísperas tenía:
    - coherence_score: 0.0
    - Datos financieros incompletos (defaults)
    - Este caso NUNCA debe generar documentos certificados
    """

    def test_visperas_blocked_by_coherence(self):
        """Hotel Vísperas: coherence 0% bloquea certificación."""
        gate = CoherenceGate()
        result = gate.execute(coherence_score=0.0)
        
        assert result.passed is False
        assert result.can_certify is False
        assert result.can_publish is False
        assert result.status == CoherenceStatus.DRAFT_INTERNAL
        assert result.publication_status == PublicationStatus.DRAFT_INTERNAL

    def test_visperas_blocked_by_defaults(self):
        """Hotel Vísperas: datos incompletos bloquean cálculo."""
        calculator = FinancialCalculatorV2()
        
        # Simular datos incompletos como los de Hotel Vísperas
        incomplete_data = {
            "rooms": 20,  # Conocido
            "adr_cop": 0,  # Desconocido/default
            "occupancy_rate": 0,  # Desconocido/default
            "direct_channel_percentage": 0,  # Desconocido/default
        }
        
        result = calculator.calculate(incomplete_data)
        
        assert result.status == CalculationStatus.BLOCKED_BY_DEFAULTS
        assert result.blocked is True
        assert result.scenarios is None
        assert result.validation_result is not None
        assert len(result.validation_result.blocks) >= 2

    def test_visperas_complete_flow_blocked(self):
        """Hotel Vísperas: flujo completo debe estar bloqueado."""
        # Simular assessment de Hotel Vísperas
        visperas_assessment = {
            "coherence_score": 0.0,
            "hard_contradictions": 3,
            "evidence_coverage": 0.2,
            "schema_analysis": {
                "coverage_score": 0.6,
                "has_hotel_schema": True,
                "missing_critical_fields": ["image", "aggregateRating"],
            },
            "performance_analysis": {
                "performance_score": 51,  # CRITICAL
                "has_critical_issues": True,
            },
            "whatsapp_data": {
                "verified": True,
                "confidence": 0.95,
            },
            "gbp_analysis": {
                "is_claimed": False,
            },
        }
        
        visperas_financial = {
            "rooms": 20,
            "adr_cop": 0,  # Desconocido
            "occupancy_rate": 0,  # Desconocido
            "direct_channel_percentage": 0,  # Desconocido
        }
        
        # 1. Coherence gate debe fallar
        coherence_gate = CoherenceGate()
        coherence_result = coherence_gate.check(visperas_assessment)
        assert coherence_result.passed is False
        assert coherence_result.can_certify is False
        
        # 2. Financial calculator debe bloquear
        calculator = FinancialCalculatorV2()
        calc_result = calculator.calculate_conditional(
            visperas_financial,
            coherence_score=visperas_assessment["coherence_score"],
            min_coherence=0.8
        )
        assert calc_result.blocked is True
        
        # 3. Domain gates debe detectar problemas
        orchestrator = DomainGatesOrchestrator()
        gate_results = orchestrator.execute_all(
            visperas_assessment,
            visperas_financial
        )
        assert gate_results["all_passed"] is False
        
        # 4. No se pueden generar documentos
        assert orchestrator.can_generate_documents(gate_results) is False

    def test_visperas_no_financial_projection(self):
        """Hotel Vísperas: no debe tener proyecciones financieras."""
        result = calculate_financial_scenarios(
            rooms=20,
            adr_cop=0,
            occupancy_rate=0,
            direct_channel_percentage=0,
            coherence_score=0.0,
            min_coherence=0.8,
        )
        
        assert result.status in [
            CalculationStatus.BLOCKED_BY_DEFAULTS,
            CalculationStatus.BLOCKED_BY_VALIDATION
        ]
        assert result.scenarios is None
        assert result.hook_range is None


class TestPhase3AcceptanceCriteria:
    """Tests for Phase 3 acceptance criteria."""

    def test_occupancy_rate_zero_blocks(self):
        """[CRITERIO] occupancy_rate=0 bloquea cálculo."""
        validator = NoDefaultsValidator()
        result = validator.validate({
            "rooms": 50,
            "adr_cop": 180000.0,
            "occupancy_rate": 0,
            "direct_channel_percentage": 0.20,
        })
        assert result.can_calculate is False

    def test_direct_channel_zero_blocks(self):
        """[CRITERIO] direct_channel_percentage=0 bloquea cálculo."""
        validator = NoDefaultsValidator()
        result = validator.validate({
            "rooms": 50,
            "adr_cop": 180000.0,
            "occupancy_rate": 0.70,
            "direct_channel_percentage": 0,
        })
        assert result.can_calculate is False

    def test_adr_cop_zero_blocks(self):
        """[CRITERIO] adr_cop=0 bloquea proyección."""
        validator = NoDefaultsValidator()
        result = validator.validate({
            "rooms": 50,
            "adr_cop": 0,
            "occupancy_rate": 0.70,
            "direct_channel_percentage": 0.20,
        })
        assert result.can_calculate is False

    def test_coherence_below_0_8_blocks_certified(self):
        """[CRITERIO] Coherence < 0.8 bloquea estado 'certificado'."""
        gate = CoherenceGate()
        result = gate.execute(coherence_score=0.79)
        
        assert result.can_certify is False
        assert result.status != CoherenceStatus.CERTIFIED

    def test_descriptive_error_messages(self):
        """[CRITERIO] Mensajes de error descriptivos para usuario."""
        validator = NoDefaultsValidator()
        result = validator.validate({
            "rooms": 50,
            "adr_cop": 0,
            "occupancy_rate": 0,
        })
        
        message = result.to_user_message()
        
        # Debe incluir información útil
        assert "BLOQUEADO" in message or "bloqueado" in message.lower()
        assert "onboarding" in message.lower()
        assert "adr_cop" in message or "occupancy" in message
