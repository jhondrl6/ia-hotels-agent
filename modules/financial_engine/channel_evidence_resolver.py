"""
Channel Evidence Resolver — Inferencia de canal dominante basada en evidencia.

Sin asumir WhatsApp como default. Usa pesos neutrales cuando no hay evidencia suficiente.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum


class InferredChannel(Enum):
    WHATSAPP = "whatsapp"
    GBP_LOCAL = "gbp"
    BOOKING_ENGINE = "booking_engine"
    OTA_DEPENDENT = "ota_dependent"
    SEO_CONTENT = "seo_content"
    UNKNOWN = "unknown"


class EvidenceConfidence(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class ChannelEvidence:
    dominant_channel: InferredChannel
    confidence: EvidenceConfidence
    evidence: List[str]
    assumptions: List[str]
    channel_weights: Dict[str, float]


# Pesos boutique neutrales (sin evidencia suficiente)
NEUTRAL_WEIGHTS = {
    "gbp_local": 1.15,
    "direct_conversion": 1.10,
    "performance_mobile": 1.05,
    "whatsapp": 1.00,
    "seo_content": 0.95,
    "iao_schema": 0.95,
}


class ChannelEvidenceResolver:
    """Infiera canal dominante basado en evidencia, no en supuestos."""

    def resolve(
        self,
        onboarding_data: Optional[Dict] = None,
        web_evidence: Optional[Dict] = None,
        gbp_data: Optional[Dict] = None,
        diagnostic_pains: Optional[List[str]] = None,
    ) -> ChannelEvidence:
        """Resuelve canal dominante con nivel de confianza."""

        # 1. Onboarding confirma canal (HIGH confidence)
        if onboarding_data:
            whatsapp_share = onboarding_data.get("whatsapp_share", 0)
            direct_pct = onboarding_data.get("direct_channel_pct", 0)
            if whatsapp_share >= 0.40:
                return self._whatsapp_dominant(onboarding_data, EvidenceConfidence.HIGH)
            if direct_pct >= 0.50 and whatsapp_share < 0.10:
                return self._booking_engine_dominant(onboarding_data, EvidenceConfidence.HIGH)

        # 2. Web scraping + GBP proporcionan senales (MEDIUM confidence)
        if web_evidence or gbp_data:
            # WhatsApp como CTA unico + sin motor de reservas → WhatsApp probable
            if web_evidence and web_evidence.get("whatsapp_visible") and not web_evidence.get("booking_engine_detected"):
                whatsapp_clues = self._count_whatsapp_signals(web_evidence, gbp_data)
                if whatsapp_clues >= 3:
                    return self._whatsapp_dominant(
                        web_evidence or gbp_data or {},
                        EvidenceConfidence.MEDIUM
                    )

            # GBP con alto volumen de reviews → GBP/local dominante
            if gbp_data and gbp_data.get("review_count", 0) >= 50 and gbp_data.get("score", 0) >= 4.0:
                return self._gbp_dominant(gbp_data, EvidenceConfidence.MEDIUM)

        # 3. Sin evidencia suficiente (LOW confidence)
        return ChannelEvidence(
            dominant_channel=InferredChannel.UNKNOWN,
            confidence=EvidenceConfidence.LOW,
            evidence=["No hay evidencia suficiente para inferir canal dominante."],
            assumptions=["Se usan pesos boutique neutrales para Eje Cafetero."],
            channel_weights=NEUTRAL_WEIGHTS,
        )

    def _whatsapp_dominant(self, data: Dict, confidence: EvidenceConfidence) -> ChannelEvidence:
        """WhatsApp como canal dominante."""
        evidence = ["WhatsApp identificado como canal principal"]
        if isinstance(data, dict):
            whatsapp_share = data.get("whatsapp_share", 0)
            if whatsapp_share:
                evidence.append(f"whatsapp_share={whatsapp_share:.0%}")
        return ChannelEvidence(
            dominant_channel=InferredChannel.WHATSAPP,
            confidence=confidence,
            evidence=evidence,
            assumptions=[],
            channel_weights=NEUTRAL_WEIGHTS,
        )

    def _gbp_dominant(self, data: Dict, confidence: EvidenceConfidence) -> ChannelEvidence:
        """GBP/Local como canal dominante."""
        evidence = ["GBP con alto volumen y score"]
        if isinstance(data, dict):
            review_count = data.get("review_count", 0)
            score = data.get("score", 0)
            evidence.append(f"reviews={review_count}, score={score}")
        return ChannelEvidence(
            dominant_channel=InferredChannel.GBP_LOCAL,
            confidence=confidence,
            evidence=evidence,
            assumptions=[],
            channel_weights=NEUTRAL_WEIGHTS,
        )

    def _booking_engine_dominant(self, data: Dict, confidence: EvidenceConfidence) -> ChannelEvidence:
        """Booking engine como canal dominante."""
        evidence = ["Canal directo (booking engine) identificado como principal"]
        if isinstance(data, dict):
            direct_pct = data.get("direct_channel_pct", 0)
            if direct_pct:
                evidence.append(f"direct_channel_pct={direct_pct:.0%}")
        return ChannelEvidence(
            dominant_channel=InferredChannel.BOOKING_ENGINE,
            confidence=confidence,
            evidence=evidence,
            assumptions=[],
            channel_weights=NEUTRAL_WEIGHTS,
        )

    def _count_whatsapp_signals(
        self, web_evidence: Optional[Dict] = None, gbp_data: Optional[Dict] = None
    ) -> int:
        """Cuenta senales de WhatsApp en web + GBP."""
        count = 0
        if web_evidence:
            if web_evidence.get("whatsapp_visible"):
                count += 1
            if web_evidence.get("whatsapp_cta_count", 0) >= 3:
                count += 1
            if web_evidence.get("whatsapp_floating_button"):
                count += 1
        if gbp_data:
            if gbp_data.get("has_whatsapp_link"):
                count += 1
            if gbp_data.get("messaging_options") == "whatsapp":
                count += 1
        return count
