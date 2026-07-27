"""Tests for Commercial Gate Validator.

Valida que el CommercialGateValidator:
1. Detecta escenario optimista negativo (CG-SCENARIO-NEGATIVE)
2. Detecta "IA Bloqueada" sin blocked_crawlers (CG-IA-BLOCKED-CLAIM)
3. Detecta ROI negativo sin onboarding plan (CG-ROI-NEGATIVE)
4. Detecta orden de escenarios inválido (CG-SCENARIO-ORDER)
5. Detecta claims sin evidencia (CG-CLAIM-VS-EVIDENCE)
6. Pasa cuando todos los datos son correctos
"""

import pytest
from modules.quality_gates.commercial_gate import (
    CommercialGateValidator,
    CommercialGateResult,
    CommercialGateReport,
)


class TestCommercialGateScenarioNegative:
    """CG-SCENARIO-NEGATIVE: Escenario optimista < 0."""

    def test_optimistic_negative_realistic_positive_warns(self):
        """BUG-8: optimista negativo + realista positivo → WARNING (no BLOCKING).

        Caso break-even: savings + IA revenue > OTA loss, matemáticamente correcto.
        """
        validator = CommercialGateValidator()
        scenarios = {"optimistic": -270950, "realistic": 3741696, "conservative": 7276953}
        result = validator._check_scenario_negative(scenarios)
        assert result.passed is False
        assert result.severity == "WARNING"
        assert result.gate_id == "CG-SCENARIO-NEGATIVE"

    def test_both_negative_blocks(self):
        """BUG-8: ambos escenarios negativos → BLOCKING (sin relajación).

        Cuando optimista Y realista son negativos, el hotel pierde incluso en
        el mejor caso — bloquear la publicación.
        """
        validator = CommercialGateValidator()
        scenarios = {"optimistic": -500000, "realistic": -200000, "conservative": 1000000}
        result = validator._check_scenario_negative(scenarios)
        assert result.passed is False
        assert result.severity == "BLOCKING"
        assert result.gate_id == "CG-SCENARIO-NEGATIVE"

    def test_optimistic_positive_passes(self):
        """Escenario optimista positivo debe pasar."""
        validator = CommercialGateValidator()
        scenarios = {"optimistic": 5000000, "realistic": 3741696, "conservative": 7276953}
        result = validator._check_scenario_negative(scenarios)
        assert result.passed is True

    def test_no_scenarios_passes(self):
        """Sin datos de escenarios, pasa (no puede validar)."""
        validator = CommercialGateValidator()
        result = validator._check_scenario_negative(None)
        assert result.passed is True


class TestCommercialGateIaBlockedClaim:
    """CG-IA-BLOCKED-CLAIM: 'IA Bloqueada' sin blocked_crawlers."""

    def test_blocked_claim_with_empty_crawlers_fails(self):
        """Claim de IA Bloqueada con blocked_crawlers vacío debe fallar."""
        validator = CommercialGateValidator()
        text = "La IA Bloqueada (Invisible para ChatGPT) es un problema crítico."
        ai_crawlers = {"blocked_crawlers": []}
        result = validator._check_ia_blocked_claim(text, ai_crawlers)
        assert result.passed is False
        assert result.severity == "BLOCKING"

    def test_blocked_claim_with_crawlers_passes(self):
        """Claim de IA Bloqueada con blocked_crawlers poblado debe pasar."""
        validator = CommercialGateValidator()
        text = "La IA Bloqueada (Invisible para ChatGPT) es un problema crítico."
        ai_crawlers = {"blocked_crawlers": ["GPTBot", "ClaudeBot"]}
        result = validator._check_ia_blocked_claim(text, ai_crawlers)
        assert result.passed is True

    def test_no_blocked_claim_passes(self):
        """Sin claim de IA Bloqueada, pasa."""
        validator = CommercialGateValidator()
        text = "La IA sin guía es un problema moderado."
        result = validator._check_ia_blocked_claim(text, None)
        assert result.passed is True

    def test_blocked_claim_no_crawler_data_fails(self):
        """Claim con ai_crawlers_data=None debe fallar (sin evidencia)."""
        validator = CommercialGateValidator()
        text = "IA Bloqueada — su hotel es invisible para ChatGPT."
        result = validator._check_ia_blocked_claim(text, None)
        assert result.passed is False


class TestCommercialGateRoiNegative:
    """CG-ROI-NEGATIVE: net_benefit_6m < 0 y sin onboarding plan."""

    def test_negative_roi_no_onboarding_fails(self):
        """ROI negativo sin plan de onboarding debe fallar."""
        validator = CommercialGateValidator()
        result = validator._check_roi_negative(
            net_benefit_6m=-5367168,
            roi=0.3,
            has_onboarding_plan=False,
        )
        assert result.passed is False
        assert result.severity == "BLOCKING"

    def test_negative_roi_with_onboarding_passes(self):
        """ROI negativo con plan de onboarding debe pasar."""
        validator = CommercialGateValidator()
        result = validator._check_roi_negative(
            net_benefit_6m=-5367168,
            roi=0.3,
            has_onboarding_plan=True,
        )
        assert result.passed is True

    def test_positive_roi_passes(self):
        """ROI positivo debe pasar."""
        validator = CommercialGateValidator()
        result = validator._check_roi_negative(
            net_benefit_6m=5000000,
            roi=2.5,
            has_onboarding_plan=False,
        )
        assert result.passed is True


class TestCommercialGateScenarioOrder:
    """CG-SCENARIO-ORDER: Orden de escenarios inválido."""

    def test_optimistic_negative_realistic_positive_order_passes(self):
        """BUG-8: optimista < 0 < realista → PASS (break-even, no BLOCKING).

        El optimista negativo es correcto cuando savings + IA > OTA loss.
        """
        validator = CommercialGateValidator()
        scenarios = {"optimistic": -270950, "realistic": 3741696, "conservative": 7276953}
        result = validator._check_scenario_order(scenarios)
        assert result.passed is True
        assert result.gate_id == "CG-SCENARIO-ORDER"

    def test_optimistic_less_than_realistic_same_sign_fails(self):
        """Optimista < realista cuando ambos tienen mismo signo → BLOCKING.

        Caso normal: orden invertido sin la excepción break-even.
        """
        validator = CommercialGateValidator()
        scenarios = {"optimistic": 100000, "realistic": 500000, "conservative": 50000}
        result = validator._check_scenario_order(scenarios)
        assert result.passed is False
        assert result.gate_id == "CG-SCENARIO-ORDER"

    def test_realistic_less_than_conservative_fails(self):
        """Realista < conservador debe fallar."""
        validator = CommercialGateValidator()
        scenarios = {"optimistic": 10000000, "realistic": 2000000, "conservative": 5000000}
        result = validator._check_scenario_order(scenarios)
        assert result.passed is False

    def test_correct_order_passes(self):
        """Orden correcto: optimista >= realista >= conservador."""
        validator = CommercialGateValidator()
        scenarios = {"optimistic": 7000000, "realistic": 3741696, "conservative": 2000000}
        result = validator._check_scenario_order(scenarios)
        assert result.passed is True


class TestCommercialGateClaimVsEvidence:
    """CG-CLAIM-VS-EVIDENCE: 'No aparece' cuando place_found=True y rating > 4.0."""

    def test_no_aparece_with_good_gbp_fails(self):
        """'No aparece' cuando place_found=True y rating 4.6 debe fallar."""
        validator = CommercialGateValidator()
        text = "El hotel no aparece en Google cuando un viajero busca hoteles en Pereira."
        result = validator._check_claim_vs_evidence(
            text, place_found=True, gbp_rating=4.6
        )
        assert result.passed is False
        assert result.severity == "BLOCKING"

    def test_no_aparece_with_low_rating_passes(self):
        """'No aparece' cuando rating < 4.0 pasa (claim puede ser válido)."""
        validator = CommercialGateValidator()
        text = "El hotel no aparece en Google."
        result = validator._check_claim_vs_evidence(
            text, place_found=True, gbp_rating=3.5
        )
        assert result.passed is True

    def test_no_no_aparece_passes(self):
        """Sin claim de 'no aparece' pasa."""
        validator = CommercialGateValidator()
        text = "Google sí lo encuentra, pero su ficha tiene fricciones."
        result = validator._check_claim_vs_evidence(
            text, place_found=True, gbp_rating=4.6
        )
        assert result.passed is True


class TestCommercialGateWhatsappLead:
    """CG-WHATSAPP-LEAD: WhatsApp no lidera narrativa inicial."""

    def test_whatsapp_in_first_section_passes(self):
        """WhatsApp en primeras líneas debe pasar."""
        validator = CommercialGateValidator()
        text = "## Hoy hay reservas escapándose\n\nEl conflicto de WhatsApp es evidente: su sitio web muestra un número y Google Maps otro. Esto confunde al cliente y pierde reservas directas."
        result = validator._check_whatsapp_lead(text)
        assert result.passed is True

    def test_no_whatsapp_in_lead_warns(self):
        """Sin WhatsApp en lead es WARNING."""
        validator = CommercialGateValidator()
        text = "## Análisis Técnico\n\nEl Schema del hotel presenta deficiencias. La puntuación AEO es baja."
        result = validator._check_whatsapp_lead(text)
        assert result.passed is False
        assert result.severity == "WARNING"


class TestCommercialGateOtaNarrative:
    """CG-OTA-NARRATIVE: Sin narrativa OTA."""

    def test_ota_terms_present_passes(self):
        """Términos OTA encontrados debe pasar."""
        validator = CommercialGateValidator()
        text = "Booking.com cobra comisiones del 15% que erosionan su rentabilidad."
        result = validator._check_ota_narrative(text)
        assert result.passed is True

    def test_no_ota_terms_warns(self):
        """Sin términos OTA debe advertir."""
        validator = CommercialGateValidator()
        text = "El Schema y el AEO son deficientes."
        result = validator._check_ota_narrative(text)
        assert result.passed is False
        assert result.severity == "WARNING"


class TestCommercialGateTechJargon:
    """CG-TECH-JARGON: Jerga técnica en vista gerencia."""

    def test_tech_jargon_detected_warns(self):
        """Schema/AEO en primeras líneas debe advertir."""
        validator = CommercialGateValidator()
        text = "\n".join(["# Diagnóstico"] + ["Schema y AEO son críticos."] * 10)
        result = validator._check_tech_jargon(text)
        assert result.passed is False
        assert result.severity == "WARNING"

    def test_no_jargon_passes(self):
        """Sin jerga técnica debe pasar."""
        validator = CommercialGateValidator()
        text = "## Reservas Directas\n\nWhatsApp, Google Maps y las reseñas son su vitrina digital."
        result = validator._check_tech_jargon(text)
        assert result.passed is True


class TestCommercialGateReport:
    """Pruebas del reporte agregado."""

    def test_all_passed_report(self):
        """Reporte con todos los gates pasando."""
        report = CommercialGateReport(
            all_passed=True,
            blocking_passed=True,
            results=[
                CommercialGateResult(
                    gate_id="CG-SCENARIO-ORDER",
                    name="Orden de escenarios",
                    passed=True,
                    severity="BLOCKING",
                    message="OK",
                    suggestion="",
                ),
            ],
            summary="All commercial gates passed.",
        )
        assert report.all_passed is True
        assert report.blocking_passed is True
        assert len(report.blocking_failures) == 0

    def test_blocking_failure_report(self):
        """Reporte con fallo bloqueante."""
        report = CommercialGateReport(
            all_passed=False,
            blocking_passed=False,
            results=[
                CommercialGateResult(
                    gate_id="CG-SCENARIO-NEGATIVE",
                    name="Escenario negativo",
                    passed=False,
                    severity="BLOCKING",
                    message="Optimista es negativo",
                    suggestion="Corregir clamp",
                ),
                CommercialGateResult(
                    gate_id="CG-WHATSAPP-LEAD",
                    name="WhatsApp no lidera",
                    passed=False,
                    severity="WARNING",
                    message="Sin WhatsApp en lead",
                    suggestion="Agregar WhatsApp",
                ),
            ],
            summary="1 BLOCKING failure(s): CG-SCENARIO-NEGATIVE",
        )
        assert report.all_passed is False
        assert report.blocking_passed is False
        assert len(report.blocking_failures) == 1
        assert report.blocking_failures[0].gate_id == "CG-SCENARIO-NEGATIVE"
        assert len(report.warnings) == 1

    def test_to_dict(self):
        """Verificar serialización a dict."""
        report = CommercialGateReport(
            all_passed=True,
            blocking_passed=True,
            results=[],
        )
        d = report.to_dict()
        assert d["all_passed"] is True
        assert d["blocking_passed"] is True
        assert isinstance(d["results"], list)


class TestCommercialGateValidateDiagnostic:
    """Pruebas de integración de validate_diagnostic()."""

    def test_all_clean_document_passes(self):
        """Documento limpio sin problemas debe pasar todos los gates."""
        validator = CommercialGateValidator()
        text = (
            "## Hoy hay reservas escapándose\n\n"
            "El conflicto de WhatsApp es evidente.\n\n"
            "## Fuga financiera\n\n"
            "Booking.com le cobra comisiones altas.\n\n"
            "## Qué hacemos\n\n"
            "Recuperamos sus reservas directas.\n\n"
        )
        scenarios = {"optimistic": 7000000, "realistic": 3741696, "conservative": 2000000}
        ai_crawlers = {"blocked_crawlers": []}

        report = validator.validate_diagnostic(
            diagnostic_text=text,
            scenarios=scenarios,
            ai_crawlers_data=ai_crawlers,
            place_found=True,
            gbp_rating=4.6,
        )
        assert report.blocking_passed is True

    def test_multiple_blocking_failures(self):
        """Documento con múltiples fallos bloqueantes.

        BUG-8: CG-SCENARIO-NEGATIVE es WARNING (optimista negativo + realista positivo)
        y CG-SCENARIO-ORDER es PASS (optimista < 0 < realista = break-even).
        Solo CG-IA-BLOCKED-CLAIM y CG-CLAIM-VS-EVIDENCE son BLOCKING aquí.
        """
        validator = CommercialGateValidator()
        text = (
            "La IA Bloqueada es crítica.\n\n"
            "El hotel no aparece en Google.\n\n"
        )
        # optimistic negativo + realista positivo: scenario-negative → WARNING, scenario-order → PASS
        scenarios = {"optimistic": -270950, "realistic": 3741696, "conservative": 7276953}
        ai_crawlers = {"blocked_crawlers": []}

        report = validator.validate_diagnostic(
            diagnostic_text=text,
            scenarios=scenarios,
            ai_crawlers_data=ai_crawlers,
            place_found=True,
            gbp_rating=4.6,
        )
        assert report.blocking_passed is False
        # CG-IA-BLOCKED-CLAIM + CG-CLAIM-VS-EVIDENCE = 2 BLOCKING failures
        # CG-SCENARIO-NEGATIVE = WARNING (no BLOCKING)
        # CG-SCENARIO-ORDER = PASS (break-even)
        assert len(report.blocking_failures) == 2
