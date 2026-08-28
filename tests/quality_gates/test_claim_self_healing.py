"""Tests FASE-SR-C (D-PF2): Self-Healing Loop para CG-CLAIM-VS-EVIDENCE.

Criterios del prompt de fase (L-SR5):
1. Claim contradictorio con GBP → regeneración corrige el claim →
   0 gates blocking de CG-CLAIM-VS-EVIDENCE en la 2ª evaluación.
2. Claim persistente (suggestion ignorado) → escalado a BLOCKED real.
3. Guard anti-bucle — nunca más de 1 regeneración.

La re-validación usa el ``CommercialGateValidator`` REAL (contrato contra
fuente dinámica, L3): el documento se considera corregido solo si la 2ª
evaluación no produce bloqueos del gate.
"""

from modules.quality_gates import claim_self_healing as csh
from modules.quality_gates.claim_self_healing import (
    GATE_ID_CLAIM_VS_EVIDENCE,
    STATUS_ESCALATED,
    STATUS_NO_NEEDED,
    STATUS_RESOLVED,
    ClaimSelfHealer,
)
from modules.quality_gates.commercial_gate import CommercialGateValidator


# Evidencia GBP que contradice claims de invisibilidad (caso Salento Real:
# place_found=True, rating=4.5/5.0 — CONTEXT-SALENTOREAL §7.2).
GBP_FOUND = {"place_found": True, "gbp_rating": 4.5}


def make_validator() -> CommercialGateValidator:
    return CommercialGateValidator()


def validate_diagnostic(text: str, **overrides):
    """Validación comercial con parámetros fijos (GBP contradice invisibilidad)."""
    params = {
        "scenarios": None,
        "ai_crawlers_data": None,
        "place_found": GBP_FOUND["place_found"],
        "gbp_rating": GBP_FOUND["gbp_rating"],
        "frontmatter_tier": None,
        "text_tier": None,
        "ga4_available": False,
        "gsc_available": False,
        "financial_json": None,
    }
    params.update(overrides)
    return make_validator().validate_diagnostic(diagnostic_text=text, **params)


def claim_blocking(report):
    return [r for r in report.blocking_failures if r.gate_id == GATE_ID_CLAIM_VS_EVIDENCE]


class TestLoopCorrigeClaim:
    """Criterio T3-1: regeneración corrige el claim → 2ª evaluación 0 blocking."""

    def test_claim_factual_con_gbp_se_resuelve(self):
        doc = (
            "# Diagnóstico\n\n"
            "El hotel no aparece en Google cuando un viajero busca hoteles "
            "en Pereira. Esto explica la caída de reservas directas.\n"
        )
        report = validate_diagnostic(doc)
        assert len(claim_blocking(report)) == 1

        healer = ClaimSelfHealer()
        healing = healer.heal(
            document_text=doc,
            report=report,
            revalidate_fn=validate_diagnostic,
        )

        assert healing.status == STATUS_RESOLVED
        assert healing.attempts == 1
        assert healing.resolved_gates == [GATE_ID_CLAIM_VS_EVIDENCE]

        # 2ª evaluación = 0 blocking de CG-CLAIM-VS-EVIDENCE
        second = validate_diagnostic(healing.healed_text)
        assert claim_blocking(second) == []

        # El claim trazable del suggestion quedó en el documento
        assert "Google sí lo encuentra" in healing.healed_text
        assert "no aparece" not in healing.healed_text

    def test_reemplazo_preserva_estructura_de_lista_y_etiqueta(self):
        doc = (
            "## Brechas\n\n"
            "- **Google Business Profile**: no aparece en búsquedas locales.\n"
        )
        report = validate_diagnostic(doc)
        assert len(claim_blocking(report)) == 1

        healing = ClaimSelfHealer().heal(doc, report, validate_diagnostic)

        assert healing.status == STATUS_RESOLVED
        healed_line = [
            l for l in healing.healed_text.splitlines()
            if "Google sí lo encuentra" in l
        ][0]
        assert healed_line.startswith("- **Google Business Profile**:")
        assert healed_line.rstrip().endswith(".")

    def test_varias_oraciones_ofensivas_se_corrigen_en_una_regeneracion(self):
        doc = (
            "Su GBP no figura en búsquedas de la zona.\n\n"
            "El hotel no está en Google Maps y los clientes van a Booking.\n"
        )
        report = validate_diagnostic(doc)
        assert len(claim_blocking(report)) == 1

        healing = ClaimSelfHealer().heal(doc, report, validate_diagnostic)

        assert healing.status == STATUS_RESOLVED
        assert healing.attempts == 1
        # Ambas oraciones corregidas con UNA regeneración
        second = validate_diagnostic(healing.healed_text)
        assert claim_blocking(second) == []
        assert healing.healed_text.count("Google sí lo encuentra") == 2

    def test_suggestion_real_del_gate_es_la_restriccion_aplicada(self):
        """Contrato: el texto aplicado proviene del suggestion del gate."""
        doc = "El hotel no aparece en Google."
        report = validate_diagnostic(doc)
        failure = claim_blocking(report)[0]

        healer = ClaimSelfHealer()
        expected_claim = healer._extract_traceable_claim(failure.suggestion)

        assert "Google sí lo encuentra" in expected_claim
        healing = healer.heal(doc, report, validate_diagnostic)
        assert expected_claim in healing.healed_text

    def test_claim_phrase_extraida_del_message(self):
        doc = "El hotel no aparece en Google."
        report = validate_diagnostic(doc)
        failure = claim_blocking(report)[0]

        healer = ClaimSelfHealer()
        assert healer.extract_claim_phrase(failure.message) == "no aparece"


class TestInstruccionesYOtrosSujetos:
    """Oraciones sin claim contrastable con GBP se neutralizan, no se borran."""

    def test_instruccion_al_lector_se_neutraliza(self):
        doc = (
            "→ Usted mismo puede hacerlo desde su celular: busque su hotel "
            "y anote qué información no aparece.\n"
        )
        report = validate_diagnostic(doc)
        assert len(claim_blocking(report)) == 1

        healing = ClaimSelfHealer().heal(doc, report, validate_diagnostic)

        assert healing.status == STATUS_RESOLVED
        assert "anote qué información falta" in healing.healed_text
        strategies = [a.strategy for a in healing.actions]
        assert "instruction_neutralized" in strategies
        # La instrucción se preserva (no se reemplaza por el claim trazable)
        assert "Usted mismo puede hacerlo" in healing.healed_text

    def test_claim_sobre_otro_sujeto_se_neutraliza_sin_inventar_visibilidad(self):
        doc = "El botón de WhatsApp no aparece en el sitio web del hotel.\n"
        report = validate_diagnostic(doc)
        assert len(claim_blocking(report)) == 1

        healing = ClaimSelfHealer().heal(doc, report, validate_diagnostic)

        assert healing.status == STATUS_RESOLVED
        assert "El botón de WhatsApp falta en el sitio web del hotel." in (
            healing.healed_text
        )
        # No se inventa visibilidad Google para un claim del sitio
        assert "Google sí lo encuentra" not in healing.healed_text

    def test_oraciones_condicionales_quedan_intactas(self):
        doc = (
            "Si su web no tiene los datos correctos, no aparece en la "
            "respuesta de los asistentes de IA.\n"
        )
        report = validate_diagnostic(doc)
        assert claim_blocking(report) == []

        healing = ClaimSelfHealer().heal(doc, report, validate_diagnostic)

        assert healing.status == STATUS_NO_NEEDED
        assert healing.healed_text == ""
        assert healing.attempts == 0

    def test_oracion_con_rating_bajo_no_dispara_loop(self):
        """Rating < 4.0 → el claim puede ser válido → no_needed."""
        doc = "El hotel no aparece en Google."
        report = validate_diagnostic(doc, gbp_rating=3.5)
        assert claim_blocking(report) == []

        healing = ClaimSelfHealer().heal(doc, report, validate_diagnostic)

        assert healing.status == STATUS_NO_NEEDED


class TestEscaladoABlocked:
    """Criterio T3-2: claim persistente (suggestion ignorado) → BLOCKED real."""

    def test_persistencia_escalada(self, monkeypatch):
        doc = "El hotel no aparece en Google cuando un viajero busca hoteles."
        report = validate_diagnostic(doc)

        healer = ClaimSelfHealer()

        def _rewrite_ignorado(text, claim):
            # Simula "suggestion ignorado": el documento no cambia
            return text, []

        monkeypatch.setattr(healer, "_rewrite_document", _rewrite_ignorado)

        healing = healer.heal(doc, report, validate_diagnostic)

        assert healing.status == STATUS_ESCALATED
        assert healing.escalated_gates == [GATE_ID_CLAIM_VS_EVIDENCE]
        assert healing.attempts == 1
        # La re-validación sigue detectando el claim
        assert len(claim_blocking(healing.revalidated_report)) == 1

    def test_resolved_gates_vacio_en_escalada(self, monkeypatch):
        doc = "El hotel no aparece en Google."
        report = validate_diagnostic(doc)
        healer = ClaimSelfHealer()
        monkeypatch.setattr(
            healer, "_rewrite_document", lambda text, claim: (text, [])
        )
        healing = healer.heal(doc, report, validate_diagnostic)
        assert healing.resolved_gates == []


class TestGuardAntiBucle:
    """Criterio T3-3: nunca más de 1 regeneración."""

    def test_segunda_llamada_no_reescribe_ni_revalida(self, monkeypatch):
        doc = "El hotel no aparece en Google."
        report = validate_diagnostic(doc)

        healer = ClaimSelfHealer()
        revalidate_calls = {"n": 0}

        def _spy_revalidate(text):
            revalidate_calls["n"] += 1
            return validate_diagnostic(text)

        monkeypatch.setattr(
            healer, "_rewrite_document", lambda text, claim: (text, [])
        )

        first = healer.heal(doc, report, _spy_revalidate)
        assert first.status == STATUS_ESCALATED
        assert first.attempts == 1
        assert revalidate_calls["n"] == 1

        # 2ª llamada sobre un claim que persiste: guard anti-bucle
        second = healer.heal(doc, first.revalidated_report, _spy_revalidate)
        assert second.status == STATUS_ESCALATED
        assert second.attempts == 1  # NO incrementa
        assert revalidate_calls["n"] == 1  # NO re-validó de nuevo

    def test_max_regenerations_constante(self):
        assert ClaimSelfHealer.MAX_REGENERATIONS == 1

    def test_custom_guard_respeta_limite(self):
        healer = ClaimSelfHealer(max_regenerations=1)
        assert healer._max_attempts == 1


class TestTrazabilidad:
    """El reporte final distingue resuelto por regeneración vs escalado."""

    def test_to_dict_resolved(self):
        doc = "El hotel no aparece en Google."
        report = validate_diagnostic(doc)
        healing = ClaimSelfHealer().heal(doc, report, validate_diagnostic)

        payload = healing.to_dict()
        assert payload["status"] == STATUS_RESOLVED
        assert payload["attempts"] == 1
        assert payload["max_attempts"] == 1
        assert payload["resolved_gates"] == [GATE_ID_CLAIM_VS_EVIDENCE]
        assert payload["escalated_gates"] == []
        assert len(payload["actions"]) >= 1
        assert payload["actions"][0]["strategy"] == "traceable_claim"

    def test_to_dict_escalated(self, monkeypatch):
        doc = "El hotel no aparece en Google."
        report = validate_diagnostic(doc)
        healer = ClaimSelfHealer()
        monkeypatch.setattr(
            healer, "_rewrite_document", lambda text, claim: (text, [])
        )
        healing = healer.heal(doc, report, validate_diagnostic)

        payload = healing.to_dict()
        assert payload["status"] == STATUS_ESCALATED
        assert payload["escalated_gates"] == [GATE_ID_CLAIM_VS_EVIDENCE]
        assert payload["resolved_gates"] == []

    def test_no_needed_to_dict(self):
        doc = "Google sí lo encuentra, pero su ficha tiene fricciones."
        report = validate_diagnostic(doc)
        healing = ClaimSelfHealer().heal(doc, report, validate_diagnostic)
        assert healing.to_dict()["status"] == STATUS_NO_NEEDED


class TestRegresionGateComercial:
    """El extractor de regex a constante de módulo no cambia el gate."""

    def test_gate_ignora_condicionales_igual_que_antes(self):
        v = make_validator()
        r = v._check_claim_vs_evidence(
            "Si su hotel no figura en Google Maps, perderá reservas.",
            place_found=True,
            gbp_rating=4.2,
        )
        assert r.passed is True

    def test_gate_detecta_factual_igual_que_antes(self):
        v = make_validator()
        r = v._check_claim_vs_evidence(
            "El hotel no figura en búsquedas de Google.",
            place_found=True,
            gbp_rating=4.3,
        )
        assert r.passed is False
        assert r.severity == "BLOCKING"

    def test_message_y_suggestion_tienen_formato_parseable(self):
        doc = "El hotel no aparece en Google."
        report = validate_diagnostic(doc)
        failure = claim_blocking(report)[0]
        healer = ClaimSelfHealer()
        assert healer.extract_claim_phrase(failure.message) is not None
        # Contrato: el suggestion real del gate provee el claim trazable
        # entrecomillado (no se usa el fallback del módulo).
        assert (
            healer._extract_traceable_claim(failure.suggestion)
            != csh._FALLBACK_TRACEABLE_CLAIM
        )
