"""ActaWriter — Writer de acta dual (JSON + MD) para el tribunal.

Produce ``acta_revision.json`` (machine-readable) y ``acta_revision.md``
(human-readable) a partir del veredicto del ``TribunalJudge``.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional


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
                f"**Artefacto fuente**: `MANIFEST.json` (evidence_tier)",
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

        reviewer_reports = acta.get("reviewer_reports", [])
        if reviewer_reports:
            lines.extend([
                f"## Reportes de Revisores",
                f"",
            ])
            for report in reviewer_reports:
                lines.append(f"- `{report}`")
            lines.append(f"")

        lines.extend([
            f"---",
            f"",
            f"*Generado por TribunalJudge v4.76.0 — {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
        ])

        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
