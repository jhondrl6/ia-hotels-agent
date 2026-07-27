"""Commercial Gate Validator — bloquea/adiverte sobre problemas de copywriting.

Valida documentos comerciales (diagnóstico y propuesta) contra reglas de
copywriting definidas en .opencode/context/Copywriting.jsonl.

Gates Bloqueantes (BLOCKING): si fallan, el documento requiere corrección.
Gates Advisory (WARNING): no bloquean pero deben revisarse.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import re


# ──────────────────────────────────────────────────────────────
# Data Classes
# ──────────────────────────────────────────────────────────────

@dataclass
class CommercialGateResult:
    """Resultado individual de un gate comercial."""
    gate_id: str
    name: str
    passed: bool
    severity: str  # "BLOCKING" or "WARNING"
    message: str
    suggestion: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "gate_id": self.gate_id,
            "name": self.name,
            "passed": self.passed,
            "severity": self.severity,
            "message": self.message,
            "suggestion": self.suggestion,
        }


@dataclass
class CommercialGateReport:
    """Reporte agregado de todos los gates comerciales."""
    all_passed: bool
    blocking_passed: bool
    results: List[CommercialGateResult]
    summary: str = ""

    @property
    def blocking_failures(self) -> List[CommercialGateResult]:
        return [r for r in self.results if not r.passed and r.severity == "BLOCKING"]

    @property
    def warnings(self) -> List[CommercialGateResult]:
        return [r for r in self.results if not r.passed and r.severity == "WARNING"]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "all_passed": self.all_passed,
            "blocking_passed": self.blocking_passed,
            "results": [r.to_dict() for r in self.results],
            "summary": self.summary,
        }


# ──────────────────────────────────────────────────────────────
# Gate IDs
# ──────────────────────────────────────────────────────────────

BLOCKING_GATE_IDS = [
    "CG-SCENARIO-ORDER",
    "CG-SCENARIO-NEGATIVE",
    "CG-IA-BLOCKED-CLAIM",
    "CG-ROI-NEGATIVE",
    "CG-CLAIM-VS-EVIDENCE",
]

WARNING_GATE_IDS = [
    "CG-WHATSAPP-LEAD",
    "CG-OTA-NARRATIVE",
    "CG-TIER-CONSISTENCY",
    "CG-TECH-JARGON",
]

# Términos técnicos que no deben aparecer en las primeras 6 secciones (vista gerencia)
TECH_JARGON_TERMS = [
    "Schema", "AEO", "IAO", "Open Graph", "NAP", "Rich Snippets",
    "schema.org", "JSON-LD", "markup estructurado",
    # PROPUESTA-COMERCIAL FASE-D: términos adicionales
    "OpenRouter", "Perplexity", "Gemini", "GA4_PROPERTY_ID",
    "GSC_SITE_URL", "UTM", "iah-cli", "iahotels.co",
]


# ──────────────────────────────────────────────────────────────
# Validator
# ──────────────────────────────────────────────────────────────

class CommercialGateValidator:
    """Valida documentos comerciales contra reglas de copywriting.

    Uso:
        validator = CommercialGateValidator()
        report = validator.validate_diagnostic(
            diagnostic_text=doc,
            scenarios=scenarios,
            ai_crawlers_data=audit_result.ai_crawlers,
            place_found=audit_result.gbp_place_found,
            gbp_rating=audit_result.gbp_rating,
        )
        if not report.blocking_passed:
            # agregar alertas al documento
            ...
    """

    # ── Diagnostic Gates ─────────────────────────────────────

    def validate_diagnostic(
        self,
        diagnostic_text: str,
        scenarios: Any = None,
        ai_crawlers_data: Optional[Dict[str, Any]] = None,
        place_found: bool = False,
        gbp_rating: float = 0.0,
        frontmatter_tier: Optional[str] = None,
        text_tier: Optional[str] = None,
    ) -> CommercialGateReport:
        """Valida el documento de diagnóstico contra gates comerciales.

        Args:
            diagnostic_text: Texto completo del diagnóstico generado.
            scenarios: Objeto con atributos optimistic, realistic, conservative (o dict).
            ai_crawlers_data: Datos de crawlers de IA del audit (dict con blocked_crawlers).
            place_found: Si el lugar fue encontrado en GBP.
            gbp_rating: Rating de GBP (0.0-5.0).
            frontmatter_tier: Tier declarado en el frontmatter del documento.
            text_tier: Tier mencionado en el texto del documento.
        """
        results: List[CommercialGateResult] = []

        # CG-SCENARIO-ORDER: Orden de escenarios inválido
        results.append(self._check_scenario_order(scenarios))

        # CG-SCENARIO-NEGATIVE: Escenario negativo como recuperación
        results.append(self._check_scenario_negative(scenarios))

        # CG-IA-BLOCKED-CLAIM: "IA Bloqueada" sin evidencia
        results.append(self._check_ia_blocked_claim(diagnostic_text, ai_crawlers_data))

        # CG-CLAIM-VS-EVIDENCE: Claims no soportados por datos
        results.append(self._check_claim_vs_evidence(diagnostic_text, place_found, gbp_rating))

        # CG-WHATSAPP-LEAD: WhatsApp no lidera narrativa
        results.append(self._check_whatsapp_lead(diagnostic_text))

        # CG-OTA-NARRATIVE: Sin narrativa OTA
        results.append(self._check_ota_narrative(diagnostic_text))

        # CG-TIER-CONSISTENCY: Tier inconsistente
        results.append(self._check_tier_consistency(frontmatter_tier, text_tier))

        # CG-TECH-JARGON: Jerga técnica en vista gerencia
        results.append(self._check_tech_jargon(diagnostic_text))

        # Build report
        blocking_failed = [r for r in results if not r.passed and r.severity == "BLOCKING"]
        all_passed = len(blocking_failed) == 0 and all(
            r.passed for r in results if r.severity == "WARNING"
        )
        blocking_passed = len(blocking_failed) == 0

        summary_parts = []
        if blocking_failed:
            summary_parts.append(
                f"{len(blocking_failed)} BLOCKING failure(s): "
                + ", ".join(r.gate_id for r in blocking_failed)
            )
        warning_failed = [r for r in results if not r.passed and r.severity == "WARNING"]
        if warning_failed:
            summary_parts.append(
                f"{len(warning_failed)} WARNING(s): "
                + ", ".join(r.gate_id for r in warning_failed)
            )
        if not summary_parts:
            summary_parts.append("All commercial gates passed.")

        report = CommercialGateReport(
            all_passed=all_passed,
            blocking_passed=blocking_passed,
            results=results,
            summary=" | ".join(summary_parts),
        )
        return report

    # ── Proposal Gates ───────────────────────────────────────

    def validate_proposal(
        self,
        proposal_text: str,
        net_benefit_6m: float = 0.0,
        roi: float = 0.0,
        has_onboarding_plan: bool = False,
    ) -> CommercialGateReport:
        """Valida el documento de propuesta contra gates comerciales.

        Args:
            proposal_text: Texto completo de la propuesta generada.
            net_benefit_6m: Beneficio neto a 6 meses.
            roi: Retorno sobre inversión (e.g., 1.5 = 150%).
            has_onboarding_plan: Si hay plan de onboarding alternativo.
        """
        results: List[CommercialGateResult] = []

        # CG-ROI-NEGATIVE: ROI negativo como argumento de cierre
        results.append(self._check_roi_negative(net_benefit_6m, roi, has_onboarding_plan))

        # CG-OTA-NARRATIVE: Sin narrativa OTA
        results.append(self._check_ota_narrative(proposal_text))

        # CG-TECH-JARGON: Jerga técnica en propuesta
        # (La propuesta es vista gerencia, aplica mismo gate)
        results.append(self._check_tech_jargon(proposal_text))

        blocking_failed = [r for r in results if not r.passed and r.severity == "BLOCKING"]
        all_passed = len(blocking_failed) == 0 and all(
            r.passed for r in results if r.severity == "WARNING"
        )
        blocking_passed = len(blocking_failed) == 0

        summary_parts = []
        if blocking_failed:
            summary_parts.append(
                f"{len(blocking_failed)} BLOCKING failure(s): "
                + ", ".join(r.gate_id for r in blocking_failed)
            )
        warning_failed = [r for r in results if not r.passed and r.severity == "WARNING"]
        if warning_failed:
            summary_parts.append(
                f"{len(warning_failed)} WARNING(s): "
                + ", ".join(r.gate_id for r in warning_failed)
            )
        if not summary_parts:
            summary_parts.append("All commercial gates passed.")

        return CommercialGateReport(
            all_passed=all_passed,
            blocking_passed=blocking_passed,
            results=results,
            summary=" | ".join(summary_parts),
        )

    # ── Individual Gate Checks ───────────────────────────────

    @staticmethod
    def _extract_scenario_values(scenarios: Any):
        """Extract numeric scenario values from either dataclass or dict.

        Normalizes both paths to numeric values by extracting
        .monthly_loss_central from Scenario objects when present.
        """
        if scenarios is None:
            return None, None, None

        if isinstance(scenarios, dict):
            optimistic = scenarios.get("optimistic")
            realistic = scenarios.get("realistic")
            conservative = scenarios.get("conservative")
        else:
            optimistic = getattr(scenarios, "optimistic", None)
            realistic = getattr(scenarios, "realistic", None)
            conservative = getattr(scenarios, "conservative", None)

        # Normalize to numeric: extract monthly_loss_central if values are objects
        def _to_numeric(val):
            if val is None:
                return None
            if isinstance(val, (int, float)):
                return val
            return getattr(val, "monthly_loss_central", None)

        return _to_numeric(optimistic), _to_numeric(realistic), _to_numeric(conservative)

    def _check_scenario_order(self, scenarios: Any) -> CommercialGateResult:
        """CG-SCENARIO-ORDER: optimista < realista o realista < conservador."""
        optimistic, realistic, conservative = self._extract_scenario_values(scenarios)
        if optimistic is None or realistic is None or conservative is None:
            return CommercialGateResult(
                gate_id="CG-SCENARIO-ORDER",
                name="Orden de escenarios inválido",
                passed=True,
                severity="BLOCKING",
                message="Sin datos de escenarios para validar orden.",
                suggestion="",
            )

        if optimistic < realistic:
            # BUG-8 fix: cuando optimista < 0 < realista, el optimista negativo
            # es break-even (savings + IA > OTA loss) — no bloquear
            if optimistic < 0 < realistic:
                return CommercialGateResult(
                    gate_id="CG-SCENARIO-ORDER",
                    name="Orden de escenarios inválido",
                    passed=True,
                    severity="BLOCKING",
                    message=f"Escenario optimista ({optimistic:,.0f}) < 0 < realista ({realistic:,.0f}). "
                            f"Reinterpretación break-even: el optimista negativo es correcto cuando "
                            f"ahorros + IA revenue > fuga OTA. El mejor caso no tiene pérdida neta.",
                    suggestion="",
                )
            return CommercialGateResult(
                gate_id="CG-SCENARIO-ORDER",
                name="Orden de escenarios inválido",
                passed=False,
                severity="BLOCKING",
                message=f"Escenario optimista ({optimistic:,.0f}) < realista ({realistic:,.0f}). "
                        f"El optimista debe ser el valor más alto.",
                suggestion="Revisar _build_scenario_table_rows: verificar clamp y signos. "
                          "El optimista debe ser >= realista.",
            )

        if realistic < conservative:
            return CommercialGateResult(
                gate_id="CG-SCENARIO-ORDER",
                name="Orden de escenarios inválido",
                passed=False,
                severity="BLOCKING",
                message=f"Escenario realista ({realistic:,.0f}) < conservador ({conservative:,.0f}). "
                        f"El realista debe ser >= conservador.",
                suggestion="Revisar _build_scenario_table_rows: verificar fórmulas. "
                          "El realista debe ser >= conservador.",
            )

        return CommercialGateResult(
            gate_id="CG-SCENARIO-ORDER",
            name="Orden de escenarios inválido",
            passed=True,
            severity="BLOCKING",
            message="Orden de escenarios válido: optimista ≥ realista ≥ conservador.",
            suggestion="",
        )

    def _check_scenario_negative(self, scenarios: Any) -> CommercialGateResult:
        """CG-SCENARIO-NEGATIVE: optimista < 0 mostrado en tabla de recuperación.

        BUG-8 fix (Opción B — reinterpretación comercial):
        Cuando optimista < 0 PERO realista > 0, el resultado negativo es
        matemáticamente correcto (savings + IA revenue > OTA loss = break-even).
        Se degrada a WARNING en lugar de BLOCKING.
        Solo se mantiene BLOCKING cuando AMBOS escenarios son negativos.
        """
        optimistic, realistic, _ = self._extract_scenario_values(scenarios)
        if optimistic is None:
            return CommercialGateResult(
                gate_id="CG-SCENARIO-NEGATIVE",
                name="Escenario negativo como recuperación",
                passed=True,
                severity="BLOCKING",
                message="Sin datos de escenarios para validar.",
                suggestion="",
            )

        if optimistic < 0:
            # BUG-8: cuando el optimista es negativo pero el realista positivo,
            # es el caso break-even (savings + IA > OTA loss): WARNING, no BLOCKING
            if realistic is not None and realistic > 0:
                return CommercialGateResult(
                    gate_id="CG-SCENARIO-NEGATIVE",
                    name="Escenario negativo como recuperación",
                    passed=False,
                    severity="WARNING",
                    message=f"Escenario optimista es negativo ({optimistic:,.0f}) "
                            f"pero realista es positivo ({realistic:,.0f}). "
                            f"Interpretación break-even: savings + IA revenue > OTA loss "
                            f"— el mejor caso cubre la fuga.",
                    suggestion="Validar que es comercialmente correcto mostrar el optimista "
                              "como 'sin pérdida neta' (break-even). "
                              "Si savings + IA > OTA loss, el optimista negativo es "
                              "matemáticamente correcto: no hay pérdida neta en el mejor caso.",
                )

            # Ambos escenarios negativos: mantener BLOCKING
            return CommercialGateResult(
                gate_id="CG-SCENARIO-NEGATIVE",
                name="Escenario negativo como recuperación",
                passed=False,
                severity="BLOCKING",
                message=f"Escenario optimista es negativo ({optimistic:,.0f}). "
                        f"No puede mostrarse como recuperación.",
                suggestion="Si el hotel tiene fugas tan severas que incluso el optimista es negativo, "
                          "mostrar como 'Equilibrio/sin pérdida neta' o excluir de vista Gerencia. "
                          "Alternativa: presentar solo el rango de fuga (conservador a realista) "
                          "sin etiquetar como 'recuperación'.",
            )

        return CommercialGateResult(
            gate_id="CG-SCENARIO-NEGATIVE",
            name="Escenario negativo como recuperación",
            passed=True,
            severity="BLOCKING",
            message="Escenario optimista no es negativo.",
            suggestion="",
        )

    def _check_ia_blocked_claim(
        self,
        diagnostic_text: str,
        ai_crawlers_data: Optional[Dict[str, Any]],
    ) -> CommercialGateResult:
        """CG-IA-BLOCKED-CLAIM: 'IA Bloqueada' sin evidencia de blocked_crawlers."""
        # Check if text contains "bloqueada" in IA context
        has_blocked_claim = bool(re.search(
            r'IA\s+[Bb]loqueada|bloqueada.*[Ii][Aa]|[Ii]nvisible\s+para\s+ChatGPT',
            diagnostic_text,
        ))

        if not has_blocked_claim:
            return CommercialGateResult(
                gate_id="CG-IA-BLOCKED-CLAIM",
                name='"IA Bloqueada" sin evidencia',
                passed=True,
                severity="BLOCKING",
                message="No se encontró claim de 'IA Bloqueada' en el texto.",
                suggestion="",
            )

        # Verify blocked_crawlers is non-empty
        blocked = []
        if ai_crawlers_data:
            if isinstance(ai_crawlers_data, dict):
                blocked = ai_crawlers_data.get("blocked_crawlers", [])
            else:
                blocked = getattr(ai_crawlers_data, "blocked_crawlers", []) or []

        if not blocked:
            return CommercialGateResult(
                gate_id="CG-IA-BLOCKED-CLAIM",
                name='"IA Bloqueada" sin evidencia',
                passed=False,
                severity="BLOCKING",
                message='El documento dice "IA Bloqueada" pero blocked_crawlers está vacío. '
                        'El hotel NO tiene crawlers bloqueados.',
                suggestion='Cambiar a "IA sin guía (Sin mapa para asistentes de IA)" '
                          'o "Sin robots.txt/llms.txt para orientar rastreadores de IA". '
                          'Solo usar "bloqueada" si blocked_crawlers > 0.',
            )

        return CommercialGateResult(
            gate_id="CG-IA-BLOCKED-CLAIM",
            name='"IA Bloqueada" sin evidencia',
            passed=True,
            severity="BLOCKING",
            message=f"Claim de IA Bloqueada soportado: {len(blocked)} crawler(s) bloqueado(s).",
            suggestion="",
        )

    def _check_roi_negative(
        self,
        net_benefit_6m: float,
        roi: float,
        has_onboarding_plan: bool,
    ) -> CommercialGateResult:
        """CG-ROI-NEGATIVE: net_benefit_6m < 0 y no hay plan de onboarding alternativo."""
        if net_benefit_6m >= 0:
            return CommercialGateResult(
                gate_id="CG-ROI-NEGATIVE",
                name="ROI negativo como argumento de cierre",
                passed=True,
                severity="BLOCKING",
                message=f"Beneficio neto 6m positivo: ${net_benefit_6m:,.0f} COP.",
                suggestion="",
            )

        if has_onboarding_plan:
            return CommercialGateResult(
                gate_id="CG-ROI-NEGATIVE",
                name="ROI negativo como argumento de cierre",
                passed=True,
                severity="BLOCKING",
                message=f"Beneficio neto 6m negativo (${net_benefit_6m:,.0f}) "
                        f"pero hay plan de onboarding alternativo.",
                suggestion="",
            )

        return CommercialGateResult(
            gate_id="CG-ROI-NEGATIVE",
            name="ROI negativo como argumento de cierre",
            passed=False,
            severity="BLOCKING",
            message=f"Beneficio neto 6m negativo (${net_benefit_6m:,.0f} COP) "
                    f"y ROI {roi:.2f}X sin plan de onboarding alternativo. "
                    f"Una propuesta que dice 'págueme para perder dinero' no cierra.",
            suggestion="Reestructurar oferta: (1) vender quick wins de alto dolor primero, "
                      "(2) separar plan diagnóstico/onboarding de plan mensual, "
                      "(3) recalcular recuperación con evidencia real antes de mostrar ROI, "
                      "o (4) proponer una fase inicial de bajo riesgo (onboarding/activación).",
        )

    def _check_claim_vs_evidence(
        self,
        diagnostic_text: str,
        place_found: bool,
        gbp_rating: float,
    ) -> CommercialGateResult:
        """CG-CLAIM-VS-EVIDENCE: 'No aparece' cuando place_found=True o rating > 4.0."""
        no_aparece_pattern = re.search(
            r'[Nn]o\s+aparece|[Nn]o\s+figura|no\s+est[aá]\s+en\s+Google|invisible\s+en\s+b[uú]squedas',
            diagnostic_text,
        )

        if not no_aparece_pattern:
            return CommercialGateResult(
                gate_id="CG-CLAIM-VS-EVIDENCE",
                name="Claims no soportados por datos",
                passed=True,
                severity="BLOCKING",
                message="No se encontraron claims absolutos de invisibilidad.",
                suggestion="",
            )

        if place_found and gbp_rating >= 4.0:
            # The business IS found and rated well — "no aparece" claim contradicts data
            return CommercialGateResult(
                gate_id="CG-CLAIM-VS-EVIDENCE",
                name="Claims no soportados por datos",
                passed=False,
                severity="BLOCKING",
                message=f'El documento dice "{no_aparece_pattern.group(0)}" pero '
                        f'place_found=True y rating={gbp_rating}/5.0. '
                        f'El hotel SÍ aparece en Google.',
                suggestion='Cambiar absolutos por claims trazables: '
                          '"Google sí lo encuentra, pero su ficha/web tienen fricciones '
                          'que desvían reservas directas: WhatsApp inconsistente, sin Schema, '
                          'sin FAQ, sin OG, sin medición".',
            )

        return CommercialGateResult(
            gate_id="CG-CLAIM-VS-EVIDENCE",
            name="Claims no soportados por datos",
            passed=True,
            severity="BLOCKING",
            message="Claims de visibilidad son consistentes con los datos.",
            suggestion="",
        )

    def _check_whatsapp_lead(self, diagnostic_text: str) -> CommercialGateResult:
        """CG-WHATSAPP-LEAD: WhatsApp no es primera brecha/sección en diagnóstico."""
        # Check if WhatsApp appears in first ~500 chars (the lead section)
        first_chunk = diagnostic_text[:800] if len(diagnostic_text) > 800 else diagnostic_text
        has_whatsapp_early = bool(re.search(
            r'WhatsApp|whatsapp',
            first_chunk,
        ))

        if has_whatsapp_early:
            return CommercialGateResult(
                gate_id="CG-WHATSAPP-LEAD",
                name="WhatsApp no lidera narrativa",
                passed=True,
                severity="WARNING",
                message="WhatsApp aparece en la sección inicial del diagnóstico.",
                suggestion="",
            )

        return CommercialGateResult(
            gate_id="CG-WHATSAPP-LEAD",
            name="WhatsApp no lidera narrativa",
            passed=False,
            severity="WARNING",
            message="WhatsApp no aparece en la sección inicial del diagnóstico. "
                    "El conflicto de WhatsApp es el gancho emocional más fuerte para el dueño.",
            suggestion="Abrir diagnóstico con 'cliente escribiendo al número equivocado' "
                      "o el conflicto WhatsApp web vs GBP como quick win #1.",
        )

    def _check_ota_narrative(self, text: str) -> CommercialGateResult:
        """CG-OTA-NARRATIVE: 0 menciones de Booking/Expedia/comisiones."""
        ota_terms = ["Booking", "Expedia", "comisión", "comisiones", "OTA"]
        found = [t for t in ota_terms if t.lower() in text.lower()]

        if found:
            return CommercialGateResult(
                gate_id="CG-OTA-NARRATIVE",
                name="Sin narrativa OTA",
                passed=True,
                severity="WARNING",
                message=f"Términos OTA encontrados: {', '.join(found)}.",
                suggestion="",
            )

        return CommercialGateResult(
            gate_id="CG-OTA-NARRATIVE",
            name="Sin narrativa OTA",
            passed=False,
            severity="WARNING",
            message="0 menciones de Booking, Expedia, comisiones u OTAs. "
                    "El hotelero siente más fuerte el 'impuesto OTA' que 'Schema'.",
            suggestion="Insertar narrativa central: 'menos dependencia de Booking/Expedia, "
                      "más reserva directa por WhatsApp/Google/IA', usando la comisión OTA "
                      "como base de dolor.",
        )

    def _check_tier_consistency(
        self,
        frontmatter_tier: Optional[str],
        text_tier: Optional[str],
    ) -> CommercialGateResult:
        """CG-TIER-CONSISTENCY: Frontmatter tier ≠ texto tier."""
        if frontmatter_tier is None or text_tier is None:
            # Can't check — skip gracefully
            return CommercialGateResult(
                gate_id="CG-TIER-CONSISTENCY",
                name="Tier inconsistente",
                passed=True,
                severity="WARNING",
                message="Sin datos de tier para comparar (frontmatter o texto no disponibles).",
                suggestion="",
            )

        ft = frontmatter_tier.strip().upper()
        tt = text_tier.strip().upper()

        if ft != tt:
            return CommercialGateResult(
                gate_id="CG-TIER-CONSISTENCY",
                name="Tier inconsistente",
                passed=False,
                severity="WARNING",
                message=f"Frontmatter dice tier '{ft}' pero el texto dice tier '{tt}'.",
                suggestion="Unificar tier en todas las secciones del documento. "
                          "Usar la fuente de verdad del financial_json.",
            )

        return CommercialGateResult(
            gate_id="CG-TIER-CONSISTENCY",
            name="Tier inconsistente",
            passed=True,
            severity="WARNING",
            message=f"Tier consistente: '{ft}' en frontmatter y texto.",
            suggestion="",
        )

    def _check_tech_jargon(self, text: str) -> CommercialGateResult:
        """CG-TECH-JARGON: Jerga técnica en vista gerencia (primeras 6 secciones).

        Busca términos técnicos en las primeras líneas del documento.
        La vista gerencia debe evitar: Schema, AEO, IAO, Open Graph, NAP, Rich Snippets.
        """
        # Tomar solo las primeras ~150 líneas (~6 secciones típicas)
        lines = text.split("\n")[:150]
        early_text = "\n".join(lines)

        found_terms = []
        for term in TECH_JARGON_TERMS:
            # Match as whole word/term, case-insensitive
            if re.search(r'\b' + re.escape(term) + r'\b', early_text, re.IGNORECASE):
                found_terms.append(term)

        if not found_terms:
            return CommercialGateResult(
                gate_id="CG-TECH-JARGON",
                name="Jerga técnica en vista gerencia",
                passed=True,
                severity="WARNING",
                message="No se encontró jerga técnica en las primeras secciones.",
                suggestion="",
            )

        return CommercialGateResult(
            gate_id="CG-TECH-JARGON",
            name="Jerga técnica en vista gerencia",
            passed=False,
            severity="WARNING",
            message=f"Jerga técnica encontrada en vista gerencia: {', '.join(found_terms)}. "
                    f"El decisor entiende ocupación, reservas directas, comisiones, WhatsApp, "
                    f"reseñas y caja; no compra por leer pesos internos de scoring.",
            suggestion="Mover {0} al Anexo Técnico (sección 7+). "
                      "Vista Gerencia (secciones 1-6): lenguaje de negocio.".format(
                          ', '.join(found_terms)
                      ),
        )
