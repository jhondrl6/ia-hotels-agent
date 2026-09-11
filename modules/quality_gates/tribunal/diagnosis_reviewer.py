"""DiagnosisReviewer — Bot 1 del tribunal de certificación.

Revisor determinista que verifica trazabilidad brecha→pain_id, fuente declarada,
y respeto a is_coherent. Lee artefactos existentes; NUNCA reimplementa gates.

Produce revision_diagnostico.json que alimenta el acta del Juez.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


SEVERITY_CRITICAL = "CRITICAL"
SEVERITY_WARNING = "WARNING"
SEVERITY_INFO = "INFO"

FINDING_UNTRACEABLE_PAIN = "UNTRACEABLE_PAIN"
FINDING_UNDECLARED_SOURCE = "UNDECLARED_SOURCE"
FINDING_VACUOUS_RECALL = "VACUOUS_RECALL"
FINDING_UNSUPPORTED_CLAIM = "UNSUPPORTED_CLAIM"

VERDICT_APROBADO = "APROBADO"
VERDICT_DEVOLVER = "DEVOLVER-PRUEBAS"
VERDICT_BLOQUEAR = "BLOQUEAR"


class DiagnosisReviewer:
    """Revisor determinista del diagnóstico (Bot 1).

    Constructor: ``DiagnosisReviewer(v4_audit_dir)``.
    Lee 5 artefactos y produce hallazgos por severidad.
    """

    def __init__(self, v4_audit_dir: str | Path):
        self.v4_audit_dir = Path(v4_audit_dir)

    def review(self) -> dict:
        """Retorna revision_diagnostico.json con hallazgos y veredicto."""
        findings = []

        pain_ledger = self._load_pain_ledger()
        pain_ledger_resolved = self._load_pain_ledger_resolved()
        coherence_validation = self._load_coherence_validation()
        gate_report = self._load_gate_report()
        diagnostic_md = self._load_diagnostic_md()

        findings.extend(self._check_pain_traceability(pain_ledger, diagnostic_md))
        findings.extend(self._check_declared_sources(pain_ledger))
        findings.extend(self._check_vacuous_recall(gate_report))
        findings.extend(self._check_unsupported_claims(
            coherence_validation, gate_report, diagnostic_md
        ))
        findings.extend(self._check_critical_priority(pain_ledger))

        summary = self._compute_summary(findings)
        verdict = self._compute_verdict(findings)

        return {
            "reviewer": "diagnosis_reviewer",
            "clause": "P6.1",
            "findings": findings,
            "summary": summary,
            "verdict_recommendation": verdict,
            "timestamp": datetime.now().isoformat(),
            "artifacts_read": self._list_artifacts_read(),
        }

    def write_report(self, output_path: Optional[Path] = None) -> Path:
        """Escribe revision_diagnostico.json y retorna la ruta."""
        report = self.review()
        if output_path is None:
            output_path = self.v4_audit_dir / "revision_diagnostico.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        return output_path

    def _resolve_artifact(self, pattern: str) -> Optional[Path]:
        """Resuelve artefacto timestamped por glob (más reciente)."""
        matches = sorted(
            self.v4_audit_dir.glob(pattern),
            key=lambda p: p.stat().st_mtime if p.exists() else 0,
            reverse=True,
        )
        return matches[0] if matches else None

    def _load_json(self, path: Optional[Path]) -> Optional[dict]:
        """Carga JSON de forma segura (never-block)."""
        if path is None or not path.exists():
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return None

    def _load_pain_ledger(self) -> Optional[dict]:
        """Carga pain_ledger.json."""
        path = self._resolve_artifact("pain_ledger.json")
        return self._load_json(path)

    def _load_pain_ledger_resolved(self) -> Optional[dict]:
        """Carga pain_ledger_resolved.json."""
        path = self._resolve_artifact("pain_ledger_resolved.json")
        return self._load_json(path)

    def _load_coherence_validation(self) -> Optional[dict]:
        """Carga coherence_validation.json."""
        path = self._resolve_artifact("coherence_validation.json")
        return self._load_json(path)

    def _load_gate_report(self) -> Optional[dict]:
        """Carga gate_report_*.json (resuelve por glob)."""
        path = self._resolve_artifact("gate_report_*.json")
        return self._load_json(path)

    def _load_diagnostic_md(self) -> Optional[str]:
        """Carga 01_DIAGNOSTICO_Y_OPORTUNIDAD_*.md como texto."""
        path = self._resolve_artifact("01_DIAGNOSTICO_Y_OPORTUNIDAD*.md")
        if path is None or not path.exists():
            return None
        try:
            return path.read_text(encoding="utf-8")
        except OSError:
            return None

    def _check_pain_traceability(
        self, pain_ledger: Optional[dict], diagnostic_md: Optional[str]
    ) -> list:
        """Verifica que brechas diagnosticadas tienen pain_id trazable en ledger."""
        findings = []

        if pain_ledger is None or diagnostic_md is None:
            return findings

        ledger_pain_ids = self._extract_pain_ids_from_ledger(pain_ledger)
        diagnostic_pain_ids = self._extract_pain_ids_from_diagnostic(diagnostic_md)

        for pain_id in diagnostic_pain_ids:
            if pain_id not in ledger_pain_ids:
                findings.append(self._make_finding(
                    severity=SEVERITY_WARNING,
                    clause="P6.1",
                    finding_type=FINDING_UNTRACEABLE_PAIN,
                    source_artifact="pain_ledger.json",
                    description=f"Brecha '{pain_id}' mencionada en diagnóstico pero ausente en pain_ledger",
                    pain_id=pain_id,
                ))

        return findings

    def _check_declared_sources(self, pain_ledger: Optional[dict]) -> list:
        """Verifica que cada entrada del ledger tiene fuente declarada."""
        findings = []

        if pain_ledger is None:
            return findings

        entries = pain_ledger.get("entries", [])
        for entry in entries:
            pain_id = entry.get("pain_id", "unknown")
            source_module = entry.get("source_module")
            source_file = entry.get("source_file")

            if not source_module or not source_file:
                findings.append(self._make_finding(
                    severity=SEVERITY_WARNING,
                    clause="P6.1",
                    finding_type=FINDING_UNDECLARED_SOURCE,
                    source_artifact="pain_ledger.json",
                    description=f"pain_id '{pain_id}' sin fuente declarada (source_module/source_file vacíos)",
                    pain_id=pain_id,
                ))

        return findings

    def _check_vacuous_recall(self, gate_report: Optional[dict]) -> list:
        """S-I1: Detecta critical_recall vacuo (details sin critical_issues_count)."""
        findings = []

        if gate_report is None:
            return findings

        recall_gate = self._find_gate(gate_report, "critical_recall")
        if recall_gate is None:
            return findings

        details = recall_gate.get("details", {})
        if not isinstance(details, dict):
            details = {}

        has_critical_count = "critical_issues_count" in details
        recall_value = recall_gate.get("value")

        if recall_value == 1.0 and not has_critical_count:
            findings.append(self._make_finding(
                severity=SEVERITY_CRITICAL,
                clause="P6.1",
                finding_type=FINDING_VACUOUS_RECALL,
                source_artifact="gate_report_*.json",
                description=(
                    "critical_recall=1.0 pero details no declara critical_issues_count. "
                    "Recall vacuo: no hay evidencia de issues críticos evaluados."
                ),
                pain_id="critical_recall",
            ))

        return findings

    def _check_unsupported_claims(
        self,
        coherence_validation: Optional[dict],
        gate_report: Optional[dict],
        diagnostic_md: Optional[str],
    ) -> list:
        """Verifica que el diagnóstico no afirma cosas que gates no pudieron validar."""
        findings = []

        if coherence_validation is None or gate_report is None:
            return findings

        is_coherent = coherence_validation.get("is_coherent", False)
        coherence_gate = self._find_gate(gate_report, "coherence")

        if coherence_gate and not coherence_gate.get("passed", False):
            if is_coherent:
                findings.append(self._make_finding(
                    severity=SEVERITY_WARNING,
                    clause="P6.1",
                    finding_type=FINDING_UNSUPPORTED_CLAIM,
                    source_artifact="coherence_validation.json",
                    description=(
                        "is_coherent=true pero gate coherence falló. "
                        "El diagnóstico podría afirmar coherencia no validada."
                    ),
                    pain_id="coherence_claim",
                ))

        return findings

    def _check_critical_priority(self, pain_ledger: Optional[dict]) -> list:
        """Verifica que brechas críticas tienen prioridad correcta."""
        findings = []

        if pain_ledger is None:
            return findings

        entries = pain_ledger.get("entries", [])
        for entry in entries:
            severity = entry.get("severity", "")
            pain_id = entry.get("pain_id", "unknown")

            if severity == SEVERITY_CRITICAL:
                confidence = entry.get("confidence", 0.0)
                if confidence < 0.5:
                    findings.append(self._make_finding(
                        severity=SEVERITY_WARNING,
                        clause="P6.1",
                        finding_type=FINDING_UNSUPPORTED_CLAIM,
                        source_artifact="pain_ledger.json",
                        description=(
                            f"pain_id '{pain_id}' marcado CRITICAL pero confidence={confidence:.2f} < 0.5. "
                            "Prioridad podría estar inflada."
                        ),
                        pain_id=pain_id,
                    ))

        return findings

    def _extract_pain_ids_from_ledger(self, pain_ledger: dict) -> set:
        """Extrae pain_ids del ledger."""
        entries = pain_ledger.get("entries", [])
        return {entry.get("pain_id") for entry in entries if entry.get("pain_id")}

    def _extract_pain_ids_from_diagnostic(self, diagnostic_md: str) -> set:
        """Extrae pain_ids mencionados en el diagnóstico markdown."""
        pain_ids = set()
        pattern = r'pain_id[\*`:\s]+([a-z_][a-z0-9_]*)'
        matches = re.findall(pattern, diagnostic_md, re.IGNORECASE)
        pain_ids.update(matches)

        pattern2 = r'`([a-z_][a-z0-9_]*)`'
        candidates = re.findall(pattern2, diagnostic_md)
        known_keywords = {"whatsapp", "schema", "faq", "llms", "conflict", "missing"}
        for candidate in candidates:
            if any(kw in candidate for kw in known_keywords):
                pain_ids.add(candidate)

        return pain_ids

    def _find_gate(self, gate_report: dict, gate_name: str) -> Optional[dict]:
        """Busca un gate específico en gate_report → gate_results."""
        gate_results = gate_report.get("gate_results", [])
        for gate in gate_results:
            if gate.get("gate_name") == gate_name:
                return gate
        return None

    def _make_finding(
        self,
        severity: str,
        clause: str,
        finding_type: str,
        source_artifact: str,
        description: str,
        pain_id: str = "",
    ) -> dict:
        """Construye un finding con estructura uniforme."""
        return {
            "severity": severity,
            "clause": clause,
            "finding_type": finding_type,
            "source_artifact": source_artifact,
            "description": description,
            "pain_id": pain_id,
        }

    def _compute_summary(self, findings: list) -> dict:
        """Calcula resumen de hallazgos."""
        critical = sum(1 for f in findings if f["severity"] == SEVERITY_CRITICAL)
        warning = sum(1 for f in findings if f["severity"] == SEVERITY_WARNING)
        info = sum(1 for f in findings if f["severity"] == SEVERITY_INFO)

        return {
            "total_findings": len(findings),
            "critical": critical,
            "warning": warning,
            "info": info,
        }

    def _compute_verdict(self, findings: list) -> str:
        """Determina veredicto basado en hallazgos."""
        critical_count = sum(1 for f in findings if f["severity"] == SEVERITY_CRITICAL)
        warning_count = sum(1 for f in findings if f["severity"] == SEVERITY_WARNING)

        if critical_count > 0:
            return VERDICT_BLOQUEAR
        elif warning_count >= 3:
            return VERDICT_DEVOLVER
        else:
            return VERDICT_APROBADO

    def _list_artifacts_read(self) -> list:
        """Lista artefactos que este revisor lee."""
        return [
            "01_DIAGNOSTICO_Y_OPORTUNIDAD_*.md",
            "coherence_validation.json",
            "pain_ledger.json",
            "pain_ledger_resolved.json",
            "gate_report_*.json",
        ]
