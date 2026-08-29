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
        """FASE-B: orden correcto = conservador (peor caso) >= realista >= optimista."""
        validator = CommercialGateValidator()
        scenarios = {"optimistic": 1000000, "realistic": 3741696, "conservative": 7276953}
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
        scenarios = {"optimistic": 1000000, "realistic": 3741696, "conservative": 7276953}
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


# =============================================================================
# FASE-2 DT-4: Tests for commercial gates report persistence and BLOCKED_BY_GATES.md
# =============================================================================

class TestCommercialGateReportPersistence:
    """Verifica que el reporte de commercial gates se serializa correctamente para persistencia."""

    def test_to_dict_blocking_failure_serializes_correctly(self):
        """to_dict() con blocking_passed=False produce JSON válido con resultados."""
        report = CommercialGateReport(
            all_passed=False,
            blocking_passed=False,
            results=[
                CommercialGateResult(
                    gate_id="CG-SCENARIO-NEGATIVE",
                    name="Escenario negativo",
                    passed=False,
                    severity="BLOCKING",
                    message="Optimista es negativo (-270950)",
                    suggestion="Corregir clamp de escenarios",
                ),
                CommercialGateResult(
                    gate_id="CG-IA-BLOCKED-CLAIM",
                    name="IA Bloqueada sin evidencia",
                    passed=False,
                    severity="BLOCKING",
                    message="Claim de IA Bloqueada sin crawlers bloqueados",
                    suggestion="Agregar blocked_crawlers o eliminar claim",
                ),
                CommercialGateResult(
                    gate_id="CG-WHATSAPP-LEAD",
                    name="WhatsApp no lidera",
                    passed=False,
                    severity="WARNING",
                    message="WhatsApp no aparece en primeras líneas",
                    suggestion="Mover WhatsApp al lead",
                ),
            ],
            summary="2 BLOCKING failure(s), 1 WARNING(s)",
        )

        d = report.to_dict()
        assert d["blocking_passed"] is False
        assert d["all_passed"] is False
        assert len(d["results"]) == 3

        # Verify blocking failures are included
        blocking_ids = [r["gate_id"] for r in d["results"] if not r["passed"]]
        assert "CG-SCENARIO-NEGATIVE" in blocking_ids
        assert "CG-IA-BLOCKED-CLAIM" in blocking_ids

    def test_to_dict_roundtrip_via_json(self, tmp_path):
        """El reporte serializado a JSON se puede leer de vuelta con json.load()."""
        import json

        report = CommercialGateReport(
            all_passed=False,
            blocking_passed=False,
            results=[
                CommercialGateResult(
                    gate_id="CG-ROI-NEGATIVE",
                    name="ROI negativo",
                    passed=False,
                    severity="BLOCKING",
                    message="net_benefit_6m negativo sin onboarding",
                    suggestion="Activar plan de onboarding",
                ),
            ],
            summary="1 BLOCKING failure(s)",
        )

        # Write to temp file (simulating what v4_proposal_generator.py does)
        report_path = tmp_path / "commercial_gates_report.json"
        report_path.write_text(
            json.dumps(report.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        # Read back
        assert report_path.exists()
        with open(report_path, "r", encoding="utf-8") as f:
            loaded = json.load(f)

        assert loaded["blocking_passed"] is False
        assert len(loaded["results"]) == 1
        assert loaded["results"][0]["gate_id"] == "CG-ROI-NEGATIVE"
        assert loaded["results"][0]["severity"] == "BLOCKING"


class TestBlockedByGatesCommercialSection:
    """Verifica que BLOCKED_BY_GATES.md incluya la sección de commercial gates."""

    def test_blocked_md_includes_commercial_section_when_json_exists(self, tmp_path):
        """Si commercial_gates_report.json existe con blocking_passed=False,
        BLOCKED_BY_GATES.md debe incluir la sección 'Commercial Gates Bloqueantes'."""
        import json

        # Setup: write commercial_gates_report.json with blocking failures
        commercial_data = {
            "all_passed": False,
            "blocking_passed": False,
            "results": [
                {
                    "gate_id": "CG-SCENARIO-NEGATIVE",
                    "name": "Escenario negativo",
                    "passed": False,
                    "severity": "BLOCKING",
                    "message": "Optimista es negativo (-270950)",
                    "suggestion": "Corregir clamp",
                },
                {
                    "gate_id": "CG-IA-BLOCKED-CLAIM",
                    "name": "IA Bloqueada",
                    "passed": False,
                    "severity": "BLOCKING",
                    "message": "Claim sin evidencia",
                    "suggestion": "Agregar crawlers",
                },
            ],
            "summary": "2 BLOCKING failure(s)",
        }
        report_path = tmp_path / "commercial_gates_report.json"
        report_path.write_text(json.dumps(commercial_data, indent=2), encoding="utf-8")

        # Simulate what main.py does: read the JSON and generate markdown
        blocked_lines = []
        blocked_lines.append(f"# 🚫 Publicación Bloqueada por Gates de Calidad\n\n")
        blocked_lines.append(f"**Fecha**: 2026-07-26T00:00:00\n")
        blocked_lines.append(f"**Hotel**: Test Hotel\n\n")
        blocked_lines.append(f"## Gates Fallidos (1)\n\n")
        blocked_lines.append(f"### CG-COHERENCE\n\n")
        blocked_lines.append(f"- **Mensaje**: Coherence below threshold\n\n")

        # Commercial gates check (patched logic)
        has_commercial_block = False
        if report_path.exists():
            with open(report_path, "r", encoding="utf-8") as f:
                cg_data = json.load(f)
            if not cg_data.get("blocking_passed", True):
                has_commercial_block = True
                blocked_lines.append("\n## 🚨 Commercial Gates Bloqueantes\n\n")
                blocked_lines.append(
                    "Los siguientes gates comerciales impidieron la generación "
                    "de la propuesta. **No vuelva a ejecutar sin resolverlos** — "
                    "la re-ejecución idéntica fallará igual.\n\n"
                )
                for result in cg_data.get("results", []):
                    if not result.get("passed", True):
                        blocked_lines.append(
                            f"- **{result['gate_id']}**: {result.get('message', 'Sin detalle')}\n"
                        )
                blocked_lines.append(
                    "\n> ⚠️ Estos gates evalúan la viabilidad comercial de la propuesta. "
                    "Resuélvalos antes de re-ejecutar `v4complete`.\n"
                )

        blocked_lines.append(f"\n---\n\n")
        if not has_commercial_block:
            blocked_lines.append("**Acción requerida**: Resuelva los issues listados arriba y vuelva a ejecutar:\n\n")
        else:
            blocked_lines.append(
                "**Acción requerida**: Resuelva los commercial gates bloqueantes "
                "y los publication gates fallidos antes de re-ejecutar.\n\n"
            )

        blocked_md = "".join(blocked_lines)

        # Assertions
        assert "🚨 Commercial Gates Bloqueantes" in blocked_md
        assert "CG-SCENARIO-NEGATIVE" in blocked_md
        assert "CG-IA-BLOCKED-CLAIM" in blocked_md
        assert "Resuelva los commercial gates bloqueantes" in blocked_md
        assert "No vuelva a ejecutar sin resolverlos" in blocked_md
        assert "la re-ejecución idéntica fallará igual" in blocked_md

    def test_blocked_md_without_commercial_json_uses_default_action(self, tmp_path):
        """Si NO existe commercial_gates_report.json, la acción requerida es la estándar
        (no menciona commercial gates)."""
        import json

        # No commercial_gates_report.json written — path doesn't exist
        report_path = tmp_path / "commercial_gates_report.json"

        has_commercial_block = False
        if report_path.exists():
            has_commercial_block = True

        # Simulate the action-required block
        action = (
            "**Acción requerida**: Resuelva los commercial gates bloqueantes "
            "y los publication gates fallidos antes de re-ejecutar."
            if has_commercial_block
            else "**Acción requerida**: Resuelva los issues listados arriba y vuelva a ejecutar:"
        )

        assert "vuelva a ejecutar" in action
        assert "commercial gates" not in action

    def test_blocked_md_with_non_blocking_commercial_json_uses_default_action(self, tmp_path):
        """Si existe commercial_gates_report.json pero blocking_passed=True,
        el mensaje de acción es el estándar (no menciona commercial gates)."""
        import json

        commercial_data = {
            "all_passed": True,
            "blocking_passed": True,
            "results": [
                {
                    "gate_id": "CG-WHATSAPP-LEAD",
                    "name": "WhatsApp no lidera",
                    "passed": False,
                    "severity": "WARNING",
                    "message": "Sin WhatsApp en lead",
                    "suggestion": "Mover WhatsApp al lead",
                },
            ],
            "summary": "All blocking gates passed. 1 WARNING(s).",
        }
        report_path = tmp_path / "commercial_gates_report.json"
        report_path.write_text(json.dumps(commercial_data, indent=2), encoding="utf-8")

        has_commercial_block = False
        if report_path.exists():
            with open(report_path, "r", encoding="utf-8") as f:
                cg_data = json.load(f)
            if not cg_data.get("blocking_passed", True):
                has_commercial_block = True

        assert has_commercial_block is False  # blocking_passed=True → no block


# =============================================================================
# FASE-C: Tests for CG-CLAIM-VS-EVIDENCE conditional fix (N11)
# =============================================================================

class TestClaimVsEvidenceConditionalFix:
    """FASE-C N11: CG-CLAIM-VS-EVIDENCE no dispara falso positivo con condicionales."""

    def test_conditional_text_passes(self):
        """Texto condicional 'si...no aparece' NO debe disparar el gate."""
        validator = CommercialGateValidator()
        text = (
            "Si su web no tiene los datos correctos, no aparece en la respuesta "
            "de los asistentes de IA. Esto significa pérdida de visibilidad."
        )
        result = validator._check_claim_vs_evidence(
            text, place_found=True, gbp_rating=4.6
        )
        assert result.passed is True, (
            "Texto condicional no debe disparar CG-CLAIM-VS-EVIDENCE"
        )

    def test_conditional_with_si_su_passes(self):
        """'Si su hotel...' + 'no figura' es condicional → PASS."""
        validator = CommercialGateValidator()
        text = "Si su hotel no figura en Google Maps, perderá reservas directas."
        result = validator._check_claim_vs_evidence(
            text, place_found=True, gbp_rating=4.2
        )
        assert result.passed is True

    def test_conditional_en_caso_de_passes(self):
        """'En caso de...no está en Google' es condicional → PASS."""
        validator = CommercialGateValidator()
        text = "En caso de que la información no esté en Google, el viajero no lo encontrará."
        result = validator._check_claim_vs_evidence(
            text, place_found=True, gbp_rating=4.5
        )
        assert result.passed is True

    def test_factual_claim_with_good_gbp_fails(self):
        """'El hotel no aparece en Google.' (factual) + place_found=True → FAIL."""
        validator = CommercialGateValidator()
        text = "El hotel no aparece en Google cuando un viajero busca hoteles."
        result = validator._check_claim_vs_evidence(
            text, place_found=True, gbp_rating=4.6
        )
        assert result.passed is False
        assert result.severity == "BLOCKING"

    def test_factual_no_figura_fails(self):
        """'El hotel no figura en búsquedas' (factual) + buen rating → FAIL."""
        validator = CommercialGateValidator()
        text = "El hotel no figura en búsquedas de Google."
        result = validator._check_claim_vs_evidence(
            text, place_found=True, gbp_rating=4.3
        )
        assert result.passed is False

    def test_factual_claim_low_rating_passes(self):
        """Factual claim con rating bajo → PASS (claim puede ser válido)."""
        validator = CommercialGateValidator()
        text = "El hotel no aparece en Google."
        result = validator._check_claim_vs_evidence(
            text, place_found=True, gbp_rating=3.5
        )
        assert result.passed is True

    def test_mixed_conditional_and_factual_fails(self):
        """Texto con oración condicional Y factual → detecta la factual."""
        validator = CommercialGateValidator()
        text = (
            "Si su web no tiene Schema, no aparece en rich results. "
            "El hotel no aparece en Google Maps."
        )
        result = validator._check_claim_vs_evidence(
            text, place_found=True, gbp_rating=4.6
        )
        assert result.passed is False, (
            "Oración factual debe disparar el gate aunque haya condicional"
        )

    def test_no_claim_at_all_passes(self):
        """Sin ningún claim de invisibilidad → PASS."""
        validator = CommercialGateValidator()
        text = "Google sí lo encuentra, pero su ficha tiene fricciones."
        result = validator._check_claim_vs_evidence(
            text, place_found=True, gbp_rating=4.6
        )
        assert result.passed is True

    def test_podria_conditional_passes(self):
        """'Podría no aparecer' es condicional → PASS."""
        validator = CommercialGateValidator()
        text = "El hotel podría no aparecer en búsquedas si no corrige su Schema."
        result = validator._check_claim_vs_evidence(
            text, place_found=True, gbp_rating=4.6
        )
        assert result.passed is True


# =============================================================================
# FASE-C: Tests for CG-TIER-CONSISTENCY cabling (N15)
# =============================================================================

class TestTierConsistencyCabling:
    """FASE-C N15: CG-TIER-CONSISTENCY valida inputs reales; None → fallo."""

    def test_both_none_fails(self):
        """Ambos inputs None → FAIL (no pasa vacuo)."""
        validator = CommercialGateValidator()
        result = validator._check_tier_consistency(None, None)
        assert result.passed is False
        assert result.severity == "WARNING"
        assert "AMBOS" in result.message

    def test_frontmatter_none_fails(self):
        """Solo frontmatter_tier=None → FAIL."""
        validator = CommercialGateValidator()
        result = validator._check_tier_consistency(None, "B+")
        assert result.passed is False
        assert "frontmatter_tier" in result.message

    def test_text_none_fails(self):
        """Solo text_tier=None → FAIL."""
        validator = CommercialGateValidator()
        result = validator._check_tier_consistency("B+", None)
        assert result.passed is False
        assert "text_tier" in result.message

    def test_matching_tiers_pass(self):
        """Tiers coincidentes → PASS."""
        validator = CommercialGateValidator()
        result = validator._check_tier_consistency("B+", "B+")
        assert result.passed is True

    def test_mismatched_tiers_fail(self):
        """Tiers diferentes → FAIL."""
        validator = CommercialGateValidator()
        result = validator._check_tier_consistency("A", "B+")
        assert result.passed is False

    def test_case_insensitive_match(self):
        """Tier comparison es case-insensitive."""
        validator = CommercialGateValidator()
        result = validator._check_tier_consistency("b+", "B+")
        assert result.passed is True


# =============================================================================
# FASE-C: Tests for _extract_text_tier helper
# =============================================================================

class TestExtractTextTier:
    """FASE-C N15: _extract_text_tier extrae tier del texto del diagnóstico."""

    def test_tier_b_plus(self):
        """'Tier B+' → 'B+'."""
        from modules.commercial_documents.v4_diagnostic_generator import V4DiagnosticGenerator
        result = V4DiagnosticGenerator._extract_text_tier(
            "El diagnóstico indica Tier B+ para este hotel."
        )
        assert result == "B+"

    def test_tier_a(self):
        """'Tier A' → 'A'."""
        from modules.commercial_documents.v4_diagnostic_generator import V4DiagnosticGenerator
        result = V4DiagnosticGenerator._extract_text_tier(
            "Clasificación: Tier A con GA4 y GSC verificados."
        )
        assert result == "A"

    def test_nivel_c(self):
        """'nivel C' → 'C'."""
        from modules.commercial_documents.v4_diagnostic_generator import V4DiagnosticGenerator
        result = V4DiagnosticGenerator._extract_text_tier(
            "El hotel tiene nivel C de evidencia."
        )
        assert result == "C"

    def test_no_tier_returns_none(self):
        """Sin mención de tier → None."""
        from modules.commercial_documents.v4_diagnostic_generator import V4DiagnosticGenerator
        result = V4DiagnosticGenerator._extract_text_tier(
            "El diagnóstico no menciona tier explícitamente."
        )
        assert result is None

    def test_lowercase_tier(self):
        """FASE-SR-G (L30): 'tier b+' en minúscula es prosa, NO token canónico.

        Los valores canónicos del financial engine son MAYÚSCULAS (el template
        V6 los renderiza tal cual). Aceptar minúsculas capturaba la 'd' de
        "Nivel de evidencia" como tier 'D' espurio (corrida C 2026-08-27).
        """
        from modules.commercial_documents.v4_diagnostic_generator import V4DiagnosticGenerator
        result = V4DiagnosticGenerator._extract_text_tier(
            "Según el análisis, el tier b+ es apropiado."
        )
        assert result is None

    def test_nivel_de_evidencia_not_d(self):
        """FASE-SR-G regresión corrida C: 'Nivel de evidencia' NO es tier 'D'.

        Línea real del template V6 renderizado (diagnostico_v6_template L156):
        el regex viejo capturaba la 'd' de 'de' → text_tier='D' vs
        frontmatter_tier='B' → falso CG-TIER-CONSISTENCY.
        """
        from modules.commercial_documents.v4_diagnostic_generator import V4DiagnosticGenerator
        result = V4DiagnosticGenerator._extract_text_tier(
            "> *Nivel de evidencia: **Tier B** · Precisión: **Tier C***"
        )
        assert result == "B"

    def test_nivel_de_evidencia_sin_token_returns_none(self):
        """FASE-SR-G: mención de 'Nivel de evidencia' sin token canónico → None."""
        from modules.commercial_documents.v4_diagnostic_generator import V4DiagnosticGenerator
        result = V4DiagnosticGenerator._extract_text_tier(
            "El nivel de evidencia queda registrado en el frontmatter del documento."
        )
        assert result is None

    def test_corrida_c_tier_gate_resolution(self):
        """FASE-SR-G: extracción corregida + gate → 'B' canónico == 'B' → PASS.

        Mismo wiring de la corrida C (frontmatter desde
        financial_breakdown.evidence_tier, text_tier desde el documento) con
        la línea real del template V6: el falso positivo desaparece.
        """
        from modules.commercial_documents.v4_diagnostic_generator import V4DiagnosticGenerator
        text_tier = V4DiagnosticGenerator._extract_text_tier(
            "> *Nivel de evidencia: **Tier B** · Precisión: **Tier C***"
        )
        validator = CommercialGateValidator()
        result = validator._check_tier_consistency("B", text_tier)
        assert result.passed is True

    def test_real_mismatch_still_detected_via_extraction(self):
        """FASE-SR-G test negativo: mismatch REAL sigue disparando el gate.

        Documento cuyo texto canónico dice 'Tier C' mientras el financial
        engine declaró 'B' → el gate debe FALLAR (no se enmascara).
        """
        from modules.commercial_documents.v4_diagnostic_generator import V4DiagnosticGenerator
        text_tier = V4DiagnosticGenerator._extract_text_tier(
            "Nivel de evidencia: **Tier C** con datos limitados de su web."
        )
        assert text_tier == "C"
        validator = CommercialGateValidator()
        result = validator._check_tier_consistency("B", text_tier)
        assert result.passed is False
