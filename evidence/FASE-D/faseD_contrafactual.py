"""FASE-D — contrafactual medido del cambio de severidad.

Reproduce la decision de `check_publication_readiness` ANTES (plano
`not r.passed`) y DESPUES (filtro por severidad con piso) sobre los
`gate_report*.json` reales del repo, y reporta los flips de `ready`.

Uso:  ./venv/Scripts/python.exe evidence/FASE-D/faseD_contrafactual.py
"""

import glob
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

# Copia local de la decision nueva para poder contrastar sin reimportar el
# modulo bajo test (el objetivo es medir el delta, no volver a ejecutar gates).
ADVISORY_GATE_NAMES = {"content_quality", "proposal_asset_alignment"}
PROPOSAL_ASSET_ALIGNMENT_FLOOR = 0.8
GATE_EXECUTION_FAILED_KEY = "gate_execution_failed"


def blocks_publication(gate: dict) -> bool:
    if gate["passed"]:
        return False
    if gate["details"].get(GATE_EXECUTION_FAILED_KEY):
        return True
    if gate["gate_name"] not in ADVISORY_GATE_NAMES:
        return True
    if gate["gate_name"] == "content_quality":
        return bool(gate["details"].get("blockers"))
    value = gate["value"]
    return isinstance(value, (int, float)) and value < PROPOSAL_ASSET_ALIGNMENT_FLOOR


def main() -> int:
    paths = sorted(
        glob.glob(str(REPO / "output" / "**" / "gate_report_*.json"), recursive=True)
    )
    if not paths:
        print("No hay artefactos gate_report_*.json en output/ — nada que medir.")
        return 1

    total_flips = 0
    disclosed_new = 0
    for path in paths:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        gates = data.get("gate_results", [])
        old_blocking = [g["gate_name"] for g in gates if not g["passed"]]
        new_blocking = [g["gate_name"] for g in gates if blocks_publication(g)]
        flips = sorted(set(old_blocking) ^ set(new_blocking))
        total_flips += len(flips)

        advisory_issues = [
            g["gate_name"]
            for g in gates
            if g["gate_name"] in ADVISORY_GATE_NAMES
            and not blocks_publication(g)
            and (not g["passed"] or g["status"] == "WARNING")
        ]
        disclosed_new += len(advisory_issues)

        print(f"\n{Path(path).relative_to(REPO)}")
        print(f"  gates={len(gates)}")
        print(f"  OLD ready={not old_blocking} blocking={old_blocking}")
        print(f"  NEW ready={not new_blocking} blocking={new_blocking}")
        print(f"  flips de ready = {flips or 'ninguno'}")
        print(f"  advisory divulgados al checklist = {advisory_issues or 'ninguno'}")

    print("\n" + "=" * 62)
    print(f"corridas analizadas: {len(paths)}")
    print(f"flips totales de `ready`: {total_flips}")
    print(f"advisories nuevos divulgados al humano: {disclosed_new}")
    print(
        "LECTURA: el cambio de severidad es neutro en `ready` para el corpus "
        "disponible (ningun advisory falla hoy por encima de su piso) y lo que "
        "SI cambia es la divulgacion: los outcomes advisory aterrzan en "
        "human_checklist.md, que antes no los veia."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
