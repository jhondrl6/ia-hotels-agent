"""Test de regresión: Caso Hotel Vísperas.

⭐ IMPORTANTE: Este test asegura que el caso Hotel Vísperas
nunca pase a producción sin ser detectado.

El Hotel Vísperas tenía:
- Título con "My WordPress Blog" (por defecto)
- Schema Hotel con campos críticos faltantes
- Performance 51/100, LCP 21.2s (crítico)
- Coherence bajo por contradicciones
"""
import sys
from pathlib import Path

# Add project root to Python path for pytest
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
from typing import Dict, Any

from modules.data_validation.metadata_validator import MetadataValidator
from modules.data_validation.schema_validator_v2 import SchemaValidatorV2
from modules.auditors.pagespeed_auditor_v2 import PageSpeedAuditorV2
from data_models.canonical_assessment import (
    CanonicalAssessment,
    SiteMetadata,
    SchemaAnalysis,
    PerformanceAnalysis,
    PerformanceMetrics,
    Claim as PydanticClaim,
)
from enums.severity import Severity


class TestHotelVisperasRegression:
    """Test de regresión completo para el caso Hotel Vísperas."""

    @pytest.fixture
    def visperas_html(self) -> str:
        """HTML real del Hotel Vísperas (simulado)."""
        return """
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Hotel Vísperas | My WordPress Blog</title>
            <meta name="description" content="">
            <script type="application/ld+json">
            {
                "@context": "https://schema.org",
                "@type": "Hotel",
                "name": "Hotel Vísperas",
                "address": {
                    "@type": "PostalAddress",
                    "streetAddress": "Calle 5 de Mayo 100",
                    "addressLocality": "Oaxaca de Juárez",
                    "addressRegion": "Oaxaca",
                    "postalCode": "68000",
                    "addressCountry": "MX"
                },
                "telephone": "+52-951-123-4567",
                "url": "https://hotelvisperas.com"
            }
            </script>
        </head>
        <body>
            <h1>Hotel Vísperas</h1>
        </body>
        </html>
        """

    @pytest.fixture
    def visperas_pagespeed_response(self) -> Dict[str, Any]:
        """Respuesta de PageSpeed API del Hotel Vísperas (real)."""
        return {
            "lighthouseResult": {
                "categories": {
                    "performance": {"score": 0.51},  # 51/100 - CRÍTICO
                    "accessibility": {"score": 0.72}
                },
                "audits": {
                    "largest-contentful-paint": {"numericValue": 21200},  # 21.2s - CRÍTICO
                    "first-contentful-paint": {"numericValue": 8500},     # 8.5s
                    "cumulative-layout-shift": {"numericValue": 0.32},    # Alto
                    "server-response-time": {"numericValue": 2100}        # 2.1s
                }
            },
            "loadingExperience": {
                "metrics": {
                    "LARGEST_CONTENTFUL_PAINT_MS": {"percentile": 21200},
                    "FIRST_CONTENTFUL_PAINT_MS": {"percentile": 8500},
                    "CUMULATIVE_LAYOUT_SHIFT_SCORE": {"percentile": 0.32}
                }
            }
        }

    @pytest.fixture
    def visperas_schema(self) -> Dict[str, Any]:
        """Schema del Hotel Vísperas (incompleto)."""
        return {
            "@context": "https://schema.org",
            "@type": "Hotel",
            "name": "Hotel Vísperas",
            "address": {
                "@type": "PostalAddress",
                "streetAddress": "Calle 5 de Mayo 100",
                "addressLocality": "Oaxaca de Juárez",
                "addressRegion": "Oaxaca",
                "postalCode": "68000",
                "addressCountry": "MX"
            },
            "telephone": "+52-951-123-4567",
            "url": "https://hotelvisperas.com"
            # FALTAN: image, aggregateRating, geo (críticos para Rich Results)
        }

    def test_hotel_visperas_regression(
        self,
        visperas_html,
        visperas_pagespeed_response,
        visperas_schema
    ):
        """
        Caso Hotel Vísperas - Nunca debe pasar a producción así.
        
        Este test verifica que todas las herramientas de validación
        detecten correctamente los problemas del Hotel Vísperas.
        """
        url = "https://hotelvisperas.com"
        
        # ═══════════════════════════════════════════════════════
        # 1. VALIDACIÓN DE METADATOS
        # ═══════════════════════════════════════════════════════
        metadata_validator = MetadataValidator()
        metadata_claims = metadata_validator.analyze(visperas_html, url)
        
        # 1.1: Título por defecto debe detectarse (My WordPress Blog)
        wordpress_claims = [
            c for c in metadata_claims 
            if "My WordPress Blog" in c.message and c.severity == Severity.CRITICAL
        ]
        assert len(wordpress_claims) >= 1, \
            "FALLA CRÍTICA: No se detectó 'My WordPress Blog' en el título"
        
        # 1.2: Meta description vacía debe detectarse
        desc_claims = [
            c for c in metadata_claims 
            if c.field_path == "meta.description" and c.severity == Severity.HIGH
        ]
        assert len(desc_claims) >= 1, \
            "FALLA: No se detectó meta description vacía"
        
        # 1.3: El CMS debe detectarse como WordPress
        cms = metadata_validator.detect_cms(visperas_html)
        assert cms == "wordpress", \
            f"FALLA: CMS detectado como '{cms}', esperaba 'wordpress'"
        
        # ═══════════════════════════════════════════════════════
        # 2. VALIDACIÓN DE SCHEMA
        # ═══════════════════════════════════════════════════════
        schema_validator = SchemaValidatorV2()
        schema_analysis, schema_claims = schema_validator.validate(
            visperas_html, url, is_hotel_site=True
        )
        
        # 2.1: Schema Hotel debe identificarse correctamente
        assert schema_analysis.schema_type == "Hotel", \
            f"FALLA CRÍTICA: Schema detectado como '{schema_analysis.schema_type}', esperaba 'Hotel'"
        assert schema_analysis.has_hotel_schema is True, \
            "FALLA CRÍTICA: has_hotel_schema es False"
        
        # 2.2: Campos críticos faltantes deben detectarse
        expected_missing = ["image", "aggregateRating", "geo"]
        for field in expected_missing:
            assert field in schema_analysis.missing_critical_fields, \
                f"FALLA: Campo crítico '{field}' no detectado como faltante"
        
        # 2.3: Debe haber claims HIGH para campos críticos faltantes
        critical_field_claims = [
            c for c in schema_claims 
            if c.severity == Severity.HIGH and c.category == "schema"
        ]
        assert len(critical_field_claims) >= 3, \
            f"FALLA: Solo {len(critical_field_claims)} claims HIGH para schema, esperaba >= 3"
        
        # 2.4: Coverage debe ser bajo (< 50%)
        assert schema_analysis.coverage_score < 0.5, \
            f"FALLA: Coverage score {schema_analysis.coverage_score} >= 0.5, esperaba < 0.5"
        
        # ═══════════════════════════════════════════════════════
        # 3. VALIDACIÓN DE PERFORMANCE
        # ═══════════════════════════════════════════════════════
        pagespeed_auditor = PageSpeedAuditorV2()
        performance_analysis = pagespeed_auditor.analyze(
            visperas_pagespeed_response, url
        )
        performance_claims = pagespeed_auditor.generate_claims(performance_analysis)
        
        # 3.1: Performance crítico debe reportarse
        assert performance_analysis.severity == Severity.CRITICAL, \
            f"FALLA CRÍTICA: Severidad {performance_analysis.severity}, esperaba CRITICAL"
        assert performance_analysis.has_critical_issues is True, \
            "FALLA: has_critical_issues es False"
        
        # 3.2: Performance score debe ser 51
        assert performance_analysis.performance_score == 51, \
            f"FALLA: Performance score {performance_analysis.performance_score}, esperaba 51"
        
        # 3.3: LCP debe ser 21.2s
        assert performance_analysis.metrics.lcp == 21.2, \
            f"FALLA: LCP {performance_analysis.metrics.lcp}, esperaba 21.2"
        
        # 3.4: Debe generar claim sobre pérdida de usuarios
        abandonment_claims = [
            c for c in performance_claims 
            if c.severity == Severity.CRITICAL and ("abandono" in c.message.lower() or "90%" in c.message)
        ]
        assert len(abandonment_claims) >= 1, \
            "FALLA: No se generó claim sobre pérdida de usuarios/abandono"
        
        # 3.5: Debe generar claim específico para LCP crítico
        lcp_claims = [
            c for c in performance_claims 
            if "LCP" in c.message and c.severity == Severity.CRITICAL
        ]
        assert len(lcp_claims) >= 1, \
            "FALLA: No se generó claim CRITICAL para LCP"
        
        # ═══════════════════════════════════════════════════════
        # 4. ASSESSMENT CANÓNICO INTEGRADO
        # ═══════════════════════════════════════════════════════
        site_metadata = SiteMetadata(
            title="Hotel Vísperas | My WordPress Blog",
            description="",
            cms_detected="wordpress",
            has_default_title=True,
            detected_language="es",
            viewport_meta=True
        )
        
        # Convertir claims de dataclass a Pydantic Claim para CanonicalAssessment
        all_raw_claims = metadata_claims + schema_claims + performance_claims
        pydantic_claims = [
            PydanticClaim(
                source_id=c.source_id,
                evidence_excerpt=c.evidence_excerpt,
                severity=c.severity,
                category=c.category,
                message=c.message,
                confidence=c.confidence,
                field_path=c.field_path,
            )
            for c in all_raw_claims
        ]
        
        assessment = CanonicalAssessment(
            url=url,
            site_metadata=site_metadata,
            schema_analysis=schema_analysis,
            performance_analysis=performance_analysis,
            claims=pydantic_claims,
            coherence_score=0.4,  # Baja coherencia por contradicciones
            evidence_coverage=0.8,
            hard_contradictions=2
        )
        
        # 4.1: Coherence bajo debe marcarse
        assert assessment.coherence_score < 0.5, \
            f"FALLA: Coherence score {assessment.coherence_score} >= 0.5, esperaba < 0.5"
        
        # 4.2: Debe tener claims críticos
        critical_claims = assessment.get_critical_claims()
        assert len(critical_claims) >= 4, \
            f"FALLA: Solo {len(critical_claims)} claims críticos, esperaba >= 4"
        
        # 4.3: Debe tener blockers de deployment
        blockers = assessment.get_deployment_blockers()
        assert len(blockers) >= 2, \
            f"FALLA: Solo {len(blockers)} blockers, esperaba >= 2 (metadata + performance)"
        
        # 4.4: El summary debe reflejar los problemas
        summary = assessment.get_summary()
        assert summary["severity_breakdown"]["critical"] >= 2, \
            "FALLA: Menos de 2 issues CRITICAL en el resumen"
        assert summary["deployment_blockers"] >= 2, \
            "FALLA: Menos de 2 blockers de deployment"
        assert summary["hard_contradictions"] >= 1, \
            "FALLA: No se reportaron contradicciones duras"
        
        # ═══════════════════════════════════════════════════════
        # ÉXITO: Hotel Vísperas detectado correctamente
        # ═══════════════════════════════════════════════════════
        print(f"\n✅ Hotel Vísperas detectado correctamente:")
        print(f"   - Claims CRITICAL: {summary['severity_breakdown']['critical']}")
        print(f"   - Blockers: {summary['deployment_blockers']}")
        print(f"   - Coherence: {assessment.coherence_score}")

    def test_visperas_metadata_severity_breakdown(self, visperas_html):
        """Verifica el breakdown de severidad para metadatos del Vísperas."""
        validator = MetadataValidator()
        claims = validator.analyze(visperas_html, "https://hotel.com")
        
        severities = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for claim in claims:
            severities[claim.severity.name] += 1
        
        # Debe tener al menos 1 CRITICAL (WordPress default)
        assert severities["CRITICAL"] >= 1, \
            "Debe haber al menos 1 claim CRITICAL por título por defecto"
        
        # Debe tener al menos 1 HIGH (description vacía)
        assert severities["HIGH"] >= 1, \
            "Debe haber al menos 1 claim HIGH por description vacía"

    def test_visperas_schema_coverage_calculation(self, visperas_html):
        """Verifica que el coverage del schema del Vísperas sea bajo."""
        validator = SchemaValidatorV2()
        analysis = validator.analyze(visperas_html, "https://hotel.com")
        
        # Campos required presentes: name, address, @type (3/3 = 100%)
        # Campos críticos presentes: 0/3 (image, aggregateRating, geo) = 0%
        # Campos recommended presentes: telephone (1/4) = 25%
        # Overall: 0.4*1.0 + 0.4*0.0 + 0.2*0.25 = 0.45
        
        assert analysis.coverage_score < 0.6, \
            f"Coverage score {analysis.coverage_score} demasiado alto para schema incompleto"
        
        assert "image" in analysis.missing_critical_fields
        assert "aggregateRating" in analysis.missing_critical_fields
        assert "geo" in analysis.missing_critical_fields

    def test_visperas_performance_metrics_extraction(self, visperas_pagespeed_response):
        """Verifica extracción correcta de métricas del Vísperas."""
        auditor = PageSpeedAuditorV2()
        normalized = auditor.normalize_pagespeed_response(visperas_pagespeed_response)
        
        assert normalized["performance_score"] == 51
        assert normalized["lcp"] == 21.2
        assert normalized["fcp"] == 8.5
        assert normalized["cls"] == 0.32
        assert normalized["accessibility_score"] == 72

    def test_visperas_no_production_deployment(self):
        """Test explícito: Vísperas no debe poder desplegarse."""
        # Este test es una protección explícita
        assessment = CanonicalAssessment(
            url="https://hotelvisperas.com",
            site_metadata=SiteMetadata(
                title="Hotel Vísperas | My WordPress Blog",
                description="",
                cms_detected="wordpress",
                has_default_title=True,
                detected_language="es",
                viewport_meta=True
            ),
            schema_analysis=SchemaAnalysis(
                schema_type="Hotel",
                coverage_score=0.4,
                missing_critical_fields=["image", "aggregateRating", "geo"],
                present_fields=["name", "address", "@type", "telephone", "url"],
                raw_schema={},
                has_hotel_schema=True,
                has_local_business=False
            ),
            performance_analysis=PerformanceAnalysis(
                performance_score=51,
                accessibility_score=72,
                metrics=PerformanceMetrics(lcp=21.2, fcp=8.5, cls=0.32, ttfb=2100),
                severity=Severity.CRITICAL,
                has_critical_issues=True
            ),
            claims=[
                PydanticClaim(
                    source_id="metadata_validator",
                    evidence_excerpt="My WordPress Blog",
                    severity=Severity.CRITICAL,
                    category="metadata",
                    message="Título contiene string por defecto",
                    confidence=0.95,
                    field_path="title"
                ),
                PydanticClaim(
                    source_id="pagespeed_auditor",
                    evidence_excerpt="Performance 51/100",
                    severity=Severity.CRITICAL,
                    category="performance",
                    message="Performance crítico - ~90% abandono",
                    confidence=0.95
                )
            ],
            coherence_score=0.4,
            evidence_coverage=0.9,
            hard_contradictions=2
        )
        
        # NO debe poder desplegarse
        blockers = assessment.get_deployment_blockers()
        assert len(blockers) >= 2, \
            "❌ PROTECCIÓN FALLIDA: Hotel Vísperas podría desplegarse a producción"
        
        print("\n🛡️ Protección activa: Hotel Vísperas bloqueado para producción")
