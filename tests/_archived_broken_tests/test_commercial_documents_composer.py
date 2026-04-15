"""Tests de sincronización Diagnóstico vs Propuesta para la Fase 4 de Composición Documental.

Este módulo contiene tests que verifican que los documentos comerciales
generados (diagnóstico y propuesta) mantengan sincronización consistente
con el CanonicalAssessment fuente.

Tests incluidos:
    - Sincronización de assessment_id y claim_ids
    - Consistencia de status (WhatsApp, GBP, Schema)
    - Disclaimers según nivel de confianza
    - Estados de publicación basados en criterios objetivos
    - Determinismo del composer
"""

import pytest
from datetime import datetime
from uuid import UUID, uuid4

from commercial_documents.composer import DocumentComposer, Document
from data_models.canonical_assessment import (
    CanonicalAssessment,
    SiteMetadata,
    SchemaAnalysis,
    PerformanceAnalysis,
    PerformanceMetrics,
    GBPAnalysis,
    Claim,
)
from enums.severity import Severity


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def sample_assessment():
    """Crea un CanonicalAssessment de ejemplo con claims variados.
    
    Returns:
        CanonicalAssessment con:
        - URL: https://hotelvisperas.com
        - 4 claims (1 CRITICAL, 1 HIGH, 1 MEDIUM, 1 LOW)
        - coherence_score: 0.85
        - evidence_coverage: 0.95
        - hard_contradictions: 0
    """
    claims = [
        Claim(
            source_id="web_scraping",
            evidence_excerpt="<title>Hotel Vísperas | My WordPress Blog</title>",
            severity=Severity.CRITICAL,
            category="metadata",
            message="Título con tagline por defecto de WordPress",
            confidence=0.95,
        ),
        Claim(
            source_id="schema_validator",
            evidence_excerpt='{"@type": "Hotel", "name": "Hotel Vísperas"}',
            severity=Severity.HIGH,
            category="schema",
            message="Falta campo aggregateRating en Schema.org",
            confidence=0.90,
        ),
        Claim(
            source_id="performance_api",
            evidence_excerpt='{"lcp": 2.5, "fcp": 1.2}',
            severity=Severity.MEDIUM,
            category="performance",
            message="LCP ligeramente elevado en móvil",
            confidence=0.85,
        ),
        Claim(
            source_id="gbp_api",
            evidence_excerpt='{"rating": 4.5, "reviews": 12}',
            severity=Severity.LOW,
            category="gbp",
            message="Pocas reseñas en Google Business Profile",
            confidence=0.95,
        ),
    ]
    
    return CanonicalAssessment(
        url="https://hotelvisperas.com",
        site_metadata=SiteMetadata(
            title="Hotel Vísperas - Oaxaca",
            description="Hotel boutique en el centro histórico de Oaxaca",
            cms_detected="WordPress",
            has_default_title=True,
            detected_language="es",
            viewport_meta=True,
        ),
        schema_analysis=SchemaAnalysis(
            schema_type="Hotel",
            coverage_score=0.6,
            missing_critical_fields=["image", "aggregateRating"],
            present_fields=["name", "address", "telephone"],
            has_hotel_schema=True,
        ),
        performance_analysis=PerformanceAnalysis(
            performance_score=65.0,
            metrics=PerformanceMetrics(lcp=2.5, fcp=1.2, cls=0.05),
        ),
        gbp_analysis=GBPAnalysis(
            profile_url="https://g.page/hotelvisperas",
            rating=4.5,
            review_count=12,
            is_claimed=True,
        ),
        claims=claims,
        coherence_score=0.85,
        evidence_coverage=0.95,
        hard_contradictions=0,
    )


@pytest.fixture
def assessment_with_conflicts():
    """Crea un Assessment con claims en conflicto.
    
    Returns:
        CanonicalAssessment con:
        - Un claim CONFLICT (confidence < 0.5)
        - hard_contradictions: 1
        - coherence_score: 0.6
    """
    claims = [
        Claim(
            source_id="web_scraping",
            evidence_excerpt="<title>Hotel Vísperas</title>",
            severity=Severity.HIGH,
            category="metadata",
            message="Título del sitio web",
            confidence=0.95,
        ),
        Claim(
            source_id="gbp_api",
            evidence_excerpt='{"name": "Hotel Las Vísperas"}',
            severity=Severity.HIGH,
            category="gbp",
            message="Nombre en GBP difiere del sitio web",
            confidence=0.40,  # CONFLICT level
        ),
    ]
    
    return CanonicalAssessment(
        url="https://hotelvisperas.com",
        site_metadata=SiteMetadata(
            title="Hotel Vísperas",
            description="Hotel boutique",
            cms_detected="WordPress",
        ),
        schema_analysis=SchemaAnalysis(
            coverage_score=0.5,
            missing_critical_fields=["image"],
            present_fields=["name"],
        ),
        performance_analysis=PerformanceAnalysis(
            performance_score=55.0,
            metrics=PerformanceMetrics(lcp=3.0, fcp=1.5),
        ),
        claims=claims,
        coherence_score=0.6,
        evidence_coverage=0.80,
        hard_contradictions=1,
    )


@pytest.fixture
def assessment_low_coherence():
    """Crea un Assessment con baja coherencia.
    
    Returns:
        CanonicalAssessment con:
        - coherence_score: 0.5 (< 0.8)
        - Sin contradicciones duras
    """
    claims = [
        Claim(
            source_id="web_scraping",
            evidence_excerpt="<title>Hotel Example</title>",
            severity=Severity.MEDIUM,
            category="metadata",
            message="Metadatos básicos presentes",
            confidence=0.70,
        ),
    ]
    
    return CanonicalAssessment(
        url="https://hotelexample.com",
        site_metadata=SiteMetadata(
            title="Hotel Example",
            description="Un hotel de ejemplo",
            cms_detected="WordPress",
        ),
        schema_analysis=SchemaAnalysis(
            coverage_score=0.3,
            missing_critical_fields=["image", "priceRange", "aggregateRating"],
            present_fields=["name"],
        ),
        performance_analysis=PerformanceAnalysis(
            performance_score=45.0,
            metrics=PerformanceMetrics(lcp=4.0, fcp=2.0),
        ),
        claims=claims,
        coherence_score=0.5,
        evidence_coverage=0.60,
        hard_contradictions=0,
    )


@pytest.fixture
def composer():
    """Crea una instancia de DocumentComposer para testing."""
    return DocumentComposer(version="4.2.0")


# =============================================================================
# TESTS DE SINCRONIZACIÓN
# =============================================================================


class TestSynchronization:
    """Tests de sincronización entre diagnóstico y propuesta."""
    
    def test_diagnostico_and_propuesta_same_assessment_id(
        self, composer, sample_assessment
    ):
        """Verifica que ambos documentos usen el mismo assessment_id."""
        diagnostico = composer.compose_diagnostico(sample_assessment)
        propuesta = composer.compose_propuesta(sample_assessment)
        
        assert diagnostico.assessment_id == sample_assessment.assessment_id
        assert propuesta.assessment_id == sample_assessment.assessment_id
        assert diagnostico.assessment_id == propuesta.assessment_id
    
    def test_diagnostico_and_propuesta_same_claim_ids(
        self, composer, sample_assessment
    ):
        """Verifica que ambos documentos incluyan los mismos claim_ids."""
        diagnostico = composer.compose_diagnostico(sample_assessment)
        propuesta = composer.compose_propuesta(sample_assessment)
        
        # Ambos deben tener los mismos claim_ids
        assert sorted(diagnostico.claim_ids) == sorted(propuesta.claim_ids)
        
        # Deben incluir todos los claims del assessment
        assessment_claim_ids = [c.claim_id for c in sample_assessment.claims]
        assert sorted(diagnostico.claim_ids) == sorted(assessment_claim_ids)
    
    def test_whatsapp_status_consistent(self, composer):
        """Verifica que el status de WhatsApp sea consistente en ambos documentos."""
        # Crear assessment con claim de WhatsApp VERIFIED
        whatsapp_claim = Claim(
            source_id="validation_cruzada",
            evidence_excerpt='{"whatsapp": "+5219511234567", "match": true}',
            severity=Severity.HIGH,
            category="whatsapp",
            message="Número de WhatsApp verificado: coincide en web y GBP",
            confidence=0.95,
        )
        
        assessment = CanonicalAssessment(
            url="https://hoteltest.com",
            site_metadata=SiteMetadata(
                title="Hotel Test",
                description="Test",
            ),
            schema_analysis=SchemaAnalysis(
                coverage_score=0.5,
                missing_critical_fields=[],
                present_fields=["name"],
            ),
            performance_analysis=PerformanceAnalysis(
                performance_score=70.0,
                metrics=PerformanceMetrics(),
            ),
            claims=[whatsapp_claim],
            coherence_score=0.90,
            evidence_coverage=0.95,
            hard_contradictions=0,
        )
        
        diagnostico = composer.compose_diagnostico(assessment)
        propuesta = composer.compose_propuesta(assessment)
        
        # Ambos documentos deben incluir el claim de WhatsApp
        assert whatsapp_claim.claim_id in diagnostico.claim_ids
        assert whatsapp_claim.claim_id in propuesta.claim_ids
        
        # El contenido debe mencionar WhatsApp
        assert "WhatsApp" in diagnostico.content or "whatsapp" in diagnostico.content.lower()
        assert "WhatsApp" in propuesta.content
    
    def test_gbp_status_consistent(self, composer):
        """Verifica que el status de GBP sea consistente en ambos documentos."""
        # Crear assessment con GBP analysis y claims
        gbp_claim = Claim(
            source_id="gbp_api",
            evidence_excerpt='{"is_claimed": true, "rating": 4.5}',
            severity=Severity.MEDIUM,
            category="gbp",
            message="Perfil de GBP verificado y activo",
            confidence=0.90,
        )
        
        assessment = CanonicalAssessment(
            url="https://hoteltest.com",
            site_metadata=SiteMetadata(
                title="Hotel Test",
                description="Test",
            ),
            schema_analysis=SchemaAnalysis(
                coverage_score=0.5,
                missing_critical_fields=[],
                present_fields=["name"],
            ),
            performance_analysis=PerformanceAnalysis(
                performance_score=70.0,
                metrics=PerformanceMetrics(),
            ),
            gbp_analysis=GBPAnalysis(
                profile_url="https://g.page/hoteltest",
                rating=4.5,
                review_count=25,
                is_claimed=True,
            ),
            claims=[gbp_claim],
            coherence_score=0.90,
            evidence_coverage=0.95,
            hard_contradictions=0,
        )
        
        diagnostico = composer.compose_diagnostico(assessment)
        propuesta = composer.compose_propuesta(assessment)
        
        # Ambos deben incluir el claim de GBP
        assert gbp_claim.claim_id in diagnostico.claim_ids
        assert gbp_claim.claim_id in propuesta.claim_ids
        
        # La propuesta debe mencionar GBP
        assert "Google Business Profile" in propuesta.content
    
    def test_schema_presence_consistent(self, composer, sample_assessment):
        """Verifica que la cobertura de schema sea consistente."""
        diagnostico = composer.compose_diagnostico(sample_assessment)
        propuesta = composer.compose_propuesta(sample_assessment)
        
        # Ambos documentos deben mencionar el coherence_score
        assert "0.85" in diagnostico.content
        assert "0.85" in propuesta.content
        
        # El schema debe mencionarse en ambos
        assert "Schema" in diagnostico.content or "schema" in diagnostico.content.lower()


# =============================================================================
# TESTS DE DISCLAIMERS
# =============================================================================


class TestDisclaimers:
    """Tests de disclaimers según nivel de confianza."""
    
    def test_disclaimers_for_estimated_data(self, composer):
        """Verifica que se incluya disclaimer para datos ESTIMATED."""
        # Crear assessment con claims ESTIMATED (confidence 0.7)
        estimated_claim = Claim(
            source_id="benchmark_regional",
            evidence_excerpt="Estimación basada en benchmark de hoteles similares",
            severity=Severity.MEDIUM,
            category="metadata",
            message="ADR estimado basado en benchmark regional",
            confidence=0.70,  # ESTIMATED level
        )
        
        assessment = CanonicalAssessment(
            url="https://hoteltest.com",
            site_metadata=SiteMetadata(
                title="Hotel Test",
                description="Test",
            ),
            schema_analysis=SchemaAnalysis(
                coverage_score=0.5,
                missing_critical_fields=[],
                present_fields=["name"],
            ),
            performance_analysis=PerformanceAnalysis(
                performance_score=70.0,
                metrics=PerformanceMetrics(),
            ),
            claims=[estimated_claim],
            coherence_score=0.85,
            evidence_coverage=0.80,
            hard_contradictions=0,
        )
        
        diagnostico = composer.compose_diagnostico(assessment)
        
        # Debe incluir disclaimer de datos estimados
        assert len(diagnostico.disclaimers) > 0
        assert any("ESTIMATED" in d or "estimados" in d.lower() for d in diagnostico.disclaimers)
    
    def test_disclaimers_for_conflict_data(self, composer):
        """Verifica disclaimer para datos en conflicto."""
        # Usar fixture de conflicto
        conflict_claim = Claim(
            source_id="validation_cruzada",
            evidence_excerpt="Conflicto entre fuentes",
            severity=Severity.HIGH,
            category="metadata",
            message="Conflicto en nombre del hotel entre fuentes",
            confidence=0.40,  # CONFLICT level
        )
        
        assessment = CanonicalAssessment(
            url="https://hoteltest.com",
            site_metadata=SiteMetadata(
                title="Hotel Test",
                description="Test",
            ),
            schema_analysis=SchemaAnalysis(
                coverage_score=0.5,
                missing_critical_fields=[],
                present_fields=["name"],
            ),
            performance_analysis=PerformanceAnalysis(
                performance_score=70.0,
                metrics=PerformanceMetrics(),
            ),
            claims=[conflict_claim],
            coherence_score=0.85,
            evidence_coverage=0.80,
            hard_contradictions=0,
        )
        
        diagnostico = composer.compose_diagnostico(assessment)
        
        # Debe incluir disclaimer de conflicto
        assert len(diagnostico.disclaimers) > 0
        assert any("CONFLICT" in d or "conflicto" in d.lower() for d in diagnostico.disclaimers)
    
    def test_evidence_format_in_claims(self, composer, sample_assessment):
        """Verifica formato de evidencia: fuente + timestamp + excerpt."""
        diagnostico = composer.compose_diagnostico(sample_assessment)
        
        # El contenido debe incluir formato de evidencia
        assert "Fuente:" in diagnostico.content
        assert "Timestamp:" in diagnostico.content
        assert "Excerpt:" in diagnostico.content
        
        # Debe incluir los source_ids de los claims
        for claim in sample_assessment.claims:
            assert claim.source_id in diagnostico.content


# =============================================================================
# TESTS DE PUBLICACIÓN
# =============================================================================


class TestPublicationStatus:
    """Tests de estados de publicación."""
    
    def test_ready_for_client_when_high_coherence_no_conflicts(
        self, composer, sample_assessment
    ):
        """coherence >= 0.8 AND hard_contradictions == 0 -> READY_FOR_CLIENT."""
        assert sample_assessment.coherence_score >= 0.8
        assert sample_assessment.hard_contradictions == 0
        
        diagnostico = composer.compose_diagnostico(sample_assessment)
        propuesta = composer.compose_propuesta(sample_assessment)
        
        assert diagnostico.publication_status == "READY_FOR_CLIENT"
        assert propuesta.publication_status == "READY_FOR_CLIENT"
    
    def test_draft_internal_when_low_coherence(
        self, composer, assessment_low_coherence
    ):
        """coherence < 0.8 -> DRAFT_INTERNAL."""
        assert assessment_low_coherence.coherence_score < 0.8
        
        diagnostico = composer.compose_diagnostico(assessment_low_coherence)
        propuesta = composer.compose_propuesta(assessment_low_coherence)
        
        assert diagnostico.publication_status == "DRAFT_INTERNAL"
        assert propuesta.publication_status == "DRAFT_INTERNAL"
    
    def test_draft_internal_when_hard_conflicts(
        self, composer, assessment_with_conflicts
    ):
        """hard_contradictions > 0 -> DRAFT_INTERNAL."""
        assert assessment_with_conflicts.hard_contradictions > 0
        
        diagnostico = composer.compose_diagnostico(assessment_with_conflicts)
        propuesta = composer.compose_propuesta(assessment_with_conflicts)
        
        # Como tiene hard_contradictions, debe ser DRAFT_INTERNAL
        assert diagnostico.publication_status == "DRAFT_INTERNAL"
        assert propuesta.publication_status == "DRAFT_INTERNAL"
    
    def test_requires_review_when_soft_conflicts(self, composer):
        """Tiene claims CONFLICT pero coherence >= 0.8 -> REQUIRES_REVIEW."""
        # Crear assessment con claim CONFLICT pero alta coherencia
        conflict_claim = Claim(
            source_id="validation_cruzada",
            evidence_excerpt="Conflicto detectado",
            severity=Severity.MEDIUM,
            category="metadata",
            message="Diferencia menor entre fuentes",
            confidence=0.40,  # CONFLICT level
        )
        
        verified_claim = Claim(
            source_id="web_scraping",
            evidence_excerpt="<title>Hotel Test</title>",
            severity=Severity.LOW,
            category="metadata",
            message="Título verificado",
            confidence=0.95,
        )
        
        assessment = CanonicalAssessment(
            url="https://hoteltest.com",
            site_metadata=SiteMetadata(
                title="Hotel Test",
                description="Test",
            ),
            schema_analysis=SchemaAnalysis(
                coverage_score=0.8,
                missing_critical_fields=[],
                present_fields=["name", "address"],
            ),
            performance_analysis=PerformanceAnalysis(
                performance_score=85.0,
                metrics=PerformanceMetrics(lcp=1.5, fcp=0.8),
            ),
            claims=[conflict_claim, verified_claim],
            coherence_score=0.85,  # >= 0.8
            evidence_coverage=0.90,
            hard_contradictions=0,  # No hard contradictions
        )
        
        diagnostico = composer.compose_diagnostico(assessment)
        
        # Como tiene claims CONFLICT pero alta coherencia y no hard_contradictions
        assert diagnostico.publication_status == "REQUIRES_REVIEW"


# =============================================================================
# TESTS DE DETERMINISMO
# =============================================================================


class TestDeterminism:
    """Tests de determinismo del composer."""
    
    def test_composer_is_deterministic(self, composer, sample_assessment):
        """Ejecuta compose_diagnostico dos veces y verifica contenido idéntico."""
        # Ejecutar dos veces con el mismo assessment
        doc1 = composer.compose_diagnostico(sample_assessment)
        doc2 = composer.compose_diagnostico(sample_assessment)
        
        # El contenido debe ser idéntico
        assert doc1.content == doc2.content
        
        # Los metadatos también deben coincidir
        assert doc1.claim_ids == doc2.claim_ids
        assert doc1.disclaimers == doc2.disclaimers
        assert doc1.publication_status == doc2.publication_status
        assert doc1.assessment_id == doc2.assessment_id
    
    def test_propuesta_is_deterministic(self, composer, sample_assessment):
        """Ejecuta compose_propuesta dos veces y verifica contenido idéntico."""
        # Ejecutar dos veces
        doc1 = composer.compose_propuesta(sample_assessment)
        doc2 = composer.compose_propuesta(sample_assessment)
        
        # El contenido debe ser idéntico (excepto timestamp si lo tuviera)
        # Nota: la propuesta incluye proposal_date con datetime.utcnow()
        # Por eso comparamos todo excepto la fecha
        assert doc1.claim_ids == doc2.claim_ids
        assert doc1.disclaimers == doc2.disclaimers
        assert doc1.publication_status == doc2.publication_status
        
        # El assessment_id debe ser el mismo
        assert doc1.assessment_id == doc2.assessment_id


# =============================================================================
# TESTS ADICIONALES DE ESTRUCTURA
# =============================================================================


class TestDocumentStructure:
    """Tests de estructura y contenido de documentos."""
    
    def test_diagnostico_has_all_sections(self, composer, sample_assessment):
        """Verifica que el diagnóstico tenga todas las secciones requeridas."""
        doc = composer.compose_diagnostico(sample_assessment)
        
        # Secciones requeridas
        required_sections = [
            "# Diagnóstico de Presencia Digital",
            "## Resumen Ejecutivo",
            "## 1. Metadatos del Sitio",
            "## 2. Análisis de Schema.org",
            "## 3. Análisis de Performance",
            "## 4. Google Business Profile",
            "## Claims por Severidad",
            "## Evidencia Detallada",
        ]
        
        for section in required_sections:
            assert section in doc.content, f"Falta sección: {section}"
    
    def test_propuesta_has_all_sections(self, composer, sample_assessment):
        """Verifica que la propuesta tenga todas las secciones requeridas."""
        doc = composer.compose_propuesta(sample_assessment)
        
        # Secciones requeridas
        required_sections = [
            "# Propuesta Comercial",
            "## Resumen Ejecutivo",
            "## Situación Actual",
            "## Oportunidades Identificadas",
            "## Propuesta de Valor",
            "## Inversión y Escenarios",
            "## Siguientes Pasos",
        ]
        
        for section in required_sections:
            assert section in doc.content, f"Falta sección: {section}"
    
    def test_document_version(self, composer, sample_assessment):
        """Verifica que los documentos incluyan la versión correcta."""
        diagnostico = composer.compose_diagnostico(sample_assessment)
        propuesta = composer.compose_propuesta(sample_assessment)
        
        assert diagnostico.version == "4.2.0"
        assert propuesta.version == "4.2.0"
        
        # La versión debe aparecer en el contenido
        assert "4.2.0" in diagnostico.content
        assert "4.2.0" in propuesta.content
    
    def test_claim_count_matches(self, composer, sample_assessment):
        """Verifica que el conteo de claims sea correcto."""
        doc = composer.compose_diagnostico(sample_assessment)
        
        # El número de claim_ids debe coincidir con el assessment
        assert len(doc.claim_ids) == len(sample_assessment.claims)
        
        # El summary debe tener el conteo correcto
        summary = doc.get_summary()
        assert summary["claim_count"] == len(sample_assessment.claims)
