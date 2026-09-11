"""HonestyReviewer — Bot 4 del tribunal de certificación.

Revisor híbrido que detecta sobre-presentación de datos ESTIMATED como verificados,
verifica que los 3 escenarios (70/20/10) están presentes, y lee los 12 CG-* repartidos
en DOS archivos comerciales (canónico + diagnóstico).

Flujo:
1. LLM extrae claims de sobre-presentación de la propuesta
2. Capa determinista verifica cada claim contra: tier labels, escenarios, CG-*
3. Clasifica: OVER_PRESENTATION / TIER_MISMATCH / CG_WARNING_UNDISCLOSED / MISSING_SCENARIO
4. Produce revision_honestidad.json

CRÍTICO: El reporte comercial está PARTIDO en dos archivos. Leer solo el canónico
produce falso "todo pasó". El único gate que falló en la corrida real (CG-WHATSAPP-LEAD)
está en el archivo de diagnóstico.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

from modules.quality_gates.tribunal.llm_extractor import (
    LLMPromiseExtractor,
    PromiseExtractor,
    VerbalPromise,
)


FINDING_OVER_PRESENTATION = "OVER_PRESENTATION"
FINDING_TIER_MISMATCH = "TIER_MISMATCH"
FINDING_CG_WARNING_UNDISCLOSED = "CG_WARNING_UNDISCLOSED"
FINDING_MISSING_SCENARIO = "MISSING_SCENARIO"

VERDICT_APROBADO = "APROBADO"
VERDICT_DEVOLVER = "DEVOLVER-PRUEBAS"
VERDICT_BLOQUEAR = "BLOQUEAR"

SCENARIO_KEYS = ["conservative", "realistic", "optimistic"]
SCENARIO_LABELS = {
    "conservative": "conservador (70%)",
    "realistic": "realista (20%)",
    "optimistic": "optimista (10%)",
}


class HonestyReviewer:
    """Revisor híbrido de honestidad comercial (Bot 4).

    Constructor: ``HonestyReviewer(v4_audit_dir, deliveries_dir=None)``.
    Lee propuesta + escenarios + CG-* (AMBOS archivos) + MANIFEST, extrae claims
    de sobre-presentación (LLM), verifica contra tier labels y CG-*.
    """

    def __init__(self, v4_audit_dir: str | Path, deliveries_dir: Optional[str | Path] = None):
        """Inicializa el revisor.

        Args:
            v4_audit_dir: Directorio v4_audit con artefactos del pipeline.
            deliveries_dir: Directorio deliveries con MANIFEST.json (si es None,
                           busca en v4_audit_dir/../deliveries).
        """
        self.v4_audit_dir = Path(v4_audit_dir)
        self.deliveries_dir = Path(deliveries_dir) if deliveries_dir else self._resolve_deliveries_dir()

    def _resolve_deliveries_dir(self) -> Path:
        """Resuelve deliveries_dir como v4_audit_dir/../deliveries."""
        return self.v4_audit_dir.parent.parent / "deliveries"

    def review(self, extractor: Optional[PromiseExtractor] = None) -> dict:
        """Retorna revision_honestidad.json con findings y commercial_gates_read.

        Args:
            extractor: Extractor de claims (si es None, usa LLMPromiseExtractor).
        """
        proposal_text = self._load_proposal()
        financial_scenarios = self._load_financial_scenarios()
        manifest = self._load_manifest()
        cg_canonical = self._load_commercial_gates_canonical()
        cg_diagnostic = self._load_commercial_gates_diagnostic()

        if proposal_text is None:
            return self._error_report("No se encontró 02_PROPUESTA_COMERCIAL*.md")
        if financial_scenarios is None:
            return self._error_report("No se encontró financial_scenarios_*.json")

        if extractor is None:
            extractor = LLMPromiseExtractor()

        findings = []
        commercial_gates_read = self._merge_commercial_gates(cg_canonical, cg_diagnostic)

        evidence_tier = self._extract_evidence_tier(manifest, financial_scenarios)
        precision_tier = self._extract_precision_tier(manifest, financial_scenarios)

        claims = extractor.extract_verbal_promises(proposal_text)
        for claim in claims:
            over_presentation = self._check_over_presentation(claim, evidence_tier, proposal_text)
            if over_presentation:
                findings.append(over_presentation)

            tier_mismatch = self._check_tier_mismatch(claim, evidence_tier, precision_tier)
            if tier_mismatch:
                findings.append(tier_mismatch)

        missing_scenario = self._check_missing_scenarios(financial_scenarios)
        if missing_scenario:
            findings.extend(missing_scenario)

        cg_warnings = self._extract_cg_warnings(commercial_gates_read)
        for warning in cg_warnings:
            undisclosed = self._check_cg_warning_undisclosed(warning, proposal_text)
            if undisclosed:
                findings.append(undisclosed)

        summary = self._compute_summary(findings)
        verdict = self._compute_verdict(findings)

        return {
            "reviewer": "honesty_reviewer",
            "clause": "P6.5",
            "findings": findings,
            "commercial_gates_read": commercial_gates_read,
            "summary": summary,
            "verdict_recommendation": verdict,
            "timestamp": datetime.now().isoformat(),
            "artifacts_read": self._list_artifacts_read(),
        }

    def write_report(self, extractor: Optional[PromiseExtractor] = None, output_path: Optional[Path] = None) -> Path:
        """Escribe revision_honestidad.json y retorna la ruta."""
        report = self.review(extractor)
        if output_path is None:
            output_path = self.v4_audit_dir / "revision_honestidad.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        return output_path

    def _load_proposal(self) -> Optional[str]:
        """Carga 02_PROPUESTA_COMERCIAL*.md (más reciente)."""
        pattern = "02_PROPUESTA_COMERCIAL*.md"
        matches = sorted(
            self.v4_audit_dir.glob(pattern),
            key=lambda p: p.stat().st_mtime if p.exists() else 0,
            reverse=True,
        )
        if not matches:
            matches = sorted(
                self.v4_audit_dir.parent.glob(pattern),
                key=lambda p: p.stat().st_mtime if p.exists() else 0,
                reverse=True,
            )
        if not matches:
            return None
        try:
            with open(matches[0], "r", encoding="utf-8") as f:
                return f.read()
        except OSError:
            return None

    def _load_financial_scenarios(self) -> Optional[dict]:
        """Carga financial_scenarios_*.json (más reciente)."""
        pattern = "financial_scenarios_*.json"
        matches = sorted(
            self.v4_audit_dir.glob(pattern),
            key=lambda p: p.stat().st_mtime if p.exists() else 0,
            reverse=True,
        )
        if not matches:
            return None
        try:
            with open(matches[0], "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return None

    def _load_manifest(self) -> Optional[dict]:
        """Carga MANIFEST.json desde deliveries_dir (más reciente)."""
        if not self.deliveries_dir.exists():
            return None
        pattern = "*/MANIFEST.json"
        matches = sorted(
            self.deliveries_dir.glob(pattern),
            key=lambda p: p.stat().st_mtime if p.exists() else 0,
            reverse=True,
        )
        if not matches:
            return None
        try:
            with open(matches[0], "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return None

    def _load_commercial_gates_canonical(self) -> Optional[dict]:
        """Carga commercial_gates_report.json (archivo canónico con 3 gates)."""
        path = self.v4_audit_dir / "commercial_gates_report.json"
        if not path.exists():
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return None

    def _load_commercial_gates_diagnostic(self) -> Optional[dict]:
        """Carga commercial_gates_report_diagnostic_*.json (9 gates adicionales)."""
        pattern = "commercial_gates_report_diagnostic_*.json"
        matches = sorted(
            self.v4_audit_dir.glob(pattern),
            key=lambda p: p.stat().st_mtime if p.exists() else 0,
            reverse=True,
        )
        if not matches:
            return None
        try:
            with open(matches[0], "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return None

    def _merge_commercial_gates(self, canonical: Optional[dict], diagnostic: Optional[dict]) -> dict:
        """Une los CG-* de AMBOS archivos y reporta metadata de lectura.

        CRÍTICO: Leer solo el canónico produce falso "todo pasó". El único gate
        que falló en la corrida real (CG-WHATSAPP-LEAD) está en el diagnóstico.
        """
        all_gates = []
        warnings_found = []
        canonical_file = None
        diagnostic_file = None

        if canonical:
            canonical_file = "commercial_gates_report.json"
            for gate in canonical.get("results", []):
                all_gates.append(gate)
                if gate.get("severity") == "WARNING" and not gate.get("passed", True):
                    warnings_found.append(gate.get("gate_id"))

        if diagnostic:
            pattern = "commercial_gates_report_diagnostic_*.json"
            matches = list(self.v4_audit_dir.glob(pattern))
            if matches:
                diagnostic_file = matches[0].name
            for gate in diagnostic.get("results", []):
                all_gates.append(gate)
                if gate.get("severity") == "WARNING" and not gate.get("passed", True):
                    warnings_found.append(gate.get("gate_id"))

        return {
            "canonical_file": canonical_file,
            "diagnostic_file": diagnostic_file,
            "total_cg_count": len(all_gates),
            "warnings_found": warnings_found,
            "all_gates": all_gates,
        }

    def _extract_evidence_tier(self, manifest: Optional[dict], financial_scenarios: Optional[dict]) -> str:
        """Extrae evidence_tier del MANIFEST o financial_scenarios."""
        if manifest and "quality_metadata" in manifest:
            tier = manifest["quality_metadata"].get("evidence_tier")
            if tier:
                return tier
        if financial_scenarios and "breakdown" in financial_scenarios:
            tier = financial_scenarios["breakdown"].get("evidence_tier")
            if tier:
                return tier
        return "UNKNOWN"

    def _extract_precision_tier(self, manifest: Optional[dict], financial_scenarios: Optional[dict]) -> str:
        """Extrae precision_tier del MANIFEST o financial_scenarios."""
        if manifest and "quality_metadata" in manifest:
            tier = manifest["quality_metadata"].get("precision_tier")
            if tier:
                return tier
        if financial_scenarios:
            tier = financial_scenarios.get("precision_tier")
            if tier:
                return tier
        return "UNKNOWN"

    def _check_over_presentation(self, claim: VerbalPromise, evidence_tier: str, proposal_text: str) -> Optional[dict]:
        """Detecta OVER_PRESENTATION: ESTIMATED presentado como verificado.

        Si evidence_tier es B o C (no A), y el claim usa lenguaje de verificación
        ("verificado", "confirmado", "dato real"), es sobre-presentación.
        """
        if evidence_tier in ["A", "UNKNOWN"]:
            return None

        verification_patterns = [
            r"\b(verificad[oa]s?|confirmad[oa]s?|dato real|cifra exacta|validad[oa]s?)\b",
            r"\b(100%|total|absoluto|definitivo)\b",
        ]

        claim_text = claim.text.lower()
        for pattern in verification_patterns:
            if re.search(pattern, claim_text, re.IGNORECASE):
                return {
                    "severity": "CRITICAL",
                    "type": FINDING_OVER_PRESENTATION,
                    "claim_text": claim.text,
                    "evidence_tier_declared": evidence_tier,
                    "cg_reference": None,
                    "description": f"Claim con lenguaje de verificación pero evidence_tier={evidence_tier} (no A)",
                }

        return None

    def _check_tier_mismatch(self, claim: VerbalPromise, evidence_tier: str, precision_tier: str) -> Optional[dict]:
        """Detecta TIER_MISMATCH: claim con tier declarado ≠ tier real.

        Si el claim menciona un tier específico (ej: "tier A") pero el tier real
        es B o C, es un mismatch.
        """
        claim_text = claim.text.lower()

        tier_mentions = {
            "tier a": "A",
            "evidence a": "A",
            "tier b": "B",
            "evidence b": "B",
            "tier c": "C",
            "evidence c": "C",
        }

        for mention, mentioned_tier in tier_mentions.items():
            if mention in claim_text and mentioned_tier != evidence_tier:
                return {
                    "severity": "WARNING",
                    "type": FINDING_TIER_MISMATCH,
                    "claim_text": claim.text,
                    "evidence_tier_declared": evidence_tier,
                    "cg_reference": None,
                    "description": f"Claim menciona tier {mentioned_tier} pero evidence_tier real es {evidence_tier}",
                }

        return None

    def _check_missing_scenarios(self, financial_scenarios: dict) -> list[dict]:
        """Detecta MISSING_SCENARIO: falta alguno de los 3 escenarios (70/20/10)."""
        findings = []
        scenarios = financial_scenarios.get("scenarios", {})

        for key in SCENARIO_KEYS:
            if key not in scenarios or scenarios[key] is None:
                findings.append({
                    "severity": "CRITICAL",
                    "type": FINDING_MISSING_SCENARIO,
                    "claim_text": None,
                    "evidence_tier_declared": self._extract_evidence_tier(None, financial_scenarios),
                    "cg_reference": None,
                    "description": f"Falta escenario {SCENARIO_LABELS.get(key, key)}",
                })

        return findings

    def _extract_cg_warnings(self, commercial_gates_read: dict) -> list[dict]:
        """Extrae CG-* WARNING que no pasaron de all_gates."""
        warnings = []
        for gate in commercial_gates_read.get("all_gates", []):
            if gate.get("severity") == "WARNING" and not gate.get("passed", True):
                warnings.append({
                    "gate_id": gate.get("gate_id"),
                    "name": gate.get("name"),
                    "message": gate.get("message"),
                    "suggestion": gate.get("suggestion"),
                })
        return warnings

    def _check_cg_warning_undisclosed(self, warning: dict, proposal_text: str) -> Optional[dict]:
        """Detecta CG_WARNING_UNDISCLOSED: WARNING no divulgado en la propuesta.

        Si la propuesta no menciona el problema que el WARNING detectó, es un
        warning no divulgado.
        """
        gate_id = warning.get("gate_id", "")
        message = warning.get("message", "").lower()

        keywords_by_gate = {
            "CG-WHATSAPP-LEAD": ["whatsapp", "número", "mensaje"],
            "CG-OTA-NARRATIVE": ["ota", "booking", "expedia", "comisión"],
            "CG-TECH-JARGON": ["jerga", "técnico", "api", "backend"],
            "CG-TIER-CONSISTENCY": ["tier", "evidencia"],
        }

        keywords = keywords_by_gate.get(gate_id, [])
        proposal_lower = proposal_text.lower()

        mentioned = any(kw in proposal_lower for kw in keywords)
        if not mentioned:
            return {
                "severity": "WARNING",
                "type": FINDING_CG_WARNING_UNDISCLOSED,
                "claim_text": None,
                "evidence_tier_declared": self._extract_evidence_tier(None, None),
                "cg_reference": gate_id,
                "description": f"CG-* WARNING {gate_id} no divulgado en propuesta: {warning.get('message', '')[:100]}",
            }

        return None

    def _compute_summary(self, findings: list) -> dict:
        """Calcula resumen de hallazgos."""
        over_presentations = sum(1 for f in findings if f.get("type") == FINDING_OVER_PRESENTATION)
        tier_mismatches = sum(1 for f in findings if f.get("type") == FINDING_TIER_MISMATCH)
        undisclosed_warnings = sum(1 for f in findings if f.get("type") == FINDING_CG_WARNING_UNDISCLOSED)
        missing_scenarios = sum(1 for f in findings if f.get("type") == FINDING_MISSING_SCENARIO)
        return {
            "over_presentations": over_presentations,
            "tier_mismatches": tier_mismatches,
            "undisclosed_warnings": undisclosed_warnings,
            "missing_scenarios": missing_scenarios,
            "total_findings": len(findings),
        }

    def _compute_verdict(self, findings: list) -> str:
        """Veredicto recomendado: BLOQUEAR por CRITICAL, DEVOLVER-PRUEBAS por
        WARNING sustantivo, APROBADO en otro caso.
        """
        if any(f.get("severity") == "CRITICAL" for f in findings):
            return VERDICT_BLOQUEAR
        if any(f.get("severity") == "WARNING" for f in findings):
            return VERDICT_DEVOLVER
        return VERDICT_APROBADO

    def _error_report(self, message: str) -> dict:
        """Retorna reporte de error cuando faltan artefactos."""
        return {
            "reviewer": "honesty_reviewer",
            "clause": "P6.5",
            "findings": [{
                "severity": "CRITICAL",
                "type": "MISSING_ARTIFACT",
                "claim_text": None,
                "evidence_tier_declared": "UNKNOWN",
                "cg_reference": None,
                "description": message,
            }],
            "commercial_gates_read": {
                "canonical_file": None,
                "diagnostic_file": None,
                "total_cg_count": 0,
                "warnings_found": [],
            },
            "summary": {
                "over_presentations": 0,
                "tier_mismatches": 0,
                "undisclosed_warnings": 0,
                "missing_scenarios": 0,
                "total_findings": 1,
            },
            "verdict_recommendation": VERDICT_BLOQUEAR,
            "timestamp": datetime.now().isoformat(),
            "artifacts_read": self._list_artifacts_read(),
        }

    def _list_artifacts_read(self) -> list:
        """Lista artefactos que este revisor lee."""
        return [
            "02_PROPUESTA_COMERCIAL*.md",
            "financial_scenarios_*.json",
            "commercial_gates_report.json",
            "commercial_gates_report_diagnostic_*.json",
            "MANIFEST.json (deliveries_dir)",
        ]
