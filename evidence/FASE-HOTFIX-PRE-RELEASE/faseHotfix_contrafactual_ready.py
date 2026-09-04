"""FASE-HOTFIX-PRE-RELEASE — contrafactual de 0 flips de `ready`.

El plan exige **re-producir** el contrafactual, no asumirlo: esta sesion escribe
codigo de produccion (H2 serializa, H3 publica, H6 reescribe un mensaje), y la
promesa es que ninguna decision de negocio cambia.

Metodo (L-F3: reproducir la lectura del consumidor de produccion): tomar cada
`gate_report_*.json` persistido, reconstruir sus `PublicationGateResult` tal como
el artefacto los declara, volver a decidir `ready` con el codigo de HEAD y
comparar contra el `readiness` que esa corrida publico.

Solo lectura sobre los artefactos. Re-ejecutable:
    python evidence/FASE-HOTFIX-PRE-RELEASE/faseHotfix_contrafactual_ready.py
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from modules.quality_gates.publication_gates import (  # noqa: E402
    GateStatus,
    PublicationGateResult,
    check_publication_readiness,
    gate_severity,
)

ARTIFACTOS = [
    ROOT / "evidence/FASE-I/corrida/hotelsalentoreal/v4_audit/gate_report_20260904_120413.json",
    ROOT / "output/FASE-D_salentoreal_post_guard/v4_complete/hotelsalentoreal/v4_audit/gate_report_20260831_122803.json",
    ROOT / "output/FASE-D_salentoreal_post_guard/v4_complete/deliveries/hotelsalentoreal_20260831/ASSETS/v4_audit/gate_report_20260831_122803.json",
]

if __name__ == "__main__":
    flips = 0
    for ruta in ARTIFACTOS:
        if not ruta.exists():
            print(f"AUSENTE (no evaluable): {ruta}")
            continue
        data = json.loads(ruta.read_text(encoding="utf-8"))
        results = [
            PublicationGateResult(
                gate_name=g["gate_name"], passed=g["passed"], status=GateStatus(g["status"]),
                message=g["message"], value=g["value"], suggestion=g.get("suggestion", ""),
                details=g.get("details", {}) or {},
            )
            for g in data["gate_results"]
        ]
        rede = check_publication_readiness({}, gate_results=results)
        antes = data["readiness"]["ready"]
        despues = rede["ready"]
        mismo = antes == despues
        flips += 0 if mismo else 1
        print(f"{ruta.parent.parent.name}/{ruta.name}")
        print(f"  gates re-evaluados = {len(results)} "
              f"(blocking declarados = "
              f"{sum(1 for r in results if gate_severity(r.gate_name) == 'blocking')}, "
              f"advisory = {sum(1 for r in results if gate_severity(r.gate_name) == 'advisory')})")
        print(f"  ready  publicado = {antes}   ready  re-producido = {despues}   "
              f"{'IGUAL' if mismo else '*** FLIP ***'}")
        print(f"  blocking_issues publicado = {len(data['readiness']['blocking_issues'])}   "
              f"re-producido = {len(rede['blocking_issues'])}")
    print(f"\nFLIPS de ready = {flips} / {len(ARTIFACTOS)} artefactos evaluados")
    print("CONTRAFACTUAL: 0 flips => ninguna decision de negocio cambio"
          if flips == 0 else "CONTRAFACTUAL FALLIDO: revisar alcance de la sesion")
    sys.exit(1 if flips else 0)
