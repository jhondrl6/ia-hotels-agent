"""
Tests for FASE-2: proposal_asset_alignment BLOCKING para P1.

Tests gate hardening: _proposal_asset_alignment_gate ahora retorna BLOCKED
cuando un asset asociado a un dolor P1 tiene status NOT_READY o BLOCKED.

Cobertura:
- Test 1: P1 pain + asset NOT_READY → BLOCKING
- Test 2: P1 pain + asset IMPLEMENT → PASS
- Test 3: P2 pain + asset NOT_READY → WARNING (no bloquea)
- Test 4: skipped_existing con P1 → PASS (AUDIT_ONLY narrativa)
- Test 5: Todos P1 implementados → PASS
- Test 6: Semantic hallucination (BLOCKED de validar_semantica_comercial) → BLOCKED
"""

import pytest
from typing import Dict, Any, List

from modules.quality_gates.publication_gates import (
    PublicationGatesOrchestrator,
    PublicationGateConfig,
    GateStatus,
)
from modules.quality.asset_semantics_validator import validar_semantica_comercial


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def config() -> PublicationGateConfig:
    """Default gate configuration."""
    return PublicationGateConfig()


@pytest.fixture
def orchestrator(config) -> PublicationGatesOrchestrator:
    """Publication gates orchestrator."""
    return PublicationGatesOrchestrator(config)


def _minimal_assessment(
    services: List[str],
    generated_assets: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Build minimal assessment for proposal_asset_alignment_gate tests.

    Args:
        services: List of proposal service names (from PROPOSAL_SERVICE_TO_ASSET keys)
        generated_assets: List of asset dicts with asset_type and optional status
    """
    return {
        "hotel_url": "https://www.test-hotel.com/",
        "proposal_services": services,
        "generated_assets": generated_assets,
        # Minimal data for other gates (not exercised by our test)
        "coherence_score": 0.85,
        "evidence_coverage": 0.96,
        "hard_contradictions": 0,
        "critical_recall": 0.95,
        "financial_data": {
            "occupancy_rate": 75.0,
            "direct_channel_percentage": 30.0,
            "adr_cop": 450000.0,
        },
        "validation_summary": {"hard_contradictions_count": 0},
        # FASE-C: clave AUSENTE a propósito. ``pain_ledger: []`` ahora significa
        # "ledger resuelto sin brechas" → 0 servicios comprometidos → PASS
        # trivial. Estos tests ejercitan el bloqueo P1/P2 sobre una
        # proposal_services explícita, que es la ruta legacy sin fuente.
        "diagnostic_pain_ids": [],
        "proposal_pain_ids": [],
        "financial_evidence_tier": "B",
    }


# =============================================================================
# Test 1: P1 pain + asset NOT_READY → BLOCKED
# =============================================================================

class TestP1NotReadyBlocking:
    """Tests: P1 pain con asset NOT_READY debe bloquear el gate."""

    def test_whatsapp_button_not_ready_blocks(self, orchestrator):
        """
        Botón de WhatsApp (P1) con status NOT_READY → BLOCKING.

        whatsapp_button resuelve pain_id "no_whatsapp_visible" (priority=1).
        Cuando el asset está NOT_READY, no puede prometerse al cliente.
        El gate debe retornar BLOCKED.
        """
        assessment = _minimal_assessment(
            services=["Botón de WhatsApp"],
            generated_assets=[
                {
                    "asset_type": "whatsapp_button",
                    "confidence_score": 0.5,
                    "status": "NOT_READY",  # P1 asset NOT_READY
                }
            ],
        )

        result = orchestrator._proposal_asset_alignment_gate(assessment)

        assert result.passed is False
        assert result.status == GateStatus.BLOCKED
        assert "BLOQUEO P1" in result.message or "whatsapp_button" in result.message

    def test_whatsapp_button_blocked_blocks(self, orchestrator):
        """
        Botón de WhatsApp (P1) con status BLOCKED → BLOCKING.

        Same as NOT_READY — cualquier status que no sea IMPLEMENT
        o skipped_existing para P1 debe bloquear.
        """
        assessment = _minimal_assessment(
            services=["Botón de WhatsApp"],
            generated_assets=[
                {
                    "asset_type": "whatsapp_button",
                    "confidence_score": 0.5,
                    "status": "BLOCKED",  # P1 asset BLOCKED
                }
            ],
        )

        result = orchestrator._proposal_asset_alignment_gate(assessment)

        assert result.passed is False
        assert result.status == GateStatus.BLOCKED

    def test_multiple_p1_assets_not_ready_blocks(self, orchestrator):
        """
        Dos assets P1 NOT_READY → BLOCKING con detalle de ambos.
        """
        assessment = _minimal_assessment(
            services=["Botón de WhatsApp", "SEO Local"],
            generated_assets=[
                {
                    "asset_type": "whatsapp_button",
                    "confidence_score": 0.5,
                    "status": "NOT_READY",
                },
                {
                    "asset_type": "optimization_guide",
                    "confidence_score": 0.5,
                    "status": "NOT_READY",
                },
            ],
        )

        result = orchestrator._proposal_asset_alignment_gate(assessment)

        assert result.passed is False
        assert result.status == GateStatus.BLOCKED


# =============================================================================
# Test 2: P1 pain + asset IMPLEMENT → PASS
# =============================================================================

class TestP1ImplementPasses:
    """Tests: P1 pain con asset IMPLEMENT debe pasar el gate."""

    def test_whatsapp_button_implement_passes(self, orchestrator):
        """
        Botón de WhatsApp (P1) con status IMPLEMENT (default) → PASS.
        """
        assessment = _minimal_assessment(
            services=["Botón de WhatsApp"],
            generated_assets=[
                {
                    "asset_type": "whatsapp_button",
                    "confidence_score": 0.9,
                    "status": "IMPLEMENT",  # Normal case
                }
            ],
        )

        result = orchestrator._proposal_asset_alignment_gate(assessment)

        assert result.passed is True
        assert result.status == GateStatus.PASSED

    def test_whatsapp_button_default_status_passes(self, orchestrator):
        """
        Botón de WhatsApp sin campo status → default IMPLEMENT → PASS.
        """
        assessment = _minimal_assessment(
            services=["Botón de WhatsApp"],
            generated_assets=[
                {
                    "asset_type": "whatsapp_button",
                    "confidence_score": 0.9,
                    # Sin campo "status" — default IMPLEMENT
                }
            ],
        )

        result = orchestrator._proposal_asset_alignment_gate(assessment)

        assert result.passed is True

    def test_all_p1_assets_implement_passes(self, orchestrator):
        """
        Todos los servicios P1 con status IMPLEMENT → PASS con alignment 100%.
        """
        assessment = _minimal_assessment(
            services=[
                "Botón de WhatsApp",      # P1
                "SEO Local",              # P1 (optimization_guide)
                "Schema Hotel",          # P1 (hotel_schema)
            ],
            generated_assets=[
                {"asset_type": "whatsapp_button", "confidence_score": 0.9, "status": "IMPLEMENT"},
                {"asset_type": "optimization_guide", "confidence_score": 0.9, "status": "IMPLEMENT"},
                {"asset_type": "hotel_schema", "confidence_score": 0.9, "status": "IMPLEMENT"},
            ],
        )

        result = orchestrator._proposal_asset_alignment_gate(assessment)

        assert result.passed is True
        assert result.status == GateStatus.PASSED


# =============================================================================
# Test 3: P2 pain + asset NOT_READY → WARNING (no bloquea)
# =============================================================================

class TestP2NotReadyAdvisory:
    """Tests: P2 pain con asset NOT_READY no bloquea (WARNING)."""

    def test_p2_not_ready_mixed_alignment_75_percent_blocks(self, orchestrator):
        """
        P2 (NOT_READY) + P1 (IMPLEMENT) con alignment 75% < 80% → BLOCKED.

        3 OK + 1 P2 NOT_READY (no asset) = 3/4 = 75% alignment < 80%.
        No P1 blocked → BLOCKED por threshold, no por P1.
        """
        assessment = _minimal_assessment(
            services=[
                "Botón de WhatsApp",       # P1, IMPLEMENT
                "SEO Local",               # P1, IMPLEMENT
                "Página de FAQ",           # P2, NOT_READY
                "Optimización para IA Generativa",  # P3, IMPLEMENT
            ],
            generated_assets=[
                {"asset_type": "whatsapp_button", "confidence_score": 0.9, "status": "IMPLEMENT"},
                {"asset_type": "optimization_guide", "confidence_score": 0.9, "status": "IMPLEMENT"},
                # faq_page NOT_READY (no asset generated)
                {"asset_type": "llms_txt", "confidence_score": 0.9, "status": "IMPLEMENT"},
            ],
        )

        result = orchestrator._proposal_asset_alignment_gate(assessment)

        # alignment = 3/4 = 75% < 80% → BLOCKED por threshold
        assert result.passed is False
        assert result.status == GateStatus.BLOCKED

    def test_faq_page_not_ready_above_threshold_warns(self, orchestrator):
        """
        FAQ Page (P2) NOT_READY con otros servicios OK → alignment >= 80% → WARNING.

        Solo cuando alignment >= 80% Y el servicio bloqueante es P2/P3,
        el gate pasa con WARNING. Esto requiere al menos 4 servicios OK.
        
        FASE-3 (BUG-10): "Informe Mensual" / monthly_report removido de PROPOSAL_SERVICE_TO_ASSET.
        Ahora son 5 servicios en alignment (no 6). 4/5 = 80% sigue pasando WARNING.
        """
        assessment = _minimal_assessment(
            services=[
                "Botón de WhatsApp",       # P1, IMPLEMENT
                "SEO Local",               # P1, IMPLEMENT
                "Schema Hotel",            # P1, IMPLEMENT
                "Schema Organization",     # P3, IMPLEMENT
                "Página de FAQ",           # P2, NOT_READY
            ],
            generated_assets=[
                {"asset_type": "whatsapp_button", "confidence_score": 0.9, "status": "IMPLEMENT"},
                {"asset_type": "optimization_guide", "confidence_score": 0.9, "status": "IMPLEMENT"},
                {"asset_type": "hotel_schema", "confidence_score": 0.9, "status": "IMPLEMENT"},
                {"asset_type": "org_schema", "confidence_score": 0.9, "status": "IMPLEMENT"},
                # faq_page NOT_READY → P2, advisory
            ],
        )

        result = orchestrator._proposal_asset_alignment_gate(assessment)

        # FASE-3 (BUG-10): alignment = 4/5 = 80% >= 80%, P2 NOT_READY solo → WARNING
        assert result.passed is True
        assert result.status == GateStatus.WARNING


# =============================================================================
# Test 4: skipped_existing con P1 → PASS
# =============================================================================

class TestSkippedExistingAuditOnly:
    """Tests: skipped_existing para P1 pasa con narrativa AUDIT_ONLY."""

    def test_whatsapp_skipped_existing_passes(self, orchestrator):
        """
        Botón de WhatsApp (P1) con status skipped_existing → PASS.

        skipped_existing es la excepcion: pasa PERO fuerza narrativa AUDIT_ONLY.
        El gate pasa (passed=True) — la narrativa AUDIT_ONLY se aplica
        en la generacion de propuesta, no aqui.
        """
        assessment = _minimal_assessment(
            services=["Botón de WhatsApp"],
            generated_assets=[
                {
                    "asset_type": "whatsapp_button",
                    "confidence_score": 0.9,
                    "status": "skipped_existing",  # Exception: audit only
                }
            ],
        )

        result = orchestrator._proposal_asset_alignment_gate(assessment)

        # skipped_existing: pasa (AUDIT_ONLY narrativa se maneja en generacion)
        assert result.passed is True

    def test_whatsapp_skipped_existing_no_blocking(self, orchestrator):
        """
        skipped_existing NO debe bloquear aunque sea P1.
        """
        assessment = _minimal_assessment(
            services=["Botón de WhatsApp"],
            generated_assets=[
                {
                    "asset_type": "whatsapp_button",
                    "confidence_score": 0.9,
                    "status": "skipped_existing",
                }
            ],
        )

        result = orchestrator._proposal_asset_alignment_gate(assessment)

        assert result.status != GateStatus.BLOCKED


# =============================================================================
# Test 5: Alignment 80% threshold para P2/P3
# =============================================================================

class TestAlignmentThreshold:
    """Tests: alignment 80% threshold para P2/P3."""

    def test_mixed_p1_p2_below_80_alignment_blocks(self, orchestrator):
        """
        Mix de P1 (OK) + P2 (NOT_READY) con alignment < 80% → BLOCKED.

        1 P1 OK + 2 P2 missing de 3 servicios = 33% alignment.
        Como alignment < 80%, el gate original bloquearia por alignment,
        no por P1. En este caso el P2 es NOT_READY (advisory), pero
        el threshold de alignment fuerza BLOCKED.
        """
        assessment = _minimal_assessment(
            services=["Botón de WhatsApp", "Página de FAQ", "Meta Tags Sociales (Open Graph)"],
            generated_assets=[
                {"asset_type": "whatsapp_button", "confidence_score": 0.9, "status": "IMPLEMENT"},
                # faq_page NOT_READY (P2 — advisory)
                # open_graph missing
            ],
        )

        result = orchestrator._proposal_asset_alignment_gate(assessment)

        # Alignment = 1/3 = 33% < 80% → BLOCKED por threshold
        assert result.passed is False
        assert result.status == GateStatus.BLOCKED

    def test_p2_not_ready_above_80_alignment_warns(self, orchestrator):
        """
        P2 NOT_READY con alignment >= 80% → WARNING (no bloquea).

        4/5 servicios = 80% alignment. EI P2 (faq_page NOT_READED) no bloquea.
        El gate pasa con WARNING.
        """
        assessment = _minimal_assessment(
            services=[
                "Botón de WhatsApp",       # P1, IMPLEMENT
                "SEO Local",               # P1, IMPLEMENT
                "Schema Hotel",            # P1, IMPLEMENT
                "Schema Organization",     # P3, IMPLEMENT
                "Página de FAQ",           # P2, NOT_READY
            ],
            generated_assets=[
                {"asset_type": "whatsapp_button", "confidence_score": 0.9, "status": "IMPLEMENT"},
                {"asset_type": "optimization_guide", "confidence_score": 0.9, "status": "IMPLEMENT"},
                {"asset_type": "hotel_schema", "confidence_score": 0.9, "status": "IMPLEMENT"},
                {"asset_type": "org_schema", "confidence_score": 0.9, "status": "IMPLEMENT"},
                # faq_page NOT_READY → P2, advisory
            ],
        )

        result = orchestrator._proposal_asset_alignment_gate(assessment)

        # alignment = 4/5 = 80% >= 80%, solo P2 NOT_READY → WARNING
        assert result.passed is True
        assert result.status == GateStatus.WARNING


# =============================================================================
# Test 6: Semantic hallucination (validar_semantica_comercial BLOCKED)
# =============================================================================

class TestSemanticHallucination:
    """Tests:幻觉映射 → BLOCKED via validar_semantica_comercial."""

    def test_hallucination_monthly_report_faq_blocks(self, orchestrator):
        """
        FASE-3 (BUG-10): monthly_report removido de PROPOSAL_SERVICE_TO_ASSET.
        
        "Informe Mensual" ya no participa en alignment — el gate lo salta (line 220-221).
        Este test verifica que el gate maneja correctamente servicios fuera del mapping,
        retornando un report vacío sin errores.
        
        Antes de BUG-10, este test documentaba que monthly_report no puede resolver
        faq_missing (hallucination). Con monthly_report fuera de alignment, ese
        escenario ya no puede ocurrir a través del gate.
        """
        assessment = _minimal_assessment(
            services=["Informe Mensual"],  # → skipped, not in PROPOSAL_SERVICE_TO_ASSET
            generated_assets=[
                {"asset_type": "monthly_report", "confidence_score": 0.9, "status": "IMPLEMENT"},
            ],
        )

        result = orchestrator._proposal_asset_alignment_gate(assessment)

        # BUG-10: "Informe Mensual" skipped → 0 services checked → gate passes vacuously
        assert result.passed is True
        assert result.status == GateStatus.PASSED

    def test_whatsapp_conflict_guide_hallucination_no_whatsapp_visible(self, orchestrator):
        """
        whatsapp_conflict_guide no puede resolver no_whatsapp_visible (hallucination).

        INVALID_MAPPINGS[no_whatsapp_visible] = [whatsapp_conflict_guide].
        El guia es advisory — no resuelve el problema de WhatsApp faltante.
        """
        # Este test verifica que el INVALID_MAPPING existe
        ok, result = validar_semantica_comercial(
            "no_whatsapp_visible",
            "whatsapp_conflict_guide",
            "IMPLEMENT"
        )
        assert ok is False
        assert "BLOCKED" in result
        assert "HALLUCINATION" in result


# =============================================================================
# Test 7: validar_semantica_comercial integration
# =============================================================================

class TestAssetSemanticsValidator:
    """Tests para la integracion con AssetSemanticsValidator (FASE-1)."""

    def test_skipped_existing_returns_audit_only(self):
        """
        skipped_existing → AUDIT_ONLY.
        """
        ok, result = validar_semantica_comercial(
            "no_whatsapp_visible",
            "whatsapp_button",
            "skipped_existing"
        )
        assert ok is True
        assert result == "AUDIT_ONLY"

    def test_valid_mapping_returns_implement(self):
        """
        Mapping valido → IMPLEMENT.
        """
        ok, result = validar_semantica_comercial(
            "no_whatsapp_visible",
            "whatsapp_button",
            "IMPLEMENT"
        )
        assert ok is True
        assert result == "IMPLEMENT"

    def test_invalid_hallucination_returns_blocked(self):
        """
        Mapping invalido (hallucination) → BLOCKED.

        FASE-2: INVALID_MAPPINGS keys were bugged (asset_type instead of pain_id).
        After fix: no_whatsapp_visible blocks whatsapp_conflict_guide.
        """
        ok, result = validar_semantica_comercial(
            "no_whatsapp_visible",
            "whatsapp_conflict_guide",  # No puede resolver no_whatsapp_visible
            "IMPLEMENT"
        )
        assert ok is False
        assert "BLOCKED" in result

    def test_deprecated_with_migration_target_still_valid(self):
        """
        Un asset DEPRECATED con migration_target → valido (se redirige).
        La funcion no conoce migration_target (eso lo maneja el mapper).
        """
        ok, result = validar_semantica_comercial(
            "missing_llmstxt",
            "llms_txt",
            "IMPLEMENT"
        )
        # Sin INVALID_MAPPING especifico para llms_txt + missing_llmstxt
        assert ok is True
        assert result == "IMPLEMENT"
