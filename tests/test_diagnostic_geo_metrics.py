"""
Tests para integración de métricas GEO en V4DiagnosticGenerator (Fase 3)

La cabecera de la sección no la emite la tabla: el fix N1 de la release v4.36.0
(commit 7daec91) retiró el header duplicado del generador y dejó que la plantilla
lo proveyera. Las aserciones de este archivo están re-ancladas a esa forma emitida,
y el diente `test_geo_section_survives_end_to_end_render` falla por PÉRDIDA de la
sección (tabla huérfana o desaparecida), no por cambio literal del título.
"""
import re
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.commercial_documents.v4_diagnostic_generator import V4DiagnosticGenerator
from modules.commercial_documents.data_structures import (
    ConfidenceLevel,
    CrossValidationResult,
    FinancialScenarios,
    GBPData,
    PerformanceData,
    Scenario,
    SchemaValidation,
    V4AuditResult,
    ValidatedField,
    ValidationSummary,
)
from unittest.mock import Mock

# Titulo que emite la plantilla para la seccion de metricas de IA
GEO_SECTION_TITLE = "### Métricas de Acceso para IA"

# Las tres filas que la tabla debe conservar
GEO_ROW_LABELS = ("Accesibilidad IA", "Citabilidad", "IA-Readiness")


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


def _generator(**kwargs) -> V4DiagnosticGenerator:
    """Costura unica de construccion: los mutantes la sustituyen, el producto no."""
    return V4DiagnosticGenerator(**kwargs)


class _MockAuditGEOMetrics:
    """Audit con los tres datos GEO, sin MagicMock, para la asercion re-anclada."""

    def __init__(self):
        self.ai_crawlers = MockAICrawlerAuditResult()
        self.citability = MockCitabilityResult()
        self.ia_readiness = MockIAReadinessReport()


def _make_audit_with_geo() -> V4AuditResult:
    """Audit completo con los tres datos GEO para un render real."""
    audit = V4AuditResult(
        url="https://example.com",
        hotel_name="Hotel Prueba",
        timestamp="2026-01-01T00:00:00",
        schema=SchemaValidation(
            hotel_schema_detected=True,
            hotel_schema_valid=True,
            hotel_confidence="verified",
            faq_schema_detected=True,
            faq_schema_valid=True,
            faq_confidence="verified",
            org_schema_detected=True,
            total_schemas=3,
        ),
        gbp=GBPData(
            place_found=True,
            place_id="ChI123",
            name="Hotel Prueba",
            rating=4.5,
            reviews=100,
            photos=30,
            phone="+571234567890",
            website="https://example.com",
            address="Calle 123, Ciudad, Colombia",
            geo_score=80,
            geo_score_breakdown={},
            confidence="verified",
        ),
        performance=PerformanceData(
            has_field_data=True,
            mobile_score=85,
            desktop_score=90,
            lcp=1.5,
            fid=20,
            cls=0.05,
            status="ok",
            message="Good performance",
        ),
        validation=CrossValidationResult(
            whatsapp_status="verified",
            phone_web="+571234567890",
            phone_gbp="+571234567890",
            adr_status="verified",
            adr_web=300000.0,
            adr_benchmark=280000.0,
        ),
        overall_confidence="verified",
        critical_issues=[],
        recommendations=[],
    )
    audit.ai_crawlers = MockAICrawlerAuditResult(overall_score=0.50, blocked_crawlers=["GPTBot"] * 14)
    audit.citability = MockCitabilityResult(overall_score=57.4, blocks_analyzed=21)
    audit.ia_readiness = MockIAReadinessReport(overall_score=73.8, status="Ready")
    return audit


def _render_diagnostic() -> str:
    """Render real del diagnostico completo (generador + plantilla)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        path = _generator().generate(
            audit_result=_make_audit_with_geo(),
            validation_summary=ValidationSummary(
                fields=[
                    ValidatedField(
                        field_name="rooms",
                        value=10,
                        confidence=ConfidenceLevel.VERIFIED,
                        sources=["onboarding"],
                    ),
                ],
                overall_confidence=ConfidenceLevel.VERIFIED,
                conflicts=[],
            ),
            financial_scenarios=FinancialScenarios(
                conservative=_scenario(),
                realistic=_scenario(),
                optimistic=_scenario(),
            ),
            hotel_name="Hotel Prueba",
            hotel_url="https://example.com",
            output_dir=tmpdir,
            coherence_score=0.85,
            gate_status="PASSED",
        )
        return Path(path).read_text(encoding="utf-8")


def _scenario() -> Scenario:
    return Scenario(
        monthly_loss_min=1_000_000,
        monthly_loss_max=2_000_000,
        probability=0.7,
        description="Test scenario",
        assumptions=["Assumption 1"],
        confidence_score=0.8,
        monthly_loss_central=1_500_000,
    )


def _geo_section_window(doc: str) -> Optional[Dict[str, Any]]:
    """Ventana GEO ubicada por el DATO, no por el titulo.

    Devuelve None si la tabla no esta en el documento (perdida por dato).
    Devuelve `heading=False` si lo que antecede a la tabla no es un encabezado
    (perdida por titulo: la tabla quedo huerfana).
    """
    lines = doc.splitlines()
    first_row = next(
        (i for i, l in enumerate(lines) if l.startswith(f"| {GEO_ROW_LABELS[0]} |")),
        None,
    )
    if first_row is None:
        return None

    # Subir al inicio del bloque de tabla (encabezado y separador tambien empiezan por '|')
    start = first_row
    while start - 1 >= 0 and lines[start - 1].lstrip().startswith("|"):
        start -= 1

    title_idx = next((i for i in range(start - 1, -1, -1) if lines[i].strip()), None)
    title_line = lines[title_idx] if title_idx is not None else ""
    is_heading = bool(re.match(r"^#{2,6}\s+\S", title_line))

    end_idx = next(
        (i for i in range(first_row, len(lines)) if re.match(r"^#{2,6}\s+\S", lines[i])),
        len(lines),
    )
    return {
        "title_line": title_line,
        "heading": is_heading,
        "window": "\n".join(lines[title_idx:end_idx]) if title_idx is not None else "",
    }


# Tests
class TestDiagnosticGEOMetrics:
    """Tests para métricas GEO en diagnóstico."""

    def test_diagnostic_includes_geo_metrics(self):
        """La tabla emite las tres metricas bajo la forma vigente del producto."""
        result = _generator()._build_geo_problems_table(_MockAuditGEOMetrics())

        assert "Accesibilidad IA" in result
        assert "Citabilidad" in result
        assert "IA-Readiness" in result

        # N1 (7daec91): el header duplicado del generador fue retirado y no debe volver.
        assert "## [NEW]" not in result
        assert "Métricas de Optimización para IA" not in result

    def test_diagnostic_excludes_geo_when_no_data(self):
        """Test que verifica que NO hay sección GEO cuando no hay datos."""
        audit_result = Mock()
        audit_result.ai_crawlers = None
        audit_result.citability = None
        audit_result.ia_readiness = None

        result = _generator()._build_geo_problems_table(audit_result)

        assert result == ""

    def test_geo_scores_display_correctly(self):
        """Test que verifica que los scores GEO se muestran con formato correcto."""
        audit_result = Mock()
        audit_result.ai_crawlers = MockAICrawlerAuditResult(overall_score=0.50)
        audit_result.citability = MockCitabilityResult(overall_score=54.8)
        audit_result.ia_readiness = MockIAReadinessReport(overall_score=38.7)

        result = _generator()._build_geo_problems_table(audit_result)

        assert "0.50/1.00" in result  # ai_crawlers formato        assert "54.8/100" in result    # citability formato
        assert "38.7/100" in result    # ia_readiness formato

    def test_geo_section_survives_end_to_end_render(self):
        """Diente de PERDIDA: la seccion GEO llega completa al documento renderizado.

        Falla si la tabla desaparece, si queda huerfana de encabezado o si el
        placeholder no se resuelve. Sobrevive un puro renombre del titulo.
        """
        doc = _render_diagnostic()

        assert "${ia_metrics_table}" not in doc, "el placeholder no se resolvio"

        section = _geo_section_window(doc)
        assert section is not None, (
            "PERDIDA DE SECCION: ninguna fila de metricas GEO llega al documento"
        )
        assert section["heading"], (
            "PERDIDA DE SECCION: la tabla GEO quedo huerfana, no hay encabezado "
            f"que la encabece (anterior: {section['title_line']!r})"
        )
        for label in GEO_ROW_LABELS:
            assert label in section["window"], f"falta la fila {label} en la seccion"
        for score in ("0.50/1.00", "57.4/100", "73.8/100"):
            assert score in section["window"], f"falta el score {score} en la seccion"

        # N1 (7daec91): el header duplicado del generador no debe volver al documento.
        # Se comprueba por el retire, no por el titulo vigente, para que un renombre
        # legitimo de la seccion no ponga rojo este diente.
        assert "## [NEW]" not in doc

    def test_geo_section_title_is_emitted_by_the_product(self):
        """El titulo anclado arriba es el que emite el producto hoy, y solo una vez.

        Este test SI es sensible al renombre: es el registro del anclaje, no el diente
        de perdida. Quien renombre la seccion tiene que mover GEO_SECTION_TITLE aqui.
        """
        doc = _render_diagnostic()
        assert doc.count(GEO_SECTION_TITLE) == 1
