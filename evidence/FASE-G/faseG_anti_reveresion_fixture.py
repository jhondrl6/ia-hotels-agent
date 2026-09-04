"""FASE-G: genera el fixture anti-reversión BUG-6/N2 con el gate REAL.

Caso Zione (2026-07-25): whatsapp_button existe en producción pero el doc no
lo menciona. En la era post-P1-D ese estado llega como VERIFIED_IN_SITE
(primera clase, preservado por el reconciler) — el estrechamiento V5 de G3
solo afecta a ASSET_GENERATED silencioso, así que este caso NO debe bloquear.

Escribe evidence/FASE-G/faseG_anti_reveresion_fixture.json con el assessment
de entrada y el resultado real del gate.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from modules.quality_gates.publication_gates import (
    PublicationGatesOrchestrator,
    PublicationGateConfig,
)

assessment = {
    "pain_ledger": [
        {"pain_id": "no_whatsapp_visible", "status": "VERIFIED_IN_SITE"},
    ],
    "diagnostic_pain_ids": [],
    "proposal_pain_ids": [],
}

orchestrator = PublicationGatesOrchestrator(PublicationGateConfig())
result = orchestrator._coverage_gate(assessment)

fixture = {
    "caso": "Zione 2026-07-25 — asset existe en producción, doc no lo menciona",
    "regla_v5": (
        "ASSET_GENERATED permanece en _JUSTIFIED_STATUSES (anti-reversión "
        "BUG-6); solo el par generado+silencioso deja de justificar. El caso "
        "moderno 'existe en producción' es VERIFIED_IN_SITE y justifica sin "
        "mención."
    ),
    "assessment": assessment,
    "gate_result": {
        "gate_name": result.gate_name,
        "passed": result.passed,
        "status": result.status.value if hasattr(result.status, "value") else str(result.status),
        "value": result.value,
        "message": result.message,
        "details": result.details,
    },
    "aserciones": {
        "passed": result.passed is True,
        "justified_1": result.details.get("justified") == 1,
        "uncovered_vacio": result.details.get("uncovered") == [],
        "asset_generated_en_justified_statuses": (
            "ASSET_GENERATED" in PublicationGatesOrchestrator._JUSTIFIED_STATUSES
        ),
    },
}

out = Path(__file__).resolve().parent / "faseG_anti_reveresion_fixture.json"
out.write_text(json.dumps(fixture, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"OK -> {out}")
print(json.dumps(fixture["aserciones"], indent=2))
assert all(fixture["aserciones"].values()), "anti-reversión VIOLADA"
print("ANTI-REVERSIÓN OK: el caso Zione NO se bloquea bajo V5.")
