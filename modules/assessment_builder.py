"""
modules/assessment_builder.py
NUEVO-8-ASSESSMENT-BUILDER — AssessmentPayload dataclass

Fase: N8-A
Verificado contra: main.py L2663-2754, modules/quality_gates/publication_gates.py

T1 VERIFICATION TABLE (claims vs live code):
==============================================
| Claim                                          | Status  | Evidence                            |
|------------------------------------------------|---------|-------------------------------------|
| coherence_report consumido (_extract_cs)        | ❌ FALSE| L1236-1238 checks existence but     |
|                                                |         | extracts from coherence_score first; |
|                                                |         | coherence_report never used in cur-  |
|                                                |         | rent main.py assessment dict        |
| SitePresenceChecker ejecuta 2x                  | ✅ TRUE | main.py L2607 + publication_gates   |
|                                                |         | L840 (2 calls when hotel_url set)   |
| proposal_services fallback a ALL_PROMISED_     | ✅ TRUE | publication_gates.py L832:           |
| SERVICES                                               |         | .get("proposal_services",           |
|                                                |         | ALL_PROMISED_SERVICES)              |
| critical_issues == critical_issues_detected     | ✅ TRUE | main.py L2687-2688 ambos ссылаются  |
|                                                |         | на audit_result.critical_issues      |
| audit_schema consumido (_proposal_asset_)      | ✅ TRUE| L868: audit_schema=assessment.get()  |
| coherence_score consumido (_extract_cs)         | ✅ TRUE| L1227-1228: extraction priority #1  |
| site_presence_report consumido                 | ✅ TRUE| publication_gates.py L835, L839     |
| pain_ledger consumido                           | ✅ TRUE| pain_ledger_gate L868+              |
| diagnostic_pain_ids, proposal_pain_ids          | ✅ TRUE| referenced in gates                  |
| generated_assets consumido                      | ✅ TRUE| asset_confidence_gate, alignment_gate|
| financial_data, financial_sources               | ✅ TRUE| gates consumen dicts directamente  |
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class AssessmentPayload:
    """Contrato tipado entre main.py y publication_gates.

    Todos los campos que los 11 gates consumen, verificados contra código vivo (N8-A).
    Campos eliminados (0 consumidores): quality_gate_issues, quality_gate_blockers,
    quality_gate_warnings, coherence_checks, coherence_errors, coherence_warnings,
    critical_issues_detected, metrics, coherence_report.
    """
    # Core — REQUIRED (sin default)
    url: str
    hotel_name: str
    hotel_url: str = ""  # alias de url, builder lo setea a url

    # Validation
    validation_summary: Dict[str, Any] = field(default_factory=dict)

    # Financial
    financial_data: Dict[str, Any] = field(default_factory=dict)
    financial_sources: Dict[str, Any] = field(default_factory=dict)
    financial_evidence_tier: str = "C"

    # Coherence
    coherence_score: float = 0.0
    # FASE-F (N11/P9): veredicto binario del CoherenceValidator. None =
    # campo ausente (assessments legacy sin reporte) — vacío ≠ ausente.
    is_coherent: Optional[bool] = None

    # Pain Ledger / FASE-0
    pain_ledger: List[Dict] = field(default_factory=list)
    pain_ledger_resolved: Optional[List[Dict]] = None  # DT4-R1: post-reconciler ledger
    diagnostic_pain_ids: List[str] = field(default_factory=list)
    proposal_pain_ids: List[str] = field(default_factory=list)

    # Audit
    audit_schema: Dict[str, Any] = field(default_factory=dict)
    critical_issues: List[str] = field(default_factory=list)
    # FASE-G (G1): audit_data crudo para doc_audit_consistency — antes el
    # payload no lo traía y el gate caía en "No audit data available" PASSED.
    audit_data: Dict[str, Any] = field(default_factory=dict)

    # Proposal
    proposal_services: List[str] = field(default_factory=list)

    # Documents
    diagnostico_text: str = ""
    propuesta_text: str = ""

    # Assets
    generated_assets: List[Dict] = field(default_factory=list)
    skipped_assets: List[Dict] = field(default_factory=list)  # FASE-1B: skipped por SitePresenceChecker
    evidence_coverage: float = 0.95  # TODO: calcular en vez de hardcodear

    # Site presence (evita duplicación SitePresenceChecker)
    site_presence_report: Optional[Dict[str, Any]] = None

    # Hotel data
    hotel_data: Dict[str, str] = field(default_factory=dict)

    # FASE-P0-B: Pricing data for pricing_compliance gate
    pricing_data: Optional[Dict[str, Any]] = None


class AssessmentBuilder:
    """API fluida para construir AssessmentPayload y convertirlo a dict.

    Refactor del bloque L2663-2754 de main.py — ahora tipado y testeable.
    """

    def __init__(self):
        self._payload = AssessmentPayload(url="", hotel_name="")

    # ─── Métodos fluid ──────────────────────────────────────────────────────

    def with_core(self, url: str, hotel_name: str) -> "AssessmentBuilder":
        self._payload.url = url
        self._payload.hotel_name = hotel_name
        self._payload.hotel_url = url
        return self

    def with_validation(
        self,
        validation_summary: Dict[str, Any],
        whatsapp_validation: Any,
    ) -> "AssessmentBuilder":
        self._payload.validation_summary = validation_summary
        return self

    def with_financial(
        self,
        rooms: int,
        adr_cop: float,
        occupancy_rate: float,
        direct_channel_pct: float,
        financial_sources: Dict[str, Any],
        financial_breakdown: Any,
    ) -> "AssessmentBuilder":
        self._payload.financial_data = {
            "rooms": rooms,
            "adr_cop": adr_cop,
            "occupancy_rate": occupancy_rate,
            "direct_channel_percentage": direct_channel_pct,
        }
        self._payload.financial_sources = financial_sources
        self._payload.financial_evidence_tier = (
            getattr(financial_breakdown, "evidence_tier", "C")
            if financial_breakdown
            else "C"
        )
        return self

    def with_coherence(
        self, pre_coherence_report: Any, asset_result: Any
    ) -> "AssessmentBuilder":
        # FASE-F (N11/P9): extraer score Y veredicto de la MISMA fuente
        # canónica (final_coherence_report preferred, DT4-N4). El veredicto
        # binario viaja al assessment para que _coherence_gate lo respete.
        source = None
        if asset_result:
            if (
                hasattr(asset_result, "final_coherence_report")
                and asset_result.final_coherence_report
            ):
                source = asset_result.final_coherence_report
                self._payload.coherence_score = source.overall_score
            elif (
                hasattr(asset_result, "coherence_report")
                and asset_result.coherence_report
            ):
                source = asset_result.coherence_report
                self._payload.coherence_score = source.overall_score
            else:
                self._payload.coherence_score = 0.0
        else:
            self._payload.coherence_score = 0.0
        verdict = getattr(source, "is_coherent", None) if source is not None else None
        self._payload.is_coherent = None if verdict is None else bool(verdict)
        # NO setear coherence_report en el payload (0 consumidores post-simplificación)
        return self

    def with_pain_ledger(
        self,
        entries: List[Any],
        diagnostic_summary: Any,
        asset_plan: Any,
    ) -> "AssessmentBuilder":
        self._payload.pain_ledger = [
            e.to_dict() if hasattr(e, "to_dict") else e for e in entries
        ]
        self._payload.diagnostic_pain_ids = list(
            getattr(diagnostic_summary, "pain_ids", []) or []
        ) if diagnostic_summary else []
        self._payload.proposal_pain_ids = list(
            set(
                pid
                for asset in (asset_plan or [])
                for pid in (getattr(asset, "pain_ids", None) or [])
            )
        )
        return self

    def with_resolved_pain_ledger(
        self, entries: List[Dict]
    ) -> "AssessmentBuilder":
        """DT4-R1: Inject reconciled pain_ledger into assessment.

        Called after with_pain_ledger() when post-orchestrator reconciliation
        produced a pain_ledger_resolved.json.
        """
        self._payload.pain_ledger_resolved = entries
        return self

    def with_audit(self, audit_result: Any) -> "AssessmentBuilder":
        if audit_result is None:
            self._payload.audit_schema = {}
            self._payload.critical_issues = []
            return self
        self._payload.critical_issues = audit_result.critical_issues or []
        self._payload.audit_schema = {
            "hotel_schema_detected": audit_result.schema.hotel_schema_detected,
            "hotel_schema_valid": audit_result.schema.hotel_schema_valid,
            "hotel_confidence": audit_result.schema.hotel_confidence,
            "faq_schema_detected": audit_result.schema.faq_schema_detected,
            "faq_schema_valid": audit_result.schema.faq_schema_valid,
            "faq_confidence": audit_result.schema.faq_confidence,
        }
        return self

    def with_audit_data(self, audit_data: Dict[str, Any]) -> "AssessmentBuilder":
        """FASE-G (G1): audit_data crudo (to_dict del auditor) para el gate
        doc_audit_consistency — es la única fuente de gbp.reviews int y
        performance.status que el gate puede contrastar contra el doc."""
        self._payload.audit_data = audit_data or {}
        return self

    def with_geo_flow(self, geo_flow_result: Any) -> "AssessmentBuilder":
        """FASE-G (G2): banda GEO critical califica como critical_issue.

        El geo flow corre en FASE 4 (después del audit de FASE 2), así que
        _identify_critical_issues no pudo verlo en audit-time; se anexa al
        critical_issues del assessment antes de correr los gates.
        """
        if not geo_flow_result:
            return self
        from modules.auditors.v4_comprehensive import geo_band_critical_issue

        issue = geo_band_critical_issue(geo_flow_result)
        if issue and issue not in self._payload.critical_issues:
            self._payload.critical_issues.append(issue)
        return self

    def with_documents(
        self, diagnostic_path: str, proposal_path: str
    ) -> "AssessmentBuilder":
        self._payload.diagnostico_text = ""
        self._payload.propuesta_text = ""
        if diagnostic_path:
            try:
                from pathlib import Path

                if Path(diagnostic_path).exists():
                    with open(
                        diagnostic_path, "r", encoding="utf-8"
                    ) as f:
                        self._payload.diagnostico_text = f.read()
            except Exception:
                pass
        if proposal_path:
            try:
                from pathlib import Path

                if Path(proposal_path).exists():
                    with open(
                        proposal_path, "r", encoding="utf-8"
                    ) as f:
                        self._payload.propuesta_text = f.read()
            except Exception:
                pass
        return self

    def with_assets(self, asset_result: Any) -> "AssessmentBuilder":
        if asset_result and asset_result.generated_assets:
            self._payload.generated_assets = [
                {
                    "asset_type": a.asset_type,
                    "filename": a.filename,
                    "confidence_score": a.confidence_score,
                    "preflight_status": a.preflight_status,
                    "path": a.path,
                }
                for a in asset_result.generated_assets
            ]
        # FASE-1B: Propagar skipped_assets al assessment para que publication_gate los consuma
        if asset_result and hasattr(asset_result, 'skipped_assets') and asset_result.skipped_assets:
            self._payload.skipped_assets = [
                {
                    "asset_type": a.asset_type,
                    "presence_status": a.presence_status,
                    "reason": a.reason,
                    "site_verified": a.site_verified,
                    "pain_ids_affected": getattr(a, 'pain_ids_affected', []),
                }
                for a in asset_result.skipped_assets
            ]
        # NO setear metrics (0 consumidores — dict con campos que nunca existieron)
        return self

    def with_site_presence(
        self, site_presence_report: Dict[str, Any]
    ) -> "AssessmentBuilder":
        self._payload.site_presence_report = site_presence_report
        return self

    def with_hotel_data(self, region: str) -> "AssessmentBuilder":
        self._payload.hotel_data = (
            {"region": region.replace("_", " ").title()} if region else {}
        )
        return self

    def with_pricing(self, pricing_result: Any) -> "AssessmentBuilder":
        """FASE-P0-B: Inject pricing data for pricing_compliance gate.

        Extracts pain_ratio, tier, monthly_price_cop, expected_loss_cop
        from PricingResult / PricingResolutionResult (both have these fields).
        """
        if pricing_result is None:
            return self
        self._payload.pricing_data = {
            "pain_ratio": getattr(pricing_result, "pain_ratio", None),
            "tier": getattr(pricing_result, "tier", "boutique"),
            "monthly_price_cop": getattr(pricing_result, "monthly_price_cop", 0),
            "expected_loss_cop": getattr(pricing_result, "expected_loss_cop", 0),
            "is_compliant": getattr(pricing_result, "is_compliant", None),
        }
        return self

    # ─── Build ──────────────────────────────────────────────────────────────

    def _validate(self) -> None:
        if not self._payload.url:
            raise ValueError("url es requerido para build()")
        if not self._payload.hotel_name:
            raise ValueError("hotel_name es requerido para build()")

    def _to_dict(self) -> Dict[str, Any]:
        from dataclasses import asdict

        return asdict(self._payload)

    def build(self) -> Dict[str, Any]:
        self._validate()
        return self._to_dict()