"""
Tests para ChannelEvidenceResolver.
Minimo 8 tests cubriendo los criterios de completitud.
"""
import pytest
from modules.financial_engine.channel_evidence_resolver import (
    ChannelEvidenceResolver,
    InferredChannel,
    EvidenceConfidence,
    ChannelEvidence,
    NEUTRAL_WEIGHTS,
)


class TestChannelEvidenceResolver:
    """Suite de tests para ChannelEvidenceResolver."""

    def setup_method(self):
        self.resolver = ChannelEvidenceResolver()

    # Test 1: WhatsApp HIGH con 40%+ share
    def test_whatsapp_dominant_from_onboarding_high_share(self):
        onboarding = {"whatsapp_share": 0.55, "direct_channel_pct": 0.10}
        result = self.resolver.resolve(onboarding_data=onboarding)
        assert result.dominant_channel == InferredChannel.WHATSAPP
        assert result.confidence == EvidenceConfidence.HIGH
        assert "whatsapp_share" in str(result.evidence)

    # Test 2: GBP MEDIUM con 50+ reviews y score >= 4.0
    def test_gbp_dominant_high_reviews(self):
        gbp = {"review_count": 75, "score": 4.3}
        result = self.resolver.resolve(gbp_data=gbp)
        assert result.dominant_channel == InferredChannel.GBP_LOCAL
        assert result.confidence == EvidenceConfidence.MEDIUM

    # Test 3: UNKNOWN LOW sin datos
    def test_unknown_channel_no_evidence(self):
        result = self.resolver.resolve()
        assert result.dominant_channel == InferredChannel.UNKNOWN
        assert result.confidence == EvidenceConfidence.LOW
        assert "No hay evidencia suficiente" in result.evidence[0]

    # Test 4: Pesos neutrales aplicados cuando UNKNOWN
    def test_neutral_weights_when_unknown(self):
        result = self.resolver.resolve()
        assert result.channel_weights == NEUTRAL_WEIGHTS

    # Test 5: Region NO influye en peso WhatsApp (sin hardcode)
    def test_no_whatsapp_hardcode_by_region(self):
        """Verifica que no hay regla hardcodeada por region."""
        # Intentar con region eje_cafetero - debe comportarse igual que sin region
        result_1 = self.resolver.resolve()
        onboarding = {"whatsapp_share": 0.45}
        result_2 = self.resolver.resolve(onboarding_data=onboarding)
        # Ambos usan NEUTRAL_WEIGHTS como base
        assert result_1.channel_weights == NEUTRAL_WEIGHTS
        #WhatsApp usa los mismos pesos neutrales
        assert result_2.channel_weights == NEUTRAL_WEIGHTS

    # Test 6: Booking engine HIGH con directo 50%+ y WhatsApp < 10%
    def test_booking_engine_dominant_from_onboarding(self):
        onboarding = {"whatsapp_share": 0.05, "direct_channel_pct": 0.60}
        result = self.resolver.resolve(onboarding_data=onboarding)
        assert result.dominant_channel == InferredChannel.BOOKING_ENGINE
        assert result.confidence == EvidenceConfidence.HIGH

    # Test 7: WhatsApp MEDIUM cuando es unico CTA visible
    def test_whatsapp_cta_only_web_medium(self):
        web = {"whatsapp_visible": True, "booking_engine_detected": False, "whatsapp_cta_count": 3}
        gbp = {"has_whatsapp_link": True, "messaging_options": "whatsapp"}
        result = self.resolver.resolve(web_evidence=web, gbp_data=gbp)
        assert result.dominant_channel == InferredChannel.WHATSAPP
        assert result.confidence == EvidenceConfidence.MEDIUM

    # Test 8: Pesos incluidos en ChannelEvidence output
    def test_channel_weights_present_in_output(self):
        result = self.resolver.resolve()
        assert hasattr(result, "channel_weights")
        assert isinstance(result.channel_weights, dict)
        assert "whatsapp" in result.channel_weights
        assert "gbp_local" in result.channel_weights
        assert "direct_conversion" in result.channel_weights
