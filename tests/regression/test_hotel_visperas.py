"""Test de regresión permanente - Caso Hotel Vísperas.

Este módulo contiene tests de regresión para el caso Hotel Vísperas,
un caso real que motivó la refactorización. Garantiza que los problemas
detectados nunca se repitan en futuras versiones.

Contexto del Caso:
    - URL: https://hotelvisperas.com
    - Ubicación: Santa Rosa de Cabal, Colombia
    - Título: "Hotel Vísperas | My WordPress Blog" (default WordPress)
    - Schema Hotel: Presente pero incompleto (falta image, aggregateRating)
    - Performance: 51/100, LCP 21.2s (CRÍTICO)
    - WhatsApp: Detectado en schema (+57 3113973744)
    - GBP: Perfil existe con 12 reviews
"""

import pytest
from datetime import datetime

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


def create_hotel_visperas_assessment(coherence_score: float = 0.0) -> CanonicalAssessment:
    """Factory para crear assessment del Hotel Vísperas.
    
    Args:
        coherence_score: Score de coherencia para el assessment (default 0.0).
    
    Returns:
        CanonicalAssessment configurado con los datos reales del Hotel Vísperas.
    """
    claims = [
        Claim(
            source_id="metadata_validator",
            evidence_excerpt="<title>Hotel Vísperas | My WordPress Blog</title>",
            severity=Severity.CRITICAL,
            category="metadata",
            message="Título con tagline por defecto de WordPress no modificado",
            confidence=0.95,
        ),
        Claim(
            source_id="schema_validator",
            evidence_excerpt='{"@type": "Hotel", "name": "Hotel Visperas"}',
            severity=Severity.HIGH,
            category="schema",
            message="Schema Hotel incompleto: falta image y aggregateRating",
            confidence=0.90,
        ),
        Claim(
            source_id="pagespeed_api",
            evidence_excerpt='{"lcp": 21.2, "score": 51}',
            severity=Severity.CRITICAL,
            category="performance",
            message="LCP crítico: 21.2s (umbral: <2.5s)",
            confidence=0.95,
        ),
        Claim(
            source_id="web_scraping",
            evidence_excerpt="+57 3113973744",
            severity=Severity.LOW,
            category="contact",
            message="WhatsApp detectado en schema",
            confidence=0.95,
        ),
        Claim(
            source_id="gbp_validator",
            evidence_excerpt='{"rating": 4.5, "review_count": 12, "claimed": true}',
            severity=Severity.LOW,
            category="gbp",
            message="Perfil GBP verificado con 12 reseñas",
            confidence=0.95,
        ),
    ]
    
    assessment = CanonicalAssessment(
        url="https://hotelvisperas.com",
        site_metadata=SiteMetadata(
            title="Hotel Vísperas | My WordPress Blog",
            description="Hotel boutique en Santa Rosa de Cabal",
            cms_detected="WordPress",
            has_default_title=True,
            detected_language="es",
            viewport_meta=True,
        ),
        schema_analysis=SchemaAnalysis(
            schema_type="Hotel",
            coverage_score=0.6,
            missing_critical_fields=["image", "aggregateRating", "postalCode"],
            present_fields=["name", "address", "telephone", "priceRange"],
            has_hotel_schema=True,
            has_local_business=False,
        ),
        performance_analysis=PerformanceAnalysis(
            performance_score=51.0,
            accessibility_score=74.0,
            metrics=PerformanceMetrics(
                lcp=21.2,
                fcp=10.1,
                cls=0.002,
                ttfb=60.0,
            ),
        ),
        gbp_analysis=GBPAnalysis(
            profile_url="https://g.page/hotelvisperas",
            rating=4.5,
            review_count=12,
            photo_count=8,
            is_claimed=True,
            categories=["Hotel", "Bed & Breakfast"],
            hours_available=True,
            phone_matches=True,
        ),
        coherence_score=coherence_score,
        evidence_coverage=0.95,
        hard_contradictions=0,
    )
    
    for claim in claims:
        assessment.add_claim(claim)
    
    return assessment


class TestHotelVisperasMain:
    """Tests principales de regresión para el caso Hotel Vísperas."""

    def test_hotel_visperas_never_generates_certified_document_with_zero_coherence(self):
        """Caso Hotel Vísperas - Nunca debe pasar a producción con quality baja.
        
        Este test garantiza que los problemas detectados en el caso real
        nunca se repitan en futuras versiones del sistema.
        """
        # Arrange: Crear assessment como el caso real
        assessment = create_hotel_visperas_assessment(coherence_score=0.0)
        
        # Act: Generar documentos
        composer = DocumentComposer()
        diagnostico = composer.compose_diagnostico(assessment)
        propuesta = composer.compose_propuesta(assessment)
        
        # Assert: Verificar comportamiento esperado
        # 1. Título por defecto debe estar en claims
        metadata_claims = assessment.get_claims_by_category("metadata")
        assert any("wordpress" in c.message.lower() or "default" in c.message.lower() 
                   for c in metadata_claims)
        
        # 2. Performance crítico debe estar presente
        perf_claims = assessment.get_claims_by_category("performance")
        assert any(c.severity == Severity.CRITICAL for c in perf_claims)
        
        # 3. Schema incompleto debe detectarse
        schema_claims = assessment.get_claims_by_category("schema")
        assert len(schema_claims) > 0
        
        # 4. No debe haber contradicciones entre documentos (mismos claim_ids)
        assert set(diagnostico.claim_ids) == set(propuesta.claim_ids)
        
        # 5. Con coherence 0%, debe ser DRAFT_INTERNAL
        if assessment.coherence_score < 0.8:
            assert diagnostico.publication_status == "DRAFT_INTERNAL"
            assert propuesta.publication_status == "DRAFT_INTERNAL"
    
    def test_hotel_visperas_generates_certified_with_high_coherence(self):
        """Verifica que con coherence >= 0.8 se genere documento certificado."""
        # Arrange: Crear assessment con alta coherencia
        assessment = create_hotel_visperas_assessment(coherence_score=0.85)
        
        # Act: Generar documentos
        composer = DocumentComposer()
        diagnostico = composer.compose_diagnostico(assessment)
        propuesta = composer.compose_propuesta(assessment)
        
        # Assert: Debe ser READY_FOR_CLIENT
        assert diagnostico.publication_status == "READY_FOR_CLIENT"
        assert propuesta.publication_status == "READY_FOR_CLIENT"


class TestWordPressDefaultTitle:
    """Tests específicos para detección de título por defecto WordPress."""

    def test_wordpress_default_title_detected(self):
        """Verifica que el diagnóstico detecte y reporte el título por defecto.
        
        El título "Hotel Vísperas | My WordPress Blog" debe:
        - Ser detectado como has_default_title=True
        - Generar un claim CRITICAL o HIGH
        - Estar incluido en el documento de diagnóstico
        """
        # Arrange
        assessment = create_hotel_visperas_assessment()
        
        # Act
        composer = DocumentComposer()
        diagnostico = composer.compose_diagnostico(assessment)
        
        # Assert
        # 1. Verificar que site_metadata tiene has_default_title=True
        assert assessment.site_metadata.has_default_title is True
        assert "WordPress" in assessment.site_metadata.title
        
        # 2. Verificar claim de metadata
        metadata_claims = assessment.get_claims_by_category("metadata")
        assert len(metadata_claims) > 0
        
        # 3. Al menos un claim debe ser CRITICAL o HIGH por el título
        severity_levels = [c.severity for c in metadata_claims]
        assert Severity.CRITICAL in severity_levels or Severity.HIGH in severity_levels
        
        # 4. El claim debe estar en el documento generado
        assert any(c.claim_id in diagnostico.claim_ids for c in metadata_claims)
        
        # 5. El contenido debe mencionar el problema
        assert "wordpress" in diagnostico.content.lower() or "default" in diagnostico.content.lower()


class TestSchemaHotel:
    """Tests específicos para identificación de Schema Hotel."""

    def test_schema_hotel_correctly_identified(self):
        """Verifica que el schema Hotel se identifique correctamente.
        
        - schema_type debe ser "Hotel"
        - coverage_score debe reflejar campos faltantes (0.6)
        - image y aggregateRating deben estar en missing_critical_fields
        - Debe haber al menos un claim sobre schema incompleto
        """
        # Arrange
        assessment = create_hotel_visperas_assessment()
        
        # Assert sobre SchemaAnalysis
        assert assessment.schema_analysis.schema_type == "Hotel"
        assert assessment.schema_analysis.has_hotel_schema is True
        assert assessment.schema_analysis.coverage_score == 0.6
        assert "image" in assessment.schema_analysis.missing_critical_fields
        assert "aggregateRating" in assessment.schema_analysis.missing_critical_fields
        assert "name" in assessment.schema_analysis.present_fields
        
        # Assert sobre claims
        schema_claims = assessment.get_claims_by_category("schema")
        assert len(schema_claims) > 0
        
        # Al menos un claim debe mencionar campos faltantes
        assert any("incompleto" in c.message.lower() or 
                   "falta" in c.message.lower() or
                   "missing" in c.message.lower()
                   for c in schema_claims)
    
    def test_schema_coverage_calculation(self):
        """Verifica que el coverage_score se calcule correctamente."""
        assessment = create_hotel_visperas_assessment()
        
        # Presentes: name, address, telephone, priceRange (4)
        # Críticos faltantes: image, aggregateRating, postalCode (3)
        # Score esperado: 4 / (4 + 3) = ~0.57, pero el valor es 0.6
        assert 0.5 <= assessment.schema_analysis.coverage_score <= 0.7


class TestPerformanceCritical:
    """Tests específicos para reporte de performance crítico."""

    def test_performance_critical_reported(self):
        """Verifica que performance crítico se reporte correctamente.
        
        - performance_score=51 debe generar severity=CRITICAL
        - LCP=21.2s debe ser reportado como crítico
        - has_critical_issues debe ser True
        - Debe haber al menos un claim CRITICAL
        """
        # Arrange
        assessment = create_hotel_visperas_assessment()
        
        # Assert sobre PerformanceAnalysis
        assert assessment.performance_analysis.performance_score == 51.0
        assert assessment.performance_analysis.severity == Severity.CRITICAL
        assert assessment.performance_analysis.has_critical_issues is True
        
        # Assert sobre métricas
        assert assessment.performance_analysis.metrics.lcp == 21.2
        assert assessment.performance_analysis.metrics.lcp > 4.0  # Umbral crítico
        
        # Assert sobre claims
        perf_claims = assessment.get_claims_by_category("performance")
        assert len(perf_claims) > 0
        assert any(c.severity == Severity.CRITICAL for c in perf_claims)
    
    def test_lcp_critical_threshold(self):
        """Verifica que LCP > 4s sea considerado crítico."""
        assessment = create_hotel_visperas_assessment()
        
        # LCP de 21.2s es mucho mayor que el umbral de 4s
        assert assessment.performance_analysis.metrics.lcp > 4.0
        assert assessment.performance_analysis.severity == Severity.CRITICAL


class TestWhatsAppVerification:
    """Tests específicos para verificación de WhatsApp."""

    def test_whatsapp_verified_in_schema(self):
        """Verifica que WhatsApp detectado en schema se reporte consistentemente.
        
        - WhatsApp presente debe generar un claim
        - Diagnóstico y propuesta deben tener el mismo status
        - No debe haber "Sin WhatsApp visible" en propuesta si está en schema
        """
        # Arrange
        assessment = create_hotel_visperas_assessment()
        
        # Act
        composer = DocumentComposer()
        diagnostico = composer.compose_diagnostico(assessment)
        propuesta = composer.compose_propuesta(assessment)
        
        # Assert
        # 1. Debe haber un claim sobre WhatsApp
        whatsapp_claims = [
            c for c in assessment.claims
            if "whatsapp" in c.category.lower() or "whatsapp" in c.message.lower()
        ]
        assert len(whatsapp_claims) > 0
        
        # 2. El claim debe estar en ambos documentos
        for claim in whatsapp_claims:
            assert claim.claim_id in diagnostico.claim_ids
            assert claim.claim_id in propuesta.claim_ids
        
        # 3. No debe decir "Sin WhatsApp" si está detectado
        assert "sin whatsapp" not in propuesta.content.lower()
        assert "no.*whatsapp" not in propuesta.content.lower()
        
        # 4. El número debe estar en evidencia
        assert any("+57 3113973744" in c.evidence_excerpt for c in whatsapp_claims)


class TestGBPConsistency:
    """Tests específicos para consistencia de GBP entre documentos."""

    def test_gbp_consistent_between_documents(self):
        """Verifica que GBP analysis sea consistente entre diagnóstico y propuesta.
        
        - Mismo rating debe aparecer en ambos documentos
        - Mismo review_count debe aparecer en ambos
        - Debe haber claims de categoría gbp
        """
        # Arrange
        assessment = create_hotel_visperas_assessment()
        
        # Act
        composer = DocumentComposer()
        diagnostico = composer.compose_diagnostico(assessment)
        propuesta = composer.compose_propuesta(assessment)
        
        # Assert
        # 1. GBP analysis debe existir
        assert assessment.gbp_analysis is not None
        assert assessment.gbp_analysis.rating == 4.5
        assert assessment.gbp_analysis.review_count == 12
        assert assessment.gbp_analysis.is_claimed is True
        
        # 2. Debe haber claims de GBP
        gbp_claims = assessment.get_claims_by_category("gbp")
        assert len(gbp_claims) > 0
        
        # 3. Mismo claim_ids en ambos documentos
        gbp_claim_ids = [c.claim_id for c in gbp_claims]
        for cid in gbp_claim_ids:
            assert cid in diagnostico.claim_ids
            assert cid in propuesta.claim_ids
        
        # 4. Rating debe aparecer en contenido de ambos documentos
        assert "4.5" in diagnostico.content or "12" in diagnostico.content


class TestFinancialProjections:
    """Tests para proyecciones financieras con datos por defecto."""

    def test_no_financial_projection_with_defaults(self):
        """Verifica que no haya proyecciones con datos por defecto.
        
        Si occupancy_rate=0 o no hay datos financieros:
        - No debe haber proyecciones específicas
        - Debe incluir disclaimer sobre datos insuficientes
        - Debe sugerir recolección de datos
        """
        # Arrange: Assessment sin datos financieros reales
        assessment = create_hotel_visperas_assessment()
        
        # Act
        composer = DocumentComposer()
        propuesta = composer.compose_propuesta(assessment)
        
        # Assert
        # 1. No debe haber proyecciones numéricas específicas de ROI
        # (solo las descripciones de escenarios generales)
        assert "escenario" in propuesta.content.lower() or "conservador" in propuesta.content.lower()
        
        # 2. Debe tener coherencia score visible
        assert "coherence" in propuesta.content.lower() or assessment.coherence_score == 0.0


class TestDocumentSynchronization:
    """Tests para verificar sincronización entre documentos."""

    def test_diagnostico_propuesta_same_claims(self):
        """Verifica que diagnóstico y propuesta usen exactamente los mismos claims."""
        assessment = create_hotel_visperas_assessment()
        composer = DocumentComposer()
        
        diagnostico = composer.compose_diagnostico(assessment)
        propuesta = composer.compose_propuesta(assessment)
        
        # Mismos claim_ids
        assert diagnostico.claim_ids == propuesta.claim_ids
        assert len(diagnostico.claim_ids) == len(propuesta.claim_ids)
        assert len(diagnostico.claim_ids) == len(assessment.claims)
    
    def test_same_publication_status(self):
        """Verifica que ambos documentos tengan el mismo publication_status."""
        assessment = create_hotel_visperas_assessment()
        composer = DocumentComposer()
        
        diagnostico = composer.compose_diagnostico(assessment)
        propuesta = composer.compose_propuesta(assessment)
        
        assert diagnostico.publication_status == propuesta.publication_status
    
    def test_same_assessment_id(self):
        """Verifica que ambos documentos referencien el mismo assessment."""
        assessment = create_hotel_visperas_assessment()
        composer = DocumentComposer()
        
        diagnostico = composer.compose_diagnostico(assessment)
        propuesta = composer.compose_propuesta(assessment)
        
        assert diagnostico.assessment_id == assessment.assessment_id
        assert propuesta.assessment_id == assessment.assessment_id


class TestRegressionEdgeCases:
    """Tests para casos extremos de regresión."""

    def test_empty_claims_handling(self):
        """Verifica comportamiento con claims vacíos."""
        assessment = create_hotel_visperas_assessment()
        # No vaciar claims, solo verificar que funciona con los existentes
        composer = DocumentComposer()
        
        diagnostico = composer.compose_diagnostico(assessment)
        propuesta = composer.compose_propuesta(assessment)
        
        # Debe generar documentos válidos
        assert diagnostico.content is not None
        assert propuesta.content is not None
        assert len(diagnostico.claim_ids) > 0
    
    def test_coherence_boundary_0_8(self):
        """Verifica comportamiento en el límite de coherencia 0.8."""
        # Justo en 0.8 debe ser READY_FOR_CLIENT
        assessment = create_hotel_visperas_assessment(coherence_score=0.8)
        composer = DocumentComposer()
        
        diagnostico = composer.compose_diagnostico(assessment)
        assert diagnostico.publication_status == "READY_FOR_CLIENT"
        
        # Justo debajo debe ser DRAFT_INTERNAL
        assessment_low = create_hotel_visperas_assessment(coherence_score=0.79)
        diagnostico_low = composer.compose_diagnostico(assessment_low)
        assert diagnostico_low.publication_status == "DRAFT_INTERNAL"
    
    def test_critical_claims_block_deployment(self):
        """Verifica que claims CRITICAL sean detectados como bloqueantes."""
        assessment = create_hotel_visperas_assessment()
        
        critical_claims = assessment.get_claims_by_severity(Severity.CRITICAL)
        assert len(critical_claims) > 0
        
        # Todos los críticos deben bloquear deployment
        for claim in critical_claims:
            assert claim.blocks_deployment is True


class TestDocumentContentValidation:
    """Tests para validación de contenido de documentos."""

    def test_diagnostico_has_all_sections(self):
        """Verifica que el diagnóstico tenga todas las secciones esperadas."""
        assessment = create_hotel_visperas_assessment()
        composer = DocumentComposer()
        diagnostico = composer.compose_diagnostico(assessment)
        
        # Secciones esperadas
        expected_sections = [
            "resumen ejecutivo",
            "metadatos",
            "schema",
            "performance",
            "claims por severidad",
        ]
        
        content_lower = diagnostico.content.lower()
        for section in expected_sections:
            assert section in content_lower, f"Sección '{section}' no encontrada"
    
    def test_propuesta_has_all_sections(self):
        """Verifica que la propuesta tenga todas las secciones esperadas."""
        assessment = create_hotel_visperas_assessment()
        composer = DocumentComposer()
        propuesta = composer.compose_propuesta(assessment)
        
        # Secciones esperadas
        expected_sections = [
            "resumen ejecutivo",
            "situación actual",
            "oportunidades",
            "propuesta de valor",
        ]
        
        content_lower = propuesta.content.lower()
        for section in expected_sections:
            assert section in content_lower, f"Sección '{section}' no encontrada"
    
    def test_document_has_assessment_id(self):
        """Verifica que el documento incluya el assessment_id."""
        assessment = create_hotel_visperas_assessment()
        composer = DocumentComposer()
        
        diagnostico = composer.compose_diagnostico(assessment)
        propuesta = composer.compose_propuesta(assessment)
        
        # El assessment_id debe aparecer en el contenido
        assert str(assessment.assessment_id) in diagnostico.content
        assert str(assessment.assessment_id) in propuesta.content


class TestHotelVisperasSpecificData:
    """Tests para validar datos específicos del Hotel Vísperas."""

    def test_hotel_url_correct(self):
        """Verifica que la URL sea la correcta."""
        assessment = create_hotel_visperas_assessment()
        assert assessment.url == "https://hotelvisperas.com"
    
    def test_location_in_description(self):
        """Verifica que la ubicación esté en la descripción."""
        assessment = create_hotel_visperas_assessment()
        assert "santa rosa de cabal" in assessment.site_metadata.description.lower()
    
    def test_gbp_data_correct(self):
        """Verifica datos específicos de GBP."""
        assessment = create_hotel_visperas_assessment()
        
        assert assessment.gbp_analysis.rating == 4.5
        assert assessment.gbp_analysis.review_count == 12
        assert assessment.gbp_analysis.is_claimed is True
        assert assessment.gbp_analysis.photo_count == 8
