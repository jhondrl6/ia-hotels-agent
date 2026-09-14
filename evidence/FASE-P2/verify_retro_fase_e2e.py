"""Retro estructural de FASE-P2 sobre la corrida E2E congelada del predecesor.

Re-ejecutable: `python evidence/FASE-P2/verify_retro_fase_e2e.py`

No modifica el repositorio: copia `evidence/FASE-E2E/` (la corrida real de
v4complete del plan TRIBUNAL-OFFLINE) a un directorio temporal, le aplica el flujo
nuevo del tribunal (primera pasada → leer los 4 informes → segunda pasada →
outcome) y publica el **diff estructural** contra el acta congelada (L-VUP-14: se
comparan claves y estados, nunca el aspecto del documento).

Expected del diff:
- Ninguna clave del acta desaparece; las cláusulas no cambian de estado (NR2: el
  tribunal no recalcula gates ni los blanquea).
- `verdict` y `evidence_tier` se re-anclan: el veredicto que salía solo de gates
  pasa a consumir las objeciones verificadas de los revisores (eso es AC-E2).
- Claves nuevas: las tres del contrato (reviewer_reports deja de estar vacía,
  enforcement, corrective_actions).
"""

import json
import shutil
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from modules.quality_gates.tribunal.acta_writer import ActaWriter  # noqa: E402
from modules.quality_gates.tribunal.asset_reviewer import AssetReviewer  # noqa: E402
from modules.quality_gates.tribunal.judge import (  # noqa: E402
    TribunalJudge,
    blocks_delivery_zip,
)

E2E_DIR = PROJECT_ROOT / "evidence" / "FASE-E2E"
REPORT = Path(__file__).resolve().parent / "retro-estructural-FASE-E2E.md"

CONTRACTUAL_NEW_KEYS = {"enforcement", "corrective_actions"}


def _shape(value):
    if isinstance(value, dict):
        return f"dict({len(value)})"
    if isinstance(value, list):
        return f"list({len(value)})"
    return f"{type(value).__name__}={value!r}"


def structural_diff(before: dict, after: dict) -> list:
    rows = []
    for key in sorted(set(before) | set(after)):
        if key not in before:
            rows.append((key, "—", _shape(after[key]), "ALTA (nueva)"))
        elif key not in after:
            rows.append((key, _shape(before[key]), "—", "BAJA (desapareció)"))
        elif before[key] != after[key]:
            if key == "clauses":
                rows.append((key, "ver cláusulas", "ver cláusulas", "CAMBIO (detalle abajo)"))
            elif key == "reviewer_reports":
                rows.append((key, _shape(before[key]), _shape(after[key]), "CAMBIO (poblado)"))
            else:
                rows.append((key, _shape(before[key]), _shape(after[key]), "CAMBIO"))
        else:
            rows.append((key, _shape(before[key]), _shape(after[key]), "igual"))
    return rows


def main() -> int:
    if not E2E_DIR.exists():
        print(f"!! no existe la corrida congelada: {E2E_DIR}")
        return 2

    frozen = json.loads((E2E_DIR / "acta_revision.json").read_text(encoding="utf-8"))
    workdir = Path(tempfile.mkdtemp(prefix="p2_retro_"))
    try:
        audit = workdir / "v4_audit"
        shutil.copytree(E2E_DIR, audit)
        deliveries = audit / "deliveries"

        judge = TribunalJudge(
            v4_audit_dir=audit,
            deliveries_dir=deliveries,
            hotel_id=frozen.get("hotel_id") or "hotelsalentoreal",
        )
        first_pass = judge.evaluate()
        reports = judge.collect_reviewer_reports()
        acta = judge.enrich(first_pass, reports)
        blocks = blocks_delivery_zip(acta)
        outcome = judge.finalize(acta, reports, blocks=blocks, gate_blocking_enabled=True)
        json_path, md_path = ActaWriter(audit / "acta_out").write(acta)
        written = json.loads(json_path.read_text(encoding="utf-8"))
        md_text = md_path.read_text(encoding="utf-8")

        asset_review = AssetReviewer(audit, deliveries).review()

        rows = structural_diff(frozen, written)
        clause_rows = [
            (cid, frozen["clauses"][cid]["status"], written["clauses"][cid]["status"])
            for cid in sorted(frozen["clauses"])
        ]

        lines = [
            "# Retro estructural — FASE-P2 sobre la corrida E2E congelada",
            "",
            f"Baseline: `evidence/FASE-E2E/acta_revision.json` (regimen advisory, "
            f"verdict `{frozen['verdict']}`).",
            "",
            "## Diff estructural del acta (claves)",
            "",
            "| Clave | Antes (congelado) | Después (P2) | Delta |",
            "|-------|-------------------|--------------|-------|",
        ]
        for key, before, after, delta in rows:
            lines.append(f"| `{key}` | {before} | {after} | {delta} |")
        for cid, before, after in clause_rows:
            lines.append(f"| `clauses.{cid}` | {before} | {after} | "
                         f"{'igual' if before == after else 'CAMBIO'} |")

        lines += [
            "",
            "## reviewer_reports (los cuatro estados del contrato)",
            "",
            "| Bot | status | findings | critical | recomendación |",
            "|-----|--------|----------|----------|---------------|",
        ]
        for entry in written["reviewer_reports"]:
            lines.append(
                f"| {entry['reviewer']} | `{entry['status']}` | {entry['findings_count']} "
                f"| {entry['critical_count']} | {entry['recommendation']} |"
            )

        lines += [
            "",
            "## Consecuencia sobre el paquete de la corrida",
            "",
            f"- `blocks_delivery_zip` → **{blocks}** (único predicado, NR3)",
            f"- `outcome.blocks_publish` → **{outcome.blocks_publish}**",
            f"- acciones correctivas derivadas: **{len(outcome.corrective_actions)}**",
            f"- enforcement: `{json.dumps(written['enforcement'], ensure_ascii=False)}`",
            f"- Bot 3 sobre el ZIP congelado: `implementation_order_check` = "
            f"`{json.dumps(asset_review['implementation_order_check'], ensure_ascii=False)}`, "
            f"recomendación `{asset_review['verdict_recommendation']}`",
            "",
            "## Presencia de secciones en el MD",
            "",
        ]
        for section in ("## Reportes de Revisores", "## Acciones correctivas", "## Enforcement"):
            lines.append(f"- `{section}` → {'presente' if section in md_text else 'AUSENTE'}")

        verdict_change = (
            f"- veredicto: `{frozen['verdict']}` → `{written['verdict']}`; "
            f"tier: `{frozen['evidence_tier']}` → `{written['evidence_tier']}`"
        )
        lines += ["", verdict_change, ""]

        disappeared = [k for k, b, a, d in rows if d.startswith("BAJA")]
        clause_moved = [cid for cid, b, a in clause_rows if b != a]
        unexpected = {k for k, b, a, d in rows if d.startswith("ALTA")} - CONTRACTUAL_NEW_KEYS - {"reviewer_reports"}
        checks = [
            ("ninguna clave del acta desaparece", not disappeared),
            ("las cláusulas no cambian de estado (NR2, sin blanqueo de gates)", not clause_moved),
            ("las únicas altas son las del contrato §4", not unexpected),
            ("reviewer_reports deja de estar vacío", len(written["reviewer_reports"]) == 4),
            ("la sección de revisores está en el MD", "## Reportes de Revisores" in md_text),
        ]
        lines += ["## Gates del retro", ""]
        for label, ok in checks:
            lines.append(f"- [{'x' if ok else ' '}] {label}")

        report = "\n".join(lines) + "\n"
        REPORT.write_text(report, encoding="utf-8")
        print(report)
        print(f"[{'OK' if all(ok for _, ok in checks) else 'FALLO'}] retro escrito en {REPORT}")
        return 0 if all(ok for _, ok in checks) else 1
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
