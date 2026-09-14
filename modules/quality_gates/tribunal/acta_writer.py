"""ActaWriter — Writer de acta dual (JSON + MD) para el tribunal.

Produce ``acta_revision.json`` (machine-readable) y ``acta_revision.md``
(human-readable) a partir del veredicto del ``TribunalJudge``.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from .outcome import EXPECTED_REVIEWERS, ReviewerStatus

VERSION_FILE = Path(__file__).resolve().parents[3] / "VERSION.yaml"

VERSION_NO_DISPONIBLE = "version-no-disponible"


def _read_project_version() -> str:
    """Version del pipeline leida de VERSION.yaml (fuente unica del repo, AC-F6).

    Sin literal de respaldo: si VERSION.yaml no se puede leer el acta lo declara,
    porque una version plausible pero falsa es justo el defecto de fidelidad que
    este tribunal existe para evitar.
    """
    try:
        with open(VERSION_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("version:"):
                    return line.split(":", 1)[1].strip().strip('"').strip("'")
    except (OSError, UnicodeDecodeError):
        pass
    return VERSION_NO_DISPONIBLE


class ActaWriter:
    """Escribe el acta de revisión en formato JSON y Markdown."""

    def __init__(self, output_dir: str | Path):
        self.output_dir = Path(output_dir)

    def write(self, acta: dict) -> tuple[Path, Path]:
        """Escribe acta_revision.json + acta_revision.md.

        Retorna las rutas de ambos archivos creados.
        """
        self.output_dir.mkdir(parents=True, exist_ok=True)

        json_path = self.output_dir / "acta_revision.json"
        md_path = self.output_dir / "acta_revision.md"

        self._write_json(acta, json_path)
        self._write_md(acta, md_path)

        return json_path, md_path

    def _write_json(self, acta: dict, path: Path) -> None:
        """Escribe el JSON del acta."""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(acta, f, indent=2, ensure_ascii=False)

    def _write_md(self, acta: dict, path: Path) -> None:
        """Escribe el Markdown del acta con las 6 cláusulas P6."""
        verdict = acta.get("verdict", "DESCONOCIDO")
        evidence_tier = acta.get("evidence_tier", "?")
        hotel_id = acta.get("hotel_id", "N/A")
        timestamp = acta.get("timestamp", datetime.now().isoformat())
        clauses = acta.get("clauses", {})
        first_floor = acta.get("first_floor_rule", {})

        verdict_emoji = {
            "APROBADO-PARA-ENTREGA": "✅",
            "APROBADO-CONDICIONAL-PENDING-ONBOARDING": "⚠️",
            "DEVOLVER-CORRECCIONES": "🔄",
            "BLOQUEADO": "🚫",
        }.get(verdict, "❓")

        lines = [
            f"# Acta de Revisión — Tribunal de Certificación",
            f"",
            f"**Hotel**: {hotel_id}",
            f"**Fecha**: {timestamp}",
            f"**Veredicto**: {verdict_emoji} {verdict}",
            f"**Evidence Tier**: {evidence_tier}",
            f"**Cláusulas evaluadas**: {acta.get('clauses_evaluated', 6)}",
            f"",
        ]

        if first_floor.get("applied"):
            lines.extend([
                f"## Regla de Primer Piso",
                f"",
                f"**Aplicada**: Sí",
                f"**Artefacto fuente**: `{first_floor.get('source_artifact') or 'no informado por el Juez'}`",
                f"**Razón**: {first_floor.get('reason', 'N/A')}",
                f"",
            ])

        lines.append(f"## Cláusulas P6 Evaluadas")
        lines.append(f"")

        clause_titles = {
            "P6.1": "Critical Recall (Diagnóstico)",
            "P6.2": "Alineación de Promesas (NL)",
            "P6.3": "Completitud de Assets",
            "P6.4": "Cobertura Propuesta→Asset",
            "P6.5": "Honestidad Comercial (NL) — reservada Bot 4",
            "P6.6": "Coherencia + Contradicciones",
        }

        for clause_id in ["P6.1", "P6.2", "P6.3", "P6.4", "P6.5", "P6.6"]:
            clause = clauses.get(clause_id, {})
            status = clause.get("status", "NOT_EVALUABLE")
            source = clause.get("source_artifact", "N/A")
            finding = clause.get("finding", "Sin evaluación")

            status_emoji = {
                "PASS": "✅",
                "FAIL": "❌",
                "ADVISORY": "⚠️",
                "NOT_EVALUABLE": "⬜",
            }.get(status, "❓")

            title = clause_titles.get(clause_id, clause_id)

            lines.extend([
                f"### {clause_id}: {title}",
                f"",
                f"- **Status**: {status_emoji} {status}",
                f"- **Artefacto fuente**: `{source}`",
                f"- **Finding**: {finding}",
                f"",
            ])

        lines.extend(self._render_reviewer_reports(acta.get("reviewer_reports") or []))
        lines.extend(self._render_corrective_actions(acta.get("corrective_actions") or []))
        lines.extend(self._render_enforcement(acta.get("enforcement")))

        lines.extend([
            f"---",
            f"",
            f"*Generado por TribunalJudge v{_read_project_version()} — {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
        ])

        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    _STATUS_LABELS = {
        "OK_NO_FINDINGS": "✅ sin hallazgos",
        "OK_WITH_FINDINGS": "⚠️ con hallazgos",
        "ARTIFACT_MISSING": "⬜ artefacto ausente",
        "READER_FAILED": "🔴 lector fallido",
        "NOT_RUN": "🚫 no corrió",
    }

    def _render_reviewer_reports(self, reviewer_reports: list) -> list:
        """Sección `Reportes de Revisores`: **siempre**, una fila por Bot (AC-E0).

        Omitirla cuando la lista viene vacía es justo lo que NR8 prohíbe: en el MD
        «no corrieron», «sin hallazgos» y «fallaron» quedaban indistinguibles.
        """
        by_reviewer = {
            r.get("reviewer"): r for r in reviewer_reports if isinstance(r, dict)
        }
        expected = {spec.reviewer for spec in EXPECTED_REVIEWERS}
        ordered = [spec.reviewer for spec in EXPECTED_REVIEWERS]
        ordered += [r for r in by_reviewer if r not in expected]

        lines = [
            f"## Reportes de Revisores",
            f"",
            f"| Bot | Estado | Hallazgos | CRITICAL | Recomendación | Informe |",
            f"|-----|--------|-----------|----------|---------------|---------|",
        ]
        for reviewer in ordered:
            report = by_reviewer.get(reviewer) or {}
            status = report.get("status") or ReviewerStatus.NOT_RUN.value
            lines.append(
                f"| {reviewer} "
                f"| {self._STATUS_LABELS.get(status, status)} "
                f"| {report.get('findings_count', 0)} "
                f"| {report.get('critical_count', 0)} "
                f"| {report.get('recommendation') or 'N/A'} "
                f"| {report.get('report_path') or '—'} |"
            )
        lines.append(f"")
        return lines

    def _render_corrective_actions(self, corrective_actions: list) -> list:
        """Sección `Acciones correctivas`: qué hace el humano ante el bloqueo (§3.2)."""
        lines = [f"## Acciones correctivas", f""]
        if not corrective_actions:
            lines.extend([f"Ninguna: el acta no declaró hallazgos bloqueantes.", f""])
            return lines
        for action in corrective_actions:
            if not isinstance(action, dict):
                continue
            lines.extend([
                f"- **[{action.get('severity', '?')}] {action.get('finding_type', '?')}** "
                f"— dueño: `{action.get('owner', '?')}`",
                f"  - Artefacto: `{action.get('artifact', 'N/A')}`",
                f"  - Instrucción: {action.get('instruction', 'N/A')}",
            ])
        lines.append(f"")
        return lines

    def _render_enforcement(self, enforcement: Optional[dict]) -> list:
        """Sección `Enforcement`: el acta declara si el operador apagó el bloqueo (Q7)."""
        state = enforcement if isinstance(enforcement, dict) else {}
        enabled = state.get("enabled")
        suppressed = state.get("suppressed_by_operator")
        return [
            f"## Enforcement",
            f"",
            f"- **Knob**: `{state.get('blocking_env', 'desconocido')}`",
            f"- **Bloqueo activo**: {'Sí' if enabled else 'No' if enabled is False else 'Desconocido'}",
            f"- **Suprimido por el operador**: "
            f"{'SÍ — el ZIP se publicó sin aplicar el veredicto' if suppressed else 'No'}",
            f"",
        ]
