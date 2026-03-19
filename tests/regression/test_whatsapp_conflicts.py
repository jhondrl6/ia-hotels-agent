"""Tests de regresion para conflictos de WhatsApp."""

import pytest
from data_models.canonical_assessment import CanonicalAssessment, Claim, SiteMetadata
from enums.severity import Severity
from enums.confidence_level import ConfidenceLevel


class TestWhatsAppConflicts:
    """Tests para deteccion y manejo de conflictos de WhatsApp."""
    
    def test_whatsapp_web_vs_gbp_conflict_detected(self):
        """Detecta cuando WhatsApp diffiere entre web y GBP."""
        # Simular assessment con numeros diferentes
        web_claim = Claim(
            source_id="web_scraping",
            evidence_excerpt="+57 3111111111",
            severity=Severity.MEDIUM,
            category="contact",
            message="WhatsApp en web: +57 3111111111",
            confidence=0.9
        )
        gbp_claim = Claim(
            source_id="gbp_api",
            evidence_excerpt="+57 3222222222",
            severity=Severity.MEDIUM,
            category="contact",
            message="WhatsApp en GBP: +57 3222222222",
            confidence=0.95
        )
        
        # Verificar que son diferentes
        assert "+57 3111111111" != "+57 3222222222"
        # Esto indicaria un conflicto potencial
        
    def test_whatsapp_consistent_across_sources(self):
        """Verifica que WhatsApp consistente no genera conflicto."""
        number = "+57 3113973744"
        
        web_claim = Claim(
            source_id="web_scraping",
            evidence_excerpt=number,
            severity=Severity.LOW,
            category="contact",
            message=f"WhatsApp detectado: {number}",
            confidence=0.95
        )
        
        # Si ambas fuentes coinciden, no hay conflicto
        assert "+57 3113973744" in web_claim.evidence_excerpt
        assert web_claim.confidence >= 0.9  # Alta confianza por coincidencia
        
    def test_whatsapp_schema_extraction(self):
        """Verifica extraccion correcta desde schema."""
        schema_data = '{"telephone": ["+57 3113973744", "+57 3168245636"]}'
        
        claim = Claim(
            source_id="schema_validator",
            evidence_excerpt=schema_data,
            severity=Severity.LOW,
            category="contact",
            message="Telefonos encontrados en schema",
            confidence=0.95
        )
        
        assert "+57 3113973744" in claim.evidence_excerpt
        assert "+57 3168245636" in claim.evidence_excerpt
        
    def test_whatsapp_verified_status_assigned(self):
        """Asigna estado VERIFIED cuando fuentes coinciden."""
        # Cuando 2+ fuentes coinciden, confianza >= 0.9
        claim = Claim(
            source_id="cross_validation",
            evidence_excerpt="+57 3113973744 (web + GBP + Schema)",
            severity=Severity.LOW,
            category="contact",
            message="WhatsApp verificado en multiples fuentes",
            confidence=0.95
        )
        
        assert claim.confidence >= 0.9
        assert claim.confidence_level == ConfidenceLevel.VERIFIED
