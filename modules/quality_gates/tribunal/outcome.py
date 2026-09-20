"""DTOs del veredicto enriquecido — contrato FASE-P1 §2.3.

El Juez decide sobre estos objetos; el acta se deriva de ellos (serie→documento,
nunca al revés). Ningún consumidor hace ``json.loads`` del acta para decidir.
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Iterable, Mapping, Optional


GATE_BLOCKING_ENV = "GATE_BLOCKING_ENABLED"

RECOMMENDATION_BLOCK = "BLOQUEAR"
RECOMMENDATION_RETURN_TESTS = "DEVOLVER-PRUEBAS"
SEVERITY_CRITICAL = "CRITICAL"

# FASE-0 (AC20-ii): proyección que el acta publica de cada hallazgo.
# ``ACTA_FINDING_KEYS`` es la lista blanca de claves y ``ACTA_FINDING_TEXT_LIMIT``
# acota la descripción: el acta debe nombrar la causa sin convertirse en una
# segunda copia de los ``revision_*.json``, que ya llevan el hallazgo completo.
# ``ACTA_FINDING_CAP`` acota CUÁNTOS hallazgos por revisor se proyectan; se
# declara aquí y viaja en ``findings_omitted`` para que un techo nunca se lea
# como "sin causas" (L-R.4: una regla sin verificador declara su límite).
ACTA_FINDING_KEYS = ("finding_type", "severity", "clause", "description")
ACTA_FINDING_TEXT_LIMIT = 240
ACTA_FINDING_CAP = 20


def _acta_finding_projection(finding: Any) -> Optional[Mapping[str, Any]]:
    """Recorta un hallazgo a las claves que el acta necesita; ``None`` si no es mapeable."""
    if not isinstance(finding, Mapping):
        return None
    projected: dict = {}
    for key in ACTA_FINDING_KEYS:
        value = finding.get(key)
        if value is None:
            continue
        if isinstance(value, str) and len(value) > ACTA_FINDING_TEXT_LIMIT:
            value = value[:ACTA_FINDING_TEXT_LIMIT] + "…"
        projected[key] = value
    return projected or None


class ReviewerStatus(str, Enum):
    """Estado de lectura de un revisor (Q6 / NR8).

    Los cuatro estados de NR8 distinguen *si la revisión ocurrió y fue legible*.
    ``OK_WITH_FINDINGS`` no es un quinto estado: refina la familia ``OK_*`` que la
    matriz §2.1 ya escribe con comodín, para que un acta no pueda declarar
    ``OK_NO_FINDINGS`` junto con ``findings_count: 3``.
    """

    OK_NO_FINDINGS = "OK_NO_FINDINGS"
    OK_WITH_FINDINGS = "OK_WITH_FINDINGS"
    ARTIFACT_MISSING = "ARTIFACT_MISSING"
    READER_FAILED = "READER_FAILED"
    NOT_RUN = "NOT_RUN"

    @property
    def is_ok(self) -> bool:
        return self.value.startswith("OK_")

    @property
    def blocks_approval(self) -> bool:
        """Ausencia jamás es PASS: impide APROBADO-PARA-ENTREGA (regla 2 de DA-P1.6)."""
        return self is not ReviewerStatus.OK_NO_FINDINGS and self is not ReviewerStatus.OK_WITH_FINDINGS


@dataclass
class ReviewerSpec:
    """Lo que el tribunal espera de cada Bot: nombre, artefacto y cláusulas."""

    reviewer: str
    report_filename: str
    clauses: tuple


# Orden del contrato §4: una entrada por Bot, siempre presente.
EXPECTED_REVIEWERS = (
    ReviewerSpec("diagnosis_reviewer", "revision_diagnostico.json", ("P6.1",)),
    ReviewerSpec("asset_reviewer", "revision_assets.json", ("P6.3", "P6.4")),
    ReviewerSpec("alignment_reviewer", "revision_alineacion.json", ("P6.2",)),
    ReviewerSpec("honesty_reviewer", "revision_honestidad.json", ("P6.5",)),
)

_OWNER_BY_REVIEWER = {
    "diagnosis_reviewer": "equipo-diagnostico",
    "asset_reviewer": "equipo-assets",
    "alignment_reviewer": "equipo-propuesta",
    "honesty_reviewer": "comercial",
}
_DEFAULT_OWNER = "pipeline-v4complete"


@dataclass
class ReviewerReport:
    """Resumen determinista del informe de un Bot, listo para decidir."""

    reviewer: str
    status: ReviewerStatus
    findings_count: int = 0
    critical_count: int = 0
    recommendation: Optional[str] = None
    report_path: Optional[str] = None
    clauses: tuple = ()
    findings: list = field(default_factory=list)

    def to_dict(self) -> dict:
        """Forma del bloque ``reviewer_reports`` del acta (JSON y MD).

        FASE-0 (AC20-ii): antes proyectaba solo conteos, así que un acta con
        ``critical_count: 1`` no decía CUÁL era el hallazgo y AC12 no tenía de
        dónde leer la causa. Se agregan ``findings`` (proyección de
        :data:`ACTA_FINDING_KEYS`, tope :data:`ACTA_FINDING_CAP`) y
        ``findings_omitted`` solo cuando se supera ese tope. Es un cambio de
        serialización, no de veredicto: ``verified_critical``, ``verified_block``
        y demás predicados siguen mirando los mismos campos de siempre.
        """
        payload = {
            "reviewer": self.reviewer,
            "status": self.status.value,
            "findings_count": self.findings_count,
            "critical_count": self.critical_count,
            "recommendation": self.recommendation,
            "report_path": self.report_path,
            "findings": [
                projected
                for projected in (
                    _acta_finding_projection(f) for f in self.findings[:ACTA_FINDING_CAP]
                )
                if projected is not None
            ],
        }
        omitted = len(self.findings) - min(len(self.findings), ACTA_FINDING_CAP)
        if omitted > 0:
            payload["findings_omitted"] = omitted
        return payload

    @property
    def verified_critical(self) -> bool:
        """CRITICAL *verificado*: status OK_* con critical_count >= 1 (matriz §2.1 fila 2)."""
        return self.status.is_ok and self.critical_count >= 1

    @property
    def verified_block(self) -> bool:
        return self.status.is_ok and self.recommendation == RECOMMENDATION_BLOCK

    @property
    def verified_return_for_tests(self) -> bool:
        return (
            self.status.is_ok
            and self.recommendation == RECOMMENDATION_RETURN_TESTS
            and self.critical_count >= 1
        )


@dataclass
class CorrectiveAction:
    """Acción correctiva derivada de un hallazgo bloqueante (consecuencia Q1b)."""

    finding_type: str
    severity: str
    artifact: str
    instruction: str
    owner: str

    def to_dict(self) -> dict:
        return {
            "finding_type": self.finding_type,
            "severity": self.severity,
            "artifact": self.artifact,
            "instruction": self.instruction,
            "owner": self.owner,
        }


@dataclass
class EnforcementState:
    """Estado del kill switch en el momento de decidir (escape honesto, Q7)."""

    blocking_env: str = GATE_BLOCKING_ENV
    enabled: bool = True
    suppressed_by_operator: bool = False

    def to_dict(self) -> dict:
        return {
            "blocking_env": self.blocking_env,
            "enabled": self.enabled,
            "suppressed_by_operator": self.suppressed_by_operator,
        }


@dataclass
class TribunalOutcome:
    """Lo que main.py consume: publica o suprime, y qué se le dice al operador."""

    verdict: str
    blocks_publish: bool
    corrective_actions: list = field(default_factory=list)
    enforcement: EnforcementState = field(default_factory=EnforcementState)

    def acta_fields(self) -> dict:
        """Campos que el acta deriva del DTO (nunca al revés)."""
        return {
            "enforcement": self.enforcement.to_dict(),
            "corrective_actions": [a.to_dict() for a in self.corrective_actions],
        }


def not_run_reports() -> list:
    """Los cuatro revisores en NOT_RUN: el estado de ``evaluate()`` antes del cableado."""
    return [
        ReviewerReport(reviewer=spec.reviewer, status=ReviewerStatus.NOT_RUN, clauses=spec.clauses)
        for spec in EXPECTED_REVIEWERS
    ]


def _read_report_json(path: Path) -> Optional[dict]:
    try:
        import json

        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, ValueError):
        return None


def _counts_from(payload: Mapping[str, Any]) -> tuple:
    """(findings_count, critical_count, findings) desde el informe del Bot.

    Se cuenta desde ``findings[]`` porque el ``summary`` tiene una forma distinta
    por revisor; carecer de ``findings`` es un fallo de lectura, no 'sin hallazgos'.
    """
    findings = payload.get("findings")
    if not isinstance(findings, list):
        return None
    critical = sum(1 for f in findings if isinstance(f, Mapping) and f.get("severity") == SEVERITY_CRITICAL)
    return len(findings), critical, [f for f in findings if isinstance(f, Mapping)]


def collect_reviewer_reports(
    v4_audit_dir: str | Path,
    written: Optional[Mapping[str, Optional[Path]]] = None,
) -> list:
    """Construye los 4 `ReviewerReport` desde los artefactos de la corrida.

    ``written`` mapea revisor → ruta escrita por ese Bot en esta corrida, o ``None``
    si corrió y reventó. Sin clave = no corrió (``NOT_RUN``), que tras el
    reordenamiento es un canario de cableado roto (regla 4 de DA-P1.6).
    ``written=None`` (llamada sin cableado, p. ej. tests) resuelve por nombre.
    """
    audit_dir = Path(v4_audit_dir)
    reports: list = []

    for spec in EXPECTED_REVIEWERS:
        declared = None if written is None else (spec.reviewer in written)
        path_value = None if written is None else written.get(spec.reviewer)

        if written is not None and not declared:
            reports.append(ReviewerReport(reviewer=spec.reviewer, status=ReviewerStatus.NOT_RUN, clauses=spec.clauses))
            continue

        if written is not None and declared and path_value is None:
            reports.append(ReviewerReport(reviewer=spec.reviewer, status=ReviewerStatus.READER_FAILED, clauses=spec.clauses))
            continue

        path = Path(path_value) if path_value else audit_dir / spec.report_filename
        if not path.exists():
            reports.append(ReviewerReport(reviewer=spec.reviewer, status=ReviewerStatus.ARTIFACT_MISSING, clauses=spec.clauses))
            continue

        payload = _read_report_json(path)
        counts = _counts_from(payload) if isinstance(payload, Mapping) else None
        if payload is None or counts is None:
            reports.append(ReviewerReport(reviewer=spec.reviewer, status=ReviewerStatus.READER_FAILED, clauses=spec.clauses))
            continue

        findings_count, critical_count, findings = counts
        reports.append(ReviewerReport(
            reviewer=spec.reviewer,
            status=(
                ReviewerStatus.OK_NO_FINDINGS
                if findings_count == 0
                else ReviewerStatus.OK_WITH_FINDINGS
            ),
            findings_count=findings_count,
            critical_count=critical_count,
            recommendation=payload.get("verdict_recommendation"),
            report_path=path.name,
            clauses=spec.clauses,
            findings=findings,
        ))

    return reports


def _clause_instruction(clause: str, finding: str) -> str:
    return f"Resolver {finding} antes de publicar ({clause})"


def derive_corrective_actions(
    reports: Iterable[ReviewerReport],
    clauses: Optional[Mapping[str, Mapping[str, Any]]] = None,
    blocking: bool = False,
    verdict: str = "",
) -> list:
    """Un `CorrectiveAction` por hallazgo bloqueante, con dueño (contrato §3.2).

    Si el bloqueo viene de un gate y ningún revisor lo documentó, se emite la
    acción desde la cláusula: un veredicto bloqueante nunca deja el acta sin
    camino de reparación.
    """
    actions: list = []
    for report in reports:
        if not report.status.is_ok:
            continue
        report_blocks = report.verified_critical or report.verified_block or report.verified_return_for_tests
        if not report_blocks:
            continue
        owner = _OWNER_BY_REVIEWER.get(report.reviewer, _DEFAULT_OWNER)
        criticals = [
            f for f in report.findings if f.get("severity") == SEVERITY_CRITICAL
        ]
        if not criticals and report.recommendation in (RECOMMENDATION_BLOCK, RECOMMENDATION_RETURN_TESTS):
            criticals = [{
                "finding_type": report.recommendation,
                "severity": SEVERITY_CRITICAL,
                "source_artifact": report.report_path,
                "description": f"El revisor recomienda {report.recommendation} sin declarar un hallazgo CRITICAL",
            }]
        for finding in criticals:
            actions.append(CorrectiveAction(
                finding_type=str(finding.get("finding_type") or report.recommendation or "UNSPECIFIED"),
                severity=str(finding.get("severity") or SEVERITY_CRITICAL),
                artifact=str(finding.get("source_artifact") or report.report_path or "sin artefacto"),
                instruction=str(finding.get("description") or _clause_instruction(
                    ",".join(report.clauses), str(finding.get("finding_type") or "")
                )),
                owner=owner,
            ))

    if not blocking or actions:
        return actions

    for clause_id, clause in (clauses or {}).items():
        if not isinstance(clause, Mapping) or clause.get("status") != "FAIL":
            continue
        actions.append(CorrectiveAction(
            finding_type=f"CLAUSE_{clause_id}_FAIL",
            severity=SEVERITY_CRITICAL,
            artifact=str(clause.get("source_artifact") or clause_id),
            instruction=str(clause.get("finding") or f"Cláusula {clause_id} en FAIL"),
            owner="quality-gates",
        ))

    if not actions:
        actions.append(CorrectiveAction(
            finding_type="VEREDICTO_BLOQUEANTE_SIN_HALLAZGO",
            severity=SEVERITY_CRITICAL,
            artifact="acta_revision.json",
            instruction=(
                f"El veredicto {verdict} bloquea la publicación pero ningún revisor ni "
                "cláusula documentó el motivo: revisar el tribunal antes de publicar."
            ),
            owner=_DEFAULT_OWNER,
        ))
    return actions


def build_outcome(
    verdict: str,
    blocks: bool,
    reports: Iterable[ReviewerReport],
    clauses: Optional[Mapping[str, Mapping[str, Any]]] = None,
    gate_blocking_enabled: bool = True,
) -> TribunalOutcome:
    """Consecuencia del bloqueo bajo el knob único del operador (Q7)."""
    enabled = bool(gate_blocking_enabled)
    outcome = TribunalOutcome(
        verdict=verdict,
        blocks_publish=bool(blocks) and enabled,
        corrective_actions=derive_corrective_actions(
            reports, clauses, blocking=bool(blocks), verdict=verdict
        ),
        enforcement=EnforcementState(
            blocking_env=GATE_BLOCKING_ENV,
            enabled=enabled,
            suppressed_by_operator=bool(blocks) and not enabled,
        ),
    )
    return outcome
