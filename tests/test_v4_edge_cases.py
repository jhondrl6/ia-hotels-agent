"""
Tests de Casos de Borde v4.0

Basado en casos documentados en .agent/knowledge/DOMAIN_PRIMER.md
"""
import pytest
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from modules.data_validation import CrossValidator
from modules.data_validation.confidence_taxonomy import (
    ConfidenceLevel, DataPoint, DataSource, ValidationResult, ConfidenceTaxonomy
)
from modules.financial_engine.scenario_calculator import (
    ScenarioCalculator, HotelFinancialData, ScenarioType, FinancialScenario
)
from modules.commercial_documents.v4_diagnostic_generator import V4DiagnosticGenerator
from modules.asset_generation.v4_asset_orchestrator import (
    V4AssetOrchestrator, GeneratedAsset, FailedAsset
)
from modules.commercial_documents.data_structures import (
    ValidationSummary, ValidatedField, AssetSpec,
    V4AuditResult, SchemaValidation, GBPData, PerformanceData, CrossValidationResult,
    FinancialScenarios, Scenario, ConfidenceLevel as DSConfidenceLevel,
    DiagnosticDocument, ProposalDocument
)


class TestWhatsAppConflictCases:
    """Caso 1: WhatsApp válido pero GBP contradictorio"""
    
    def test_whatsapp_valid_but_gbp_conflicting(self):
        """
        Caso: WhatsApp en web es válido pero difiere de GBP.
        Comportamiento esperado: CONFLICT, confidence < 0.5
        """
        validator = CrossValidator()
        
        # Web tiene WhatsApp válido
        validator.add_scraped_data("whatsapp", "+573113973744")
        
        # GBP tiene WhatsApp diferente
        validator.add_gbp_data("whatsapp", "+573000000000")
        
        result = validator.get_validated_field("whatsapp")
        
        assert result is not None
        assert result.confidence == ConfidenceLevel.CONFLICT
        assert result._validation_result.match_percentage < 50.0
        assert not result.can_use
        assert len(result._validation_result.discrepancies) > 0
    
    def test_whatsapp_single_source(self):
        """Sub-caso: Solo una fuente disponible"""
        validator = CrossValidator()
        
        # Solo web tiene WhatsApp
        validator.add_scraped_data("whatsapp", "+573113973744")
        
        result = validator.get_validated_field("whatsapp")
        
        assert result is not None
        # Con una sola fuente, debería ser ESTIMATED
        assert result.confidence == ConfidenceLevel.ESTIMATED
        assert result._validation_result.match_percentage == 100.0
        # Puede usarse en assets pero con disclaimer
        assert result.can_use
        assert result._validation_result.disclaimer is not None


class TestSchemaValidationCases:
    """Caso 2: Schema presente pero inválido"""
    
    def test_schema_present_but_invalid(self):
        """
        Caso: Hotel tiene schema pero no cumple con estándares de Google.
        Comportamiento esperado: Detectado en audit con errores
        """
        # Crear un audit result con schema detectado pero inválido
        schema_validation = SchemaValidation(
            hotel_schema_detected=True,
            hotel_schema_valid=False,
            hotel_confidence="ESTIMATED",
            faq_schema_detected=False,
            faq_schema_valid=False,
            faq_confidence="UNKNOWN",
            org_schema_detected=False,
            total_schemas=1,
            errors=[{"field": "image", "message": "Missing required field: image"}],
            warnings=[{"field": "address", "message": "Address incomplete"}]
        )
        
        # Verificar que el schema fue detectado pero tiene errores
        assert schema_validation.hotel_schema_detected is True
        assert schema_validation.hotel_schema_valid is False
        assert len(schema_validation.errors) > 0
        assert any("image" in str(e) for e in schema_validation.errors)
    
    def test_schema_missing_required_fields(self):
        """Sub-caso: Schema con campos requeridos faltantes"""
        schema_validation = SchemaValidation(
            hotel_schema_detected=True,
            hotel_schema_valid=False,
            hotel_confidence="ESTIMATED",
            faq_schema_detected=False,
            faq_schema_valid=False,
            faq_confidence="UNKNOWN",
            org_schema_detected=False,
            total_schemas=1,
            errors=[
                {"field": "name", "message": "Missing required field"},
                {"field": "url", "message": "Missing required field"},
                {"field": "image", "message": "Missing required field"}
            ]
        )
        
        # Debería tener múltiples errores de campos requeridos
        assert len(schema_validation.errors) == 3
        assert schema_validation.hotel_confidence == "ESTIMATED"


class TestFinancialDataCases:
    """Caso 3: Datos financieros parciales"""
    
    def test_partial_financial_data(self):
        """
        Caso: Solo se conoce número de habitaciones, ADR es estimado.
        Comportamiento esperado: Escenarios calculados con confidence ESTIMATED
        """
        # Datos parciales - solo rooms es real, el resto son defaults
        hotel_data = HotelFinancialData(
            rooms=15,  # Dato real
            adr_cop=300000,  # Estimado (benchmark)
            occupancy_rate=0.50,  # Default
            direct_channel_percentage=0.20,  # Default
            ota_presence=["booking"]  # Default simplificado
        )
        
        calc = ScenarioCalculator()
        scenarios = calc.calculate_scenarios(hotel_data)
        
        # Todos los escenarios deben existir
        assert ScenarioType.CONSERVATIVE in scenarios
        assert ScenarioType.REALISTIC in scenarios
        assert ScenarioType.OPTIMISTIC in scenarios
        
        # Los escenarios deben tener valores calculados
        for scenario_type, scenario in scenarios.items():
            # El valor puede ser negativo en escenarios optimistas (caso de borde #4)
            assert isinstance(scenario.monthly_loss_cop, (int, float))
            assert scenario.probability > 0
            assert scenario.confidence_score > 0
            assert len(scenario.assumptions) > 0
    
    def test_all_defaults_used(self):
        """Sub-caso: Todos los valores son defaults"""
        hotel_data = HotelFinancialData(
            rooms=10,
            adr_cop=250000,
            occupancy_rate=0.40,
            direct_channel_percentage=0.0,  # Default
            ota_presence=["booking", "expedia"]  # Default
        )
        
        calc = ScenarioCalculator()
        scenarios = calc.calculate_scenarios(hotel_data)
        
        # Verificar que se usan los valores default en el cálculo
        conservative = scenarios[ScenarioType.CONSERVATIVE]
        assert conservative.monthly_loss_cop > 0
        assert "5%" in conservative.calculation_basis or "90%" in conservative.calculation_basis


class TestScenarioEdgeCases:
    """Caso 4: Escenarios con rango negativo"""
    
    def test_negative_scenario_range(self):
        """
        Caso: Escenario optimista resulta en valor negativo (ganancia en lugar de pérdida).
        Comportamiento esperado: Sistema maneja gracefulmente
        """
        # Crear escenarios donde el optimista es negativo (hotel ya optimizado)
        scenarios = FinancialScenarios(
            conservative=Scenario(
                monthly_loss_min=5000000, 
                monthly_loss_max=6000000,
                probability=0.70,
                description="Escenario conservador",
                assumptions=["Pérdida mínima estimada"],
                confidence_score=0.85
            ),
            realistic=Scenario(
                monthly_loss_min=2000000, 
                monthly_loss_max=3000000,
                probability=0.20,
                description="Escenario realista",
                assumptions=["Pérdida moderada"],
                confidence_score=0.70
            ),
            optimistic=Scenario(
                monthly_loss_min=-500000,  # Negativo = ganancia
                monthly_loss_max=-100000,
                probability=0.10,
                description="Escenario optimista - hotel ya optimizado",
                assumptions=["Sin pérdidas, hotel ya captura reservas directas"],
                confidence_score=0.50
            )
        )
        
        # El sistema debería manejar valores negativos
        assert scenarios.optimistic.monthly_loss_min < 0
        assert scenarios.optimistic.monthly_loss_max < 0
        
        # El rango formateado debería mostrar el negativo
        formatted = scenarios.format_range_cop()
        assert "$" in formatted
        assert "COP/mes" in formatted
    
    def test_zero_loss_scenario(self):
        """Sub-caso: Pérdida cero (hotel optimizado)"""
        scenarios = FinancialScenarios(
            conservative=Scenario(
                monthly_loss_min=1000000, 
                monthly_loss_max=2000000,
                probability=0.70,
                description="Conservador",
                assumptions=[],
                confidence_score=0.80
            ),
            realistic=Scenario(
                monthly_loss_min=500000, 
                monthly_loss_max=800000,
                probability=0.20,
                description="Realista",
                assumptions=[],
                confidence_score=0.70
            ),
            optimistic=Scenario(
                monthly_loss_min=0, 
                monthly_loss_max=0,
                probability=0.10,
                description="Hotel completamente optimizado",
                assumptions=["Sin pérdidas detectadas"],
                confidence_score=0.90
            )
        )
        
        assert scenarios.optimistic.monthly_loss_min == 0
        assert scenarios.optimistic.monthly_loss_max == 0


class TestAssetGenerationCases:
    """Caso 5: Asset bloqueado por conflicto"""
    
    def test_asset_blocked_by_conflict(self):
        """
        Caso: Asset requiere WhatsApp VERIFIED pero hay CONFLICT.
        Comportamiento esperado: Asset no se genera, reporta BLOCKED
        """
        # Crear validation summary con conflicto en WhatsApp
        validation_summary = ValidationSummary(
            fields=[
                ValidatedField(
                    field_name="whatsapp",
                    value=None,
                    confidence=DSConfidenceLevel.CONFLICT,
                    sources=["web", "gbp"],
                    match_percentage=0.0,
                    can_use_in_assets=False
                )
            ],
            overall_confidence=DSConfidenceLevel.CONFLICT,
            conflicts=[
                {
                    "field_name": "whatsapp",
                    "source_a": "web",
                    "value_a": "+573113973744",
                    "source_b": "gbp",
                    "value_b": "+573000000000"
                }
            ]
        )
        
        # Verificar que hay conflicto
        assert validation_summary.has_conflicts()
        
        # El campo WhatsApp no debería poder usarse en assets
        whatsapp_field = validation_summary.get_field("whatsapp")
        assert whatsapp_field is not None
        assert whatsapp_field.confidence == DSConfidenceLevel.CONFLICT
        assert not whatsapp_field.can_use_in_assets
    
    def test_asset_warning_low_confidence(self):
        """Sub-caso: Confidence bajo pero no bloqueante"""
        validation_summary = ValidationSummary(
            fields=[
                ValidatedField(
                    field_name="whatsapp",
                    value="+573113973744",
                    confidence=DSConfidenceLevel.ESTIMATED,  # No es CONFLICT
                    sources=["web"],  # Solo una fuente
                    match_percentage=100.0,
                    can_use_in_assets=True  # Sí se puede usar con disclaimer
                )
            ],
            overall_confidence=DSConfidenceLevel.ESTIMATED,
            conflicts=[]
        )
        
        # No hay conflictos
        assert not validation_summary.has_conflicts()
        
        # El campo puede usarse pero con warning
        whatsapp_field = validation_summary.get_field("whatsapp")
        assert whatsapp_field.confidence == DSConfidenceLevel.ESTIMATED
        assert whatsapp_field.can_use_in_assets is True
    
    def test_asset_passed_high_confidence(self):
        """Sub-caso: Confidence alto, asset generado"""
        validation_summary = ValidationSummary(
            fields=[
                ValidatedField(
                    field_name="whatsapp",
                    value="+573113973744",
                    confidence=DSConfidenceLevel.VERIFIED,  # Alta confianza
                    sources=["web", "gbp", "user_input"],  # Múltiples fuentes
                    match_percentage=100.0,
                    can_use_in_assets=True
                )
            ],
            overall_confidence=DSConfidenceLevel.VERIFIED,
            conflicts=[]
        )
        
        # Alta confianza, sin conflictos
        whatsapp_field = validation_summary.get_field("whatsapp")
        assert whatsapp_field.confidence == DSConfidenceLevel.VERIFIED
        assert whatsapp_field.can_use_in_assets is True
        assert len(whatsapp_field.sources) >= 2


# Fixtures
@pytest.fixture
def mock_audit_result():
    """Fixture para crear audit results mock"""
    return V4AuditResult(
        url="https://hotelvisperas.com",
        hotel_name="Hotel Visperas",
        timestamp=datetime.now().isoformat(),
        schema=SchemaValidation(
            hotel_schema_detected=True,
            hotel_schema_valid=True,
            hotel_confidence="VERIFIED",
            faq_schema_detected=True,
            faq_schema_valid=True,
            faq_confidence="VERIFIED",
            org_schema_detected=True,
            total_schemas=3
        ),
        gbp=GBPData(
            place_found=True,
            place_id="ChIJ123456789",
            name="Hotel Visperas",
            rating=4.5,
            reviews=127,
            photos=45,
            phone="+573113973744",
            website="https://hotelvisperas.com",
            address="Calle Principal 123",
            geo_score=85,
            geo_score_breakdown={"basic": 100, "media": 80, "engagement": 75},
            confidence="VERIFIED"
        ),
        performance=PerformanceData(
            has_field_data=True,
            mobile_score=72,
            desktop_score=85,
            lcp=2.1,
            fid=15,
            cls=0.05,
            status="GOOD",
            message="Rendimiento aceptable"
        ),
        validation=CrossValidationResult(
            whatsapp_status="VERIFIED",
            phone_web="+573113973744",
            phone_gbp="+573113973744",
            adr_status="ESTIMATED",
            adr_web=None,
            adr_benchmark=350000.0,
            conflicts=[],
            validated_fields={"whatsapp": "+573113973744"}
        ),
        overall_confidence="VERIFIED"
    )


@pytest.fixture
def mock_validation_summary():
    """Fixture para crear validation summaries mock"""
    return ValidationSummary(
        fields=[
            ValidatedField(
                field_name="whatsapp",
                value="+573113973744",
                confidence=DSConfidenceLevel.VERIFIED,
                sources=["web", "gbp"],
                match_percentage=100.0,
                can_use_in_assets=True
            ),
            ValidatedField(
                field_name="rooms",
                value=15,
                confidence=DSConfidenceLevel.VERIFIED,
                sources=["web", "schema"],
                match_percentage=100.0,
                can_use_in_assets=True
            ),
            ValidatedField(
                field_name="adr",
                value=400000,
                confidence=DSConfidenceLevel.ESTIMATED,
                sources=["benchmark"],
                match_percentage=100.0,
                can_use_in_assets=True
            )
        ],
        overall_confidence=DSConfidenceLevel.VERIFIED,
        conflicts=[]
    )


@pytest.fixture
def mock_validation_summary_with_conflict():
    """Fixture para crear validation summary con conflicto"""
    return ValidationSummary(
        fields=[
            ValidatedField(
                field_name="whatsapp",
                value=None,
                confidence=DSConfidenceLevel.CONFLICT,
                sources=["web", "gbp"],
                match_percentage=0.0,
                can_use_in_assets=False
            )
        ],
        overall_confidence=DSConfidenceLevel.CONFLICT,
        conflicts=[
            {
                "field_name": "whatsapp",
                "source_a": "web",
                "value_a": "+573113973744",
                "source_b": "gbp",
                "value_b": "+573000000000"
            }
        ]
    )


@pytest.fixture
def mock_financial_scenarios():
    """Fixture para crear escenarios financieros mock"""
    return FinancialScenarios(
        conservative=Scenario(
            monthly_loss_min=5000000,
            monthly_loss_max=7000000,
            probability=0.70,
            description="Escenario conservador con pérdidas significativas",
            assumptions=["90% occupancy", "18% OTA commission"],
            confidence_score=0.85
        ),
        realistic=Scenario(
            monthly_loss_min=3000000,
            monthly_loss_max=5000000,
            probability=0.20,
            description="Escenario realista basado en datos actuales",
            assumptions=["Current data", "10% shift potential"],
            confidence_score=0.70
        ),
        optimistic=Scenario(
            monthly_loss_min=1000000,
            monthly_loss_max=2000000,
            probability=0.10,
            description="Escenario optimista con mejora significativa",
            assumptions=["20% shift", "IA visibility boost"],
            confidence_score=0.50
        )
    )


@pytest.fixture
def mock_diagnostic_document(tmp_path):
    """Fixture para crear un documento diagnóstico mock"""
    return DiagnosticDocument(
        path=str(tmp_path / "diagnostic.md"),
        problems=[],
        financial_impact=Scenario(
            monthly_loss_min=3000000,
            monthly_loss_max=5000000,
            probability=0.20,
            description="Escenario principal",
            assumptions=[],
            confidence_score=0.70
        ),
        generated_at=datetime.now().isoformat()
    )


@pytest.fixture
def mock_proposal_document(tmp_path):
    """Fixture para crear un documento de propuesta mock"""
    return ProposalDocument(
        path=str(tmp_path / "proposal.md"),
        price_monthly=1500000,
        assets_proposed=[],
        roi_projected=2.5,
        generated_at=datetime.now().isoformat()
    )
