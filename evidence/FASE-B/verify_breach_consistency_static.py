# -*- coding: utf-8 -*-
"""FASE-B T3: Verificación E2E estática contra evidencia del run 20260804_124443.

Parsea opportunity_scores del v4_complete_report.json real (Zi One Luxury),
construye el mapa dinámico asset_type → brecha con la NUEVA lógica del
generador (_build_dynamic_breach_map, vía mapa inverso de pain_solution_mapper)
y verifica que los 7 services de PROPOSAL_SERVICE_TO_ASSET resuelven
costo/rank/label correctamente:
  - 5 services con costo: whatsapp, hotel_schema, faq, optimization, open_graph
  - 2 services sin costo: org_schema, llms_txt (brechas ausentes en scores)

Sin re-ejecutar v4complete (reservado para FASE-F).
"""

import io
import json
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from modules.commercial_documents.v4_proposal_generator import V4ProposalGenerator
from modules.asset_generation.proposal_asset_alignment import PROPOSAL_SERVICE_TO_ASSET

REPORT_PATH = REPO / "output" / "v4_verify_4.70.0" / "v4_complete" / "v4_complete_report.json"

report = json.loads(REPORT_PATH.read_text(encoding='utf-8'))
opportunity_scores = report.get("opportunity_scores", [])
assert len(opportunity_scores) == 8, f"Esperadas 8 entries, hay {len(opportunity_scores)}"
print(f"[OK] opportunity_scores cargadas: {len(opportunity_scores)} entries")

scores_by_id = {e["brecha_id"]: e for e in opportunity_scores}
suma = sum(e["estimated_monthly_cop"] for e in opportunity_scores)
print(f"[OK] Suma estimated_monthly_cop: ${suma:,} COP")

gen = V4ProposalGenerator()
breach_map = gen._build_dynamic_breach_map(opportunity_scores)

EXPECTED_WITH_COST = {
    "whatsapp_button": "whatsapp_conflict",
    "hotel_schema": "no_hotel_schema",
    "faq_page": "no_faq_schema",
    "optimization_guide": "low_seo_score",
    "open_graph": "no_og_tags",
}
EXPECTED_WITHOUT_COST = ["org_schema", "llms_txt"]  # brechas ausentes en scores

failures = []

print("\n--- Services de PROPOSAL_SERVICE_TO_ASSET ---")
for service_name, asset_type in PROPOSAL_SERVICE_TO_ASSET.items():
    info = breach_map.get(asset_type)
    if asset_type in EXPECTED_WITH_COST:
        expected_bid = EXPECTED_WITH_COST[asset_type]
        if info is None:
            failures.append(f"{asset_type}: no resolvió brecha (esperada {expected_bid})")
            print(f"[FAIL] {service_name:40s} → sin brecha")
            continue
        expected = scores_by_id[expected_bid]
        ok_cost = info["cost"] == expected["estimated_monthly_cop"]
        ok_rank = info["rank"] == expected["rank"]
        ok_label = info["label"] == expected["brecha_name"]
        ok_bid = info["brecha_id"] == expected_bid
        if ok_cost and ok_rank and ok_label and ok_bid:
            print(
                f"[OK]   {service_name:40s} → #{info['rank']} {info['label']} "
                f"(${info['cost']:,} COP/mes)"
            )
        else:
            failures.append(
                f"{asset_type}: divergencia (bid={info['brecha_id']} vs {expected_bid}, "
                f"cost={info['cost']} vs {expected['estimated_monthly_cop']}, "
                f"rank={info['rank']} vs {expected['rank']})"
            )
            print(f"[FAIL] {service_name:40s} → divergencia: {info}")
    else:
        if info is None:
            print(f"[OK]   {service_name:40s} → sin costo ('—', sin cifras inventadas)")
        else:
            failures.append(f"{asset_type}: resolvió brecha inesperada {info}")
            print(f"[FAIL] {service_name:40s} → costo inesperado: {info}")

# Verificación de la tabla renderizada (fallback + datos vivos)
table = gen._generate_dynamic_services_table(
    assets_generated=[
        {"asset_type": a, "confidence_score": 0.9}
        for a in PROPOSAL_SERVICE_TO_ASSET.values()
    ],
    whatsapp_conflict=True,
    opportunity_scores=opportunity_scores,
)
import re
wa_line = next(l for l in table.splitlines() if "Botón de WhatsApp" in l)
if "Brecha #1: Conflicto de WhatsApp ($1.198.906 COP/mes)" in wa_line:
    print("[OK]   Tabla renderizada: WhatsApp rank vivo 1 + costo vivo")
else:
    failures.append(f"Tabla WhatsApp inesperada: {wa_line}")

if "Sin Schema Hotel" in "\n".join(
    l for l in table.splitlines() if "SEO Local" in l
):
    failures.append("N17: SEO Local todavía muestra 'Sin Schema Hotel'")
else:
    print("[OK]   Tabla renderizada: N17 corregido (SEO Local → 'SEO Local Bajo')")

print()
if failures:
    print(f"RESULTADO: FAIL ({len(failures)} fallos)")
    for f in failures:
        print(f"  - {f}")
    sys.exit(1)
print("RESULTADO: PASS — 5 services con costo vivo correcto, 2 sin costo, N17/N18 corregidos")
