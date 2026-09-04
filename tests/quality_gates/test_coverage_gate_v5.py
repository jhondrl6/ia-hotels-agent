"""
Tests for coverage-gate escotillas V5 and V9 (FASE-G G3/G4).

V5 (G3): "generado y silencioso" deja de justificar. ASSET_GENERATED only
justifies alongside a mention in diagnostic/proposal — the silent variant
(ledger says generated, doc never mentions the pain) is UNCOVERED.

Anti-reversión BUG-6/N2 (Zione 2026-07-25): ASSET_GENERATED MUST remain in
_JUSTIFIED_STATUSES. The modern "exists in production" case is
VERIFIED_IN_SITE (first-class since FASE-P1-D, preserved by the reconciler),
which justifies WITHOUT doc mention — so this tightening must NOT block the
Zione scenario again.

V9 (G4): unified empty-ledger treatment after normalization (DA-C3:
vacío ≠ ausente):
  - ledger present but empty = legitimate favorable state → PASSED with trace
  - pain_ledger_resolved empty while original non-empty = silent reconciler
    drop → BLOCKED
  - ledger key absent → BLOCKED (L-SR5)
"""

import pytest

from modules.quality_gates.publication_gates import (
    PublicationGatesOrchestrator,
    PublicationGateConfig,
    GateStatus,
)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def orchestrator() -> PublicationGatesOrchestrator:
    return PublicationGatesOrchestrator(PublicationGateConfig())


def make_assessment(
    ledger,
    diagnostic_pain_ids=None,
    proposal_pain_ids=None,
    resolved=None,
    include_original=True,
) -> dict:
    assessment = {
        "diagnostic_pain_ids": diagnostic_pain_ids or [],
        "proposal_pain_ids": proposal_pain_ids or [],
    }
    if include_original:
        assessment["pain_ledger"] = ledger
    if resolved is not None:
        assessment["pain_ledger_resolved"] = resolved
    return assessment


def entry(pain_id: str, status: str) -> dict:
    return {"pain_id": pain_id, "status": status}


# Huérfanos reales de la corrida SalentoReal 2026-08-31 (gate_report:
# coverage 3/3 PASSED con ledger 100% ASSET_GENERATED y 0 menciones en doc).
HAURFANOS_SALENTOREAL = ["indirect_traffic_optimization", "analytics_setup_guide"]


# =============================================================================
# V5 (G3): generado + silencioso deja de justificar
# =============================================================================

class TestV5Escotilla:
    def test_generado_y_mencionado_cubre(self, orchestrator):
        """ASSET_GENERATED + mención en diagnóstico → covered → PASSED."""
        assessment = make_assessment(
            ledger=[entry("whatsapp_button", "ASSET_GENERATED")],
            diagnostic_pain_ids=["whatsapp_button"],
        )
        result = orchestrator._coverage_gate(assessment)
        assert result.passed is True
        assert result.details["covered"] == 1

    def test_generado_y_mencionado_en_propuesta_cubre(self, orchestrator):
        assessment = make_assessment(
            ledger=[entry("faq_page", "ASSET_GENERATED")],
            proposal_pain_ids=["faq_page"],
        )
        result = orchestrator._coverage_gate(assessment)
        assert result.passed is True
        assert result.details["covered"] == 1

    def test_generado_silencioso_uncovered(self, orchestrator):
        """ASSET_GENERATED sin mención en doc → uncovered → FAILED (V5 cerrada)."""
        assessment = make_assessment(
            ledger=[entry("indirect_traffic_optimization", "ASSET_GENERATED")],
        )
        result = orchestrator._coverage_gate(assessment)
        assert result.passed is False
        assert result.status == GateStatus.FAILED
        assert result.details["uncovered"] == ["indirect_traffic_optimization"]
        assert result.value < 1.0

    def test_huerfanos_salentoreal_uncovered(self, orchestrator):
        """Los 2 huérfanos reales de SalentoReal (ledger ASSET_GENERATED,
        0 menciones) ya no pasan en verde."""
        assessment = make_assessment(
            ledger=[
                entry(pid, "ASSET_GENERATED") for pid in HAURFANOS_SALENTOREAL
            ],
        )
        result = orchestrator._coverage_gate(assessment)
        assert result.passed is False
        assert set(result.details["uncovered"]) == set(HAURFANOS_SALENTOREAL)
        assert result.value == 0.0

    def test_asset_generated_still_in_justified_statuses(self, orchestrator):
        """Anti-reversión BUG-6/N2 (Zione 2026-07-25): ASSET_GENERATED NO debe
        quitarse de _JUSTIFIED_STATUSES — el estrechamiento vive en la regla
        de mención, no en la lista."""
        assert "ASSET_GENERATED" in PublicationGatesOrchestrator._JUSTIFIED_STATUSES

    def test_anti_reversion_verified_in_site_silencioso_pasa(self, orchestrator):
        """Caso Zione moderno: VERIFIED_IN_SITE justifica SIN mención en doc
        (protección BUG-6 intacta — el sitio vivo es la verdad)."""
        assessment = make_assessment(
            ledger=[entry("whatsapp_button", "VERIFIED_IN_SITE")],
        )
        result = orchestrator._coverage_gate(assessment)
        assert result.passed is True
        assert result.details["justified"] == 1
        assert result.details["uncovered"] == []

    def test_otros_estatus_siguen_justificando(self, orchestrator):
        """JUSTIFIED_SKIP/BLOCKED/MAPPED_TO_SERVICE silenciosos siguen
        justificando (regresión cero)."""
        assessment = make_assessment(
            ledger=[
                entry("p1", "JUSTIFIED_SKIP"),
                entry("p2", "BLOCKED"),
                entry("p3", "MAPPED_TO_SERVICE"),
            ],
        )
        result = orchestrator._coverage_gate(assessment)
        assert result.passed is True
        assert result.details["justified"] == 3

    def test_mixto_mencion_y_silencioso(self, orchestrator):
        """1 mencionado + 1 generado silencioso → solo el silencioso uncovered."""
        assessment = make_assessment(
            ledger=[
                entry("whatsapp_button", "ASSET_GENERATED"),
                entry("analytics_setup_guide", "ASSET_GENERATED"),
            ],
            diagnostic_pain_ids=["whatsapp_button"],
        )
        result = orchestrator._coverage_gate(assessment)
        assert result.passed is False
        assert result.details["uncovered"] == ["analytics_setup_guide"]
        assert result.details["covered"] == 1


# =============================================================================
# V9 (G4): tratamiento unificado del ledger vacío
# =============================================================================

class TestV9LedgerVacio:
    def test_fallback_vacio_pass_con_traza(self, orchestrator):
        """pain_ledger=[] sin reconciler → estado favorable legítimo PASSED
        con coverage_basis trazado (no silencioso)."""
        assessment = make_assessment(ledger=[], resolved=None)
        result = orchestrator._coverage_gate(assessment)
        assert result.passed is True
        assert result.status == GateStatus.PASSED
        assert result.value == 1.0
        assert result.details["coverage_basis"] == "ledger_present_zero_entries"
        assert result.details["reconciler_ran"] is False

    def test_fallback_ausente_blocked(self, orchestrator):
        """Clave pain_ledger inexistente → BLOCKED (pipeline incompleto, L-SR5)."""
        assessment = make_assessment(
            ledger=[], resolved=None, include_original=False
        )
        result = orchestrator._coverage_gate(assessment)
        assert result.passed is False
        assert result.status == GateStatus.BLOCKED

    def test_resolved_vacio_con_original_no_vacio_blocked(self, orchestrator):
        """resolved=[] con ledger original con entradas → caída silenciosa del
        reconciler → BLOCKED (G4: misma semántica que la ruta legacy)."""
        assessment = make_assessment(
            ledger=[entry("whatsapp_button", "DETECTED")],
            resolved=[],
        )
        result = orchestrator._coverage_gate(assessment)
        assert result.passed is False
        assert result.status == GateStatus.BLOCKED
        assert result.details["coverage_basis"] == "reconciler_dropped_entries"
        assert result.details["original_entries"] == 1

    def test_resolved_vacio_con_original_vacio_pass(self, orchestrator):
        """resolved=[] con original también vacío → "resuelto, 0 brechas"
        legítimo → PASSED (mismo tratamiento que la ruta fallback)."""
        assessment = make_assessment(ledger=[], resolved=[])
        result = orchestrator._coverage_gate(assessment)
        assert result.passed is True
        assert result.status == GateStatus.PASSED
        assert result.details["coverage_basis"] == "ledger_present_zero_entries"
        assert result.details["reconciler_ran"] is True

    def test_resolved_ausente_usa_fallback(self, orchestrator):
        """Sin pain_ledger_resolved → ruta fallback intacta (no-regresión);
        el covered=1 prueba que el ledger fallback fue el validado."""
        assessment = make_assessment(
            ledger=[entry("whatsapp_button", "ASSET_GENERATED")],
            diagnostic_pain_ids=["whatsapp_button"],
        )
        result = orchestrator._coverage_gate(assessment)
        assert result.passed is True
        assert result.details["covered"] == 1

    def test_resolved_dict_entries_vacias_con_original_no_vacio_blocked(
        self, orchestrator
    ):
        """resolved como dict {"entries": []} con original no vacío → BLOCKED
        (la unificación cubre la ruta dict)."""
        assessment = make_assessment(
            ledger=[entry("whatsapp_button", "DETECTED")],
            resolved={"entries": []},
        )
        result = orchestrator._coverage_gate(assessment)
        assert result.passed is False
        assert result.status == GateStatus.BLOCKED
