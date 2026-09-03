"""FASE-C (punto 8) — experimento contrafactual sobre artefactos REALES.

Re-procesa el corpus de referencia de SalenteReal
(`output/FASE-D_salentoreal_post_guard/v4_complete/`, corrida 2026-08-31 12:28:03)
con el código VIVO del repo y mide los 5 valores que AC5/AC6 necesitan:

    no_breach · coverage_ratio · unresolved · effective_total · is_coherent

No usa fixtures inventados: el pain_ledger resuelto, los assets generados y los
scores de los checks de coherencia salen de los JSON del run. Las funciones que
se ejercitan son las reales (`PainSolutionMapper.map_to_solutions`,
`V4AssetOrchestrator._solutions_to_asset_specs`,
`CoherenceValidator._check_assets_are_justified`, `AssetAlignmentMatrix.build`,
`AlignmentResult`).

Uso:  ./venv/Scripts/python.exe evidence/FASE-C/faseC_contrafactual.py
"""

import io
import json
import sys
from pathlib import Path
from types import SimpleNamespace

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

BASE = ROOT / "output/FASE-D_salentoreal_post_guard/v4_complete/hotelsalentoreal/v4_audit"


def _load(name):
    with open(BASE / name, encoding="utf-8") as f:
        return json.load(f)


def medir_matriz(pain_ledger, generated_assets):
    """AC5 — no_breach / coverage_ratio / unresolved / effective_total."""
    from modules.asset_generation.proposal_asset_alignment import AssetAlignmentMatrix
    from modules.delivery.delivery_context import DeliveryContext
    from modules.quality_gates.alignment_result import AlignmentResult

    matrix = AssetAlignmentMatrix.build(
        delivery_context=DeliveryContext(),
        pain_ledger=pain_ledger,
        generated_assets=generated_assets,
    )
    res = AlignmentResult.from_asset_alignment_matrix(matrix, None)
    d = res.to_dict()
    from collections import Counter
    return {
        "promised_services_total": d["promised_services_total"],
        "effective_total": d["effective_total"],
        "unresolved": d["unresolved"],
        "no_breach": d["no_breach"],
        "coverage_ratio": round(d["coverage_ratio"], 4),
        "actionable_total": d["actionable_total"],
        "delivery_ready": matrix.is_delivery_ready(),
        "status_counts": dict(Counter(e.status for e in matrix.entries)),
        "invariante_ok": (
            d["effective_total"] + d["unresolved"] + d["no_breach"]
            == d["promised_services_total"]
        ),
        "message": d["message"],
    }


def medir_coherencia(pains, pain_ledger, checks_reales):
    """AC6 — is_coherent, vía el check que realmente lo pone en false."""
    from modules.asset_generation.v4_asset_orchestrator import V4AssetOrchestrator
    from modules.commercial_documents.coherence_validator import CoherenceValidator
    from modules.commercial_documents.pain_solution_mapper import PainSolutionMapper

    solutions = PainSolutionMapper().map_to_solutions(pains)
    # _solutions_to_asset_specs no usa self: se invoca sin construir el orquestador.
    specs = V4AssetOrchestrator._solutions_to_asset_specs(None, solutions, pains)

    diagnostic = SimpleNamespace(problems=[{"id": p.id} for p in pains])
    validator = CoherenceValidator()
    chk = validator._check_assets_are_justified(specs, diagnostic)

    # Los otros 5 checks se toman del run real (este experimento solo re-ejecuta
    # el que el punto 8 altera: la lista de assets prometidos).
    scores = {c["name"]: c["score"] for c in checks_reales}
    scores["assets_are_justified"] = chk.score

    weights = CoherenceValidator.CHECK_WEIGHTS
    total_w = sum(weights.get(n, 1.0) for n in scores)
    overall = sum(s * weights.get(n, 1.0) for n, s in scores.items()) / total_w

    errors = []
    for c in checks_reales:
        if c["name"] == "assets_are_justified":
            if chk.severity == "error" and not chk.passed:
                errors.append(f"[{chk.name}] {chk.message}")
            continue
        if c.get("severity") == "error" and not c.get("passed"):
            errors.append(f"[{c['name']}] {c.get('message')}")

    threshold = validator.config.get_threshold("overall_coherence")
    return {
        "asset_specs": [(s.asset_type, list(s.pain_ids)) for s in specs],
        "specs_total": len(specs),
        "specs_sin_pain": [s.asset_type for s in specs if not s.pain_ids],
        "assets_are_justified_score": round(chk.score, 4),
        "assets_are_justified_passed": chk.passed,
        "assets_are_justified_severity": chk.severity,
        "assets_are_justified_message": chk.message,
        "overall_score": round(overall, 4),
        "threshold": threshold,
        "errors": errors,
        "is_coherent": (len(errors) == 0 and overall >= threshold),
    }


def main():
    ledger = _load("pain_ledger_resolved.json")
    ag = _load("asset_generation_report.json")
    coh = _load("coherence_validation.json")

    from modules.commercial_documents.pain_solution_mapper import Pain

    pains = [
        Pain(
            id=e["pain_id"],
            name=e.get("human_label", e["pain_id"]),
            description=e.get("human_label", e["pain_id"]),
            severity=str(e.get("severity", "medium")).lower(),
            detected_by=e.get("source_module", "unknown"),
            confidence=float(e.get("confidence", 0.0) or 0.0),
        )
        for e in ledger["entries"]
    ]
    generated_assets = [
        {"asset_type": a["asset_type"], "confidence_score": a.get("confidence_score")}
        for a in ag.get("generated_assets", [])
    ]

    print("=" * 76)
    print("FASE-C — CONTRAFACTUAL punto 8 sobre artefactos REALES de SalenteReal")
    print("=" * 76)
    print(f"corpus: {BASE}")
    print(f"run:    {ag.get('timestamp')}  hotel_id={ag.get('hotel_id')}")
    print(f"ledger resuelto: {len(pains)} pains -> {[p.id for p in pains]}")
    print(f"assets generados: {[a['asset_type'] for a in generated_assets]}")
    print(f"site_presence persistido: NO (A2 lo persiste en FASE-E) -> presencia=None")
    print()

    m = medir_matriz(ledger["entries"], generated_assets)
    print("--- MATRIZ / ALIGNMENT (AC5) ---")
    for k, v in m.items():
        print(f"  {k}: {v}")
    print()

    c = medir_coherencia(pains, ledger["entries"], coh["checks"])
    print("--- COHERENCIA (AC6) ---")
    for k, v in c.items():
        print(f"  {k}: {v}")
    print()

    print("--- LÍMITE P12/A3 (declarado, no ocultado) ---")
    pae = next(x for x in coh["checks"] if x["name"] == "promised_assets_exist")
    print(f"  promised_assets_exist: passed={pae['passed']} score={pae['score']}")
    print(f"  message: {pae['message']}")
    print("  => la rama de éxito hardcodea score=1.0 (coherence_validator.py:689-700)")
    print("     y está acotada por `if not generated_assets:` (:670, comentario H6 FIX):")
    print("     post-gen P6.3 NO tiene verificación de score. Este experimento NO se")
    print("     apoya en ese check para certificar nada; solo lo reporta como límite.")

    out = {"matriz": m, "coherencia": c}
    with open(ROOT / "evidence/FASE-C/faseC_contrafactual.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print()
    print("JSON -> evidence/FASE-C/faseC_contrafactual.json")


if __name__ == "__main__":
    main()
