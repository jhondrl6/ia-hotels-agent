"""
Tests for Phase 2 Commercial Documents v4.0.

Tests for CoherenceValidator and PainSolutionMapper.
"""

import pytest
from datetime import datetime

from modules.commercial_documents.data_structures import (
    DiagnosticDocument,
    ProposalDocument,
    AssetSpec,
    ValidationSummary,
    ValidatedField,
    ConfidenceLevel,
    Scenario,
    V4AuditResult,
    SchemaValidation,
    GBPData,
    PerformanceData,
    CrossValidationResult
)
from modules.commercial_documents.coherence_validator import (
    CoherenceValidator,
    CoherenceReport,
    CoherenceCheck
)
from modules.commercial_documents.pain_solution_mapper import (
    PainSolutionMapper,
    Pain,
    Solution
)


class TestCoherenceValidator:
    """Tests for CoherenceValidator."""
    
    @pytest.fixture
    def validator(self):
        return CoherenceValidator(confidence_threshold=0.7)
    
    @pytest.fixture
    def sample_diagnostic(self):
        return DiagnosticDocument(
            path="output/diagnostic.md",
            problems=[
                Pain(
                    id="no_whatsapp_visible",
                    name="Sin WhatsApp",
                    description="No hay WhatsApp",
                    severity="high",
                    detected_by="validation",
                    confidence=0.9
                ),
                Pain(
                    id="no_faq_schema",
                    name="Sin FAQ",
                    description="No hay FAQ",
                    severity="medium",
                    detected_by="schema",
                    confidence=1.0
                )
            ],
            financial_impact=Scenario(
                monthly_loss_min=1000000,
                monthly_loss_max=3000000,
                probability=0.2,
                description="Realistic scenario"
            ),
            generated_at=datetime.now().isoformat()
        )
    
    @pytest.fixture
    def sample_proposal(self):
        return ProposalDocument(
            path="output/proposal.md",
            price_monthly=135000,  # 4.5% of 3M pain (rango ideal: 3%-6%)
            assets_proposed=[],
            roi_projected=2.5,
            generated_at=datetime.now().isoformat()
        )
    
    @pytest.fixture
    def sample_assets(self):
        return [
            AssetSpec(
                asset_type="whatsapp_button",
                pain_ids=["no_whatsapp_visible"],
                confidence_required=0.9,
                can_generate=True,
                reason="Verified"
            ),
            AssetSpec(
                asset_type="faq_page",
                pain_ids=["no_faq_schema"],
                confidence_required=0.7,
                can_generate=True,
                reason="Sufficient confidence"
            )
        ]
    
    @pytest.fixture
    def sample_validation_summary(self):
        return ValidationSummary(
            fields=[
                ValidatedField(
                    field_name="whatsapp_number",
                    value="+573113973744",
                    confidence=ConfidenceLevel.VERIFIED,
                    sources=["web", "gbp"],
                    match_percentage=1.0,
                    can_use_in_assets=True
                ),
                ValidatedField(
                    field_name="adr_cop",
                    value=400000,
                    confidence=ConfidenceLevel.VERIFIED,
                    sources=["input"],
                    can_use_in_assets=True
                ),
                ValidatedField(
                    field_name="rooms",
                    value=15,
                    confidence=ConfidenceLevel.VERIFIED,
                    sources=["input"],
                    can_use_in_assets=True
                )
            ],
            overall_confidence=ConfidenceLevel.VERIFIED
        )
    
    def test_validate_all_checks_pass(
        self, 
        validator, 
        sample_diagnostic, 
        sample_proposal, 
        sample_assets,
        sample_validation_summary
    ):
        """Test validation when all checks pass."""
        report = validator.validate(
            sample_diagnostic,
            sample_proposal,
            sample_assets,
            sample_validation_summary
        )
        
        assert isinstance(report, CoherenceReport)
        assert report.is_coherent is True
        assert report.overall_score >= 0.6

    def test_promised_assets_exist_pass(self):
        """Test que el check pasa cuando todos los assets están implementados."""
        # Assets que SÍ están en el catálogo como IMPLEMENTED
        assets = [
            AssetSpec(
                asset_type="whatsapp_button",
                pain_ids=["no_whatsapp_visible"],
                confidence_required=0.9,
                can_generate=True,
                reason="Verified"
            ),
            AssetSpec(
                asset_type="faq_page",
                pain_ids=["no_faq_schema"],
                confidence_required=0.7,
                can_generate=True,
                reason="Sufficient confidence"
            ),
            AssetSpec(
                asset_type="hotel_schema",
                pain_ids=["no_hotel_schema"],
                confidence_required=0.8,
                can_generate=True,
                reason="Schema detected"
            ),
        ]
        
        diagnostic = DiagnosticDocument(
            path="output/diagnostic.md",
            problems=[
                Pain(id="no_whatsapp_visible", name="Sin WhatsApp", description="No hay", severity="high", detected_by="validation", confidence=0.9),
                Pain(id="no_faq_schema", name="Sin FAQ", description="No hay", severity="medium", detected_by="schema", confidence=1.0),
                Pain(id="no_hotel_schema", name="Sin Schema", description="No hay", severity="medium", detected_by="schema", confidence=1.0),
            ],
            financial_impact=Scenario(
                monthly_loss_min=1000000,
                monthly_loss_max=3000000,
                probability=0.2,
                description="Realistic"
            ),
            generated_at=datetime.now().isoformat()
        )
        
        proposal = ProposalDocument(
            path="output/proposal.md",
            price_monthly=135000,
            assets_proposed=[],
            roi_projected=2.5,
            generated_at=datetime.now().isoformat()
        )
        
        validation = ValidationSummary(
            fields=[
                ValidatedField(field_name="whatsapp_number", value="+573001234567", confidence=ConfidenceLevel.VERIFIED, sources=["web", "gbp"], match_percentage=1.0, can_use_in_assets=True),
                ValidatedField(field_name="adr_cop", value=350000, confidence=ConfidenceLevel.VERIFIED, sources=["web"], match_percentage=1.0, can_use_in_assets=True),
                ValidatedField(field_name="rooms", value=25, confidence=ConfidenceLevel.VERIFIED, sources=["web"], match_percentage=1.0, can_use_in_assets=True),
                ValidatedField(field_name="occupancy_rate", value=0.75, confidence=ConfidenceLevel.VERIFIED, sources=["web"], match_percentage=1.0, can_use_in_assets=True),
                ValidatedField(field_name="direct_channel_percentage", value=0.30, confidence=ConfidenceLevel.VERIFIED, sources=["web"], match_percentage=1.0, can_use_in_assets=True),
            ],
            overall_confidence=ConfidenceLevel.VERIFIED
        )
        
        validator = CoherenceValidator(confidence_threshold=0.7)
        report = validator.validate(diagnostic, proposal, assets, validation)
        
        # Encontrar el check específico
        promised_check = next((c for c in report.checks if c.name == "promised_assets_exist"), None)
        assert promised_check is not None, "Check promised_assets_exist no encontrado"
        assert promised_check.passed is True, f"Check debería pasar pero: {promised_check.message}"
        assert promised_check.severity == "info"
    
    def test_promised_assets_exist_fail(self):
        """Test que el check falla cuando hay asset no implementado."""
        # Un asset que NO está implementado (MISSING en el catálogo)
        assets = [
            AssetSpec(
                asset_type="nonexistent_asset_12345",
                pain_ids=["poor_performance"],
                confidence_required=0.7,
                can_generate=False,
                reason="Not implemented in catalog"
            ),
            AssetSpec(
                asset_type="whatsapp_button",
                pain_ids=["no_whatsapp_visible"],
                confidence_required=0.9,
                can_generate=True,
                reason="Verified"
            ),
        ]
        
        diagnostic = DiagnosticDocument(
            path="output/diagnostic.md",
            problems=[
                Pain(id="poor_performance", name="Baja Performance", description="Lenta", severity="high", detected_by="validation", confidence=0.9),
                Pain(id="no_whatsapp_visible", name="Sin WhatsApp", description="No hay", severity="high", detected_by="validation", confidence=0.9),
            ],
            financial_impact=Scenario(
                monthly_loss_min=1000000,
                monthly_loss_max=3000000,
                probability=0.2,
                description="Realistic"
            ),
            generated_at=datetime.now().isoformat()
        )
        
        proposal = ProposalDocument(
            path="output/proposal.md",
            price_monthly=135000,
            assets_proposed=[],
            roi_projected=2.5,
            generated_at=datetime.now().isoformat()
        )
        
        validation = ValidationSummary(
            fields=[
                ValidatedField(field_name="whatsapp_number", value="+573001234567", confidence=ConfidenceLevel.VERIFIED, sources=["web", "gbp"], match_percentage=1.0, can_use_in_assets=True),
                ValidatedField(field_name="adr_cop", value=350000, confidence=ConfidenceLevel.VERIFIED, sources=["web"], match_percentage=1.0, can_use_in_assets=True),
                ValidatedField(field_name="rooms", value=25, confidence=ConfidenceLevel.VERIFIED, sources=["web"], match_percentage=1.0, can_use_in_assets=True),
                ValidatedField(field_name="occupancy_rate", value=0.75, confidence=ConfidenceLevel.VERIFIED, sources=["web"], match_percentage=1.0, can_use_in_assets=True),
                ValidatedField(field_name="direct_channel_percentage", value=0.30, confidence=ConfidenceLevel.VERIFIED, sources=["web"], match_percentage=1.0, can_use_in_assets=True),
            ],
            overall_confidence=ConfidenceLevel.VERIFIED
        )
        
        validator = CoherenceValidator(confidence_threshold=0.7)
        report = validator.validate(diagnostic, proposal, assets, validation)
        
        # Encontrar el check específico
        promised_check = next((c for c in report.checks if c.name == "promised_assets_exist"), None)
        assert promised_check is not None, "Check promised_assets_exist no encontrado"
        assert promised_check.passed is False, "Check debería fallar porque hay asset no implementado"
        assert promised_check.severity == "error", "Severidad debe ser error (blocking)"
        assert "nonexistent_asset_12345" in promised_check.message, "Mensaje debe mencionar el asset faltante"


class TestIntegration:
    """Integration tests between mapper and validator."""
    
    def test_end_to_end_workflow(self):
        """Test complete workflow from detection to validation."""
        # Create mapper and detect pains
        mapper = PainSolutionMapper()
        
        audit = V4AuditResult(
            url="https://test.com",
            hotel_name="Test Hotel",
            timestamp=datetime.now().isoformat(),
            schema=SchemaValidation(
                hotel_schema_detected=False,
                hotel_schema_valid=False,
                hotel_confidence="NONE",
                faq_schema_detected=True,
                faq_schema_valid=True,
                faq_confidence="VERIFIED",
                org_schema_detected=True,
                total_schemas=2
            ),
            gbp=GBPData(
                place_found=True,
                place_id="ChIJ123",
                name="Test Hotel",
                rating=4.8,
                reviews=50,
                photos=20,
                phone="+573113973744",
                website="https://test.com",
                address="Test Address",
                geo_score=85,
                geo_score_breakdown={},
                confidence="VERIFIED"
            ),
            performance=PerformanceData(
                has_field_data=True,
                mobile_score=75,
                desktop_score=85,
                lcp=1.5,
                fid=50,
                cls=0.05,
                status="GOOD",
                message="Good performance"
            ),
            validation=CrossValidationResult(
                whatsapp_status="VERIFIED",
                phone_web="+573113973744",
                phone_gbp="+573113973744",
                adr_status="VALIDATED",
                adr_web=400000.0,
                adr_benchmark=380000.0
            ),
            overall_confidence="VERIFIED"
        )
        
        validation = ValidationSummary(
            fields=[
                ValidatedField(
                    field_name="whatsapp_number",
                    value="+573113973744",
                    confidence=ConfidenceLevel.VERIFIED,
                    sources=["web", "gbp"],
                    can_use_in_assets=True
                ),
                ValidatedField(
                    field_name="adr_cop",
                    value=350000,
                    confidence=ConfidenceLevel.VERIFIED,
                    sources=["input"],
                    can_use_in_assets=True
                ),
                ValidatedField(
                    field_name="rooms",
                    value=10,
                    confidence=ConfidenceLevel.VERIFIED,
                    sources=["input"],
                    can_use_in_assets=True
                ),
                ValidatedField(
                    field_name="occupancy_rate",
                    value=0.6,
                    confidence=ConfidenceLevel.ESTIMATED,
                    sources=["benchmark"],
                    can_use_in_assets=True
                )
            ],
            overall_confidence=ConfidenceLevel.VERIFIED
        )
        
        # Detect pains
        pains = mapper.detect_pains(audit, validation)
        
        # Generate asset plan
        assets = mapper.generate_asset_plan(pains, validation)
        
        # Create documents
        diagnostic = DiagnosticDocument(
            path="output/diagnostic.md",
            problems=pains,
            financial_impact=Scenario(
                monthly_loss_min=500000,
                monthly_loss_max=2000000,
                probability=0.2,
                description="Realistic scenario"
            ),
            generated_at=datetime.now().isoformat()
        )
        
        proposal = ProposalDocument(
            path="output/proposal.md",
            price_monthly=90000,  # 4.5% of 2M pain = rango ideal
            assets_proposed=assets,
            roi_projected=3.0,
            generated_at=datetime.now().isoformat()
        )
        
        # Validate coherence
        validator = CoherenceValidator(confidence_threshold=0.7)
        report = validator.validate(diagnostic, proposal, assets, validation)
        
        assert report.is_coherent is True
        assert report.overall_score >= 0.6
        """Test que el check pasa cuando todos los assets están implementados."""
        # Assets que SÍ están en el catálogo como IMPLEMENTED
        assets = [
            AssetSpec(
                asset_type="whatsapp_button",
                pain_ids=["no_whatsapp_visible"],
                confidence_required=0.9,
                can_generate=True,
                reason="Verified"
            ),
            AssetSpec(
                asset_type="faq_page",
                pain_ids=["no_faq_schema"],
                confidence_required=0.7,
                can_generate=True,
                reason="Sufficient confidence"
            ),
            AssetSpec(
                asset_type="hotel_schema",
                pain_ids=["no_hotel_schema"],
                confidence_required=0.8,
                can_generate=True,
                reason="Schema detected"
            ),
        ]
        
        diagnostic = DiagnosticDocument(
            path="output/diagnostic.md",
            problems=[
                Pain(id="no_whatsapp_visible", name="Sin WhatsApp", description="No hay", severity="high", detected_by="validation", confidence=0.9),
                Pain(id="no_faq_schema", name="Sin FAQ", description="No hay", severity="medium", detected_by="schema", confidence=1.0),
                Pain(id="no_hotel_schema", name="Sin Schema", description="No hay", severity="medium", detected_by="schema", confidence=1.0),
            ],
            financial_impact=Scenario(
                monthly_loss_min=1000000,
                monthly_loss_max=3000000,
                probability=0.2,
                description="Realistic"
            ),
            generated_at=datetime.now().isoformat()
        )
        
        proposal = ProposalDocument(
            path="output/proposal.md",
            price_monthly=135000,
            assets_proposed=[],
            roi_projected=2.5,
            generated_at=datetime.now().isoformat()
        )
        
        validation = ValidationSummary(
            fields=[
                ValidatedField(field_name="whatsapp_number", value="+573001234567", confidence=ConfidenceLevel.VERIFIED, sources=["web", "gbp"], match_percentage=1.0, can_use_in_assets=True),
                ValidatedField(field_name="adr_cop", value=350000, confidence=ConfidenceLevel.VERIFIED, sources=["web"], match_percentage=1.0, can_use_in_assets=True),
                ValidatedField(field_name="rooms", value=25, confidence=ConfidenceLevel.VERIFIED, sources=["web"], match_percentage=1.0, can_use_in_assets=True),
                ValidatedField(field_name="occupancy_rate", value=0.75, confidence=ConfidenceLevel.VERIFIED, sources=["web"], match_percentage=1.0, can_use_in_assets=True),
                ValidatedField(field_name="direct_channel_percentage", value=0.30, confidence=ConfidenceLevel.VERIFIED, sources=["web"], match_percentage=1.0, can_use_in_assets=True),
            ],
            overall_confidence=ConfidenceLevel.VERIFIED
        )
        
        validator = CoherenceValidator(confidence_threshold=0.7)
        report = validator.validate(diagnostic, proposal, assets, validation)
        
        # Encontrar el check específico
        promised_check = next((c for c in report.checks if c.name == "promised_assets_exist"), None)
        assert promised_check is not None, "Check promised_assets_exist no encontrado"
        assert promised_check.passed is True, f"Check debería pasar pero: {promised_check.message}"
        assert promised_check.severity == "info"
    
    def test_promised_assets_exist_fail(self):
        """Test que el check falla cuando hay asset no implementado."""
        # Un asset que NO está implementado (MISSING en el catálogo)
        assets = [
            AssetSpec(
                asset_type="nonexistent_asset_12345",
                pain_ids=["poor_performance"],
                confidence_required=0.7,
                can_generate=False,
                reason="Not implemented in catalog"
            ),
            AssetSpec(
                asset_type="whatsapp_button",
                pain_ids=["no_whatsapp_visible"],
                confidence_required=0.9,
                can_generate=True,
                reason="Verified"
            ),
        ]
        
        diagnostic = DiagnosticDocument(
            path="output/diagnostic.md",
            problems=[
                Pain(id="poor_performance", name="Baja Performance", description="Lenta", severity="high", detected_by="validation", confidence=0.9),
                Pain(id="no_whatsapp_visible", name="Sin WhatsApp", description="No hay", severity="high", detected_by="validation", confidence=0.9),
            ],
            financial_impact=Scenario(
                monthly_loss_min=1000000,
                monthly_loss_max=3000000,
                probability=0.2,
                description="Realistic"
            ),
            generated_at=datetime.now().isoformat()
        )
        
        proposal = ProposalDocument(
            path="output/proposal.md",
            price_monthly=135000,
            assets_proposed=[],
            roi_projected=2.5,
            generated_at=datetime.now().isoformat()
        )
        
        validation = ValidationSummary(
            fields=[
                ValidatedField(field_name="whatsapp_number", value="+573001234567", confidence=ConfidenceLevel.VERIFIED, sources=["web", "gbp"], match_percentage=1.0, can_use_in_assets=True),
                ValidatedField(field_name="adr_cop", value=350000, confidence=ConfidenceLevel.VERIFIED, sources=["web"], match_percentage=1.0, can_use_in_assets=True),
                ValidatedField(field_name="rooms", value=25, confidence=ConfidenceLevel.VERIFIED, sources=["web"], match_percentage=1.0, can_use_in_assets=True),
                ValidatedField(field_name="occupancy_rate", value=0.75, confidence=ConfidenceLevel.VERIFIED, sources=["web"], match_percentage=1.0, can_use_in_assets=True),
                ValidatedField(field_name="direct_channel_percentage", value=0.30, confidence=ConfidenceLevel.VERIFIED, sources=["web"], match_percentage=1.0, can_use_in_assets=True),
            ],
            overall_confidence=ConfidenceLevel.VERIFIED
        )
        
        validator = CoherenceValidator(confidence_threshold=0.7)
        report = validator.validate(diagnostic, proposal, assets, validation)
        
        # Encontrar el check específico
        promised_check = next((c for c in report.checks if c.name == "promised_assets_exist"), None)
        assert promised_check is not None, "Check promised_assets_exist no encontrado"
        assert promised_check.passed is False, "Check debería fallar porque hay asset no implementado"
        assert promised_check.severity == "error", "Severidad debe ser error (blocking)"
        assert "nonexistent_asset_12345" in promised_check.message, "Mensaje debe mencionar el asset faltante"
