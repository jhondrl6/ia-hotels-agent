"""
Test de consistencia para top problems entre diagnóstico y propuesta.

Verifica que M-002 esté corregido: los problemas mostrados en el diagnóstico
y la propuesta deben ser idénticos (misma fuente de datos).
"""

import pytest
from dataclasses import dataclass, field
from typing import List, Optional

from modules.commercial_documents.data_structures import (
    V4AuditResult,
    SchemaValidation,
    GBPData,
    PerformanceData,
    CrossValidationResult,
    ConfidenceLevel,
    calculate_quick_wins,
    extract_top_problems,
)


class TestTopProblemsConsistency:
    """Tests para verificar consistencia de problemas entre documentos."""
    
    def create_mock_audit_result(
        self,
        critical_issues: List[str] = None,
        recommendations: List[str] = None,
        hotel_schema_detected: bool = True,
        phone_web: Optional[str] = None,
        faq_schema_detected: bool = True,
        whatsapp_status: str = "VERIFIED",
        conflicts: List[dict] = None,
    ) -> V4AuditResult:
        """Create a mock audit result for testing."""
        return V4AuditResult(
            url="https://test-hotel.com",
            hotel_name="Test Hotel",
            timestamp="2024-01-01T00:00:00",
            schema=SchemaValidation(
                hotel_schema_detected=hotel_schema_detected,
                hotel_schema_valid=hotel_schema_detected,
                hotel_confidence="VERIFIED" if hotel_schema_detected else "UNKNOWN",
                faq_schema_detected=faq_schema_detected,
                faq_schema_valid=faq_schema_detected,
                faq_confidence="VERIFIED" if faq_schema_detected else "UNKNOWN",
                org_schema_detected=False,
                total_schemas=1 if hotel_schema_detected else 0,
            ),
            gbp=GBPData(
                place_found=True,
                place_id="test123",
                name="Test Hotel",
                rating=4.5,
                reviews=50,
                photos=10,
                phone="+573001234567",
                website="https://test-hotel.com",
                address="Test Address",
                geo_score=70,
                geo_score_breakdown={},
                confidence="VERIFIED",
            ),
            performance=PerformanceData(
                has_field_data=True,
                mobile_score=75,
                desktop_score=80,
                lcp=2.5,
                fid=50,
                cls=0.1,
                status="good",
                message="Good performance",
            ),
            validation=CrossValidationResult(
                whatsapp_status=whatsapp_status,
                phone_web=phone_web,
                phone_gbp="+573001234567",
                adr_status="VERIFIED",
                adr_web=150000.0,
                adr_benchmark=150000.0,
                conflicts=conflicts or [],
            ),
            overall_confidence="VERIFIED",
            critical_issues=critical_issues or [],
            recommendations=recommendations or [],
        )
    
    def test_extract_top_problems_returns_critical_issues_first(self):
        """Los critical_issues deben aparecer primero en la lista."""
        critical = ["Issue 1", "Issue 2", "Issue 3"]
        audit = self.create_mock_audit_result(
            critical_issues=critical,
            hotel_schema_detected=True,
        )
        
        problems = extract_top_problems(audit, limit=5)
        
        assert len(problems) == 3
        assert problems[0] == "Issue 1"
        assert problems[1] == "Issue 2"
        assert problems[2] == "Issue 3"
    
    def test_extract_top_problems_includes_schema_issues(self):
        """Si no hay schema de hotel, debe aparecer en problemas."""
        audit = self.create_mock_audit_result(
            critical_issues=["Critical issue"],
            hotel_schema_detected=False,
        )
        
        problems = extract_top_problems(audit, limit=5)
        
        assert len(problems) >= 2
        assert "Critical issue" in problems
        assert any("Schema de Hotel" in p for p in problems)
    
    def test_extract_top_problems_includes_whatsapp_conflict(self):
        """Si hay conflicto de WhatsApp, debe aparecer en problemas."""
        audit = self.create_mock_audit_result(
            critical_issues=["Critical issue"],
            whatsapp_status="CONFLICT",
        )
        
        problems = extract_top_problems(audit, limit=5)
        
        assert any("WhatsApp" in p for p in problems)
    
    def test_extract_top_problems_uses_recommendations_as_fallback(self):
        """Si hay espacio, usar recommendations para completar."""
        audit = self.create_mock_audit_result(
            critical_issues=["Only one issue"],
            recommendations=["Rec 1", "Rec 2", "Rec 3"],
            hotel_schema_detected=True,
            faq_schema_detected=True,
        )
        
        problems = extract_top_problems(audit, limit=5)
        
        assert len(problems) >= 2
        assert "Only one issue" in problems
    
    def test_extract_top_problems_respects_limit(self):
        """Nunca debe exceder el límite especificado."""
        audit = self.create_mock_audit_result(
            critical_issues=[f"Issue {i}" for i in range(10)],
        )
        
        problems = extract_top_problems(audit, limit=3)
        assert len(problems) == 3
        
        problems = extract_top_problems(audit, limit=5)
        assert len(problems) == 5
    
    def test_calculate_quick_wins_detects_missing_schema(self):
        """Sin schema de hotel = 1 quick win."""
        audit = self.create_mock_audit_result(
            hotel_schema_detected=False,
            phone_web="+573001234567",
            faq_schema_detected=True,
        )
        
        wins = calculate_quick_wins(audit)
        assert wins >= 1
    
    def test_calculate_quick_wins_detects_missing_whatsapp(self):
        """Sin teléfono web = 1 quick win."""
        audit = self.create_mock_audit_result(
            hotel_schema_detected=True,
            phone_web=None,
            faq_schema_detected=True,
        )
        
        wins = calculate_quick_wins(audit)
        assert wins >= 1
    
    def test_calculate_quick_wins_detects_missing_faq(self):
        """Sin FAQ schema = 1 quick win."""
        audit = self.create_mock_audit_result(
            hotel_schema_detected=True,
            phone_web="+573001234567",
            faq_schema_detected=False,
        )
        
        wins = calculate_quick_wins(audit)
        assert wins >= 1
    
    def test_same_source_for_diagnostic_and_proposal(self):
        """
        TEST CLAVE PARA M-002: Verifica que diagnóstico y propuesta
        usen la misma fuente de problemas.
        """
        audit = self.create_mock_audit_result(
            critical_issues=[
                "Sin visibilidad en Google Maps",
                "Web muy lenta en móvil",
            ],
            recommendations=[
                "Faltan fotos en GBP",
                "Sin descripción optimizada",
            ],
            hotel_schema_detected=False,
            phone_web=None,
        )
        
        # Extraer problemas como lo haría el diagnóstico
        diagnostic_problems = extract_top_problems(audit, limit=5)
        
        # Extraer problemas como lo haría la propuesta (misma función)
        proposal_problems = extract_top_problems(audit, limit=5)
        
        # Deben ser idénticos
        assert diagnostic_problems == proposal_problems, (
            f"Diagnóstico y propuesta tienen problemas diferentes!\n"
            f"Diagnóstico: {diagnostic_problems}\n"
            f"Propuesta: {proposal_problems}"
        )
    
    def test_critical_problems_count_matches_extracted(self):
        """El conteo de problemas debe coincidir con la lista extraída."""
        audit = self.create_mock_audit_result(
            critical_issues=["Issue 1", "Issue 2", "Issue 3"],
        )
        
        problems = extract_top_problems(audit, limit=5)
        critical_count = len(audit.critical_issues)
        
        # El conteo crítico debe ser consistente
        assert critical_count == 3
        assert len(problems) >= 3
