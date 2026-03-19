"""
Tests para integración de métricas GEO en V4DiagnosticGenerator (Fase 3)
"""
import pytest
from unittest.mock import Mock, patch
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

# Importar el generador
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.commercial_documents.v4_diagnostic_generator import V4DiagnosticGenerator
from modules.commercial_documents.data_structures import (
    ValidationSummary,
    FinancialScenarios,
    ConfidenceLevel,
)


# Mock classes para los datos GEO
@dataclass
class MockAICrawlerAuditResult:
    robots_exists: bool = True
    overall_score: float = 0.65
    allowed_crawlers: List[str] = field(default_factory=lambda: ["Googlebot"])
    blocked_crawlers: List[str] = field(default_factory=lambda: ["GPTBot", "CludeBot"])
    recommendations: List[str] = field(default_factory=list)


@dataclass
class MockCitabilityResult:
    overall_score: float = 54.8
    blocks_analyzed: int = 12
    high_citability_blocks: int = 5
    recommendations: List[str] = field(default_factory=list)
    confidence: str = "ADVISORY"


@dataclass
class MockIAReadinessReport:
    overall_score: float = 38.7
    components: Dict[str, float] = field(default_factory=lambda: {"schema": 50, "crawler": 40})
    status: str = "Needs Improvement"
    actionable_items: List[str] = field(default_factory=list)


# Tests
class TestDiagnosticGEOMetrics:
    """Tests para métricas GEO en diagnóstico."""
    
    def test_diagnostic_includes_geo_metrics(self):
        """Test que verifica que el diagnóstico incluye métricas GEO."""
        # Crear generador
        generator = V4DiagnosticGenerator()
        
        # Crear mock audit_result con datos GEO
        audit_result = Mock()
        audit_result.ai_crawlers = MockAICrawlerAuditResult()
        audit_result.citability = MockCitabilityResult()
        audit_result.ia_readiness = MockIAReadinessReport()
        
        # Llamar al método
        result = generator._build_geo_problems_table(audit_result)
        
        # Verificar que contiene las métricas
        assert "Métricas de Optimización para IA" in result
        assert "Accesibilidad IA" in result
        assert "Citabilidad" in result
        assert "IA-Readiness" in result
        
    def test_diagnostic_excludes_geo_when_no_data(self):
        """Test que verifica que NO hay sección GEO cuando no hay datos."""
        generator = V4DiagnosticGenerator()
        
        # Crear audit_result sin datos GEO
        audit_result = Mock()
        audit_result.ai_crawlers = None
        audit_result.citability = None
        audit_result.ia_readiness = None
        
        result = generator._build_geo_problems_table(audit_result)
        
        # Verificar que no contiene la sección
        assert result == ""
        
    def test_geo_scores_display_correctly(self):
        """Test que verifica que los scores GEO se muestran con formato correcto."""
        generator = V4DiagnosticGenerator()
        
        audit_result = Mock()
        audit_result.ai_crawlers = MockAICrawlerAuditResult(overall_score=0.50)
        audit_result.citability = MockCitabilityResult(overall_score=54.8)
        audit_result.ia_readiness = MockIAReadinessReport(overall_score=38.7)
        
        result = generator._build_geo_problems_table(audit_result)
        
        # Verificar formatos
        assert "0.50/1.00" in result  # ai_crawlers formato
        assert "54.8/100" in result    # citability formato
        assert "38.7/100" in result    # ia_readiness formato
